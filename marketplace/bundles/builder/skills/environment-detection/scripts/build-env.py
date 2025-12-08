#!/usr/bin/env python3
"""
Build environment detection - detect available build systems.

Usage:
    build-env.py detect --project-dir <dir> [--format <format>]
    build-env.py --help

Subcommands:
    detect      Detect available build systems in a project
"""

import argparse
import json
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
    """Detect all available build systems in the project directory."""
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
                break

    if not detected:
        return {
            "available_systems": "",
            "default_system": "",
            "detected": [],
            "message": "No build systems detected"
        }

    detected.sort(key=lambda x: x["priority"])
    available = ",".join(d["name"] for d in detected)
    default = detected[0]["name"]

    return {
        "available_systems": available,
        "default_system": default,
        "detected": detected,
        "message": f"Detected {len(detected)} build system(s)"
    }


def cmd_detect(args):
    """Handle detect subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({"status": "error", "message": f"Directory not found: {project_dir}"}, indent=2))
        return 1

    result = detect_build_systems(project_dir)
    result["status"] = "success"
    result["project_dir"] = str(project_dir)

    if args.format == "simple":
        print(f"available_systems={result['available_systems']}")
        print(f"default_system={result['default_system']}")
    else:
        print(json.dumps(result, indent=2))

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build environment detection", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # detect subcommand
    detect_parser = subparsers.add_parser("detect", help="Detect available build systems in a project")
    detect_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory to scan")
    detect_parser.add_argument("--format", choices=["json", "simple"], default="json", help="Output format")
    detect_parser.set_defaults(func=cmd_detect)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
