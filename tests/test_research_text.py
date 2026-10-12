from src.research.text import shorten_text


def test_shorten_text_keeps_complete_sentence_when_possible():
    text = "Google's mission is to build useful products. " + "Additional detail " * 30

    assert shorten_text(text, 80) == "Google's mission is to build useful products."


def test_shorten_text_marks_word_boundary_truncation():
    text = "A long evidence snippet with many details that cannot fit in the brief."

    result = shorten_text(text, 40)

    assert result.endswith("...")
    assert len(result) <= 40
