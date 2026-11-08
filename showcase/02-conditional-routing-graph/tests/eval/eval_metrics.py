"""Deterministic trace evaluation for the conditional routing service desk."""

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
    last_output = outputs[-1] if outputs else {}

    if case_id == "route_billing_inquiry":
        passed = (
            last_output.get("department") == "Billing & Payments"
            and last_output.get("ticket_id") == "BILL-01"
            and "Finance Desk Agent" in last_output.get("assigned_specialist", "")
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Billing inquiry properly triaged and resolved by Billing specialist.",
        }

    elif case_id == "route_technical_bug":
        passed = (
            last_output.get("department") == "Engineering Support"
            and last_output.get("ticket_id") == "TECH-02"
            and "Site Reliability Engineer" in last_output.get("assigned_specialist", "")
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Technical bug triaged and assigned to Engineering with 2h SLA.",
        }

    elif case_id == "route_default_fallback":
        passed = (
            last_output.get("department") == "General Customer Care"
            and last_output.get("ticket_id") == "GEN-03"
            and "Frontline Care Agent" in last_output.get("assigned_specialist", "")
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Unmatched general inquiry caught by DEFAULT_ROUTE fallback handler.",
        }

    return {"score": 0.0, "explanation": f"Unknown eval case: {case_id}"}
