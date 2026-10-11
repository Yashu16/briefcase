from pathlib import Path

from src.ingest.parser import _repair_fields, parse_posting_heuristic

FIXTURE = Path(__file__).parent / "fixtures" / "posting.txt"


def test_heuristic_parser_extracts_company_title_reqs():
    posting = parse_posting_heuristic(FIXTURE.read_text(encoding="utf-8"))
    assert posting.company == "Stripe"
    assert "Senior Software Engineer" in posting.title
    assert posting.location.startswith("New York")
    assert any("Python" in r for r in posting.requirements)


def test_repair_fields_recovers_google_careers_metadata():
    company, title, location = _repair_fields(
        company="Unknown",
        title="Senior Software Engineer, Generative AI/Machine Learning, Google Ads",
        location="",
        text="Minimum qualifications:",
        raw_url=(
            "https://www.google.com/about/careers/applications/jobs/results/123"
            "?location=United%20States"
        ),
    )

    assert company == "Google"
    assert title.startswith("Senior Software Engineer")
    assert location == "United States"


def test_heuristic_parser_recovers_url_metadata_when_llm_is_unavailable():
    url = "https://www.google.com/about/careers/applications/jobs/results/123?location=United%20States"
    posting = parse_posting_heuristic(
        "Senior Software Engineer, Generative AI/Machine Learning, Google Ads\n"
        "- Bachelor’s degree in Computer Science",
        url,
    )

    assert posting.company == "Google"
    assert posting.location == "United States"
    assert posting.company_domain == "google.com"
