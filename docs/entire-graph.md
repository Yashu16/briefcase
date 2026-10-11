# Entire graph evidence

Entire is used **while building Briefcase**, not as a runtime tool of the job-intel agent.

Intended checkpoints (record IDs after `entire enable`):

1. After ingest + parser land
2. After research + adjudicate land
3. After first successful `brief.md` (offline golden is acceptable)

Commands for judges to re-run (from repo root, Entire CLI installed):

```text
entire enable
entire graph doctor --json
entire graph search --repo . --query "where is credibility prior applied during adjudication"
entire graph snapshot --repo . --format ndjson
entire graph impact --symbol adjudicate
```

## Snapshot (sanitized)

If the Entire CLI is not on PATH in this environment, this file still documents the intended graph. A captured snippet from `entire graph search` should be pasted below when the CLI is available:

```text
pending: run `entire graph search --repo . --query "job brief pipeline stages"`
key symbols expected:
  - src.pipeline.run_brief
  - src.adjudicate.verdict.adjudicate
  - src.verify.citations.verify_evidence
  - src.research.worker.research_question
  - src.tracing.init_tracing
```

Do not paste secrets, `.env`, or private checkpoint payloads.
