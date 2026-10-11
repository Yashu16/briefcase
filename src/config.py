from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    neatlogs_api_key: str
    neatlogs_endpoint: str | None
    litellm_api_key: str
    litellm_base_url: str
    litellm_model: str
    crustdata_api_key: str
    crustdata_api_version: str
    tavily_api_key: str
    runs_dir: Path


def get_settings() -> Settings:
    return Settings(
        neatlogs_api_key=os.getenv("NEATLOGS_API_KEY", "").strip(),
        neatlogs_endpoint=os.getenv("NEATLOGS_ENDPOINT", "").strip() or None,
        litellm_api_key=os.getenv("LITELLM_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", "").strip(),
        litellm_base_url=os.getenv("LITELLM_BASE_URL", "https://litellm.neatlogs.com/v1").strip(),
        litellm_model=os.getenv("LITELLM_MODEL", "claude-sonnet-4").strip(),
        crustdata_api_key=os.getenv("CRUSTDATA_API_KEY", "").strip(),
        crustdata_api_version=os.getenv("CRUSTDATA_API_VERSION", "2025-11-01").strip(),
        tavily_api_key=os.getenv("TAVILY_API_KEY", "").strip(),
        runs_dir=Path(os.getenv("BRIEFCASE_RUNS_DIR", "runs")),
    )
