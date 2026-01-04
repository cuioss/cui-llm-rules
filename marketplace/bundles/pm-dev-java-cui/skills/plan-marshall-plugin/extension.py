#!/usr/bin/env python3
"""Extension API for pm-dev-java-cui bundle.

Provides CUI-specific Java patterns for logging, testing, and HTTP.

This is an ADDITIVE bundle - it extends pm-dev-java rather than standing alone.
It intentionally does NOT provide triage; it relies on pm-dev-java:java-triage.
"""

from extension_base import ExtensionBase


class Extension(ExtensionBase):
    """CUI Java extension for pm-dev-java-cui bundle."""

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
