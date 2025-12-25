#!/usr/bin/env python3
"""Extension API for pm-dev-java-cui bundle.

Provides supplementary skills for the Java domain (CUI-specific patterns).
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if CUI Java supplement applies to the project.

    Returns True if pom.xml exists and contains cui- dependencies.
    This is a heuristic - actual activation depends on domain configuration.
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

    Supplements do not provide build systems.
    """
    return []


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Supplements do not provide build commands.
    """
    return {}


def get_domain_supplements() -> dict:
    """Domain supplement metadata for skill loading.

    Returns supplementary skills to merge into a parent domain's profiles.
    """
    return {
        "domain": "java",
        "description": "CUI-specific Java patterns for logging, testing, and HTTP",
        "profiles": {
            "core": {
                "defaults": [],
                "optionals": ["pm-dev-java-cui:cui-logging"]
            },
            "implementation": {
                "defaults": [],
                "optionals": ["pm-dev-java-cui:cui-http"]
            },
            "testing": {
                "defaults": [],
                "optionals": ["pm-dev-java-cui:cui-testing", "pm-dev-java-cui:cui-testing-http"]
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
