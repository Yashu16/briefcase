from src.research.text import shorten_text, summarize_evidence


def test_shorten_text_keeps_complete_sentence_when_possible():
    text = "Google's mission is to build useful products. " + "Additional detail " * 30

    assert shorten_text(text, 80) == "Google's mission is to build useful products."


def test_shorten_text_marks_word_boundary_truncation():
    text = "A long evidence snippet with many details that cannot fit in the brief."

    result = shorten_text(text, 40)

    assert result.endswith("...")
    assert len(result) <= 40


def test_summarize_evidence_uses_grounded_llm_summary(monkeypatch):
    from src import llm

    monkeypatch.setattr(
        llm,
        "complete_text",
        lambda system, user, max_tokens: "Google builds products used by people worldwide.",
    )

    assert summarize_evidence("Google builds products for people worldwide.", "What does Google do?") == (
        "Google builds products used by people worldwide."
    )
