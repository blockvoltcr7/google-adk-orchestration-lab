"""Builder for the explicit fitness-onboarding graph."""

from google.adk.agents import LlmAgent
from google.adk.workflow import Workflow

from app.tools import (
    create_booking,
    render_intake_correction,
    render_onboarding_confirmation,
    send_email,
    validate_intake,
)

from .consultation import ConsultationAgentBuilder
from .welcome import WelcomeAgentBuilder


class FitnessOnboardingGraphBuilder:
    """Compose fresh agents and deterministic nodes into a routed workflow."""

    def __init__(
        self,
        consultation_builder: ConsultationAgentBuilder,
        welcome_builder: WelcomeAgentBuilder,
    ) -> None:
        self._consultation_builder = consultation_builder
        self._welcome_builder = welcome_builder

    def build(self) -> Workflow:
        """Create a new graph with structurally isolated valid and invalid paths."""
        consultation_agent = self._consultation_builder.build()
        welcome_agent = self._welcome_builder.build()
        return self._compose(consultation_agent, welcome_agent)

    @staticmethod
    def _compose(
        consultation_agent: LlmAgent,
        welcome_agent: LlmAgent,
    ) -> Workflow:
        return Workflow(
            name="fitness_onboarding_graph",
            description=(
                "Routes a qualified fitness-client intake through validation, "
                "consultation planning, booking, welcome drafting, and local delivery."
            ),
            edges=[
                ("START", validate_intake),
                (
                    validate_intake,
                    {
                        "valid": consultation_agent,
                        "invalid": render_intake_correction,
                    },
                ),
                (consultation_agent, create_booking),
                (create_booking, welcome_agent),
                (welcome_agent, send_email),
                (send_email, render_onboarding_confirmation),
            ],
        )
