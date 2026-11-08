"""Deterministic multi-agent trajectory metric for onboarding tool policy."""

import json

REQUIRED_INTAKE_FIELDS = {
    "name",
    "email",
    "primary_goal",
    "experience_level",
    "availability",
    "physical_constraints",
    "preferred_consultation_time",
}
EXPECTED_AUTHORS = [
    "intake_agent",
    "consultation_agent",
    "welcome_agent",
]


def _prompt_payload(instance):
    prompt = instance.get("prompt") or {}
    parts = prompt.get("parts") or []
    text = parts[0].get("text", "") if parts else ""
    try:
        payload = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _trace_summary(instance):
    authors = []
    tool_calls = []
    agent_data = instance.get("agent_data") or {}
    for turn in agent_data.get("turns") or []:
        for event in turn.get("events") or []:
            author = event.get("author")
            if author and author not in authors:
                authors.append(author)
            content = event.get("content") or {}
            for part in content.get("parts") or []:
                function_call = part.get("function_call") or part.get("functionCall")
                if function_call:
                    tool_calls.append(function_call.get("name"))
    return authors, tool_calls


def evaluate(instance):
    """Score exact agent order and valid/invalid tool-call policy."""
    payload = _prompt_payload(instance)
    authors, tool_calls = _trace_summary(instance)
    intake_is_complete = REQUIRED_INTAKE_FIELDS.issubset(payload) and all(
        payload[field] for field in REQUIRED_INTAKE_FIELDS
    )
    expected_tools = (
        [
            "validate_client_intake",
            "create_booking_link",
            "send_welcome_email",
        ]
        if intake_is_complete
        else ["validate_client_intake"]
    )

    errors = []
    if authors != EXPECTED_AUTHORS:
        errors.append(f"expected authors {EXPECTED_AUTHORS}, got {authors}")
    if tool_calls != expected_tools:
        errors.append(f"expected tools {expected_tools}, got {tool_calls}")

    return {
        "score": 0.0 if errors else 1.0,
        "explanation": "; ".join(errors)
        if errors
        else "Agent and tool order is correct.",
    }
