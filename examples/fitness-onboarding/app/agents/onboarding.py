"""Builder for the fixed-order fitness onboarding agent."""

from google.adk.agents import SequentialAgent
from google.adk.agents.callback_context import CallbackContext

from .consultation import ConsultationAgentBuilder
from .intake import IntakeAgentBuilder
from .welcome import WelcomeAgentBuilder


def initialize_onboarding_state(callback_context: CallbackContext) -> None:
    """Reset invocation-scoped onboarding state before the sequence starts."""
    callback_context.state["intake_status"] = "invalid"
    callback_context.state["client_profile"] = {}
    callback_context.state["intake_errors"] = ["intake validation did not complete"]
    callback_context.state["booking_result"] = {}
    callback_context.state["email_result"] = {}


class FitnessOnboardingAgentBuilder:
    """Compose fresh stage agents into the documented fixed sequence."""

    def __init__(
        self,
        intake_builder: IntakeAgentBuilder,
        consultation_builder: ConsultationAgentBuilder,
        welcome_builder: WelcomeAgentBuilder,
    ) -> None:
        self._intake_builder = intake_builder
        self._consultation_builder = consultation_builder
        self._welcome_builder = welcome_builder

    def build(self) -> SequentialAgent:
        """Create the root sequential agent with fresh children."""
        return SequentialAgent(
            name="fitness_onboarding_agent",
            description=(
                "Onboards a qualified fitness client through intake validation, "
                "consultation planning, booking, and welcome-email delivery."
            ),
            sub_agents=[
                self._intake_builder.build(),
                self._consultation_builder.build(),
                self._welcome_builder.build(),
            ],
            before_agent_callback=initialize_onboarding_state,
        )
