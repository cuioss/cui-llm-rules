#!/usr/bin/env python3
"""
detect-suspicious-permissions.py

Detect permissions matching anti-patterns (security risks).

Detects:
1. System temp directory access (/tmp, /var/tmp)
2. Critical system directory access (/etc, /dev, /sys, /proc, etc.)
3. Overly broad wildcards (root write, all users)
4. Dangerous command patterns (sudo, rm -rf, curl | bash)

Excludes permissions that user has explicitly approved.

Usage:
    python3 detect-suspicious-permissions.py --settings PATH [--approved-file PATH]

Output: JSON with suspicious and already_approved arrays
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# Patterns for suspicious permissions with severity levels
SUSPICIOUS_PATTERNS = [
    # High severity - root/system write access
    {
        "pattern": r"^Write\(\/\*\*\)$",
        "reason": "Root write access - can modify any file on system",
        "severity": "high",
        "category": "root_access"
    },
    {
        "pattern": r"^Read\(\/\*\*\)$",
        "reason": "Root read access - can read any file on system",
        "severity": "high",
        "category": "root_access"
    },
    {
        "pattern": r"^Write\(\/etc\/.*\)$",
        "reason": "System configuration write access",
        "severity": "high",
        "category": "system_directory"
    },
    {
        "pattern": r"^Write\(\/dev\/.*\)$",
        "reason": "Device file write access",
        "severity": "high",
        "category": "system_directory"
    },
    {
        "pattern": r"^Write\(\/sys\/.*\)$",
        "reason": "System kernel interface write access",
        "severity": "high",
        "category": "system_directory"
    },
    {
        "pattern": r"^Write\(\/proc\/.*\)$",
        "reason": "Process information write access",
        "severity": "high",
        "category": "system_directory"
    },
    {
        "pattern": r"^Write\(\/boot\/.*\)$",
        "reason": "Boot files write access",
        "severity": "high",
        "category": "system_directory"
    },
    {
        "pattern": r"^Write\(\/root\/.*\)$",
        "reason": "Root user home directory write access",
        "severity": "high",
        "category": "system_directory"
    },
    # Dangerous commands - high severity
    {
        "pattern": r"^Bash\(sudo:.*\)$",
        "reason": "Privilege escalation - sudo access",
        "severity": "high",
        "category": "dangerous_command"
    },
    {
        "pattern": r"^Bash\(rm:-rf.*\)$",
        "reason": "Recursive force delete - can destroy data",
        "severity": "high",
        "category": "dangerous_command"
    },
    {
        "pattern": r"^Bash\(dd:.*\)$",
        "reason": "Low-level disk operations",
        "severity": "high",
        "category": "dangerous_command"
    },
    {
        "pattern": r"^Bash\(mkfs:.*\)$",
        "reason": "Filesystem creation - can destroy data",
        "severity": "high",
        "category": "dangerous_command"
    },
    {
        "pattern": r"^Bash\(fdisk:.*\)$",
        "reason": "Disk partitioning - can destroy data",
        "severity": "high",
        "category": "dangerous_command"
    },
    {
        "pattern": r".*\|\s*bash.*",
        "reason": "Piping to bash - potential remote code execution",
        "severity": "high",
        "category": "dangerous_command"
    },
    {
        "pattern": r".*\|\s*sh.*",
        "reason": "Piping to sh - potential remote code execution",
        "severity": "high",
        "category": "dangerous_command"
    },
    # Medium severity - temp directories
    {
        "pattern": r"^Write\(\/tmp\/.*\)$",
        "reason": "System temp directory write access - use project-specific temp",
        "severity": "medium",
        "category": "temp_directory"
    },
    {
        "pattern": r"^Write\(\/var\/tmp\/.*\)$",
        "reason": "Persistent temp directory write access",
        "severity": "medium",
        "category": "temp_directory"
    },
    {
        "pattern": r"^Write\(\/private\/tmp\/.*\)$",
        "reason": "macOS private temp directory write access",
        "severity": "medium",
        "category": "temp_directory"
    },
    {
        "pattern": r"^Read\(\/\/tmp\/.*\)$",
        "reason": "System temp directory read access",
        "severity": "medium",
        "category": "temp_directory"
    },
    {
        "pattern": r"^Write\(\/\/tmp\/.*\)$",
        "reason": "System temp directory write access",
        "severity": "medium",
        "category": "temp_directory"
    },
    # Medium severity - broad user access
    {
        "pattern": r"^Read\(\/\/Users\/\*\*\)$",
        "reason": "All users read access",
        "severity": "medium",
        "category": "broad_access"
    },
    {
        "pattern": r"^Write\(\/\/Users\/\*\*\)$",
        "reason": "All users write access",
        "severity": "high",
        "category": "broad_access"
    },
    {
        "pattern": r"^Read\(\/\/home\/\*\*\)$",
        "reason": "All home directories read access",
        "severity": "medium",
        "category": "broad_access"
    },
    {
        "pattern": r"^Write\(\/\/home\/\*\*\)$",
        "reason": "All home directories write access",
        "severity": "high",
        "category": "broad_access"
    },
    # Low severity - potentially risky network commands
    {
        "pattern": r"^Bash\(curl:\*\)$",
        "reason": "Unrestricted curl access - network operations",
        "severity": "low",
        "category": "network_access"
    },
    {
        "pattern": r"^Bash\(wget:\*\)$",
        "reason": "Unrestricted wget access - network operations",
        "severity": "low",
        "category": "network_access"
    },
]


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

        # Navigate to the user_approved_permissions list
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


def detect_suspicious_permissions(
    settings: dict,
    approved_permissions: set[str]
) -> dict:
    """
    Detect suspicious permissions in settings.

    Returns dict with:
        - suspicious: List of suspicious permissions with details
        - already_approved: List of permissions user has approved
        - summary: Counts by severity
    """
    allow_list = settings.get("permissions", {}).get("allow", [])

    suspicious = []
    already_approved = []

    for permission in allow_list:
        # Check if user has approved this permission
        if permission in approved_permissions:
            result = check_permission(permission)
            if result:
                already_approved.append(permission)
            continue

        # Check against suspicious patterns
        result = check_permission(permission)
        if result:
            suspicious.append(result)

    # Count by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for item in suspicious:
        severity_counts[item["severity"]] += 1

    return {
        "suspicious": suspicious,
        "already_approved": already_approved,
        "summary": {
            "total_suspicious": len(suspicious),
            "already_approved_count": len(already_approved),
            "by_severity": severity_counts,
            "permissions_checked": len(allow_list)
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect suspicious permissions matching anti-patterns"
    )
    parser.add_argument(
        "--settings",
        required=True,
        help="Path to settings file to analyze"
    )
    parser.add_argument(
        "--approved-file",
        help="Path to run-configuration file with user-approved permissions"
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

    # Load approved permissions
    approved_permissions = load_approved_permissions(args.approved_file)

    # Detect suspicious permissions
    result = detect_suspicious_permissions(settings, approved_permissions)
    result["settings_path"] = args.settings
    if args.approved_file:
        result["approved_file"] = args.approved_file

    # Output
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Text format
        print("=" * 60)
        print("SUSPICIOUS PERMISSIONS ANALYSIS")
        print("=" * 60)
        print()
        print(f"Settings: {args.settings}")
        if args.approved_file:
            print(f"Approved file: {args.approved_file}")
        print()

        if result["suspicious"]:
            print("SUSPICIOUS PERMISSIONS:")
            for severity in ["high", "medium", "low"]:
                items = [s for s in result["suspicious"] if s["severity"] == severity]
                if items:
                    print(f"\n  [{severity.upper()}]")
                    for item in items:
                        print(f"    - {item['permission']}")
                        print(f"      Reason: {item['reason']}")
            print()

        if result["already_approved"]:
            print("USER-APPROVED (not flagged):")
            for perm in result["already_approved"]:
                print(f"  - {perm}")
            print()

        summary = result["summary"]
        print("SUMMARY:")
        print(f"  Total suspicious: {summary['total_suspicious']}")
        print(f"    High: {summary['by_severity']['high']}")
        print(f"    Medium: {summary['by_severity']['medium']}")
        print(f"    Low: {summary['by_severity']['low']}")
        print(f"  Already approved: {summary['already_approved_count']}")


if __name__ == "__main__":
    main()
