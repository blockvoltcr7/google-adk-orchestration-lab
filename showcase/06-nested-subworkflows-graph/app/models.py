"""Data models for nested content publishing pipeline."""

from pydantic import BaseModel, Field


class RawArticleInput(BaseModel):
    title: str = Field(..., min_length=1)
    raw_markdown: str = Field(..., min_length=1)
    author: str = Field(default="Editorial Team")
    channel: str = Field(default="Developer Blog")


class IngestedContent(BaseModel):
    article_id: str
    title: str
    clean_body: str
    word_count: int
    reading_time_min: int
    author: str
    channel: str


class EnrichedEditorial(BaseModel):
    article_id: str
    title: str
    clean_body: str
    author: str
    channel: str
    tone_grade: str
    seo_keywords: list[str]
    meta_description: str


class PublishedArticleRecord(BaseModel):
    article_id: str
    title: str
    status: str
    reading_time_min: int
    primary_channel: str
    live_url: str
    archive_hash: str
