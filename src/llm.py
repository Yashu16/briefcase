from __future__ import annotations

import json
from typing import Any, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from src.config import get_settings
from src.tracing import span, wrap_openai

T = TypeVar("T", bound=BaseModel)

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        raw = OpenAI(
            api_key=settings.litellm_api_key or "missing",
            base_url=settings.litellm_base_url,
        )
        _client = wrap_openai(raw)
    return _client


@span(kind="CHAIN", name="llm_json")
def complete_json(system: str, user: str, model_cls: type[T], *, max_tokens: int = 2000) -> T:
    settings = get_settings()
    client = get_client()
    response = client.chat.completions.create(
        model=settings.litellm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        max_tokens=max_tokens,
        temperature=0.2,
    )
    text = response.choices[0].message.content or "{}"
    data: dict[str, Any] = json.loads(text)
    return model_cls.model_validate(data)


@span(kind="CHAIN", name="llm_text")
def complete_text(system: str, user: str, *, max_tokens: int = 2500) -> str:
    settings = get_settings()
    client = get_client()
    response = client.chat.completions.create(
        model=settings.litellm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""
