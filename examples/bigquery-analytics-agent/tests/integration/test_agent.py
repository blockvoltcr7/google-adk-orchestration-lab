"""Live integration smoke test for the local ADK runtime."""

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


def test_agent_stream_returns_text() -> None:
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")
    message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text="What product category had the highest completed revenue in 2024?"
            )
        ],
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    assert events
    assert any(
        part.text
        for event in events
        if event.content
        for part in (event.content.parts or [])
    )
