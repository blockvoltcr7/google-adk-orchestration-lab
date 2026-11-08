"""Data models for enterprise ticket routing graph."""

from pydantic import BaseModel, Field


class TicketInput(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class SpecialistResolution(BaseModel):
    ticket_id: str
    department: str
    assigned_specialist: str
    action_taken: str
    status: str
    sla_hours: int


class FinalResolutionRecord(BaseModel):
    ticket_id: str
    department: str
    status: str
    assigned_specialist: str
    sla_hours: int
    resolution_summary: str
