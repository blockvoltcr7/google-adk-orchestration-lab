"""Deterministic trace evaluation for the HITL expense authorization graph."""

from typing import Any


def _events(instance: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for turn in (instance.get("agent_data") or {}).get("turns", [])
        for event in turn.get("events", [])
    ]


def evaluate(instance: dict[str, Any]) -> dict[str, Any]:
    events = _events(instance)
    case_id = instance.get("eval_case_id", "")
    outputs = [e.get("output") for e in events if e.get("output")]
    last = outputs[-1] if outputs else {}

    if case_id == "auto_approve_small_expense":
        passed = (
            last.get("status") == "REIMBURSED"
            and last.get("payout_amount") == 120.0
            and last.get("authorization_tier") == "TIER_1_AUTO"
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Small expense under $500 auto-approved according to policy.",
        }

    elif case_id == "high_value_approved":
        passed = (
            last.get("status") == "REIMBURSED"
            and last.get("payout_amount") == 1800.0
            and "Approved by Department Manager" in last.get("notes", "")
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "High-value expense successfully authorized following human manager signoff.",
        }

    elif case_id == "high_value_rejected":
        passed = (
            last.get("status") == "REJECTED"
            and last.get("payout_amount") == 0.0
            and "Rejected by Department Manager" in last.get("notes", "")
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "High-value expense blocked and denied following manager review rejection.",
        }

    return {"score": 0.0, "explanation": f"Unknown case: {case_id}"}
