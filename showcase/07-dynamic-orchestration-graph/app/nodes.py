"""Child worker and reducer nodes invoked dynamically via ctx.run_node."""

import json
from typing import Any
from app.models import SectionAnalysis, BatchSummaryReport


def analyze_section(node_input: Any) -> dict[str, Any]:
    """Child worker node: analyzes an individual document section."""
    if isinstance(node_input, str):
        data = json.loads(node_input)
    else:
        data = node_input

    heading = data.get("heading", "Section")
    content = str(data.get("content", ""))
    content_lower = content.lower()

    risk_keywords = ["liability", "vulnerability", "breach", "penalty", "outage", "failure"]
    has_risk = any(k in content_lower for k in risk_keywords)

    findings = [
        f"Analyzed {heading}: {len(content.split())} words.",
    ]
    if has_risk:
        findings.append(f"Risk marker detected in {heading}.")

    analysis = SectionAnalysis(
        section_index=int(data.get("section_index", 0)),
        heading=heading,
        key_findings=findings,
        has_risk=has_risk,
    )
    return analysis.model_dump()


def synthesize_batch(node_input: dict[str, Any]) -> BatchSummaryReport:
    """Child reducer node: aggregates dynamic worker results into final report."""
    doc_id = node_input.get("doc_id", "DOC-001")
    title = node_input.get("title", "Batch Document")
    analyses = node_input.get("analyses", [])

    total = len(analyses)
    flagged = sum(1 for a in analyses if a.get("has_risk"))
    status = "AUDIT_FLAGGED" if flagged > 0 else "CLEARED"

    digest = (
        f"Processed {total} dynamic sections for '{title}'. "
        f"{flagged} sections flagged for potential risk. Overall status: {status}."
    )

    return BatchSummaryReport(
        doc_id=doc_id,
        title=title,
        total_sections=total,
        flagged_sections_count=flagged,
        executive_digest=digest,
        status=status,
    )
