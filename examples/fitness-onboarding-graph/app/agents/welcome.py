"""Builder for the welcome-email drafting graph node."""

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm

from app.models import BookingPackage, WelcomeEmailDraft
from app.prompts import PromptLoader


class WelcomeAgentBuilder:
    """Build fresh, typed welcome-agent nodes."""

    def __init__(
        self,
        model: str | BaseLlm,
        prompt_loader: PromptLoader,
    ) -> None:
        self._model = model
        self._prompt_loader = prompt_loader

    def build(self) -> LlmAgent:
        """Create an unparented welcome agent for graph composition."""
        prompt = self._prompt_loader.load("welcome_agent")
        return LlmAgent(
            name=prompt.id,
            model=self._model,
            description=prompt.description,
            instruction=prompt.instruction,
            input_schema=BookingPackage,
            output_schema=WelcomeEmailDraft,
            output_key="welcome_email_draft",
        )
