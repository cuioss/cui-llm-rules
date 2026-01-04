#!/usr/bin/env python3
"""Extension API for pm-dev-frontend bundle.

Provides build system detection, module discovery for npm/JavaScript projects.

Implementation logic resides in scripts/ directory.
"""

import json
from pathlib import Path

from extension_base import ExtensionBase


# Build file constant
PACKAGE_JSON = "package.json"


class Extension(ExtensionBase):
    """npm/JavaScript extension for pm-dev-frontend bundle."""

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

    # =========================================================================
    # discover_modules() Implementation
    # =========================================================================

    def discover_modules(self, project_root: str) -> list:
        """Discover all npm modules with complete metadata.

        Implements the unified discover_modules() API for npm projects.
        Returns comprehensive module information including metadata, dependencies,
        and stats.

        Also discovers npm modules in first-level subdirectories (hybrid modules
        in multi-module projects like Maven+npm).
        """
        modules = []
        root = Path(project_root)

        # Check for package.json at root
        package_json_path = root / PACKAGE_JSON
        if package_json_path.exists():
            # Load root package.json
            try:
                with open(package_json_path) as f:
                    root_pkg = json.load(f)

                # Check for workspaces (monorepo)
                workspaces = root_pkg.get("workspaces", [])
                if isinstance(workspaces, dict):
                    workspaces = workspaces.get("packages", [])

                if workspaces:
                    # Monorepo with workspaces - discover each workspace module
                    for workspace_pattern in workspaces:
                        modules.extend(self._discover_workspace_modules(root, workspace_pattern))
                else:
                    # Single-module project - discover the root
                    module_data = self._extract_npm_module_data(root, root, "")
                    if module_data:
                        modules.append(module_data)
            except (json.JSONDecodeError, OSError):
                pass

        # Also check first-level subdirectories for npm modules (hybrid projects)
        for subdir in root.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                if (subdir / PACKAGE_JSON).exists():
                    relative_path = subdir.name
                    # Skip if already discovered (via workspaces)
                    if not any(m.get('path') == relative_path for m in modules):
                        module_data = self._extract_npm_module_data(subdir, root, relative_path)
                        if module_data:
                            modules.append(module_data)

        return modules

    def _discover_workspace_modules(self, root: Path, workspace_pattern: str) -> list:
        """Discover modules matching a workspace pattern."""
        modules = []

        if "*" in workspace_pattern:
            # Glob pattern like "packages/*"
            base_path = root / workspace_pattern.replace("/*", "").replace("/**", "")
            if base_path.exists() and base_path.is_dir():
                for subdir in base_path.iterdir():
                    if subdir.is_dir() and (subdir / PACKAGE_JSON).exists():
                        relative_path = str(subdir.relative_to(root))
                        module_data = self._extract_npm_module_data(subdir, root, relative_path)
                        if module_data:
                            modules.append(module_data)
        else:
            # Direct path
            workspace_path = root / workspace_pattern
            if workspace_path.exists() and (workspace_path / PACKAGE_JSON).exists():
                module_data = self._extract_npm_module_data(workspace_path, root, workspace_pattern)
                if module_data:
                    modules.append(module_data)

        return modules

    def _extract_npm_module_data(self, module_path: Path, project_root: Path, relative_path: str) -> dict | None:
        """Extract complete module data from an npm module."""
        package_json_path = module_path / PACKAGE_JSON
        if not package_json_path.exists():
            return None

        try:
            with open(package_json_path) as f:
                pkg = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        # Extract metadata from package.json
        name = pkg.get("name", module_path.name)
        description = pkg.get("description")
        version = pkg.get("version")
        pkg_type = pkg.get("type", "commonjs")  # "module" for ESM, "commonjs" for CJS
        main = pkg.get("main")
        exports = pkg.get("exports")

        # Check for hybrid (Maven+npm)
        build_systems = ["npm"]
        pom_xml = module_path / "pom.xml"
        if pom_xml.exists():
            build_systems.insert(0, "maven")

        # Build descriptors
        descriptors = {
            "pom": str(Path(relative_path) / "pom.xml") if pom_xml.exists() else None,
            "gradle": None,
            "package": str(Path(relative_path) / PACKAGE_JSON) if relative_path else PACKAGE_JSON
        }

        # Discover source directories
        sources = self._discover_npm_sources(module_path, pkg)

        # Extract dependencies
        dependencies = self._extract_npm_dependencies(pkg)

        # Calculate stats
        source_files = self._count_js_files(module_path, sources["main"])
        test_files = self._count_js_files(module_path, sources["test"])
        has_readme = self._check_readme(module_path)

        return {
            "name": name,
            "path": relative_path if relative_path else ".",
            "build_systems": build_systems,
            "descriptors": descriptors,
            "metadata": {
                "description": description,
                "version": version,
                "type": pkg_type,
                "main": main,
                "exports": exports is not None,
                "scripts": list(pkg.get("scripts", {}).keys()),
                "modules": []  # npm doesn't have child modules in the same way
            },
            "sources": sources,
            "packages": [],  # npm doesn't have Java-style packages
            "dependencies": dependencies,
            "stats": {
                "source_files": source_files,
                "test_files": test_files,
                "has_readme": has_readme
            }
        }

    def _discover_npm_sources(self, module_path: Path, pkg: dict) -> dict:
        """Discover source directories for an npm module."""
        sources = {
            "main": [],
            "test": [],
            "resources": []
        }

        # Common source directories
        common_src_dirs = ["src", "lib", "source"]
        for src_dir in common_src_dirs:
            if (module_path / src_dir).exists():
                sources["main"].append(src_dir)
                break

        # Common test directories
        common_test_dirs = ["test", "tests", "__tests__", "spec"]
        for test_dir in common_test_dirs:
            if (module_path / test_dir).exists():
                sources["test"].append(test_dir)

        # Check Jest configuration for custom test locations
        jest_config = pkg.get("jest", {})
        if isinstance(jest_config, dict):
            test_match = jest_config.get("testMatch", [])
            if test_match and not sources["test"]:
                # Extract directory from first pattern
                for pattern in test_match:
                    if "__tests__" in pattern:
                        sources["test"].append("__tests__")
                        break

        # Resources (public, static)
        resource_dirs = ["public", "static", "assets"]
        for res_dir in resource_dirs:
            if (module_path / res_dir).exists():
                sources["resources"].append(res_dir)

        return sources

    def _extract_npm_dependencies(self, pkg: dict) -> list:
        """Extract dependencies from package.json."""
        dependencies = []

        # Production dependencies
        for name, version in pkg.get("dependencies", {}).items():
            dependencies.append({
                "name": name,
                "version": version,
                "scope": "compile"
            })

        # Dev dependencies
        for name, version in pkg.get("devDependencies", {}).items():
            dependencies.append({
                "name": name,
                "version": version,
                "scope": "test"
            })

        # Peer dependencies
        for name, version in pkg.get("peerDependencies", {}).items():
            dependencies.append({
                "name": name,
                "version": version,
                "scope": "provided"
            })

        return dependencies

    def _count_js_files(self, module_path: Path, directories: list) -> int:
        """Count JavaScript/TypeScript files in directories."""
        count = 0
        js_extensions = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}

        for dir_name in directories:
            dir_path = module_path / dir_name
            if dir_path.exists():
                for file in dir_path.rglob("*"):
                    if file.is_file() and file.suffix in js_extensions:
                        count += 1

        return count

    def _check_readme(self, module_path: Path) -> bool:
        """Check if module has a README file."""
        readme_names = ["README.md", "README", "readme.md", "Readme.md"]
        return any((module_path / name).exists() for name in readme_names)
