from __future__ import annotations

import time
from urllib.parse import urlparse

import httpx
import trafilatura

from src.tracing import span

USER_AGENT = "Briefcase/0.1 (+neatHack job-intel-agent)"


class FetchError(RuntimeError):
    pass


@span(kind="TOOL", name="fetch_url", tool_name="fetch_url")
def fetch_url(url: str, *, retries: int = 3, force_fail: bool = False) -> str:
    if force_fail:
        last = FetchError("forced fetch failure (demo recovery path)")
        recovered = _retry_loop(url, retries=retries, first_error=last)
        if recovered:
            return recovered
        raise last
    return _retry_loop(url, retries=retries)


def _retry_loop(url: str, *, retries: int, first_error: Exception | None = None) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise FetchError(f"unsupported URL scheme: {url}")
    last_err: Exception | None = first_error
    start = 1 if first_error else 0
    for attempt in range(start, retries):
        try:
            with httpx.Client(follow_redirects=True, timeout=20.0, headers={"User-Agent": USER_AGENT}) as client:
                resp = client.get(url)
                resp.raise_for_status()
                extracted = trafilatura.extract(resp.text, include_comments=False, include_tables=True)
                text = (extracted or resp.text or "").strip()
                if not text:
                    raise FetchError("empty body after extract")
                return text
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(0.4 * (attempt + 1))
    raise FetchError(f"fetch failed after {retries} attempts: {last_err}") from last_err
