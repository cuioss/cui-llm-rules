#!/usr/bin/env python3
"""Client command handlers for architecture script.

Handles: info, modules, module, commands, resolve
These commands merge derived + enriched data for consumer output.
"""

import sys

from _architecture_core import (
    DataNotFoundError,
    ModuleNotFoundError,
    get_derived_path,
    load_derived_data,
    load_llm_enriched_or_empty,
    get_module_names,
    get_root_module,
    get_module,
    merge_module_data,
    print_toon_kv,
    print_toon_table,
    print_toon_list,
    error_data_not_found,
    error_module_not_found,
    error_command_not_found,
)


# =============================================================================
# API Functions
# =============================================================================

def get_project_info(project_dir: str = '.') -> dict:
    """Get project summary with metadata and module overview.

    Args:
        project_dir: Project directory path

    Returns:
        Dict with project info, technologies, and module overview
    """
    derived = load_derived_data(project_dir)
    enriched = load_llm_enriched_or_empty(project_dir)

    project = derived.get("project", {})
    enriched_project = enriched.get("project", {})

    # Collect unique build systems
    technologies = set()
    modules_data = derived.get("modules", {})
    for module in modules_data.values():
        for bs in module.get("build_systems", []):
            technologies.add(bs)

    # Build module overview with enriched purpose
    module_overview = []
    enriched_modules = enriched.get("modules", {})
    for name, data in modules_data.items():
        paths = data.get("paths", {})
        enriched_module = enriched_modules.get(name, {})
        module_overview.append({
            "name": name,
            "path": paths.get("module", ""),
            "purpose": enriched_module.get("purpose", "")
        })

    return {
        "project": {
            "name": project.get("name", ""),
            "description": enriched_project.get("description", ""),
            "root": project.get("root", "")
        },
        "technologies": sorted(technologies),
        "modules": module_overview
    }


def get_modules_list(project_dir: str = '.') -> list:
    """Get list of module names.

    Args:
        project_dir: Project directory path

    Returns:
        List of module names
    """
    derived = load_derived_data(project_dir)
    return get_module_names(derived)


def get_modules_with_command(command_name: str, project_dir: str = '.') -> list:
    """Get list of module names that provide a specific command.

    Args:
        command_name: Command name to filter by
        project_dir: Project directory path

    Returns:
        List of module names that have the specified command
    """
    derived = load_derived_data(project_dir)
    modules_with_command = []

    for module_name, module_data in derived.get("modules", {}).items():
        commands = module_data.get("commands", {})
        if command_name in commands:
            modules_with_command.append(module_name)

    return modules_with_command


def get_module_info(module_name: str = None, full: bool = False, project_dir: str = '.') -> dict:
    """Get module information merged from derived + enriched data.

    Args:
        module_name: Module name (None for root module)
        full: Include all fields (packages, dependencies, reasoning)
        project_dir: Project directory path

    Returns:
        Merged module data dict
    """
    derived = load_derived_data(project_dir)
    enriched = load_llm_enriched_or_empty(project_dir)

    # Default to root module
    if not module_name:
        module_name = get_root_module(derived)
        if not module_name:
            raise ModuleNotFoundError("No modules found", [])

    # Merge data
    merged = merge_module_data(derived, enriched, module_name)

    # Filter fields based on full flag
    if not full:
        # Remove reasoning fields and full package/dependency lists
        reasoning_fields = [
            'responsibility_reasoning',
            'purpose_reasoning',
            'key_dependencies_reasoning',
            'proposed_skill_domains_reasoning'
        ]
        for field in reasoning_fields:
            merged.pop(field, None)

        # Keep only key_packages, not all packages
        merged.pop('packages', None)

        # Keep only key_dependencies (already in enriched)
        merged.pop('dependencies', None)

    return merged


def get_module_commands(module_name: str = None, project_dir: str = '.') -> dict:
    """Get available commands for a module.

    Args:
        module_name: Module name (None for root module)
        project_dir: Project directory path

    Returns:
        Dict with module name and commands list
    """
    derived = load_derived_data(project_dir)

    # Default to root module
    if not module_name:
        module_name = get_root_module(derived)
        if not module_name:
            raise ModuleNotFoundError("No modules found", [])

    module = get_module(derived, module_name)
    commands = module.get("commands", {})

    # Build command list with descriptions
    command_list = []
    for cmd_name, cmd_data in commands.items():
        description = ""
        if isinstance(cmd_data, dict):
            description = cmd_data.get("description", "")
        command_list.append({
            "name": cmd_name,
            "description": description
        })

    return {
        "module": module_name,
        "commands": command_list
    }


def resolve_command(command_name: str, module_name: str = None, project_dir: str = '.') -> dict:
    """Resolve command to executable form.

    Args:
        command_name: Command name to resolve
        module_name: Module name (None for root module)
        project_dir: Project directory path

    Returns:
        Dict with module, command, and executable(s)
    """
    derived = load_derived_data(project_dir)

    # Default to root module
    if not module_name:
        module_name = get_root_module(derived)
        if not module_name:
            raise ModuleNotFoundError("No modules found", [])

    module = get_module(derived, module_name)
    commands = module.get("commands", {})

    if command_name not in commands:
        available = list(commands.keys())
        raise ValueError(f"Command not found: {command_name}")

    cmd_data = commands[command_name]

    # Check if hybrid (multiple build systems provide same command)
    if isinstance(cmd_data, dict) and not cmd_data.get("executable"):
        # Nested by build system
        executables = []
        for build_system, executable in cmd_data.items():
            if build_system != "description":
                executables.append({
                    "build_system": build_system,
                    "command": executable
                })
        return {
            "module": module_name,
            "command": command_name,
            "executables": executables
        }
    else:
        # Single executable
        executable = cmd_data if isinstance(cmd_data, str) else cmd_data.get("executable", "")
        return {
            "module": module_name,
            "command": command_name,
            "executable": executable
        }


# =============================================================================
# CLI Handlers
# =============================================================================

def cmd_info(args) -> int:
    """CLI handler for info command."""
    try:
        info = get_project_info(args.project_dir)

        # Output project info
        print("project:")
        print(f"  name: {info['project']['name']}")
        print(f"  description: {info['project']['description']}")
        print(f"  root: {info['project']['root']}")
        print()

        # Output technologies
        print_toon_list("technologies", info['technologies'])
        print()

        # Output modules table
        print_toon_table("modules", info['modules'], ["name", "path", "purpose"])

        return 0
    except DataNotFoundError:
        error_data_not_found(
            str(get_derived_path(args.project_dir)),
            "Run 'architecture.py discover' first"
        )
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_modules(args) -> int:
    """CLI handler for modules command."""
    try:
        command_filter = getattr(args, 'command', None)

        if command_filter:
            # Filter modules by command availability
            modules = get_modules_with_command(command_filter, args.project_dir)
            print(f"command: {command_filter}")
            print()
        else:
            # List all modules
            modules = get_modules_list(args.project_dir)

        print_toon_list("modules", modules)
        return 0
    except DataNotFoundError:
        error_data_not_found(
            str(get_derived_path(args.project_dir)),
            "Run 'architecture.py discover' first"
        )
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_module(args) -> int:
    """CLI handler for module command."""
    try:
        derived = load_derived_data(args.project_dir)
        module_name = args.name or get_root_module(derived)

        module = get_module_info(module_name, args.full, args.project_dir)

        # Output module info
        print("module:")
        print(f"  name: {module.get('name', module_name)}")
        if module.get('responsibility'):
            print(f"  responsibility: {module['responsibility']}")
        if args.full and module.get('responsibility_reasoning'):
            print(f"  responsibility_reasoning: {module['responsibility_reasoning']}")
        if module.get('purpose'):
            print(f"  purpose: {module['purpose']}")
        if args.full and module.get('purpose_reasoning'):
            print(f"  purpose_reasoning: {module['purpose_reasoning']}")
        paths = module.get("paths", {})
        print(f"  path: {paths.get('module', '')}")
        print()

        # Output paths
        print("paths:")
        sources = paths.get("sources", [])
        if sources:
            print(f"  sources[{len(sources)}]:")
            for s in sources:
                print(f"    - {s}")
        tests = paths.get("tests", [])
        if tests:
            print(f"  tests[{len(tests)}]:")
            for t in tests:
                print(f"    - {t}")
        if paths.get("descriptor"):
            print(f"  descriptor: {paths['descriptor']}")
        print()

        # Output key_packages
        key_packages = module.get("key_packages", {})
        if key_packages:
            pkg_items = []
            for pkg_name, pkg_data in key_packages.items():
                desc = pkg_data.get("description", "") if isinstance(pkg_data, dict) else ""
                pkg_items.append({"name": pkg_name, "description": desc})
            print_toon_table("key_packages", pkg_items, ["name", "description"])
            print()

        # Full mode: all packages
        if args.full:
            packages = module.get("packages", {})
            if packages:
                pkg_items = []
                for pkg_name, pkg_data in packages.items():
                    has_info = "true" if pkg_data.get("package_info") else "false"
                    pkg_items.append({
                        "name": pkg_name,
                        "path": pkg_data.get("path", ""),
                        "has_package_info": has_info
                    })
                print_toon_table("packages", pkg_items, ["name", "path", "has_package_info"])
                print()

        # Output key_dependencies
        key_deps = module.get("key_dependencies", [])
        if key_deps:
            print_toon_list("key_dependencies", key_deps)
        if args.full and module.get('key_dependencies_reasoning'):
            print(f"key_dependencies_reasoning: {module['key_dependencies_reasoning']}")
        print()

        # Full mode: all dependencies
        if args.full:
            deps = module.get("dependencies", [])
            if deps:
                dep_items = []
                for dep in deps[:30]:  # Limit display
                    parts = dep.split(":")
                    if len(parts) >= 3:
                        dep_items.append({
                            "artifact": f"{parts[0]}:{parts[1]}",
                            "scope": parts[2] if len(parts) > 2 else ""
                        })
                print_toon_table("dependencies", dep_items, ["artifact", "scope"])
                if len(deps) > 30:
                    print(f"  ... and {len(deps) - 30} more")
                print()

        # Output internal_dependencies
        internal_deps = module.get("internal_dependencies", [])
        print_toon_list("internal_dependencies", internal_deps)
        print()

        # Output proposed_skill_domains (backward compatible flat list)
        domains = module.get("proposed_skill_domains", [])
        if domains:
            print_toon_list("proposed_skill_domains", domains)
        if args.full and module.get('proposed_skill_domains_reasoning'):
            print(f"proposed_skill_domains_reasoning: {module['proposed_skill_domains_reasoning']}")
        print()

        # Output skills_by_profile (new profile-keyed format)
        skills_by_profile = module.get("skills_by_profile", {})
        if skills_by_profile:
            print("skills_by_profile:")
            for profile, skills in skills_by_profile.items():
                print(f"  {profile}:")
                for skill in skills:
                    print(f"    - {skill}")
        if args.full and module.get('skills_by_profile_reasoning'):
            print(f"skills_by_profile_reasoning: {module['skills_by_profile_reasoning']}")
        print()

        # Output commands
        commands = module.get("commands", {})
        if commands:
            print_toon_list("commands", list(commands.keys()))

        return 0
    except DataNotFoundError:
        error_data_not_found(
            str(get_derived_path(args.project_dir)),
            "Run 'architecture.py discover' first"
        )
    except ModuleNotFoundError:
        modules = get_modules_list(args.project_dir)
        error_module_not_found(args.name, modules)
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_commands(args) -> int:
    """CLI handler for commands command."""
    try:
        result = get_module_commands(args.name, args.project_dir)

        print(f"module: {result['module']}")
        print()
        print_toon_table("commands", result['commands'], ["name", "description"])

        return 0
    except DataNotFoundError:
        error_data_not_found(
            str(get_derived_path(args.project_dir)),
            "Run 'architecture.py discover' first"
        )
    except ModuleNotFoundError:
        modules = get_modules_list(args.project_dir)
        error_module_not_found(args.name, modules)
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_resolve(args) -> int:
    """CLI handler for resolve command."""
    try:
        result = resolve_command(args.command, args.name, args.project_dir)

        print(f"module: {result['module']}")
        print(f"command: {result['command']}")

        if 'executable' in result:
            print(f"executable: {result['executable']}")
        elif 'executables' in result:
            print()
            print_toon_table(
                "executables",
                result['executables'],
                ["build_system", "command"]
            )

        return 0
    except DataNotFoundError:
        error_data_not_found(
            str(get_derived_path(args.project_dir)),
            "Run 'architecture.py discover' first"
        )
    except ModuleNotFoundError:
        modules = get_modules_list(args.project_dir)
        error_module_not_found(args.name, modules)
    except ValueError:
        # Command not found
        derived = load_derived_data(args.project_dir)
        module_name = args.name or get_root_module(derived)
        module = get_module(derived, module_name)
        commands = list(module.get("commands", {}).keys())
        error_command_not_found(module_name, args.command, commands)
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1
