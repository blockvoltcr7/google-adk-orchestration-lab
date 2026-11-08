"""User-visible terminal response node.

This module provides the terminal confirmation response node for successful
onboarding graph executions.
"""

from google.adk.events.event import Event
from google.genai import types

from app.models import OnboardingResult


def render_onboarding_confirmation(node_input: OnboardingResult) -> Event:
    """Emit a terminal confirmation event rendered in ADK web and client interfaces.

    Formats a summary text response containing the client's name, primary goal,
    physical constraints, placeholder booking URL, and email delivery status.

    Args:
        node_input: The compiled ``OnboardingResult`` emitted by ``send_email``.

    Returns:
        An ``Event`` containing:
            - content: ``types.Content`` with role 'model' containing the user-facing text.
            - output: JSON dictionary representation of ``OnboardingResult``.
    """
    text = (
        f"Local onboarding workflow completed for {node_input.client_profile.name}.\n"
        f"Goal: {node_input.client_profile.primary_goal}\n"
        "Constraint retained for the coach: "
        f"{node_input.client_profile.physical_constraints}\n"
        "Local placeholder booking link: "
        f"{node_input.booking_result.booking_url}\n"
        f"Local placeholder welcome email: {node_input.email_result.status} "
        f"({node_input.email_result.message_id})."
    )
    return Event(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=text)],
        ),
        output=node_input.model_dump(mode="json"),
    )

