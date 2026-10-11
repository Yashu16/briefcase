from __future__ import annotations

from src.models import Brief, Evidence, JobPosting, Topic, UnverifiedClaim, Verdict
from src.tracing import span
from src.verify.citations import citation_ids

SECTION_ORDER = (
    (Topic.company, "Company"),
    (Topic.role_fit, "Role fit"),
    (Topic.interview, "Interview loop"),
    (Topic.comp, "Compensation"),
    (Topic.sponsorship, "Sponsorship and news"),
)


def render_markdown(
    posting: JobPosting,
    verdicts: list[Verdict],
    evidence: list[Evidence],
    unverified: list[UnverifiedClaim],
) -> str:
    ids = citation_ids(evidence)
    lines: list[str] = [
        f"# Briefcase brief: {posting.title} at {posting.company}",
        "",
        f"**Location:** {posting.location or 'n/a'}  ",
        f"**Source:** {posting.raw_url or 'pasted text'}",
        "",
        "## Requirements (from posting)",
    ]
    if posting.requirements:
        lines.extend(f"- {r}" for r in posting.requirements)
    else:
        lines.append("- (none extracted)")
    lines.append("")

    by_topic: dict[Topic, list[Verdict]] = {t: [] for t, _ in SECTION_ORDER}
    leftover: list[Verdict] = []
    for v in verdicts:
        if v.topic in by_topic:
            by_topic[v.topic].append(v)
        else:
            leftover.append(v)

    used_urls: set[str] = set()
    for topic, heading in SECTION_ORDER:
        lines.append(f"## {heading}")
        items = by_topic[topic]
        if not items:
            lines.append("_Insufficient evidence._")
            lines.append("")
            continue
        for v in items:
            cites = []
            for url in v.sources:
                if url in ids:
                    cites.append(f"[{ids[url]}]")
                    used_urls.add(url)
            cite = "".join(dict.fromkeys(cites)) or ""
            lines.append(f"- {v.verdict} {cite}".rstrip())
            lines.append(f"  - Confidence: {v.confidence:.2f}. {v.rationale}")
            if v.dissent:
                lines.append(f"  - Dissent: {v.dissent}")
        lines.append("")

    if leftover:
        lines.append("## Other findings")
        for v in leftover:
            lines.append(f"- {v.verdict}")
        lines.append("")

    lines.append("## Sources")
    # Only URLs that actually appear in evidence (citation honesty).
    inverted = {n: url for url, n in ids.items()}
    for n in sorted(inverted):
        url = inverted[n]
        name = next((e.source_name for e in evidence if e.source_url == url), url)
        lines.append(f"{n}. [{name}]({url})")
    lines.append("")

    if unverified:
        lines.append("## Needs confirmation")
        for u in unverified:
            lines.append(f"- {u.claim} — `{u.source_url}` ({u.reason})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


@span(kind="CHAIN", name="synthesize_brief")
def synthesize(
    posting: JobPosting,
    verdicts: list[Verdict],
    evidence: list[Evidence],
    unverified: list[UnverifiedClaim],
) -> Brief:
    md = render_markdown(posting, verdicts, evidence, unverified)
    return Brief(markdown=md, verdicts=verdicts, evidence=evidence, unverified_claims=unverified)
