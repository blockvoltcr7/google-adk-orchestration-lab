"""Deterministic trace evaluation for the cyclic refinement spec generator."""

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

    # Verify that the spec successfully went through at least 2 iterations and published
    iterations = last_output.get("iterations_taken", 0)
    score = last_output.get("final_score", 0)
    status = last_output.get("status", "")

    passed = (status == "APPROVED_AND_PUBLISHED") and (iterations >= 2) and (score >= 85)

    return {
        "score": 1.0 if passed else 0.0,
        "explanation": (
            f"Spec completed {iterations} iterations, reaching quality score {score}/100 "
            f"before publishing."
            if passed
            else f"Failed quality bar: status={status}, iterations={iterations}, score={score}"
        ),
    }
