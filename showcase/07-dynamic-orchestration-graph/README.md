# 07 — Dynamic Orchestration Graph (`dynamic_batch_orchestrator`)

This showcase project demonstrates the **Dynamic Orchestration & Runtime Topology** pattern in Google ADK 2.x, using `@node(rerun_on_resume=True)` and `ctx.run_node` to execute dynamic workflows whose task count or structure is discovered at runtime.

---

## 1. Pattern Overview

Static graphs require all nodes, edges, and join barriers to be compiled at initialization. When processing variable collections (e.g. batch documents, dynamic task breakdowns, variable search depths), static graphs become unwieldy.

ADK's dynamic workflow model combines **natural Python control flow** (`for`, `if`, `while`) with **ADK's event-sourcing and crash-resilience engine**:

```mermaid
flowchart TD
    START["START (Dynamic Input)"] --> ORCH["@node(rerun_on_resume=True)\ndynamic_batch_orchestrator"]
    ORCH -.->|ctx.run_node()| W1["analyze_section(section_1)"]
    ORCH -.->|ctx.run_node()| W2["analyze_section(section_2)"]
    ORCH -.->|ctx.run_node()| WN["analyze_section(section_N)"]
    W1 -.->|returns output| ORCH
    W2 -.->|returns output| ORCH
    WN -.->|returns output| ORCH
    ORCH -.->|ctx.run_node()| S["synthesize_batch(results)"]
    S -.->|returns report| ORCH
    ORCH --> END["BatchSummaryReport"]

    style ORCH fill:#e8f4f8,stroke:#17a2b8
    style S fill:#d4edda,stroke:#28a745
```

### Why `@node(rerun_on_resume=True)` is Mandatory
1. **Interrupt Replay:** If an interrupt occurs inside any dynamically scheduled child (e.g., human-in-the-loop signoff or authentication), the orchestrator is suspended.
2. **Memoization & Fast-Forwarding:** Upon resume, the orchestrator re-executes from line 1, but `DynamicNodeScheduler` intercepts previously completed children, retrieving their cached outputs from `session.events` without re-running them.
3. **Deterministic Identities:** ADK assigns deterministic child identifiers (`parent/child@run_id`) to each dynamic node execution.

---

## 2. Quickstart & Testing

### Run Tests
```bash
uv run pytest
```

### Run Behavioral Evals
```bash
agents-cli eval run
```

---

## 3. Deployment to Agent Engine

Scaffolded with `deployment_target: agent_runtime` in `agents-cli-manifest.yaml`:

```bash
# Dry run check
agents-cli deploy -n --deployment-target agent_runtime --project <GCP_PROJECT_ID> --region us-central1

# Deploy to Vertex AI Agent Engine
agents-cli deploy --deployment-target agent_runtime --project <GCP_PROJECT_ID> --region us-central1
```
