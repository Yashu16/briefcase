from pathlib import Path

from src.ingest.parser import parse_posting_heuristic

FIXTURE = Path(__file__).parent / "fixtures" / "posting.txt"


def test_heuristic_parser_extracts_company_title_reqs():
    posting = parse_posting_heuristic(FIXTURE.read_text(encoding="utf-8"))
    assert posting.company == "Stripe"
    assert "Senior Software Engineer" in posting.title
    assert posting.location.startswith("New York")
    assert any("Python" in r for r in posting.requirements)
