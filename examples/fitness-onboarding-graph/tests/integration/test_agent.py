# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0

"""Integration tests for valid and invalid graph execution."""

import json
from typing import Any

from dotenv import load_dotenv
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

from app.agent import root_agent  # noqa: E402

COMPLETE_INTAKE = {
    "name": "Jordan Lee",
    "email": "jordan@example.com",
    "primary_goal": "Build consistent strength",
    "experience_level": "Beginner",
    "availability": "Monday, Wednesday, and Friday evenings",
    "physical_constraints": "Previous knee discomfort; avoid assumptions",
    "preferred_consultation_time": "Tuesday at 6:00 PM Eastern",
}


def _run(message_text: str) -> list[Event]:
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")
    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message_text)],
    )
    return list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )


def _node_names(events: list[Event]) -> list[str]:
    return [
        event.node_info.path.rsplit("/", 1)[-1].split("@", 1)[0]
        for event in events
        if event.node_info.path
    ]


def test_complete_intake_runs_valid_graph_path() -> None:
    events = _run(json.dumps(COMPLETE_INTAKE))
    node_names = _node_names(events)

    expected_order = [
        "validate_intake",
        "consultation_agent",
        "create_booking",
        "welcome_agent",
        "send_email",
        "render_onboarding_confirmation",
    ]
    positions = [node_names.index(name) for name in expected_order]
    assert positions == sorted(positions)
    assert "render_intake_correction" not in node_names

    final_outputs: list[dict[str, Any]] = [
        event.output
        for event in events
        if isinstance(event.output, dict) and event.output.get("status") == "completed"
    ]
    assert final_outputs
    final = final_outputs[-1]
    assert final["email_result"]["status"] == "sent"
    assert (
        final["client_profile"]["physical_constraints"]
        == (COMPLETE_INTAKE["physical_constraints"])
    )
    assert any(
        event.content
        and event.content.parts
        and any(
            "booking.example.com" in (part.text or "") for part in event.content.parts
        )
        for event in events
    )


def test_incomplete_intake_uses_only_invalid_route() -> None:
    events = _run(json.dumps({"name": "Jordan Lee"}))
    node_names = _node_names(events)

    assert "validate_intake" in node_names
    assert "render_intake_correction" in node_names
    assert "consultation_agent" not in node_names
    assert "create_booking" not in node_names
    assert "welcome_agent" not in node_names
    assert "send_email" not in node_names
    assert any(
        event.content
        and event.content.parts
        and any("email:" in (part.text or "") for part in event.content.parts)
        for event in events
    )
