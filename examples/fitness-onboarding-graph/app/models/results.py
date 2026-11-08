"""Typed outputs exchanged between graph nodes."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .client import ClientIntake


class IntakeValidationResult(BaseModel):
    """Result of parsing and validating the user's intake message."""

    model_config = ConfigDict(frozen=True)

    status: Literal["valid", "invalid"]
    client_profile: ClientIntake | None = None
    errors: list[str]
    provided_fields: dict[str, str] = Field(default_factory=dict)


class ConsultationPlan(BaseModel):
    """Structured plan produced by the consultation LLM node."""

    model_config = ConfigDict(str_strip_whitespace=True)

    coach_briefing: str = Field(min_length=1)
    goal_focus: str = Field(min_length=1)
    consultation_agenda: list[str] = Field(min_length=1)
    constraint_notes: str = Field(min_length=1)


class BookingResult(BaseModel):
    """Production-shaped result from the local booking node."""

    model_config = ConfigDict(frozen=True)

    status: Literal["created"]
    booking_id: str = Field(min_length=1)
    booking_url: str = Field(min_length=1)
    client_name: str = Field(min_length=1)
    preferred_consultation_time: str = Field(min_length=1)


class BookingPackage(BaseModel):
    """Data contract passed from booking into the welcome LLM node."""

    model_config = ConfigDict(frozen=True)

    client_profile: ClientIntake
    consultation_plan: ConsultationPlan
    booking_result: BookingResult


class WelcomeEmailDraft(BaseModel):
    """Structured email draft produced by the welcome LLM node."""

    model_config = ConfigDict(str_strip_whitespace=True)

    recipient: EmailStr
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
    booking_url: str = Field(min_length=1)


class EmailDeliveryResult(BaseModel):
    """Production-shaped result from the local email node."""

    model_config = ConfigDict(frozen=True)

    status: Literal["sent"]
    provider: Literal["local_placeholder"]
    message_id: str = Field(min_length=1)
    recipient: EmailStr
    subject: str = Field(min_length=1)


class OnboardingResult(BaseModel):
    """Complete successful result emitted by the graph."""

    model_config = ConfigDict(frozen=True)

    status: Literal["completed"]
    client_profile: ClientIntake
    consultation_plan: ConsultationPlan
    booking_result: BookingResult
    email_result: EmailDeliveryResult
