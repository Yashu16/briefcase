from __future__ import annotations

from typing import Any

import httpx

from src.config import get_settings
from src.tracing import span


@span(kind="RETRIEVER", name="web_search")
def web_search(query: str, *, max_results: int = 5) -> list[dict[str, str]]:
    settings = get_settings()
    if settings.tavily_api_key:
        return _tavily(query, settings.tavily_api_key, max_results)
    return _ddg(query, max_results)


def _tavily(query: str, api_key: str, max_results: int) -> list[dict[str, str]]:
    with httpx.Client(timeout=25.0) as client:
        resp = client.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": max_results},
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
    out = []
    for item in data.get("results", [])[:max_results]:
        out.append(
            {
                "title": str(item.get("title") or "web"),
                "url": str(item.get("url") or ""),
                "snippet": str(item.get("content") or item.get("snippet") or "")[:800],
            }
        )
    return [r for r in out if r["url"]]


def _ddg(query: str, max_results: int) -> list[dict[str, str]]:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS  # type: ignore[no-redef]
    results: list[dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results) or []:
                url = str(item.get("href") or item.get("url") or "")
                if not url:
                    continue
                results.append(
                    {
                        "title": str(item.get("title") or "web"),
                        "url": url,
                        "snippet": str(item.get("body") or item.get("snippet") or "")[:800],
                    }
                )
    except Exception:
        return []
    return results
