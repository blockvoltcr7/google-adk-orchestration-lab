"""Deterministic trace evaluation for explicit fan-in JoinNode graph."""

from typing import Any


def _events(instance: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for turn in (instance.get("agent_data") or {}).get("turns", [])
        for event in turn.get("events", [])
    ]


def evaluate(instance: dict[str, Any]) -> dict[str, Any]:
    events = _events(instance)
    outputs = [e.get("output") for e in events if e.get("output")]
    last_output = outputs[-1] if outputs else {}

    # Verify that the final dossier consolidated outputs from all 3 branches
    has_financial = "Growth" in last_output.get("financial_summary", "")
    has_competitive = "Moat" in last_output.get("competitive_summary", "")
    has_compliance = "Sanctions" in last_output.get("compliance_summary", "")
    has_verdict = last_output.get("investment_verdict") in ["STRONG BUY", "HOLD"]

    passed = has_financial and has_competitive and has_compliance and has_verdict

    return {
        "score": 1.0 if passed else 0.0,
        "explanation": (
            "JoinNode aggregated all 3 parallel branches (financial, competitive, compliance) "
            "into the synthesized executive dossier."
            if passed
            else "Failed to synchronize or synthesize all 3 branches."
        ),
    }
