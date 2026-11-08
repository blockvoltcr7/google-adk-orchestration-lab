"""Deterministic client-intake validation tool."""

from typing import Any

from google.adk.tools import ToolContext
from pydantic import ValidationError

from app.models import ClientIntake, IntakeValidationResult


def _format_validation_errors(error: ValidationError) -> list[str]:
    """Convert Pydantic errors into stable, client-safe messages."""
    messages = []
    for detail in error.errors(include_url=False, include_input=False):
        location = ".".join(str(part) for part in detail["loc"])
        message = "field is required" if detail["type"] == "missing" else detail["msg"]
        messages.append(f"{location}: {message}")
    return messages


def validate_client_intake(
    payload: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Validate and normalize an already-qualified client's intake form.

    Args:
        payload: Intake fields explicitly provided by the client.

    Returns:
        Validation status, normalized client profile, and field-level errors.
    """
    try:
        intake = ClientIntake.model_validate(payload)
    except ValidationError as error:
        errors = _format_validation_errors(error)
        result = IntakeValidationResult(
            status="invalid",
            client_profile={},
            errors=errors,
        )
    else:
        result = IntakeValidationResult(
            status="valid",
            client_profile=intake.model_dump(mode="json"),
            errors=[],
        )

    serialized = result.model_dump(mode="json")
    tool_context.state["intake_status"] = result.status
    tool_context.state["client_profile"] = serialized["client_profile"]
    tool_context.state["intake_errors"] = serialized["errors"]
    return serialized
