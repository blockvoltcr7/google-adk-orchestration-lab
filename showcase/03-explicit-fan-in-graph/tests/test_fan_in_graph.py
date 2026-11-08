"""Unit and runner tests for explicit fan-in JoinNode graph."""

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import Workflow, JoinNode
from google.genai import types

from app.agent import root_agent, gather_diligence


def test_graph_topology():
    """Verify JoinNode synchronization barrier wiring."""
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "due_diligence_graph"
    assert isinstance(gather_diligence, JoinNode)

    edges = [(e.from_node.name, e.to_node.name) for e in root_agent.graph.edges]
    # Verify 3 branches entering gather_diligence
    incoming_to_gather = [e[0] for e in edges if e[1] == "gather_diligence"]
    assert set(incoming_to_gather) == {
        "analyze_financials",
        "evaluate_competitors",
        "audit_compliance",
    }
    # Verify gather_diligence exits to synthesize_executive_dossier
    outgoing_from_gather = [e[1] for e in edges if e[0] == "gather_diligence"]
    assert outgoing_from_gather == ["synthesize_executive_dossier"]


def test_end_to_end_fan_in_execution():
    """Verify all 3 parallel nodes run and synthesize into ExecutiveDossier."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = '{"name": "Starlight Cloud", "ticker": "STAR", "industry": "Infrastructure"}'
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
    assert final_output["company_name"] == "Starlight Cloud"
    assert final_output["ticker"] == "STAR"
    assert final_output["investment_verdict"] == "STRONG BUY"
    assert "Growth +24.5%" in final_output["financial_summary"]
    assert "Wide" in final_output["competitive_summary"]
    assert "Good Standing" in final_output["compliance_summary"]
