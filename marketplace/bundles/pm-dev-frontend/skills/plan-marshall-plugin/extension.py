#!/usr/bin/env python3
"""Extension API for pm-dev-frontend bundle.

Provides build system detection, module discovery for npm/JavaScript projects.

Implementation logic resides in scripts/ directory.
"""

import json
from pathlib import Path

from extension_base import ExtensionBase
from build_discover import discover_descriptors, build_module_base


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

        Uses base library discover_descriptors() for recursive package.json discovery.
        Returns comprehensive module information including metadata, dependencies,
        and stats per build-project-structure.md specification.
        """
        # Use base library to find all package.json files recursively
        descriptors = discover_descriptors(project_root, PACKAGE_JSON)

        modules = []
        discovered_paths = set()

        for desc_path in descriptors:
            # Build base module info using base library
            base = build_module_base(project_root, str(desc_path))

            # Skip if already discovered (same module path)
            if base.paths.module in discovered_paths:
                continue
            discovered_paths.add(base.paths.module)

            # Load package.json for npm-specific enrichment
            try:
                with open(desc_path) as f:
                    pkg = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            # Skip workspace root if it has workspaces (discover children instead)
            workspaces = pkg.get("workspaces", [])
            if isinstance(workspaces, dict):
                workspaces = workspaces.get("packages", [])
            if workspaces and base.paths.module == ".":
                # This is a workspace root - children will be discovered separately
                continue

            # Enrich with npm-specific data
            module_data = self._enrich_npm_module(base, pkg, project_root)
            if module_data:
                modules.append(module_data)

        return modules

    def _enrich_npm_module(self, base, pkg: dict, project_root: str) -> dict | None:
        """Enrich base module with npm-specific data.

        Args:
            base: ModuleBase from build_module_base()
            pkg: Parsed package.json content
            project_root: Project root directory

        Returns structure per build-project-structure.md specification:
        - technology: "npm" (single string)
        - paths: {module, descriptor, sources, tests, readme}
        - metadata: npm-specific fields (version, type, private, description, main, license)
        - packages: {} (object keyed by package name)
        - dependencies: ["npm:name:scope", ...] (string format)
        - stats: {source_files, test_files}
        - commands: {} (canonical command mappings)
        """
        root = Path(project_root)
        module_path = root / base.paths.module if base.paths.module != "." else root

        # Use name from package.json, fallback to base name
        name = pkg.get("name", base.name)

        # Discover source and test directories (module-relative)
        source_dirs_local = self._discover_source_dirs(module_path, pkg)
        test_dirs_local = self._discover_test_dirs(module_path, pkg)

        # Convert to repo-root relative paths
        module_prefix = base.paths.module
        if module_prefix == ".":
            source_dirs = source_dirs_local
            test_dirs = test_dirs_local
        else:
            source_dirs = [f"{module_prefix}/{d}" for d in source_dirs_local]
            test_dirs = [f"{module_prefix}/{d}" for d in test_dirs_local]

        # Build paths object (extending base), filtering out None values
        paths = {
            k: v for k, v in {
                "module": base.paths.module,
                "descriptor": base.paths.descriptor,
                "sources": source_dirs,
                "tests": test_dirs,
                "readme": base.paths.readme
            }.items() if v is not None
        }

        # Build npm-specific metadata for planning context, filtering out None values
        metadata = {
            k: v for k, v in {
                "type": pkg.get("type"),  # "module" (ESM) or "commonjs" - affects imports
                "description": pkg.get("description")
            }.items() if v is not None
        }

        # Discover packages (from exports or directories)
        packages = self._discover_npm_packages(module_path, pkg, base.paths.module)

        # Extract dependencies in string format: npm:{name}:{scope}
        dependencies = self._extract_npm_dependencies_strings(pkg)

        # Calculate stats (use module-relative dirs since module_path is the base)
        source_files = self._count_js_files(module_path, source_dirs_local)
        test_files = self._count_js_files(module_path, test_dirs_local)

        # Build commands based on available scripts
        commands = self._build_npm_commands(base.paths.module, pkg.get("scripts", {}))

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
