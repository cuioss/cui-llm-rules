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
                    # Check both paths.module (new format) and path (legacy)
                    if not any(m.get('paths', {}).get('module') == relative_path or
                               m.get('path') == relative_path for m in modules):
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
        """Extract complete module data from an npm module.

        Returns structure per build-project-structure.md specification:
        - technology: "npm" (single string)
        - paths: {module, descriptor, sources, tests, readme}
        - metadata: {artifact_id, group_id, description, parent, profiles}
        - packages: {} (object keyed by package name)
        - dependencies: ["npm:name:scope", ...] (string format)
        - stats: {source_files, test_files}
        - commands: {} (canonical command mappings)
        """
        package_json_path = module_path / PACKAGE_JSON
        if not package_json_path.exists():
            return None

        try:
            with open(package_json_path) as f:
                pkg = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        # Extract name
        name = pkg.get("name", module_path.name)

        # Build paths object
        module_rel_path = relative_path if relative_path else "."
        descriptor_path = f"{relative_path}/{PACKAGE_JSON}" if relative_path else PACKAGE_JSON

        # Discover source and test directories
        source_dirs = self._discover_source_dirs(module_path, pkg)
        test_dirs = self._discover_test_dirs(module_path, pkg)

        # Check for README
        readme_path = self._find_readme(module_path, relative_path)

        paths = {
            "module": module_rel_path,
            "descriptor": descriptor_path,
            "sources": source_dirs,
            "tests": test_dirs,
            "readme": readme_path
        }

        # Build metadata (no packaging field for npm per spec line 115)
        metadata = {
            "artifact_id": None,
            "group_id": None,
            "description": pkg.get("description"),
            "parent": None,
            "profiles": []
        }

        # Discover packages (from exports or directories)
        packages = self._discover_npm_packages(module_path, pkg, relative_path)

        # Extract dependencies in string format: npm:{name}:{scope}
        dependencies = self._extract_npm_dependencies_strings(pkg)

        # Calculate stats
        source_files = self._count_js_files(module_path, source_dirs)
        test_files = self._count_js_files(module_path, test_dirs)

        # Build commands based on available scripts
        commands = self._build_npm_commands(module_rel_path, pkg.get("scripts", {}))

        return {
            "name": name,
            "technology": "npm",
            "paths": paths,
            "metadata": metadata,
            "packages": packages,
            "dependencies": dependencies,
            "stats": {
                "source_files": source_files,
                "test_files": test_files
            },
            "commands": commands
        }

    def _discover_source_dirs(self, module_path: Path, pkg: dict) -> list:
        """Discover source directories for an npm module.

        Returns list of source directory paths relative to module.
        """
        source_dirs = []
        common_src_dirs = ["src", "lib", "source"]
        for src_dir in common_src_dirs:
            if (module_path / src_dir).exists():
                source_dirs.append(src_dir)
                break
        return source_dirs

    def _discover_test_dirs(self, module_path: Path, pkg: dict) -> list:
        """Discover test directories for an npm module.

        Returns list of test directory paths relative to module.
        """
        test_dirs = []
        common_test_dirs = ["test", "tests", "__tests__", "spec"]
        for test_dir in common_test_dirs:
            if (module_path / test_dir).exists():
                test_dirs.append(test_dir)

        # Check Jest configuration for custom test locations
        jest_config = pkg.get("jest", {})
        if isinstance(jest_config, dict) and not test_dirs:
            test_match = jest_config.get("testMatch", [])
            for pattern in test_match:
                if "__tests__" in pattern:
                    test_dirs.append("__tests__")
                    break

        return test_dirs

    def _find_readme(self, module_path: Path, relative_path: str) -> str | None:
        """Find README file and return its path.

        Returns path relative to project root, or None if not found.
        """
        readme_names = ["README.md", "README", "readme.md", "Readme.md", "README.adoc"]
        for name in readme_names:
            if (module_path / name).exists():
                if relative_path:
                    return f"{relative_path}/{name}"
                return name
        return None

    def _discover_npm_packages(self, module_path: Path, pkg: dict, relative_path: str) -> dict:
        """Discover npm packages from exports or directories.

        Per build-project-structure.md:
        - Discover from package.json exports field (subpath exports)
        - Fall back to top-level directories under src/ or lib/
        - Returns object keyed by package name with {path, exports?}
        """
        packages = {}
        module_rel = relative_path if relative_path else "."

        # Check for subpath exports in package.json
        exports = pkg.get("exports", {})
        if isinstance(exports, dict):
            for export_key, export_value in exports.items():
                # Skip main export "." and conditional exports
                if export_key == "." or not export_key.startswith("./"):
                    continue
                # Extract package name from export key (e.g., "./utils" -> "utils")
                pkg_name = export_key[2:]  # Remove "./"
                if pkg_name:
                    # Resolve export path
                    export_path = export_value if isinstance(export_value, str) else None
                    pkg_entry = {
                        "path": f"{module_rel}/src/{pkg_name}" if module_rel != "." else f"src/{pkg_name}"
                    }
                    if export_path:
                        pkg_entry["exports"] = export_key
                    packages[pkg_name] = pkg_entry

        # Fall back to top-level directories under src/ or lib/
        if not packages:
            for src_dir_name in ["src", "lib"]:
                src_dir = module_path / src_dir_name
                if src_dir.exists() and src_dir.is_dir():
                    for subdir in src_dir.iterdir():
                        if subdir.is_dir() and not subdir.name.startswith('.'):
                            pkg_name = subdir.name
                            if module_rel != ".":
                                pkg_path = f"{module_rel}/{src_dir_name}/{pkg_name}"
                            else:
                                pkg_path = f"{src_dir_name}/{pkg_name}"
                            packages[pkg_name] = {"path": pkg_path}
                    break  # Only check first existing src directory

        return packages

    def _extract_npm_dependencies_strings(self, pkg: dict) -> list:
        """Extract dependencies in string format.

        Returns list of "npm:{name}:{scope}" strings per specification.
        """
        dependencies = []

        # Production dependencies -> compile scope
        for name in pkg.get("dependencies", {}).keys():
            dependencies.append(f"npm:{name}:compile")

        # Dev dependencies -> test scope
        for name in pkg.get("devDependencies", {}).keys():
            dependencies.append(f"npm:{name}:test")

        # Peer dependencies -> provided scope
        for name in pkg.get("peerDependencies", {}).keys():
            dependencies.append(f"npm:{name}:provided")

        return dependencies

    def _build_npm_commands(self, module_path: str, scripts: dict) -> dict:
        """Build canonical command mappings based on available scripts.

        Per canonical-commands.md for npm:
        - clean: npm run clean (if "clean" script exists)
        - compile: npm run build (if "build" script exists)
        - module-tests: npm test (if "test" script exists)
        - quality-gate: npm run lint (if "lint" script exists)
        - verify: npm run build && npm test (if both scripts exist)
        """
        commands = {}
        base = "python3 .plan/execute-script.py pm-dev-frontend:plan-marshall-plugin:npm run"

        # Module path handling for --workspace
        workspace_arg = f' --workspace {module_path}' if module_path != "." else ""

        if "clean" in scripts:
            commands["clean"] = f'{base} --targets "run clean"{workspace_arg}'

        if "build" in scripts:
            commands["compile"] = f'{base} --targets "run build"{workspace_arg}'

        if "test" in scripts:
            commands["module-tests"] = f'{base} --targets "test"{workspace_arg}'

        if "lint" in scripts:
            commands["quality-gate"] = f'{base} --targets "run lint"{workspace_arg}'

        # verify: build + test combined
        if "build" in scripts and "test" in scripts:
            commands["verify"] = f'{base} --targets "run build && npm test"{workspace_arg}'
        elif "test" in scripts:
            # If no build script, verify is just test
            commands["verify"] = f'{base} --targets "test"{workspace_arg}'

        return commands

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
