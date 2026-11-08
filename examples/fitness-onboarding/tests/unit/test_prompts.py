"""Unit tests for YAML prompt resources."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models import PromptDefinition
from app.prompts import YamlPromptLoader
from app.prompts import loader as loader_module


def test_loader_loads_and_caches_all_agent_prompts() -> None:
    loader = YamlPromptLoader()

    intake = loader.load("intake_agent")
    consultation = loader.load("consultation_agent")
    welcome = loader.load("welcome_agent")

    assert intake.id == "intake_agent"
    assert "{client_profile}" in consultation.instruction
    assert "{consultation_plan}" in welcome.instruction
    assert loader.load("welcome_agent") is welcome


def test_prompt_definition_rejects_undocumented_placeholders() -> None:
    with pytest.raises(ValidationError, match="undeclared placeholders"):
        PromptDefinition.model_validate(
            {
                "id": "example_agent",
                "version": "1.0.0",
                "description": "Example",
                "instruction": "Use {missing_state}.",
                "required_state_keys": [],
            }
        )


def test_loader_rejects_invalid_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompt_file = tmp_path / "broken.yaml"
    prompt_file.write_text("instruction: [", encoding="utf-8")
    monkeypatch.setattr(loader_module.resources, "files", lambda package: tmp_path)

    with pytest.raises(ValueError, match="Prompt YAML is invalid"):
        YamlPromptLoader(package="test.prompts").load("broken")


def test_loader_rejects_missing_prompt() -> None:
    with pytest.raises(ValueError, match="Prompt resource not found"):
        YamlPromptLoader().load("missing_agent")
