"""Unit and runner tests for iterative refinement cyclic graph."""

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import Workflow
from google.genai import types

from app.agent import root_agent
from app.nodes import evaluate_spec_quality


def test_graph_validation_and_cycle_structure():
    """Verify that the cyclic graph compiles with conditional route."""
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "spec_refinement_graph"
    # Back-edge must be conditional
    eval_edges = [
        (e.from_node.name, e.route, e.to_node.name)
        for e in root_agent.graph.edges
        if e.from_node.name == "evaluate_spec_quality"
    ]
    routes = {e[1]: e[2] for e in eval_edges}
    assert routes == {
        "refine": "draft_specification",
        "publish": "publish_specification",
    }


def test_evaluator_scoring_gate():
    """Test evaluator scoring behavior on iteration 1 vs iteration 2."""
    spec_v1 = {
        "iteration": 1,
        "security_controls": ["Basic Auth"],
        "api_endpoints": ["/health"],
    }
    res_v1 = evaluate_spec_quality(spec_v1)
    assert res_v1.actions.route == "refine"
    assert res_v1.output["quality_score"] < 85

    spec_v2 = {
        "iteration": 2,
        "security_controls": ["mTLS Zero-Trust", "Cloud KMS"],
        "api_endpoints": ["/ingest", "/health", "/metrics"],
    }
    res_v2 = evaluate_spec_quality(spec_v2)
    assert res_v2.actions.route == "publish"
    assert res_v2.output["quality_score"] >= 85


def test_end_to_end_cyclic_refinement():
    """Verify workflow loops through draft -> evaluate -> refine -> draft -> publish."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = '{"title": "Enterprise Event Streaming Broker"}'
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
    assert final_output["status"] == "APPROVED_AND_PUBLISHED"
    # Verifies it completed 2 iterations to meet the quality bar
    assert final_output["iterations_taken"] == 2
    assert final_output["final_score"] >= 85
    assert "Cloud Spanner" in final_output["summary"]
