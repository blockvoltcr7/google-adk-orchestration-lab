/**
 * Agent SDK Builder Lab - Interactive Architecture Data Model
 * Defines chapters, scenarios, node coordinates, narration scripts, and architectural deep-dives.
 */

window.AGENT_LAB_DATA = {
  version: "2.0.0",
  title: "Agent SDK Builder Lab: End-to-End Orchestration Architecture",
  subtitle: "BUILD • TEST • EVALUATE • DEPLOY",
  totalDuration: 180, // 3 minutes total runtime

  // Node coordinates on a 1920x1080 canvas
  nodes: {
    user: {
      id: "user",
      x: 140,
      y: 200,
      width: 170,
      height: 190,
      title: "USER",
      badge: "Perimeter",
      icon: "user",
      items: ["Web App", "Mobile", "API / CLI"],
      color: "#00d2ff",
      accent: "#3a7bd5",
      camera: { x: 225, y: 295, zoom: 1.4 },
      adkPattern: "Input Interface & Gateway",
      description: "Omnichannel ingest endpoint accepting structured API requests, user chat prompts, and multimodal streams.",
      adkSnippet: `# Client request arrives via REST / WebSocket / ADK Client
from google.adk.events import UserMessage

msg = UserMessage(
    content="Book a qualification call with Acme Corp lead",
    session_id="sess_8912",
    client_channel="web_app"
)`
    },
    goal: {
      id: "goal",
      x: 230,
      y: 40,
      width: 210,
      height: 120,
      title: "GOAL",
      badge: "Objective",
      icon: "target",
      items: ["Help user accomplish", "Complex tasks", "accurately + safely"],
      color: "#00f2fe",
      accent: "#4facfe",
      camera: { x: 335, y: 100, zoom: 1.3 },
      adkPattern: "System Directive / Objective Spec",
      description: "High-level deterministic objective and invariant constraints framing the agent's task boundary.",
      adkSnippet: `GOAL_PROMPT = """
Help user accomplish complex CRM qualification tasks 
accurately and safely with zero hallucinated tool args.
"""`
    },
    context: {
      id: "context",
      x: 80,
      y: 430,
      width: 180,
      height: 180,
      title: "CONTEXT",
      badge: "State Feed",
      icon: "layers",
      items: ["History", "Preferences", "State", "Memory"],
      color: "#00f2fe",
      accent: "#00c6ff",
      camera: { x: 170, y: 520, zoom: 1.4 },
      adkPattern: "Session Context & Memory Hook",
      description: "Pre-execution context assembly gathering conversation history, user preferences, and tenant session state.",
      adkSnippet: `ctx = await agent.get_context(
    session_id=msg.session_id,
    include_history=True,
    include_user_prefs=True
)`
    },
    taskFlow: {
      id: "taskFlow",
      x: 30,
      y: 650,
      width: 220,
      height: 380,
      title: "TASK FLOW",
      badge: "Pipeline",
      icon: "git-commit",
      items: [
        "1. Understand Intent",
        "2. Retrieve Context",
        "3. Select Tools",
        "4. Execute",
        "5. Evaluate",
        "6. Respond"
      ],
      color: "#00c6ff",
      accent: "#0072ff",
      camera: { x: 140, y: 840, zoom: 1.25 },
      adkPattern: "SequentialPipeline & Graph Topology",
      description: "Deterministic 6-phase lifecycle guaranteeing orderly execution, verification, and auditability.",
      adkSnippet: `# ADK 2.x Graph Workflow topology
workflow = Workflow(
    nodes=[understand_intent, retrieve_ctx, select_tools, execute, evaluate, respond],
    edges=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
)`
    },
    agent: {
      id: "agent",
      x: 340,
      y: 170,
      width: 230,
      height: 250,
      title: "AGENT",
      badge: "Core Controller",
      icon: "cpu",
      items: ["Neural Ingest", "Context Assembler", "Goal Alignment"],
      color: "#00f2fe",
      accent: "#7f00ff",
      camera: { x: 455, y: 295, zoom: 1.35 },
      adkPattern: "LlmAgent / Primary Controller",
      description: "Central LLM agent reasoning hub receiving hydrated context and generating bounded execution trajectories.",
      adkSnippet: `from google.adk.agents import LlmAgent

primary_agent = LlmAgent(
    model="gemini-2.5-pro",
    system_prompt=GOAL_PROMPT,
    sub_agents=[reasoning_orchestrator]
)`
    },
    reasoning: {
      id: "reasoning",
      x: 650,
      y: 170,
      width: 230,
      height: 310,
      title: "REASONING / ORCHESTRATION",
      badge: "Decide & Plan",
      icon: "network",
      items: ["Planner", "Tool Selection", "Reflection"],
      color: "#a18cd1",
      accent: "#fbc2eb",
      camera: { x: 765, y: 325, zoom: 1.3 },
      adkPattern: "Dynamic Orchestrator & Reflection Loop",
      description: "Multi-step plan decomposition, heuristic tool filtering, and recursive reflection against intermediate state.",
      adkSnippet: `# Reflection & Plan refinement
class Orchestrator:
    async def step(self, ctx):
        plan = await self.planner.generate(ctx)
        tool_call = await self.selector.choose(plan, ctx.available_tools)
        return tool_call`
    },
    memory: {
      id: "memory",
      x: 650,
      y: 530,
      width: 210,
      height: 250,
      title: "MEMORY",
      badge: "Persistence",
      icon: "hard-drive",
      items: ["Short Term", "Long Term", "Vector Store", "State Store"],
      color: "#00d2ff",
      accent: "#00f2fe",
      camera: { x: 755, y: 655, zoom: 1.35 },
      adkPattern: "Persistent Storage & Vector Store",
      description: "Hierarchical memory combining scratchpad working memory, Postgres state store, and Pinecone vector store.",
      adkSnippet: `state_store.save_snapshot(ctx.session_id, ctx.state)
vector_docs = await vector_store.similarity_search(query, k=5)`
    },
    guardrails: {
      id: "guardrails",
      x: 910,
      y: 550,
      width: 230,
      height: 250,
      title: "GUARDRAILS",
      badge: "Safety Gate",
      icon: "shield",
      items: ["Content Safety", "PII Redaction", "Rate Limits", "Policy Checks"],
      routes: ["FAIL -> ROUTE BACK"],
      color: "#ff007f",
      accent: "#7928ca",
      camera: { x: 1025, y: 675, zoom: 1.35 },
      adkPattern: "Safety Interceptor & RouteGuard",
      description: "Active pre-execution security layer enforcing automated PII masking, safety filtering, and enterprise policy rules.",
      adkSnippet: `@guardrail.intercept
async def check_safety(call: ToolCall):
    redacted = pii_engine.mask(call.payload)
    if safety_model.check_toxicity(redacted) > 0.05:
        raise PolicyViolationException("Toxic payload detected")
    return redacted`
    },
    tools: {
      id: "tools",
      x: 950,
      y: 170,
      width: 290,
      height: 330,
      title: "TOOLS / MCP SERVERS",
      badge: "Action Space",
      icon: "server",
      items: [
        "CRM",
        "PostgreSQL (Data)",
        "Email (SendGrid)",
        "Calendar (Google)",
        "Vector DB (Pinecone)",
        "... More Tools"
      ],
      color: "#00f2fe",
      accent: "#4facfe",
      camera: { x: 1095, y: 335, zoom: 1.25 },
      adkPattern: "McpToolset & Tool Integration",
      description: "Standardized Model Context Protocol (MCP) tool integration layer communicating with SaaS and database backends.",
      adkSnippet: `from google.adk.tools.mcp import McpToolset

tools = McpToolset(servers=[
    "mcp://crm-service:8080",
    "mcp://postgres-service:5432",
    "mcp://sendgrid-mailer:8081",
    "mcp://pinecone-vector:443"
])`
    },
    evalGate: {
      id: "evalGate",
      x: 1300,
      y: 170,
      width: 250,
      height: 350,
      title: "EVALUATION GATE",
      badge: "Quality Barrier",
      icon: "check-circle",
      items: [
        "Correctness",
        "Groundedness",
        "Safety",
        "Tool Selection",
        "Latency",
        "Cost"
      ],
      verdict: "PASS",
      retryRoute: "RETRY?",
      color: "#00f5a0",
      accent: "#00d2ff",
      camera: { x: 1425, y: 345, zoom: 1.3 },
      adkPattern: "Evaluator / Refinement Gate",
      description: "Automated LLM-as-a-judge & deterministic validation gate measuring quality, groundedness, and budget compliance.",
      adkSnippet: `eval_result = await eval_gate.grade(
    trajectory=ctx.trajectory,
    rubric=["correctness", "groundedness", "safety", "cost"]
)
if not eval_result.passed:
    yield Event(route="RETRY", feedback=eval_result.reasons)`
    },
    observability: {
      id: "observability",
      x: 1220,
      y: 560,
      width: 230,
      height: 250,
      title: "OBSERVABILITY",
      badge: "Telemetry",
      icon: "activity",
      items: ["Tracing", "Logs", "Metrics", "Evaluations", "Alerts"],
      sparkline: true,
      color: "#00c6ff",
      accent: "#0072ff",
      camera: { x: 1335, y: 685, zoom: 1.35 },
      adkPattern: "OpenTelemetry Tracing & Cloud Monitoring",
      description: "Distributed trace spans, prompt token usage, latency breakdowns, and automated anomaly alert rules.",
      adkSnippet: `tracer.record_span("tool_exec", duration_ms=142, cost_usd=0.0014)
metrics.increment("agent.eval.pass_count")`
    },
    evalEvidence: {
      id: "evalEvidence",
      x: 1570,
      y: 650,
      width: 230,
      height: 220,
      title: "EVAL EVIDENCE",
      badge: "Audit Ledger",
      icon: "file-text",
      items: ["Test Cases", "Trajectory", "Tool Calls", "Latency", "Cost", "Score"],
      color: "#a18cd1",
      accent: "#fbc2eb",
      camera: { x: 1685, y: 760, zoom: 1.4 },
      adkPattern: "Trajectory Logging & Benchmark Store",
      description: "Immutable trajectory logging recording deterministic inputs, tool outputs, and LLM reasoning steps.",
      adkSnippet: `eval_evidence_store.save({
    "test_id": "test_crm_booking_004",
    "score": 98.4,
    "latency_ms": 1120,
    "cost_usd": 0.0032
})`
    },
    deployment: {
      id: "deployment",
      x: 1600,
      y: 200,
      width: 210,
      height: 280,
      title: "DEPLOYMENT",
      badge: "Release Stage",
      icon: "cloud",
      items: ["Staging", "Production", "Monitoring", "Alerts"],
      parentTrigger: "HUMAN APPROVAL",
      color: "#00f5a0",
      accent: "#00c6ff",
      camera: { x: 1705, y: 340, zoom: 1.35 },
      adkPattern: "Human-in-the-Loop & Staged Rollout",
      description: "Safe staged release pipeline requiring human approval for high-consequence tools before production rollout.",
      adkSnippet: `# Human in the loop approval node
if action.risk_level == "HIGH":
    yield RequestInput(
        interrupt_id="approval_gate",
        message="Approve mass customer update?",
        payload=action.summary
    )`
    }
  },

  // Interactive Video Chapters Timeline
  chapters: [
    {
      id: "ch1",
      title: "1. Intake & Context Ingestion",
      start: 0,
      end: 20,
      focusNode: "user",
      activeNodes: ["user", "goal", "context", "agent"],
      activeConnections: ["user->agent", "context->agent", "goal->agent"],
      status: "Ingesting user input across Web, Mobile & CLI...",
      subtitle: "Every agentic execution begins at the client perimeter. Requests from Web, Mobile, or CLI are captured alongside conversation history, preferences, and session state.",
      voiceText: "Every agentic execution begins at the client perimeter. Requests from Web App, Mobile, or API are captured alongside user preferences, runtime state, and persistent memory."
    },
    {
      id: "ch2",
      title: "2. Task Flow & Intent Mapping",
      start: 20,
      end: 40,
      focusNode: "taskFlow",
      activeNodes: ["taskFlow", "agent"],
      activeConnections: ["taskFlow->agent"],
      status: "Executing 6-Phase Task Lifecycle: Understanding Intent & Context...",
      subtitle: "The Agent invokes its 6-phase Task Flow: Understand Intent, Retrieve Context, Select Tools, Execute, Evaluate, and Respond.",
      voiceText: "The Agent invokes its structured 6-phase Task Flow: Understand Intent, Retrieve Context, Select Tools, Execute, Evaluate, and Respond."
    },
    {
      id: "ch3",
      title: "3. Reasoning & Orchestration",
      start: 40,
      end: 65,
      focusNode: "reasoning",
      activeNodes: ["agent", "reasoning", "memory"],
      activeConnections: ["agent->reasoning", "reasoning<->memory"],
      status: "Synthesizing execution plan across Memory Stores...",
      subtitle: "The Reasoning and Orchestration engine decomposes the goal using dedicated Planners, heuristic Tool Selection, and Reflection across Short-Term, Long-Term, Vector, and State memory stores.",
      voiceText: "The Reasoning and Orchestration engine decomposes the goal using dedicated Planners, Tool Selection algorithms, and Reflection across Short-Term, Long-Term, Vector, and State stores."
    },
    {
      id: "ch4",
      title: "4. Guardrails & Policy Checks",
      start: 65,
      end: 90,
      focusNode: "guardrails",
      activeNodes: ["memory", "guardrails", "reasoning"],
      activeConnections: ["memory->guardrails", "guardrails->tools", "guardrails--fail->reasoning"],
      status: "Validating Content Safety, PII Redaction, and Rate Limits...",
      subtitle: "Before any external action is taken, Guardrails enforce Content Safety, automated PII Redaction, Rate Limiting, and Policy Checks. If any check fails, execution routes back safely.",
      voiceText: "Before any external action is executed, Guardrails enforce Content Safety, PII Redaction, Rate Limits, and Policy Checks. If any violation is detected, the workflow instantly routes back."
    },
    {
      id: "ch5",
      title: "5. Tools & MCP Server Invocation",
      start: 90,
      end: 120,
      focusNode: "tools",
      activeNodes: ["guardrails", "tools", "evalGate"],
      activeConnections: ["guardrails->tools", "tools<->evalGate"],
      status: "Dispatching MCP calls to CRM, Postgres, SendGrid, Calendar, and Pinecone...",
      subtitle: "The agent invokes standardized Model Context Protocol (MCP) servers: querying Postgres, synchronizing CRM records, dispatching SendGrid emails, and booking Google Calendar slots.",
      voiceText: "The agent invokes standardized Model Context Protocol servers: querying Postgres data, updating CRM records, dispatching SendGrid emails, and booking Google Calendar events."
    },
    {
      id: "ch6",
      title: "6. Evaluation Gate & Self-Correction",
      start: 120,
      end: 145,
      focusNode: "evalGate",
      activeNodes: ["tools", "evalGate", "reasoning"],
      activeConnections: ["tools->evalGate", "evalGate--retry->reasoning"],
      status: "Grading Correctness, Groundedness, Safety, Tool Selection, Latency & Cost...",
      subtitle: "Outputs are evaluated at the Evaluation Gate across 6 dimensions: Correctness, Groundedness, Safety, Tool Selection, Latency, and Cost. If quality criteria fail, a Retry loop triggers reflection.",
      voiceText: "Outputs are graded at the Evaluation Gate across 6 key metrics: Correctness, Groundedness, Safety, Tool Selection, Latency, and Cost. A passing grade unlocks the deployment pipeline."
    },
    {
      id: "ch7",
      title: "7. Observability & Evaluation Evidence",
      start: 145,
      end: 165,
      focusNode: "observability",
      activeNodes: ["observability", "evalEvidence", "evalGate"],
      activeConnections: ["evalGate->observability", "observability->evalEvidence"],
      status: "Recording distributed traces, latency profiles, cost tokens, and test trajectories...",
      subtitle: "Full-stack Observability streams real-time Tracing, Logs, Metrics, Evaluations, and Alerts while storing deterministic Eval Evidence for benchmark analysis.",
      voiceText: "Full-stack Observability captures distributed traces, logs, latency metrics, and alerts, indexing immutable evaluation evidence for continuous benchmarking."
    },
    {
      id: "ch8",
      title: "8. Human Approval & Production Deployment",
      start: 165,
      end: 180,
      focusNode: "deployment",
      activeNodes: ["evalGate", "deployment"],
      activeConnections: ["evalGate->deployment"],
      status: "Human approval verified. Deployed to Staging & Production with continuous alerts!",
      subtitle: "Critical actions prompt Human-in-the-Loop verification before rolling out across Staging, Production, live Monitoring, and automated Alert monitors. Build. Test. Evaluate. Deploy.",
      voiceText: "Critical actions prompt Human Approval before rolling out across Staging, Production, live Monitoring, and automated Alerting. Build. Test. Evaluate. Deploy."
    }
  ],

  // Interactive Simulation Scenarios
  scenarios: {
    happyPath: {
      id: "happyPath",
      name: "Standard Enterprise Run (Happy Path)",
      badge: "Standard Flow",
      description: "User requests CRM lead qualification and calendar booking. Passes guardrails, executes MCP tools, clears all eval criteria, and deploys.",
      steps: [
        { node: "user", text: "Incoming user query via Web App: 'Qualify lead Acme Corp and schedule meeting'" },
        { node: "context", text: "Hydrated history: Acme Corp lead score 85, Tier 1 VIP customer" },
        { node: "agent", text: "Central LLM initializes task plan and state tracking" },
        { node: "reasoning", text: "Planner selects CRM + Google Calendar MCP tools" },
        { node: "guardrails", text: "Guardrails PASS: No PII leak, within 50 req/min rate limit" },
        { node: "tools", text: "CRM lead updated -> Google Calendar invite dispatched for Friday 2 PM" },
        { node: "evalGate", text: "Evaluation Gate: 100% Groundedness, 0.8s Latency, $0.0021 Cost -> PASS" },
        { node: "observability", text: "Trace logged: 2 spans, 0 error rate, latency within p95 SLA" },
        { node: "deployment", text: "Automated deployment to Production with active alerts" }
      ]
    },
    guardrailFail: {
      id: "guardrailFail",
      name: "Security Interception (Guardrail Route-Back)",
      badge: "Security Defense",
      description: "Prompt injection / SSN data detected in query. Guardrail intercepts, redacts sensitive payload, and routes back for clarification.",
      steps: [
        { node: "user", text: "Malicious prompt or unmasked SSN submitted in query" },
        { node: "context", text: "Raw context loaded into orchestrator" },
        { node: "guardrails", text: "GUARDRAIL ALERT: PII Detector triggers on SSN pattern [XXX-XX-XXXX]" },
        { node: "guardrails", text: "ROUTE BACK: Halting MCP execution; sanitizing input and returning warning to user" },
        { node: "observability", text: "Security anomaly alert fired to Slack SecOps channel" }
      ]
    },
    evalRetry: {
      id: "evalRetry",
      name: "Hallucination Self-Correction (Retry Loop)",
      badge: "Refinement Loop",
      description: "Agent generates ungrounded calendar time slot. Eval Gate detects hallucination and triggers RETRY loop for self-correction.",
      steps: [
        { node: "reasoning", text: "Agent proposes calendar slot outside business hours (Saturday 11 PM)" },
        { node: "tools", text: "Simulated tool proposal sent to Evaluation Gate" },
        { node: "evalGate", text: "Eval Gate FAILED Groundedness check: Proposed slot conflicts with working hours" },
        { node: "reasoning", text: "RETRY LOOP TRIGGERED: Reflection node ingests critique and queries Pinecone for business hour policy" },
        { node: "tools", text: "Corrected slot generated (Monday 10 AM) -> Tool succeeds" },
        { node: "evalGate", text: "Re-evaluation: Correctness 100%, Groundedness 100% -> PASS" }
      ]
    },
    humanApproval: {
      id: "humanApproval",
      name: "High-Stakes Human-in-the-Loop Gate",
      badge: "Governance",
      description: "Action involves sending bulk email to 5,000 customers. Agent pauses execution, yields RequestInput, and awaits executive approval.",
      steps: [
        { node: "agent", text: "Agent drafts mass email campaign to 5,000 clients" },
        { node: "tools", text: "SendGrid MCP flagged: High-consequence tool operation" },
        { node: "deployment", text: "HUMAN APPROVAL INTERRUPT: Yielding RequestInput(interrupt_id='exec_signoff')" },
        { node: "deployment", text: "Human Reviewer clicks [APPROVE] in dashboard -> Workflow resumes safely" }
      ]
    }
  }
};
