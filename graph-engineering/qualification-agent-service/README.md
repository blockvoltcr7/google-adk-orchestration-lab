# Inbound Lead Qualification Service (Google ADK 2 + FastAPI)

A production-ready microservice built with **Google Agent Development Kit (ADK 2)**, **FastAPI**, and **Google Cloud Run**.

Demonstrates how to handle inbound webhooks/API requests where **every request carries user identity & CRM metadata** (`user_id`, `contact_id`, `calendar_id`, `metadata`) that is **injected into ADK Session State** rather than polluting prompt context tokens.

---

## 1. Key Architectural Features

- **Session State Injection:** Ingests user identity and CRM attributes on every turn via `state_delta` or initial session creation without stuffing raw JSON into conversational history.
- **State-Aware Tools:** Tools access session state on demand via `tool_context: ToolContext` (e.g. `get_lead_profile`, `record_qualification`, `book_calendar_slot`).
- **Dual Runtime Support:**
  - **FastAPI / Cloud Run:** Exposes high-throughput REST and SSE endpoints (`/qualify` and `/qualify/stream`).
  - **ADK Native CLI:** Exposes `root_agent` so developers can use `adk web` for visual debugging and `adk eval` for evaluation suites.

---

## 2. Inbound Payload Specification

Every inbound request sends this JSON body to `POST /qualify`:

```json
{
  "user_id": "usr_9981",
  "contact_id": "cnt_4432",
  "calendar_id": "sales-team-cal@acmecorp.com",
  "message": "Hi, I want to see if our 50-person sales team is a fit for your enterprise plan.",
  "metadata": {
    "company": "Acme Corp",
    "company_size": 50,
    "current_crm": "Salesforce",
    "budget_range": "$10k-$25k"
  }
}
```

### What Happens Internally:
1. The service creates or loads the session: `sess_{contact_id}`.
2. `user_id`, `contact_id`, `calendar_id`, and `metadata` are injected into **Session State**.
3. `message` is passed as conversational `Content` to the Gemini model.
4. The model calls `get_lead_profile` to inspect the injected state, evaluates qualification criteria, records the determination into `session.state["qualification"]`, and proactively books a demo slot onto `calendar_id`.

---

## 3. Running Locally

### Option A: Running as FastAPI Microservice
```bash
./run_local.sh --api
# Server starts on http://localhost:8080
# Swagger Docs: http://localhost:8080/docs
```

### Option B: Running in ADK Web UI
```bash
./run_local.sh --web
# Starts ADK Web UI on http://localhost:8000
```

---

## 4. Evaluation Testing with Session State Injection

### How to Inject State in ADK Eval Sets (`evals/lead_qualification_evals.json`)
In ADK's native evaluation format, specify `session_input.state` inside each `EvalCase`:

```json
{
  "eval_id": "eval_enterprise_lead",
  "session_input": {
    "app_name": "qualification_app",
    "user_id": "usr_enterprise_01",
    "state": {
      "user_id": "usr_enterprise_01",
      "contact_id": "cnt_8841",
      "calendar_id": "sales-enterprise@acme.com",
      "metadata": {
        "company_size": 250,
        "budget_range": "$50k-$100k"
      }
    }
  },
  "conversation": [
    {
      "invocation_id": "inv_1",
      "user_content": {
        "role": "user",
        "parts": [{"text": "Can we book an enterprise demo?"}]
      }
    }
  ]
}
```

### Running the Evaluation Suite
```bash
python tests/run_evals.py
```
This executes each test case, verifies that tools read the injected state, and asserts that the resulting qualification status and calendar booking are recorded into session state.

---

## 5. Deployment Guide: Cloud Run vs. Agent Engine

| Dimension | Cloud Run (FastAPI + ADK) — **Recommended** | Vertex AI Agent Engine (Reasoning Engine) |
|---|---|---|
| **Custom Payloads** | Full control over Pydantic validation & custom headers | Strict method signature wrapper |
| **Session Persistence** | Pluggable (Cloud SQL, Firestore, Spanner) | Vertex-managed session storage |
| **Streaming** | Native SSE (`/qualify/stream`) & WebSockets | SDK streaming iterator |
| **Cold Starts & Cost** | Scale-to-zero, $0 when idle, VPC-SC support | Managed provisioning fee |

### Deploying to Google Cloud Run
Ensure `gcloud` is authenticated and configured with your project:

```bash
./deploy.sh
```

Or run manually:
```bash
gcloud run deploy lead-qualification-service \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "ADK_MODEL=gemini-2.5-flash,GOOGLE_GENAI_USE_VERTEXAI=True"
```
