"""Deterministic local email-delivery node.

This module provides the deterministic email delivery step in the fitness onboarding
graph. Per safety and privacy guidelines, it generates a local placeholder delivery
result rather than dispatching real emails over external SMTP/API services.
"""

import hashlib

from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions

from app.models import (
    BookingResult,
    ClientIntake,
    ConsultationPlan,
    EmailDeliveryResult,
    OnboardingResult,
    WelcomeEmailDraft,
)


def send_email(
    ctx: Context,
    node_input: WelcomeEmailDraft,
) -> Event:
    """Record a local delivery result and assemble the successful graph output.

    Validates that the recipient and booking URL in the LLM-generated ``WelcomeEmailDraft``
    match the stored ``client_profile`` and ``booking_result`` in context state. Constructs
    a deterministic local message ID, creates an ``EmailDeliveryResult``, and compiles
    the final ``OnboardingResult``.

    Args:
        ctx: ADK workflow execution context containing session state (`client_profile`,
            `booking_result`, `consultation_plan`).
        node_input: Generated ``WelcomeEmailDraft`` from the preceding welcome agent node.

    Returns:
        An ``Event`` containing:
            - output: JSON dictionary representation of the final ``OnboardingResult``.
            - actions: ``EventActions`` with ``state_delta`` updating ``email_result``.

    Raises:
        ValueError: If the welcome draft recipient or booking URL does not match stored state.
    """
    client = ClientIntake.model_validate(ctx.state["client_profile"])
    booking = BookingResult.model_validate(ctx.state["booking_result"])
    consultation = ConsultationPlan.model_validate(ctx.state["consultation_plan"])

    if str(node_input.recipient).lower() != str(client.email).lower():
        raise ValueError("welcome draft recipient differs from validated email")
    if node_input.booking_url != booking.booking_url:
        raise ValueError("welcome draft booking URL differs from booking result")

    seed = "|".join(
        (
            str(node_input.recipient).lower(),
            node_input.subject,
            node_input.body,
        )
    )
    delivery = EmailDeliveryResult(
        status="sent",
        provider="local_placeholder",
        message_id=f"local-{hashlib.sha256(seed.encode()).hexdigest()[:20]}",
        recipient=node_input.recipient,
        subject=node_input.subject,
    )
    result = OnboardingResult(
        status="completed",
        client_profile=client,
        consultation_plan=consultation,
        booking_result=booking,
        email_result=delivery,
    )
    return Event(
        output=result.model_dump(mode="json"),
        actions=EventActions(
            state_delta={"email_result": delivery.model_dump(mode="json")}
        ),
    )

