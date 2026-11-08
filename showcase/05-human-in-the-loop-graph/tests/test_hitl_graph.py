"""Unit and runner tests for HITL expense authorization graph."""

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import Workflow
from google.genai import types

from app.agent import root_agent
from app.nodes import assess_expense_risk, manager_approval_gate


def test_graph_topology():
    """Verify routing and edge structure."""
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "expense_authorization_graph"

    risk_edges = {
        e.route: e.to_node.name
        for e in root_agent.graph.edges
        if e.from_node.name == "assess_expense_risk"
    }
    assert risk_edges == {
        "auto_approve": "execute_reimbursement",
        "require_approval": "manager_approval_gate",
    }

    gate_edges = {
        e.route: e.to_node.name
        for e in root_agent.graph.edges
        if e.from_node.name == "manager_approval_gate"
    }
    assert gate_edges == {
        "approved": "execute_reimbursement",
        "rejected": "notify_rejection",
    }


def test_auto_approval_execution():
    """Expense <= 500 automatically reimburses without human gate."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = '{"claim_id": "EXP-01", "employee_name": "Sam", "amount": 250.0, "business_justification": "Monitor"}'
    content = types.Content(role="user", parts=[types.Part.from_text(text=payload)])

    events = list(
        runner.run(
            new_message=content,
            user_id="user_1",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    outputs = [e.output for e in events if e.output]
    final = outputs[-1]
    assert final["status"] == "REIMBURSED"
    assert final["payout_amount"] == 250.0
    assert final["authorization_tier"] == "TIER_1_AUTO"


def test_high_value_approved_by_manager():
    """Expense > 500 with human approval proceeds to reimbursement."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = (
        '{"claim_id": "EXP-02", "employee_name": "Elena", "amount": 2400.0, '
        '"business_justification": "Conference attendance", "human_decision": "approved"}'
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

    outputs = [e.output for e in events if e.output]
    final = outputs[-1]
    assert final["status"] == "REIMBURSED"
    assert final["payout_amount"] == 2400.0
    assert "Approved by Department Manager" in final["notes"]


def test_high_value_rejected_by_manager():
    """Expense > 500 with human rejection terminates at notify_rejection."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = (
        '{"claim_id": "EXP-03", "employee_name": "Dan", "amount": 5500.0, '
        '"business_justification": "Executive travel upgrade", "human_decision": "rejected"}'
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

    outputs = [e.output for e in events if e.output]
    final = outputs[-1]
    assert final["status"] == "REJECTED"
    assert final["payout_amount"] == 0.0
    assert "Rejected by Department Manager" in final["notes"]
