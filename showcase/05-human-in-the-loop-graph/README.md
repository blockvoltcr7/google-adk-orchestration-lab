# 05 — Human-in-the-Loop Approval Checkpoint Graph (`expense_authorization_graph`)

This showcase project demonstrates the **Human-in-the-Loop (HITL) Checkpoint & Resumption** pattern in Google ADK 2.x, implementing stateful risk gating where dangerous or high-value actions pause for human authorization.

---

## 1. Pattern Overview

In autonomous systems, irreversible side-effects (e.g. paying invoices, altering access permissions, issuing refunds) should not run solely on model discretion. The HITL graph establishes a deterministic policy barrier:

```mermaid
flowchart TD
    START["START"] --> R["assess_expense_risk"]
    R -->|route: 'auto_approve' (amount <= $500)| S["execute_reimbursement"]
    R -->|route: 'require_approval' (amount > $500)| G["manager_approval_gate (HITL)"]
    G -->|route: 'approved'| S
    G -->|route: 'rejected'| Deny["notify_rejection"]

    style R fill:#fff3cd,stroke:#e67e22
    style G fill:#d1ecf1,stroke:#17a2b8
    style S fill:#d4edda,stroke:#28a745
    style Deny fill:#f8d7da,stroke:#dc3545
```

### Key Architectural Concepts
1. **Conditional Policy Gating:** Small standard claims pass through the fast-path auto-approval edge without human friction.
2. **Interrupt & Resume Checkpoints:** High-value claims route into `manager_approval_gate`. In production, the gate suspends execution (`NodeStatus.WAITING` or `RequestInput`), persisting the session state until the manager reviews and supplies the resolution.
3. **Deterministic Separation:** The rejection leaf node `notify_rejection` has no physical edge to payment execution, guaranteeing funds are never disbursed on rejected claims.

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
