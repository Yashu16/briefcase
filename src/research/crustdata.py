from __future__ import annotations

from typing import Any

import httpx

from src.config import get_settings
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
                    "Authorization": settings.crustdata_api_key,
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
                        "claim": f"{name}: {desc[:280]}",
                        "url": str(url),
                        "name": "Crustdata",
                        "snippet": str(desc)[:500],
                        "question_id": question_id,
                    }
                )
            funding = data.get("funding") or {}
            if funding:
                rows.append(
                    {
                        "claim": f"{name} funding snapshot: {str(funding)[:240]}",
                        "url": str(url),
                        "name": "Crustdata",
                        "snippet": str(funding)[:500],
                        "question_id": question_id,
                    }
                )
            news = data.get("news") or []
            for article in news[:3]:
                if not isinstance(article, dict):
                    continue
                nurl = str(article.get("url") or url)
                title = str(article.get("title") or "news")
                rows.append(
                    {
                        "claim": title,
                        "url": nurl,
                        "name": "Crustdata news",
                        "snippet": title,
                        "question_id": question_id,
                    }
                )
            people = data.get("people") or {}
            for key in ("founders", "cxos", "decision_makers"):
                for person in (people.get(key) or [])[:3]:
                    if isinstance(person, dict):
                        pname = person.get("name") or person.get("full_name") or "leader"
                        rows.append(
                            {
                                "claim": f"{name} {key}: {pname}",
                                "url": str(url),
                                "name": "Crustdata people",
                                "snippet": str(person)[:400],
                                "question_id": question_id,
                            }
                        )
    return rows
