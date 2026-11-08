"""Builder for the welcome LLM agent."""

from collections.abc import Callable
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.prompts import PromptLoader


class WelcomeAgentBuilder:
    """Build fresh welcome-agent instances with injected tool dependencies."""

    def __init__(
        self,
        model: str | BaseLlm,
        prompt_loader: PromptLoader,
        booking_tool: Callable[..., dict[str, Any]],
        email_tool: Callable[..., dict[str, Any]],
    ) -> None:
        self._model = model
        self._prompt_loader = prompt_loader
        self._booking_tool = booking_tool
        self._email_tool = email_tool

    def build(self) -> LlmAgent:
        """Create an unparented welcome agent."""
        prompt = self._prompt_loader.load("welcome_agent")
        return LlmAgent(
            name=prompt.id,
            model=self._model,
            description=prompt.description,
            instruction=prompt.instruction,
            tools=[self._booking_tool, self._email_tool],
            output_key="onboarding_response",
        )
