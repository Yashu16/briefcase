# Demo video script (≤ 3:00)

Goal: judges see the agent complete a posting → brief loop, then neatlogs / Entire / cfo.ai each get architecture, implementation, runtime, reasoning, result.

## 0:00–0:25 — The problem

“Candidates open ten tabs per job. Briefcase is an agent: posting in, cited brief out. Five questions, evidence, verdicts when sources disagree, live URL check.”

Show: `python -m src.main --url … --out brief.md` starting.

## 0:25–1:05 — The agent (30% criterion)

Screen: terminal + `brief.md`.

- Ingest parsed company/title
- Five questions
- Crustdata + web evidence
- A verdict with dissent
- Sources numbered; “Needs confirmation” if a link died

“Citations are data, not prose. The verifier only keeps URLs the researcher stored.”

## 1:05–1:45 — neatlogs

Architecture: one WORKFLOW `job-brief`, CHAIN/AGENT/TOOL/RETRIEVER/GUARDRAIL children.

Implementation: `src/tracing.py` `init` + `wrap(OpenAI)` + `@span` on every stage.

Runtime: dashboard span tree (latency, tokens, cost).

Reasoning: `--no-priors` vs default. “We compare two traces of the same posting.”

Result: point at two traces; say the numbers on screen (do not invent). Confidence / unverified claims / cost.

Optional 10s: `--force-fetch-fail` retry span.

## 1:45–2:20 — Entire

Architecture: checkpoints of *this repo* as the coding agent builds it; entire-graph for symbols.

Implementation: `entire enable`; checkpoints after ingest, research, first brief.

Runtime: show checkpoint list + `docs/entire-graph.md`.

Reasoning: graph search “who calls adjudicate”.

Result: entity-level diff of the latest checkpoint.

## 2:20–2:50 — cfo.ai

Architecture: unit = one brief.

Implementation: COGS from neatlogs + Crustdata; tiers in `docs/business-plan.md`.

Runtime: Ari model (pricing, costs, revenue, runway).

Reasoning: freemium 3/week vs career-center seats.

Result: one scenario table (Base MRR).

## 2:50–3:00 — Close

Repo URL, `#neatHack`, “all code this weekend.”
