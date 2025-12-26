#!/usr/bin/env python3
"""Extension API for pm-documents bundle.

Provides skill-only domain detection for documentation projects.
"""

from pathlib import Path

from extension_base import ExtensionBase


class Extension(ExtensionBase):
    """Documentation extension for pm-documents bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if documentation bundle applies to the project."""
        root = Path(project_root)
        return (root / "doc").is_dir()

    def provides_triage(self) -> str | None:
        """Return triage skill reference."""
        return "pm-documents:documentation-triage"

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
        return {
            "domain": {
                "key": "documentation",
                "name": "Documentation",
                "description": "AsciiDoc documentation, ADRs, and interface specifications"
            },
            "profiles": {
                "core": {
                    "defaults": ["pm-documents:cui-documentation"],
                    "optionals": []
                },
                "implementation": {
                    "defaults": [],
                    "optionals": ["pm-documents:adr-management", "pm-documents:interface-management"]
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
