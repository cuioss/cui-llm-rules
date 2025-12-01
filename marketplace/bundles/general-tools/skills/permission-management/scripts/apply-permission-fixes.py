#!/usr/bin/env python3
"""
apply-permission-fixes.py

Apply safe fixes to permission settings: duplicate removal, path fixing,
sorting, and adding default permissions.

Fixes:
1. Remove duplicate permissions
2. Normalize path formats (trailing slashes)
3. Sort permission lists alphabetically
4. Add default project permissions (.plan access)

Usage:
    python3 apply-permission-fixes.py --settings PATH [--dry-run]

Output: JSON with changes summary
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# Default project permissions that should exist
DEFAULT_PERMISSIONS = [
    "Edit(.plan/**)",
    "Write(.plan/**)"
]


def load_settings(path: str) -> tuple[dict, Optional[str]]:
    """Load settings from a JSON file."""
    settings_path = Path(path)

    if not settings_path.exists():
        return {}, f"Settings file not found: {path}"

    try:
        with open(settings_path, 'r') as f:
            data = json.load(f)
        ensure_permissions_structure(data)
        return data, None
    except json.JSONDecodeError as err:
        return {}, f"Invalid JSON in {path}: {err}"


def ensure_permissions_structure(data: dict) -> None:
    """Ensure permissions structure exists in settings."""
    if "permissions" not in data:
        data["permissions"] = {}
    for key in ["allow", "deny", "ask"]:
        if key not in data["permissions"]:
            data["permissions"][key] = []


def save_settings(path: str, settings: dict) -> bool:
    """Save settings to a JSON file."""
    try:
        with open(path, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except OSError:
        return False


def normalize_path(permission: str) -> tuple[str, bool]:
    """
    Normalize a permission path.

    Returns tuple of (normalized_permission, was_changed).
    """
    # Remove trailing slash inside parentheses (but preserve ** wildcards)
    match = re.match(r'^(\w+)\((.+?)(/)?\)$', permission)
    if not match:
        return permission, False

    perm_type = match.group(1)
    path = match.group(2)
    trailing = match.group(3)

    # Only remove trailing slash if it's not part of a wildcard pattern
    if trailing and not path.endswith('*'):
        return f"{perm_type}({path})", True

    return permission, False


def remove_duplicates(perm_list: list[str]) -> tuple[list[str], int]:
    """
    Remove duplicate permissions from a list.

    Returns tuple of (deduplicated_list, count_removed).
    """
    seen = set()
    result = []
    duplicates = 0

    for perm in perm_list:
        if perm in seen:
            duplicates += 1
        else:
            seen.add(perm)
            result.append(perm)

    return result, duplicates


def process_permission_list(perm_list: list[str]) -> tuple[list[str], int, int, bool]:
    """
    Process a single permission list: normalize, dedupe, sort.

    Returns tuple of (processed_list, paths_fixed, duplicates_removed, was_sorted).
    """
    paths_fixed = 0
    normalized = []

    for perm in perm_list:
        norm_perm, changed = normalize_path(perm)
        normalized.append(norm_perm)
        if changed:
            paths_fixed += 1

    deduplicated, dups = remove_duplicates(normalized)
    sorted_list = sorted(deduplicated)
    was_sorted = sorted_list != deduplicated

    return sorted_list, paths_fixed, dups, was_sorted


def add_default_permissions(allow_list: list[str]) -> list[str]:
    """Add default permissions if missing. Returns list of added permissions."""
    added = []
    for default_perm in DEFAULT_PERMISSIONS:
        if default_perm not in allow_list:
            allow_list.append(default_perm)
            added.append(default_perm)
    return added


def apply_permission_fixes(settings: dict, add_defaults: bool = True) -> dict:
    """
    Apply all safe fixes to settings.

    Args:
        settings: Settings dict to modify
        add_defaults: Whether to add default project permissions

    Returns dict with fix results.
    """
    total_duplicates = 0
    total_paths_fixed = 0
    was_sorted = False

    # Process each permission list
    for key in ["allow", "deny", "ask"]:
        perm_list = settings.get("permissions", {}).get(key, [])
        processed, paths_fixed, dups, sorted_flag = process_permission_list(perm_list)

        settings["permissions"][key] = processed
        total_paths_fixed += paths_fixed
        total_duplicates += dups
        was_sorted = was_sorted or sorted_flag

    # Add default permissions if requested
    defaults_added = []
    if add_defaults:
        allow_list = settings["permissions"]["allow"]
        defaults_added = add_default_permissions(allow_list)
        if defaults_added:
            settings["permissions"]["allow"] = sorted(allow_list)
            was_sorted = True

    changes_made = total_duplicates > 0 or total_paths_fixed > 0 or len(defaults_added) > 0 or was_sorted

    return {
        "duplicates_removed": total_duplicates,
        "paths_fixed": total_paths_fixed,
        "defaults_added": defaults_added,
        "sorted": was_sorted,
        "changes_made": changes_made
    }


def output_json(result: dict) -> None:
    """Output result as JSON."""
    print(json.dumps(result, indent=2))


def output_text(result: dict, settings_path: str, dry_run: bool) -> None:
    """Output result as human-readable text."""
    print("=" * 60)
    print("PERMISSION FIXES")
    print("=" * 60)
    print()
    print(f"Settings: {settings_path}")
    print("Mode: " + ("Dry-run" if dry_run else "Apply changes"))
    print()

    print("CHANGES:")
    print(f"  Duplicates removed: {result['duplicates_removed']}")
    print(f"  Paths normalized: {result['paths_fixed']}")
    print("  Sorted: " + ("Yes" if result["sorted"] else "No"))

    if result["defaults_added"]:
        print("\n  Defaults added:")
        for perm in result["defaults_added"]:
            print(f"    + {perm}")

    print()
    if result["changes_made"]:
        if not dry_run and result.get("applied"):
            print("Changes applied successfully")
        elif dry_run:
            print("Dry-run mode: No files modified")
    else:
        print("No changes needed.")


def main():
    parser = argparse.ArgumentParser(
        description="Apply safe fixes to permission settings"
    )
    parser.add_argument(
        "--settings",
        required=True,
        help="Path to settings file to fix"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "text"],
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Load settings
    settings, error = load_settings(args.settings)
    if error:
        output_json({"error": error})
        return

    # Apply fixes (always add defaults by default)
    result = apply_permission_fixes(settings, add_defaults=True)
    result["dry_run"] = args.dry_run
    result["settings_path"] = args.settings

    # Save if not dry-run and changes were made
    if not args.dry_run and result["changes_made"]:
        result["applied"] = save_settings(args.settings, settings)
        if not result["applied"]:
            result["error"] = "Failed to save settings"
    else:
        result["applied"] = False

    # Output
    if args.format == "json":
        output_json(result)
    else:
        output_text(result, args.settings, args.dry_run)


if __name__ == "__main__":
    main()
