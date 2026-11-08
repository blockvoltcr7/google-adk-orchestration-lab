"""Data models for dynamic batch document processing."""

from pydantic import BaseModel, Field


class DocumentSection(BaseModel):
    section_index: int
    heading: str
    content: str


class BatchDocumentInput(BaseModel):
    doc_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    sections: list[DocumentSection] = Field(..., min_length=1)


class SectionAnalysis(BaseModel):
    section_index: int
    heading: str
    key_findings: list[str]
    has_risk: bool


class BatchSummaryReport(BaseModel):
    doc_id: str
    title: str
    total_sections: int
    flagged_sections_count: int
    executive_digest: str
    status: str
