"""Deterministic trace evaluation for the sequential order pipeline."""

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

    # Look for terminal output in events
    outputs = [e.get("output") for e in events if e.get("output")]
    last_output = outputs[-1] if outputs else {}

    if case_id == "standard_order_under_100":
        passed = (
            last_output.get("status") == "CONFIRMED"
            and "Alice Smith" in last_output.get("customer_name", "")
            and "INV-" in last_output.get("invoice_number", "")
            and float(last_output.get("grand_total", 0.0)) > 45.0
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Order confirmed with valid invoice and under-100 shipping fee applied.",
        }

    elif case_id == "premium_order_over_100":
        passed = (
            last_output.get("status") == "CONFIRMED"
            and "Robert Johnson" in last_output.get("customer_name", "")
            and "INV-" in last_output.get("invoice_number", "")
            and float(last_output.get("grand_total", 0.0)) >= 299.99
        )
        return {
            "score": 1.0 if passed else 0.0,
            "explanation": "Order confirmed with valid invoice and over-100 free shipping applied.",
        }

    return {"score": 0.0, "explanation": f"Unknown case id: {case_id}"}
