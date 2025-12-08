#!/usr/bin/env python3
"""
scripts.py - Script discovery and library management.

Consolidated from:
- generate-scripts-library.py → generate subcommand
- test-script-discovery.py → test subcommand

Manages .plan/scripts-library.toon generation and script discovery testing.

Output: TOON format to stdout.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# =============================================================================
# Shared Functions
# =============================================================================

def discover_marketplace_scripts(marketplace_root: Path) -> tuple[list[dict], str]:
    """
    Run scan-marketplace-inventory.py and return all discovered scripts.

    Returns:
        (scripts_list, marketplace_name)
    """
    script_path = (
        marketplace_root /
        "marketplace/bundles/cui-plugin-development-tools/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py"
    )

    if not script_path.exists():
        raise FileNotFoundError(f"Inventory script not found: {script_path}")

    result = subprocess.run(
        ["python3", str(script_path), "--resource-types", "scripts"],
        cwd=str(marketplace_root),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Inventory script failed: {result.stderr}")

    inventory = json.loads(result.stdout)

    # Detect marketplace name from plugin paths
    marketplace_name = "unknown"
    base_path = inventory.get("base_path", "")
    if "marketplace/bundles" in base_path:
        # Try to find marketplace name from mcp.json or .claude-plugin
        mcp_path = marketplace_root / ".claude" / "mcp.json"
        if mcp_path.exists():
            with open(mcp_path) as f:
                mcp = json.load(f)
                for key in mcp.get("mcpServers", {}):
                    if "@" in key:
                        marketplace_name = key.split("@")[-1]
                        break

    # Collect all scripts from all bundles
    all_scripts = []
    for bundle in inventory.get("bundles", []):
        bundle_name = bundle["name"]
        for script in bundle.get("scripts", []):
            all_scripts.append({
                "bundle": bundle_name,
                "skill": script["skill"],
                "name": script["name"],
                "type": script["type"],
                "absolute_path": script["path_formats"]["absolute"]
            })

    return all_scripts, marketplace_name


def build_notation(bundle: str, skill: str, script_name: str, script_type: str) -> str:
    """Build the portable notation for a script."""
    ext = ".py" if script_type == "python" else ".sh"
    return f"{bundle}:{skill}/scripts/{script_name}{ext}"


def load_scripts_local(path: Path) -> dict:
    """Load scripts.local.json and return the scripts mapping."""
    if not path.exists():
        return {}

    with open(path) as f:
        data = json.load(f)

    return data.get("scripts", {})


# =============================================================================
# Generate Subcommand
# =============================================================================

def generate_scripts_library_toon(scripts: list[dict], marketplace_name: str) -> str:
    """Generate the scripts-library.toon content."""
    lines = []

    # Header
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines.append(f"version: 2")
    lines.append(f"generated: {timestamp}")
    lines.append(f"marketplace: {marketplace_name}")
    lines.append(f"script_count: {len(scripts)}")
    lines.append("")

    # Build sorted list of (notation, absolute, type)
    script_entries = []
    for script in scripts:
        notation = build_notation(
            script["bundle"],
            script["skill"],
            script["name"],
            script["type"]
        )
        script_entries.append((notation, script["absolute_path"], script["type"]))

    # Sort by notation for consistent output
    script_entries.sort(key=lambda x: x[0])

    # Scripts table
    lines.append(f"scripts[{len(script_entries)}]{{notation,absolute,type}}:")
    for notation, absolute, script_type in script_entries:
        lines.append(f"{notation},{absolute},{script_type}")

    return "\n".join(lines)


def cmd_generate(args) -> int:
    """Generate scripts-library.toon from marketplace inventory."""
    # Resolve paths
    output_path = args.output
    if not output_path.is_absolute():
        output_path = args.marketplace_root / output_path

    try:
        # Discover all scripts
        scripts, marketplace_name = discover_marketplace_scripts(args.marketplace_root)

        # Generate TOON content
        toon_content = generate_scripts_library_toon(scripts, marketplace_name)

        if args.dry_run:
            print(toon_content)
            print(f"\n# Would write to: {output_path}", file=sys.stderr)
            print(f"# Scripts discovered: {len(scripts)}", file=sys.stderr)
        else:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, "w") as f:
                f.write(toon_content)
                f.write("\n")

            # Output success in TOON format
            print(f"status: success")
            print(f"scripts_discovered: {len(scripts)}")
            print(f"output_file: {output_path}")
            print(f"marketplace: {marketplace_name}")

        return 0

    except Exception as e:
        # Output error in TOON format
        print(f"status: error", file=sys.stderr)
        print(f"message: {e}", file=sys.stderr)
        return 1


# =============================================================================
# Test Subcommand
# =============================================================================

def test_skill_scripts(
    scripts_local: dict,
    discovered_scripts: list[dict],
    skill_name: str,
    expected_scripts: list[str]
) -> tuple[bool, list[str], list[str]]:
    """
    Test that all expected scripts for a skill are discovered and in scripts.local.json.

    Returns:
        (passed, missing_in_local, missing_in_inventory)
    """
    # Find scripts for this skill in inventory
    skill_scripts = [s for s in discovered_scripts if s["skill"] == skill_name]
    skill_script_names = {f"{s['name']}.{('py' if s['type'] == 'python' else 'sh')}"
                         for s in skill_scripts}

    # Check what's missing from inventory
    missing_in_inventory = [s for s in expected_scripts if s not in skill_script_names]

    # Check what's missing from scripts.local.json
    missing_in_local = []
    for script in skill_scripts:
        notation = build_notation(script["bundle"], script["skill"],
                                  script["name"], script["type"])
        if notation not in scripts_local:
            ext = ".py" if script["type"] == "python" else ".sh"
            missing_in_local.append(f"{script['name']}{ext}")

    passed = len(missing_in_inventory) == 0 and len(missing_in_local) == 0
    return passed, missing_in_local, missing_in_inventory


def cmd_test(args) -> int:
    """Test script discovery against marketplace inventory."""
    # Resolve paths
    scripts_local_path = args.scripts_local
    if not scripts_local_path.is_absolute():
        scripts_local_path = args.marketplace_root / scripts_local_path

    print("Testing script discovery...")
    print(f"  scripts.local.json: {scripts_local_path}")
    print(f"  marketplace root: {args.marketplace_root}")
    print()

    try:
        # Load current scripts.local.json
        scripts_local = load_scripts_local(scripts_local_path)
        print(f"Scripts in scripts.local.json: {len(scripts_local)}")

        # Discover all marketplace scripts
        discovered, _ = discover_marketplace_scripts(args.marketplace_root)
        print(f"Scripts discovered by inventory: {len(discovered)}")
        print()

        # Test specific skills that are known to have issues
        test_cases = [
            {
                "skill": "manage-lessons-learned",
                "expected": [
                    "query-lessons.py",
                    "write-lesson.py",
                    "update-lesson.py",
                    "test-lessons-scripts.py",
                    "test-query-lessons.sh"
                ]
            }
        ]

        all_passed = True

        for test_case in test_cases:
            skill = test_case["skill"]
            expected = test_case["expected"]

            passed, missing_local, missing_inventory = test_skill_scripts(
                scripts_local, discovered, skill, expected
            )

            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {skill}")
            print(f"       Expected scripts: {len(expected)}")

            if missing_inventory:
                print(f"       Missing from inventory: {missing_inventory}")
                all_passed = False

            if missing_local:
                print(f"       Missing from scripts.local.json: {missing_local}")
                all_passed = False

            if passed:
                print(f"       All {len(expected)} scripts discovered and registered")

            print()

        # Summary
        print("=" * 60)
        if all_passed:
            print("SUCCESS: All scripts discovered correctly")
            return 0
        else:
            print("FAILURE: Missing scripts detected")
            print()
            print("The Discover workflow is not capturing all scripts.")
            print("This is the bug that needs to be fixed.")
            return 1

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Script discovery and library management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate scripts-library.toon
  %(prog)s generate

  # Generate with custom output path
  %(prog)s generate --output custom/path/scripts-library.toon

  # Dry-run (print without writing)
  %(prog)s generate --dry-run

  # Test script discovery
  %(prog)s test

  # Test with custom paths
  %(prog)s test --scripts-local path/to/scripts.local.json
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # generate command
    p_generate = subparsers.add_parser('generate', help='Generate scripts-library.toon')
    p_generate.add_argument(
        '--output',
        type=Path,
        default=Path('.plan/scripts-library.toon'),
        help='Output path for scripts-library.toon'
    )
    p_generate.add_argument(
        '--marketplace-root',
        type=Path,
        default=Path.cwd(),
        help='Path to marketplace root directory'
    )
    p_generate.add_argument(
        '--dry-run',
        action='store_true',
        help='Print output instead of writing file'
    )
    p_generate.set_defaults(func=cmd_generate)

    # test command
    p_test = subparsers.add_parser('test', help='Test script discovery')
    p_test.add_argument(
        '--scripts-local',
        type=Path,
        default=Path('.claude/scripts.local.json'),
        help='Path to scripts.local.json'
    )
    p_test.add_argument(
        '--marketplace-root',
        type=Path,
        default=Path.cwd(),
        help='Path to marketplace root directory'
    )
    p_test.set_defaults(func=cmd_test)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
