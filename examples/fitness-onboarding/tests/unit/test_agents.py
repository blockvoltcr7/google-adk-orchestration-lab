"""Unit tests for agent construction and fixed-order composition."""

from google.adk.agents import SequentialAgent

from app.agents import (
    ConsultationAgentBuilder,
    FitnessOnboardingAgentBuilder,
    IntakeAgentBuilder,
    WelcomeAgentBuilder,
)
from app.prompts import YamlPromptLoader
from app.tools import (
    create_booking_link,
    send_welcome_email,
    validate_client_intake,
)


def build_root() -> SequentialAgent:
    """Build a root agent without constructing a network-backed model object."""
    prompt_loader = YamlPromptLoader()
    return FitnessOnboardingAgentBuilder(
        intake_builder=IntakeAgentBuilder(
            model="gemini-test",
            prompt_loader=prompt_loader,
            validation_tool=validate_client_intake,
        ),
        consultation_builder=ConsultationAgentBuilder(
            model="gemini-test",
            prompt_loader=prompt_loader,
        ),
        welcome_builder=WelcomeAgentBuilder(
            model="gemini-test",
            prompt_loader=prompt_loader,
            booking_tool=create_booking_link,
            email_tool=send_welcome_email,
        ),
    ).build()


def test_root_agent_has_expected_fixed_order_and_contracts() -> None:
    root = build_root()
    intake, consultation, welcome = root.sub_agents

    assert root.name == "fitness_onboarding_agent"
    assert [agent.name for agent in root.sub_agents] == [
        "intake_agent",
        "consultation_agent",
        "welcome_agent",
    ]
    assert intake.output_key == "intake_summary"
    assert consultation.output_key == "consultation_plan"
    assert welcome.output_key == "onboarding_response"
    assert [tool.__name__ for tool in intake.tools] == ["validate_client_intake"]
    assert consultation.tools == []
    assert [tool.__name__ for tool in welcome.tools] == [
        "create_booking_link",
        "send_welcome_email",
    ]


def test_builders_return_fresh_agent_hierarchies() -> None:
    first = build_root()
    second = build_root()

    assert first is not second
    for first_child, second_child in zip(
        first.sub_agents,
        second.sub_agents,
        strict=True,
    ):
        assert first_child is not second_child
        assert first_child.parent_agent is first
        assert second_child.parent_agent is second
