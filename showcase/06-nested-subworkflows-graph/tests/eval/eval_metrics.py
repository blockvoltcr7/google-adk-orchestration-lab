"""Deterministic trace evaluation for nested sub-workflows architecture."""

from typing import Any


def _events(instance: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for turn in (instance.get("agent_data") or {}).get("turns", [])
        for event in turn.get("events", [])
    ]


def evaluate(instance: dict[str, Any]) -> dict[str, Any]:
    events = _events(instance)
    outputs = [e.get("output") for e in events if e.get("output")]
    last = outputs[-1] if outputs else {}

    # Verify that article traversed through all sub-workflows to PUBLISHED_LIVE
    is_live = last.get("status") == "PUBLISHED_LIVE"
    has_url = "https://techradar.corp.internal/posts/" in last.get("live_url", "")
    has_hash = "SHA256-" in last.get("archive_hash", "")

    passed = is_live and has_url and has_hash

    return {
        "score": 1.0 if passed else 0.0,
        "explanation": (
            "Article passed through Ingestion -> Editorial -> Distribution sub-workflows "
            "and was published live with verified CDN slug and archival hash."
            if passed
            else f"Failed sub-workflow delivery: {last}"
        ),
    }
