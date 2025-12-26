#!/usr/bin/env python3
"""Extension API for pm-plugin-development bundle.

Provides skill-only domain detection for plugin development projects.
"""

from pathlib import Path

from extension_base import ExtensionBase


class Extension(ExtensionBase):
    """Plugin development extension for pm-plugin-development bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if plugin development bundle applies to the project."""
        root = Path(project_root)
        return (root / "marketplace" / "bundles").is_dir()

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
        return {
            "domain": {
                "key": "plan-marshall-plugin-dev",
                "name": "Plugin Development",
                "description": "Claude Code marketplace component development"
            },
            "profiles": {
                "core": {
                    "defaults": ["pm-plugin-development:plugin-architecture"],
                    "optionals": ["pm-plugin-development:plugin-script-architecture"]
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

    def provides_triage(self) -> str | None:
        """Return triage skill reference."""
        return "pm-plugin-development:plugin-triage"
