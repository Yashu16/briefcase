from __future__ import annotations

from src.credibility import credibility_for_url
from src.models import Evidence, JobPosting, ResearchQuestion, Topic
from src.research.crustdata import enrich_company, evidence_from_enrichment
from src.research.web_search import web_search
from src.tracing import span


@span(kind="AGENT", name="research_question")
def research_question(
    posting: JobPosting,
    question: ResearchQuestion,
    *,
    use_priors: bool = True,
) -> list[Evidence]:
    hits = web_search(question.prompt, max_results=5)
    evidence: list[Evidence] = []
    for hit in hits:
        url = hit["url"]
        evidence.append(
            Evidence(
                claim=hit["snippet"][:280] or hit["title"],
                source_url=url,
                source_name=hit["title"][:80],
                snippet=hit["snippet"],
                credibility=credibility_for_url(url, posting.company_domain, use_priors),
                question_id=question.id,
            )
        )
    if question.topic in {Topic.company, Topic.sponsorship, Topic.comp} or question.id == "q1":
        payload = enrich_company(posting.company, posting.company_domain)
        if payload and not (isinstance(payload, dict) and payload.get("_error")):
            for row in evidence_from_enrichment(payload, question.id):
                evidence.append(
                    Evidence(
                        claim=row["claim"],
                        source_url=row["url"],
                        source_name=row["name"],
                        snippet=row["snippet"],
                        credibility=credibility_for_url(row["url"], posting.company_domain, use_priors),
                        question_id=question.id,
                    )
                )
        elif isinstance(payload, dict) and payload.get("_error"):
            evidence.append(
                Evidence(
                    claim=f"Crustdata unavailable ({payload.get('_error')}); continuing with web sources only.",
                    source_url="https://docs.crustdata.com/company-docs/enrichment/introduction",
                    source_name="Crustdata fallback",
                    snippet=str(payload.get("_error")),
                    credibility=0.3 if use_priors else 0.5,
                    question_id=question.id,
                )
            )
    return evidence


@span(kind="CHAIN", name="research_all")
def research_all(
    posting: JobPosting,
    questions: list[ResearchQuestion],
    *,
    use_priors: bool = True,
) -> list[Evidence]:
    bundled: list[Evidence] = []
    for q in questions:
        bundled.extend(research_question(posting, q, use_priors=use_priors))
    return bundled
