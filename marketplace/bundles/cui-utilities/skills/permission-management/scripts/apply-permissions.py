#!/usr/bin/env python3
"""
Apply permissions to Claude Code settings files.

This script manages permissions in both global (~/.claude/settings.json) and
project-level settings (.claude/settings.json or .claude/settings.local.json).

Usage:
    python3 apply-permissions.py --action analyze [--settings-file PATH]
    python3 apply-permissions.py --action sync-scripts --scripts-file PATH
    python3 apply-permissions.py --action add --permission "Bash(foo:*)"
    python3 apply-permissions.py --action remove --permission "Bash(foo:*)"
    python3 apply-permissions.py --action ensure --permissions "Bash(a:*),Bash(b:*)"

Output: JSON with results
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional


def get_global_settings_path() -> Path:
    """Get path to global settings file."""
    return Path.home() / ".claude" / "settings.json"


def get_project_settings_path(project_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Get path to project settings file.

    Priority:
    1. .claude/settings.json (project-level, version-controlled)
    2. .claude/settings.local.json (personal overrides)

    Returns None if neither exists.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Check for version-controlled settings first
    settings_json = project_dir / ".claude" / "settings.json"
    if settings_json.exists():
        return settings_json

    # Fall back to local settings
    settings_local = project_dir / ".claude" / "settings.local.json"
    if settings_local.exists():
        return settings_local

    return None


def get_project_settings_path_for_write(project_dir: Optional[Path] = None) -> Path:
    """
    Get path for writing project settings.

    If settings.json exists, use it (version-controlled).
    Otherwise, use settings.local.json (personal).
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Check for existing settings.json first
    settings_json = project_dir / ".claude" / "settings.json"
    if settings_json.exists():
        return settings_json

    # Default to settings.local.json for personal/local changes
    return project_dir / ".claude" / "settings.local.json"


def load_settings(path: Path) -> dict:
    """Load settings from a JSON file."""
    if not path.exists():
        return {"permissions": {"allow": [], "deny": [], "ask": []}}

    try:
        with open(path, 'r') as f:
            data = json.load(f)
        # Ensure permissions structure exists
        if "permissions" not in data:
            data["permissions"] = {}
        for key in ["allow", "deny", "ask"]:
            if key not in data["permissions"]:
                data["permissions"][key] = []
        return data
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}", "permissions": {"allow": [], "deny": [], "ask": []}}


def save_settings(path: Path, data: dict) -> bool:
    """Save settings to a JSON file."""
    try:
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}", file=sys.stderr)
        return False


def analyze_settings(settings_path: Optional[str] = None) -> dict:
    """
    Analyze current settings configuration.

    Returns information about which settings files exist and their contents.
    """
    global_path = get_global_settings_path()
    project_path = get_project_settings_path()

    result = {
        "global": {
            "path": str(global_path),
            "exists": global_path.exists(),
            "permissions": None
        },
        "project": {
            "path": str(project_path) if project_path else None,
            "exists": project_path is not None,
            "type": None,
            "permissions": None
        },
        "effective_project_path": str(get_project_settings_path_for_write())
    }

    if global_path.exists():
        global_settings = load_settings(global_path)
        result["global"]["permissions"] = {
            "allow_count": len(global_settings.get("permissions", {}).get("allow", [])),
            "deny_count": len(global_settings.get("permissions", {}).get("deny", [])),
            "ask_count": len(global_settings.get("permissions", {}).get("ask", []))
        }

    if project_path:
        project_settings = load_settings(project_path)
        result["project"]["type"] = "version-controlled" if "settings.json" in str(project_path) and "local" not in str(project_path) else "local"
        result["project"]["permissions"] = {
            "allow_count": len(project_settings.get("permissions", {}).get("allow", [])),
            "deny_count": len(project_settings.get("permissions", {}).get("deny", [])),
            "ask_count": len(project_settings.get("permissions", {}).get("ask", []))
        }

    return result


def sync_script_permissions(scripts_file: str, target: str = "global") -> dict:
    """
    Sync script permissions from scripts.local.json to settings.

    Args:
        scripts_file: Path to scripts.local.json
        target: "global" or "project"

    Returns:
        Dict with added/removed counts
    """
    scripts_path = Path(scripts_file)
    if not scripts_path.exists():
        return {"error": f"Scripts file not found: {scripts_file}"}

    try:
        with open(scripts_path, 'r') as f:
            scripts_data = json.load(f)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in scripts file: {e}"}

    new_permissions = scripts_data.get("permissions", [])
    marketplace = scripts_data.get("marketplace", "unknown")

    # Determine target settings file
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings(settings_path)
    allow_list = settings["permissions"]["allow"]

    # Find and remove old script permissions for this marketplace
    old_script_permissions = [
        p for p in allow_list
        if ("scripts/*.sh" in p or "scripts/*.py" in p) and marketplace.replace("-", "") in p.replace("-", "").lower()
    ]

    # More precise: remove permissions containing /marketplace/bundles/
    old_script_permissions = [
        p for p in allow_list
        if "/marketplace/bundles/" in p and ("scripts/*.sh" in p or "scripts/*.py" in p)
    ]

    for old_perm in old_script_permissions:
        allow_list.remove(old_perm)

    # Add new permissions
    added = 0
    for perm in new_permissions:
        if perm not in allow_list:
            allow_list.append(perm)
            added += 1

    # Sort permissions
    allow_list.sort()

    # Save
    if save_settings(settings_path, settings):
        return {
            "success": True,
            "settings_file": str(settings_path),
            "removed": len(old_script_permissions),
            "added": added,
            "total_permissions": len(allow_list)
        }
    else:
        return {"error": "Failed to save settings"}


def add_permission(permission: str, target: str = "project") -> dict:
    """Add a permission to settings."""
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings(settings_path)
    allow_list = settings["permissions"]["allow"]

    if permission in allow_list:
        return {
            "success": True,
            "action": "already_exists",
            "settings_file": str(settings_path)
        }

    allow_list.append(permission)
    allow_list.sort()

    if save_settings(settings_path, settings):
        return {
            "success": True,
            "action": "added",
            "settings_file": str(settings_path)
        }
    else:
        return {"error": "Failed to save settings"}


def remove_permission(permission: str, target: str = "project") -> dict:
    """Remove a permission from settings."""
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings(settings_path)
    allow_list = settings["permissions"]["allow"]

    if permission not in allow_list:
        return {
            "success": True,
            "action": "not_found",
            "settings_file": str(settings_path)
        }

    allow_list.remove(permission)

    if save_settings(settings_path, settings):
        return {
            "success": True,
            "action": "removed",
            "settings_file": str(settings_path)
        }
    else:
        return {"error": "Failed to save settings"}


def ensure_permissions(permissions: list, target: str = "global") -> dict:
    """Ensure all specified permissions exist in settings."""
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings(settings_path)
    allow_list = settings["permissions"]["allow"]

    added = []
    already_exists = []

    for perm in permissions:
        if perm in allow_list:
            already_exists.append(perm)
        else:
            allow_list.append(perm)
            added.append(perm)

    if added:
        allow_list.sort()
        if not save_settings(settings_path, settings):
            return {"error": "Failed to save settings"}

    return {
        "success": True,
        "settings_file": str(settings_path),
        "added": added,
        "already_exists": already_exists,
        "added_count": len(added),
        "total_permissions": len(allow_list)
    }


def main():
    parser = argparse.ArgumentParser(description="Manage Claude Code permissions")
    parser.add_argument("--action", required=True,
                       choices=["analyze", "sync-scripts", "add", "remove", "ensure"],
                       help="Action to perform")
    parser.add_argument("--settings-file", help="Path to settings file (for analyze)")
    parser.add_argument("--scripts-file", help="Path to scripts.local.json (for sync-scripts)")
    parser.add_argument("--permission", help="Single permission (for add/remove)")
    parser.add_argument("--permissions", help="Comma-separated permissions (for ensure)")
    parser.add_argument("--target", default="global", choices=["global", "project"],
                       help="Target settings file (default: global)")
    parser.add_argument("--format", default="json", choices=["json", "text"],
                       help="Output format")

    args = parser.parse_args()

    result = {}

    if args.action == "analyze":
        result = analyze_settings(args.settings_file)

    elif args.action == "sync-scripts":
        if not args.scripts_file:
            result = {"error": "--scripts-file required for sync-scripts action"}
        else:
            result = sync_script_permissions(args.scripts_file, args.target)

    elif args.action == "add":
        if not args.permission:
            result = {"error": "--permission required for add action"}
        else:
            result = add_permission(args.permission, args.target)

    elif args.action == "remove":
        if not args.permission:
            result = {"error": "--permission required for remove action"}
        else:
            result = remove_permission(args.permission, args.target)

    elif args.action == "ensure":
        if not args.permissions:
            result = {"error": "--permissions required for ensure action"}
        else:
            perms = [p.strip() for p in args.permissions.split(",")]
            result = ensure_permissions(perms, args.target)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
