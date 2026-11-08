"""Parsing, validation, and invalid-route response nodes.

This module provides the intake validation gate node (``validate_intake``) that controls
graph routing between the valid intake branch (consultation/booking/email) and the
invalid intake branch (correction response), as well as the terminal response node
(``render_intake_correction``) for invalid submissions.
"""

import json
from typing import Any

from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.genai import types
from pydantic import ValidationError

from app.models import ClientIntake, IntakeValidationResult


def _extract_text(content: types.Content) -> str:
    """Join text parts from the incoming ADK user message content.

    Strips surrounding markdown code blocks (e.g. ```json ... ```) if present.

    Args:
        content: Incoming ADK user message content containing text parts.

    Returns:
        Stripped text content string.
    """
    text = "".join(part.text or "" for part in content.parts or []).strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return text


def _parse_payload(content: types.Content) -> dict[str, Any]:
    """Parse either raw JSON or a production-like text wrapper containing JSON.

    Args:
        content: Incoming ADK user message content.

    Returns:
        Parsed JSON object as a Python dictionary.

    Raises:
        json.JSONDecodeError: If JSON decoding fails entirely.
        ValueError: If the parsed JSON payload is not a dictionary.
    """
    text = _extract_text(content)
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end <= start:
            raise
        payload = json.loads(text[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("the intake must be a JSON object")
    return payload


def _safe_provided_fields(payload: dict[str, Any]) -> dict[str, str]:
    """Retain only supplied non-empty string fields belonging to the intake contract.

    Args:
        payload: Parsed raw input payload dictionary.

    Returns:
        Filtered dictionary containing valid fields present in ``ClientIntake``.
    """
    return {
        key: value.strip()
        for key, value in payload.items()
        if key in ClientIntake.model_fields and isinstance(value, str) and value.strip()
    }


def _format_validation_errors(error: ValidationError) -> list[str]:
    """Convert Pydantic validation details into stable, client-safe error strings.

    Args:
        error: Pydantic ``ValidationError`` exception instance.

    Returns:
        List of formatted error string messages (e.g. "email: value is not a valid email address").
    """
    messages = []
    for detail in error.errors(include_url=False, include_input=False):
        location = ".".join(str(part) for part in detail["loc"])
        message = "field is required" if detail["type"] == "missing" else detail["msg"]
        messages.append(f"{location}: {message}")
    return messages


def validate_intake(node_input: types.Content) -> Event:
    """Parse the user's JSON intake and route valid vs invalid submissions.

    Attempts to extract and validate a ``ClientIntake`` model from the user message.
    Sets the workflow routing signal (`valid` vs `invalid`) and populates session state.

    Args:
        node_input: Incoming user message ``types.Content``.

    Returns:
        An ``Event`` containing:
            - output: Validated intake profile dictionary if valid, or validation summary if invalid.
            - actions: ``EventActions`` with ``route`` set to 'valid' or 'invalid', and ``state_delta``.
    """
    payload: dict[str, Any] = {}
    try:
        payload = _parse_payload(node_input)
        intake = ClientIntake.model_validate(payload)
    except json.JSONDecodeError as error:
        result = IntakeValidationResult(
            status="invalid",
            client_profile=None,
            errors=[f"message: invalid JSON ({error.msg})"],
            provided_fields={},
        )
    except ValidationError as error:
        result = IntakeValidationResult(
            status="invalid",
            client_profile=None,
            errors=_format_validation_errors(error),
            provided_fields=_safe_provided_fields(payload),
        )
    except ValueError as error:
        result = IntakeValidationResult(
            status="invalid",
            client_profile=None,
            errors=[f"message: {error}"],
            provided_fields=_safe_provided_fields(payload),
        )
    else:
        result = IntakeValidationResult(
            status="valid",
            client_profile=intake,
            errors=[],
            provided_fields=_safe_provided_fields(payload),
        )

    serialized = result.model_dump(mode="json")
    output = (
        result.client_profile.model_dump(mode="json")
        if result.client_profile is not None
        else serialized
    )
    return Event(
        output=output,
        actions=EventActions(
            route=result.status,
            state_delta={
                "intake_status": result.status,
                "client_profile": serialized["client_profile"],
                "intake_errors": result.errors,
            },
        ),
    )


def render_intake_correction(node_input: IntakeValidationResult) -> Event:
    """Emit a terminal correction response for the invalid graph route.

    Formats user-friendly error details explaining missing or invalid fields
    and prompts the user to resubmit a complete intake.

    Args:
        node_input: The ``IntakeValidationResult`` emitted by ``validate_intake`` when status is 'invalid'.

    Returns:
        An ``Event`` containing:
            - content: Model response text containing formatted error instructions.
            - output: JSON dictionary representation of the ``IntakeValidationResult``.
    """
    fields = "\n".join(f"- {error}" for error in node_input.errors)
    goal = node_input.provided_fields.get("primary_goal")
    context = ""
    if goal:
        context = f" for the submitted goal to {goal.lower()}"
    text = (
        f"I could not start onboarding{context} because the intake needs correction:\n"
        f"{fields}\n\n"
        "Please submit the complete intake again."
    )
    return Event(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=text)],
        ),
        output=node_input.model_dump(mode="json"),
    )

