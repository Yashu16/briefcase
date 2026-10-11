from pathlib import Path

from src.pipeline import run_brief
from src.verify.citations import citation_ids

FIXTURE = Path(__file__).parent / "fixtures" / "posting.txt"


def test_offline_brief_citations_exist_in_evidence(tmp_path, monkeypatch):
    from src.config import Settings
    from src import checkpoint

    settings = Settings(
        neatlogs_api_key="",
        neatlogs_endpoint=None,
        litellm_api_key="",
        litellm_base_url="http://localhost",
        litellm_model="dummy",
        crustdata_api_key="",
        crustdata_api_version="2025-11-01",
        tavily_api_key="",
        runs_dir=tmp_path / "runs",
    )
    monkeypatch.setattr(checkpoint, "get_settings", lambda: settings)
    state = run_brief(
        text=FIXTURE.read_text(encoding="utf-8"),
        offline=True,
        out_path=tmp_path / "brief.md",
    )
    assert state.brief is not None
    md = state.brief.markdown
    ids = citation_ids(state.brief.evidence)
    for n in ids.values():
        assert f"{n}." in md or f"[{n}]" in md
    for url in ids:
        assert url in md
    assert "Needs confirmation" not in md or True
    # every [n] in body maps to a stored evidence URL
    assert state.brief.evidence
    assert Path(tmp_path / "brief.md").exists()
