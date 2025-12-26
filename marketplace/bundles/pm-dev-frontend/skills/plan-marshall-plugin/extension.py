#!/usr/bin/env python3
"""Extension API for pm-dev-frontend bundle.

Provides build system detection, module discovery, and command mappings
for npm/JavaScript projects.
"""

import json
from pathlib import Path


# Build file constant
PACKAGE_JSON = "package.json"


def is_applicable(project_root: str) -> bool:
    """Check if JavaScript bundle applies to the project.

    Returns True if package.json exists.
    """
    root = Path(project_root)
    return (root / PACKAGE_JSON).exists()


def provides_build_systems() -> list:
    """Build system keys this bundle handles (static declaration)."""
    return ["npm"]


def get_applicable_build_systems(project_root: str) -> list:
    """Return build systems that are actually present in the project.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of build system keys present (e.g., ["npm"])
    """
    root = Path(project_root)
    if (root / PACKAGE_JSON).exists():
        return ["npm"]
    return []


def get_command_mappings() -> dict:
    """Return canonical -> script invocation template.

    Placeholders:
        {module} - replaced by persist with ' --workspace <name>' or ''
                   (using {module} for consistency with Java, resolved to --workspace for npm)
    """
    base_npm = "python3 .plan/execute-script.py pm-dev-frontend:plan-marshall-plugin:npm run"

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


# =============================================================================
# Build System Extensions
# =============================================================================

def get_modules(project_root: str) -> list:
    """Return project modules detected from npm workspaces.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of module dicts: {name, path, build_system}
    """
    root = Path(project_root)
    workspaces = _load_workspaces(root)

    if not workspaces:
        return []

    modules = []
    for workspace in workspaces:
        modules.extend(_resolve_workspace(root, workspace))

    return modules


def _load_workspaces(root: Path) -> list:
    """Load workspaces from package.json."""
    package_json_path = root / PACKAGE_JSON

    if not package_json_path.exists():
        return []

    try:
        with open(package_json_path) as f:
            package_data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    workspaces = package_data.get("workspaces", [])

    # Handle object format with packages key
    if isinstance(workspaces, dict):
        return workspaces.get("packages", [])

    return workspaces


def _resolve_workspace(root: Path, workspace: str) -> list:
    """Resolve a single workspace pattern to modules."""
    # Handle glob patterns like "packages/*"
    if "*" in workspace:
        return _resolve_glob_workspace(root, workspace)

    # Direct path
    workspace_path = root / workspace
    if workspace_path.exists() and (workspace_path / PACKAGE_JSON).exists():
        return [{
            "name": workspace_path.name,
            "path": workspace,
            "build_system": "npm"
        }]

    return []


def _resolve_glob_workspace(root: Path, workspace: str) -> list:
    """Resolve a glob pattern workspace to modules."""
    base_path = root / workspace.replace("/*", "").replace("/**", "")
    modules = []

    if not base_path.exists() or not base_path.is_dir():
        return modules

    for subdir in base_path.iterdir():
        if subdir.is_dir() and (subdir / PACKAGE_JSON).exists():
            modules.append({
                "name": subdir.name,
                "path": str(subdir.relative_to(root)),
                "build_system": "npm"
            })

    return modules


def get_module_type(_module_path: str) -> str:
    """Return the module type for a given module path.

    Args:
        module_path: Absolute path to module directory.

    Returns:
        Always returns "npm" for JavaScript modules.
    """
    return "npm"


def get_profiles(_module_path: str) -> list:
    """Return build profiles for a module.

    Args:
        _module_path: Absolute path to module directory.

    Returns:
        Empty list - npm doesn't have Maven-style profiles.
    """
    # npm doesn't have profiles like Maven
    # Build variants are typically handled via npm scripts or environment variables
    return []
