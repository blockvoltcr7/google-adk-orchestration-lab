"""Tests for intake parsing, validation, and routing."""

import json

from google.genai import types

from app.models import IntakeValidationResult
from app.tools.intake import render_intake_correction, validate_intake

COMPLETE_INTAKE = {
    "name": "Jordan Lee",
    "email": "jordan@example.com",
    "primary_goal": "Build consistent strength",
    "experience_level": "Beginner",
    "availability": "Monday, Wednesday, and Friday evenings",
    "physical_constraints": "Previous knee discomfort; avoid assumptions",
    "preferred_consultation_time": "Tuesday at 6:00 PM Eastern",
}


def _content(payload: object) -> types.Content:
    return types.Content(
        role="user",
        parts=[types.Part.from_text(text=json.dumps(payload))],
    )


def test_complete_intake_routes_to_valid_and_normalizes_state() -> None:
    event = validate_intake(_content(COMPLETE_INTAKE))

    assert event.actions.route == "valid"
    assert event.output["name"] == "Jordan Lee"
    assert event.actions.state_delta["intake_status"] == "valid"
    assert event.actions.state_delta["client_profile"]["email"] == "jordan@example.com"
    assert event.actions.state_delta["intake_errors"] == []


def test_instruction_with_embedded_json_is_supported() -> None:
    content = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=(
                    "Onboard this qualified fitness client using the intake:\n"
                    f"{json.dumps(COMPLETE_INTAKE)}"
                )
            )
        ],
    )
    event = validate_intake(content)

    assert event.actions.route == "valid"
    assert event.output["email"] == "jordan@example.com"


def test_incomplete_intake_routes_to_terminal_correction() -> None:
    event = validate_intake(
        _content(
            {
                "name": "Jordan Lee",
                "primary_goal": "Build consistent strength",
            }
        )
    )

    assert event.actions.route == "invalid"
    result = IntakeValidationResult.model_validate(event.output)
    assert result.client_profile is None
    assert any(error.startswith("email:") for error in result.errors)

    response = render_intake_correction(result)
    assert response.content is not None
    text = response.content.parts[0].text or ""
    assert "intake needs correction" in text
    assert "email:" in text
    assert "submitted goal to build consistent strength" in text


def test_non_json_message_routes_to_invalid() -> None:
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Please onboard Jordan")],
    )
    event = validate_intake(content)

    assert event.actions.route == "invalid"
    assert event.output["errors"][0].startswith("message: invalid JSON")
