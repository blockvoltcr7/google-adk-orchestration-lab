"""Deterministic local booking-link tool."""

import hashlib
import re
from typing import Any

from google.adk.tools import ToolContext

from app.models import BookingResult


def _slugify(value: str) -> str:
    """Create a stable URL-safe client slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "client"


def create_booking_link(
    client_name: str,
    client_email: str,
    preferred_consultation_time: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Create a consultation booking link for a validated client.

    Args:
        client_name: Validated client name.
        client_email: Validated client email.
        preferred_consultation_time: Client's requested consultation time.

    Returns:
        A booking identifier, URL, client name, and requested time.
    """
    seed = "|".join(
        (
            client_name.strip().lower(),
            client_email.strip().lower(),
            preferred_consultation_time.strip().lower(),
        )
    )
    booking_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    booking_url = (
        "https://booking.example.com/fitness-consultation/"
        f"{_slugify(client_name)}-{booking_id}"
    )
    result = BookingResult(
        status="created",
        booking_id=booking_id,
        booking_url=booking_url,
        client_name=client_name.strip(),
        preferred_consultation_time=preferred_consultation_time.strip(),
    )
    serialized = result.model_dump(mode="json")
    tool_context.state["booking_result"] = serialized
    return serialized
