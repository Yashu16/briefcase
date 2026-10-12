# neatHack build log — Briefcase

## Project

**Briefcase** turns a job posting (URL or pasted text) into a cited research brief: company, role-fit, interview loop, compensation, and sponsorship/news. Candidates currently stitch this together from tabs; the agent retrieves evidence, resolves conflicts, and refuses to cite a URL it did not fetch.

## Team

Yaswanth (solo).

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
- Verification on 2026-10-10: credentialed fixture run completed with `21` verdicts and `7` unverified claims. LiteLLM returned HTTP 404 for the configured endpoint, and Crustdata returned HTTP 401; both paths degraded to documented fallbacks without exposing credentials.
- Fixed the Crustdata response-shape boundary so its documented top-level list response is handled correctly, and wired the local API key into the request header. The live fallback run passed afterward.
- Verification on 2026-10-10: corrected LiteLLM endpoint/model returned HTTP 200 for all three model calls in the live fixture run. The run wrote `runs/live-sonnet/` and produced 19 verdicts with 4 unverified claims.
- A/B evidence on the same fixture: `runs/ab-with-priors/` produced 18 verdicts and 5 unverified claims; `runs/ab-without-priors/` produced 14 verdicts and 4 unverified claims. Both used the live LiteLLM endpoint and completed successfully.
- Failure/recovery evidence: `runs/recovery-fetch/` recorded `fetch_retry` after the forced first fetch failure, then completed with 8 verdicts and 0 unverified claims.
- Verification on 2026-10-11: Crustdata required the dashboard-compatible `apikey` header plus `Authorization: Bearer <API key>`. A direct enrichment check returned one record, and the full live run completed with 27 verdicts and 4 unverified claims.

### 2026-10-11 — Real Google Careers URL validation and parser repair

- Tested a real Google Careers posting URL end to end with live fetching, LiteLLM, web research, Crustdata, and citation verification.
- Found and fixed two ingestion issues: page navigation labels leaked into requirements, and an LLM JSON failure caused the fallback parser to label the company `Unknown`.
- URL-aware fallback parsing now recovers `Google`, `United States`, and `google.com` from the Google Careers URL, filters the leaked navigation labels, and produced a cited brief for `Senior Software Engineer, Generative AI/Machine Learning, Google Ads at Google`.
- Full suite after the fix: 7 tests passed.

### 2026-10-11 — Demo progress and readable evidence output

- Added sentence-aware evidence shortening so long claims end at a complete sentence when possible, or use an explicit `...` at a word boundary.
- Added six-stage CLI progress output covering ingest, parsing, planning, research, adjudication/citation verification, and brief writing.
- HTTP request logs remain available for debugging, while the stage lines provide a concise demo-friendly summary.
- Full suite after the change: 9 tests passed.
- Web-search evidence is now rewritten into one concise, source-grounded sentence by LiteLLM before it enters the brief; the original snippet remains stored for citation verification. The output label is `Source credibility` to distinguish source priors from claim truth probability.

### 2026-10-11 — Crustdata evidence routing and formatting cleanup

- Restricted Crustdata enrichment to the Company research question so funding, news, and leadership records no longer appear in Compensation or Sponsorship sections.
- Replaced raw funding dictionaries with readable acquisition/investor claims, prefixed news claims with the company name, and skipped records without a named person or news title.
- Preserved Crustdata provenance for source credibility, including shortened company URLs returned by the service.
- Live Google rerun produced one readable acquisition finding under Company; unrelated duplicate `news` / `leader` findings were removed. Full suite: 11 tests passed.

**Evidence (fill after live runs — do not fabricate dashboard URLs):**

- neatlogs doctor: local diagnostic capture passed with `NEATLOGS_API_KEY` configured
- First `job-brief` trace: live LiteLLM and Crustdata run completed; dashboard trace URL pending
- A/B traces (with vs without priors): `runs/ab-with-priors/` and `runs/ab-without-priors/` captured; dashboard latency/token/cost fields pending
- Failure/recovery trace: captured in `runs/recovery-fetch/` with `fetch_retry`; dashboard link pending
- Entire graph evidence: captured and committed; GitHub repository mirrored in Entire at `aws-us-east-2`. Session checkpoint IDs remain pending because this session uses Copilot SDK rather than the configured Claude Code integration. See `docs/entire-graph.md`.
- cfo.ai model export: sanitized workbook `Briefcase — Runway & decisions.xlsx` summarized in `docs/business-plan.md`; includes base, conservative, growth, 5% conversion, doubled-Crustdata, and full-allowance stress cases

## Demo

- Recorded demo video: [Google Drive](https://drive.google.com/file/d/1ytcZE7jDnrAHu9eQlAAM5m-hIwSo6-lr/view?usp=sharing)
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
- [x] Demo video ≤3 min covering neatlogs, Entire, cfo.ai (architecture, implementation, runtime, reasoning, result) — [watch on Google Drive](https://drive.google.com/file/d/1ytcZE7jDnrAHu9eQlAAM5m-hIwSo6-lr/view?usp=sharing)
- [ ] Quote the official neatlogs X post in the 12 Oct 19:00–23:55 IST window
- [ ] `#neatHack` build-in-public posts
- [ ] neatlogs traces (A/B + recovery) linked or screenshotted
- [ ] Entire checkpoints / entire-graph output in repo
- [x] cfo.ai business plan (pricing, costs, revenue, runway)

Do not submit on the builder's behalf. Opening the X draft is not a submission.
