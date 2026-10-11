from __future__ import annotations

import json
from pathlib import Path

from src.config import get_settings
from src.models import PipelineState


def run_dir(run_id: str) -> Path:
    path = get_settings().runs_dir / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_state(state: PipelineState) -> Path:
    path = run_dir(state.run_id) / "state.json"
    path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_state(run_id: str) -> PipelineState:
    path = run_dir(run_id) / "state.json"
    return PipelineState.model_validate_json(path.read_text(encoding="utf-8"))


def save_artifact(run_id: str, name: str, payload: object) -> Path:
    path = run_dir(run_id) / name
    if hasattr(payload, "model_dump_json"):
        path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    elif isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
