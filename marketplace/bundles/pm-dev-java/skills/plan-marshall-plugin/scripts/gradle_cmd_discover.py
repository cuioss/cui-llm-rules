#!/usr/bin/env python3
"""Gradle module discovery command.

Discovers Gradle modules with complete metadata using file system analysis.
Implements the discover_modules() contract from build-project-structure.md.

Usage:
    python3 gradle_cmd_discover.py discover --root /path/to/project [--format json]

Output:
    JSON array of module objects conforming to build-project-structure.md contract.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Add extension-api scripts to path for base library imports
EXTENSION_API_DIR = Path(__file__).parent.parent.parent.parent.parent / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'
if str(EXTENSION_API_DIR) not in sys.path:
    sys.path.insert(0, str(EXTENSION_API_DIR))

from build_discover import find_readme


# =============================================================================
# Constants
# =============================================================================

BUILD_GRADLE = "build.gradle"
BUILD_GRADLE_KTS = "build.gradle.kts"
SETTINGS_GRADLE = "settings.gradle"
SETTINGS_GRADLE_KTS = "settings.gradle.kts"


# =============================================================================
# Module Discovery
# =============================================================================

def discover_gradle_modules(project_root: str) -> list:
    """Discover all Gradle modules with complete metadata.

    Uses file system analysis to find all build.gradle files and
    extract module information.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of module dicts conforming to build-project-structure.md contract.
    """
    root = Path(project_root).resolve()
    modules = []

    # Check for settings.gradle
    settings_path = None
    for sf in [SETTINGS_GRADLE_KTS, SETTINGS_GRADLE]:
        if (root / sf).exists():
            settings_path = root / sf
            break

    if settings_path:
        # Multi-module project
        content = settings_path.read_text()
        for match in re.finditer(r'include\s*[(\'"]+:?([^)\'\"]+)[)\'"]+', content):
            module_name = match.group(1).replace(':', '/')
            module_path = root / module_name
            if module_path.exists():
                module_data = _extract_gradle_module(module_path, root, module_name)
                if module_data:
                    modules.append(module_data)
    else:
        # Single-module project
        for bf in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
            if (root / bf).exists():
                module_data = _extract_gradle_module(root, root, "")
                if module_data:
                    modules.append(module_data)
                break

    return modules


# =============================================================================
# Module Extraction
# =============================================================================

def _extract_gradle_module(module_path: Path, project_root: Path, relative_path: str) -> dict | None:
    """Extract Gradle module with contract-compliant structure.

    Args:
        module_path: Path to module directory
        project_root: Project root path (unused but kept for API consistency)
        relative_path: Path relative to project root ("" for root module)

    Returns:
        Module dict conforming to build-project-structure.md or None
    """
    build_file = None
    for bf in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
        if (module_path / bf).exists():
            build_file = module_path / bf
            break

    if not build_file:
        return None

    content = build_file.read_text()

    # Extract name
    name = module_path.name if module_path.name != "." else project_root.name
    for pattern in [r'archivesBaseName\s*=\s*[\'"]([^\'"]+)[\'"]']:
        match = re.search(pattern, content)
        if match:
            name = match.group(1)
            break

    # Source directories
    sources = _discover_sources(module_path)
    source_paths = [f"{relative_path}/{s}" if relative_path else s for s in sources["main"]]
    test_paths = [f"{relative_path}/{t}" if relative_path else t for t in sources["test"]]

    # README
    readme = find_readme(str(module_path))
    readme_path = f"{relative_path}/{readme}" if readme and relative_path else readme

    # Stats
    source_files = _count_java_files(module_path, sources["main"])
    test_files = _count_java_files(module_path, sources["test"])

    # Commands
    commands = _build_commands(
        module_name=name,
        has_sources=source_files > 0,
        has_tests=test_files > 0,
        relative_path=relative_path
    )

    return {
        "name": name,
        "technology": "gradle",
        "paths": {
            "module": relative_path if relative_path else ".",
            "descriptor": f"{relative_path}/{build_file.name}" if relative_path else build_file.name,
            "sources": source_paths,
            "tests": test_paths,
            "readme": readme_path
        },
        "metadata": {
            "artifact_id": name,
            "group_id": None,
            "packaging": "jar",
            "description": None,
            "parent": None
        },
        "packages": {},
        "dependencies": [],
        "stats": {
            "source_files": source_files,
            "test_files": test_files
        },
        "commands": commands
    }


# =============================================================================
# Source Discovery
# =============================================================================

def _discover_sources(module_path: Path) -> dict:
    """Discover source directories.

    Returns:
        Dict with main and test source directories
    """
    sources = {"main": [], "test": []}

    if (module_path / "src" / "main" / "java").exists():
        sources["main"].append("src/main/java")
    if (module_path / "src" / "test" / "java").exists():
        sources["test"].append("src/test/java")

    return sources


def _count_java_files(module_path: Path, source_dirs: list) -> int:
    """Count Java files in source directories."""
    count = 0
    for src in source_dirs:
        src_path = module_path / src
        if src_path.exists():
            count += len(list(src_path.rglob("*.java")))
    return count


# =============================================================================
# Commands
# =============================================================================

def _build_commands(
    module_name: str,
    has_sources: bool,
    has_tests: bool,
    relative_path: str
) -> dict:
    """Build commands object with resolved canonical command strings.

    Resolution rules per canonical-commands.md:
    - Always: clean (separate), quality-gate, verify, install, clean-install, package
    - Source-conditional: compile
    - Test-conditional: test-compile, module-tests

    Note: clean is a separate command. Other commands do NOT include clean goal.
    Use clean-install for the combined clean + install workflow.

    Args:
        module_name: Module name or directory name
        has_sources: Whether module has source files
        has_tests: Whether module has test files
        relative_path: Path relative to project root ("" for root module)
    """
    base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run"

    # Only use --module for submodules, not root single-module projects
    is_root_module = not relative_path or relative_path == "."
    module_arg = "" if is_root_module else f" --module {module_name}"

    commands = {
        # Always: clean (separate), quality-gate, verify, install, clean-install, package
        # Per canonical-commands.md: clean is separate, other commands don't include clean
        "clean": f'{base} --targets "clean"{module_arg}',
        "quality-gate": f'{base} --targets "build"{module_arg}',
        "verify": f'{base} --targets "build"{module_arg}',
        "install": f'{base} --targets "publishToMavenLocal"{module_arg}',
        "clean-install": f'{base} --targets "clean publishToMavenLocal"{module_arg}',
        "package": f'{base} --targets "jar"{module_arg}',
    }

    # Source-conditional: compile
    if has_sources:
        commands["compile"] = f'{base} --targets "compileJava"{module_arg}'

    # Test-conditional: test-compile, module-tests
    if has_tests:
        commands["test-compile"] = f'{base} --targets "compileTestJava"{module_arg}'
        commands["module-tests"] = f'{base} --targets "test"{module_arg}'

    return commands


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Gradle module discovery")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # discover subcommand
    discover_parser = subparsers.add_parser("discover", help="Discover Gradle modules")
    discover_parser.add_argument("--root", required=True, help="Project root directory")
    discover_parser.add_argument("--format", choices=["json"], default="json", help="Output format")

    args = parser.parse_args()

    if args.command == "discover":
        modules = discover_gradle_modules(args.root)
        print(json.dumps(modules, indent=2))


if __name__ == "__main__":
    main()
