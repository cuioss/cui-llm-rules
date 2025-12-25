#!/usr/bin/env python3
"""Extension API for pm-requirements bundle.

Provides skill-only domain detection for requirements engineering projects.
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if requirements bundle applies to the project.

    Returns True if Requirements.adoc exists in doc/spec/ or root.
    """
    root = Path(project_root)
    return (
        (root / "doc" / "spec" / "Requirements.adoc").exists() or
        (root / "Requirements.adoc").exists()
    )


def provides_build_systems() -> list:
    """Build system keys this bundle handles.

    Requirements has no build systems.
    """
    return []


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Requirements has no build commands.
    """
    return {}


def get_skill_domains() -> dict:
    """Domain metadata for skill loading.

    Returns profile-based skill organization for requirements engineering.
    """
    return {
        "domain": {
            "key": "requirements",
            "name": "Requirements Engineering",
            "description": "User stories, acceptance criteria, specifications"
        },
        "profiles": {
            "core": {
                "defaults": ["pm-requirements:cui-requirements"],
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
