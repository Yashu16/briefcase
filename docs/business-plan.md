# Briefcase unit economics (cfo.ai)

Modeled as **one API call = one brief**. Numbers below are a founder-ready starting model for Ari / cfo.ai. Replace token and Crustdata rows with the first live neatlogs trace once keys are in `.env`. Do not treat these as measured dashboard figures until a trace is pasted here.

Hackathon note: if you sign up at cfo.ai with a card, cancel immediately in Settings → Billing. neatHack credits come from the event team.

## Unit: one brief

| Line | Assumption | Cost / brief (USD) |
| --- | --- | ---: |
| LiteLLM inference (plan + parse + 5 research synthesizers + brief) | ~40k tokens blended @ hackathon Claude/Nova list | 0.12 |
| Web search | DuckDuckGo $0; Tavily ~5 queries if enabled | 0.00–0.05 |
| Crustdata enrich | 1 company enrich + news/people fields | 0.08 |
| neatlogs ingest | included on Pro trial / hackathon | 0.00 |
| **COGS / brief** | | **~0.20–0.25** |

Use neatlogs span cost on workflow `job-brief` as the source of truth after the first successful live run.

## Pricing

| Tier | Price | Included | Who |
| --- | --- | --- | --- |
| Freemium | $0 | 3 briefs / week, citations, no CSV export | students, individual hunters |
| Pro | $19 / month | 40 briefs, A/B traces, resume-fit (roadmap) | active candidates |
| Career center (B2B) | $8 / seat / month (min 50 seats) **or** $1.50 / brief overage | SSO-lite, shared workspace, weekly digest | university career centers, bootcamps |

Gross margin on Pro at 40 briefs × $0.22 COGS = $8.80 cost vs $19 revenue ≈ **54%** before support. B2B overage at $1.50 vs $0.22 COGS ≈ **85%**.

## Monthly scenarios (illustrative)

| | Conservative | Base | Growth |
| --- | --- | --- | --- |
| Freemium users | 400 | 1,200 | 4,000 |
| Pro subs | 40 | 120 | 400 |
| B2B seats | 0 | 100 | 400 |
| MRR | $760 | $3,080 | $10,800 |
| Briefs rendered | 1,200 | 5,000 | 18,000 |
| COGS | $264 | $1,100 | $3,960 |
| Gross profit | $496 | $1,980 | $6,840 |
| Gross margin | 65% | 64% | 63% |

Fixed monthly (founder-draw $0 during hackathon): LiteLLM reserved $20 event budget, Crustdata 5,000 event credits, hosting $0 (CLI). Post-event SaaS: $80 infra + $40 neatlogs Pro + $50 search = **$170 opex**.

## Runway

At Base MRR $3,080 and $170 opex + $1,100 COGS, contribution is positive. Seed cash $25k (example) / net burn if growth spend is $4k/month marketing → **~6 months** runway before needing the B2B career-center contract.

## What to load into cfo.ai / Ari

1. Variable `cogs_per_brief` = neatlogs-measured $
2. Dimension `tier` = freemium | pro | career_center
3. Drivers: `briefs_per_pro_user` = 40, `seats`, `conversion_freemium_to_pro` = 10%
4. Scenarios Conservative / Base / Growth as above
5. Ask Ari: “Show cash runway if Pro conversion is 5% vs 10% and Crustdata cost doubles.”

Paste Ari’s table/export below when available.

### Ari export (pending)

_No live cfo.ai export in this file yet. Assumptions above are the model to type into Ari on Monday office hours if credits arrive late._
