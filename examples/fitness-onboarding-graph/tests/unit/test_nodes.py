"""Tests for deterministic booking, email, and response nodes."""

from types import SimpleNamespace
from typing import cast

import pytest
from google.adk.agents.context import Context

from app.models import (
    BookingPackage,
    ConsultationPlan,
    OnboardingResult,
    WelcomeEmailDraft,
)
from app.tools import (
    create_booking,
    render_onboarding_confirmation,
    send_email,
)

CLIENT = {
    "name": "Jordan Lee",
    "email": "jordan@example.com",
    "primary_goal": "Build consistent strength",
    "experience_level": "Beginner",
    "availability": "Monday, Wednesday, and Friday evenings",
    "physical_constraints": "Previous knee discomfort; avoid assumptions",
    "preferred_consultation_time": "Tuesday at 6:00 PM Eastern",
}
PLAN = ConsultationPlan(
    coach_briefing="Discuss a sustainable beginner strength routine.",
    goal_focus="Build consistent strength",
    consultation_agenda=["Clarify goals", "Review availability"],
    constraint_notes="Previous knee discomfort; avoid assumptions",
)


def _context(state: dict[str, object]) -> Context:
    return cast(Context, SimpleNamespace(state=state))


def test_booking_node_is_deterministic_and_preserves_typed_data() -> None:
    first = create_booking(_context({"client_profile": CLIENT}), PLAN)
    second = create_booking(_context({"client_profile": CLIENT}), PLAN)

    assert first.output == second.output
    package = BookingPackage.model_validate(first.output)
    assert package.booking_result.booking_url.startswith(
        "https://booking.example.com/fitness-consultation/jordan-lee-"
    )
    assert package.client_profile.physical_constraints == CLIENT["physical_constraints"]
    assert first.actions.state_delta["booking_result"]["status"] == "created"


def test_email_node_is_deterministic_and_checks_llm_output_contract() -> None:
    booking_event = create_booking(_context({"client_profile": CLIENT}), PLAN)
    package = BookingPackage.model_validate(booking_event.output)
    state = {
        "client_profile": CLIENT,
        "consultation_plan": PLAN.model_dump(mode="json"),
        "booking_result": package.booking_result.model_dump(mode="json"),
    }
    draft = WelcomeEmailDraft(
        recipient="jordan@example.com",
        subject="Welcome to fitness coaching",
        body=f"Book here: {package.booking_result.booking_url}",
        booking_url=package.booking_result.booking_url,
    )

    first = send_email(_context(state), draft)
    second = send_email(_context(state), draft)
    assert first.output == second.output

    result = OnboardingResult.model_validate(first.output)
    assert result.email_result.status == "sent"
    assert result.email_result.provider == "local_placeholder"
    assert result.client_profile.physical_constraints == CLIENT["physical_constraints"]

    response = render_onboarding_confirmation(result)
    assert response.content is not None
    assert package.booking_result.booking_url in (response.content.parts[0].text or "")


def test_email_node_rejects_changed_recipient_or_booking_url() -> None:
    booking_event = create_booking(_context({"client_profile": CLIENT}), PLAN)
    package = BookingPackage.model_validate(booking_event.output)
    state = {
        "client_profile": CLIENT,
        "consultation_plan": PLAN.model_dump(mode="json"),
        "booking_result": package.booking_result.model_dump(mode="json"),
    }

    with pytest.raises(ValueError, match="recipient"):
        send_email(
            _context(state),
            WelcomeEmailDraft(
                recipient="other@example.com",
                subject="Welcome",
                body="Hello",
                booking_url=package.booking_result.booking_url,
            ),
        )

    with pytest.raises(ValueError, match="booking URL"):
        send_email(
            _context(state),
            WelcomeEmailDraft(
                recipient="jordan@example.com",
                subject="Welcome",
                body="Hello",
                booking_url="https://booking.example.com/wrong",
            ),
        )
