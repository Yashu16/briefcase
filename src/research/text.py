from __future__ import annotations


def shorten_text(text: str, limit: int) -> str:
    """Keep evidence readable while making any shortening explicit."""
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized

    cutoff = max(1, limit - 3)
    sentence_end = max(
        (normalized.rfind(mark, 0, cutoff) for mark in ".!?"),
        default=-1,
    )
    if sentence_end >= max(40, cutoff // 2):
        return normalized[: sentence_end + 1]

    word_end = normalized.rfind(" ", 0, cutoff)
    return normalized[: max(1, word_end)] + "..."
