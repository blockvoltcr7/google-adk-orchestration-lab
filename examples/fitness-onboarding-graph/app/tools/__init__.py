"""Deterministic function nodes used by the onboarding graph.

This package exposes the deterministic node functions that power both valid and
invalid routes within the Google ADK ``FitnessOnboardingGraph`` workflow.

Exported Nodes:
    - ``validate_intake``: Parses user message payload and routes to 'valid' or 'invalid'.
    - ``render_intake_correction``: Terminal response node for invalid intake submissions.
    - ``create_booking``: Deterministic local booking placeholder node.
    - ``send_email``: Deterministic local email-delivery placeholder node.
    - ``render_onboarding_confirmation``: Terminal response node for valid completions.
"""

from .booking import create_booking
from .email import send_email
from .intake import render_intake_correction, validate_intake
from .response import render_onboarding_confirmation

__all__ = [
    "create_booking",
    "render_intake_correction",
    "render_onboarding_confirmation",
    "send_email",
    "validate_intake",
]

