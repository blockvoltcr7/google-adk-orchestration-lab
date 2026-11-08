"""Unit and runner tests for conditional routing graph."""

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import Workflow, DEFAULT_ROUTE
from google.genai import types

from app.agent import root_agent
from app.nodes import triage_ticket


def test_triage_routing_logic():
    """Verify triage_ticket emits correct route labels."""
    billing_ev = triage_ticket({
        "ticket_id": "T-1",
        "customer_id": "C-1",
        "subject": "Incorrect Invoice Charge",
        "body": "I was double charged on my subscription invoice.",
    })
    assert billing_ev.actions.route == "billing"

    tech_ev = triage_ticket({
        "ticket_id": "T-2",
        "customer_id": "C-2",
        "subject": "API 500 Internal Error",
        "body": "We are getting timeout exceptions when calling endpoint /v1/users.",
    })
    assert tech_ev.actions.route == "technical"

    account_ev = triage_ticket({
        "ticket_id": "T-3",
        "customer_id": "C-3",
        "subject": "Password reset needed",
        "body": "User cannot login with SSO MFA credentials.",
    })
    assert account_ev.actions.route == "account"

    fallback_ev = triage_ticket({
        "ticket_id": "T-4",
        "customer_id": "C-4",
        "subject": "Office Hours Inquiry",
        "body": "What time does the conference center open tomorrow?",
    })
    assert fallback_ev.actions.route == DEFAULT_ROUTE


def test_graph_topology():
    """Verify routes and connectivity."""
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "service_desk_router_graph"
    edges = [(e.from_node.name, e.route, e.to_node.name) for e in root_agent.graph.edges]
    # Check that triage_ticket routes to all 4 destinations
    triage_targets = {e[1]: e[2] for e in edges if e[0] == "triage_ticket"}
    assert triage_targets == {
        "billing": "handle_billing",
        "technical": "handle_technical",
        "account": "handle_account",
        DEFAULT_ROUTE: "handle_fallback",
    }


def test_end_to_end_technical_route():
    """Execute graph with technical ticket and verify terminal resolution."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = (
        '{"ticket_id": "T-101", "customer_id": "C-999", '
        '"subject": "System Crash on Data Export", '
        '"body": "Database query timeout and NullPointer exception thrown."}'
    )
    content = types.Content(role="user", parts=[types.Part.from_text(text=payload)])

    events = list(
        runner.run(
            new_message=content,
            user_id="user_1",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    assert len(events) > 0
    outputs = [e.output for e in events if e.output]
    final_output = outputs[-1]
    assert final_output["ticket_id"] == "T-101"
    assert final_output["department"] == "Engineering Support"
    assert final_output["sla_hours"] == 2
    assert "Site Reliability Engineer" in final_output["assigned_specialist"]
