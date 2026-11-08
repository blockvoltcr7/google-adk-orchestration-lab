# Agent SDK Builder Lab — Interactive Architecture Video & Simulation Studio

An interactive, animated architectural video walkthrough and simulator based on the **Agent SDK Builder Lab** end-to-end framework (*Build • Test • Evaluate • Deploy*).

## How to Launch

From the repository root, open the interactive video in your default browser:

```bash
# Open directly on macOS
open interactive-video/index.html
```

Or serve it with a local static web server:

```bash
cd interactive-video
python3 -m http.server 8000
# Then open http://localhost:8000 in your browser
```

---

## Core Capabilities

### 1. Interactive Video Player
- **Video Timeline & Scrubber**: Drag or click anywhere on the progress bar to navigate across the 3-minute architectural lifecycle.
- **Synchronized Voiceover Narration**: Automatic text-to-speech narration (via Web Speech API) and futuristic synthesizer sound effects (via Web Audio API) matching each chapter.
- **Live Closed Captions (CC)**: Real-time subtitle HUD displaying high-level concepts and active component execution status.
- **Cinematic Director Camera**: Smoothly tracks and zooms into active components during playback, with one-click toggle to full overview mode (`D` key).
- **Speed Selector**: 0.75x, 1.0x, 1.25x, 1.5x, and 2.0x playback rates.

### 2. Full Architecture Exploration & Node Inspector
- **Click Any Node on the Glass Board**: Pauses and opens the side-drawer inspector with:
  - Component role & design patterns
  - Google ADK 2.x code implementation snippets (`LlmAgent`, `Workflow`, `McpToolset`, `RequestInput`, etc.)
  - Copyable code blocks
- **Interactive Scenarios**:
  - **Standard Enterprise Run (Happy Path)**: Ingests user input -> Injects history -> Plans -> Passes Guardrails -> Executes MCP Tools -> Clears Eval Gate -> Deploys to Staging/Production.
  - **Security Interception (Guardrail Route-Back)**: Demonstrates PII detection / prompt injection halting execution and routing back safely.
  - **Hallucination Self-Correction (Eval Retry Loop)**: Demonstrates an ungrounded tool call being caught by the Evaluation Gate and looping back to the Reasoning engine for reflection.
  - **High-Stakes Human-in-the-Loop Gate**: Shows high-consequence operations pausing execution for executive sign-off before production deployment.

### 3. One-Click Video Recording & Export
- Click **"Record Video"** at the top right to record a 60FPS high-definition `.webm` video file directly from the canvas animations and download it to your machine.

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Space` | Play / Pause |
| `←` / `→` | Seek 5s Backward / Forward |
| `M` | Mute / Unmute Voiceover |
| `C` | Toggle Closed Captions HUD |
| `D` | Toggle Director Camera (Auto-Focus vs Overview) |
| `F` | Toggle Fullscreen |
| `Esc` | Close Inspector Drawer / Modals |
| `Click on Node` | Inspect Architecture Component & ADK Code |

---

## Architecture Mappings (Visual to Google ADK)

| Diagram Module | ADK Orchestration Equivalent | Purpose |
|---|---|---|
| **User & Context** | `UserMessage`, `SessionContext` | Ingests omnichannel client queries and conversation history |
| **Agent Core** | `LlmAgent(model="gemini-2.5-pro")` | Central LLM controller coordinating sub-agents |
| **Reasoning / Orchestration** | `Workflow`, `Dynamic Orchestration`, `Reflection` | Multi-step plan decomposition and tool selection |
| **Memory** | `StateStore`, `VectorStore` | Hybrid working memory, PostgreSQL state, and Pinecone vector search |
| **Guardrails** | `RouteGuard`, `Safety Plugins` | PII redaction, content safety filters, and policy enforcement |
| **Tools / MCP Servers** | `McpToolset` | Standardized Model Context Protocol connections (CRM, SQL, Email, Calendar) |
| **Evaluation Gate** | `EvaluatorNode`, `LoopAgent` | 6-metric grading (Correctness, Groundedness, Safety, Tool Selection, Latency, Cost) |
| **Observability** | `OpenTelemetry`, `Cloud Trace & Monitoring` | Traces, logs, latency profiles, and cost tracking |
| **Deployment & Human Approval** | `RequestInput`, `Staged Rollout` | Human-in-the-loop authorization and production release |
