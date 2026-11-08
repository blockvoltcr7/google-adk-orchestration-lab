from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.genai import types

from app.schemas import InboundLeadPayload, AgentResponse
from app.session_manager import APP_NAME, runner, session_service, get_or_create_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qualification-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Lead Qualification Agent Service...")
    yield
    logger.info("Shutting down Lead Qualification Agent Service...")

app = FastAPI(
    title="ADK Lead Qualification Service",
    description="Enterprise Inbound Lead Qualification Service with Session State Injection on Google Cloud Run",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    """Cloud Run health & liveness probe."""
    return {"status": "HEALTHY", "service": "qualification-agent"}

@app.post("/qualify", response_model=AgentResponse, tags=["Agent"])
async def qualify_lead(payload: InboundLeadPayload) -> AgentResponse:
    """
    Main endpoint for inbound lead messages.
    Accepts:
      - user_id, contact_id, calendar_id, metadata (Injected into Session State)
      - message (Passed as conversational Content to the model)
    """
    # Deterministic session ID tied to contact_id for continuous conversation
    session_id = f"sess_{payload.contact_id}"

    # 1. State Delta: Payload information injected directly into ADK Session State
    state_delta = {
        "user_id": payload.user_id,
        "contact_id": payload.contact_id,
        "calendar_id": payload.calendar_id,
        "metadata": payload.metadata or {},
    }

    # 2. Ensure session exists with initial state
    await get_or_create_session(
        app_name=APP_NAME,
        user_id=payload.user_id,
        session_id=session_id,
        initial_state=state_delta,
    )

    # 3. Create model conversational message
    new_message = types.Content(
        role="user",
        parts=[types.Part(text=payload.message)],
    )

    response_text_chunks = []

    # 4. Execute ADK Runner with state_delta
    try:
        async for event in runner.run_async(
            user_id=payload.user_id,
            session_id=session_id,
            new_message=new_message,
            state_delta=state_delta, # Injects/updates state without prompt pollution
        ):
            # Extract generated text from event
            content = getattr(event, "content", None)
            if content and getattr(content, "parts", None):
                for part in content.parts:
                    if getattr(part, "text", None) and not getattr(part, "thought", False):
                        response_text_chunks.append(part.text)

    except Exception as e:
        logger.error(f"Error during agent execution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

    # 5. Fetch updated session state snapshot
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=payload.user_id,
        session_id=session_id,
    )

    state_snapshot = session.state.to_dict() if hasattr(session.state, "to_dict") else dict(session.state)
    qual_info = state_snapshot.get("qualification", {})
    booking_info = state_snapshot.get("meeting_booking", {})

    return AgentResponse(
        response_text="".join(response_text_chunks).strip(),
        session_id=session_id,
        qualification_status=qual_info.get("tier", "PENDING"),
        meeting_booked=bool(booking_info),
        session_state_snapshot=state_snapshot,
    )

@app.post("/qualify/stream", tags=["Agent"])
async def qualify_lead_stream(payload: InboundLeadPayload):
    """
    Server-Sent Events (SSE) streaming endpoint for real-time frontend integration.
    """
    session_id = f"sess_{payload.contact_id}"
    state_delta = {
        "user_id": payload.user_id,
        "contact_id": payload.contact_id,
        "calendar_id": payload.calendar_id,
        "metadata": payload.metadata or {},
    }

    await get_or_create_session(
        app_name=APP_NAME,
        user_id=payload.user_id,
        session_id=session_id,
        initial_state=state_delta,
    )

    new_message = types.Content(
        role="user",
        parts=[types.Part(text=payload.message)],
    )

    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in runner.run_async(
            user_id=payload.user_id,
            session_id=session_id,
            new_message=new_message,
            state_delta=state_delta,
        ):
            if hasattr(event, "model_dump_json"):
                data = event.model_dump_json(exclude_none=True)
                yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
