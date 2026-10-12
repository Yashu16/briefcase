from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


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


def summarize_evidence(snippet: str, question: str) -> str:
    """Rewrite a search snippet as one concise, source-grounded sentence."""
    fallback = shorten_text(snippet, 280)
    if not snippet.strip():
        return ""
    try:
        from src.llm import complete_text

        summary = complete_text(
            (
                "Rewrite the supplied search snippet as one concise factual sentence. "
                "Use only information explicitly present in the snippet. "
                "Do not add dates, numbers, entities, or conclusions that are not stated. "
                "Do not mention that it is a snippet and do not use a bullet or quotation marks."
            ),
            f"Research question: {question}\nSearch snippet: {snippet}",
            max_tokens=120,
        ).strip()
        return shorten_text(summary, 280) if summary else fallback
    except Exception as exc:  # noqa: BLE001
        logger.warning("evidence summarization failed; using source snippet: %s", exc)
        return fallback
