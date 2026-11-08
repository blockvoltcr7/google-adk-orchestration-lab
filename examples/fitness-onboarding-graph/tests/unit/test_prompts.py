"""Tests for versioned YAML prompt resources."""

import pytest

from app.prompts import YamlPromptLoader


def test_yaml_prompts_load_and_cache_without_state_placeholders() -> None:
    loader = YamlPromptLoader()

    consultation = loader.load("consultation_agent")
    welcome = loader.load("welcome_agent")

    assert consultation.version == "1.0.0"
    assert welcome.version == "1.0.0"
    assert consultation.required_state_keys == ()
    assert welcome.required_state_keys == ()
    assert loader.load("consultation_agent") is consultation


def test_prompt_loader_rejects_unsafe_or_missing_ids() -> None:
    loader = YamlPromptLoader()

    with pytest.raises(ValueError, match="Invalid prompt id"):
        loader.load("../secret")
    with pytest.raises(ValueError, match="not found"):
        loader.load("missing_prompt")
