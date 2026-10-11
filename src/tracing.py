from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

from src.config import get_settings

log = logging.getLogger("briefcase.tracing")

_initialized = False
_neatlogs = None

F = TypeVar("F", bound=Callable[..., Any])


def _load_neatlogs():
    global _neatlogs
    if _neatlogs is not None:
        return _neatlogs
    try:
        import neatlogs as nl

        _neatlogs = nl
    except ImportError:
        _neatlogs = False
    return _neatlogs


def init_tracing() -> None:
    """Call once at CLI entry. Safe if the API key is missing (tests / offline)."""
    global _initialized
    if _initialized:
        return
    settings = get_settings()
    nl = _load_neatlogs()
    if not nl or not settings.neatlogs_api_key:
        log.warning("neatlogs not initialized (missing package or NEATLOGS_API_KEY)")
        _initialized = True
        return
    kwargs: dict[str, Any] = {
        "api_key": settings.neatlogs_api_key,
        "workflow_name": "job-brief",
    }
    if settings.neatlogs_endpoint:
        kwargs["endpoint"] = settings.neatlogs_endpoint
    nl.init(**kwargs)
    _initialized = True
    log.info("neatlogs initialized workflow=job-brief")


def flush_tracing() -> None:
    nl = _load_neatlogs()
    if not nl or not _initialized:
        return
    try:
        nl.flush()
        nl.shutdown()
    except Exception as exc:  # noqa: BLE001
        log.warning("neatlogs flush/shutdown failed: %s", exc)


def wrap_openai(client: Any) -> Any:
    nl = _load_neatlogs()
    if not nl or not get_settings().neatlogs_api_key:
        return client
    return nl.wrap(client)


def span(kind: str = "CHAIN", name: str | None = None, **extra: Any) -> Callable[[F], F]:
    """neatlogs @span when available; otherwise a no-op so tests still run."""

    def decorator(fn: F) -> F:
        nl = _load_neatlogs()
        if nl and get_settings().neatlogs_api_key:
            kwargs: dict[str, Any] = {"kind": kind}
            if name:
                kwargs["name"] = name
            kwargs.update(extra)
            return nl.span(**kwargs)(fn)

        @functools.wraps(fn)
        def wrapped(*args: Any, **kwargs: Any):
            return fn(*args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator
