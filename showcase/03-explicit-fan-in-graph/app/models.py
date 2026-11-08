"""Models for due diligence intelligence gather."""

from pydantic import BaseModel, Field


class CompanyTarget(BaseModel):
    name: str = Field(..., min_length=1)
    ticker: str = Field(..., min_length=1)
    industry: str = Field(default="Cloud Infrastructure")


class FinancialAnalysis(BaseModel):
    financial_score: int
    revenue_growth_yoy: str
    ebitda_margin: str
    balance_sheet_strength: str


class CompetitiveAnalysis(BaseModel):
    market_share_pct: str
    moat_rating: str
    primary_competitor: str


class ComplianceAudit(BaseModel):
    regulatory_status: str
    sanctions_clearance: bool
    risk_level: str


class ExecutiveDossier(BaseModel):
    company_name: str
    ticker: str
    overall_health_score: int
    investment_verdict: str
    financial_summary: str
    competitive_summary: str
    compliance_summary: str
