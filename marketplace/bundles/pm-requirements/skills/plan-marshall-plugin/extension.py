#!/usr/bin/env python3
"""Extension API for pm-requirements bundle.

Provides skill-only domain detection for requirements engineering projects.
"""

from pathlib import Path

from extension_base import ExtensionBase


class Extension(ExtensionBase):
    """Requirements extension for pm-requirements bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if requirements bundle applies to the project."""
        root = Path(project_root)
        return (
            (root / "doc" / "spec" / "Requirements.adoc").exists() or
            (root / "Requirements.adoc").exists()
        )

    def provides_triage(self) -> str | None:
        """Return triage skill reference."""
        return "pm-requirements:requirements-triage"

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
        return {
            "domain": {
                "key": "requirements",
                "name": "Requirements Engineering",
                "description": "User stories, acceptance criteria, specifications"
            },
            "profiles": {
                "core": {
                    "defaults": ["pm-requirements:requirements-authoring"],
                    "optionals": []
                },
                "implementation": {
                    "defaults": [],
                    "optionals": []
                },
                "testing": {
                    "defaults": [],
                    "optionals": []
                },
                "quality": {
                    "defaults": [],
                    "optionals": []
                }
            }
        }
