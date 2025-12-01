#!/usr/bin/env python3
"""
consolidate-build-outputs.py

Replace timestamped build output permissions with wildcard patterns.

Detects patterns like:
  Read(target/build-output-2025-11-20-174411.log)
  Read(module/target/build-output-2025-11-21-093000.log)

And consolidates them to:
  Read(target/build-output-*.log)
  Read(**/target/build-output-*.log)

Usage:
    python3 consolidate-build-outputs.py --settings PATH [--dry-run]

Output: JSON with consolidated count and changes
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


# Timestamp pattern in build output filenames
# Matches patterns like: build-output-2025-11-20-174411.log
TIMESTAMP_PATTERN = re.compile(
    r'^(\w+)\((.*/)?(.+)-(\d{4}-\d{2}-\d{2}-\d{6})\.(\w+)\)$'
)

# Alternative pattern for files with date-only timestamps
DATE_PATTERN = re.compile(
    r'^(\w+)\((.*/)?(.+)-(\d{4}-\d{2}-\d{2})\.(\w+)\)$'
)

# Pattern for generic timestamped files
GENERIC_TIMESTAMP_PATTERN = re.compile(
    r'^(\w+)\((.*/)?(.+[_-])(\d{4,})([_-]?\d*)\.(\w+)\)$'
)


def load_settings(path: str) -> tuple[dict, Optional[str]]:
    """Load settings from a JSON file."""
    settings_path = Path(path)

    if not settings_path.exists():
        return {}, f"Settings file not found: {path}"

    try:
        with open(settings_path, 'r') as f:
            data = json.load(f)

        if "permissions" not in data:
            data["permissions"] = {}
        for key in ["allow", "deny", "ask"]:
            if key not in data["permissions"]:
                data["permissions"][key] = []

        return data, None
    except json.JSONDecodeError as e:
        return {}, f"Invalid JSON in {path}: {e}"


def save_settings(path: str, settings: dict) -> bool:
    """Save settings to a JSON file."""
    try:
        with open(path, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        return False


def parse_timestamped_permission(permission: str) -> Optional[dict]:
    """
    Parse a permission to check if it contains a timestamp pattern.

    Returns dict with parsed components if it's a timestamped permission,
    None otherwise.
    """
    # Try the full timestamp pattern first (YYYY-MM-DD-HHMMSS)
    match = TIMESTAMP_PATTERN.match(permission)
    if match:
        perm_type, path_prefix, base_name, timestamp, extension = match.groups()
        return {
            "permission": permission,
            "type": perm_type,
            "path_prefix": path_prefix or "",
            "base_name": base_name,
            "timestamp": timestamp,
            "extension": extension
        }

    # Try date-only pattern (YYYY-MM-DD)
    match = DATE_PATTERN.match(permission)
    if match:
        perm_type, path_prefix, base_name, timestamp, extension = match.groups()
        return {
            "permission": permission,
            "type": perm_type,
            "path_prefix": path_prefix or "",
            "base_name": base_name,
            "timestamp": timestamp,
            "extension": extension
        }

    return None


def generate_wildcard(parsed_permissions: list[dict]) -> str:
    """
    Generate a wildcard pattern from a list of parsed timestamped permissions.

    Groups by permission type, base name, and extension.
    """
    if not parsed_permissions:
        return ""

    first = parsed_permissions[0]
    perm_type = first["type"]
    base_name = first["base_name"]
    extension = first["extension"]

    # Collect all unique path prefixes
    path_prefixes = set(p["path_prefix"] for p in parsed_permissions)

    # If all have the same path prefix, use it directly
    if len(path_prefixes) == 1:
        path_prefix = first["path_prefix"]
        return f"{perm_type}({path_prefix}{base_name}-*.{extension})"

    # If there are multiple path prefixes, use ** to cover all
    return f"{perm_type}(**/{base_name}-*.{extension})"


def consolidate_build_outputs(settings: dict) -> dict:
    """
    Analyze permissions and consolidate timestamped build outputs.

    Returns dict with:
        - consolidated: Number of permissions consolidated
        - removed: List of permissions that would be removed
        - wildcards_added: List of wildcard patterns to add
        - changes: Description of changes
    """
    allow_list = settings.get("permissions", {}).get("allow", [])

    # Group timestamped permissions by their base pattern
    timestamped_groups = defaultdict(list)
    non_timestamped = []

    for permission in allow_list:
        parsed = parse_timestamped_permission(permission)
        if parsed:
            # Group key: type + base_name + extension
            key = (parsed["type"], parsed["base_name"], parsed["extension"])
            timestamped_groups[key].append(parsed)
        else:
            non_timestamped.append(permission)

    # Generate wildcards for each group
    wildcards_to_add = []
    permissions_to_remove = []

    for key, group in timestamped_groups.items():
        if len(group) >= 1:  # Even single timestamped entries should be wildcarded
            wildcard = generate_wildcard(group)
            wildcards_to_add.append(wildcard)
            permissions_to_remove.extend([p["permission"] for p in group])

    return {
        "consolidated": len(permissions_to_remove),
        "removed": permissions_to_remove,
        "wildcards_added": wildcards_to_add,
        "changes": {
            "timestamped_groups_found": len(timestamped_groups),
            "non_timestamped_kept": len(non_timestamped)
        }
    }


def apply_changes(settings: dict, result: dict) -> dict:
    """Apply the consolidation changes to settings."""
    allow_list = settings.get("permissions", {}).get("allow", [])

    # Remove timestamped permissions
    for perm in result["removed"]:
        if perm in allow_list:
            allow_list.remove(perm)

    # Add wildcards (avoid duplicates)
    for wildcard in result["wildcards_added"]:
        if wildcard not in allow_list:
            allow_list.append(wildcard)

    # Sort for consistency
    allow_list.sort()

    return settings


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate timestamped build output permissions with wildcards"
    )
    parser.add_argument(
        "--settings",
        required=True,
        help="Path to settings file to analyze and modify"
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
        result = {"error": error}
        print(json.dumps(result, indent=2))
        return

    # Analyze and consolidate
    result = consolidate_build_outputs(settings)
    result["dry_run"] = args.dry_run
    result["settings_path"] = args.settings

    # Apply changes if not dry-run
    if not args.dry_run and result["consolidated"] > 0:
        settings = apply_changes(settings, result)
        if save_settings(args.settings, settings):
            result["applied"] = True
        else:
            result["error"] = "Failed to save settings"
            result["applied"] = False
    else:
        result["applied"] = False

    # Output
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Text format
        print("=" * 60)
        print("BUILD OUTPUT CONSOLIDATION")
        print("=" * 60)
        print()
        print(f"Settings: {args.settings}")
        print(f"Mode: {'Dry-run' if args.dry_run else 'Apply changes'}")
        print()

        if result["consolidated"] > 0:
            print(f"PERMISSIONS TO CONSOLIDATE: {result['consolidated']}")
            print("\nRemoving:")
            for perm in result["removed"]:
                print(f"  - {perm}")
            print("\nAdding wildcards:")
            for wildcard in result["wildcards_added"]:
                print(f"  + {wildcard}")
        else:
            print("No timestamped permissions found to consolidate.")

        print()
        if not args.dry_run and result.get("applied"):
            print("✅ Changes applied successfully")
        elif args.dry_run:
            print("ℹ️  Dry-run mode: No files modified")


if __name__ == "__main__":
    main()
