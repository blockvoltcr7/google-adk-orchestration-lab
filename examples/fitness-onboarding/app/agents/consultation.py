"""Builder for the consultation-planning LLM agent."""

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.prompts import PromptLoader


class ConsultationAgentBuilder:
    """Build fresh consultation-agent instances."""

    def __init__(
        self,
        model: str | BaseLlm,
        prompt_loader: PromptLoader,
    ) -> None:
        self._model = model
        self._prompt_loader = prompt_loader

    def build(self) -> LlmAgent:
        """Create an unparented consultation agent."""
        prompt = self._prompt_loader.load("consultation_agent")
        return LlmAgent(
            name=prompt.id,
            model=self._model,
            description=prompt.description,
            instruction=prompt.instruction,
            output_key="consultation_plan",
        )
