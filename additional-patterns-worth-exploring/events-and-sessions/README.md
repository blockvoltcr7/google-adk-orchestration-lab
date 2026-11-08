# Google ADK Events & Sessions Guide

## Overview

In the **Google Agent Development Kit (ADK)** (`google-adk`), **Sessions** and **Events** form the foundational backbone of state management, conversation tracking, and execution history.

Every turn, model response, tool execution, state mutation, or agent delegation is captured as a structured `Event` and recorded sequentially within a `Session` managed by a `SessionService`.

```text
+------------------+         ListEvents         +--------------------------+
|                  | -------------------------> |                          |
|      Runner      |                            |      Services            |
|  (Orchestration) | <------------------------- | (Session, State, Memory) |
|                  |            Event           |                          |
+------------------+                            +--------------------------+
      |      ^                                                ^
  Ask |      | Yield                                          | append_event()
      v      |                                                |
+------------------+                                          |
| Execution Logic  | -----------------------------------------+
| (LlmAgent, LLM,  |
| Tools, Plugins)  |
+------------------+
```

---

## Key Pillars for Students

### 1. How It Works
- **Session Identification:** Every interaction thread is bound to a unique `session_id`.
- **Append-Only History:** As the agent executes instructions or tools, the runner yields `Event` objects. The `SessionService` appends each event to the session's event history (`session_service.append_event(session, event)`).
- **Dual State Storage:**
  - **Event History:** The full, immutable chronological log of every interaction (prompts, model responses, tool inputs/outputs, errors).
  - **Session State (`session.state`):** A dynamic key-value dictionary updated whenever an event carries state mutations (`event.actions.state_delta`).

### 2. Why It Is Important
- **Session Persistence & Recovery:** Allows long-running workflows to pause, save to database (`DatabaseSessionService`), and resume without losing context.
- **Auditability & Observability:** Provides a transparent trail of every decision, tool call, and state change made by the agent.
- **Lifecycle Interception:** Developers can hook into events (`before_tool_callback`, `on_event_callback`, `before_agent_callback`) via `BasePlugin` to enforce safety policies, content filters, or audit logging.
- **Event Streaming:** Enables real-time UI updates (token streaming, progress indicators) while maintaining background storage.

### 3. What the Agent Needs It For
- **Context Reconstruction:** Rebuilds the LLM's chat history before every prompt invocation.
- **Multi-Turn Tool Execution Loops:** Tracks tool calls yielded by the model, pairs them with tool execution results, and feeds the output back to the model.
- **Subagent Delegation & Coordination:** Tracks interactions across parent and subagent boundaries.

---

## Module Directory Structure

This learning module is divided into three detailed lessons:

1. **[01_how_events_work.md](01_how_events_work.md)** — Detailed anatomy of an `Event`, types of events, and the complete Runner $\leftrightarrow$ SessionService lifecycle loop.
2. **[02_why_events_matter.md](02_why_events_matter.md)** — Session persistence across restarts (`InMemorySessionService` vs `DatabaseSessionService`), state vs. event log isolation, and intercepting events via `BasePlugin`.
3. **[03_agent_event_lifecycle.md](03_agent_event_lifecycle.md)** — How the agent uses events to reconstruct context, execute multi-turn tool loops, and coordinate multi-agent delegation with Google ADK Python code examples.

---

## Quick Example: Creating an ADK Session & Running Events

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 1. Instantiate Gemini Model & ADK Agent
model = Gemini(model="gemini-3.6-flash")

agent = LlmAgent(
    name="fitness_assistant",
    model=model,
    instruction="You are a helpful fitness onboarding assistant.",
)

# 2. Setup Session Service & Create Session
session_service = InMemorySessionService()
session_id = "sess_001"
session_service.create_session(session_id=session_id, app_name="fitness_app")

# 3. Initialize ADK Runner
runner = Runner(
    agent=agent,
    session_service=session_service,
)

async def main():
    # 4. Execute a turn; Runner handles Event creation & Session persistence automatically
    events = runner.run(
        session_id=session_id,
        user_message="Hi! My target fitness goal is muscle hypertrophy.",
    )
    
    async for event in events:
        if event.is_final_response() and event.content:
            print("Agent Response:", event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```
