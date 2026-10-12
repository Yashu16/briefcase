from __future__ import annotations

import re
from collections import defaultdict

from src.models import Evidence, Topic, Verdict
from src.tracing import span

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    stop = {"the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "at", "is", "are"}
    return {t for t in _TOKEN.findall(text.lower()) if t not in stop and len(t) > 2}


def _similar(a: Evidence, b: Evidence) -> bool:
    ta, tb = _tokens(a.claim), _tokens(b.claim)
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / max(1, min(len(ta), len(tb)))
    return overlap >= 0.45


def _cluster(items: list[Evidence]) -> list[list[Evidence]]:
    clusters: list[list[Evidence]] = []
    for item in items:
        placed = False
        for cluster in clusters:
            if any(_similar(item, other) for other in cluster):
                cluster.append(item)
                placed = True
                break
        if not placed:
            clusters.append([item])
    return clusters


def _winner(cluster: list[Evidence], use_priors: bool) -> tuple[Evidence, Evidence | None]:
    ranked = sorted(cluster, key=lambda e: (e.credibility if use_priors else 0.5, len(e.snippet)), reverse=True)
    best = ranked[0]
    dissent_src = None
    for other in ranked[1:]:
        if other.source_url != best.source_url and not _similar(best, other):
            dissent_src = other
            break
        if other.credibility + 0.15 < best.credibility and other.source_url != best.source_url:
            dissent_src = other
            break
    if dissent_src is None and len(ranked) > 1 and ranked[-1].source_url != best.source_url:
        # Prefer a lower-credibility source as dissent for the A/B story.
        if ranked[-1].credibility < best.credibility:
            dissent_src = ranked[-1]
    return best, dissent_src


@span(kind="CHAIN", name="adjudicate")
def adjudicate(evidence: list[Evidence], *, use_priors: bool = True) -> list[Verdict]:
    by_q: dict[str, list[Evidence]] = defaultdict(list)
    for ev in evidence:
        by_q[ev.question_id or "q"].append(ev)

    verdicts: list[Verdict] = []
    for qid, items in by_q.items():
        for cluster in _cluster(items):
            best, dissent = _winner(cluster, use_priors)
            conf = best.credibility if use_priors else min(0.55, 0.35 + 0.05 * len(cluster))
            if not use_priors:
                # Without priors, treat sources as equal — confidence stays mid and dissent is noisier.
                conf = min(0.6, 0.4 + 0.04 * len(cluster))
            topic = None
            if qid.startswith("q"):
                mapping = {"q1": Topic.company, "q2": Topic.role_fit, "q3": Topic.interview, "q4": Topic.comp, "q5": Topic.sponsorship}
                topic = mapping.get(qid)
            verdicts.append(
                Verdict(
                    claim=best.claim,
                    verdict=best.claim,
                    confidence=round(conf, 3),
                    rationale=(
                        f"Chose {best.source_name} ({best.source_url}) "
                        + (
                            f"because source credibility prior {best.credibility:.2f} beat alternatives."
                            if use_priors
                            else "without credibility priors; first/longest snippet in the cluster won."
                        )
                    ),
                    sources=[e.source_url for e in cluster],
                    dissent=None if dissent is None else dissent.claim,
                    topic=topic,
                )
            )
    return verdicts
