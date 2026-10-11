from __future__ import annotations

from urllib.parse import urlparse

import httpx

from src.models import Evidence, UnverifiedClaim
from src.tracing import span

USER_AGENT = "Briefcase/0.1 citation-check"


def _live(url: str) -> tuple[bool, str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False, "invalid URL", ""
    headers = {"User-Agent": USER_AGENT}
    try:
        with httpx.Client(follow_redirects=True, timeout=12.0, headers=headers) as client:
            try:
                head = client.head(url)
                if head.status_code < 400:
                    return True, "ok", ""
            except Exception:
                pass
            get = client.get(url)
            if get.status_code >= 400:
                return False, f"HTTP {get.status_code}", get.text[:2000]
            return True, "ok", get.text[:8000]
    except Exception as exc:  # noqa: BLE001
        return False, str(exc), ""


@span(kind="GUARDRAIL", name="verify_citations")
def verify_evidence(evidence: list[Evidence]) -> tuple[list[Evidence], list[UnverifiedClaim]]:
    live: list[Evidence] = []
    bad: list[UnverifiedClaim] = []
    seen: set[str] = set()
    for ev in evidence:
        key = ev.source_url
        if key in seen:
            # still keep evidence row if previously verified
            if any(x.source_url == key for x in live):
                live.append(ev)
            continue
        seen.add(key)
        ok, reason, body = _live(ev.source_url)
        if not ok:
            bad.append(UnverifiedClaim(claim=ev.claim, source_url=ev.source_url, reason=reason))
            continue
        if ev.snippet and body:
            needle = ev.snippet[:40].strip()
            if needle and needle.lower() not in body.lower() and len(needle) > 12:
                # Page is live but snippet not found — keep the source, flag the quote.
                bad.append(
                    UnverifiedClaim(
                        claim=ev.claim,
                        source_url=ev.source_url,
                        reason="live URL but snippet not found on page",
                    )
                )
        live.append(ev)
    return live, bad


def citation_ids(evidence: list[Evidence]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    n = 1
    for ev in evidence:
        if ev.source_url not in mapping:
            mapping[ev.source_url] = n
            n += 1
    return mapping
