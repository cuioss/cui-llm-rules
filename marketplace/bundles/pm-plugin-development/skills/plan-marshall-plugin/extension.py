#!/usr/bin/env python3
"""Extension API for pm-plugin-development bundle.

Provides skill-only domain detection for plugin development projects.
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if plugin development bundle applies to the project.

    Returns True if marketplace/bundles/ directory exists.
    """
    root = Path(project_root)
    return (root / "marketplace" / "bundles").is_dir()


def provides_build_systems() -> list:
    """Build system keys this bundle handles.

    Plugin development has no build systems.
    """
    return []


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Plugin development has no build commands.
    """
    return {}


def get_skill_domains() -> dict:
    """Domain metadata for skill loading.

    Returns profile-based skill organization for plugin development.
    """
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


def provides_triage() -> str | None:
    """Return triage skill reference if available.

    Returns:
        Skill reference like 'bundle:skill' or None if not provided.
    """
    return "pm-plugin-development:plugin-triage"


def provides_outline() -> str | None:
    """Return outline skill reference if available.

    Returns:
        Skill reference like 'bundle:skill' or None if not provided.
    """
    return None
