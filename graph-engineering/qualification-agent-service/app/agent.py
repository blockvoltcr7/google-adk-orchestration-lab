import json
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

from google.adk import Agent
from google.adk.tools import ToolContext

# ─────────────────────────────────────────────────────────────────────────────
# State-Aware Tools (Read & Write directly to session.state via ToolContext)
# ─────────────────────────────────────────────────────────────────────────────

def get_lead_profile(tool_context: ToolContext) -> dict[str, Any]:
    """
    Fetches the lead's identity, contact record, and CRM metadata
    stored in the ADK Session State.
    Call this tool whenever you need to know who you are speaking with.
    """
    state = tool_context.state
    return {
        "user_id": state.get("user_id"),
        "contact_id": state.get("contact_id"),
        "calendar_id": state.get("calendar_id"),
        "metadata": state.get("metadata", {}),
        "qualification": state.get("qualification", {}),
    }

def record_qualification(
    tier: str,
    score: int,
    is_qualified: bool,
    reasons: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Records the final qualification determination into the session state.
    Args:
        tier: 'ENTERPRISE' | 'MID_MARKET' | 'SMB' | 'UNQUALIFIED'
        score: Score between 0 and 100
        is_qualified: True if the lead satisfies target qualification criteria
        reasons: Bulleted rationale for this determination
    """
    qual_data = {
        "tier": tier.upper(),
        "score": score,
        "is_qualified": is_qualified,
        "reasons": reasons,
        "contact_id": tool_context.state.get("contact_id"),
    }
    # Mutate session state directly:
    tool_context.state["qualification"] = qual_data
    return {"status": "SUCCESS", "qualification_recorded": qual_data}

def book_calendar_slot(
    proposed_time: str,
    topic: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Schedules a qualification or product demo on the team's designated calendar.
    Reads target calendar_id directly from the injected session state.
    Args:
        proposed_time: Natural language or ISO timestamp (e.g., 'Tomorrow at 2pm EST')
        topic: Purpose of the meeting (e.g., 'Enterprise Demo & Technical Discovery')
    """
    calendar_id = tool_context.state.get("calendar_id")
    contact_id = tool_context.state.get("contact_id")
    user_id = tool_context.state.get("user_id")

    if not calendar_id:
        return {"status": "ERROR", "message": "No calendar_id found in session state."}

    booking_confirmation = {
        "status": "CONFIRMED",
        "calendar_id": calendar_id,
        "user_id": user_id,
        "contact_id": contact_id,
        "scheduled_time": proposed_time,
        "topic": topic,
        "meeting_link": f"https://meet.google.com/adk-{contact_id[:6] if contact_id else 'demo'}",
    }

    # Store booking in session state
    tool_context.state["meeting_booking"] = booking_confirmation
    return booking_confirmation

# ─────────────────────────────────────────────────────────────────────────────
# ADK Web Adapter & Session State Interceptor
# ─────────────────────────────────────────────────────────────────────────────

def web_state_adapter(callback_context):
    """
    Provides seamless session state injection during ADK Web and interactive testing:
    1. In-chat command injection: If a user message begins with 'STATE: {json} | <message>',
       extracts the JSON into session state and passes <message> to the LLM.
    2. Zero-config fallback: If state is empty (e.g. freshly created in ADK Web),
       populates realistic default lead attributes so developers can test immediately.
    """
    state = callback_context.state
    content = callback_context.user_content

    # Check for in-chat state injection: STATE: {"company_size": 250} | Hello
    if content and getattr(content, "parts", None):
        first_part = content.parts[0]
        text = getattr(first_part, "text", "") or ""
        if text.startswith("STATE:") and "|" in text:
            raw_json, remainder = text.split("|", 1)
            try:
                parsed_state = json.loads(raw_json.replace("STATE:", "").strip())
                if isinstance(parsed_state, dict):
                    state.update(parsed_state)
                    first_part.text = remainder.strip()
            except Exception:
                pass

    # Zero-config default mock state for ADK Web UI
    if not state.get("contact_id"):
        state.setdefault("user_id", "usr_web_demo")
        state.setdefault("contact_id", "cnt_web_default")
        state.setdefault("calendar_id", "sales-enterprise@acmecorp.com")
        state.setdefault("metadata", {
            "company_name": "Demo Enterprises",
            "company_size": 175,
            "budget_range": "$40k-$80k",
            "industry": "Software",
        })

# ─────────────────────────────────────────────────────────────────────────────
# Agent Definition
# ─────────────────────────────────────────────────────────────────────────────

MODEL_NAME = os.getenv("ADK_MODEL", "gemini-2.5-flash")

qualification_agent = Agent(
    name="qualification_coach",
    model=MODEL_NAME,
    tools=[get_lead_profile, record_qualification, book_calendar_slot],
    before_agent_callback=web_state_adapter,
    instruction="""You are an expert Inbound Lead Qualification Assistant for an enterprise SaaS platform.

Your mission:
1. Greet the user professionally and engage naturally with their message.
2. Call `get_lead_profile` to review their contact_id and CRM metadata from session state.
3. Assess qualification criteria:
   - Enterprise: >100 employees or >$25k budget
   - Mid-Market: 20-100 employees or $10k-$25k budget
   - SMB: <20 employees
4. Record qualification status using `record_qualification`.
5. If qualified, proactively propose a demo and call `book_calendar_slot` when they agree to a time.
   (The tool automatically resolves their target calendar_id from session state).

Keep replies concise, consultative, and helpful. Never expose raw internal IDs unless asked.""",
)

# Export root_agent for ADK CLI (adk web / adk eval) discovery
root_agent = qualification_agent

