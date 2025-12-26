#!/usr/bin/env python3
"""
Build environment detection and command generation.

Uses extension-api for discovery and delegates domain-specific detection
to domain bundle extensions (pm-dev-java, pm-dev-frontend).

Usage:
    build-env.py detect --project-dir <dir> [--format <format>]
    build-env.py detect-modules --project-dir <dir>
    build-env.py detect-module-type --module <module> [--build-system <bs>]
    build-env.py detect-profiles --module <module> [--build-system <bs>]
    build-env.py persist --project-dir <dir> [--dry-run]
    build-env.py lookup --canonical <name> --module <module>
    build-env.py get-available-commands --module <module>
    build-env.py validate-required --module <module>
    build-env.py --help

Subcommands:
    detect               Detect available build systems in a project
    detect-modules       Detect project modules (Maven, Gradle, npm workspaces)
    detect-module-type   Detect module type (pom, jar, war, quarkus)
    detect-profiles      Detect Maven/Gradle profiles and classify them
    persist              Generate and persist module commands to marshal.json
    lookup               Look up canonical command for a module
    get-available-commands  List available canonical commands for a module
    validate-required    Validate required commands are configured
"""

import argparse
import json
import sys
from pathlib import Path

# Import from extension module (same directory)
from extension import (
    discover_extensions,
    get_build_systems_from_extensions,
    get_command_mappings_from_extensions,
    get_skill_domains_from_extensions,
    get_modules_from_extensions,
)


# =============================================================================
# Canonical Command Vocabulary
# =============================================================================

# Canonical command definitions with phase, description, required flag, applicable_to
# Reference: extension-api/standards/canonical-commands.md
CANONICAL_COMMANDS = {
    # Build phase
    "compile": {
        "phase": "build",
        "description": "Compile production sources only",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus"],
    },
    "test-compile": {
        "phase": "build",
        "description": "Compile production and test sources",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus"],
    },

    # Test phase
    "module-tests": {
        "phase": "test",
        "description": "Unit tests for the module (JUnit, Jest, pytest)",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    "integration-tests": {
        "phase": "test",
        "description": "Integration tests (containers, external services)",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    "coverage": {
        "phase": "test",
        "description": "Test execution with coverage measurement",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    "performance": {
        "phase": "test",
        "description": "Performance/benchmark tests (JMH, k6, wrk)",
        "required": False,
        "applicable_to": ["jar", "quarkus", "npm"],
    },

    # Quality phase
    "quality-gate": {
        "phase": "quality",
        "description": "Static analysis, linting, formatting checks",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "pom", "npm"],
    },

    # Verify phase
    "verify": {
        "phase": "verify",
        "description": "Full verification (compile + test + quality)",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },

    # Deploy phase
    "install": {
        "phase": "deploy",
        "description": "Install artifact to local repository",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "pom"],
    },
    "package": {
        "phase": "deploy",
        "description": "Create deployable artifact (jar, war, native)",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
}


# =============================================================================
# Build System Detection (via Extensions)
# =============================================================================

# Build file indicators for each build system
BUILD_FILE_INDICATORS = {
    "maven": ["pom.xml"],
    "gradle": ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"],
    "npm": ["package.json"],
}


def _build_system_files_exist(project_dir: Path, build_system: str) -> bool:
    """Check if any indicator file for a build system exists in the project."""
    indicators = BUILD_FILE_INDICATORS.get(build_system, [])
    return any((project_dir / f).exists() for f in indicators)


def detect_build_systems(project_dir: Path) -> dict:
    """Detect all available build systems in the project directory using extensions."""
    extensions = discover_extensions(project_dir)
    declared_systems = get_build_systems_from_extensions(extensions)

    # Filter to only build systems with actual files present
    build_systems = [
        bs for bs in declared_systems
        if _build_system_files_exist(project_dir, bs)
    ]

    if not build_systems:
        return {
            "available_systems": "",
            "default_system": "",
            "detected": [],
            "message": "No build systems detected"
        }

    # Build detected list with priority
    priority_order = {"maven": 1, "gradle": 2, "npm": 3}
    detected = [
        {"name": bs, "priority": priority_order.get(bs, 99)}
        for bs in build_systems
    ]
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
# Module Detection (via Extensions)
# =============================================================================

def detect_all_modules(project_dir: Path) -> list:
    """Detect all modules from all build systems via extensions."""
    extensions = discover_extensions(project_dir)
    return get_modules_from_extensions(extensions, project_dir)


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
# Module Type and Profile Detection (via Extensions)
# =============================================================================

def detect_module_type_for_path(module_path: Path, _build_system: str = None) -> str:
    """Detect module type for a given path via extensions."""
    extensions = discover_extensions(module_path)

    for ext in extensions:
        module = ext.get("module")
        if module and hasattr(module, 'get_module_type'):
            try:
                return module.get_module_type(str(module_path))
            except Exception:
                pass

    return "jar"  # Default


def detect_profiles_for_module(module_path: Path, _build_system: str = None) -> list:
    """Detect profiles for a module via extensions."""
    extensions = discover_extensions(module_path)
    profiles = []

    for ext in extensions:
        module = ext.get("module")
        if module and hasattr(module, 'get_profiles'):
            try:
                ext_profiles = module.get_profiles(str(module_path))
                profiles.extend(ext_profiles)
            except Exception:
                pass

    return profiles


def cmd_detect_module_type(args):
    """Handle detect-module-type subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"error: Directory not found: {project_dir}", file=sys.stderr)
        return 1

    # Determine module path
    if args.module and args.module != "default":
        module_path = project_dir / args.module
        if not module_path.exists():
            config = load_marshal_json(project_dir)
            module_config = config.get("modules", {}).get(args.module)
            if module_config:
                module_path = project_dir / module_config.get("path", args.module)
            else:
                print(f"error: Module path not found: {module_path}", file=sys.stderr)
                return 1
    else:
        module_path = project_dir

    module_type = detect_module_type_for_path(module_path, args.build_system)

    print("status: success")
    print(f"module: {args.module or 'default'}")
    print(f"path: {module_path}")
    print(f"type: {module_type}")

    return 0


def cmd_detect_profiles(args):
    """Handle detect-profiles subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"error: Directory not found: {project_dir}", file=sys.stderr)
        return 1

    # Determine module path
    if args.module and args.module != "default":
        module_path = project_dir / args.module
        if not module_path.exists():
            config = load_marshal_json(project_dir)
            module_config = config.get("modules", {}).get(args.module)
            if module_config:
                module_path = project_dir / module_config.get("path", args.module)
            else:
                print(f"error: Module path not found: {module_path}", file=sys.stderr)
                return 1
    else:
        module_path = project_dir

    profiles = detect_profiles_for_module(module_path, args.build_system)

    print("status: success")
    print(f"module: {args.module or 'default'}")
    print(f"path: {module_path}")
    print(f"count: {len(profiles)}")
    print()
    print(f"profiles[{len(profiles)}]" + "{id,canonical,activation_type}:")
    for profile in profiles:
        canonical = profile.get("canonical") or "-"
        activation_type = profile.get("activation", {}).get("type", "command-line")
        print(f"{profile['id']}\t{canonical}\t{activation_type}")

    return 0


# =============================================================================
# Hybrid Module Detection
# =============================================================================

def detect_hybrid_build_systems(module_path: Path) -> list:
    """Detect all build systems present in a module directory."""
    systems = []

    if (module_path / "pom.xml").exists():
        systems.append("maven")
    if (module_path / "build.gradle").exists() or (module_path / "build.gradle.kts").exists():
        systems.append("gradle")
    if (module_path / "package.json").exists():
        systems.append("npm")

    return systems


def is_hybrid_module(module_path: Path) -> bool:
    """Check if a module has multiple build systems."""
    return len(detect_hybrid_build_systems(module_path)) > 1


# =============================================================================
# Command Generation and Persistence
# =============================================================================

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


def generate_commands_from_extensions(
    extension_mappings: dict,
    build_system: str,
    module_type: str,
    module_name: str = None,
    minimal: bool = False
) -> dict:
    """Generate canonical commands from extension mappings."""
    commands = {}

    if build_system not in extension_mappings:
        return commands

    build_mappings = extension_mappings[build_system]

    for canonical, spec in CANONICAL_COMMANDS.items():
        if module_type not in spec["applicable_to"]:
            continue
        if minimal and not spec.get("required", False):
            continue

        cmd_template = build_mappings.get(canonical)
        if cmd_template is None:
            continue

        # Resolve {module} placeholder
        if module_name and module_name != "default":
            if build_system == "npm":
                cmd = cmd_template.replace("{module}", f" --workspace {module_name}")
            else:
                cmd = cmd_template.replace("{module}", f" --module {module_name}")
        else:
            cmd = cmd_template.replace("{module}", "")

        commands[canonical] = cmd

    return commands


def generate_hybrid_commands_from_extensions(
    extension_mappings: dict,
    module_path: Path,
    module_name: str = None
) -> dict:
    """Generate commands for a hybrid module using extension mappings."""
    build_systems = detect_hybrid_build_systems(module_path)
    if len(build_systems) <= 1:
        return {}

    commands = {}

    for build_system in build_systems:
        if build_system not in extension_mappings:
            continue

        mod_type = detect_module_type_for_path(module_path, build_system)
        build_mappings = extension_mappings[build_system]

        for canonical, spec in CANONICAL_COMMANDS.items():
            if mod_type not in spec["applicable_to"]:
                continue

            cmd_template = build_mappings.get(canonical)
            if cmd_template is None:
                continue

            if module_name and module_name != "default":
                if build_system == "npm":
                    cmd = cmd_template.replace("{module}", f" --workspace {module_name}")
                else:
                    cmd = cmd_template.replace("{module}", f" --module {module_name}")
            else:
                cmd = cmd_template.replace("{module}", "")

            if canonical not in commands:
                commands[canonical] = {}
            commands[canonical][build_system] = cmd

    return commands


def generate_profile_command(
    build_system: str,
    canonical: str,
    profile_id: str,
    activation: dict,
    module_name: str = None
) -> str:
    """Generate a command string for a profile-based canonical command."""
    if build_system == "maven":
        if activation.get("type") == "property":
            prop_name = activation.get("property", "")
            prop_value = activation.get("value")
            if prop_value:
                targets = f"clean verify -D{prop_name}={prop_value}"
            else:
                targets = f"clean verify -D{prop_name}"
        else:
            targets = f"clean verify -P{profile_id}"

        cmd = f'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets "{targets}"'
    elif build_system == "gradle":
        cmd = f'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run --targets "clean {profile_id}"'
    else:
        return None

    if module_name and module_name != "default":
        cmd += f" --module {module_name}"

    return cmd


def cmd_persist(args):
    """Handle persist subcommand - detect and persist module commands."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({"status": "error", "message": f"Directory not found: {project_dir}"}, indent=2))
        return 1

    # Parse include_profiles if provided
    include_profiles_set = set()
    if args.include_profiles:
        for pair in args.include_profiles.split(","):
            pair = pair.strip()
            if ":" in pair:
                include_profiles_set.add(pair)

    minimal = getattr(args, 'minimal', False)

    # Discover applicable extensions
    extensions = discover_extensions(project_dir)
    extension_mappings = get_command_mappings_from_extensions(extensions)
    skill_domains = get_skill_domains_from_extensions(extensions)

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

    # Check if default module is hybrid
    default_is_hybrid = is_hybrid_module(project_dir)
    default_build_systems = detect_hybrid_build_systems(project_dir) if default_is_hybrid else [default_system]
    default_type = detect_module_type_for_path(project_dir, default_system)
    default_profiles = detect_profiles_for_module(project_dir, default_system)

    # Configure default module
    if "default" not in config["modules"]:
        config["modules"]["default"] = {"path": ".", "domains": [], "build_systems": default_build_systems}
    else:
        config["modules"]["default"]["build_systems"] = default_build_systems

    config["modules"]["default"]["type"] = default_type

    if default_profiles:
        config["modules"]["default"]["detected_profiles"] = [
            {"id": p["id"], "canonical": p.get("canonical")} for p in default_profiles
        ]

    # Generate commands for default module
    if default_is_hybrid:
        default_commands = generate_hybrid_commands_from_extensions(extension_mappings, project_dir, None)
    else:
        default_commands = generate_commands_from_extensions(
            extension_mappings, default_system, default_type, minimal=minimal
        )
        # Add profile-based commands
        for profile in default_profiles:
            if profile.get("canonical"):
                canonical = profile["canonical"]
                profile_key = f"default:{profile['id']}"
                if minimal and profile_key not in include_profiles_set:
                    continue
                if include_profiles_set and profile_key not in include_profiles_set:
                    continue

                activation = profile.get("activation", {})
                if canonical not in default_commands or activation.get("type") in ("property", "jdk", "os", "default"):
                    cmd = generate_profile_command(default_system, canonical, profile["id"], activation, None)
                    if cmd:
                        default_commands[canonical] = cmd

    config["modules"]["default"]["commands"] = default_commands

    # Generate commands for detected modules
    modules_updated = 1
    commands_generated = len(default_commands)

    for module in modules:
        mod_name = module["name"]
        mod_system = module["build_system"]
        mod_path = project_dir / module["path"]

        mod_is_hybrid = is_hybrid_module(mod_path)
        mod_build_systems = detect_hybrid_build_systems(mod_path) if mod_is_hybrid else [mod_system]
        mod_type = detect_module_type_for_path(mod_path, mod_system)
        mod_profiles = detect_profiles_for_module(mod_path, mod_system)

        if mod_name not in config["modules"]:
            config["modules"][mod_name] = {"path": module["path"], "domains": [], "build_systems": mod_build_systems}
        else:
            config["modules"][mod_name]["build_systems"] = mod_build_systems

        config["modules"][mod_name]["type"] = mod_type

        if mod_profiles:
            config["modules"][mod_name]["detected_profiles"] = [
                {"id": p["id"], "canonical": p.get("canonical")} for p in mod_profiles
            ]

        if mod_is_hybrid:
            mod_commands = generate_hybrid_commands_from_extensions(extension_mappings, mod_path, mod_name)
        else:
            mod_commands = generate_commands_from_extensions(
                extension_mappings, mod_system, mod_type, mod_name, minimal=minimal
            )
            for profile in mod_profiles:
                if profile.get("canonical"):
                    canonical = profile["canonical"]
                    profile_key = f"{mod_name}:{profile['id']}"
                    if minimal and profile_key not in include_profiles_set:
                        continue
                    if include_profiles_set and profile_key not in include_profiles_set:
                        continue

                    activation = profile.get("activation", {})
                    if canonical not in mod_commands or activation.get("type") in ("property", "jdk", "os", "default"):
                        cmd = generate_profile_command(mod_system, canonical, profile["id"], activation, mod_name)
                        if cmd:
                            mod_commands[canonical] = cmd

        config["modules"][mod_name]["commands"] = mod_commands
        modules_updated += 1
        commands_generated += len(mod_commands)

    # Update build_systems section
    build_system_skill_map = {
        "maven": "pm-dev-java:plan-marshall-plugin",
        "gradle": "pm-dev-java:plan-marshall-plugin",
        "npm": "pm-dev-frontend:plan-marshall-plugin"
    }
    config["build_systems"] = [
        {"system": system, "skill": build_system_skill_map.get(system, "plan-marshall:extension-api")}
        for system in available_systems
    ]

    if skill_domains:
        config["detected_domains"] = skill_domains

    if not args.dry_run:
        save_marshal_json(project_dir, config)

    print("status: success")
    print(f"build_systems: {build_result['available_systems']}")
    print(f"modules_updated: {modules_updated}")
    print(f"commands_generated: {commands_generated}")
    print()
    print(f"modules[{modules_updated}]" + "{name,path,type,commands_count}:")
    for mod_name, mod_config in config["modules"].items():
        cmd_count = len(mod_config.get("commands", {}))
        mod_type = mod_config.get("type", "jar")
        print(f"{mod_name}\t{mod_config.get('path', mod_name)}\t{mod_type}\t{cmd_count}")

    return 0


# =============================================================================
# Canonical Lookup API
# =============================================================================

def lookup_command(canonical: str, module: str, config: dict, build_system: str = None) -> str | dict | None:
    """Look up the executable command for a canonical name and module."""
    modules = config.get("modules", {})
    module_config = modules.get(module)

    if not module_config:
        return None

    commands = module_config.get("commands", {})
    command_entry = commands.get(canonical)

    if command_entry is None:
        return None

    if isinstance(command_entry, dict):
        if "command" in command_entry:
            return command_entry["command"]

        if build_system:
            bs_entry = command_entry.get(build_system)
            if bs_entry and isinstance(bs_entry, dict):
                return bs_entry.get("command")
            return bs_entry

        build_systems = module_config.get("build_systems", [])
        if build_systems and any(bs in command_entry for bs in build_systems):
            return command_entry

        return None

    return command_entry


def cmd_lookup(args):
    """Handle lookup subcommand."""
    project_dir = Path(args.project_dir).resolve()
    config = load_marshal_json(project_dir)

    if not config:
        print(f"error: marshal.json not found in {project_dir}/.plan/", file=sys.stderr)
        print("hint: Run '/marshall-steward' to initialize configuration", file=sys.stderr)
        return 1

    result = lookup_command(args.canonical, args.module, config, args.build_system)

    if result is None:
        print(f"error: Command '{args.canonical}' not found for module '{args.module}'", file=sys.stderr)
        module_config = config.get("modules", {}).get(args.module)
        if module_config:
            available = list(module_config.get("commands", {}).keys())
            if available:
                print(f"available: {', '.join(available)}", file=sys.stderr)
        else:
            available_modules = list(config.get("modules", {}).keys())
            print(f"available modules: {', '.join(available_modules)}", file=sys.stderr)
        print("hint: Run '/marshall-steward' to reconfigure", file=sys.stderr)
        return 1

    if isinstance(result, dict):
        print("status: ambiguous")
        print(f"message: Module '{args.module}' has multiple build systems. Specify --build-system.")
        print()
        print("commands{build_system,command}:")
        for bs, cmd in result.items():
            print(f"{bs}\t{cmd}")
        return 1

    print(result)
    return 0


def get_available_commands(module: str, config: dict) -> list:
    """Get list of available canonical command names for a module."""
    modules = config.get("modules", {})
    module_config = modules.get(module)

    if not module_config:
        return []

    commands = module_config.get("commands", {})
    return list(commands.keys())


def cmd_get_available_commands(args):
    """Handle get-available-commands subcommand."""
    project_dir = Path(args.project_dir).resolve()
    config = load_marshal_json(project_dir)

    if not config:
        print(f"error: marshal.json not found in {project_dir}/.plan/", file=sys.stderr)
        print("hint: Run '/marshall-steward' to initialize configuration", file=sys.stderr)
        return 1

    module_config = config.get("modules", {}).get(args.module)
    if not module_config:
        print(f"error: Module '{args.module}' not found", file=sys.stderr)
        available_modules = list(config.get("modules", {}).keys())
        print(f"available modules: {', '.join(available_modules)}", file=sys.stderr)
        return 1

    available = get_available_commands(args.module, config)

    print("status: success")
    print(f"module: {args.module}")
    print(f"count: {len(available)}")
    print()
    print(f"commands[{len(available)}]" + "{name}:")
    for cmd in available:
        print(cmd)

    return 0


def validate_required_commands(module: str, config: dict) -> list:
    """Validate that required commands are configured for a module."""
    modules = config.get("modules", {})
    module_config = modules.get(module)

    if not module_config:
        raise ValueError(f"Module '{module}' not found in configuration")

    module_type = module_config.get("type", "jar")
    commands = module_config.get("commands", {})

    missing = []
    for canonical, spec in CANONICAL_COMMANDS.items():
        if spec["required"] and module_type in spec["applicable_to"]:
            if canonical not in commands:
                missing.append(canonical)

    return missing


def cmd_validate_required(args):
    """Handle validate-required subcommand."""
    project_dir = Path(args.project_dir).resolve()
    config = load_marshal_json(project_dir)

    if not config:
        print(f"error: marshal.json not found in {project_dir}/.plan/", file=sys.stderr)
        print("hint: Run '/marshall-steward' to initialize configuration", file=sys.stderr)
        return 1

    module_config = config.get("modules", {}).get(args.module)
    if not module_config:
        print(f"error: Module '{args.module}' not found", file=sys.stderr)
        available_modules = list(config.get("modules", {}).keys())
        print(f"available modules: {', '.join(available_modules)}", file=sys.stderr)
        return 1

    try:
        missing = validate_required_commands(args.module, config)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    module_type = module_config.get("type", "jar")

    if missing:
        print("status: incomplete")
        print(f"module: {args.module}")
        print(f"module_type: {module_type}")
        print(f"missing_count: {len(missing)}")
        print()
        print(f"missing[{len(missing)}]" + "{name,description}:")
        for cmd in missing:
            desc = CANONICAL_COMMANDS.get(cmd, {}).get("description", "")
            print(f"{cmd}\t{desc}")
        return 1
    else:
        print("status: success")
        print(f"module: {args.module}")
        print(f"module_type: {module_type}")
        print("message: All required commands are configured")
        return 0


# =============================================================================
# CLI Main
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build environment detection and command generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # detect subcommand
    detect_parser = subparsers.add_parser("detect", help="Detect available build systems")
    detect_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    detect_parser.add_argument("--format", choices=["json", "simple"], default="json", help="Output format")
    detect_parser.set_defaults(func=cmd_detect)

    # detect-modules subcommand
    modules_parser = subparsers.add_parser("detect-modules", help="Detect project modules")
    modules_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    modules_parser.set_defaults(func=cmd_detect_modules)

    # persist subcommand
    persist_parser = subparsers.add_parser("persist", help="Generate and persist module commands")
    persist_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    persist_parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Show without saving")
    persist_parser.add_argument("--minimal", dest="minimal", action="store_true", help="Only required commands")
    persist_parser.add_argument("--include-profiles", dest="include_profiles", default=None,
                               help="module:profile-id pairs to include")
    persist_parser.set_defaults(func=cmd_persist)

    # lookup subcommand
    lookup_parser = subparsers.add_parser("lookup", help="Look up canonical command")
    lookup_parser.add_argument("--canonical", required=True, help="Canonical command name")
    lookup_parser.add_argument("--module", required=True, help="Module name")
    lookup_parser.add_argument("--build-system", dest="build_system", help="Build system filter")
    lookup_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    lookup_parser.set_defaults(func=cmd_lookup)

    # get-available-commands subcommand
    available_parser = subparsers.add_parser("get-available-commands", help="List available commands")
    available_parser.add_argument("--module", required=True, help="Module name")
    available_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    available_parser.set_defaults(func=cmd_get_available_commands)

    # validate-required subcommand
    validate_parser = subparsers.add_parser("validate-required", help="Validate required commands")
    validate_parser.add_argument("--module", required=True, help="Module name")
    validate_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    validate_parser.set_defaults(func=cmd_validate_required)

    # detect-module-type subcommand
    type_parser = subparsers.add_parser("detect-module-type", help="Detect module type")
    type_parser.add_argument("--module", help="Module name")
    type_parser.add_argument("--build-system", dest="build_system", help="Build system")
    type_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    type_parser.set_defaults(func=cmd_detect_module_type)

    # detect-profiles subcommand
    profiles_parser = subparsers.add_parser("detect-profiles", help="Detect profiles")
    profiles_parser.add_argument("--module", help="Module name")
    profiles_parser.add_argument("--build-system", dest="build_system", help="Build system")
    profiles_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    profiles_parser.set_defaults(func=cmd_detect_profiles)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
