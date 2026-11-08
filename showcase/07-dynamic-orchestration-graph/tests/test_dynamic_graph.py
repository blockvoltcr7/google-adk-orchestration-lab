"""Unit and runner tests for dynamic orchestration with ctx.run_node."""

import json
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent
from app.nodes import analyze_section, synthesize_batch


def test_child_nodes():
    """Verify section analyzer and reducer behavior."""
    sec_clean = {"section_index": 1, "heading": "Overview", "content": "The system runs on GCP."}
    res_clean = analyze_section(sec_clean)
    assert not res_clean["has_risk"]

    sec_risk = {"section_index": 2, "heading": "Security", "content": "Critical vulnerability detected."}
    res_risk = analyze_section(sec_risk)
    assert res_risk["has_risk"]

    summary = synthesize_batch({
        "doc_id": "D-1",
        "title": "Report",
        "analyses": [res_clean, res_risk],
    })
    assert summary.total_sections == 2
    assert summary.flagged_sections_count == 1
    assert summary.status == "AUDIT_FLAGGED"


def test_end_to_end_dynamic_orchestration():
    """Execute dynamic orchestrator through Runner over runtime-defined sections."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = {
        "doc_id": "DOC-CORP-2026",
        "title": "Cloud Migration Risk Assessment",
        "sections": [
            {
                "section_index": 1,
                "heading": "Executive Summary",
                "content": "All core microservices migrated successfully to Cloud Run.",
            },
            {
                "section_index": 2,
                "heading": "Legal & Liability Review",
                "content": "Potential regulatory liability regarding cross-border data transfer.",
            },
            {
                "section_index": 3,
                "heading": "Infrastructure Health",
                "content": "Latency SLAs and uptime metrics are green across all zones.",
            },
        ],
    }

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=json.dumps(payload))],
    )

    events = list(
        runner.run(
            new_message=content,
            user_id="user_1",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    assert len(events) > 0
    outputs = [e.output for e in events if e.output]
    final = outputs[-1]
    assert final["doc_id"] == "DOC-CORP-2026"
    assert final["total_sections"] == 3
    assert final["flagged_sections_count"] == 1
    assert final["status"] == "AUDIT_FLAGGED"
    assert "Legal & Liability Review" in final["executive_digest"] or "3 dynamic sections" in final["executive_digest"]
