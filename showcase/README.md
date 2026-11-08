# Google ADK Graph Engineering Showcase

Welcome to the **Google Agent Development Kit (ADK) Graph Engineering Showcase**. This directory contains complete, independently runnable, testable, and deployment-ready ADK 2.x projects showcasing **all core graph-based agent engineering patterns**.

Every project in this showcase is:
1. **Scaffolded as a standalone ADK project** with `pyproject.toml`, `.env`, and `app/` architecture.
2. **Testable via deterministic unit tests** (`pytest`) and **eval-ready** (`agents-cli eval run` with canonical datasets and local metric grading).
3. **Deployment-ready for Vertex AI Agent Engine** (`deployment_target: agent_runtime` in `agents-cli-manifest.yaml`).

---

## 1. The Graph Engineering Paradigm in ADK 2.x

In early multi-agent development (and ADK 1.x template agents like `SequentialAgent` or `ParallelAgent`), agent flows often relied on prompt instructions to enforce business boundaries (e.g. *"If intake is incomplete, do not send an email"*). This approach is fragile: LLMs can hallucinate, overlook negative instructions, or trigger side effects unexpectedly.

**Graph engineering replaces prompt steering with topological determinism:**
- **Deterministic Gating:** If validation or compliance checks fail, the workflow routes to an isolated rejection node. If there is no edge between the rejection node and downstream side effects, executing a side effect on invalid input is **physically impossible**.
- **Heterogeneous Composition:** Nodes in an ADK graph blend pure deterministic Python functions, specialized single-turn LLM agents, synchronization barriers (`JoinNode`), and nested sub-workflows.
- **Event-Sourced Resilience:** The ADK runtime records an immutable chronological event log (`session.events`). This enables state reconstruction, resume from arbitrary interruptions, and deterministic replay ordering (`ReplaySequenceBarrier`).

---

## 2. Pattern Index & Decision Matrix

| # | Project Directory | Project Name | Primary ADK Primitives | Domain Use Case |
|---|---|---|---|---|
| **01** | [`01-sequential-graph-pipeline`](./01-sequential-graph-pipeline/) | `graph-sequential` | `Workflow`, `START`, typed handoffs | E-Commerce Order Fulfillment |
| **02** | [`02-conditional-routing-graph`](./02-conditional-routing-graph/) | `graph-routing` | `Workflow`, `EventActions(route=...)`, `DEFAULT_ROUTE` | Enterprise Service Desk Router |
| **03** | [`03-explicit-fan-in-graph`](./03-explicit-fan-in-graph/) | `graph-fan-in` | `Workflow`, `JoinNode`, parallel tuples | Multi-Source Corporate Due Diligence |
| **04** | [`04-iterative-refinement-graph`](./04-iterative-refinement-graph/) | `graph-refinement` | Cyclic edges, conditional loop gate | Autonomous Architecture Spec Generator |
| **05** | [`05-human-in-the-loop-graph`](./05-human-in-the-loop-graph/) | `graph-hitl` | Interrupt checkpoints, state persistence, resume | Corporate Expense & Refund Gateway |
| **06** | [`06-nested-subworkflows-graph`](./06-nested-subworkflows-graph/) | `graph-nested` | Hierarchical `Workflow(BaseNode)` composition | Multi-Stage Content Publishing Studio |
| **07** | [`07-dynamic-orchestration-graph`](./07-dynamic-orchestration-graph/) | `graph-dynamic` | `@node(rerun_on_resume=True)`, `ctx.run_node` | Dynamic Document Section Batch Processor |

### The Graph Pattern Decision Tree

```text
How is the execution topology determined?
├── Ahead of runtime (Static Graph)
│   ├── Fixed linear steps with typed data -----------> 01. Sequential Pipeline Graph
│   ├── Branch selected by classifier/rules ----------> 02. Conditional Routing Graph
│   ├── Parallel independent branches synchronizing --> 03. Explicit Fan-In Graph (JoinNode)
│   ├── Evaluate and refine until quality bar ---------> 04. Iterative Refinement Graph
│   ├── Must suspend for human judgment/approval -----> 05. Human-in-the-Loop Graph
│   └── Reusable subgraphs composed in parent --------> 06. Nested Sub-Workflows Graph
└── At runtime based on data size or dynamic tasks
    └── Imperative loops/recursion with memoized replay -> 07. Dynamic Orchestration Graph
```

---

## 3. Detailed Walkthrough of Showcase Projects

### 01 — Sequential Pipeline Graph
- **Pattern:** Explicit linear directed graph with typed Pydantic models.
- **Why it matters:** Eliminates implicit sequence lists and prompt-instructed side-effects. Data flows cleanly from node output to node input.
- **Topology:**
  ```text
  START -> validate_order -> calculate_financials -> generate_invoice -> dispatch_confirmation
  ```

### 02 — Conditional Routing Graph
- **Pattern:** Discrete branch selection using `EventActions(route=...)` and routing dictionaries.
- **Why it matters:** Unlike coordinator LLMs that probabilistically choose tools, routing rules deterministically activate only matching paths. Includes `DEFAULT_ROUTE` (`"__DEFAULT__"`) to guarantee no unhandled dead-ends.
- **Topology:**
  ```text
  START -> triage_ticket --"billing"----> handle_billing ----------> format_resolution
                         --"technical"--> handle_technical -------> format_resolution
                         --"account"----> handle_account ---------> format_resolution
                         --"__DEFAULT__"-> handle_fallback -------> format_resolution
  ```

### 03 — Explicit Fan-In Graph (`JoinNode`)
- **Pattern:** Concurrent parallel fan-out with an explicit `JoinNode` synchronization barrier.
- **Why it matters:** Heterogeneous branches (`analyze_financials`, `evaluate_competitors`, `audit_compliance`) run concurrently and aggregate into a typed dictionary `{predecessor_name: output}` before downstream synthesis.
- **Topology:**
  ```text
  START -> analyze_financials -----\
  START -> evaluate_competitors ----+--> JoinNode("gather_diligence") --> synthesize_executive_dossier
  START -> audit_compliance ------/
  ```

### 04 — Iterative Refinement Cyclic Graph
- **Pattern:** Cyclic graph with back-edges, quality scoring gate, and loop protection.
- **Why it matters:** ADK statically checks graphs for unconditional cycles. By placing a conditional route (`"refine"` vs `"publish"`) with an iteration counter at the evaluation gate, cycles are provably safe and guaranteed to terminate.
- **Topology:**
  ```text
  START -> draft_specification <----------------\
                  │                              │ (route: "refine")
                  ▼                              │
          evaluate_spec_quality -----------------/
                  │ (route: "publish")
                  ▼
          publish_specification
  ```

### 05 — Human-in-the-Loop (HITL) Graph
- **Pattern:** Stateful risk checkpoint where execution pauses for human authorization.
- **Why it matters:** Low-risk actions (amount <= $500) auto-execute. High-risk actions route to a manager approval gate that suspends execution, awaits human signoff, and branches to reimbursement or denial. Rejection paths have no physical link to payment execution.
- **Topology:**
  ```text
  START -> assess_expense_risk --"auto_approve"-----------------------> execute_reimbursement
                               --"require_approval"-> manager_gate ---> execute_reimbursement (if approved)
                                                                   ---> notify_rejection      (if rejected)
  ```

### 06 — Nested Sub-Workflows Graph
- **Pattern:** Modular hierarchical graph composition.
- **Why it matters:** `Workflow` subclasses `BaseNode`. Sub-workflows are independently developed, tested, and encapsulated, then wired as single nodes in a parent orchestration graph.
- **Topology:**
  ```text
  START -> [Ingestion Subworkflow] -> [Editorial Subworkflow] -> [Distribution Subworkflow]
  ```

### 07 — Dynamic Orchestration Graph
- **Pattern:** Dynamic runtime-scheduled workflows using `@node(rerun_on_resume=True)` and `ctx.run_node`.
- **Why it matters:** When processing a variable collection of items discovered at runtime, static graphs are impractical. The orchestrator uses native Python loops while ADK manages child task tracking, checkpoints, and crash-resilient replay.
- **Topology:**
  ```text
  START -> dynamic_batch_orchestrator
              ├── for each section in doc: await ctx.run_node(analyze_section)
              └── await ctx.run_node(synthesize_batch)
  ```

---

## 4. Running Tests & Behavioral Evaluations

Each showcase project contains both **fast deterministic unit tests** and **ADK behavioral evaluations**.

### Run All Unit Tests
Run the test suite across all 7 showcase projects:
```bash
for dir in showcase/*/; do
  echo "=== Running tests in $dir ==="
  (cd "$dir" && uv run pytest tests)
done
```

### Run ADK Behavioral Evaluations
Each project has a canonical evaluation suite under `tests/eval/`:
- `eval_config.yaml`: Metrics configuration.
- `datasets/basic-dataset.json`: Evaluated test cases.
- `eval_metrics.py`: Custom local evaluation metric functions.

To run evals in any showcase project:
```bash
cd showcase/01-sequential-graph-pipeline
agents-cli eval run
```

---

## 5. Deployment to Google Cloud Vertex AI Agent Engine

Every project includes an `agents-cli-manifest.yaml` targeting `agent_runtime` (Vertex AI Agent Engine).

### Verify Deployment Configuration (Dry Run)
Test deployment readiness without modifying cloud resources:
```bash
cd showcase/01-sequential-graph-pipeline
agents-cli deploy -n --deployment-target agent_runtime --project <YOUR_GCP_PROJECT> --region us-central1
```

### Deploy to Production
Deploy the agent project to Vertex AI Agent Engine:
```bash
agents-cli deploy --deployment-target agent_runtime --project <YOUR_GCP_PROJECT> --region us-central1
```
