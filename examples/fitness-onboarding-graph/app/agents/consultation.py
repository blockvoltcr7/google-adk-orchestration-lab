"""Builder for the consultation-planning graph node."""

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.models import ClientIntake, ConsultationPlan
from app.prompts import PromptLoader


class ConsultationAgentBuilder:
    """Build fresh, typed consultation-agent nodes."""

    def __init__(
        self,
        model: str | BaseLlm,
        prompt_loader: PromptLoader,
    ) -> None:
        self._model = model
        self._prompt_loader = prompt_loader

    def build(self) -> LlmAgent:
        """Create an unparented consultation agent for graph composition."""
        prompt = self._prompt_loader.load("consultation_agent")
        return LlmAgent(
            name=prompt.id,
            model=self._model,
            description=prompt.description,
            instruction=prompt.instruction,
            input_schema=ClientIntake,
            output_schema=ConsultationPlan,
            output_key="consultation_plan",
        )
