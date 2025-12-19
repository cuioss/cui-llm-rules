#!/usr/bin/env python3
"""
Build environment detection and command generation.

Usage:
    build-env.py detect --project-dir <dir> [--format <format>]
    build-env.py detect-modules --project-dir <dir>
    build-env.py persist --project-dir <dir> [--dry-run]
    build-env.py --help

Subcommands:
    detect          Detect available build systems in a project
    detect-modules  Detect project modules (Maven, Gradle, npm workspaces)
    persist         Generate and persist module commands to marshal.json
"""

import argparse
import json
import re
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


# Standard command labels and their goal mappings per build system
COMMAND_MAPPINGS = {
    "maven": {
        "test-compile": "test-compile",
        "test": "clean test",
        "verify": "clean verify",
        "install": "clean install",
        "pre-commit": "clean install",
        "coverage": "clean verify -Pcoverage"
    },
    "gradle": {
        "test-compile": "testClasses",
        "test": "clean test",
        "verify": "clean build",
        "install": "clean build publishToMavenLocal",
        "pre-commit": "clean build",
        "coverage": "clean test jacocoTestReport"
    },
    "npm": {
        "test": "run test",
        "build": "run build",
        "lint": "run lint",
        "verify": "run test && npm run lint",
        "pre-commit": "run test"
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


# =============================================================================
# Module Detection
# =============================================================================

def detect_maven_modules(project_dir: Path) -> list:
    """Detect Maven modules from pom.xml."""
    modules = []
    pom_path = project_dir / "pom.xml"

    if not pom_path.exists():
        return modules

    content = pom_path.read_text()

    # Extract <modules> section
    modules_match = re.search(r'<modules>(.*?)</modules>', content, re.DOTALL)
    if modules_match:
        module_content = modules_match.group(1)
        for module in re.findall(r'<module>([^<]+)</module>', module_content):
            module_path = project_dir / module
            if module_path.exists():
                modules.append({
                    "name": module,
                    "path": module,
                    "build_system": "maven"
                })

    return modules


def detect_gradle_modules(project_dir: Path) -> list:
    """Detect Gradle modules from settings.gradle or settings.gradle.kts."""
    modules = []

    for settings_file in ["settings.gradle.kts", "settings.gradle"]:
        settings_path = project_dir / settings_file
        if settings_path.exists():
            content = settings_path.read_text()

            # Match include("module") or include ':module' patterns
            for match in re.finditer(r'include\s*[(\'"]+:?([^)\'\"]+)[)\'"]+', content):
                module_name = match.group(1).replace(':', '/')
                module_path = project_dir / module_name
                if module_path.exists():
                    modules.append({
                        "name": module_name.replace('/', '-'),
                        "path": module_name,
                        "build_system": "gradle"
                    })
            break

    return modules


def detect_npm_workspaces(project_dir: Path) -> list:
    """Detect npm workspaces from package.json."""
    modules = []
    package_path = project_dir / "package.json"

    if not package_path.exists():
        return modules

    try:
        data = json.loads(package_path.read_text())
        workspaces = data.get("workspaces", [])

        if isinstance(workspaces, dict):
            workspaces = workspaces.get("packages", [])

        for workspace in workspaces:
            # Handle glob patterns like "packages/*"
            if "*" in workspace:
                base_path = project_dir / workspace.replace("/*", "").replace("/**", "")
                if base_path.exists() and base_path.is_dir():
                    for child in base_path.iterdir():
                        if child.is_dir() and (child / "package.json").exists():
                            modules.append({
                                "name": child.name,
                                "path": str(child.relative_to(project_dir)),
                                "build_system": "npm"
                            })
            else:
                workspace_path = project_dir / workspace
                if workspace_path.exists():
                    modules.append({
                        "name": Path(workspace).name,
                        "path": workspace,
                        "build_system": "npm"
                    })
    except (json.JSONDecodeError, KeyError):
        pass

    return modules


def detect_all_modules(project_dir: Path) -> list:
    """Detect all modules from all build systems."""
    modules = []
    modules.extend(detect_maven_modules(project_dir))
    modules.extend(detect_gradle_modules(project_dir))
    modules.extend(detect_npm_workspaces(project_dir))
    return modules


def cmd_detect_modules(args):
    """Handle detect-modules subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({"status": "error", "message": f"Directory not found: {project_dir}"}, indent=2))
        return 1

    modules = detect_all_modules(project_dir)

    result = {
        "status": "success",
        "project_dir": str(project_dir),
        "modules": modules,
        "count": len(modules)
    }

    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Command Generation and Persistence
# =============================================================================

def generate_command(build_system: str, label: str, module_name: str = None) -> str:
    """Generate a full executable command string.

    Args:
        build_system: maven, gradle, or npm
        label: Command label (test, verify, etc.)
        module_name: Module name (None or "default" for root module)

    Returns:
        Full command string for execution
    """
    if build_system not in COMMAND_MAPPINGS:
        return None

    if label not in COMMAND_MAPPINGS[build_system]:
        return None

    goals = COMMAND_MAPPINGS[build_system][label]

    if build_system == "npm":
        base = f'python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "{goals}"'
    else:
        base = f'python3 .plan/execute-script.py plan-marshall:build-operations:{build_system} execute --goals "{goals}"'

    # Add module flag for non-default modules
    if module_name and module_name != "default":
        base += f" --module {module_name}"

    # Add profile for pre-commit
    if label == "pre-commit":
        base += " --profile pre-commit"

    return base


def generate_module_commands(build_system: str, module_name: str = None) -> dict:
    """Generate all standard commands for a module.

    Args:
        build_system: maven, gradle, or npm
        module_name: Module name (None or "default" for root module)

    Returns:
        Dict of label -> command string
    """
    commands = {}

    if build_system not in COMMAND_MAPPINGS:
        return commands

    for label in COMMAND_MAPPINGS[build_system]:
        cmd = generate_command(build_system, label, module_name)
        if cmd:
            commands[label] = cmd

    return commands


def load_marshal_json(project_dir: Path) -> dict:
    """Load marshal.json from .plan directory."""
    marshal_path = project_dir / ".plan" / "marshal.json"
    if marshal_path.exists():
        return json.loads(marshal_path.read_text())
    return {}


def save_marshal_json(project_dir: Path, config: dict) -> None:
    """Save marshal.json to .plan directory."""
    marshal_path = project_dir / ".plan" / "marshal.json"
    marshal_path.parent.mkdir(parents=True, exist_ok=True)
    marshal_path.write_text(json.dumps(config, indent=2))


def cmd_persist(args):
    """Handle persist subcommand - detect and persist module commands."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({"status": "error", "message": f"Directory not found: {project_dir}"}, indent=2))
        return 1

    # Detect build systems
    build_result = detect_build_systems(project_dir)
    if not build_result["available_systems"]:
        print("status: error")
        print("message: No build systems detected")
        return 1

    available_systems = build_result["available_systems"].split(",")
    default_system = build_result["default_system"]

    # Detect modules
    modules = detect_all_modules(project_dir)

    # Load existing config
    config = load_marshal_json(project_dir)

    if "modules" not in config:
        config["modules"] = {}

    # Ensure default module exists
    if "default" not in config["modules"]:
        config["modules"]["default"] = {
            "path": ".",
            "domains": [],
            "build_systems": [default_system]
        }

    # Generate commands for default module
    default_commands = generate_module_commands(default_system)
    config["modules"]["default"]["commands"] = default_commands

    # Generate commands for detected modules
    modules_updated = 1  # default
    commands_generated = len(default_commands)

    for module in modules:
        mod_name = module["name"]
        mod_system = module["build_system"]

        if mod_name not in config["modules"]:
            config["modules"][mod_name] = {
                "path": module["path"],
                "domains": [],
                "build_systems": [mod_system]
            }

        mod_commands = generate_module_commands(mod_system, mod_name)
        config["modules"][mod_name]["commands"] = mod_commands
        modules_updated += 1
        commands_generated += len(mod_commands)

    # Update build_systems section if not present
    if "build_systems" not in config or not config["build_systems"]:
        config["build_systems"] = [
            {"system": system, "skill": "plan-marshall:build-operations"}
            for system in available_systems
        ]

    # Save unless dry run
    if not args.dry_run:
        save_marshal_json(project_dir, config)

    # Output in TOON format
    print(f"status: success")
    print(f"build_systems: {build_result['available_systems']}")
    print(f"modules_updated: {modules_updated}")
    print(f"commands_generated: {commands_generated}")
    print()
    print(f"modules[{modules_updated}]" + "{name,path,commands_count}:")
    for mod_name, mod_config in config["modules"].items():
        cmd_count = len(mod_config.get("commands", {}))
        print(f"{mod_name}\t{mod_config.get('path', mod_name)}\t{cmd_count}")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build environment detection and command generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # detect subcommand
    detect_parser = subparsers.add_parser("detect", help="Detect available build systems in a project")
    detect_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory to scan")
    detect_parser.add_argument("--format", choices=["json", "simple"], default="json", help="Output format")
    detect_parser.set_defaults(func=cmd_detect)

    # detect-modules subcommand
    modules_parser = subparsers.add_parser("detect-modules", help="Detect project modules (Maven, Gradle, npm workspaces)")
    modules_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory to scan")
    modules_parser.set_defaults(func=cmd_detect_modules)

    # persist subcommand
    persist_parser = subparsers.add_parser("persist", help="Generate and persist module commands to marshal.json")
    persist_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    persist_parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Show what would be done without saving")
    persist_parser.set_defaults(func=cmd_persist)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
