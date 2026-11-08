"""Individual stage nodes used within modular sub-workflows."""

import json
from typing import Any
from google.adk.events import Event, EventActions
from app.models import (
    RawArticleInput,
    IngestedContent,
    EnrichedEditorial,
    PublishedArticleRecord,
)


def _parse_input(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    text = getattr(raw, "text", None)
    if text is None and hasattr(raw, "parts"):
        text = "".join(getattr(p, "text", "") or "" for p in raw.parts)
    elif not isinstance(text, str):
        text = str(raw)
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        return {
            "title": "Architecting Multi-Agent Systems in Google ADK",
            "raw_markdown": "# Multi-Agent ADK\nGraph orchestration allows explicit routing and modular composition.",
            "author": "Cloud Architecture Guild",
            "channel": "Engineering Tech Radar",
        }


# --- Subworkflow 1: Ingestion Nodes ---

def parse_content(node_input: Any) -> Event:
    data = _parse_input(node_input)
    article = RawArticleInput.model_validate(data)
    art_id = f"ART-{abs(hash(article.title)) % 10000:04d}"
    clean = article.raw_markdown.replace("# ", "").strip()
    return Event(
        output={
            "article_id": art_id,
            "title": article.title,
            "clean_body": clean,
            "author": article.author,
            "channel": article.channel,
        },
        actions=EventActions(state_delta={"article_id": art_id, "stage": "ingested"}),
    )


def extract_metadata(node_input: dict[str, Any]) -> Event:
    body = node_input["clean_body"]
    words = len(body.split())
    reading_time = max(1, round(words / 200))
    ingested = IngestedContent(
        article_id=node_input["article_id"],
        title=node_input["title"],
        clean_body=body,
        word_count=words,
        reading_time_min=reading_time,
        author=node_input["author"],
        channel=node_input["channel"],
    )
    return Event(
        output=ingested.model_dump(),
        actions=EventActions(state_delta={"word_count": words, "reading_time_min": reading_time}),
    )


# --- Subworkflow 2: Editorial Nodes ---

def check_editorial_tone(node_input: dict[str, Any]) -> Event:
    return Event(
        output={
            **node_input,
            "tone_grade": "Technical & Pragmatic (High Clarity)",
        },
        actions=EventActions(state_delta={"tone_grade": "Technical & Pragmatic"}),
    )


def generate_seo_tags(node_input: dict[str, Any]) -> Event:
    title = node_input["title"]
    keywords = ["google-adk", "graph-orchestration", "agent-engine", "python"]
    meta = f"In-depth guide to {title}: exploring modular workflows and enterprise agent architecture."
    editorial = EnrichedEditorial(
        article_id=node_input["article_id"],
        title=title,
        clean_body=node_input["clean_body"],
        author=node_input["author"],
        channel=node_input["channel"],
        tone_grade=node_input.get("tone_grade", "Technical"),
        seo_keywords=keywords,
        meta_description=meta,
    )
    return Event(
        output={
            **editorial.model_dump(),
            "reading_time_min": node_input.get("reading_time_min", 2),
        },
        actions=EventActions(state_delta={"seo_keywords": keywords}),
    )


# --- Subworkflow 3: Distribution Nodes ---

def bundle_distribution_package(node_input: dict[str, Any]) -> Event:
    pkg_id = f"PKG-{node_input['article_id']}-LIVE"
    return Event(
        output={
            **node_input,
            "package_id": pkg_id,
            "cdn_slug": node_input["title"].lower().replace(" ", "-"),
        },
        actions=EventActions(state_delta={"package_id": pkg_id}),
    )


def archive_and_publish(node_input: dict[str, Any]) -> PublishedArticleRecord:
    slug = node_input.get("cdn_slug", "article")
    live_url = f"https://techradar.corp.internal/posts/{slug}"
    archive_hash = f"SHA256-{abs(hash(slug)) % 100000000:08x}"

    return PublishedArticleRecord(
        article_id=node_input["article_id"],
        title=node_input["title"],
        status="PUBLISHED_LIVE",
        reading_time_min=int(node_input.get("reading_time_min", 3)),
        primary_channel=node_input["channel"],
        live_url=live_url,
        archive_hash=archive_hash,
    )
