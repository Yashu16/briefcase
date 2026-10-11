from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse

from pydantic import BaseModel, Field

from src.llm import complete_json
from src.models import JobPosting
from src.tracing import span


class _ParsedPosting(BaseModel):
    company: str
    title: str
    location: str = ""
    requirements: list[str] = Field(default_factory=list)
    company_domain: str = ""


SYSTEM = """You extract structured job posting fields.
Return JSON with keys: company, title, location, requirements (array of strings), company_domain.
company_domain is the company's public website host if mentioned (example.com), else empty string.
Use only the provided text. Do not invent a company or title."""


@span(kind="CHAIN", name="parse_posting")
def parse_posting(text: str, raw_url: str | None = None) -> JobPosting:
    snippet = text[:12000]
    try:
        parsed = complete_json(SYSTEM, snippet, _ParsedPosting)
    except Exception:
        parsed = complete_json(SYSTEM, snippet[:4000], _ParsedPosting)
    company, title, location = _repair_fields(
        company=parsed.company,
        title=parsed.title,
        location=parsed.location,
        text=text,
        raw_url=raw_url,
    )
    return JobPosting(
        company=company,
        title=title,
        location=location,
        requirements=_clean_requirements(parsed.requirements),
        raw_url=raw_url,
        source_text=text[:20000],
        company_domain=parsed.company_domain or _company_domain(raw_url),
    )


def parse_posting_heuristic(text: str, raw_url: str | None = None) -> JobPosting:
    """Offline fallback used by tests and when the LLM is unavailable."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = next((ln for ln in lines if "engineer" in ln.lower() or "role" in ln.lower() or ln[:1].isupper()), lines[0] if lines else "Unknown role")
    company = "Unknown"
    for ln in lines:
        if ln.lower().startswith("company:"):
            company = ln.split(":", 1)[1].strip()
            break
    reqs = [ln.lstrip("- ").strip() for ln in lines if ln.startswith("- ")]
    location = ""
    for ln in lines:
        if ln.lower().startswith("location:"):
            location = ln.split(":", 1)[1].strip()
    company, title, location = _repair_fields(
        company=company,
        title=title.replace("Title:", "").strip(),
        location=location,
        text=text,
        raw_url=raw_url,
    )
    return JobPosting(
        company=company,
        title=title,
        location=location,
        requirements=_clean_requirements(reqs),
        raw_url=raw_url,
        source_text=text,
        company_domain=_company_domain(raw_url),
    )


def _repair_fields(
    *,
    company: str,
    title: str,
    location: str,
    text: str,
    raw_url: str | None,
) -> tuple[str, str, str]:
    """Repair fields when page chrome causes an otherwise useful parse to be incomplete."""
    normalized_company = company.strip()
    normalized_title = title.strip()
    normalized_location = location.strip()
    lowered_company = normalized_company.casefold()

    if not normalized_company or lowered_company in {"unknown", "n/a", "none"}:
        parsed_url = urlparse(raw_url or "")
        host = parsed_url.netloc.casefold().removeprefix("www.")
        if host == "google.com" and "/careers/" in parsed_url.path:
            normalized_company = "Google"
        else:
            match = re.search(
                r",\s*([A-Z][A-Za-z0-9&. -]+?)(?:\s+(?:Ads|Careers))?\s*$",
                normalized_title,
            )
            if match:
                normalized_company = match.group(1).strip()

    if not normalized_location and raw_url:
        location_values = parse_qs(urlparse(raw_url).query).get("location")
        if location_values:
            normalized_location = unquote(location_values[0]).replace("+", " ").strip()

    return normalized_company or "Unknown", normalized_title, normalized_location


def _company_domain(raw_url: str | None) -> str | None:
    host = urlparse(raw_url or "").netloc.casefold().removeprefix("www.")
    return host or None


def _clean_requirements(requirements: list[str]) -> list[str]:
    navigation_labels = {"linkcopy link", "emailemail a friend"}
    return [item.strip() for item in requirements if item.strip().casefold() not in navigation_labels]
