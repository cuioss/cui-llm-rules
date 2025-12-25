#!/usr/bin/env python3
"""Extension API for pm-dev-frontend bundle.

Provides build system detection and command mappings for npm/JavaScript projects.
"""

from pathlib import Path


def is_applicable(project_root: str) -> bool:
    """Check if JavaScript bundle applies to the project.

    Returns True if package.json exists.
    """
    root = Path(project_root)
    return (root / "package.json").exists()


def provides_build_systems() -> list:
    """Build system keys this bundle handles."""
    return ["npm"]


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Placeholders:
        {module} - replaced by persist with ' --workspace <name>' or ''
                   (using {module} for consistency with Java, resolved to --workspace for npm)
    """
    base_npm = "python3 .plan/execute-script.py pm-dev-frontend:build-operations:npm run"

    return {
        "npm": {
            "compile": f'{base_npm} --targets "run build"{{module}}',
            "test-compile": f'{base_npm} --targets "run build"{{module}}',
            "module-tests": f'{base_npm} --targets "run test"{{module}}',
            "lint": f'{base_npm} --targets "run lint"{{module}}',
            "lint-fix": f'{base_npm} --targets "run lint:fix"{{module}}',
            "quality-gate": f'{base_npm} --targets "run lint && npm run test"{{module}}',
            "verify": f'{base_npm} --targets "run build && npm run test"{{module}}',
            "install": f'{base_npm} --targets "install"{{module}}',
            "package": f'{base_npm} --targets "run build"{{module}}',
            "e2e-tests": f'{base_npm} --targets "playwright test"{{module}}',
        }
    }


def get_skill_domains() -> dict:
    """Domain metadata for skill loading.

    Returns profile-based skill organization for JavaScript development.
    """
    return {
        "domain": {
            "key": "javascript",
            "name": "JavaScript Development",
            "description": "Modern JavaScript, ESLint, Jest testing, npm builds"
        },
        "profiles": {
            "core": {
                "defaults": ["pm-dev-frontend:cui-javascript"],
                "optionals": ["pm-dev-frontend:cui-jsdoc", "pm-dev-frontend:cui-javascript-project"]
            },
            "implementation": {
                "defaults": [],
                "optionals": ["pm-dev-frontend:cui-javascript-linting", "pm-dev-frontend:cui-javascript-maintenance"]
            },
            "testing": {
                "defaults": ["pm-dev-frontend:cui-javascript-unit-testing"],
                "optionals": ["pm-dev-frontend:cui-cypress"]
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
    return "pm-dev-frontend:javascript-triage"


def provides_outline() -> str | None:
    """Return outline skill reference if available.

    Returns:
        Skill reference like 'bundle:skill' or None if not provided.
    """
    return None
