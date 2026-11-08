"""Deterministic evaluation of the graph route visible in generated traces."""

from typing import Any


def _events(instance: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for turn in (instance.get("agent_data") or {}).get("turns", [])
        for event in turn.get("events", [])
    ]


def _trace_text(events: list[dict[str, Any]]) -> str:
    return "\n".join(
        part.get("text", "")
        for event in events
        for part in (event.get("content") or {}).get("parts", [])
        if part.get("text")
    )


def evaluate(instance: dict[str, Any]) -> dict[str, Any]:
    """Score whether each case followed its required graph route and policy."""
    events = _events(instance)
    authors = [event.get("author") for event in events]
    text = _trace_text(events)
    case_id = instance.get("eval_case_id", "")

    if case_id == "complete_intake_valid_route":
        checks = {
            "exact author sequence": authors
            == [
                "consultation_agent",
                "welcome_agent",
                "fitness_onboarding_graph",
            ],
            "booking created": "https://booking.example.com/" in text,
            "email recorded sent": "placeholder welcome email: sent" in text,
            "constraint retained": "knee discomfort" in text.lower(),
            "client retained": "Jordan Lee" in text,
            "no diagnosis or treatment": all(
                phrase not in text.lower()
                for phrase in (
                    "diagnosed with",
                    "medical diagnosis",
                    "prescribed treatment",
                )
            ),
        }
    elif case_id == "incomplete_intake_invalid_route":
        checks = {
            "only terminal root responded": authors == ["fitness_onboarding_graph"],
            "correction explained": "intake needs correction" in text.lower(),
            "missing email identified": "email: field is required" in text,
            "no booking": "booking.example.com" not in text,
            "no email delivery": "placeholder welcome email: sent" not in text,
        }
    else:
        return {"score": 0, "explanation": f"Unknown eval case: {case_id}"}

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "score": 1 if not failed else 0,
        "explanation": (
            "All graph route and policy checks passed."
            if not failed
            else f"Failed checks: {', '.join(failed)}"
        ),
    }
