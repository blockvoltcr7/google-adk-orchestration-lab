# Lesson 2: Why Events & Session History Matter

## 1. Why Do We Need Event-Driven Session History?

Without event tracking, an LLM agent would be **stateless**. Every turn would require passing the full chat history manually, and background tasks (such as database writes or tool calls) would operate out-of-band without audit logs.

Google ADK's event architecture provides four crucial capabilities:

```text
+-----------------------------------------------------------------------+
|                       WHY EVENTS ARE CRITICAL                        |
+-----------------------------------------------------------------------+
| 1. PERSISTENCE      : Save/resume sessions via DatabaseSessionService |
| 2. AUDITABILITY     : Complete history of prompts, tools, and outputs |
| 3. GOVERNANCE       : Intercept tool calls & prompts using BasePlugin |
| 4. STATE ISOLATION  : Separate raw audit logs from session.state      |
+-----------------------------------------------------------------------+
```

---

## 2. Event Log vs. Session State

A common point of confusion when learning ADK is the difference between **Event Log** and **Session State**:

| Dimension | Event Log (`session.events`) | Session State (`session.state`) |
| :--- | :--- | :--- |
| **Structure** | Immutable, append-only chronological list of `Event`s | Mutable key-value dictionary (`google.adk.sessions.State`) |
| **Contents** | Raw text, model tokens, function call inputs/responses | Consolidated business variables (e.g. `client_name`, `is_valid`) |
| **Primary Use** | Context window building for LLM & full auditability | Templating in prompts (`{client_name}`) & fast state checks |
| **Lifetime** | Preserved across entire session history | Updated continuously via `event.actions.state_delta` |

---

## 3. Governance & Control: ADK Plugins (`BasePlugin`)

Events act as interception points. By implementing custom ADK plugins extending `google.adk.plugins.BasePlugin`, developers can enforce safety policies, content moderation, and human-in-the-loop approvals without altering core agent prompts.

### Available ADK Plugin Callbacks:

1. **`on_user_message_callback`**: Inspect or sanitize user input before invocation begins.
2. **`before_tool_callback` / `after_tool_callback`**: Intercept tool execution before it runs (e.g. require confirmation) or modify tool results.
3. **`on_event_callback`**: Modify or audit `Event` objects before they are appended to the session and yielded to the caller.
4. **`before_model_callback` / `after_model_callback`**: Inspect raw `LlmRequest` and `LlmResponse` objects.

---

## 4. Code Example: Governance Plugin & Database Session Persistence

```python
import asyncio
from typing import Any, Dict, Optional
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.plugins import BasePlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.tools import BaseTool, ToolContext

# Define a governance plugin extending Google ADK BasePlugin
class SecurityGovernancePlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="security_governance")

    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args: Dict[str, Any], tool_context: ToolContext
    ) -> Optional[Dict[str, Any]]:
        print(f"\n[GOVERNANCE PLUGIN] Intercepted tool: '{tool.name}'")
        
        # Block dangerous or unauthorized tool calls by returning a substitute result dictionary
        if tool.name == "delete_database":
            print("  --> [REJECTED] Tool execution blocked by governance policy!")
            return {"error": "Unauthorized operation: database deletion blocked."}
        
        print("  --> [APPROVED] Tool execution allowed.")
        return None  # Returning None allows normal tool execution

# Setup model and agent
model = Gemini(model="gemini-3.6-flash")

agent = LlmAgent(
    name="admin_agent",
    model=model,
    instruction="Execute requested system tasks.",
)

# Use SessionService for state persistence across calls
session_service = InMemorySessionService()
session_id = "gov_sess_100"
session_service.create_session(session_id=session_id, app_name="admin_app")

runner = Runner(
    agent=agent,
    session_service=session_service,
    plugins=[SecurityGovernancePlugin()],
)

async def main():
    print("--- User Turn 1: Normal Query ---")
    events1 = runner.run(session_id=session_id, user_message="Status check.")
    async for e in events1:
        if e.is_final_response() and e.content:
            print("Response:", e.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```
