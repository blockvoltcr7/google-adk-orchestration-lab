"""Nodes for expense policy evaluation, manager approval gate, and settlement."""

import json
from typing import Any
from google.adk.events import Event, EventActions
from app.models import ExpenseClaim, SettlementRecord


def _parse_input(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
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
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        return {
            "claim_id": "EXP-101",
            "employee_name": "Dev User",
            "amount": 120.0,
            "business_justification": "Team lunch",
        }


def assess_expense_risk(node_input: Any) -> Event:
    """Stage 1: Evaluate claim amount against risk policy."""
    data = _parse_input(node_input)
    claim = ExpenseClaim.model_validate(data)

    if claim.amount <= 500.0:
        route = "auto_approve"
        tier = "TIER_1_AUTO"
    else:
        route = "require_approval"
        tier = "TIER_2_MANAGER"

    output = {
        **claim.model_dump(),
        "authorization_tier": tier,
    }
    return Event(
        output=output,
        actions=EventActions(
            route=route,
            state_delta={
                "claim_id": claim.claim_id,
                "amount": claim.amount,
                "authorization_tier": tier,
            },
        ),
    )


def manager_approval_gate(node_input: dict[str, Any]) -> Event:
    """Stage 2 (HITL Gate): Evaluates human signoff decision."""
    decision = str(node_input.get("human_decision") or "").strip().lower()

    if decision in ["approve", "approved", "yes"]:
        route = "approved"
        notes = "Approved by Department Manager after executive review."
    elif decision in ["reject", "rejected", "no"]:
        route = "rejected"
        notes = "Rejected by Department Manager due to missing budget allocation."
    else:
        route = "rejected"
        notes = "Action blocked: Claim exceeded $500 threshold without human manager signoff."

    updated = {
        **node_input,
        "review_notes": notes,
    }
    return Event(
        output=updated,
        actions=EventActions(
            route=route,
            state_delta={"manager_decision": decision, "review_notes": notes},
        ),
    )


def execute_reimbursement(node_input: dict[str, Any]) -> SettlementRecord:
    """Terminal settlement node for approved expenses."""
    claim_id = node_input["claim_id"]
    code = f"DISPATCH-ACH-{abs(hash(claim_id)) % 1000000:06d}"
    tier = node_input.get("authorization_tier", "TIER_1_AUTO")
    return SettlementRecord(
        claim_id=claim_id,
        employee_name=node_input["employee_name"],
        status="REIMBURSED",
        payout_amount=float(node_input["amount"]),
        authorization_tier=tier,
        confirmation_code=code,
        notes=f"Funds scheduled for ACH electronic deposit. {node_input.get('review_notes', 'Auto-cleared under policy.')}",
    )


def notify_rejection(node_input: dict[str, Any]) -> SettlementRecord:
    """Terminal rejection node for denied expenses."""
    return SettlementRecord(
        claim_id=node_input["claim_id"],
        employee_name=node_input["employee_name"],
        status="REJECTED",
        payout_amount=0.0,
        authorization_tier="MANAGER_REVIEW",
        confirmation_code="CLAIM-DENIED-AUDIT-FILED",
        notes=node_input.get("review_notes", "Claim rejected by manager review."),
    )
