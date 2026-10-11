from __future__ import annotations

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
    return JobPosting(
        company=parsed.company,
        title=parsed.title,
        location=parsed.location,
        requirements=parsed.requirements,
        raw_url=raw_url,
        source_text=text[:20000],
        company_domain=parsed.company_domain or None,
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
    return JobPosting(
        company=company,
        title=title.replace("Title:", "").strip(),
        location=location,
        requirements=reqs,
        raw_url=raw_url,
        source_text=text,
    )
