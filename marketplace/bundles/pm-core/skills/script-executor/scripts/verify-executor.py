#!/usr/bin/env python3
"""
Verify execute-script.py executor and detect drift from marketplace state.

Usage:
    python3 verify-executor.py check
    python3 verify-executor.py drift
    python3 verify-executor.py paths

Subcommands:
    check   Verify executor exists and is valid Python
    drift   Compare executor mappings with current marketplace state
    paths   Verify all mapped paths exist
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

PLAN_DIR = Path('.plan')
EXECUTOR_PATH = PLAN_DIR / 'execute-script.py'
LOG_MODULE_PATH = PLAN_DIR / 'execution_log.py'
STATE_PATH = PLAN_DIR / 'marshall-state.toon'

MARKETPLACE_ROOT = Path('marketplace/bundles')
INVENTORY_SCRIPT = MARKETPLACE_ROOT / 'pm-plugins/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py'


# ============================================================================
# VERIFICATION
# ============================================================================

def check_executor_exists() -> bool:
    """Check if executor files exist."""
    if not EXECUTOR_PATH.exists():
        print(f"MISSING: {EXECUTOR_PATH}", file=sys.stderr)
        return False

    if not LOG_MODULE_PATH.exists():
        print(f"MISSING: {LOG_MODULE_PATH}", file=sys.stderr)
        return False

    return True


def check_executor_valid() -> tuple[bool, int]:
    """
    Check if executor is valid Python and extract script count.

    Returns:
        (is_valid, script_count)
    """
    try:
        result = subprocess.run(
            ['python3', '-c', f"import sys; sys.path.insert(0, '{PLAN_DIR}'); import execute_script; print(len(execute_script.SCRIPTS))"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"INVALID: Executor import failed: {result.stderr}", file=sys.stderr)
            return False, 0

        script_count = int(result.stdout.strip())
        return True, script_count

    except Exception as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return False, 0


def check_log_module_valid() -> bool:
    """Check if log module is valid Python."""
    try:
        result = subprocess.run(
            ['python3', '-c', f"import sys; sys.path.insert(0, '{PLAN_DIR}'); import execution_log"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"INVALID: Log module import failed: {result.stderr}", file=sys.stderr)
            return False

        return True

    except Exception as e:
        print(f"INVALID: Log module error: {e}", file=sys.stderr)
        return False


def get_executor_mappings() -> dict[str, str]:
    """Extract mappings from current executor."""
    try:
        result = subprocess.run(
            ['python3', '-c', f"import sys; sys.path.insert(0, '{PLAN_DIR}'); import execute_script; import json; print(json.dumps(execute_script.SCRIPTS))"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {}

        return json.loads(result.stdout.strip())

    except Exception:
        return {}


def get_current_marketplace_scripts() -> dict[str, str]:
    """Get current marketplace script mappings."""
    if not INVENTORY_SCRIPT.exists():
        return {}

    try:
        result = subprocess.run(
            ['python3', str(INVENTORY_SCRIPT), '--scope', 'marketplace', '--resource-types', 'scripts'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {}

        inventory = json.loads(result.stdout)
        mappings = {}

        for bundle in inventory.get('bundles', []):
            bundle_name = bundle['name']
            for script in bundle.get('scripts', []):
                skill_name = script.get('skill', '')
                if skill_name:
                    notation = f"{bundle_name}:{skill_name}"
                    mappings[notation] = str(Path(script['path']).resolve())

        return mappings

    except Exception:
        return {}


def check_paths_exist(mappings: dict[str, str]) -> tuple[list, list]:
    """
    Check if all mapped paths exist.

    Returns:
        (existing_paths, missing_paths)
    """
    existing = []
    missing = []

    for notation, path in mappings.items():
        if Path(path).exists():
            existing.append(notation)
        else:
            missing.append((notation, path))

    return existing, missing


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_check(args):
    """Verify executor exists and is valid."""
    issues = []

    # Check existence
    if not check_executor_exists():
        issues.append("Executor files missing")
    else:
        # Check validity
        valid, count = check_executor_valid()
        if not valid:
            issues.append("Executor invalid")
        else:
            print(f"Executor valid: {count} scripts")

        if not check_log_module_valid():
            issues.append("Log module invalid")
        else:
            print("Log module valid")

    if issues:
        print(f"\nstatus\tissues")
        print(f"error\t{'; '.join(issues)}")
        sys.exit(1)
    else:
        print(f"\nstatus\tscript_count")
        print(f"ok\t{count}")
        sys.exit(0)


def cmd_drift(args):
    """Compare executor mappings with current marketplace state."""
    executor_mappings = get_executor_mappings()
    current_mappings = get_current_marketplace_scripts()

    if not executor_mappings:
        print("Error: Could not read executor mappings", file=sys.stderr)
        sys.exit(1)

    if not current_mappings:
        print("Warning: Could not read marketplace state", file=sys.stderr)

    # Find differences
    executor_set = set(executor_mappings.keys())
    current_set = set(current_mappings.keys())

    added = current_set - executor_set
    removed = executor_set - current_set
    changed = []

    for notation in executor_set & current_set:
        if executor_mappings[notation] != current_mappings.get(notation):
            changed.append(notation)

    # Report
    print(f"Executor scripts: {len(executor_mappings)}")
    print(f"Marketplace scripts: {len(current_mappings)}")

    if added:
        print(f"\nAdded in marketplace ({len(added)}):")
        for n in sorted(added):
            print(f"  + {n}")

    if removed:
        print(f"\nRemoved from marketplace ({len(removed)}):")
        for n in sorted(removed):
            print(f"  - {n}")

    if changed:
        print(f"\nPath changed ({len(changed)}):")
        for n in sorted(changed):
            print(f"  ~ {n}")

    if added or removed or changed:
        print(f"\nstatus\tadded\tremoved\tchanged")
        print(f"drift\t{len(added)}\t{len(removed)}\t{len(changed)}")
        sys.exit(1)
    else:
        print(f"\nstatus\tadded\tremoved\tchanged")
        print(f"ok\t0\t0\t0")
        sys.exit(0)


def cmd_paths(args):
    """Verify all mapped paths exist."""
    mappings = get_executor_mappings()

    if not mappings:
        print("Error: Could not read executor mappings", file=sys.stderr)
        sys.exit(1)

    existing, missing = check_paths_exist(mappings)

    print(f"Total mappings: {len(mappings)}")
    print(f"Existing: {len(existing)}")
    print(f"Missing: {len(missing)}")

    if missing:
        print(f"\nMissing scripts:")
        for notation, path in missing:
            print(f"  {notation} -> {path}")

        print(f"\nstatus\texisting\tmissing")
        print(f"error\t{len(existing)}\t{len(missing)}")
        sys.exit(1)
    else:
        print(f"\nstatus\texisting\tmissing")
        print(f"ok\t{len(existing)}\t0")
        sys.exit(0)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Verify execute-script.py executor'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # check subcommand
    check_parser = subparsers.add_parser('check', help='Verify executor exists and is valid')
    check_parser.set_defaults(func=cmd_check)

    # drift subcommand
    drift_parser = subparsers.add_parser('drift', help='Compare with current marketplace state')
    drift_parser.set_defaults(func=cmd_drift)

    # paths subcommand
    paths_parser = subparsers.add_parser('paths', help='Verify all mapped paths exist')
    paths_parser.set_defaults(func=cmd_paths)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
