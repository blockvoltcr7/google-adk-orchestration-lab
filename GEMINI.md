# Google Agent Development Kit (ADK) Guidelines

## Core Framework Specification

This repository is a visual, practical curriculum dedicated to **Google Agent Development Kit (ADK)** design patterns (`google-adk` Python package).

> [!IMPORTANT]
> **DO NOT USE `google.antigravity` or Antigravity SDK APIs.**
> All agent code, examples, and documentation in this repository must use official **Google ADK** modules: `google.adk` (such as `google.adk.agents`, `google.adk.events`, `google.adk.sessions`, `google.adk.runners`, `google.adk.plugins`, `google.adk.models`, `google.adk.apps`, and `google.adk.tools`).

---

## Core Google ADK Components

| ADK Module | Responsibility | Key Classes / Functions |
| :--- | :--- | :--- |
| **`google.adk.agents`** | Agent definition & composition | `LlmAgent`, `SequentialAgent`, `BaseAgent` |
| **`google.adk.events`** | Event data structures & actions | `Event`, `EventActions`, `NodeInfo` |
| **`google.adk.sessions`** | Session management & persistence | `Session`, `BaseSessionService`, `InMemorySessionService`, `DatabaseSessionService` |
| **`google.adk.runners`** | Invocation & orchestration runner | `Runner` |
| **`google.adk.models`** | LLM model adapters | `Gemini` |
| **`google.adk.plugins`** | Lifecycle hooks & event callbacks | `BasePlugin` |
| **`google.adk.tools`** | Deterministic function tools & toolsets | `FunctionTool` |
| **`google.adk.apps`** | Deployment application container | `App` |

---

## Workflow & Development Rules

- **Execution Environment:** Use `uv` for Python setup, dependency management, and script execution.
- **CLI Commands:** Use `agents-cli` for scaffolding, running smoke tests (`agents-cli run`), and evaluation (`agents-cli eval`).
- **Storage & State:**
  - `Event`: Complete, append-only log of every interaction (messages, tool calls/responses, node state).
  - `Session`: Session state container (`session.state` key-value dictionary) maintained by `SessionService`.


# Gemini Guidelines
- DO NOT WRITE DOCUMENATION IN THE visuals folder unless you are generating an Image in a folder
- full code examples go to the examples folder
- documenation and learning material can go into a new folder in the root folder or in the "additional-patterns" folder
- code should be runnable without any changes to the code base. means all env variables and api keys can be mock values or placeholders, but they MUST be defined in a .env file and all dependencies MUST be installed via uv.
