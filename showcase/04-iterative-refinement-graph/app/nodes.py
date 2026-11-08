"""Nodes for iterative spec drafting, evaluation gate, and publishing."""

import json
from typing import Any
from google.adk.events import Event, EventActions
from app.models import FeatureRequest, DraftSpec, PublishedSpecRecord


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
        return {"title": "Real-time Telemetry Service", "requirements": ["High throughput", "mTLS"]}


def draft_specification(node_input: Any) -> Event:
    """Generator node: drafts or refines spec based on feedback."""
    data = _parse_input(node_input)
    current_iter = int(data.get("iteration", 0)) + 1
    spec_id = data.get("spec_id") or f"SPEC-{abs(hash(data.get('title', 'Service'))) % 10000:04d}"
    title = data.get("title", "Service Architecture")

    # If first iteration, basic draft; if refined, incorporate hardened security
    if current_iter == 1:
        security = ["Basic JWT Auth"]
        endpoints = ["POST /api/v1/ingest", "GET /api/v1/health"]
        arch = "Single-region Cloud Run container with local in-memory buffering."
    else:
        security = ["mTLS Zero-Trust", "Cloud KMS Envelope Encryption", "IAM Role Binding"]
        endpoints = ["POST /api/v1/ingest", "GET /api/v1/health", "GET /api/v1/metrics"]
        arch = "Multi-region Cloud Run with Cloud Pub/Sub backpressure queue and Cloud Spanner storage."

    draft = DraftSpec(
        spec_id=spec_id,
        title=title,
        iteration=current_iter,
        architecture_overview=arch,
        security_controls=security,
        api_endpoints=endpoints,
        quality_score=0,
        feedback_notes=data.get("feedback_notes", ""),
    )
    return Event(
        output=draft.model_dump(),
        actions=EventActions(
            state_delta={
                "spec_id": spec_id,
                "iteration": current_iter,
            }
        ),
    )


def evaluate_spec_quality(node_input: dict[str, Any]) -> Event:
    """Evaluator gate node: scores draft and emits 'refine' or 'publish' route."""
    current_iter = int(node_input.get("iteration", 1))
    security = node_input.get("security_controls", [])

    # Scoring rubric: base 60 + 10 for endpoints + 20 for advanced security
    score = 60
    if len(node_input.get("api_endpoints", [])) >= 3:
        score += 15
    if any("KMS" in s or "mTLS" in s for s in security):
        score += 20

    # Decision: pass if score >= 85 or max iterations reached
    if score >= 85 or current_iter >= 3:
        route = "publish"
        feedback = "Spec meets enterprise reliability and security bar."
    else:
        route = "refine"
        feedback = "Missing enterprise envelope encryption (KMS) and multi-region failover."

    updated_spec = {
        **node_input,
        "quality_score": score,
        "feedback_notes": feedback,
    }

    return Event(
        output=updated_spec,
        actions=EventActions(
            route=route,
            state_delta={
                "quality_score": score,
                "feedback": feedback,
                "route_decision": route,
            },
        ),
    )


def publish_specification(node_input: dict[str, Any]) -> PublishedSpecRecord:
    """Terminal node producing approved and published specification record."""
    return PublishedSpecRecord(
        spec_id=node_input["spec_id"],
        title=node_input["title"],
        final_score=node_input["quality_score"],
        iterations_taken=node_input["iteration"],
        status="APPROVED_AND_PUBLISHED",
        summary=(
            f"Specification '{node_input['title']}' ({node_input['spec_id']}) "
            f"approved at iteration {node_input['iteration']} with score {node_input['quality_score']}/100. "
            f"Architecture: {node_input['architecture_overview']}"
        ),
    )
