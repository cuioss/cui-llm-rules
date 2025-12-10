#!/usr/bin/env python3
"""Permission management tools for Claude Code settings.

Consolidated script providing:
- generate-wildcards: Generate permission wildcards from marketplace inventory
- detect-redundant: Detect redundant permissions between global and local settings
- detect-suspicious: Detect suspicious permissions matching anti-patterns
- consolidate: Consolidate timestamped build output permissions with wildcards
- ensure-wildcards: Ensure marketplace bundle wildcards exist in global settings
- apply-fixes: Apply safe fixes to permission settings
- apply: Manage permissions (analyze, sync-scripts, add, remove, ensure)
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1


# =============================================================================
# Shared Utilities
# =============================================================================

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
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False


def output_result(result: dict, format_type: str = "json") -> None:
    """Output result in specified format."""
    if format_type == "json":
        print(json.dumps(result, indent=2))


# =============================================================================
# generate-wildcards subcommand
# =============================================================================

def extract_command_prefix(command_name: str) -> str:
    """Extract the prefix from a command name."""
    parts = command_name.split("-")
    if len(parts) > 1:
        return parts[0]
    return command_name


def extract_skill_prefix(skill_name: str) -> str:
    """Extract the prefix from a skill name."""
    parts = skill_name.split("-")
    if len(parts) > 1:
        return parts[0]
    return skill_name


def generate_skill_wildcards(bundles: list[dict]) -> list[str]:
    """Generate Skill wildcards for bundles with skills."""
    wildcards = []
    for bundle in bundles:
        if bundle.get("skills") and len(bundle["skills"]) > 0:
            wildcards.append(f"Skill({bundle['name']}:*)")
    return sorted(wildcards)


def generate_command_bundle_wildcards(bundles: list[dict]) -> list[str]:
    """Generate SlashCommand wildcards for bundles with commands."""
    wildcards = []
    for bundle in bundles:
        if bundle.get("commands") and len(bundle["commands"]) > 0:
            wildcards.append(f"SlashCommand(/{bundle['name']}:*)")
    return sorted(wildcards)


def generate_command_shortform_permissions(bundles: list[dict]) -> list[str]:
    """Generate SlashCommand permissions for each command."""
    permissions = []
    for bundle in bundles:
        for command in bundle.get("commands", []):
            permissions.append(f"SlashCommand(/{command['name']}:*)")
    return sorted(permissions)


def count_scripts(bundles: list[dict]) -> int:
    """Count total scripts in bundles."""
    total = 0
    for bundle in bundles:
        total += len(bundle.get("scripts", []))
    return total


def analyze_naming_patterns(bundles: list[dict]) -> dict[str, Any]:
    """Analyze naming patterns in skills and commands."""
    skill_prefixes = set()
    command_prefixes = set()
    bundle_names = []

    for bundle in bundles:
        bundle_names.append(bundle["name"])
        for skill in bundle.get("skills", []):
            prefix = extract_skill_prefix(skill["name"])
            skill_prefixes.add(prefix)
        for command in bundle.get("commands", []):
            prefix = extract_command_prefix(command["name"])
            command_prefixes.add(prefix)

    return {
        "bundle_names": sorted(bundle_names),
        "skill_prefixes": sorted(skill_prefixes),
        "command_prefixes": sorted(command_prefixes)
    }


def build_bundle_summary(bundles: list[dict]) -> list[dict]:
    """Build summary of each bundle's contents."""
    summaries = []
    for bundle in bundles:
        summaries.append({
            "name": bundle["name"],
            "skills": {
                "count": len(bundle.get("skills", [])),
                "names": [s["name"] for s in bundle.get("skills", [])]
            },
            "commands": {
                "count": len(bundle.get("commands", [])),
                "names": [c["name"] for c in bundle.get("commands", [])]
            },
            "scripts": {
                "count": len(bundle.get("scripts", [])),
                "names": [s["name"] for s in bundle.get("scripts", [])]
            }
        })
    return summaries


def cmd_generate_wildcards(args) -> int:
    """Handle generate-wildcards subcommand."""
    try:
        if args.input:
            with open(args.input, "r") as f:
                inventory = json.load(f)
        else:
            inventory = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        return EXIT_ERROR
    except FileNotFoundError:
        print(json.dumps({"error": f"Input file not found: {args.input}"}))
        return EXIT_ERROR

    bundles = inventory.get("bundles", [])

    if not bundles:
        result = {
            "error": "No bundles found in inventory",
            "statistics": {
                "bundles_scanned": 0,
                "skills_found": 0,
                "commands_found": 0,
                "scripts_found": 0,
                "wildcards_generated": 0
            }
        }
        print(json.dumps(result, indent=2))
        return EXIT_SUCCESS

    skill_wildcards = generate_skill_wildcards(bundles)
    command_bundle_wildcards = generate_command_bundle_wildcards(bundles)
    command_shortform = generate_command_shortform_permissions(bundles)

    stats = inventory.get("statistics", {})
    total_scripts = count_scripts(bundles)
    wildcards_generated = len(skill_wildcards) + len(command_bundle_wildcards) + len(command_shortform)
    patterns = analyze_naming_patterns(bundles)
    bundle_summary = build_bundle_summary(bundles)

    result = {
        "statistics": {
            "bundles_scanned": stats.get("total_bundles", len(bundles)),
            "skills_found": stats.get("total_skills", 0),
            "commands_found": stats.get("total_commands", 0),
            "scripts_found": total_scripts,
            "wildcards_generated": wildcards_generated,
            "breakdown": {
                "skill_bundle_wildcards": len(skill_wildcards),
                "command_bundle_wildcards": len(command_bundle_wildcards),
                "command_shortform_permissions": len(command_shortform)
            }
        },
        "naming_patterns": patterns,
        "bundle_summary": bundle_summary,
        "permissions": {
            "skill_wildcards": skill_wildcards,
            "command_bundle_wildcards": command_bundle_wildcards,
            "command_shortform": command_shortform
        },
        "coverage": {
            "skills_covered": f"{stats.get('total_skills', 0)} skills covered by {len(skill_wildcards)} bundle wildcards",
            "commands_covered": f"{stats.get('total_commands', 0)} commands covered by {len(command_bundle_wildcards)} bundle wildcards + {len(command_shortform)} short-form permissions",
            "scripts_note": f"{total_scripts} scripts - handled by relative path architecture (no permissions needed)"
        }
    }
    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


# =============================================================================
# detect-redundant subcommand
# =============================================================================

def is_marketplace_permission(permission: str) -> bool:
    """Check if a permission is a marketplace permission."""
    return permission.startswith("Skill(") or permission.startswith("SlashCommand(/")


def extract_permission_parts(permission: str) -> tuple[str, str]:
    """Extract the type and pattern from a permission string."""
    match = re.match(r'^(\w+)\((.+)\)$', permission)
    if match:
        return match.group(1), match.group(2)
    return permission, ""


def is_covered_by_wildcard(specific: str, broader: str) -> bool:
    """Check if a specific permission is covered by a broader wildcard pattern."""
    spec_type, spec_pattern = extract_permission_parts(specific)
    broad_type, broad_pattern = extract_permission_parts(broader)

    if spec_type != broad_type:
        return False

    if broad_pattern.endswith(':*'):
        prefix = broad_pattern[:-1]
        if spec_pattern.startswith(prefix):
            return True

    if broad_type in ('Read', 'Write', 'Edit'):
        broad_base = broad_pattern.rstrip('*').rstrip('/')
        spec_base = spec_pattern.rstrip('*').rstrip('/')
        if spec_base.startswith(broad_base) and len(spec_base) > len(broad_base):
            return True

    return False


def cmd_detect_redundant(args) -> int:
    """Handle detect-redundant subcommand."""
    global_settings, global_error = load_settings(args.global_settings)
    if global_error:
        print(json.dumps({"error": global_error, "global_exists": False}))
        return EXIT_ERROR

    local_settings, local_error = load_settings(args.local_settings)
    if local_error:
        print(json.dumps({"error": local_error, "local_exists": False}))
        return EXIT_ERROR

    global_allow = set(global_settings.get("permissions", {}).get("allow", []))
    local_allow = local_settings.get("permissions", {}).get("allow", [])

    redundant = []
    marketplace_in_local = []

    for local_perm in local_allow:
        if local_perm in global_allow:
            redundant.append({
                "permission": local_perm,
                "reason": "Exact duplicate exists in global settings",
                "type": "exact_duplicate",
                "covered_by": local_perm
            })
            continue

        if is_marketplace_permission(local_perm):
            marketplace_in_local.append({
                "permission": local_perm,
                "reason": "Marketplace permissions should be in global settings",
                "type": "marketplace_permission"
            })
            continue

        for global_perm in global_allow:
            if is_covered_by_wildcard(local_perm, global_perm):
                redundant.append({
                    "permission": local_perm,
                    "reason": "Covered by broader wildcard in global settings",
                    "type": "covered_by_wildcard",
                    "covered_by": global_perm
                })
                break

    result = {
        "redundant": redundant,
        "marketplace_in_local": marketplace_in_local,
        "summary": {
            "redundant_count": len(redundant),
            "marketplace_in_local_count": len(marketplace_in_local),
            "total_issues": len(redundant) + len(marketplace_in_local),
            "local_permissions_checked": len(local_allow),
            "global_permissions_count": len(global_allow)
        },
        "global_exists": True,
        "local_exists": True,
        "global_path": args.global_settings,
        "local_path": args.local_settings
    }
    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


# =============================================================================
# detect-suspicious subcommand
# =============================================================================

SUSPICIOUS_PATTERNS = [
    {"pattern": r"^Write\(\/\*\*\)$", "reason": "Root write access", "severity": "high", "category": "root_access"},
    {"pattern": r"^Read\(\/\*\*\)$", "reason": "Root read access", "severity": "high", "category": "root_access"},
    {"pattern": r"^Write\(\/etc\/.*\)$", "reason": "System configuration write access", "severity": "high", "category": "system_directory"},
    {"pattern": r"^Write\(\/dev\/.*\)$", "reason": "Device file write access", "severity": "high", "category": "system_directory"},
    {"pattern": r"^Write\(\/sys\/.*\)$", "reason": "System kernel interface write access", "severity": "high", "category": "system_directory"},
    {"pattern": r"^Write\(\/proc\/.*\)$", "reason": "Process information write access", "severity": "high", "category": "system_directory"},
    {"pattern": r"^Write\(\/boot\/.*\)$", "reason": "Boot files write access", "severity": "high", "category": "system_directory"},
    {"pattern": r"^Write\(\/root\/.*\)$", "reason": "Root user home directory write access", "severity": "high", "category": "system_directory"},
    {"pattern": r"^Bash\(sudo:.*\)$", "reason": "Privilege escalation - sudo access", "severity": "high", "category": "dangerous_command"},
    {"pattern": r"^Bash\(rm:-rf.*\)$", "reason": "Recursive force delete", "severity": "high", "category": "dangerous_command"},
    {"pattern": r"^Bash\(dd:.*\)$", "reason": "Low-level disk operations", "severity": "high", "category": "dangerous_command"},
    {"pattern": r"^Bash\(mkfs:.*\)$", "reason": "Filesystem creation", "severity": "high", "category": "dangerous_command"},
    {"pattern": r"^Bash\(fdisk:.*\)$", "reason": "Disk partitioning", "severity": "high", "category": "dangerous_command"},
    {"pattern": r".*\|\s*bash.*", "reason": "Piping to bash", "severity": "high", "category": "dangerous_command"},
    {"pattern": r".*\|\s*sh.*", "reason": "Piping to sh", "severity": "high", "category": "dangerous_command"},
    {"pattern": r"^Write\(\/tmp\/.*\)$", "reason": "System temp directory write access", "severity": "medium", "category": "temp_directory"},
    {"pattern": r"^Write\(\/var\/tmp\/.*\)$", "reason": "Persistent temp directory write access", "severity": "medium", "category": "temp_directory"},
    {"pattern": r"^Write\(\/private\/tmp\/.*\)$", "reason": "macOS private temp directory write access", "severity": "medium", "category": "temp_directory"},
    {"pattern": r"^Read\(\/\/Users\/\*\*\)$", "reason": "All users read access", "severity": "medium", "category": "broad_access"},
    {"pattern": r"^Write\(\/\/Users\/\*\*\)$", "reason": "All users write access", "severity": "high", "category": "broad_access"},
    {"pattern": r"^Read\(\/\/home\/\*\*\)$", "reason": "All home directories read access", "severity": "medium", "category": "broad_access"},
    {"pattern": r"^Write\(\/\/home\/\*\*\)$", "reason": "All home directories write access", "severity": "high", "category": "broad_access"},
    {"pattern": r"^Bash\(curl:\*\)$", "reason": "Unrestricted curl access", "severity": "low", "category": "network_access"},
    {"pattern": r"^Bash\(wget:\*\)$", "reason": "Unrestricted wget access", "severity": "low", "category": "network_access"},
]


def load_approved_permissions(approved_file: Optional[str]) -> set[str]:
    """Load user-approved permissions from run-configuration file."""
    if not approved_file:
        return set()

    approved_path = Path(approved_file)
    if not approved_path.exists():
        return set()

    try:
        with open(approved_path, 'r') as f:
            data = json.load(f)
        commands = data.get("commands", {})
        setup_perms = commands.get("setup-project-permissions", {})
        approved_list = setup_perms.get("user_approved_permissions", [])
        return set(approved_list)
    except (json.JSONDecodeError, KeyError):
        return set()


def check_permission(permission: str) -> Optional[dict]:
    """Check if a permission matches any suspicious pattern."""
    for pattern_info in SUSPICIOUS_PATTERNS:
        if re.match(pattern_info["pattern"], permission, re.IGNORECASE):
            return {
                "permission": permission,
                "reason": pattern_info["reason"],
                "severity": pattern_info["severity"],
                "category": pattern_info["category"]
            }
    return None


def cmd_detect_suspicious(args) -> int:
    """Handle detect-suspicious subcommand."""
    settings, error = load_settings(args.settings)
    if error:
        print(json.dumps({"error": error}))
        return EXIT_ERROR

    approved_permissions = load_approved_permissions(args.approved_file)
    allow_list = settings.get("permissions", {}).get("allow", [])

    suspicious = []
    already_approved = []

    for permission in allow_list:
        if permission in approved_permissions:
            check_result = check_permission(permission)
            if check_result:
                already_approved.append(permission)
            continue

        check_result = check_permission(permission)
        if check_result:
            suspicious.append(check_result)

    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for item in suspicious:
        severity_counts[item["severity"]] += 1

    result = {
        "suspicious": suspicious,
        "already_approved": already_approved,
        "summary": {
            "total_suspicious": len(suspicious),
            "already_approved_count": len(already_approved),
            "by_severity": severity_counts,
            "permissions_checked": len(allow_list)
        },
        "settings_path": args.settings
    }
    if args.approved_file:
        result["approved_file"] = args.approved_file

    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


# =============================================================================
# consolidate subcommand
# =============================================================================

TIMESTAMP_PATTERN = re.compile(r'^(\w+)\((.*/)?(.+)-(\d{4}-\d{2}-\d{2}-\d{6})\.(\w+)\)$')
DATE_PATTERN = re.compile(r'^(\w+)\((.*/)?(.+)-(\d{4}-\d{2}-\d{2})\.(\w+)\)$')


def parse_timestamped_permission(permission: str) -> Optional[dict]:
    """Parse a permission to check if it contains a timestamp pattern."""
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
    """Generate a wildcard pattern from a list of parsed timestamped permissions."""
    if not parsed_permissions:
        return ""

    first = parsed_permissions[0]
    perm_type = first["type"]
    base_name = first["base_name"]
    extension = first["extension"]
    path_prefixes = set(p["path_prefix"] for p in parsed_permissions)

    if len(path_prefixes) == 1:
        path_prefix = first["path_prefix"]
        return f"{perm_type}({path_prefix}{base_name}-*.{extension})"

    return f"{perm_type}(**/{base_name}-*.{extension})"


def cmd_consolidate(args) -> int:
    """Handle consolidate subcommand."""
    settings, error = load_settings(args.settings)
    if error:
        print(json.dumps({"error": error}))
        return EXIT_ERROR

    allow_list = settings.get("permissions", {}).get("allow", [])
    timestamped_groups = defaultdict(list)
    non_timestamped = []

    for permission in allow_list:
        parsed = parse_timestamped_permission(permission)
        if parsed:
            key = (parsed["type"], parsed["base_name"], parsed["extension"])
            timestamped_groups[key].append(parsed)
        else:
            non_timestamped.append(permission)

    wildcards_to_add = []
    permissions_to_remove = []

    for key, group in timestamped_groups.items():
        if len(group) >= 1:
            wildcard = generate_wildcard(group)
            wildcards_to_add.append(wildcard)
            permissions_to_remove.extend([p["permission"] for p in group])

    result = {
        "consolidated": len(permissions_to_remove),
        "removed": permissions_to_remove,
        "wildcards_added": wildcards_to_add,
        "changes": {
            "timestamped_groups_found": len(timestamped_groups),
            "non_timestamped_kept": len(non_timestamped)
        },
        "dry_run": args.dry_run,
        "settings_path": args.settings
    }

    if not args.dry_run and result["consolidated"] > 0:
        for perm in permissions_to_remove:
            if perm in allow_list:
                allow_list.remove(perm)
        for wildcard in wildcards_to_add:
            if wildcard not in allow_list:
                allow_list.append(wildcard)
        allow_list.sort()

        if save_settings(args.settings, settings):
            result["applied"] = True
        else:
            result["error"] = "Failed to save settings"
            result["applied"] = False
    else:
        result["applied"] = False

    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


# =============================================================================
# ensure-wildcards subcommand
# =============================================================================

def has_skills(bundle: dict) -> bool:
    """Check if a bundle has skills defined."""
    skills = bundle.get("skills", [])
    return isinstance(skills, list) and len(skills) > 0


def has_commands(bundle: dict) -> bool:
    """Check if a bundle has commands defined."""
    commands = bundle.get("commands", [])
    return isinstance(commands, list) and len(commands) > 0


def generate_required_wildcards(marketplace: dict) -> list[str]:
    """Generate list of required wildcard permissions from marketplace."""
    wildcards = []
    bundles = marketplace.get("bundles", [])

    for bundle in bundles:
        bundle_name = bundle.get("name", "")
        if not bundle_name:
            continue

        if has_skills(bundle):
            wildcards.append(f"Skill({bundle_name}:*)")
        if has_commands(bundle):
            wildcards.append(f"SlashCommand(/{bundle_name}:*)")

    return wildcards


def cmd_ensure_wildcards(args) -> int:
    """Handle ensure-wildcards subcommand."""
    settings, error = load_settings(args.settings)
    if error:
        print(json.dumps({"error": error}))
        return EXIT_ERROR

    marketplace_path = Path(args.marketplace_json)
    if not marketplace_path.exists():
        print(json.dumps({"error": f"Marketplace file not found: {args.marketplace_json}"}))
        return EXIT_ERROR

    try:
        with open(marketplace_path, 'r') as f:
            marketplace = json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON in {args.marketplace_json}: {e}"}))
        return EXIT_ERROR

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

    result = {
        "added": added,
        "already_present": already_present,
        "total": len(required_wildcards),
        "bundles_analyzed": len(marketplace.get("bundles", [])),
        "dry_run": args.dry_run,
        "settings_path": args.settings,
        "marketplace_path": args.marketplace_json
    }

    if not args.dry_run and len(added) > 0:
        for wildcard in added:
            if wildcard not in allow_list:
                allow_list.append(wildcard)
        allow_list.sort()

        if save_settings(args.settings, settings):
            result["applied"] = True
        else:
            result["error"] = "Failed to save settings"
            result["applied"] = False
    else:
        result["applied"] = False

    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


# =============================================================================
# apply-fixes subcommand
# =============================================================================

DEFAULT_PERMISSIONS = ["Edit(.plan/**)", "Write(.plan/**)"]


def normalize_path_perm(permission: str) -> tuple[str, bool]:
    """Normalize a permission path."""
    match = re.match(r'^(\w+)\((.+?)(/)?\)$', permission)
    if not match:
        return permission, False

    perm_type = match.group(1)
    path = match.group(2)
    trailing = match.group(3)

    if trailing and not path.endswith('*'):
        return f"{perm_type}({path})", True

    return permission, False


def remove_duplicates(perm_list: list[str]) -> tuple[list[str], int]:
    """Remove duplicate permissions from a list."""
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
    """Process a single permission list: normalize, dedupe, sort."""
    paths_fixed = 0
    normalized = []

    for perm in perm_list:
        norm_perm, changed = normalize_path_perm(perm)
        normalized.append(norm_perm)
        if changed:
            paths_fixed += 1

    deduplicated, dups = remove_duplicates(normalized)
    sorted_list = sorted(deduplicated)
    was_sorted = sorted_list != deduplicated

    return sorted_list, paths_fixed, dups, was_sorted


def add_default_permissions(allow_list: list[str]) -> list[str]:
    """Add default permissions if missing."""
    added = []
    for default_perm in DEFAULT_PERMISSIONS:
        if default_perm not in allow_list:
            allow_list.append(default_perm)
            added.append(default_perm)
    return added


def cmd_apply_fixes(args) -> int:
    """Handle apply-fixes subcommand."""
    settings, error = load_settings(args.settings)
    if error:
        print(json.dumps({"error": error}))
        return EXIT_ERROR

    total_duplicates = 0
    total_paths_fixed = 0
    was_sorted = False

    for key in ["allow", "deny", "ask"]:
        perm_list = settings.get("permissions", {}).get(key, [])
        processed, paths_fixed, dups, sorted_flag = process_permission_list(perm_list)

        settings["permissions"][key] = processed
        total_paths_fixed += paths_fixed
        total_duplicates += dups
        was_sorted = was_sorted or sorted_flag

    defaults_added = []
    allow_list = settings["permissions"]["allow"]
    defaults_added = add_default_permissions(allow_list)
    if defaults_added:
        settings["permissions"]["allow"] = sorted(allow_list)
        was_sorted = True

    changes_made = total_duplicates > 0 or total_paths_fixed > 0 or len(defaults_added) > 0 or was_sorted

    result = {
        "duplicates_removed": total_duplicates,
        "paths_fixed": total_paths_fixed,
        "defaults_added": defaults_added,
        "sorted": was_sorted,
        "changes_made": changes_made,
        "dry_run": args.dry_run,
        "settings_path": args.settings
    }

    if not args.dry_run and changes_made:
        result["applied"] = save_settings(args.settings, settings)
        if not result["applied"]:
            result["error"] = "Failed to save settings"
    else:
        result["applied"] = False

    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


# =============================================================================
# apply subcommand (manage permissions)
# =============================================================================

def get_global_settings_path() -> Path:
    """Get path to global settings file."""
    return Path.home() / ".claude" / "settings.json"


def get_project_settings_path(project_dir: Optional[Path] = None) -> Optional[Path]:
    """Get path to project settings file."""
    if project_dir is None:
        project_dir = Path.cwd()

    settings_json = project_dir / ".claude" / "settings.json"
    if settings_json.exists():
        return settings_json

    settings_local = project_dir / ".claude" / "settings.local.json"
    if settings_local.exists():
        return settings_local

    return None


def get_project_settings_path_for_write(project_dir: Optional[Path] = None) -> Path:
    """Get path for writing project settings."""
    if project_dir is None:
        project_dir = Path.cwd()

    settings_json = project_dir / ".claude" / "settings.json"
    if settings_json.exists():
        return settings_json

    return project_dir / ".claude" / "settings.local.json"


def load_settings_path(path: Path) -> dict:
    """Load settings from a Path."""
    if not path.exists():
        return {"permissions": {"allow": [], "deny": [], "ask": []}}

    try:
        with open(path, 'r') as f:
            data = json.load(f)
        if "permissions" not in data:
            data["permissions"] = {}
        for key in ["allow", "deny", "ask"]:
            if key not in data["permissions"]:
                data["permissions"][key] = []
        return data
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}", "permissions": {"allow": [], "deny": [], "ask": []}}


def analyze_settings_action(settings_path: Optional[str] = None) -> dict:
    """Analyze current settings configuration."""
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
        global_settings = load_settings_path(global_path)
        result["global"]["permissions"] = {
            "allow_count": len(global_settings.get("permissions", {}).get("allow", [])),
            "deny_count": len(global_settings.get("permissions", {}).get("deny", [])),
            "ask_count": len(global_settings.get("permissions", {}).get("ask", []))
        }

    if project_path:
        project_settings = load_settings_path(project_path)
        result["project"]["type"] = "version-controlled" if "settings.json" in str(project_path) and "local" not in str(project_path) else "local"
        result["project"]["permissions"] = {
            "allow_count": len(project_settings.get("permissions", {}).get("allow", [])),
            "deny_count": len(project_settings.get("permissions", {}).get("deny", [])),
            "ask_count": len(project_settings.get("permissions", {}).get("ask", []))
        }

    return result


# Executor-only permission pattern
EXECUTOR_PERMISSION = "Bash(python3 .plan/execute-script.py:*)"
OVERLY_BROAD_PYTHON = "Bash(python3:*)"


def is_individual_script_permission(permission: str) -> bool:
    """Check if permission is an individual marketplace script path permission."""
    # Matches: Bash(python3 /path/to/marketplace/bundles/.../scripts/*:*)
    return (
        permission.startswith("Bash(python3 ") and
        "/marketplace/bundles/" in permission and
        "/scripts" in permission
    )


def ensure_executor_permission(target: str = "global", dry_run: bool = False) -> dict:
    """Ensure the executor permission exists (executor-only pattern).

    The executor pattern uses a single permission for all script execution:
    - Bash(python3 .plan/execute-script.py:*)

    This replaces the need for individual script path permissions since
    the executor invokes scripts via subprocess (not checked by Claude Code).
    """
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings_path(settings_path)
    allow_list = settings["permissions"]["allow"]

    result = {
        "executor_permission": EXECUTOR_PERMISSION,
        "settings_file": str(settings_path),
        "dry_run": dry_run
    }

    if EXECUTOR_PERMISSION in allow_list:
        result["action"] = "already_exists"
        result["success"] = True
        return result

    if not dry_run:
        allow_list.append(EXECUTOR_PERMISSION)
        allow_list.sort()
        if save_settings(str(settings_path), settings):
            result["action"] = "added"
            result["success"] = True
        else:
            result["error"] = "Failed to save settings"
            result["success"] = False
    else:
        result["action"] = "would_add"
        result["success"] = True

    return result


def cleanup_script_permissions(target: str = "global", dry_run: bool = False,
                                remove_broad_python: bool = False) -> dict:
    """Remove redundant individual script permissions (executor-only pattern).

    With the executor pattern, individual script permissions are unnecessary:
    - Removes: Bash(python3 /path/to/marketplace/bundles/.../scripts/*:*)
    - Optionally removes: Bash(python3:*) (overly broad)

    The executor permission handles all script execution via subprocess.
    """
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings_path(settings_path)
    allow_list = settings["permissions"]["allow"]

    # Find permissions to remove
    individual_scripts = [p for p in allow_list if is_individual_script_permission(p)]
    broad_python = OVERLY_BROAD_PYTHON in allow_list and remove_broad_python

    result = {
        "settings_file": str(settings_path),
        "individual_script_permissions": individual_scripts,
        "individual_count": len(individual_scripts),
        "broad_python_found": OVERLY_BROAD_PYTHON in allow_list,
        "broad_python_removed": broad_python,
        "dry_run": dry_run
    }

    if not individual_scripts and not broad_python:
        result["action"] = "nothing_to_remove"
        result["success"] = True
        return result

    if not dry_run:
        # Remove individual script permissions
        for perm in individual_scripts:
            allow_list.remove(perm)

        # Optionally remove overly broad python permission
        if broad_python:
            allow_list.remove(OVERLY_BROAD_PYTHON)

        if save_settings(str(settings_path), settings):
            result["action"] = "removed"
            result["success"] = True
            result["total_removed"] = len(individual_scripts) + (1 if broad_python else 0)
        else:
            result["error"] = "Failed to save settings"
            result["success"] = False
    else:
        result["action"] = "would_remove"
        result["success"] = True
        result["total_would_remove"] = len(individual_scripts) + (1 if broad_python else 0)

    return result


def migrate_to_executor_pattern(target: str = "global", dry_run: bool = False,
                                 remove_broad_python: bool = False) -> dict:
    """Full migration to executor-only permission pattern.

    Combines:
    1. ensure_executor_permission - adds executor permission
    2. cleanup_script_permissions - removes redundant individual permissions

    Result: Single permission for all script execution instead of N permissions.
    """
    # Step 1: Ensure executor permission exists
    ensure_result = ensure_executor_permission(target, dry_run)
    if not ensure_result.get("success"):
        return {"error": ensure_result.get("error"), "step": "ensure_executor"}

    # Step 2: Cleanup redundant permissions
    cleanup_result = cleanup_script_permissions(target, dry_run, remove_broad_python)
    if not cleanup_result.get("success"):
        return {"error": cleanup_result.get("error"), "step": "cleanup"}

    return {
        "success": True,
        "settings_file": ensure_result["settings_file"],
        "dry_run": dry_run,
        "executor": {
            "permission": EXECUTOR_PERMISSION,
            "action": ensure_result["action"]
        },
        "cleanup": {
            "individual_removed": cleanup_result.get("total_removed", 0) if not dry_run
                                  else cleanup_result.get("total_would_remove", 0),
            "individual_permissions": cleanup_result["individual_script_permissions"],
            "broad_python_removed": cleanup_result["broad_python_removed"]
        },
        "summary": f"Migrated to executor-only pattern: 1 permission replaces {cleanup_result['individual_count']} individual script permissions"
    }


def sync_script_permissions(scripts_file: str, target: str = "global") -> dict:
    """DEPRECATED: Use migrate_to_executor_pattern instead.

    This function is kept for backward compatibility but now just ensures
    the executor permission exists. Individual script permissions are no
    longer needed with the executor pattern.
    """
    # Just ensure executor permission exists - ignore scripts_file
    result = ensure_executor_permission(target, dry_run=False)
    result["deprecated"] = True
    result["migration_note"] = "sync-scripts is deprecated. Use 'migrate-executor' action instead."
    return result


def add_permission_action(permission: str, target: str = "project") -> dict:
    """Add a permission to settings."""
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings_path(settings_path)
    allow_list = settings["permissions"]["allow"]

    if permission in allow_list:
        return {"success": True, "action": "already_exists", "settings_file": str(settings_path)}

    allow_list.append(permission)
    allow_list.sort()

    if save_settings(str(settings_path), settings):
        return {"success": True, "action": "added", "settings_file": str(settings_path)}
    else:
        return {"error": "Failed to save settings"}


def remove_permission_action(permission: str, target: str = "project") -> dict:
    """Remove a permission from settings."""
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings_path(settings_path)
    allow_list = settings["permissions"]["allow"]

    if permission not in allow_list:
        return {"success": True, "action": "not_found", "settings_file": str(settings_path)}

    allow_list.remove(permission)

    if save_settings(str(settings_path), settings):
        return {"success": True, "action": "removed", "settings_file": str(settings_path)}
    else:
        return {"error": "Failed to save settings"}


def ensure_permissions_action(permissions: list, target: str = "global") -> dict:
    """Ensure all specified permissions exist in settings."""
    if target == "global":
        settings_path = get_global_settings_path()
    else:
        settings_path = get_project_settings_path_for_write()

    settings = load_settings_path(settings_path)
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
        if not save_settings(str(settings_path), settings):
            return {"error": "Failed to save settings"}

    return {
        "success": True,
        "settings_file": str(settings_path),
        "added": added,
        "already_exists": already_exists,
        "added_count": len(added),
        "total_permissions": len(allow_list)
    }


def cmd_apply(args) -> int:
    """Handle apply subcommand."""
    result = {}
    dry_run = getattr(args, 'dry_run', False)

    if args.action == "analyze":
        result = analyze_settings_action(args.settings_file)

    elif args.action == "sync-scripts":
        # Deprecated - now just ensures executor permission
        result = sync_script_permissions(
            args.scripts_file if args.scripts_file else "",
            args.target
        )

    elif args.action == "ensure-executor":
        result = ensure_executor_permission(args.target, dry_run)

    elif args.action == "cleanup-scripts":
        remove_broad = getattr(args, 'remove_broad_python', False)
        result = cleanup_script_permissions(args.target, dry_run, remove_broad)

    elif args.action == "migrate-executor":
        remove_broad = getattr(args, 'remove_broad_python', False)
        result = migrate_to_executor_pattern(args.target, dry_run, remove_broad)

    elif args.action == "add":
        if not args.permission:
            result = {"error": "--permission required for add action"}
        else:
            result = add_permission_action(args.permission, args.target)

    elif args.action == "remove":
        if not args.permission:
            result = {"error": "--permission required for remove action"}
        else:
            result = remove_permission_action(args.permission, args.target)

    elif args.action == "ensure":
        if not args.permissions:
            result = {"error": "--permissions required for ensure action"}
        else:
            perms = [p.strip() for p in args.permissions.split(",")]
            result = ensure_permissions_action(perms, args.target)

    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Permission management tools for Claude Code settings'
    )
    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # generate-wildcards subcommand
    p_gen = subparsers.add_parser('generate-wildcards', help='Generate permission wildcards from marketplace inventory')
    p_gen.add_argument('--input', '-i', help='Input JSON file (default: stdin)')
    p_gen.set_defaults(func=cmd_generate_wildcards)

    # detect-redundant subcommand
    p_red = subparsers.add_parser('detect-redundant', help='Detect redundant permissions between global and local settings')
    p_red.add_argument('--global-settings', required=True, help='Path to global settings file')
    p_red.add_argument('--local-settings', required=True, help='Path to local/project settings file')
    p_red.set_defaults(func=cmd_detect_redundant)

    # detect-suspicious subcommand
    p_sus = subparsers.add_parser('detect-suspicious', help='Detect suspicious permissions matching anti-patterns')
    p_sus.add_argument('--settings', required=True, help='Path to settings file to analyze')
    p_sus.add_argument('--approved-file', help='Path to run-configuration file with user-approved permissions')
    p_sus.set_defaults(func=cmd_detect_suspicious)

    # consolidate subcommand
    p_con = subparsers.add_parser('consolidate', help='Consolidate timestamped build output permissions with wildcards')
    p_con.add_argument('--settings', required=True, help='Path to settings file to analyze and modify')
    p_con.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    p_con.set_defaults(func=cmd_consolidate)

    # ensure-wildcards subcommand
    p_ens = subparsers.add_parser('ensure-wildcards', help='Ensure marketplace bundle wildcards exist in global settings')
    p_ens.add_argument('--settings', required=True, help='Path to settings file to update')
    p_ens.add_argument('--marketplace-json', required=True, help='Path to marketplace.json file')
    p_ens.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    p_ens.set_defaults(func=cmd_ensure_wildcards)

    # apply-fixes subcommand
    p_fix = subparsers.add_parser('apply-fixes', help='Apply safe fixes to permission settings')
    p_fix.add_argument('--settings', required=True, help='Path to settings file to fix')
    p_fix.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    p_fix.set_defaults(func=cmd_apply_fixes)

    # apply subcommand (manage permissions)
    p_app = subparsers.add_parser('apply', help='Manage permissions (executor pattern, add, remove, ensure)')
    p_app.add_argument('--action', required=True,
                       choices=['analyze', 'sync-scripts', 'ensure-executor', 'cleanup-scripts',
                                'migrate-executor', 'add', 'remove', 'ensure'],
                       help='Action to perform')
    p_app.add_argument('--settings-file', help='Path to settings file (for analyze)')
    p_app.add_argument('--scripts-file', help='DEPRECATED: Path to scripts file (ignored)')
    p_app.add_argument('--permission', help='Single permission (for add/remove)')
    p_app.add_argument('--permissions', help='Comma-separated permissions (for ensure)')
    p_app.add_argument('--target', default='global', choices=['global', 'project'],
                       help='Target settings file (default: global)')
    p_app.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    p_app.add_argument('--remove-broad-python', action='store_true',
                       help='Also remove Bash(python3:*) wildcard (for cleanup-scripts/migrate-executor)')
    p_app.set_defaults(func=cmd_apply)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return EXIT_ERROR

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
