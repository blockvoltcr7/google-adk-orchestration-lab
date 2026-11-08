"""Deterministic trace evaluation for dynamic orchestration."""

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

    if case_id == "dynamic_clean_document":
        passed = (
            last.get("total_sections") == 2
            and last.get("flagged_sections_count") == 0
            and last.get("status") == "CLEARED"
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Clean document dynamically mapped over 2 sections with 0 flags.",
        }

    elif case_id == "dynamic_risk_document":
        passed = (
            last.get("total_sections") == 3
            and last.get("flagged_sections_count") == 1
            and last.get("status") == "AUDIT_FLAGGED"
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Document dynamically mapped over 3 sections, correctly flagging risk breach.",
        }

    return {"score": 0.0, "explanation": f"Unknown case: {case_id}"}
