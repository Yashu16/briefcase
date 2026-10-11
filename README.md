# Briefcase

Job-intel agent for [neatHack](https://neatlogs.com/hackathon). Paste a job posting URL or text; get a **cited markdown brief** covering company, role-fit, interview loop, compensation, and visa/sponsorship news.

```
posting URL/text
  → ingest (fetch + parse)
  → planner (5 research questions)
  → research (web search + Crustdata)
  → adjudicate (conflict verdicts, optional credibility priors)
  → synthesize (cited markdown)
  → verify (every citation is a live URL)
```

Every stage is a [neatlogs](https://docs.neatlogs.com/sdk/python) span (`workflow_name=job-brief`). Entire checkpoints and `entire graph` are used while building this repo. Unit economics live in [`docs/business-plan.md`](docs/business-plan.md) (cfo.ai).

## Setup

```powershell
cd C:\Users\yaswa\briefcase
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
```

Fill `.env`:

- `NEATLOGS_API_KEY` from [app.neatlogs.com](https://app.neatlogs.com)
- `LITELLM_API_KEY` from [neatlogs.com/hackathon/models](https://neatlogs.com/hackathon/models) (Bedrock is **not** in the hackathon AWS allowance)
- `CRUSTDATA_API_KEY`
- optional `TAVILY_API_KEY` (otherwise DuckDuckGo via `ddgs`)

## Run

```powershell
python -m src.main --url "https://example.com/jobs/senior-swe" --out brief.md
python -m src.main --text-file tests\fixtures\posting.txt --offline --out brief.md
python -m src.main --text-file tests\fixtures\posting.txt --no-priors --offline --out brief-no-priors.md
python -m src.main --url "https://example.com/jobs/senior-swe" --force-fetch-fail
```

`--no-priors` is the A/B switch for judges: same posting, adjudication with vs without credibility priors. Compare the two neatlogs traces (latency, tokens, cost, unverified-claim count).

`--force-fetch-fail` fails the first HTTP fetch, then retries (recovery evidence).

Stage JSON is written under `runs/<id>/` (`posting.json`, `questions.json`, `evidence.json`, `brief.md`, `state.json`).

```powershell
python -m neatlogs doctor --local --json
pytest -q
```

## Partner usage (required)

| Tool | Role |
| --- | --- |
| **neatlogs** | Trace every LLM/tool/stage; compare A/B and failure/recovery runs |
| **Entire** | Checkpoints after ingest, research, first brief; `entire graph` dump in `docs/entire-graph.md` |
| **cfo.ai** | Per-brief cost + freemium / B2B career-center model in `docs/business-plan.md` |

See [`hackathon.md`](hackathon.md) for the evidence log and [`demo/video-script.md`](demo/video-script.md) for the ≤3 minute demo.

## License

MIT — written during neatHack, 10–12 Oct 2026.
