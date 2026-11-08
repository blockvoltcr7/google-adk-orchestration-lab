"""Structured results returned by local onboarding tools."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class IntakeValidationResult(BaseModel):
    """Result of validating and normalizing a client intake."""

    model_config = ConfigDict(frozen=True)

    status: Literal["valid", "invalid"]
    client_profile: dict[str, str]
    errors: list[str]


class BookingResult(BaseModel):
    """Production-shaped result from the local booking-link provider."""

    model_config = ConfigDict(frozen=True)

    status: Literal["created"]
    booking_id: str = Field(min_length=1)
    booking_url: str = Field(min_length=1)
    client_name: str = Field(min_length=1)
    preferred_consultation_time: str = Field(min_length=1)


class EmailDeliveryResult(BaseModel):
    """Production-shaped result from the local email provider."""

    model_config = ConfigDict(frozen=True)

    status: Literal["sent"]
    provider: Literal["local_placeholder"]
    message_id: str = Field(min_length=1)
    recipient: EmailStr
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
