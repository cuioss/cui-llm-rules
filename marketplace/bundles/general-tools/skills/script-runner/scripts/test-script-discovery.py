#!/usr/bin/env python3
"""
test-script-discovery.py

Tests that script discovery captures ALL scripts from marketplace inventory.
This test reproduces the bug where some scripts are missing from scripts.local.json.

Usage:
    python3 test-script-discovery.py [--scripts-local PATH] [--marketplace-root PATH]

Options:
    --scripts-local PATH      Path to scripts.local.json (default: .claude/scripts.local.json)
    --marketplace-root PATH   Path to marketplace root (default: current directory)

Exit codes:
    0 - All scripts discovered
    1 - Missing scripts detected (bug reproduced)
    2 - Error during execution
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_scripts_local(path: Path) -> dict:
    """Load scripts.local.json and return the scripts mapping."""
    if not path.exists():
        return {}

    with open(path) as f:
        data = json.load(f)

    return data.get("scripts", {})


def discover_marketplace_scripts(marketplace_root: Path) -> list[dict]:
    """Run scan-marketplace-inventory.py and return all discovered scripts."""
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

    return all_scripts


def build_notation(bundle: str, skill: str, script_name: str, script_type: str) -> str:
    """Build the portable notation for a script."""
    ext = ".py" if script_type == "python" else ".sh"
    return f"{bundle}:{skill}/scripts/{script_name}{ext}"


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


def main():
    parser = argparse.ArgumentParser(
        description="Test script discovery against marketplace inventory"
    )
    parser.add_argument(
        "--scripts-local",
        type=Path,
        default=Path(".claude/scripts.local.json"),
        help="Path to scripts.local.json"
    )
    parser.add_argument(
        "--marketplace-root",
        type=Path,
        default=Path.cwd(),
        help="Path to marketplace root directory"
    )

    args = parser.parse_args()

    # Resolve paths
    if not args.scripts_local.is_absolute():
        args.scripts_local = args.marketplace_root / args.scripts_local

    print("Testing script discovery...")
    print(f"  scripts.local.json: {args.scripts_local}")
    print(f"  marketplace root: {args.marketplace_root}")
    print()

    try:
        # Load current scripts.local.json
        scripts_local = load_scripts_local(args.scripts_local)
        print(f"Scripts in scripts.local.json: {len(scripts_local)}")

        # Discover all marketplace scripts
        discovered = discover_marketplace_scripts(args.marketplace_root)
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


if __name__ == "__main__":
    sys.exit(main())
