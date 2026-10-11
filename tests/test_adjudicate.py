from src.adjudicate.verdict import adjudicate
from src.models import Evidence


def _pair() -> list[Evidence]:
    return [
        Evidence(
            claim="Stripe senior SWE total compensation is about $250k.",
            source_url="https://www.levels.fyi/companies/stripe/salaries/software-engineer",
            source_name="Levels.fyi",
            snippet="$250k median",
            credibility=0.92,
            question_id="q4",
        ),
        Evidence(
            claim="Stripe senior SWE total compensation is about $90k.",
            source_url="https://example.com/random-comp-blog",
            source_name="Random blog",
            snippet="$90k",
            credibility=0.45,
            question_id="q4",
        ),
    ]


def test_priors_prefer_levels_fyi():
    verdicts = adjudicate(_pair(), use_priors=True)
    assert verdicts
    top = max(verdicts, key=lambda v: v.confidence)
    assert "250k" in top.verdict
    assert top.confidence > 0.7
    assert top.dissent is not None
    assert "90k" in top.dissent


def test_without_priors_confidence_is_lower():
    with_p = adjudicate(_pair(), use_priors=True)
    without = adjudicate(_pair(), use_priors=False)
    assert max(v.confidence for v in without) < max(v.confidence for v in with_p)
    assert any("without credibility priors" in v.rationale for v in without)
