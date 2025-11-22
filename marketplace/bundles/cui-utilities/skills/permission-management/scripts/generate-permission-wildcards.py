#!/usr/bin/env python3
"""
generate-permission-wildcards.py

Purpose: Analyze marketplace inventory and generate Claude Code permission wildcards.
Input: Marketplace inventory JSON (from scan-marketplace-inventory.sh) via stdin or --input file
Output: JSON with generated permissions, statistics, and coverage analysis

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
    parser.add_argument(
        "--base-path",
        type=str,
        help="Override base path for absolute script permissions"
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


def generate_script_permissions(bundles: list[dict], base_path_override: str | None = None) -> list[dict]:
    """
    Generate Bash permissions for each script in three formats:
    - runtime: ./.claude/skills/{skill}/scripts/{script}.sh
    - relative: ./marketplace/bundles/{bundle}/skills/{skill}/scripts/{script}.sh
    - absolute: /full/path/...

    Returns list of dicts with script info and all three permission formats.
    """
    script_permissions = []

    for bundle in bundles:
        for script in bundle.get("scripts", []):
            path_formats = script.get("path_formats", {})

            # Use override base path if provided
            absolute_path = path_formats.get("absolute", "")
            if base_path_override and absolute_path:
                # Replace the base path portion
                relative = path_formats.get("relative", "")
                if relative:
                    absolute_path = f"{base_path_override}/{relative}"

            script_permissions.append({
                "name": script["name"],
                "skill": script.get("skill", "unknown"),
                "bundle": bundle["name"],
                "permissions": {
                    "runtime": f"Bash({path_formats.get('runtime', '')}:*)",
                    "relative": f"Bash(./{path_formats.get('relative', '')}:*)",
                    "absolute": f"Bash({absolute_path}:*)"
                }
            })

    return sorted(script_permissions, key=lambda x: x["name"])


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


def generate_all_permissions(inventory: dict[str, Any], base_path_override: str | None = None) -> dict[str, Any]:
    """Main function to generate all permission wildcards from inventory."""
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

    # Generate all permission types
    skill_wildcards = generate_skill_wildcards(bundles)
    command_bundle_wildcards = generate_command_bundle_wildcards(bundles)
    command_shortform = generate_command_shortform_permissions(bundles)
    script_perms = generate_script_permissions(bundles, base_path_override)

    # Calculate statistics
    stats = inventory.get("statistics", {})
    total_scripts = stats.get("total_scripts", 0)
    script_permission_count = total_scripts * 3  # 3 formats per script

    wildcards_generated = (
        len(skill_wildcards) +
        len(command_bundle_wildcards) +
        len(command_shortform) +
        script_permission_count
    )

    # Analyze patterns
    patterns = analyze_naming_patterns(bundles)

    # Build bundle summary
    bundle_summary = build_bundle_summary(bundles)

    # Flatten script permissions for easy consumption
    script_permissions_flat = []
    for sp in script_perms:
        script_permissions_flat.extend([
            sp["permissions"]["runtime"],
            sp["permissions"]["relative"],
            sp["permissions"]["absolute"]
        ])

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
                "command_shortform_permissions": len(command_shortform),
                "script_permissions": script_permission_count
            }
        },
        "naming_patterns": patterns,
        "bundle_summary": bundle_summary,
        "permissions": {
            "skill_wildcards": skill_wildcards,
            "command_bundle_wildcards": command_bundle_wildcards,
            "command_shortform": command_shortform,
            "script_permissions": script_perms,
            "script_permissions_flat": sorted(script_permissions_flat)
        },
        "coverage": {
            "skills_covered": f"{stats.get('total_skills', 0)} skills covered by {len(skill_wildcards)} bundle wildcards",
            "commands_covered": f"{stats.get('total_commands', 0)} commands covered by {len(command_bundle_wildcards)} bundle wildcards + {len(command_shortform)} short-form permissions",
            "scripts_covered": f"{total_scripts} scripts covered by {script_permission_count} permissions (3 formats each)"
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
    lines.append(f"  Script permissions: {breakdown.get('script_permissions', 0)}")
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

    lines.append("SCRIPT PERMISSIONS (3 formats each):")
    for sp in perms.get("script_permissions", []):
        lines.append(f"  {sp['name']} ({sp['skill']}):")
        lines.append(f"    {sp['permissions']['runtime']}")
        lines.append(f"    {sp['permissions']['relative']}")
        lines.append(f"    {sp['permissions']['absolute']}")
    lines.append("")

    coverage = result.get("coverage", {})
    lines.append("COVERAGE:")
    lines.append(f"  {coverage.get('skills_covered', '')}")
    lines.append(f"  {coverage.get('commands_covered', '')}")
    lines.append(f"  {coverage.get('scripts_covered', '')}")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    args = parse_args()

    # Load inventory
    inventory = load_inventory(args.input)

    # Generate permissions
    result = generate_all_permissions(inventory, args.base_path)

    # Output
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
