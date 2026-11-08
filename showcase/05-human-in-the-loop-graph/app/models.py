"""Data models for human-in-the-loop expense authorization."""

from typing import Optional
from pydantic import BaseModel, Field


class ExpenseClaim(BaseModel):
    claim_id: str = Field(..., min_length=1)
    employee_name: str = Field(..., min_length=1)
    department: str = Field(default="Engineering")
    amount: float = Field(..., gt=0)
    business_justification: str = Field(..., min_length=1)
    human_decision: Optional[str] = Field(
        default=None,
        description="Recorded human judgment: 'approved' or 'rejected'",
    )


class SettlementRecord(BaseModel):
    claim_id: str
    employee_name: str
    status: str
    payout_amount: float
    authorization_tier: str
    confirmation_code: str
    notes: str
