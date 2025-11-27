#!/usr/bin/env python3
"""
Detect available build systems in the current project.

Scans for build files and determines:
- Available build systems (all detected)
- Default build system (primary based on priority)

Output: JSON with available_systems (comma-separated) and default_system
"""

import argparse
import json
import os
import sys
from pathlib import Path


# Build system detection configuration
BUILD_SYSTEMS = {
    "maven": {
        "files": ["pom.xml"],
        "priority": 1,
        "technology": "java"
    },
    "gradle": {
        "files": ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"],
        "priority": 2,
        "technology": "java"
    },
    "npm": {
        "files": ["package.json"],
        "priority": 3,
        "technology": "javascript"
    }
}


def detect_build_systems(project_dir: Path) -> dict:
    """
    Detect all available build systems in the project directory.

    Args:
        project_dir: Root directory of the project

    Returns:
        Dictionary with available_systems and default_system
    """
    detected = []

    for system, config in BUILD_SYSTEMS.items():
        for build_file in config["files"]:
            file_path = project_dir / build_file
            if file_path.exists():
                detected.append({
                    "name": system,
                    "priority": config["priority"],
                    "technology": config["technology"],
                    "detected_by": str(build_file)
                })
                break  # Only need one file per system

    if not detected:
        return {
            "available_systems": "",
            "default_system": "",
            "detected": [],
            "message": "No build systems detected"
        }

    # Sort by priority (lowest number = highest priority)
    detected.sort(key=lambda x: x["priority"])

    # Build comma-separated list
    available = ",".join(d["name"] for d in detected)
    default = detected[0]["name"]

    return {
        "available_systems": available,
        "default_system": default,
        "detected": detected,
        "message": f"Detected {len(detected)} build system(s)"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect available build systems in a project"
    )
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "simple"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({
            "status": "error",
            "message": f"Directory not found: {project_dir}"
        }), file=sys.stderr)
        sys.exit(1)

    result = detect_build_systems(project_dir)
    result["status"] = "success"
    result["project_dir"] = str(project_dir)

    if args.format == "simple":
        # Simple output for shell scripts
        print(f"available_systems={result['available_systems']}")
        print(f"default_system={result['default_system']}")
    else:
        # JSON output
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
