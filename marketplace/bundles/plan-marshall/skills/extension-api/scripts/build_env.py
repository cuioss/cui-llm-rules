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
import os
import subprocess
import sys
from pathlib import Path

# Import from extension module (same directory)
from extension import (
    discover_extensions,
    get_build_systems_from_extensions,
    get_command_mappings_from_extensions,
    get_modules_from_extensions,
    generate_profile_command_from_extensions,
)
from extension_base import (
    CANONICAL_COMMANDS,
    CMD_INTEGRATION_TESTS,
    CMD_COVERAGE,
    CMD_PERFORMANCE,
    CMD_QUALITY_GATE,
)


# =============================================================================
# Profile Mapping Integration (from run-config)
# =============================================================================

def load_profile_mappings(project_dir: Path) -> dict:
    """Load profile mappings from run-configuration.json.

    Returns dict of profile_id -> canonical (or 'skip').
    """
    run_config_path = project_dir / ".plan" / "run-configuration.json"
    if not run_config_path.exists():
        return {}
    try:
        config = json.loads(run_config_path.read_text())
        return config.get('profile_mappings', {})
    except (json.JSONDecodeError, IOError):
        return {}


def apply_profile_mappings(profiles: list, mappings: dict) -> list:
    """Apply user-defined profile mappings to detected profiles.

    For each profile:
    - If profile_id is in mappings with 'skip', remove from list
    - If profile_id is in mappings with a canonical, override the canonical
    - If profile_id is not in mappings, keep original detection

    Returns modified profiles list.
    """
    result = []
    for profile in profiles:
        profile_id = profile.get('id')
        if profile_id in mappings:
            mapping = mappings[profile_id]
            if mapping == 'skip':
                # User said to skip this profile - don't include it
                continue
            else:
                # User mapped this profile to a specific canonical
                profile = profile.copy()
                profile['canonical'] = mapping
        result.append(profile)
    return result


def get_unmapped_profiles(profiles: list, mappings: dict) -> list:
    """Get profiles that have no auto-classification AND no user mapping.

    These are profiles that need user decision.
    """
    unmapped = []
    for profile in profiles:
        profile_id = profile.get('id')
        # If already in mappings, user has decided
        if profile_id in mappings:
            continue
        # If auto-classified, no user decision needed
        if profile.get('canonical'):
            continue
        # Needs user decision
        unmapped.append(profile)
    return unmapped

# Canonical commands that require profile detection (not provided by static get_command_mappings)
PROFILE_BASED_CANONICALS = {CMD_INTEGRATION_TESTS, CMD_COVERAGE, CMD_PERFORMANCE, CMD_QUALITY_GATE}


# =============================================================================
# Build System Detection (via Extensions)
# =============================================================================

def detect_build_systems(project_dir: Path) -> dict:
    """Detect all available build systems in the project directory using extensions.

    Extensions are discovered via is_applicable() which checks for build files.
    Then get_applicable_build_systems() returns only systems with files present.
    """
    extensions = discover_extensions(project_dir)
    # Pass project_dir to enable dynamic detection via get_applicable_build_systems()
    build_systems = get_build_systems_from_extensions(extensions, project_dir)

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

def detect_module_type_for_path(module_path: Path) -> str:
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


def detect_profiles_for_module(module_path: Path) -> list:
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
            module_config = config.get("module_config", {}).get(args.module)
            if module_config:
                module_path = project_dir / module_config.get("path", args.module)
            else:
                print(f"error: Module path not found: {module_path}", file=sys.stderr)
                return 1
    else:
        module_path = project_dir

    module_type = detect_module_type_for_path(module_path)

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
            module_config = config.get("module_config", {}).get(args.module)
            if module_config:
                module_path = project_dir / module_config.get("path", args.module)
            else:
                print(f"error: Module path not found: {module_path}", file=sys.stderr)
                return 1
    else:
        module_path = project_dir

    profiles = detect_profiles_for_module(module_path)

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
    """Detect all build systems present in a module directory via extensions.

    Uses extension discovery to find applicable build systems.
    Each extension's get_applicable_build_systems() checks for its build files.
    """
    extensions = discover_extensions(module_path)
    return get_build_systems_from_extensions(extensions, module_path)


# =============================================================================
# Profile Analysis
# =============================================================================

def analyze_profile_coverage(profiles: list, module_type: str) -> dict:
    """Analyze which profile-based canonicals are covered and which are missing.

    Args:
        profiles: List of profile dicts with 'id', 'canonical', 'activation'
        module_type: Module type (jar, war, quarkus, etc.) for applicability check

    Returns:
        Dict with:
        - matched: {canonical: profile_info} - profiles that matched a canonical
        - unclassified: [profile_info] - profiles that couldn't be classified
        - missing: [canonical] - profile-based canonicals with no matching profile
    """
    matched = {}
    unclassified = []

    for profile in profiles:
        canonical = profile.get("canonical")
        if canonical:
            # If multiple profiles match same canonical, first wins
            if canonical not in matched:
                matched[canonical] = {
                    "id": profile["id"],
                    "activation": profile.get("activation", {"type": "command-line"})
                }
        else:
            unclassified.append({
                "id": profile["id"],
                "activation": profile.get("activation", {"type": "command-line"})
            })

    # Determine which profile-based canonicals are missing
    missing = []
    for canonical in PROFILE_BASED_CANONICALS:
        spec = CANONICAL_COMMANDS.get(canonical, {})
        # Only report missing if applicable to this module type
        if module_type in spec.get("applicable_to", []):
            if canonical not in matched:
                missing.append(canonical)

    return {
        "matched": matched,
        "unclassified": unclassified,
        "missing": missing
    }


# =============================================================================
# Command Generation and Persistence
# =============================================================================

def load_marshal_json(project_dir: Path) -> dict:
    """Load marshal.json from .plan directory."""
    marshal_path = project_dir / ".plan" / "marshal.json"
    if marshal_path.exists():
        return json.loads(marshal_path.read_text())
    return {}


def load_modules_from_raw_data(project_dir: Path) -> list:
    """Load modules from raw-project-data.json (single source of truth).

    Returns list of module dicts with: name, path, build_systems, packaging.
    Returns empty list if raw-project-data.json doesn't exist.
    """
    raw_data_path = project_dir / ".plan" / "raw-project-data.json"
    if not raw_data_path.exists():
        return []
    try:
        raw_data = json.loads(raw_data_path.read_text())
        return raw_data.get('modules', [])
    except (json.JSONDecodeError, IOError):
        return []


def get_default_build_systems_from_raw_data(project_dir: Path) -> list:
    """Get default build systems from raw-project-data.json.

    The 'default' module build systems are stored separately since they
    represent the root project build systems.
    """
    raw_data_path = project_dir / ".plan" / "raw-project-data.json"
    if not raw_data_path.exists():
        return []
    try:
        raw_data = json.loads(raw_data_path.read_text())
        # Check for explicit default_build_systems first (set by collect-raw-data)
        if 'default_build_systems' in raw_data:
            return raw_data['default_build_systems']
        # Fall back to detecting from root project files
        return []
    except (json.JSONDecodeError, IOError):
        return []


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

        mod_type = detect_module_type_for_path(module_path)
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

    # Load user-defined profile mappings from run-configuration.json
    profile_mappings = load_profile_mappings(project_dir)

    # Discover applicable extensions
    extensions = discover_extensions(project_dir)
    extension_mappings = get_command_mappings_from_extensions(extensions)

    # Detect build systems
    build_result = detect_build_systems(project_dir)
    if not build_result["available_systems"]:
        print("status: error")
        print("message: No build systems detected")
        return 1

    default_system = build_result["default_system"]

    # Load modules from raw-project-data.json (single source of truth)
    modules = load_modules_from_raw_data(project_dir)

    # Load existing config
    config = load_marshal_json(project_dir)
    if "module_config" not in config:
        config["module_config"] = {}

    # Detect build systems for default module (may be hybrid with multiple systems)
    default_build_systems = detect_hybrid_build_systems(project_dir)
    if not default_build_systems:
        default_build_systems = [default_system]
    default_is_hybrid = len(default_build_systems) > 1
    default_type = detect_module_type_for_path(project_dir)
    default_profiles_raw = detect_profiles_for_module(project_dir)

    # Apply user-defined profile mappings to detected profiles
    default_profiles = apply_profile_mappings(default_profiles_raw, profile_mappings)

    # Configure default module
    if "default" not in config["module_config"]:
        config["module_config"]["default"] = {"path": ".", "domains": [], "build_systems": default_build_systems}
    else:
        config["module_config"]["default"]["build_systems"] = default_build_systems

    config["module_config"]["default"]["type"] = default_type

    # Analyze profile coverage for default module (using mapped profiles)
    default_profile_analysis = analyze_profile_coverage(default_profiles, default_type)

    # Clean up any old diagnostic fields from marshal.json (no longer stored there)
    for field in ["detected_profiles", "unclassified_profiles", "missing_profile_commands"]:
        config["module_config"]["default"].pop(field, None)

    # Generate commands for default module
    if default_is_hybrid:
        default_commands = generate_hybrid_commands_from_extensions(extension_mappings, project_dir, None)
    else:
        default_commands = generate_commands_from_extensions(
            extension_mappings, default_system, default_type, minimal=minimal
        )
        # Add profile-based commands from detected profiles
        for canonical, profile_info in default_profile_analysis["matched"].items():
            profile_key = f"default:{profile_info['id']}"
            if minimal and profile_key not in include_profiles_set:
                continue
            if include_profiles_set and profile_key not in include_profiles_set:
                continue

            cmd = generate_profile_command_from_extensions(
                extensions, default_system, canonical, profile_info["id"],
                profile_info["activation"], None
            )
            if cmd:
                default_commands[canonical] = cmd

    config["module_config"]["default"]["commands"] = default_commands

    # Generate commands for detected modules
    modules_updated = 1
    commands_generated = len(default_commands)

    # Track profiles needing user decision (not stored in marshal.json, just reported)
    all_unmapped_profiles = []
    unmapped_default = get_unmapped_profiles(default_profiles_raw, profile_mappings)
    for p in unmapped_default:
        all_unmapped_profiles.append({"module": "default", "profile_id": p["id"]})

    for module in modules:
        mod_name = module["name"]
        # raw-project-data.json uses build_systems (array)
        mod_build_systems = module.get("build_systems", [])
        mod_system = mod_build_systems[0] if mod_build_systems else default_system
        mod_path = project_dir / module["path"]

        mod_is_hybrid = len(mod_build_systems) > 1
        mod_type = detect_module_type_for_path(mod_path)
        mod_profiles_raw = detect_profiles_for_module(mod_path)

        # Apply user-defined profile mappings
        mod_profiles = apply_profile_mappings(mod_profiles_raw, profile_mappings)

        if mod_name not in config["module_config"]:
            config["module_config"][mod_name] = {"path": module["path"], "domains": [], "build_systems": mod_build_systems}
        else:
            config["module_config"][mod_name]["build_systems"] = mod_build_systems

        config["module_config"][mod_name]["type"] = mod_type

        # Analyze profile coverage for this module (using mapped profiles)
        mod_profile_analysis = analyze_profile_coverage(mod_profiles, mod_type)

        # Clean up any old diagnostic fields from marshal.json
        for field in ["detected_profiles", "unclassified_profiles", "missing_profile_commands"]:
            config["module_config"][mod_name].pop(field, None)

        # Track unmapped profiles for reporting
        unmapped_mod = get_unmapped_profiles(mod_profiles_raw, profile_mappings)
        for p in unmapped_mod:
            all_unmapped_profiles.append({"module": mod_name, "profile_id": p["id"]})

        if mod_is_hybrid:
            mod_commands = generate_hybrid_commands_from_extensions(extension_mappings, mod_path, mod_name)
        else:
            mod_commands = generate_commands_from_extensions(
                extension_mappings, mod_system, mod_type, mod_name, minimal=minimal
            )
            # Add profile-based commands from detected profiles
            for canonical, profile_info in mod_profile_analysis["matched"].items():
                profile_key = f"{mod_name}:{profile_info['id']}"
                if minimal and profile_key not in include_profiles_set:
                    continue
                if include_profiles_set and profile_key not in include_profiles_set:
                    continue

                cmd = generate_profile_command_from_extensions(
                    extensions, mod_system, canonical, profile_info["id"],
                    profile_info["activation"], mod_name
                )
                if cmd:
                    mod_commands[canonical] = cmd

        config["module_config"][mod_name]["commands"] = mod_commands
        modules_updated += 1
        commands_generated += len(mod_commands)

    if not args.dry_run:
        # Delegate to plan-marshall-config for centralized marshal.json writes
        config_script = Path(__file__).parent.parent.parent / "plan-marshall-config" / "scripts" / "plan-marshall-config.py"

        cmd = [
            "python3", str(config_script),
            "modules", "persist-all",
            "--modules-json", json.dumps(config["module_config"])
        ]

        # Set PLAN_BASE_DIR to project's .plan directory
        env = os.environ.copy()
        env["PLAN_BASE_DIR"] = str(project_dir / ".plan")

        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
        if result.returncode != 0:
            print(f"error: Failed to persist modules: {result.stderr or result.stdout}", file=sys.stderr)
            return 1

    print("status: success")
    print(f"build_systems: {build_result['available_systems']}")
    print(f"modules_updated: {modules_updated}")
    print(f"commands_generated: {commands_generated}")
    print(f"profile_mappings_applied: {len(profile_mappings)}")
    print()
    print(f"modules[{modules_updated}]" + "{name,path,type,commands_count}:")
    for mod_name, mod_config in config["module_config"].items():
        cmd_count = len(mod_config.get("commands", {}))
        mod_type = mod_config.get("type", "jar")
        print(f"{mod_name}\t{mod_config.get('path', mod_name)}\t{mod_type}\t{cmd_count}")

    # Report profiles needing user decision (not stored in marshal.json)
    if all_unmapped_profiles:
        print()
        print(f"unmapped_profiles[{len(all_unmapped_profiles)}]" + "{module,profile_id}:")
        for item in all_unmapped_profiles:
            print(f"{item['module']}\t{item['profile_id']}")
        print()
        print("hint: Use 'run_config profile-mapping set --profile-id <id> --canonical <canonical|skip>'")
        print("      to resolve unmapped profiles, then re-run persist")

    return 0


# =============================================================================
# Canonical Lookup API
# =============================================================================

def lookup_command(canonical: str, module: str, config: dict, build_system: str = None) -> str | dict | None:
    """Look up the executable command for a canonical name and module."""
    modules = config.get("module_config", {})
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
        module_config = config.get("module_config", {}).get(args.module)
        if module_config:
            available = list(module_config.get("commands", {}).keys())
            if available:
                print(f"available: {', '.join(available)}", file=sys.stderr)
        else:
            available_modules = list(config.get("module_config", {}).keys())
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
    modules = config.get("module_config", {})
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

    module_config = config.get("module_config", {}).get(args.module)
    if not module_config:
        print(f"error: Module '{args.module}' not found", file=sys.stderr)
        available_modules = list(config.get("module_config", {}).keys())
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
    """Validate that required commands are configured for a module.

    Only validates static (non-profile-based) required commands.
    Profile-based commands (integration-tests, coverage, performance, quality-gate)
    are generated from detected profiles and are not strictly required.
    """
    modules = config.get("module_config", {})
    module_config = modules.get(module)

    if not module_config:
        raise ValueError(f"Module '{module}' not found in configuration")

    module_type = module_config.get("type", "jar")
    commands = module_config.get("commands", {})

    missing = []
    for canonical, spec in CANONICAL_COMMANDS.items():
        # Skip profile-based canonicals - they're generated from detected profiles
        if canonical in PROFILE_BASED_CANONICALS:
            continue
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

    module_config = config.get("module_config", {}).get(args.module)
    if not module_config:
        print(f"error: Module '{args.module}' not found", file=sys.stderr)
        available_modules = list(config.get("module_config", {}).keys())
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
