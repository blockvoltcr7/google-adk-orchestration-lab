"""Parallel branch nodes and synthesis node for explicit fan-in graph."""

import json
from typing import Any
from app.models import (
    CompanyTarget,
    FinancialAnalysis,
    CompetitiveAnalysis,
    ComplianceAudit,
    ExecutiveDossier,
)


def _parse_input(raw: Any) -> CompanyTarget:
    if isinstance(raw, dict):
        return CompanyTarget.model_validate(raw)
    text = getattr(raw, "text", None)
    if text is None and hasattr(raw, "parts"):
        text = "".join(getattr(p, "text", "") or "" for p in raw.parts)
    elif not isinstance(text, str):
        text = str(raw)
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    try:
        data = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            data = json.loads(text[start : end + 1])
        else:
            data = {"name": "Example Corp", "ticker": "EXMPL", "industry": "Software"}
    return CompanyTarget.model_validate(data)


def analyze_financials(node_input: Any) -> dict[str, Any]:
    """Parallel branch 1: Analyze financial statements."""
    target = _parse_input(node_input)
    analysis = FinancialAnalysis(
        financial_score=88,
        revenue_growth_yoy="+24.5%",
        ebitda_margin="31.2%",
        balance_sheet_strength="Strong (Debt-to-Equity 0.35)",
    )
    return {
        "company_name": target.name,
        "ticker": target.ticker,
        **analysis.model_dump(),
    }


def evaluate_competitors(node_input: Any) -> dict[str, Any]:
    """Parallel branch 2: Analyze competitive positioning."""
    target = _parse_input(node_input)
    comp = CompetitiveAnalysis(
        market_share_pct="34.0%",
        moat_rating="Wide",
        primary_competitor="MegaCorp Global",
    )
    return {
        "company_name": target.name,
        **comp.model_dump(),
    }


def audit_compliance(node_input: Any) -> dict[str, Any]:
    """Parallel branch 3: Verify regulatory & compliance health."""
    target = _parse_input(node_input)
    comp = ComplianceAudit(
        regulatory_status="Good Standing",
        sanctions_clearance=True,
        risk_level="Low",
    )
    return {
        "company_name": target.name,
        **comp.model_dump(),
    }


def synthesize_executive_dossier(node_input: dict[str, Any]) -> ExecutiveDossier:
    """Downstream aggregation node consuming JoinNode output dictionary."""
    fin = node_input.get("analyze_financials", {})
    comp = node_input.get("evaluate_competitors", {})
    sec = node_input.get("audit_compliance", {})

    company_name = fin.get("company_name") or comp.get("company_name") or "Target Corp"
    ticker = fin.get("ticker", "UNKNOWN")

    score = int(fin.get("financial_score", 75))
    verdict = "STRONG BUY" if score >= 80 else "HOLD"

    return ExecutiveDossier(
        company_name=company_name,
        ticker=ticker,
        overall_health_score=score,
        investment_verdict=verdict,
        financial_summary=f"Growth {fin.get('revenue_growth_yoy')}, EBITDA Margin {fin.get('ebitda_margin')}",
        competitive_summary=f"Market Share {comp.get('market_share_pct')}, Moat: {comp.get('moat_rating')}",
        compliance_summary=f"Status: {sec.get('regulatory_status')}, Sanctions Clean: {sec.get('sanctions_clearance')}",
    )
