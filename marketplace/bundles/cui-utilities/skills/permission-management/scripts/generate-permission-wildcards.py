#!/usr/bin/env python3
"""
generate-permission-wildcards.py

Purpose: Analyze marketplace inventory and generate Claude Code permission wildcards.
Input: Marketplace inventory JSON (from scan-marketplace-inventory.sh) via stdin or --input file
Output: JSON with generated permissions, statistics, and coverage analysis

Note: Script permissions are NOT generated. The {baseDir} pattern in SKILL.md handles
script invocation automatically - Claude resolves {baseDir} at runtime to the skill's
mounted directory. No hardcoded script paths should be in settings files.

Usage:
  cat inventory.json | python3 generate-permission-wildcards.py
  python3 generate-permission-wildcards.py --input inventory.json
  python3 generate-permission-wildcards.py --input inventory.json --format text
"""

import argparse
import json
import sys
from collections import defaultdict
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Claude Code permission wildcards from marketplace inventory"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input JSON file (default: stdin)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    return parser.parse_args()


def load_inventory(input_file: str | None) -> dict[str, Any]:
    """Load marketplace inventory from file or stdin."""
    try:
        if input_file:
            with open(input_file, "r") as f:
                return json.load(f)
        else:
            return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)


def extract_command_prefix(command_name: str) -> str:
    """Extract the prefix from a command name (e.g., 'plugin-create' -> 'plugin')."""
    parts = command_name.split("-")
    if len(parts) > 1:
        return parts[0]
    return command_name


def extract_skill_prefix(skill_name: str) -> str:
    """Extract the prefix from a skill name (e.g., 'cui-java-core' -> 'cui')."""
    parts = skill_name.split("-")
    if len(parts) > 1:
        return parts[0]
    return skill_name


def generate_skill_wildcards(bundles: list[dict]) -> list[str]:
    """Generate Skill({bundle-name}:*) wildcards for bundles with skills."""
    wildcards = []
    for bundle in bundles:
        if bundle.get("skills") and len(bundle["skills"]) > 0:
            wildcards.append(f"Skill({bundle['name']}:*)")
    return sorted(wildcards)


def generate_command_bundle_wildcards(bundles: list[dict]) -> list[str]:
    """Generate SlashCommand(/{bundle-name}:*) wildcards for bundles with commands."""
    wildcards = []
    for bundle in bundles:
        if bundle.get("commands") and len(bundle["commands"]) > 0:
            wildcards.append(f"SlashCommand(/{bundle['name']}:*)")
    return sorted(wildcards)


def generate_command_shortform_permissions(bundles: list[dict]) -> list[str]:
    """Generate SlashCommand(/{command-name}:*) for each command (short-form invocation)."""
    permissions = []
    for bundle in bundles:
        for command in bundle.get("commands", []):
            permissions.append(f"SlashCommand(/{command['name']}:*)")
    return sorted(permissions)


def count_scripts(bundles: list[dict]) -> int:
    """Count total scripts in bundles (for reporting only, no permissions generated)."""
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


def generate_all_permissions(inventory: dict[str, Any]) -> dict[str, Any]:
    """Main function to generate all permission wildcards from inventory.

    Note: Script permissions are NOT generated. The {baseDir} pattern handles this automatically.
    """
    bundles = inventory.get("bundles", [])

    if not bundles:
        return {
            "error": "No bundles found in inventory",
            "statistics": {
                "bundles_scanned": 0,
                "skills_found": 0,
                "commands_found": 0,
                "scripts_found": 0,
                "wildcards_generated": 0
            }
        }

    # Generate permission wildcards (Skills and SlashCommands only)
    skill_wildcards = generate_skill_wildcards(bundles)
    command_bundle_wildcards = generate_command_bundle_wildcards(bundles)
    command_shortform = generate_command_shortform_permissions(bundles)

    # Calculate statistics
    stats = inventory.get("statistics", {})
    total_scripts = count_scripts(bundles)

    wildcards_generated = (
        len(skill_wildcards) +
        len(command_bundle_wildcards) +
        len(command_shortform)
    )

    # Analyze patterns
    patterns = analyze_naming_patterns(bundles)

    # Build bundle summary
    bundle_summary = build_bundle_summary(bundles)

    return {
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
            "scripts_note": f"{total_scripts} scripts - handled by {{baseDir}} architecture (no permissions needed)"
        }
    }


def format_text_output(result: dict[str, Any]) -> str:
    """Format the result as human-readable text."""
    lines = []

    stats = result.get("statistics", {})
    lines.append("=" * 60)
    lines.append("MARKETPLACE PERMISSION WILDCARD ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    lines.append("STATISTICS:")
    lines.append(f"  Bundles scanned: {stats.get('bundles_scanned', 0)}")
    lines.append(f"  Skills found: {stats.get('skills_found', 0)}")
    lines.append(f"  Commands found: {stats.get('commands_found', 0)}")
    lines.append(f"  Scripts found: {stats.get('scripts_found', 0)}")
    lines.append(f"  Wildcards generated: {stats.get('wildcards_generated', 0)}")
    lines.append("")

    breakdown = stats.get("breakdown", {})
    lines.append("BREAKDOWN:")
    lines.append(f"  Skill bundle wildcards: {breakdown.get('skill_bundle_wildcards', 0)}")
    lines.append(f"  Command bundle wildcards: {breakdown.get('command_bundle_wildcards', 0)}")
    lines.append(f"  Command short-form permissions: {breakdown.get('command_shortform_permissions', 0)}")
    lines.append("")

    patterns = result.get("naming_patterns", {})
    lines.append("NAMING PATTERNS:")
    lines.append(f"  Bundle names: {', '.join(patterns.get('bundle_names', []))}")
    lines.append(f"  Skill prefixes: {', '.join(patterns.get('skill_prefixes', []))}")
    lines.append(f"  Command prefixes: {', '.join(patterns.get('command_prefixes', []))}")
    lines.append("")

    perms = result.get("permissions", {})

    lines.append("SKILL BUNDLE WILDCARDS:")
    for p in perms.get("skill_wildcards", []):
        lines.append(f"  {p}")
    lines.append("")

    lines.append("COMMAND BUNDLE WILDCARDS:")
    for p in perms.get("command_bundle_wildcards", []):
        lines.append(f"  {p}")
    lines.append("")

    lines.append("COMMAND SHORT-FORM PERMISSIONS:")
    for p in perms.get("command_shortform", []):
        lines.append(f"  {p}")
    lines.append("")

    lines.append("SCRIPTS:")
    lines.append("  Scripts are handled by {baseDir} architecture - no permissions needed.")
    lines.append("  Claude resolves {baseDir} at runtime to skill's mounted directory.")
    lines.append("")

    coverage = result.get("coverage", {})
    lines.append("COVERAGE:")
    lines.append(f"  {coverage.get('skills_covered', '')}")
    lines.append(f"  {coverage.get('commands_covered', '')}")
    lines.append(f"  {coverage.get('scripts_note', '')}")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    args = parse_args()

    # Load inventory
    inventory = load_inventory(args.input)

    # Generate permissions (Skills and SlashCommands only - scripts use {baseDir})
    result = generate_all_permissions(inventory)

    # Output
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
