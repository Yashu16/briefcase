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

Captured locally on 2026-10-11 with Entire CLI 0.11.4 and entire-graph v0.4.0.

```text
entire graph doctor --json:
  provider: entire-graph
  version: v0.4.0
  no_egress: true
  partial_failures: 0

entire graph snapshot --repo . --format ndjson:
  files: 39
  parsed_files: 39
  symbols: 145
  relations: 586
  completeness: ok

entire graph search --repo . --query "job brief pipeline stages":
  top result: src/pipeline.py:19-89 (run_brief)
  related symbols: ingest, planner, research, adjudicate, synthesize, verify
```

Do not paste secrets, `.env`, or private checkpoint payloads.
