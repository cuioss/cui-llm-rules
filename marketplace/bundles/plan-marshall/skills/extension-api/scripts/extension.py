#!/usr/bin/env python3
"""
Extension discovery library.

Single source of truth for discovering and loading extension.py files
from domain bundles. Used by project-structure and plan-marshall-config.

This module is a library - it has no CLI. Persistence goes through
project-structure, and reading goes through plan-marshall-config.
"""

import importlib.util
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


def get_extension_base_path() -> Path:
    """Get path to extension_base.py for import injection."""
    return Path(__file__).parent / "extension_base.py"


def load_extension_module(extension_path: Path, bundle_name: str):
    """Load an extension.py module and instantiate the Extension class.

    Injects extension_base into sys.modules so extensions can import it.

    Args:
        extension_path: Path to extension.py file
        bundle_name: Name of the bundle for module naming

    Returns:
        Extension instance or None if failed
    """
    try:
        # Ensure extension_base is importable by extensions
        _ensure_extension_base_loaded()

        spec = importlib.util.spec_from_file_location(
            f"extension_{bundle_name}",
            extension_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the Extension class and instantiate it
        if hasattr(module, 'Extension'):
            return module.Extension()

        print(f"Warning: No Extension class found in {bundle_name}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Failed to load extension from {bundle_name}: {e}", file=sys.stderr)
        return None


def _ensure_extension_base_loaded():
    """Ensure extension_base module is loaded and available for import."""
    if 'extension_base' in sys.modules:
        return

    base_path = get_extension_base_path()
    if not base_path.exists():
        return

    try:
        spec = importlib.util.spec_from_file_location("extension_base", base_path)
        base_module = importlib.util.module_from_spec(spec)
        sys.modules['extension_base'] = base_module
        spec.loader.exec_module(base_module)
    except Exception as e:
        print(f"Warning: Failed to load extension_base: {e}", file=sys.stderr)


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


