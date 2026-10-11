from __future__ import annotations

from urllib.parse import urlparse

# Domain priors: official / high-signal sources beat random blogs.
DOMAIN_PRIORS: dict[str, float] = {
    "levels.fyi": 0.92,
    "www.levels.fyi": 0.92,
    "glassdoor.com": 0.78,
    "www.glassdoor.com": 0.78,
    "teamblind.com": 0.70,
    "www.teamblind.com": 0.70,
    "linkedin.com": 0.72,
    "www.linkedin.com": 0.72,
    "crunchbase.com": 0.80,
    "www.crunchbase.com": 0.80,
    "sec.gov": 0.95,
    "www.sec.gov": 0.95,
    "wikipedia.org": 0.65,
    "en.wikipedia.org": 0.65,
    "crustdata.com": 0.88,
    "api.crustdata.com": 0.88,
    "builtin.com": 0.62,
    "wellfound.com": 0.60,
    "h1bgrader.com": 0.75,
    "h1bdata.info": 0.74,
    "myvisajobs.com": 0.73,
}


def credibility_for_url(url: str, company_domain: str | None = None, use_priors: bool = True) -> float:
    if not use_priors:
        return 0.5
    host = urlparse(url).netloc.lower().removeprefix("www.")
    full = urlparse(url).netloc.lower()
    if company_domain:
        cd = company_domain.lower().removeprefix("www.")
        if host == cd or host.endswith("." + cd):
            return 0.90
    if full in DOMAIN_PRIORS:
        return DOMAIN_PRIORS[full]
    if host in DOMAIN_PRIORS:
        return DOMAIN_PRIORS[host]
    if host.endswith(".gov"):
        return 0.90
    if host.endswith(".edu"):
        return 0.70
    return 0.45
