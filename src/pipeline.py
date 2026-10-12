from __future__ import annotations

import uuid
from collections.abc import Callable
from pathlib import Path

from src.adjudicate.verdict import adjudicate
from src.checkpoint import save_artifact, save_state
from src.ingest.fetcher import FetchError, fetch_url
from src.ingest.parser import parse_posting, parse_posting_heuristic
from src.models import Brief, JobPosting, PipelineState
from src.planner.decomposer import decompose, template_questions
from src.research.worker import research_all
from src.synthesize.brief import synthesize
from src.tracing import span
from src.verify.citations import verify_evidence


@span(kind="WORKFLOW", name="job_brief")
def run_brief(
    *,
    url: str | None = None,
    text: str | None = None,
    use_priors: bool = True,
    offline: bool = False,
    force_fetch_fail: bool = False,
    run_id: str | None = None,
    out_path: Path | None = None,
    progress: Callable[[str], None] | None = None,
) -> PipelineState:
    state = PipelineState(run_id=run_id or uuid.uuid4().hex[:12], use_priors=use_priors)

    _report(progress, "1/6 Ingesting job posting")
    if text:
        raw = text
        raw_url = url
    elif url:
        try:
            raw = fetch_url(url, force_fail=force_fetch_fail)
            if force_fetch_fail:
                state.recovered_from.append("fetch_retry")
        except FetchError:
            if text:
                raw = text
            else:
                raise
            state.recovered_from.append("fetch_failed_need_paste")
        raw_url = url
    else:
        raise ValueError("provide --url or --text / --text-file")

    _report(progress, "1/6 Ingesting job posting ... OK")

    _report(progress, "2/6 Parsing posting")
    if offline:
        posting = parse_posting_heuristic(raw, raw_url)
    else:
        try:
            posting = parse_posting(raw, raw_url)
        except Exception:
            posting = parse_posting_heuristic(raw, raw_url)
            state.recovered_from.append("parser_heuristic")
    _report(progress, f"2/6 Parsing posting ... {posting.company} / {posting.title}")
    state.posting = posting
    save_artifact(state.run_id, "posting.json", posting)
    save_state(state)

    _report(progress, "3/6 Planning research questions")
    if offline:
        questions = template_questions(posting)
    else:
        questions = decompose(posting)
    state.questions = questions
    _report(progress, f"3/6 Planning research questions ... {len(questions)} questions")
    save_artifact(state.run_id, "questions.json", [q.model_dump() for q in questions])
    save_state(state)

    _report(progress, "4/6 Researching evidence")
    if offline:
        evidence = _fixture_evidence(posting)
    else:
        evidence = research_all(posting, questions, use_priors=use_priors)
    state.evidence = evidence
    _report(progress, f"4/6 Researching evidence ... {len(evidence)} findings")
    save_artifact(state.run_id, "evidence.json", [e.model_dump() for e in evidence])
    save_state(state)

    _report(progress, "5/6 Adjudicating and verifying citations")
    live, unverified = (evidence, []) if offline else verify_evidence(evidence)
    verdicts = adjudicate(live, use_priors=use_priors)
    state.verdicts = verdicts
    _report(progress, f"5/6 Adjudicating and verifying citations ... {len(verdicts)} verdicts, {len(unverified)} unverified")
    save_state(state)

    brief: Brief = synthesize(posting, verdicts, live, unverified)
    state.brief = brief
    save_artifact(state.run_id, "brief.md", brief.markdown)
    save_state(state)

    if out_path:
        out_path.write_text(brief.markdown, encoding="utf-8")
    output_label = str(out_path or Path("runs") / state.run_id / "brief.md")
    _report(progress, f"6/6 Writing brief ... {output_label}")
    return state


def _report(progress: Callable[[str], None] | None, message: str) -> None:
    if progress:
        progress(message)


def _fixture_evidence(posting: JobPosting):
    from src.models import Evidence

    company = posting.company
    return [
        Evidence(
            claim=f"{company} is a software company with public career pages.",
            source_url="https://en.wikipedia.org/wiki/Software_company",
            source_name="Wikipedia",
            snippet="software company",
            credibility=0.65,
            question_id="q1",
        ),
        Evidence(
            claim=f"{company} blog claims faster growth than filings support.",
            source_url="https://example.com/random-blog",
            source_name="Random blog",
            snippet="hypergrowth",
            credibility=0.45,
            question_id="q1",
        ),
        Evidence(
            claim=f"{posting.title} typically requires the listed skills.",
            source_url="https://www.levels.fyi/",
            source_name="Levels.fyi",
            snippet="compensation bands",
            credibility=0.92,
            question_id="q2",
        ),
        Evidence(
            claim="Interview loops often include a recruiter screen and two technical rounds.",
            source_url="https://www.glassdoor.com/",
            source_name="Glassdoor",
            snippet="interview",
            credibility=0.78,
            question_id="q3",
        ),
        Evidence(
            claim="Public total compensation varies widely by level and location.",
            source_url="https://www.levels.fyi/",
            source_name="Levels.fyi",
            snippet="total compensation",
            credibility=0.92,
            question_id="q4",
        ),
        Evidence(
            claim="Visa sponsorship should be confirmed on the official careers page.",
            source_url="https://www.myvisajobs.com/",
            source_name="MyVisaJobs",
            snippet="H1B",
            credibility=0.73,
            question_id="q5",
        ),
    ]
