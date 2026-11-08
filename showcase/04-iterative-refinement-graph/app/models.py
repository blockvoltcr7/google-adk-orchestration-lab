"""Data models for architecture specification drafting and quality gate."""

from pydantic import BaseModel, Field


class FeatureRequest(BaseModel):
    title: str = Field(..., min_length=1)
    requirements: list[str] = Field(default_factory=list)
    target_platform: str = Field(default="Google Cloud")


class DraftSpec(BaseModel):
    spec_id: str
    title: str
    iteration: int
    architecture_overview: str
    security_controls: list[str]
    api_endpoints: list[str]
    quality_score: int = 0
    feedback_notes: str = ""


class PublishedSpecRecord(BaseModel):
    spec_id: str
    title: str
    final_score: int
    iterations_taken: int
    status: str
    summary: str
