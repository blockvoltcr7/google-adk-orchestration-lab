"""Deterministic tests for graph topology and agent construction."""

from google.adk.agents import LlmAgent
from google.adk.workflow import Workflow

from app.agent import root_agent
from app.agents import (
    ConsultationAgentBuilder,
    FitnessOnboardingGraphBuilder,
    WelcomeAgentBuilder,
)
from app.prompts import YamlPromptLoader

EXPECTED_EDGES = [
    ("__START__", None, "validate_intake"),
    ("validate_intake", "valid", "consultation_agent"),
    ("validate_intake", "invalid", "render_intake_correction"),
    ("consultation_agent", None, "create_booking"),
    ("create_booking", None, "welcome_agent"),
    ("welcome_agent", None, "send_email"),
    ("send_email", None, "render_onboarding_confirmation"),
]


def _edge_signature(workflow: Workflow) -> list[tuple[str, object, str]]:
    return [
        (edge.from_node.name, edge.route, edge.to_node.name)
        for edge in workflow.graph.edges
    ]


def _builder() -> FitnessOnboardingGraphBuilder:
    loader = YamlPromptLoader()
    return FitnessOnboardingGraphBuilder(
        consultation_builder=ConsultationAgentBuilder(
            model="gemini-3.6-flash",
            prompt_loader=loader,
        ),
        welcome_builder=WelcomeAgentBuilder(
            model="gemini-3.6-flash",
            prompt_loader=loader,
        ),
    )


def test_root_agent_is_workflow_with_expected_routes() -> None:
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "fitness_onboarding_graph"
    assert _edge_signature(root_agent) == EXPECTED_EDGES


def test_invalid_route_has_no_path_to_side_effect_nodes() -> None:
    adjacency: dict[str, list[str]] = {}
    for edge in root_agent.graph.edges:
        adjacency.setdefault(edge.from_node.name, []).append(edge.to_node.name)

    reachable = set()
    pending = ["render_intake_correction"]
    while pending:
        node = pending.pop()
        if node in reachable:
            continue
        reachable.add(node)
        pending.extend(adjacency.get(node, []))

    assert "create_booking" not in reachable
    assert "send_email" not in reachable


def test_builders_return_fresh_typed_agents_and_workflows() -> None:
    builder = _builder()
    first = builder.build()
    second = builder.build()

    assert first is not second
    first_agents = {
        node.name: node for node in first.graph.nodes if isinstance(node, LlmAgent)
    }
    second_agents = {
        node.name: node for node in second.graph.nodes if isinstance(node, LlmAgent)
    }
    assert first_agents["consultation_agent"] is not second_agents["consultation_agent"]
    assert first_agents["welcome_agent"] is not second_agents["welcome_agent"]
    assert first_agents["consultation_agent"].tools == []
    assert first_agents["welcome_agent"].tools == []
