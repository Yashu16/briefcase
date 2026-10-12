from __future__ import annotations

from typing import Any

import httpx

from src.config import get_settings
from src.research.text import shorten_text
from src.tracing import span

CRUSTDATA_URL = "https://api.crustdata.com/company/enrich"
FIELDS = ["basic_info", "funding", "people", "news", "headcount", "hiring"]


@span(kind="TOOL", name="crustdata_enrich", tool_name="crustdata_enrich")
def enrich_company(company: str, domain: str | None = None) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.crustdata_api_key:
        return None
    body: dict[str, Any]
    if domain:
        body = {"domains": [domain], "fields": FIELDS}
    else:
        body = {"names": [company], "fields": FIELDS}
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                CRUSTDATA_URL,
                headers={
                    "Content-Type": "application/json",
                    "x-api-version": settings.crustdata_api_version,
                    "apikey": settings.crustdata_api_key,
                    "Authorization": f"Bearer {settings.crustdata_api_key}",
                },
                json=body,
            )
            if resp.status_code >= 400:
                return {"_error": f"crustdata {resp.status_code}", "_body": resp.text[:400]}
            payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"_error": str(exc)}
    return payload


def evidence_from_enrichment(payload: Any, question_id: str) -> list[dict[str, str]]:
    """Flatten a Crustdata enrich response into claim-like dicts."""
    rows: list[dict[str, str]] = []
    items = payload if isinstance(payload, list) else [payload]
    for item in items:
        if not isinstance(item, dict):
            continue
        matches = item.get("matches") or []
        for match in matches:
            data = (match or {}).get("company_data") or {}
            basic = data.get("basic_info") or {}
            name = basic.get("name") or "company"
            domain = basic.get("domain") or ""
            url = basic.get("website") or (f"https://{domain}" if domain else "https://crustdata.com")
            desc = basic.get("description") or ""
            if desc:
                rows.append(
                    {
                        "claim": shorten_text(f"{name}: {desc}", 280),
                        "url": str(url),
                        "name": "Crustdata",
                        "snippet": str(desc)[:500],
                        "question_id": question_id,
                    }
                )
            funding = data.get("funding") or {}
            funding_claim = _funding_claim(name, funding)
            if funding_claim:
                rows.append(
                    {
                        "claim": funding_claim,
                        "url": str(url),
                        "name": "Crustdata funding",
                        "snippet": funding_claim,
                        "question_id": question_id,
                    }
                )
            news = data.get("news") or []
            for article in news[:3]:
                if not isinstance(article, dict):
                    continue
                nurl = str(article.get("url") or url)
                title = str(article.get("title") or "").strip()
                if not title:
                    continue
                rows.append(
                    {
                        "claim": f"{name} news: {title}",
                        "url": nurl,
                        "name": "Crustdata news",
                        "snippet": f"{name} news: {title}",
                        "question_id": question_id,
                    }
                )
            people = data.get("people") or {}
            for key in ("founders", "cxos", "decision_makers"):
                for person in (people.get(key) or [])[:3]:
                    if isinstance(person, dict):
                        pname = person.get("name") or person.get("full_name")
                        if not pname:
                            continue
                        title = person.get("current_title") or person.get("headline") or key.replace("_", " ")
                        rows.append(
                            {
                                "claim": f"{name} leadership: {pname} ({title})",
                                "url": str(url),
                                "name": "Crustdata people",
                                "snippet": f"{pname} ({title})",
                                "question_id": question_id,
                            }
                        )
    return rows


def _funding_claim(name: str, funding: Any) -> str:
    if not isinstance(funding, dict):
        return ""
    acquisitions = funding.get("acquisitions") or []
    acquisition_names: list[str] = []
    for acquisition in acquisitions:
        if not isinstance(acquisition, dict):
            continue
        acquired_name = acquisition.get("acquiree_company_name")
        if acquired_name:
            date = acquisition.get("date")
            acquisition_names.append(f"{acquired_name} ({date})" if date else str(acquired_name))
    if acquisition_names:
        return shorten_text(
            f"{name} has acquisition records for {', '.join(acquisition_names[:3])}.",
            240,
        )

    investors = funding.get("investors") or []
    if isinstance(investors, list) and investors:
        investor_names = [
            str(investor.get("name") or investor)
            for investor in investors[:3]
            if investor
        ]
        if investor_names:
            return shorten_text(f"{name} funding records list investors: {', '.join(investor_names)}.", 240)
    return ""
