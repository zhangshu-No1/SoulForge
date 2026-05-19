"""Prompt Template System for SoulForge.

Allows users to define custom system prompt templates
with variable substitution.
"""

from pathlib import Path
from typing import Optional, Dict
import json


class PromptTemplate:
    """A prompt template with support for variable substitution."""

    def __init__(self, name: str, template: str, description: str = ""):
        self.name = name
        self.template = template
        self.description = description

    def render(self, context: Dict[str, str]) -> str:
        """Render the template with the given context variables."""
        try:
            return self.template.format(**context)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PromptTemplate":
        return cls(
            name=data["name"],
            template=data["template"],
            description=data.get("description", ""),
        )


class PromptTemplateManager:
    """Manages loading, saving, and rendering prompt templates."""

    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
        self._load_custom_templates()

    def _load_default_templates(self):
        """Load built-in default templates."""
        self.templates["default"] = PromptTemplate(
            name="default",
            template=(
                "You are {name}, {personality}.\n"
                "\n{memory_context}\n"
                "\n{goal_reminder}\n"
                "\nRelationship stage: {relationship_stage}\n"
                "Intimacy: {intimacy}/{max_intimacy}"
            ),
            description="Default system prompt template with full context",
        )

        self.templates["minimal"] = PromptTemplate(
            name="minimal",
            template=(
                "You are {name}. {personality}.\n"
                "\n{memory_context}\n"
                "\n{goal_reminder}"
            ),
            description="Minimal prompt template without relationship details",
        )

        self.templates["companion"] = PromptTemplate(
            name="companion",
            template=(
                "You are {name}, a warm and caring companion. {personality}.\n"
                "\nYour role is to be there for the user, remember your shared "
                "experiences, and grow your relationship over time.\n"
                "\n{memory_context}\n"
                "\n{goal_reminder}"
            ),
            description="Companion-style prompt for emotional bonding",
        )

    def _load_custom_templates(self):
        """Load custom templates from the templates directory."""
        if not self.templates_dir.exists():
            return

        for file_path in self.templates_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                template = PromptTemplate.from_dict(data)
                self.templates[template.name] = template
            except Exception:
                continue

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self.templates.get(name)

    def list_templates(self) -> list[str]:
        """List all available template names."""
        return list(self.templates.keys())

    def save_template(self, template: PromptTemplate):
        """Save a custom template to disk."""
        self.templates[template.name] = template
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.templates_dir / f"{template.name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)

    def render_template(self, name: str, context: Dict[str, str]) -> str:
        """Render a template by name with the given context."""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        return template.render(context)
