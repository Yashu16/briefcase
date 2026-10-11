# neatHack build log — Briefcase

## Project

**Briefcase** turns a job posting (URL or pasted text) into a cited research brief: company, role-fit, interview loop, compensation, and sponsorship/news. Candidates currently stitch this together from tabs; the agent retrieves evidence, resolves conflicts, and refuses to cite a URL it did not fetch.

## Team

Yaswanth (solo unless additional handles are added here).

## Stack

- Python 3.11, Pydantic v2, OpenAI SDK → hackathon LiteLLM (Nova/Claude)
- neatlogs Python SDK (`workflow_name=job-brief`)
- Crustdata Company Enrich
- DuckDuckGo (`ddgs`); optional Tavily
- Entire CLI (checkpoints + entire-graph) while building
- cfo.ai for per-brief unit economics

## Build log

### 2026-10-10 — scaffold and tracing-first pipeline (planned → completed in-repo)

- Created `C:\Users\yaswa\briefcase`, git init, moved workspace root, then added code (not before).
- Installed neatlogs-ready CLI: ingest → planner → research → adjudicate → synthesize → verify.
- Stage checkpoints: `runs/<id>/state.json` plus per-stage JSON.
- A/B switch: `--no-priors` vs default credibility priors.
- Recovery switch: `--force-fetch-fail` fails the first fetch then retries.
- Tests: parser heuristic, adjudication priors, 404 citation flag, offline golden brief.
- Verification on 2026-10-10: `.venv\Scripts\python.exe -m pytest -q` passed (5 tests).
- Verification on 2026-10-10: offline CLI produced a cited brief from `tests\fixtures\posting.txt`; neatlogs local doctor passed with 4 captured diagnostic spans.

**Evidence (fill after live runs — do not fabricate dashboard URLs):**

- neatlogs doctor: pending until `NEATLOGS_API_KEY` is in `.env`
- First `job-brief` trace: pending
- A/B traces (with vs without priors): pending — record latency, tokens, cost, unverified-claim count
- Failure/recovery trace: pending (`--force-fetch-fail`)
- Entire checkpoint IDs: pending
- cfo.ai model export: see `docs/business-plan.md` (assumptions; replace with Ari screenshots when credits apply)

## Demo

- Script: `demo/video-script.md` (≤3 minutes; covers neatlogs, Entire, cfo.ai)
- Reproduce: `python -m src.main --text-file tests/fixtures/posting.txt --offline --out brief.md`
- Live (keys required): `python -m src.main --url <posting> --out brief.md`

## Known limitations

- LiteLLM / Crustdata / neatlogs keys are not committed; live traces need a local `.env`
- Role-fit does not ingest a candidate resume yet (posting-only)
- DuckDuckGo can rate-limit; Tavily is the paid fallback
- Snippet-on-page check is best-effort (JS-heavy career pages often fail HTML search)

## Submission

Confirmed from https://neatlogs.com/hackathon (as of 10 Oct 2026):

- [x] Public repo with commits dated during the hackathon (once pushed)
- [ ] Demo video ≤3 min covering neatlogs, Entire, cfo.ai (architecture, implementation, runtime, reasoning, result)
- [ ] Quote the official neatlogs X post in the 12 Oct 19:00–23:55 IST window
- [ ] `#neatHack` build-in-public posts (drafts in `demo/build-in-public.md`)
- [ ] neatlogs traces (A/B + recovery) linked or screenshotted
- [ ] Entire checkpoints / entire-graph output in repo
- [ ] cfo.ai business plan (pricing, costs, revenue, runway)

Do not submit on the builder's behalf. Opening the X draft is not a submission.
