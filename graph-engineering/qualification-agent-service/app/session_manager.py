from __future__ import annotations

import os
from typing import Any
from google.adk import Runner
from google.adk.sessions import InMemorySessionService, Session
from app.agent import qualification_agent

# In production, swap InMemorySessionService with DatabaseSessionService (Cloud SQL / Spanner / Firestore)
# or VertexAiSessionService for persistent state across container restarts.
session_service = InMemorySessionService()

APP_NAME = "qualification_service"

runner = Runner(
    agent=qualification_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

async def get_or_create_session(
    app_name: str,
    user_id: str,
    session_id: str,
    initial_state: dict[str, Any] | None = None,
) -> Session:
    """
    Retrieves an existing session or initializes a new one with pre-populated state.
    """
    existing_session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )
    if existing_session is not None:
        return existing_session

    return await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state or {},
    )
