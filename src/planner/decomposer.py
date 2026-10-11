from __future__ import annotations

from pydantic import BaseModel, Field

from src.llm import complete_json
from src.models import JobPosting, ResearchQuestion, Topic
from src.tracing import span


class _Plan(BaseModel):
    questions: list[str] = Field(min_length=5, max_length=5)


TOPICS = (
    Topic.company,
    Topic.role_fit,
    Topic.interview,
    Topic.comp,
    Topic.sponsorship,
)


def template_questions(posting: JobPosting) -> list[ResearchQuestion]:
    company = posting.company or "the company"
    title = posting.title or "this role"
    prompts = [
        f"What does {company} do, how is it funded, who leads it, and what is recent news?",
        f"How well does {title} at {company} match typical requirements, team, and leveling for this posting?",
        f"What is the interview loop for {title} at {company} (stages, timeline, what they test)?",
        f"What is public compensation (base, equity, levels.fyi / Glassdoor) for {title} at {company} in {posting.location or 'the listed location'}?",
        f"Does {company} sponsor visas (H-1B, OPT, green card) and is there recent immigration or policy news?",
    ]
    return [
        ResearchQuestion(id=f"q{i+1}", topic=topic, prompt=prompt)
        for i, (topic, prompt) in enumerate(zip(TOPICS, prompts, strict=True))
    ]


@span(kind="AGENT", name="decompose_questions")
def decompose(posting: JobPosting) -> list[ResearchQuestion]:
    base = template_questions(posting)
    system = (
        "Rewrite five research questions for a job-intel brief. "
        "Return JSON {\"questions\": [q1,q2,q3,q4,q5]} in this order: "
        "company, role_fit, interview, compensation, sponsorship/news. "
        "Each question must be specific to the posting."
    )
    user = posting.model_dump_json()
    try:
        plan = complete_json(system, user, _Plan)
        return [
            ResearchQuestion(id=f"q{i+1}", topic=topic, prompt=q)
            for i, (topic, q) in enumerate(zip(TOPICS, plan.questions, strict=True))
        ]
    except Exception:
        return base
