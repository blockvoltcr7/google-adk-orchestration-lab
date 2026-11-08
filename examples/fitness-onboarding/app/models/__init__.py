"""Typed domain and configuration models for fitness onboarding."""

from .client import ClientIntake
from .prompt import PromptDefinition
from .results import (
    BookingResult,
    EmailDeliveryResult,
    IntakeValidationResult,
)

__all__ = [
    "BookingResult",
    "ClientIntake",
    "EmailDeliveryResult",
    "IntakeValidationResult",
    "PromptDefinition",
]
