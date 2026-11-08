"""Deterministic local booking node.

This module provides the deterministic booking step in the fitness onboarding
graph. Per safety and privacy guidelines, it generates a local placeholder
booking result rather than creating real calendar appointments.
"""

import hashlib
import re

from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions

from app.models import (
    BookingPackage,
    BookingResult,
    ClientIntake,
    ConsultationPlan,
)


def _slugify(value: str) -> str:
    """Create a stable, URL-safe client slug from a raw string name.

    Converts characters to lowercase, replaces non-alphanumeric characters with
    hyphens, and strips leading/trailing hyphens.

    Args:
        value: Raw input string (e.g. client's full name).

    Returns:
        A sanitized, lowercased, URL-safe slug string.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "client"


def create_booking(
    ctx: Context,
    node_input: ConsultationPlan,
) -> Event:
    """Create a local placeholder booking result and pass a complete package downstream.

    Reads the validated ``client_profile`` from the execution context state, generates
    a deterministic 16-character SHA-256 hash as the booking ID, constructs a local
    placeholder booking URL, and packages the result alongside the consultation plan.

    Args:
        ctx: ADK workflow execution context containing session state (`client_profile`).
        node_input: Validated ``ConsultationPlan`` emitted by the preceding consultation node.

    Returns:
        An ``Event`` containing:
            - output: JSON dictionary representation of the ``BookingPackage``.
            - actions: ``EventActions`` with ``state_delta`` updating ``booking_result``.
    """
    client = ClientIntake.model_validate(ctx.state["client_profile"])
    seed = "|".join(
        (
            client.name.lower(),
            str(client.email).lower(),
            client.preferred_consultation_time.lower(),
        )
    )
    booking_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    booking = BookingResult(
        status="created",
        booking_id=booking_id,
        booking_url=(
            "https://booking.example.com/fitness-consultation/"
            f"{_slugify(client.name)}-{booking_id}"
        ),
        client_name=client.name,
        preferred_consultation_time=client.preferred_consultation_time,
    )
    package = BookingPackage(
        client_profile=client,
        consultation_plan=node_input,
        booking_result=booking,
    )
    return Event(
        output=package.model_dump(mode="json"),
        actions=EventActions(
            state_delta={"booking_result": booking.model_dump(mode="json")}
        ),
    )

