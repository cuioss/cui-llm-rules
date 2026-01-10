#!/usr/bin/env python3
"""Extension API for pm-dev-java-cui bundle.

Provides CUI-specific Java patterns for logging, testing, and HTTP.

This is an ADDITIVE bundle - it extends pm-dev-java rather than standing alone.
It intentionally does NOT provide triage; it relies on pm-dev-java:java-triage.
"""

import sys
from pathlib import Path

from extension_base import ExtensionBase

# Add pm-dev-java scripts to path for Maven constants
_PM_DEV_JAVA_SCRIPTS = (
    Path(__file__).parent.parent.parent.parent
    / "pm-dev-java"
    / "skills"
    / "plan-marshall-plugin"
    / "scripts"
)
if str(_PM_DEV_JAVA_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_PM_DEV_JAVA_SCRIPTS))


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

    def config_defaults(self, project_root: str) -> None:
        """Configure CUI-specific Maven defaults.

        Sets project-specific configuration for CUI Open Source projects:
        - Profile mappings for standard CUI profiles (pre-commit, coverage, javadoc)
        - Skip list for internal/infrastructure profiles

        Uses write-once semantics - only sets values if not already configured.

        See: pm-dev-java:plan-marshall-plugin:standards/maven-impl.md
        """
        from run_config import ext_defaults_set_default
        from _maven_cmd_discover import EXT_KEY_PROFILES_SKIP, EXT_KEY_PROFILES_MAP

        # CUI standard profile mappings
        # pre-commit → quality-gate, coverage → coverage, javadoc → javadoc
        ext_defaults_set_default(
            EXT_KEY_PROFILES_MAP,
            "pre-commit:quality-gate,coverage:coverage,javadoc:javadoc",
            project_root
        )

        # Skip internal profiles that shouldn't generate commands
        ext_defaults_set_default(
            EXT_KEY_PROFILES_SKIP,
            "build-plantuml,rewrite-maven-clean, release, release-snapshot, license-cleanup, sonar, only-eclipse,release-pom",
            project_root
        )
