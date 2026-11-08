"""Validated prompt-resource model."""

from string import Formatter

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PromptDefinition(BaseModel):
    """An immutable, versioned YAML prompt definition."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    version: str = Field(min_length=1)
    description: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    required_state_keys: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_state_placeholders(self) -> "PromptDefinition":
        """Require YAML metadata to document every ADK state placeholder."""
        referenced_keys = {
            field_name
            for _, field_name, _, _ in Formatter().parse(self.instruction)
            if field_name
        }
        declared_keys = set(self.required_state_keys)
        if referenced_keys != declared_keys:
            missing = sorted(referenced_keys - declared_keys)
            unused = sorted(declared_keys - referenced_keys)
            details = []
            if missing:
                details.append(f"undeclared placeholders: {missing}")
            if unused:
                details.append(f"unused required_state_keys: {unused}")
            raise ValueError("; ".join(details))
        return self
