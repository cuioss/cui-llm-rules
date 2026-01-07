#!/usr/bin/env python3
"""Shared infrastructure for integration tests.

Integration tests validate discovery and build operations against real
projects in the local git directory.
"""

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


# Default git directory (parent of cui-llm-rules)
DEFAULT_GIT_DIR = Path(__file__).parent.parent.parent.parent


@dataclass
class TestProject:
    """A test project configuration."""
    name: str
    relative_path: str  # Relative to git directory
    description: str

    def absolute_path(self, git_dir: Path = DEFAULT_GIT_DIR) -> Path:
        """Get absolute path to the project."""
        return git_dir / self.relative_path

    def exists(self, git_dir: Path = DEFAULT_GIT_DIR) -> bool:
        """Check if the project exists."""
        return self.absolute_path(git_dir).exists()


class IntegrationTestContext:
    """Context manager for integration tests.

    Manages:
    - Output directory creation and cleanup
    - Project existence validation
    - Result persistence
    """

    def __init__(self, output_dir: Path, clean_before: bool = True):
        """Initialize the context.

        Args:
            output_dir: Directory for test output (e.g., .plan/temp/test-results-npm)
            clean_before: Whether to clean the output directory before tests
        """
        self.output_dir = output_dir
        self.clean_before = clean_before
        self.git_dir = DEFAULT_GIT_DIR
        self.results: dict[str, dict] = {}
        self.skipped: list[str] = []
        self.errors: list[str] = []

    def __enter__(self):
        if self.clean_before and self.output_dir.exists():
            # Only clean JSON result files, preserve description.md and scripts
            for f in self.output_dir.glob("*-modules.json"):
                f.unlink()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def validate_project(self, project: TestProject) -> bool:
        """Check if a project exists, log if missing."""
        if not project.exists(self.git_dir):
            self.skipped.append(
                f"{project.name}: Not found at {project.absolute_path(self.git_dir)}"
            )
            return False
        return True

    def save_result(self, project: TestProject, data: list | dict) -> Path:
        """Save discovery result to JSON file."""
        # Create filename from project name (sanitize)
        filename = project.name.lower().replace(" ", "-").replace("/", "-")
        output_path = self.output_dir / f"{filename}-modules.json"
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        self.results[project.name] = {"path": output_path, "data": data}
        return output_path

    def print_summary(self):
        """Print test summary."""
        print(f"\n{'=' * 60}")
        print("Integration Test Summary")
        print(f"{'=' * 60}")
        print(f"Tested: {len(self.results)}")
        print(f"Skipped: {len(self.skipped)}")
        print(f"Errors: {len(self.errors)}")

        if self.skipped:
            print("\nSkipped projects (not found):")
            for msg in self.skipped:
                print(f"  - {msg}")

        if self.errors:
            print("\nErrors:")
            for msg in self.errors:
                print(f"  - {msg}")


def assert_no_null_values(data: dict | list, path: str = "") -> list[str]:
    """Recursively check for null values in data structure.

    Returns list of paths where null values were found.
    """
    nulls = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if value is None:
                nulls.append(current_path)
            else:
                nulls.extend(assert_no_null_values(value, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]"
            if item is None:
                nulls.append(current_path)
            else:
                nulls.extend(assert_no_null_values(item, current_path))
    return nulls


def assert_paths_exist(modules: list[dict], project_root: Path) -> list[str]:
    """Verify all paths in modules exist relative to project root.

    Checks:
    - paths.descriptor
    - paths.sources (each directory)
    - paths.tests (each directory)
    - paths.readme (if present)

    Returns list of missing paths.
    """
    missing = []
    for module in modules:
        name = module.get("name", "unknown")
        paths = module.get("paths", {})

        # Check descriptor
        descriptor = paths.get("descriptor")
        if descriptor:
            full_path = project_root / descriptor
            if not full_path.exists():
                missing.append(f"{name}: descriptor '{descriptor}' not found")

        # Check sources
        for src in paths.get("sources", []):
            full_path = project_root / src
            if not full_path.exists():
                missing.append(f"{name}: source '{src}' not found")

        # Check tests
        for test in paths.get("tests", []):
            full_path = project_root / test
            if not full_path.exists():
                missing.append(f"{name}: test '{test}' not found")

        # Check readme (optional)
        readme = paths.get("readme")
        if readme:
            full_path = project_root / readme
            if not full_path.exists():
                missing.append(f"{name}: readme '{readme}' not found")

    return missing


# =============================================================================
# Technology-Specific Assertions
# =============================================================================

def assert_npm_module_structure(modules: list[dict]) -> list[str]:
    """Validate npm-specific module structure.

    Checks:
    - technology is "npm"
    - paths.descriptor ends with "package.json"
    - dependencies follow format "npm:{name}:{scope}"
    - metadata.type is "module" or "commonjs" (if present)
    - commands contain npm execute-script pattern

    Returns list of validation errors.
    """
    errors = []
    valid_dep_scopes = {"compile", "test", "provided", "runtime"}
    valid_module_types = {"module", "commonjs"}

    for module in modules:
        name = module.get("name", "unknown")

        # Check technology
        tech = module.get("technology")
        if tech != "npm":
            errors.append(f"{name}: technology should be 'npm', got '{tech}'")

        # Check descriptor path
        paths = module.get("paths", {})
        descriptor = paths.get("descriptor", "")
        if not descriptor.endswith("package.json"):
            errors.append(f"{name}: descriptor should end with 'package.json', got '{descriptor}'")

        # Check dependencies format
        for dep in module.get("dependencies", []):
            if not isinstance(dep, str):
                errors.append(f"{name}: dependency should be string, got {type(dep).__name__}")
                continue
            parts = dep.split(":")
            if len(parts) != 3:
                errors.append(f"{name}: dependency '{dep}' should have format 'npm:name:scope'")
            elif parts[0] != "npm":
                errors.append(f"{name}: dependency '{dep}' should start with 'npm:'")
            elif parts[2] not in valid_dep_scopes:
                errors.append(f"{name}: dependency '{dep}' has invalid scope '{parts[2]}'")

        # Check metadata.type if present
        metadata = module.get("metadata", {})
        module_type = metadata.get("type")
        if module_type is not None and module_type not in valid_module_types:
            errors.append(f"{name}: metadata.type should be 'module' or 'commonjs', got '{module_type}'")

        # Check commands contain npm pattern
        commands = module.get("commands", {})
        for cmd_name, cmd_value in commands.items():
            if not isinstance(cmd_value, str):
                errors.append(f"{name}: command '{cmd_name}' should be string")
            elif "pm-dev-frontend:plan-marshall-plugin:npm" not in cmd_value:
                errors.append(f"{name}: command '{cmd_name}' missing npm execute-script pattern")

    return errors
