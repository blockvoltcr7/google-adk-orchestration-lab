"""Builder for the intake LLM agent."""

from collections.abc import Callable
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.prompts import PromptLoader


class IntakeAgentBuilder:
    """Build fresh intake-agent instances with injected dependencies."""

    def __init__(
        self,
        model: str | BaseLlm,
        prompt_loader: PromptLoader,
        validation_tool: Callable[..., dict[str, Any]],
    ) -> None:
        self._model = model
        self._prompt_loader = prompt_loader
        self._validation_tool = validation_tool

    def build(self) -> LlmAgent:
        """Create an unparented intake agent."""
        prompt = self._prompt_loader.load("intake_agent")
        return LlmAgent(
            name=prompt.id,
            model=self._model,
            description=prompt.description,
            instruction=prompt.instruction,
            tools=[self._validation_tool],
            output_key="intake_summary",
        )
