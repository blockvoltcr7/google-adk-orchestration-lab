# Lesson 3: Agent Event Lifecycle & Multi-Turn Tool Execution

## 1. Why the Agent Depends on Events

An LLM has no built-in internal memory across API calls. It relies entirely on the **Event Log** provided by the framework to construct its prompt context on every turn.

When an agent executes complex workflows involving multi-turn tool calling or multi-agent delegation, the framework orchestrates the interaction through a precise sequence of events:

```text
Turn 1: User Message Event ("Calculate BMR for male, 80kg, 180cm, 30 years old")
             |
             v
        LlmAgent Generates FunctionCall Event ("calculate_bmr(weight_kg=80, ...)")
             |
             v
   ADK Runner Executes Python Tool Function
             |
             v
     Runner Appends FunctionResponse Event ("calculated_bmr: 1780.0")
             |
             v
 Turn 2: LlmAgent Reads FunctionResponse Event & Responds ("Your BMR is 1,780 kcal/day")
```

---

## 2. Multi-Turn Tool Execution Loop

When a model decides to call a tool, the ADK event cycle follows this 4-phase sequence:

1. **Function Call Event (Yielded by Model):** The model returns a structured `FunctionCall` payload instead of final text.
2. **Plugin Interception (`before_tool_callback`):** ADK framework invokes plugin callbacks to allow validation, logging, or short-circuiting.
3. **Tool Execution:** The framework executes the python function tool or MCP tool.
4. **Function Response Event (Yielded by Runner):** The return dictionary is wrapped in a `FunctionResponse` event and appended to `session_service`.

---

## 3. End-to-End Code Example: Function Tool & Event Persistence

The following Python script demonstrates a complete Google ADK setup with custom function tools, plugins, and persistent session history:

```python
import asyncio
from typing import Any, Dict
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.plugins import BasePlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool

# 1. Define a python function tool
def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> Dict[str, Any]:
    """Calculates Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation."""
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    return {"calculated_bmr": bmr, "status": "success"}

# Wrap function in ADK FunctionTool
bmr_tool = FunctionTool(func=calculate_bmr)

# 2. Plugin to trace tool calls and events
class LifecycleLoggerPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="lifecycle_logger")

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        print(f"\n--> [ADK EVENT] Function Call Event: tool='{tool.name}' args={tool_args}")
        return None

    async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
        print(f"--> [ADK EVENT] Function Response Event: result={result}")
        return None

# 3. Build ADK LlmAgent
model = Gemini(model="gemini-3.6-flash")

agent = LlmAgent(
    name="bmr_agent",
    model=model,
    instruction="Calculate client BMR using the calculate_bmr tool when required.",
    tools=[bmr_tool],
)

# 4. Setup Session Service & Runner
session_service = InMemorySessionService()
session_id = "bmr_session_001"
session_service.create_session(session_id=session_id, app_name="fitness_app")

runner = Runner(
    agent=agent,
    session_service=session_service,
    plugins=[LifecycleLoggerPlugin()],
)

async def main():
    print("=== TURN 1: Invoking Tool ===")
    events1 = runner.run(
        session_id=session_id,
        user_message="Calculate BMR for male, 80kg, 180cm, 30 years old.",
    )
    async for event in events1:
        if event.is_final_response() and event.content:
            print(f"\nAgent Final Output:\n{event.content.parts[0].text}\n")

    print("=== TURN 2: Multi-Turn Memory Check ===")
    events2 = runner.run(
        session_id=session_id,
        user_message="What was the calculated BMR value?",
    )
    async for event in events2:
        if event.is_final_response() and event.content:
            print(f"\nAgent Final Output:\n{event.content.parts[0].text}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. Key Takeaways for Students

1. **Events are the Source of Truth:** Everything the agent "remembers" originates from the ordered `Event` history stored in `SessionService`.
2. **Tools Produce Events:** Tool invocations are not out-of-band function calls; they are formally recorded as `FunctionCall` and `FunctionResponse` events.
3. **Session Persistence:** `Runner` automatically loads past events for `session_id`, giving the model multi-turn context across calls.
