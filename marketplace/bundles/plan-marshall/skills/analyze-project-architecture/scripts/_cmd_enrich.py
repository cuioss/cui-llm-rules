#!/usr/bin/env python3
"""Enrich command handlers for architecture script.

Handles: enrich project, module, package, skills, dependencies, tip, insight, best-practice
These commands write to llm-enriched.json.
"""

import sys

from _architecture_core import (
    DataNotFoundError,
    ModuleNotFoundError,
    get_enriched_path,
    load_derived_data,
    load_llm_enriched,
    save_llm_enriched,
    get_module_names,
    print_toon_list,
)


# =============================================================================
# API Functions
# =============================================================================

def enrich_project(description: str, project_dir: str = '.') -> dict:
    """Update project description.

    Args:
        description: Project description (1-2 sentences)
        project_dir: Project directory path

    Returns:
        Dict with status and updated field
    """
    enriched = load_llm_enriched(project_dir)

    if "project" not in enriched:
        enriched["project"] = {}

    enriched["project"]["description"] = description
    save_llm_enriched(enriched, project_dir)

    return {
        "status": "success",
        "updated": "project.description"
    }


def enrich_module(
    module_name: str,
    responsibility: str,
    purpose: str = None,
    project_dir: str = '.'
) -> dict:
    """Update module responsibility and purpose.

    Args:
        module_name: Module name
        responsibility: Module description (1-3 sentences)
        purpose: Module classification (library, extension, etc.)
        project_dir: Project directory path

    Returns:
        Dict with status, module, and updated fields
    """
    # Validate module exists in derived data
    derived = load_derived_data(project_dir)
    modules = get_module_names(derived)
    if module_name not in modules:
        raise ModuleNotFoundError(f"Module not found: {module_name}", modules)

    enriched = load_llm_enriched(project_dir)

    if "modules" not in enriched:
        enriched["modules"] = {}
    if module_name not in enriched["modules"]:
        enriched["modules"][module_name] = {}

    updated = []
    enriched["modules"][module_name]["responsibility"] = responsibility
    updated.append("responsibility")

    if purpose:
        enriched["modules"][module_name]["purpose"] = purpose
        updated.append("purpose")

    save_llm_enriched(enriched, project_dir)

    return {
        "status": "success",
        "module": module_name,
        "updated": updated
    }


def enrich_package(
    module_name: str,
    package_name: str,
    description: str,
    project_dir: str = '.'
) -> dict:
    """Add or update key package description.

    Args:
        module_name: Module name
        package_name: Full package name
        description: Package description (1-2 sentences)
        project_dir: Project directory path

    Returns:
        Dict with status, module, package, and action
    """
    # Validate module exists
    derived = load_derived_data(project_dir)
    modules = get_module_names(derived)
    if module_name not in modules:
        raise ModuleNotFoundError(f"Module not found: {module_name}", modules)

    enriched = load_llm_enriched(project_dir)

    if "modules" not in enriched:
        enriched["modules"] = {}
    if module_name not in enriched["modules"]:
        enriched["modules"][module_name] = {}
    if "key_packages" not in enriched["modules"][module_name]:
        enriched["modules"][module_name]["key_packages"] = {}

    action = "updated" if package_name in enriched["modules"][module_name]["key_packages"] else "added"
    enriched["modules"][module_name]["key_packages"][package_name] = {
        "description": description
    }

    save_llm_enriched(enriched, project_dir)

    return {
        "status": "success",
        "module": module_name,
        "package": package_name,
        "action": action
    }


def enrich_skills(
    module_name: str,
    domains: list,
    project_dir: str = '.'
) -> dict:
    """Update proposed skill domains.

    Args:
        module_name: Module name
        domains: List of skill domain references
        project_dir: Project directory path

    Returns:
        Dict with status, module, and proposed_skill_domains
    """
    # Validate module exists
    derived = load_derived_data(project_dir)
    modules = get_module_names(derived)
    if module_name not in modules:
        raise ModuleNotFoundError(f"Module not found: {module_name}", modules)

    enriched = load_llm_enriched(project_dir)

    if "modules" not in enriched:
        enriched["modules"] = {}
    if module_name not in enriched["modules"]:
        enriched["modules"][module_name] = {}

    enriched["modules"][module_name]["proposed_skill_domains"] = domains

    save_llm_enriched(enriched, project_dir)

    return {
        "status": "success",
        "module": module_name,
        "proposed_skill_domains": domains
    }


def enrich_dependencies(
    module_name: str,
    key_deps: list = None,
    internal_deps: list = None,
    project_dir: str = '.'
) -> dict:
    """Update key and internal dependencies.

    Args:
        module_name: Module name
        key_deps: List of key external dependencies
        internal_deps: List of internal module dependencies
        project_dir: Project directory path

    Returns:
        Dict with status, module, and updated dependencies
    """
    # Validate module exists
    derived = load_derived_data(project_dir)
    modules = get_module_names(derived)
    if module_name not in modules:
        raise ModuleNotFoundError(f"Module not found: {module_name}", modules)

    enriched = load_llm_enriched(project_dir)

    if "modules" not in enriched:
        enriched["modules"] = {}
    if module_name not in enriched["modules"]:
        enriched["modules"][module_name] = {}

    result = {
        "status": "success",
        "module": module_name
    }

    if key_deps is not None:
        enriched["modules"][module_name]["key_dependencies"] = key_deps
        result["key_dependencies"] = key_deps

    if internal_deps is not None:
        enriched["modules"][module_name]["internal_dependencies"] = internal_deps
        result["internal_dependencies"] = internal_deps

    save_llm_enriched(enriched, project_dir)

    return result


def enrich_tip(module_name: str, tip: str, project_dir: str = '.') -> dict:
    """Add implementation tip to a module.

    Args:
        module_name: Module name
        tip: Implementation tip
        project_dir: Project directory path

    Returns:
        Dict with status, module, and tips list
    """
    return _append_to_list(module_name, "tips", tip, project_dir)


def enrich_insight(module_name: str, insight: str, project_dir: str = '.') -> dict:
    """Add learned insight to a module.

    Args:
        module_name: Module name
        insight: Learned insight from implementation
        project_dir: Project directory path

    Returns:
        Dict with status, module, and insights list
    """
    return _append_to_list(module_name, "insights", insight, project_dir)


def enrich_best_practice(module_name: str, practice: str, project_dir: str = '.') -> dict:
    """Add best practice to a module.

    Args:
        module_name: Module name
        practice: Established best practice
        project_dir: Project directory path

    Returns:
        Dict with status, module, and best_practices list
    """
    return _append_to_list(module_name, "best_practices", practice, project_dir)


def _append_to_list(module_name: str, field: str, value: str, project_dir: str = '.') -> dict:
    """Append value to a list field in module enrichment.

    Args:
        module_name: Module name
        field: Field name (tips, insights, best_practices)
        value: Value to append
        project_dir: Project directory path

    Returns:
        Dict with status, module, and field list
    """
    # Validate module exists
    derived = load_derived_data(project_dir)
    modules = get_module_names(derived)
    if module_name not in modules:
        raise ModuleNotFoundError(f"Module not found: {module_name}", modules)

    enriched = load_llm_enriched(project_dir)

    if "modules" not in enriched:
        enriched["modules"] = {}
    if module_name not in enriched["modules"]:
        enriched["modules"][module_name] = {}
    if field not in enriched["modules"][module_name]:
        enriched["modules"][module_name][field] = []

    # Append if not duplicate
    if value not in enriched["modules"][module_name][field]:
        enriched["modules"][module_name][field].append(value)

    save_llm_enriched(enriched, project_dir)

    return {
        "status": "success",
        "module": module_name,
        field: enriched["modules"][module_name][field]
    }


# =============================================================================
# CLI Handlers
# =============================================================================

def _handle_module_not_found(module_name: str, project_dir: str):
    """Handle module not found error with available modules list."""
    try:
        derived = load_derived_data(project_dir)
        modules = get_module_names(derived)
    except Exception:
        modules = []

    print("error: Module not found")
    print(f"module: {module_name}")
    print_toon_list("available", modules)
    sys.exit(1)


def cmd_enrich_project(args) -> int:
    """CLI handler for enrich project command."""
    try:
        result = enrich_project(args.description, args.project_dir)
        print(f"status\t{result['status']}")
        print(f"updated\t{result['updated']}")
        return 0
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_enrich_module(args) -> int:
    """CLI handler for enrich module command."""
    try:
        result = enrich_module(
            args.name,
            args.responsibility,
            args.purpose,
            args.project_dir
        )
        print(f"status\t{result['status']}")
        print(f"module\t{result['module']}")
        print_toon_list("updated", result['updated'])
        return 0
    except ModuleNotFoundError:
        _handle_module_not_found(args.name, args.project_dir)
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_enrich_package(args) -> int:
    """CLI handler for enrich package command."""
    try:
        result = enrich_package(
            args.module,
            args.package,
            args.description,
            args.project_dir
        )
        print(f"status\t{result['status']}")
        print(f"module\t{result['module']}")
        print(f"package\t{result['package']}")
        print(f"action\t{result['action']}")
        return 0
    except ModuleNotFoundError:
        _handle_module_not_found(args.module, args.project_dir)
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_enrich_skills(args) -> int:
    """CLI handler for enrich skills command."""
    try:
        domains = [d.strip() for d in args.domains.split(",")]
        result = enrich_skills(args.module, domains, args.project_dir)
        print(f"status\t{result['status']}")
        print(f"module\t{result['module']}")
        print_toon_list("proposed_skill_domains", result['proposed_skill_domains'])
        return 0
    except ModuleNotFoundError:
        _handle_module_not_found(args.module, args.project_dir)
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_enrich_dependencies(args) -> int:
    """CLI handler for enrich dependencies command."""
    try:
        key_deps = None
        internal_deps = None
        if args.key:
            key_deps = [d.strip() for d in args.key.split(",")]
        if args.internal:
            internal_deps = [d.strip() for d in args.internal.split(",")]

        result = enrich_dependencies(
            args.module,
            key_deps,
            internal_deps,
            args.project_dir
        )
        print(f"status\t{result['status']}")
        print(f"module\t{result['module']}")
        if 'key_dependencies' in result:
            print_toon_list("key_dependencies", result['key_dependencies'])
        if 'internal_dependencies' in result:
            print_toon_list("internal_dependencies", result['internal_dependencies'])
        return 0
    except ModuleNotFoundError:
        _handle_module_not_found(args.module, args.project_dir)
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_enrich_tip(args) -> int:
    """CLI handler for enrich tip command."""
    try:
        result = enrich_tip(args.module, args.tip, args.project_dir)
        print(f"status\t{result['status']}")
        print(f"module\t{result['module']}")
        print_toon_list("tips", result['tips'])
        return 0
    except ModuleNotFoundError:
        _handle_module_not_found(args.module, args.project_dir)
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_enrich_insight(args) -> int:
    """CLI handler for enrich insight command."""
    try:
        result = enrich_insight(args.module, args.insight, args.project_dir)
        print(f"status\t{result['status']}")
        print(f"module\t{result['module']}")
        print_toon_list("insights", result['insights'])
        return 0
    except ModuleNotFoundError:
        _handle_module_not_found(args.module, args.project_dir)
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1


def cmd_enrich_best_practice(args) -> int:
    """CLI handler for enrich best-practice command."""
    try:
        result = enrich_best_practice(args.module, args.practice, args.project_dir)
        print(f"status\t{result['status']}")
        print(f"module\t{result['module']}")
        print_toon_list("best_practices", result['best_practices'])
        return 0
    except ModuleNotFoundError:
        _handle_module_not_found(args.module, args.project_dir)
    except DataNotFoundError:
        print("error: Enrichment data not found")
        print(f"expected_file: {get_enriched_path(args.project_dir)}")
        print("resolution: Run 'architecture.py init' first")
        return 1
    except Exception as e:
        print(f"status\terror", file=sys.stderr)
        print(f"error\t{e}", file=sys.stderr)
        return 1
