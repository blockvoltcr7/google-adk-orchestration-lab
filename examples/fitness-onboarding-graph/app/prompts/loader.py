"""Validated loader for package-relative YAML prompt resources."""

import re
from importlib import resources
from typing import Protocol

import yaml
from pydantic import ValidationError

from app.models import PromptDefinition


class PromptLoader(Protocol):
    """Contract used by agent builders to retrieve prompt definitions."""

    def load(self, prompt_id: str) -> PromptDefinition:
        """Load one validated prompt definition."""
        ...


class YamlPromptLoader:
    """Load and cache validated prompts from the ``app.prompts`` package."""

    def __init__(self, package: str = "app.prompts") -> None:
        self._package = package
        self._cache: dict[str, PromptDefinition] = {}

    def load(self, prompt_id: str) -> PromptDefinition:
        """Load one YAML prompt without formatting ADK placeholders."""
        if re.fullmatch(r"[a-z][a-z0-9_]*", prompt_id) is None:
            raise ValueError(f"Invalid prompt id: {prompt_id!r}")
        if prompt_id in self._cache:
            return self._cache[prompt_id]

        resource = resources.files(self._package).joinpath(f"{prompt_id}.yaml")
        try:
            raw_prompt = resource.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise ValueError(f"Prompt resource not found: {prompt_id}") from error

        try:
            payload = yaml.safe_load(raw_prompt)
        except yaml.YAMLError as error:
            raise ValueError(f"Prompt YAML is invalid: {prompt_id}") from error
        if not isinstance(payload, dict):
            raise ValueError(f"Prompt resource must contain a mapping: {prompt_id}")

        try:
            prompt = PromptDefinition.model_validate(payload)
        except ValidationError as error:
            raise ValueError(f"Prompt definition is invalid: {prompt_id}") from error
        if prompt.id != prompt_id:
            raise ValueError(
                f"Prompt id mismatch: requested {prompt_id!r}, found {prompt.id!r}"
            )
        self._cache[prompt_id] = prompt
        return prompt
