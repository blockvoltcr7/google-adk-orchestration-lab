"""Unit tests for deterministic local onboarding tools."""

from typing import cast

from google.adk.tools import ToolContext

from app.tools import (
    create_booking_link,
    send_welcome_email,
    validate_client_intake,
)


class StubToolContext:
    """Minimal state container needed by the local tools."""

    def __init__(self) -> None:
        self.state: dict[str, object] = {}


def tool_context() -> ToolContext:
    """Create a duck-typed ToolContext for deterministic unit tests."""
    return cast(ToolContext, StubToolContext())


def valid_intake() -> dict[str, str]:
    """Return a complete fictional intake fixture."""
    return {
        "name": "Jordan Lee",
        "email": "jordan@example.com",
        "primary_goal": "Build consistent strength",
        "experience_level": "Beginner",
        "availability": "Monday, Wednesday, and Friday evenings",
        "physical_constraints": "Previous knee discomfort",
        "preferred_consultation_time": "Tuesday at 6:00 PM Eastern",
    }


def test_validate_client_intake_writes_normalized_valid_state() -> None:
    context = tool_context()

    result = validate_client_intake(valid_intake(), context)

    assert result["status"] == "valid"
    assert result["errors"] == []
    assert result["client_profile"]["name"] == "Jordan Lee"
    assert context.state["intake_status"] == "valid"
    assert context.state["client_profile"] == result["client_profile"]


def test_validate_client_intake_writes_invalid_state_without_inventing_fields() -> None:
    context = tool_context()

    result = validate_client_intake({"name": "Jordan Lee"}, context)

    assert result["status"] == "invalid"
    assert result["client_profile"] == {}
    assert any(error.startswith("email:") for error in result["errors"])
    assert context.state["intake_status"] == "invalid"
    assert context.state["client_profile"] == {}


def test_create_booking_link_is_deterministic_and_updates_state() -> None:
    first_context = tool_context()
    second_context = tool_context()

    first = create_booking_link(
        "Jordan Lee",
        "jordan@example.com",
        "Tuesday at 6:00 PM Eastern",
        first_context,
    )
    second = create_booking_link(
        "Jordan Lee",
        "jordan@example.com",
        "Tuesday at 6:00 PM Eastern",
        second_context,
    )

    assert first == second
    assert first["booking_url"].startswith(
        "https://booking.example.com/fitness-consultation/"
    )
    assert first_context.state["booking_result"] == first


def test_send_welcome_email_is_deterministic_and_updates_state() -> None:
    first_context = tool_context()
    second_context = tool_context()
    body = (
        "Welcome, Jordan. Book at "
        "https://booking.example.com/fitness-consultation/jordan-123."
    )

    first = send_welcome_email(
        "jordan@example.com",
        "Welcome to fitness coaching",
        body,
        first_context,
    )
    second = send_welcome_email(
        "jordan@example.com",
        "Welcome to fitness coaching",
        body,
        second_context,
    )

    assert first == second
    assert first["status"] == "sent"
    assert first["provider"] == "local_placeholder"
    assert first["message_id"].startswith("local-")
    assert first_context.state["email_result"] == first
