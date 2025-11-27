#!/usr/bin/env python3
"""
Find Gradle project paths from project name.

Searches settings.gradle(.kts) and build files to locate projects.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def find_settings_file(root: Path) -> Path | None:
    """Find settings.gradle or settings.gradle.kts."""
    for name in ["settings.gradle.kts", "settings.gradle"]:
        settings_path = root / name
        if settings_path.exists():
            return settings_path
    return None


def parse_included_projects(settings_path: Path) -> list[str]:
    """Parse included projects from settings file."""
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    projects = []

    # Kotlin DSL patterns
    # include(":core")
    # include(":api", ":impl")
    # include("services:auth")
    kotlin_pattern = r'include\s*\(\s*([^)]+)\s*\)'
    for match in re.finditer(kotlin_pattern, content):
        args = match.group(1)
        # Extract quoted strings
        for quoted in re.findall(r'["\']([^"\']+)["\']', args):
            # Normalize to colon prefix
            project = quoted if quoted.startswith(":") else f":{quoted}"
            projects.append(project)

    # Groovy DSL patterns
    # include ':core'
    # include ':api', ':impl'
    groovy_pattern = r"include\s+(['\"][^'\"]+['\"](?:\s*,\s*['\"][^'\"]+['\"])*)"
    for match in re.finditer(groovy_pattern, content):
        args = match.group(1)
        for quoted in re.findall(r'["\']([^"\']+)["\']', args):
            project = quoted if quoted.startswith(":") else f":{quoted}"
            projects.append(project)

    return list(set(projects))


def find_build_files(root: Path) -> list[Path]:
    """Find all build.gradle and build.gradle.kts files."""
    build_files = []
    for pattern in ["**/build.gradle", "**/build.gradle.kts"]:
        for path in root.glob(pattern):
            # Skip build directories and hidden directories
            if any(
                part.startswith(".") or part in ("build", "target", ".gradle")
                for part in path.parts
            ):
                continue
            build_files.append(path)
    return build_files


def extract_project_name(build_file: Path) -> str | None:
    """Extract project name from build file or directory."""
    # First try to get from settings if this is a subproject
    return build_file.parent.name


def project_path_to_gradle_notation(root: Path, project_dir: Path) -> str:
    """Convert file path to Gradle project notation."""
    relative = project_dir.relative_to(root)
    parts = relative.parts
    return ":" + ":".join(parts) if parts else ":"


def get_root_project_name(settings_path: Path) -> str | None:
    """Extract rootProject.name from settings file."""
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match rootProject.name = "name" or rootProject.name = 'name'
    match = re.search(r'rootProject\.name\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    return None


def search_by_name(root: Path, project_name: str) -> dict:
    """Search for project by name."""
    settings_file = find_settings_file(root)
    included_projects = []
    root_project_name = None

    if settings_file:
        included_projects = parse_included_projects(settings_file)
        root_project_name = get_root_project_name(settings_file)

    # Check if searching for root project
    if root_project_name and project_name == root_project_name:
        # Check for build file at root
        for ext in [".kts", ""]:
            candidate = root / f"build.gradle{ext}"
            if candidate.exists():
                return {
                    "status": "success",
                    "data": {
                        "project_name": project_name,
                        "project_path": ":",
                        "build_file": f"build.gradle{ext}",
                        "parent_projects": [],
                        "gradle_p_argument": "",
                    },
                }

    # Search in included projects
    matches = []
    for project in included_projects:
        # Match by last segment
        project_last = project.split(":")[-1]
        if project_last == project_name or project == f":{project_name}":
            matches.append(project)

    # Also search build files
    build_files = find_build_files(root)
    for build_file in build_files:
        dir_name = build_file.parent.name
        if dir_name == project_name:
            project_path = project_path_to_gradle_notation(
                root, build_file.parent
            )
            if project_path not in matches:
                matches.append(project_path)

    if not matches:
        return {
            "status": "error",
            "error": "project_not_found",
            "message": f"No project found with name '{project_name}'",
        }

    if len(matches) > 1:
        return {
            "status": "error",
            "error": "ambiguous_project_name",
            "message": f"Multiple projects found for name '{project_name}'. Select one.",
            "choices": matches,
        }

    project_path = matches[0]
    # Convert :services:auth to services/auth for directory path
    dir_path = project_path.lstrip(":").replace(":", "/")
    build_file = None
    for ext in [".kts", ""]:
        candidate = root / dir_path / f"build.gradle{ext}"
        if candidate.exists():
            build_file = str(candidate.relative_to(root))
            break

    # Extract parent projects
    parts = project_path.lstrip(":").split(":")
    parent_projects = [
        ":" + ":".join(parts[:i]) for i in range(1, len(parts))
    ]

    return {
        "status": "success",
        "data": {
            "project_name": project_name,
            "project_path": project_path,
            "build_file": build_file,
            "parent_projects": parent_projects,
            "gradle_p_argument": f"-p {dir_path}" if dir_path else "",
        },
    }


def validate_path(root: Path, project_path: str) -> dict:
    """Validate an explicit project path."""
    # Normalize path
    if project_path.startswith(":"):
        dir_path = project_path.lstrip(":").replace(":", "/")
    else:
        dir_path = project_path

    full_path = root / dir_path
    if not full_path.exists():
        return {
            "status": "error",
            "error": "path_not_found",
            "message": f"Project path does not exist: {project_path}",
        }

    # Find build file
    build_file = None
    for ext in [".kts", ""]:
        candidate = full_path / f"build.gradle{ext}"
        if candidate.exists():
            build_file = str(candidate.relative_to(root))
            break

    if not build_file:
        return {
            "status": "error",
            "error": "no_build_file",
            "message": f"No build.gradle(.kts) found in: {project_path}",
        }

    project_name = full_path.name
    gradle_path = ":" + dir_path.replace("/", ":")

    parts = dir_path.split("/")
    parent_projects = [
        ":" + ":".join(parts[:i]) for i in range(1, len(parts))
    ]

    return {
        "status": "success",
        "data": {
            "project_name": project_name,
            "project_path": gradle_path,
            "build_file": build_file,
            "parent_projects": parent_projects,
            "gradle_p_argument": f"-p {dir_path}",
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Find Gradle project paths from project name"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--project-name",
        help="Project name to search for",
    )
    group.add_argument(
        "--project-path",
        help="Explicit project path to validate",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()

    # Validate root exists
    if not root.exists():
        result = {
            "status": "error",
            "error": "root_not_found",
            "message": f"Root directory not found: {args.root}",
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    if args.project_name:
        result = search_by_name(root, args.project_name)
    else:
        result = validate_path(root, args.project_path)

    print(json.dumps(result, indent=2))

    # Exit with non-zero code on error
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
