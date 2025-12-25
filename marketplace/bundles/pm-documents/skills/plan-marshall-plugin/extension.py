#!/usr/bin/env python3
"""Extension API for pm-documents bundle.

Provides skill-only domain detection for documentation projects.
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if documentation bundle applies to the project.

    Returns True if doc/ directory exists (AsciiDoc documentation).
    """
    root = Path(project_root)
    return (root / "doc").is_dir()


def provides_build_systems() -> list:
    """Build system keys this bundle handles.

    Documentation has no build systems.
    """
    return []


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Documentation has no build commands.
    """
    return {}


def get_skill_domains() -> dict:
    """Domain metadata for skill loading.

    Returns profile-based skill organization for documentation.
    """
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
