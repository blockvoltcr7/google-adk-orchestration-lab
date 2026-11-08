"""Unit and runner tests for nested sub-workflows graph."""

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import Workflow
from google.genai import types

from app.agent import root_agent
from app.subworkflows import (
    ingestion_subworkflow,
    editorial_subworkflow,
    distribution_subworkflow,
)


def test_hierarchical_graph_structure():
    """Verify that root workflow contains 3 sub-workflows, which are also Workflows."""
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "publishing_studio_parent_graph"

    root_edges = [(e.from_node.name, e.to_node.name) for e in root_agent.graph.edges]
    expected_root = [
        ("__START__", "ingestion_subworkflow"),
        ("ingestion_subworkflow", "editorial_subworkflow"),
        ("editorial_subworkflow", "distribution_subworkflow"),
    ]
    assert root_edges == expected_root

    # Verify each child is an independent Workflow with its own internal graph
    for sub in [ingestion_subworkflow, editorial_subworkflow, distribution_subworkflow]:
        assert isinstance(sub, Workflow)
        assert len(sub.graph.edges) >= 2


def test_end_to_end_nested_execution():
    """Execute parent graph and verify end-to-end traversal across nested boundaries."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test_app")

    payload = (
        '{"title": "Production ADK Deployments", '
        '"raw_markdown": "# Production ADK Deployments\\nDeep dive into agent workflows on GCP.", '
        '"author": "DevOps Guild", "channel": "Engineering Weekly"}'
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
    final = outputs[-1]
    assert final["title"] == "Production ADK Deployments"
    assert final["status"] == "PUBLISHED_LIVE"
    assert final["primary_channel"] == "Engineering Weekly"
    assert "https://techradar.corp.internal/posts/" in final["live_url"]
    assert "SHA256-" in final["archive_hash"]
