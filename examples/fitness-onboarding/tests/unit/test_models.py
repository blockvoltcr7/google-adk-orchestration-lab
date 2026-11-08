"""Unit tests for typed onboarding models."""

import pytest
from pydantic import ValidationError

from app.models import ClientIntake


def test_client_intake_normalizes_strings_and_email() -> None:
    intake = ClientIntake.model_validate(
        {
            "name": "  Jordan Lee  ",
            "email": "JORDAN@EXAMPLE.COM",
            "primary_goal": "  Build consistent strength  ",
            "experience_level": "Beginner",
            "availability": "Monday evenings",
            "physical_constraints": "None reported",
            "preferred_consultation_time": "Tuesday at 6 PM Eastern",
        }
    )

    assert intake.name == "Jordan Lee"
    assert str(intake.email) == "JORDAN@example.com"
    assert intake.primary_goal == "Build consistent strength"


def test_client_intake_rejects_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        ClientIntake.model_validate(
            {
                "name": "Jordan Lee",
                "email": "jordan@example.com",
            }
        )
