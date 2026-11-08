# Additional ADK Patterns Worth Exploring

These patterns are useful parts of the broader Google ADK design landscape, but
they are **not currently prioritized** for full lessons and visualizations.

The main [orchestration pattern catalog](../README.md) remains the active learning
path. Items here are a researched backlog, not completed pattern modules.

## Why these are separate

The main catalog focuses on agent and workflow orchestration: how work is ordered,
routed, delegated, repeated, paused, parallelized, and gathered.

The patterns below operate at adjacent layers:

- lifecycle interception;
- runtime execution;
- event-driven operation;
- tool governance;
- inter-agent and external-system protocols;
- context, state, and storage management.

They are worth learning after the orchestration foundations are comfortable.

## 1. Callback design patterns

Google explicitly documents eight callback patterns:

1. **Guardrails and policy enforcement** — inspect or block model and tool calls.
2. **Dynamic state management** — read and update session state at lifecycle hooks.
3. **Logging and monitoring** — emit structured execution telemetry.
4. **Caching** — bypass repeated model or tool calls when results already exist.
5. **Request/response modification** — transform model prompts, model responses,
   tool arguments, or tool results.
6. **Conditional skipping** — return from a `before_*` callback to bypass normal
   execution.
7. **Tool-specific actions** — handle authentication and summarization control.
8. **Artifact handling** — save and load files or large session-related data.

Why deferred: these patterns modify lifecycle behavior rather than define the
workflow topology itself.

Source: [Callback design patterns](https://adk.dev/callbacks/design-patterns-and-best-practices/)

## 2. Experimental agent routing

ADK's experimental TypeScript `RoutedAgent` can select one agent for an invocation
using patterns such as:

- fallback on error;
- planning-mode selection;
- auto-routing by request complexity;
- A/B or policy-based agent selection.

This is distinct from graph conditional routing. A graph route chooses a downstream
node; `RoutedAgent` chooses the agent that handles the invocation.

Why deferred: it is currently experimental and TypeScript-specific, while the
active learning catalog is primarily Python-oriented.

Source: [Agent routing](https://adk.dev/agents/routing/)

## 3. Policy-gated human approval

A `SecurityPlugin` can consult a policy engine before a tool executes. A policy
outcome can require confirmation, allowing the application to pause the tool call,
ask the user, and continue only after approval.

Why deferred: the current policy-engine form is documented as the recommended
TypeScript approach. The main catalog already teaches the language-independent
pause/resume HITL topology.

Source: [Human in the loop with Policy](https://adk.dev/workflows/patterns/#human-in-the-loop-with-policy)

## 4. ADK event loop

The event loop is the runtime pattern beneath every ADK agent:

```text
Runner -> Agent logic -> Event -> Runner processes actions/services -> resume
```

It explains why state changes, tool calls, artifacts, and user-visible content flow
through events rather than arbitrary side effects.

Why deferred: this is runtime mechanics rather than an agent-team design pattern.

Source: [ADK event loop](https://adk.dev/runtime/event-loop/)

## 5. Ambient agent patterns

Ambient agents operate without an active chat session. Relevant patterns include:

- scheduled or cron-triggered agents;
- event-triggered agents using Pub/Sub, Eventarc, or webhooks;
- continuous monitoring agents;
- output routing to logs, alerts, email, issue trackers, or downstream topics.

Why deferred: these patterns concern invocation and production operation rather
than internal orchestration.

Source: [Ambient agents](https://adk.dev/runtime/ambient-agents/)

## 6. Tool execution and governance patterns

Potential future lessons include:

- parallel asynchronous tool execution;
- confirmation before consequential actions;
- tool authentication and credential requests;
- retries, idempotency, and rate-limit-aware tools;
- controlling whether tool results are summarized by the model.

Why deferred: these are tool lifecycle and reliability concerns rather than
workflow topologies.

Sources: [Tool performance](https://adk.dev/tools/performance/) and
[action confirmations](https://adk.dev/tools-custom/confirmation/)

## 7. Protocol and integration patterns

Potential future lessons include:

- using an MCP server as an ADK tool provider;
- exposing ADK tools through an MCP server;
- exposing an agent over the Agent2Agent protocol;
- consuming a remote A2A agent;
- composing remote and local agents behind one coordinator.

Why deferred: these patterns define system boundaries and interoperability rather
than local workflow control.

Sources: [MCP in ADK](https://adk.dev/mcp/) and
[A2A protocol](https://adk.dev/a2a/)

## 8. Context, state, and persistence patterns

Learning Modules:
- [DatabaseSessionService Masterclass](./database-session-service/README.md) — Comprehensive guide to SQL-backed session persistence, database schema, state scoping, and runner integration.

Potential future lessons include:

- session state hand-off and state-key namespaces;
- long-term memory retrieval;
- artifact storage for large outputs;
- context caching;
- context compression;
- resumable and rewindable sessions.

Why deferred: these are data-lifecycle patterns that support many orchestrations
but do not determine which agent or node runs next.

Source: [Sessions and memory](https://adk.dev/sessions/)

## Prioritization status

| Pattern family | Value | Current priority |
|---|---|---|
| Callback patterns | High for safety and production control | Deferred |
| Experimental agent routing | Useful but evolving | Deferred |
| Policy-gated HITL | High for governed tools | Deferred |
| Event loop | High for understanding internals | Deferred |
| Ambient agents | High for scheduled/event-driven systems | Deferred |
| Tool governance | High for production reliability | Deferred |
| MCP and A2A | High for integrations and distributed agents | Deferred |
| Context and persistence | High for stateful agents | Module Available |

Revisit this backlog after the 13 prioritized orchestration patterns are understood
well enough to recognize and combine them in real designs.

