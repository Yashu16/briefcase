from src.models import Evidence
from src.verify import citations


def test_http_404_is_flagged(monkeypatch):
    def fake_live(url: str):
        if "dead.example" in url:
            return False, "HTTP 404", ""
        return True, "ok", "live page body with snippet tokens here"

    monkeypatch.setattr(citations, "_live", fake_live)
    evidence = [
        Evidence(
            claim="dead link claim",
            source_url="https://dead.example/missing",
            source_name="gone",
            snippet="x",
            credibility=0.4,
            question_id="q1",
        ),
        Evidence(
            claim="live claim",
            source_url="https://en.wikipedia.org/wiki/Test",
            source_name="wiki",
            snippet="snippet tokens",
            credibility=0.65,
            question_id="q1",
        ),
    ]
    live, bad = citations.verify_evidence(evidence)
    assert any("dead.example" in u.source_url for u in bad)
    assert any(e.source_url.endswith("/wiki/Test") for e in live)
