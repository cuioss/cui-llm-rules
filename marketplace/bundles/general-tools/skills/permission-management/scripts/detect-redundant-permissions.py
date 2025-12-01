#!/usr/bin/env python3
"""
detect-redundant-permissions.py

Detect permissions in local settings that are redundant with global settings.

Detects:
1. Exact duplicates between global and local
2. Marketplace permissions (Skill, SlashCommand) in local that should be global
3. Permissions covered by broader wildcards in global

Usage:
    python3 detect-redundant-permissions.py --global-settings PATH --local-settings PATH

Output: JSON with redundant and marketplace_in_local arrays
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


def load_settings(path: str) -> tuple[dict, Optional[str]]:
    """
    Load settings from a JSON file.

    Returns:
        Tuple of (settings_dict, error_message)
        If error, settings_dict will be empty and error_message set.
    """
    settings_path = Path(path)

    if not settings_path.exists():
        return {}, f"Settings file not found: {path}"

    try:
        with open(settings_path, 'r') as f:
            data = json.load(f)

        # Ensure permissions structure exists
        if "permissions" not in data:
            data["permissions"] = {}
        for key in ["allow", "deny", "ask"]:
            if key not in data["permissions"]:
                data["permissions"][key] = []

        return data, None
    except json.JSONDecodeError as e:
        return {}, f"Invalid JSON in {path}: {e}"


def is_marketplace_permission(permission: str) -> bool:
    """Check if a permission is a marketplace permission (Skill or SlashCommand)."""
    return permission.startswith("Skill(") or permission.startswith("SlashCommand(/")


def normalize_path(path_part: str) -> str:
    """Normalize a path for comparison (handle // prefix, ~/, etc.)."""
    # Remove trailing slashes for comparison
    path_part = path_part.rstrip('/')
    return path_part


def extract_permission_parts(permission: str) -> tuple[str, str]:
    """
    Extract the type and pattern from a permission string.

    Examples:
        "Bash(git:*)" -> ("Bash", "git:*")
        "Read(//~/git/**)" -> ("Read", "//~/git/**")
        "Skill(builder:*)" -> ("Skill", "builder:*")

    Returns:
        Tuple of (permission_type, pattern)
    """
    match = re.match(r'^(\w+)\((.+)\)$', permission)
    if match:
        return match.group(1), match.group(2)
    return permission, ""


def is_covered_by_wildcard(specific: str, broader: str) -> bool:
    """
    Check if a specific permission is covered by a broader wildcard pattern.

    Examples:
        "Bash(git:status)" is covered by "Bash(git:*)"
        "Read(//~/git/my-project/**)" is covered by "Read(//~/git/**)"
    """
    spec_type, spec_pattern = extract_permission_parts(specific)
    broad_type, broad_pattern = extract_permission_parts(broader)

    # Must be same permission type
    if spec_type != broad_type:
        return False

    # If broader ends with :*, check if specific starts with same prefix
    if broad_pattern.endswith(':*'):
        prefix = broad_pattern[:-1]  # Remove the *
        if spec_pattern.startswith(prefix):
            return True

    # For path-based permissions (Read, Write, Edit), check directory coverage
    if broad_type in ('Read', 'Write', 'Edit'):
        # Remove trailing ** for comparison
        broad_base = broad_pattern.rstrip('*').rstrip('/')
        spec_base = spec_pattern.rstrip('*').rstrip('/')

        # The specific path must be under the broader path
        if spec_base.startswith(broad_base) and len(spec_base) > len(broad_base):
            return True

    return False


def detect_redundant_permissions(
    global_settings: dict,
    local_settings: dict
) -> dict:
    """
    Detect redundant permissions between global and local settings.

    Returns dict with:
        - redundant: List of redundant permissions with reasons
        - marketplace_in_local: List of marketplace permissions that should be global
        - summary: Counts of issues found
    """
    global_allow = set(global_settings.get("permissions", {}).get("allow", []))
    local_allow = local_settings.get("permissions", {}).get("allow", [])

    redundant = []
    marketplace_in_local = []

    for local_perm in local_allow:
        # Check for exact duplicates
        if local_perm in global_allow:
            redundant.append({
                "permission": local_perm,
                "reason": "Exact duplicate exists in global settings",
                "type": "exact_duplicate",
                "covered_by": local_perm
            })
            continue

        # Check for marketplace permissions that should be in global
        if is_marketplace_permission(local_perm):
            marketplace_in_local.append({
                "permission": local_perm,
                "reason": "Marketplace permissions should be in global settings",
                "type": "marketplace_permission"
            })
            continue

        # Check if covered by broader wildcard in global
        for global_perm in global_allow:
            if is_covered_by_wildcard(local_perm, global_perm):
                redundant.append({
                    "permission": local_perm,
                    "reason": f"Covered by broader wildcard in global settings",
                    "type": "covered_by_wildcard",
                    "covered_by": global_perm
                })
                break

    return {
        "redundant": redundant,
        "marketplace_in_local": marketplace_in_local,
        "summary": {
            "redundant_count": len(redundant),
            "marketplace_in_local_count": len(marketplace_in_local),
            "total_issues": len(redundant) + len(marketplace_in_local),
            "local_permissions_checked": len(local_allow),
            "global_permissions_count": len(global_allow)
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect redundant permissions between global and local settings"
    )
    parser.add_argument(
        "--global-settings",
        required=True,
        help="Path to global settings file (~/.claude/settings.json)"
    )
    parser.add_argument(
        "--local-settings",
        required=True,
        help="Path to local/project settings file"
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "text"],
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Load global settings
    global_settings, global_error = load_settings(args.global_settings)
    if global_error:
        result = {
            "error": global_error,
            "global_exists": False
        }
        print(json.dumps(result, indent=2))
        return

    # Load local settings
    local_settings, local_error = load_settings(args.local_settings)
    if local_error:
        result = {
            "error": local_error,
            "local_exists": False
        }
        print(json.dumps(result, indent=2))
        return

    # Detect redundant permissions
    result = detect_redundant_permissions(global_settings, local_settings)
    result["global_exists"] = True
    result["local_exists"] = True
    result["global_path"] = args.global_settings
    result["local_path"] = args.local_settings

    # Output
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Text format
        print("=" * 60)
        print("REDUNDANT PERMISSIONS ANALYSIS")
        print("=" * 60)
        print()
        print(f"Global: {args.global_settings}")
        print(f"Local: {args.local_settings}")
        print()

        if result["redundant"]:
            print("REDUNDANT PERMISSIONS:")
            for item in result["redundant"]:
                print(f"  - {item['permission']}")
                print(f"    Reason: {item['reason']}")
                if "covered_by" in item:
                    print(f"    Covered by: {item['covered_by']}")
            print()

        if result["marketplace_in_local"]:
            print("MARKETPLACE PERMISSIONS IN LOCAL (should be in global):")
            for item in result["marketplace_in_local"]:
                print(f"  - {item['permission']}")
            print()

        summary = result["summary"]
        print("SUMMARY:")
        print(f"  Redundant permissions: {summary['redundant_count']}")
        print(f"  Marketplace in local: {summary['marketplace_in_local_count']}")
        print(f"  Total issues: {summary['total_issues']}")


if __name__ == "__main__":
    main()
