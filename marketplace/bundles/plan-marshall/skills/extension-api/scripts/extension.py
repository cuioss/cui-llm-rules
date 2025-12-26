#!/usr/bin/env python3
"""
Extension discovery and API utilities.

Single source of truth for discovering and loading extension.py files
from domain bundles. Used by extension-api and plan-marshall-config.

Usage:
    extension.py list [--project-dir <dir>]
    extension.py list-all
    extension.py get-build-systems --project-dir <dir>
    extension.py get-command-mappings --project-dir <dir>
    extension.py get-skill-domains [--project-dir <dir>]
    extension.py --help

Subcommands:
    list              List applicable extensions for a project
    list-all          List all available extensions (no applicability check)
    get-build-systems Get build systems from applicable extensions
    get-command-mappings Get command mappings from applicable extensions
    get-skill-domains Get skill domains from all extensions
"""

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


def get_plugin_cache_path() -> Path:
    """Get the plugin cache path from environment or default."""
    env_path = os.environ.get("PLUGIN_CACHE_PATH")
    if env_path:
        return Path(env_path)
    return Path.home() / ".claude" / "plugins" / "cache" / "plan-marshall"


def get_marketplace_bundles_path() -> Path:
    """Get the path to marketplace bundles directory.

    Searches for marketplace bundles in:
    1. Source: marketplace/bundles relative to script (development)
    2. Cache: ~/.claude/plugins/cache/plan-marshall (installed)

    Returns:
        Path to bundles directory
    """
    script_path = Path(__file__).resolve()

    # Walk up from script location to find bundles directory
    current = script_path.parent
    for _ in range(10):  # Safety limit
        candidate = current / "bundles"
        if candidate.is_dir() and (candidate / "plan-marshall").is_dir():
            return candidate
        if current.name == "bundles" and (current / "plan-marshall").is_dir():
            return current
        current = current.parent
        if current == current.parent:
            break

    # Fallback: check plugin cache
    cache_path = get_plugin_cache_path()
    if cache_path.is_dir():
        return cache_path

    return script_path.parent.parent.parent.parent.parent / "bundles"


def load_extension_module(extension_path: Path, bundle_name: str):
    """Load an extension.py module dynamically.

    Args:
        extension_path: Path to extension.py file
        bundle_name: Name of the bundle for module naming

    Returns:
        Loaded module or None if failed
    """
    try:
        spec = importlib.util.spec_from_file_location(
            f"extension_{bundle_name}",
            extension_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Warning: Failed to load extension from {bundle_name}: {e}", file=sys.stderr)
        return None


def find_extension_path(bundle_dir: Path) -> Path | None:
    """Find extension.py path in a bundle directory.

    Handles both source and cache structures:
    - Source: bundles/{bundle}/skills/plan-marshall-plugin/extension.py
    - Cache: {cache}/{bundle}/skills/plan-marshall-plugin/extension.py
    - Cache versioned: {cache}/{bundle}/1.0.0/skills/plan-marshall-plugin/extension.py

    Args:
        bundle_dir: Path to the bundle directory

    Returns:
        Path to extension.py or None if not found
    """
    # Try direct path first (source structure)
    extension_path = bundle_dir / "skills" / "plan-marshall-plugin" / "extension.py"
    if extension_path.exists():
        return extension_path

    # Try versioned path (cache structure from rsync)
    for version_dir in bundle_dir.iterdir():
        if version_dir.is_dir() and not version_dir.name.startswith('.'):
            versioned_path = version_dir / "skills" / "plan-marshall-plugin" / "extension.py"
            if versioned_path.exists():
                return versioned_path

    return None


def discover_all_extensions() -> list:
    """Discover all extension.py files in bundles (no applicability check).

    Scans all bundles for extension.py files in skills/plan-marshall-plugin/

    Returns:
        List of dicts with extension info: {bundle, path, module}
    """
    extensions = []
    bundles_path = get_marketplace_bundles_path()

    if not bundles_path.is_dir():
        return extensions

    for bundle_dir in bundles_path.iterdir():
        if not bundle_dir.is_dir() or bundle_dir.name.startswith('.'):
            continue

        extension_path = find_extension_path(bundle_dir)
        if not extension_path:
            continue

        module = load_extension_module(extension_path, bundle_dir.name)
        if module:
            extensions.append({
                "bundle": bundle_dir.name,
                "path": str(extension_path),
                "module": module
            })

    return extensions


def discover_extensions(project_root: Path) -> list:
    """Discover applicable extensions for a project.

    Scans all bundles for extension.py files and calls is_applicable()
    to determine which apply to the given project.

    Args:
        project_root: Path to the project root

    Returns:
        List of dicts with extension info: {bundle, path, module}
    """
    all_extensions = discover_all_extensions()
    applicable = []

    for ext in all_extensions:
        module = ext.get("module")
        if module and hasattr(module, 'is_applicable'):
            try:
                if module.is_applicable(str(project_root)):
                    applicable.append(ext)
            except Exception as e:
                print(f"Warning: is_applicable() failed for {ext['bundle']}: {e}", file=sys.stderr)

    return applicable


def get_build_systems_from_extensions(extensions: list, project_root: Path = None) -> list:
    """Get build systems provided by extensions.

    Args:
        extensions: List of extension info dicts from discover_extensions()
        project_root: Optional project root for dynamic detection.
                     If provided, uses get_applicable_build_systems().
                     If not, uses static provides_build_systems().

    Returns:
        List of build system names (e.g., ["maven", "gradle", "npm"])
    """
    build_systems = set()

    for ext in extensions:
        module = ext.get("module")
        if not module:
            continue

        try:
            # Prefer dynamic detection if project_root provided and function exists
            if project_root and hasattr(module, 'get_applicable_build_systems'):
                systems = module.get_applicable_build_systems(str(project_root))
            elif hasattr(module, 'provides_build_systems'):
                systems = module.provides_build_systems()
            else:
                continue

            build_systems.update(systems)
        except Exception as e:
            print(f"Warning: build system detection failed for {ext['bundle']}: {e}", file=sys.stderr)

    return list(build_systems)


def get_command_mappings_from_extensions(extensions: list) -> dict:
    """Get command mappings from extensions.

    Args:
        extensions: List of extension info dicts from discover_extensions()

    Returns:
        Dict of {build_system: {canonical: command_template}}
    """
    mappings = {}

    for ext in extensions:
        module = ext.get("module")
        if module and hasattr(module, 'get_command_mappings'):
            try:
                ext_mappings = module.get_command_mappings()
                for build_system, commands in ext_mappings.items():
                    if build_system not in mappings:
                        mappings[build_system] = {}
                    mappings[build_system].update(commands)
            except Exception as e:
                print(f"Warning: get_command_mappings() failed for {ext['bundle']}: {e}", file=sys.stderr)

    return mappings


def get_skill_domains_from_extensions(extensions: list) -> list:
    """Get skill domains from extensions.

    Args:
        extensions: List of extension info dicts

    Returns:
        List of domain info dicts: {domain, profiles, bundle}
    """
    domains = []

    for ext in extensions:
        module = ext.get("module")
        if module and hasattr(module, 'get_skill_domains'):
            try:
                domain_info = module.get_skill_domains()
                if domain_info and domain_info.get("domain"):
                    domain_info["bundle"] = ext["bundle"]
                    domains.append(domain_info)
            except Exception as e:
                print(f"Warning: get_skill_domains() failed for {ext['bundle']}: {e}", file=sys.stderr)

    return domains


def get_domain_supplements_from_extensions(extensions: list) -> list:
    """Get domain supplements from extensions.

    Args:
        extensions: List of extension info dicts

    Returns:
        List of supplement info dicts: {domain, description, profiles, bundle}
    """
    supplements = []

    for ext in extensions:
        module = ext.get("module")
        if module and hasattr(module, 'get_domain_supplements'):
            try:
                supplement_info = module.get_domain_supplements()
                if supplement_info and supplement_info.get("domain"):
                    supplement_info["bundle"] = ext["bundle"]
                    supplements.append(supplement_info)
            except Exception as e:
                print(f"Warning: get_domain_supplements() failed for {ext['bundle']}: {e}", file=sys.stderr)

    return supplements


def get_modules_from_extensions(extensions: list, project_root: Path) -> list:
    """Get project modules from extensions.

    Calls get_modules() on each applicable extension that provides it.

    Args:
        extensions: List of extension info dicts from discover_extensions()
        project_root: Path to the project root

    Returns:
        List of module dicts: {name, path, build_system, ...}
    """
    modules = []

    for ext in extensions:
        module = ext.get("module")
        if module and hasattr(module, 'get_modules'):
            try:
                ext_modules = module.get_modules(str(project_root))
                modules.extend(ext_modules)
            except Exception as e:
                print(f"Warning: get_modules() failed for {ext['bundle']}: {e}", file=sys.stderr)

    return modules


def get_workflow_extensions_from_extensions(extensions: list) -> dict:
    """Get workflow extensions (triage, outline) from extensions.

    Args:
        extensions: List of extension info dicts

    Returns:
        Dict mapping bundle to {triage: skill_ref, outline: skill_ref}
    """
    workflow_extensions = {}

    for ext in extensions:
        module = ext.get("module")
        if not module:
            continue

        ext_info = {}

        if hasattr(module, 'provides_triage'):
            try:
                triage = module.provides_triage()
                if triage:
                    ext_info["triage"] = triage
            except Exception:
                pass

        if hasattr(module, 'provides_outline'):
            try:
                outline = module.provides_outline()
                if outline:
                    ext_info["outline"] = outline
            except Exception:
                pass

        if ext_info:
            workflow_extensions[ext["bundle"]] = ext_info

    return workflow_extensions


def generate_profile_command_from_extensions(
    extensions: list,
    build_system: str,
    canonical: str,
    profile_id: str,
    activation: dict,
    module_name: str = None
) -> str | None:
    """Generate a profile-based command using domain extension.

    Delegates to the appropriate extension's generate_profile_command() function.

    Args:
        extensions: List of extension info dicts
        build_system: "maven", "gradle", etc.
        canonical: The canonical command name
        profile_id: The profile ID to activate
        activation: Dict with activation info
        module_name: Optional module name

    Returns:
        Command string or None if no extension handles this build system
    """
    for ext in extensions:
        module = ext.get("module")
        if not module:
            continue

        # Check if this extension handles the build system
        if hasattr(module, 'provides_build_systems'):
            try:
                systems = module.provides_build_systems()
                if build_system not in systems:
                    continue
            except Exception:
                continue

        # Check if extension provides profile command generation
        if hasattr(module, 'generate_profile_command'):
            try:
                cmd = module.generate_profile_command(
                    build_system, canonical, profile_id, activation, module_name
                )
                if cmd:
                    return cmd
            except Exception:
                pass

    return None


# =============================================================================
# CLI Commands
# =============================================================================

def cmd_list(args) -> int:
    """List applicable extensions for a project."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"status: error\nmessage: Directory not found: {project_dir}")
        return 1

    extensions = discover_extensions(project_dir)

    print("status: success")
    print(f"project_dir: {project_dir}")
    print(f"count: {len(extensions)}")
    print()
    print(f"extensions[{len(extensions)}]" + "{bundle,build_systems}:")
    for ext in extensions:
        module = ext.get("module")
        build_systems = []
        if module and hasattr(module, 'provides_build_systems'):
            try:
                build_systems = module.provides_build_systems()
            except Exception:
                pass
        print(f"{ext['bundle']}\t{','.join(build_systems) if build_systems else '-'}")

    return 0


def cmd_list_all(args) -> int:
    """List all available extensions (no applicability check)."""
    extensions = discover_all_extensions()

    print("status: success")
    print(f"count: {len(extensions)}")
    print()
    print(f"extensions[{len(extensions)}]" + "{bundle,has_domains,has_supplements,build_systems}:")
    for ext in extensions:
        module = ext.get("module")
        has_domains = hasattr(module, 'get_skill_domains') if module else False
        has_supplements = hasattr(module, 'get_domain_supplements') if module else False
        build_systems = []
        if module and hasattr(module, 'provides_build_systems'):
            try:
                build_systems = module.provides_build_systems()
            except Exception:
                pass
        print(f"{ext['bundle']}\t{has_domains}\t{has_supplements}\t{','.join(build_systems) if build_systems else '-'}")

    return 0


def cmd_get_build_systems(args) -> int:
    """Get build systems from applicable extensions."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"status: error\nmessage: Directory not found: {project_dir}")
        return 1

    extensions = discover_extensions(project_dir)
    build_systems = get_build_systems_from_extensions(extensions)

    print("status: success")
    print(f"project_dir: {project_dir}")
    print(f"build_systems: {','.join(build_systems) if build_systems else 'none'}")

    return 0


def cmd_get_command_mappings(args) -> int:
    """Get command mappings from applicable extensions."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"status: error\nmessage: Directory not found: {project_dir}")
        return 1

    extensions = discover_extensions(project_dir)
    mappings = get_command_mappings_from_extensions(extensions)

    # Output as JSON for easy parsing
    print(json.dumps({"status": "success", "mappings": mappings}, indent=2))

    return 0


def cmd_get_skill_domains(args) -> int:
    """Get skill domains from extensions."""
    if args.project_dir:
        project_dir = Path(args.project_dir).resolve()
        if not project_dir.exists():
            print(f"status: error\nmessage: Directory not found: {project_dir}")
            return 1
        extensions = discover_extensions(project_dir)
    else:
        extensions = discover_all_extensions()

    domains = get_skill_domains_from_extensions(extensions)
    supplements = get_domain_supplements_from_extensions(extensions)

    result = {
        "status": "success",
        "domains": [
            {
                "key": d.get("domain", {}).get("key") if isinstance(d.get("domain"), dict) else d.get("domain"),
                "name": d.get("domain", {}).get("name", "") if isinstance(d.get("domain"), dict) else "",
                "bundle": d.get("bundle", "")
            }
            for d in domains
        ],
        "supplements": [
            {
                "domain": s.get("domain", ""),
                "bundle": s.get("bundle", ""),
                "description": s.get("description", "")
            }
            for s in supplements
        ]
    }

    print(json.dumps(result, indent=2))
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extension discovery and API utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list subcommand
    list_parser = subparsers.add_parser("list", help="List applicable extensions for a project")
    list_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    list_parser.set_defaults(func=cmd_list)

    # list-all subcommand
    list_all_parser = subparsers.add_parser("list-all", help="List all available extensions")
    list_all_parser.set_defaults(func=cmd_list_all)

    # get-build-systems subcommand
    bs_parser = subparsers.add_parser("get-build-systems", help="Get build systems from applicable extensions")
    bs_parser.add_argument("--project-dir", dest="project_dir", required=True, help="Project directory")
    bs_parser.set_defaults(func=cmd_get_build_systems)

    # get-command-mappings subcommand
    cm_parser = subparsers.add_parser("get-command-mappings", help="Get command mappings from applicable extensions")
    cm_parser.add_argument("--project-dir", dest="project_dir", required=True, help="Project directory")
    cm_parser.set_defaults(func=cmd_get_command_mappings)

    # get-skill-domains subcommand
    sd_parser = subparsers.add_parser("get-skill-domains", help="Get skill domains from extensions")
    sd_parser.add_argument("--project-dir", dest="project_dir", default=None, help="Project directory (optional)")
    sd_parser.set_defaults(func=cmd_get_skill_domains)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
