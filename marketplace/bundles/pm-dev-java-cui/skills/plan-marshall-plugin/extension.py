#!/usr/bin/env python3
"""Extension API for pm-dev-java-cui bundle.

Provides CUI-specific Java patterns for logging, testing, and HTTP.
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if CUI Java bundle applies to the project.

    Returns True if pom.xml exists and contains cui- dependencies.
    """
    root = Path(project_root)
    pom_file = root / "pom.xml"
    if not pom_file.exists():
        return False
    try:
        content = pom_file.read_text()
        return "cui-" in content or "de.cuioss" in content
    except OSError:
        return False


def provides_build_systems() -> list:
    """Build system keys this bundle handles.

    CUI Java does not provide build systems (uses pm-dev-java).
    """
    return []


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    CUI Java does not provide build commands (uses pm-dev-java).
    """
    return {}


def get_skill_domains() -> dict:
    """Domain metadata for skill loading.

    Returns profile-based skill organization for CUI Java development.
    """
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


def provides_triage() -> str | None:
    """Return triage skill reference if available.

    Returns:
        Skill reference like 'bundle:skill' or None if not provided.
    """
    return None


def provides_outline() -> str | None:
    """Return outline skill reference if available.

    Returns:
        Skill reference like 'bundle:skill' or None if not provided.
    """
    return None
