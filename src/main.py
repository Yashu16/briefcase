from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.pipeline import run_brief
from src.tracing import flush_tracing, init_tracing


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="briefcase",
        description="Turn a job posting URL or pasted text into a cited research brief.",
    )
    p.add_argument("--url", help="Job posting URL")
    p.add_argument("--text", help="Raw posting text")
    p.add_argument("--text-file", type=Path, help="File containing posting text")
    p.add_argument("--out", type=Path, default=Path("brief.md"), help="Markdown output path")
    p.add_argument("--no-priors", action="store_true", help="Adjudicate without credibility priors (A/B trace)")
    p.add_argument("--offline", action="store_true", help="Heuristic parse + fixture evidence (no paid APIs)")
    p.add_argument("--force-fetch-fail", action="store_true", help="Fail the first fetch attempt (recovery demo)")
    p.add_argument("--run-id", help="Reuse a run id for checkpoints")
    return p


def cli(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    text = args.text
    if args.text_file:
        text = args.text_file.read_text(encoding="utf-8")
    init_tracing()
    try:
        state = run_brief(
            url=args.url,
            text=text,
            use_priors=not args.no_priors,
            offline=args.offline,
            force_fetch_fail=args.force_fetch_fail,
            run_id=args.run_id,
            out_path=args.out,
            progress=lambda message: print(message, flush=True),
        )
    except Exception as exc:  # noqa: BLE001
        logging.error("brief failed: %s", exc)
        flush_tracing()
        return 1
    flush_tracing()
    print(f"wrote {args.out} (run {state.run_id})")
    if state.recovered_from:
        print("recovered from:", ", ".join(state.recovered_from))
    if state.brief:
        print(f"verdicts={len(state.brief.verdicts)} unverified={len(state.brief.unverified_claims)}")
    return 0


if __name__ == "__main__":
    sys.exit(cli())
