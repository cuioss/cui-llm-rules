#!/usr/bin/env python3
"""
ensure-marketplace-wildcards.py

Ensure marketplace bundle wildcards exist in global settings.

For each bundle in marketplace.json:
- Adds Skill({bundle-name}:*) if bundle has skills
- Adds SlashCommand(/{bundle-name}:*) if bundle has commands

Usage:
    python3 ensure-marketplace-wildcards.py --settings PATH --marketplace-json PATH [--dry-run]

Output: JSON with added and already_present counts
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


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


def load_marketplace(path: str) -> tuple[dict, Optional[str]]:
    """Load marketplace.json file."""
    marketplace_path = Path(path)

    if not marketplace_path.exists():
        return {}, f"Marketplace file not found: {path}"

    try:
        with open(marketplace_path, 'r') as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return {}, f"Invalid JSON in {path}: {e}"


def has_skills(bundle: dict) -> bool:
    """Check if a bundle has skills defined."""
    skills = bundle.get("skills", [])
    if isinstance(skills, list):
        return len(skills) > 0
    return False


def has_commands(bundle: dict) -> bool:
    """Check if a bundle has commands defined."""
    commands = bundle.get("commands", [])
    if isinstance(commands, list):
        return len(commands) > 0
    return False


def generate_required_wildcards(marketplace: dict) -> list[str]:
    """Generate list of required wildcard permissions from marketplace."""
    wildcards = []

    bundles = marketplace.get("bundles", [])

    for bundle in bundles:
        bundle_name = bundle.get("name", "")
        if not bundle_name:
            continue

        # Add Skill wildcard if bundle has skills
        if has_skills(bundle):
            wildcards.append(f"Skill({bundle_name}:*)")

        # Add SlashCommand wildcard if bundle has commands
        if has_commands(bundle):
            wildcards.append(f"SlashCommand(/{bundle_name}:*)")

    return wildcards


def ensure_marketplace_wildcards(
    settings: dict,
    marketplace: dict
) -> dict:
    """
    Ensure marketplace wildcards exist in settings.

    Returns dict with:
        - added: List of wildcards that were/would be added
        - already_present: Count of wildcards already in settings
        - total: Total wildcards checked
    """
    allow_list = settings.get("permissions", {}).get("allow", [])
    allow_set = set(allow_list)

    required_wildcards = generate_required_wildcards(marketplace)

    added = []
    already_present = 0

    for wildcard in required_wildcards:
        if wildcard in allow_set:
            already_present += 1
        else:
            added.append(wildcard)

    return {
        "added": added,
        "already_present": already_present,
        "total": len(required_wildcards),
        "bundles_analyzed": len(marketplace.get("bundles", []))
    }


def apply_wildcards(settings: dict, wildcards_to_add: list[str]) -> dict:
    """Add wildcards to settings."""
    allow_list = settings.get("permissions", {}).get("allow", [])

    for wildcard in wildcards_to_add:
        if wildcard not in allow_list:
            allow_list.append(wildcard)

    # Sort for consistency
    allow_list.sort()

    return settings


def main():
    parser = argparse.ArgumentParser(
        description="Ensure marketplace bundle wildcards exist in global settings"
    )
    parser.add_argument(
        "--settings",
        required=True,
        help="Path to settings file to update"
    )
    parser.add_argument(
        "--marketplace-json",
        required=True,
        help="Path to marketplace.json file"
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

    # Load marketplace
    marketplace, error = load_marketplace(args.marketplace_json)
    if error:
        result = {"error": error}
        print(json.dumps(result, indent=2))
        return

    # Analyze and generate wildcards
    result = ensure_marketplace_wildcards(settings, marketplace)
    result["dry_run"] = args.dry_run
    result["settings_path"] = args.settings
    result["marketplace_path"] = args.marketplace_json

    # Apply changes if not dry-run
    if not args.dry_run and len(result["added"]) > 0:
        settings = apply_wildcards(settings, result["added"])
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
        print("MARKETPLACE WILDCARD VERIFICATION")
        print("=" * 60)
        print()
        print(f"Settings: {args.settings}")
        print(f"Marketplace: {args.marketplace_json}")
        print(f"Mode: {'Dry-run' if args.dry_run else 'Apply changes'}")
        print()

        print(f"Bundles analyzed: {result['bundles_analyzed']}")
        print(f"Total wildcards required: {result['total']}")
        print(f"Already present: {result['already_present']}")
        print()

        if result["added"]:
            print("ADDING:")
            for wildcard in result["added"]:
                print(f"  + {wildcard}")
        else:
            print("All marketplace wildcards already present.")

        print()
        if not args.dry_run and result.get("applied"):
            print("✅ Changes applied successfully")
        elif args.dry_run:
            print("ℹ️  Dry-run mode: No files modified")


if __name__ == "__main__":
    main()
