#!/usr/bin/env python3
"""Extension API for pm-dev-frontend bundle.

Provides build system detection, module discovery, and command mappings
for npm/JavaScript projects.
"""

import json
from pathlib import Path

from extension_base import (
    ExtensionBase,
    CMD_COMPILE,
    CMD_TEST_COMPILE,
    CMD_MODULE_TESTS,
    CMD_QUALITY_GATE,
    CMD_VERIFY,
    CMD_INSTALL,
    CMD_PACKAGE,
)


# Build file constant
PACKAGE_JSON = "package.json"


class Extension(ExtensionBase):
    """npm/JavaScript extension for pm-dev-frontend bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if JavaScript bundle applies to the project."""
        root = Path(project_root)
        return (root / PACKAGE_JSON).exists()

    def provides_build_systems(self) -> list:
        """Build system keys this bundle handles."""
        return ["npm"]

    def get_applicable_build_systems(self, project_root: str) -> list:
        """Return build systems actually present in the project."""
        root = Path(project_root)
        if (root / PACKAGE_JSON).exists():
            return ["npm"]
        return []

    def get_command_mappings(self) -> dict:
        """Return canonical -> script invocation template."""
        # Use inherited build_command_template helper for consistency
        def npm(targets: str) -> str:
            return self.build_command_template("pm-dev-frontend", "npm", targets)

        # Common target patterns
        run_build = "run build"

        return {
            "npm": {
                CMD_COMPILE: npm(run_build),
                CMD_TEST_COMPILE: npm(run_build),
                CMD_MODULE_TESTS: npm("run test"),
                "lint": npm("run lint"),
                "lint-fix": npm("run lint:fix"),
                CMD_QUALITY_GATE: npm("run lint && npm run test"),
                CMD_VERIFY: npm(f"{run_build} && npm run test"),
                CMD_INSTALL: npm("install"),
                CMD_PACKAGE: npm(run_build),
                "e2e-tests": npm("playwright test"),
            }
        }

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
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

    def provides_triage(self) -> str | None:
        """Return triage skill reference."""
        return "pm-dev-frontend:javascript-triage"

    def get_modules(self, project_root: str) -> list:
        """Return project modules detected from npm workspaces."""
        root = Path(project_root)
        workspaces = self._load_workspaces(root)

        if not workspaces:
            return []

        modules = []
        for workspace in workspaces:
            modules.extend(self._resolve_workspace(root, workspace))

        return modules

    def get_module_type(self, module_path: str) -> str:
        """Return the module type for a given module path."""
        return "npm"

    def get_profiles(self, module_path: str) -> list:
        """Return npm script-based profiles for a module.

        npm doesn't have Maven-style profiles, but npm scripts can serve
        a similar purpose (e.g., test:e2e, test:coverage).
        """
        path = Path(module_path)
        package_json_path = path / PACKAGE_JSON

        if not package_json_path.exists():
            return []

        try:
            with open(package_json_path) as f:
                package_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

        scripts = package_data.get("scripts", {})
        profiles = []

        for script_name in scripts:
            canonical = self.classify_profile(script_name)
            if canonical:
                profiles.append({
                    "id": script_name,
                    "canonical": canonical,
                    "activation": {"type": "script"}
                })

        return profiles

    def generate_profile_command(
        self,
        build_system: str,
        _canonical: str,
        profile_id: str,
        _activation: dict,
        module_name: str = None
    ) -> str | None:
        """Generate a command string for a profile-based canonical command.

        For npm, profiles are npm scripts, so we run them directly.
        """
        if build_system != "npm":
            return None

        # npm scripts are invoked directly
        cmd = f'python3 .plan/execute-script.py pm-dev-frontend:plan-marshall-plugin:npm run --targets "run {profile_id}"'

        if module_name and module_name != "default":
            cmd += f" --module {module_name}"

        return cmd

    # =========================================================================
    # npm Workspace Helpers
    # =========================================================================

    def _load_workspaces(self, root: Path) -> list:
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

    def _resolve_workspace(self, root: Path, workspace: str) -> list:
        """Resolve a single workspace pattern to modules."""
        # Handle glob patterns like "packages/*"
        if "*" in workspace:
            return self._resolve_glob_workspace(root, workspace)

        # Direct path
        workspace_path = root / workspace
        if workspace_path.exists() and (workspace_path / PACKAGE_JSON).exists():
            return [{
                "name": workspace_path.name,
                "path": workspace,
                "build_system": "npm"
            }]

        return []

    def _resolve_glob_workspace(self, root: Path, workspace: str) -> list:
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
