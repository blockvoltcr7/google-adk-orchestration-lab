"""Deterministic local welcome-email tool."""

import hashlib
from typing import Any

from google.adk.tools import ToolContext

from app.models import EmailDeliveryResult


def send_welcome_email(
    recipient: str,
    subject: str,
    body: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Record a welcome email as sent through the local placeholder provider.

    Args:
        recipient: Validated client email address.
        subject: Welcome-email subject line.
        body: Welcome-email body, including the booking link.

    Returns:
        A deterministic delivery result containing the complete email.
    """
    seed = "|".join((recipient.strip().lower(), subject.strip(), body.strip()))
    message_id = f"local-{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:20]}"
    result = EmailDeliveryResult(
        status="sent",
        provider="local_placeholder",
        message_id=message_id,
        recipient=recipient.strip().lower(),
        subject=subject.strip(),
        body=body.strip(),
    )
    serialized = result.model_dump(mode="json")
    tool_context.state["email_result"] = serialized
    return serialized
