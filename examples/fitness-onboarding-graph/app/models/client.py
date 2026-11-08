"""Client intake domain model."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientIntake(BaseModel):
    """A complete intake submitted by an already-qualified fitness client."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    email: EmailStr
    primary_goal: str = Field(min_length=1)
    experience_level: str = Field(min_length=1)
    availability: str = Field(min_length=1)
    physical_constraints: str = Field(min_length=1)
    preferred_consultation_time: str = Field(min_length=1)
