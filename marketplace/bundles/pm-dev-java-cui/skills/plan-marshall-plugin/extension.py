#!/usr/bin/env python3
"""Extension API for pm-dev-java-cui bundle.

Provides CUI-specific Java patterns for logging, testing, and HTTP.
"""

from pathlib import Path

from extension_base import ExtensionBase


class Extension(ExtensionBase):
    """CUI Java extension for pm-dev-java-cui bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if CUI Java bundle applies to the project."""
        root = Path(project_root)
        pom_file = root / "pom.xml"
        if not pom_file.exists():
            return False
        try:
            content = pom_file.read_text()
            return "cui-" in content or "de.cuioss" in content
        except OSError:
            return False

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
        return {
            "domain": {
                "key": "java-cui",
                "name": "CUI Java Development",
                "description": "CUI-specific Java patterns for logging, testing, and HTTP"
            },
            "profiles": {
                "core": {
                    "defaults": ["pm-dev-java-cui:cui-logging"],
                    "optionals": []
                },
                "implementation": {
                    "defaults": [],
                    "optionals": ["pm-dev-java-cui:cui-http"]
                },
                "testing": {
                    "defaults": [],
                    "optionals": ["pm-dev-java-cui:cui-testing", "pm-dev-java-cui:cui-testing-http"]
                },
                "quality": {
                    "defaults": [],
                    "optionals": []
                }
            }
        }
