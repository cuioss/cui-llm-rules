#!/usr/bin/env python3
"""
Generate execute-script.py and execution_log.py with embedded script mappings.

Usage:
    python3 generate-executor.py generate [--force] [--dry-run]
    python3 generate-executor.py verify
    python3 generate-executor.py cleanup [--max-age-days N]

Subcommands:
    generate    Generate executor and logging module
    verify      Verify existing executor is valid
    cleanup     Clean up old global logs
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

PLAN_DIR = Path('.plan')
EXECUTOR_PATH = PLAN_DIR / 'execute-script.py'
LOG_MODULE_PATH = PLAN_DIR / 'execution_log.py'
STATE_PATH = PLAN_DIR / 'marshall-state.toon'
LOGS_DIR = PLAN_DIR / 'logs'

# Template paths (relative to this script)
SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR.parent / 'templates'
EXECUTOR_TEMPLATE = TEMPLATES_DIR / 'execute-script.py.template'
LOG_MODULE_TEMPLATE = TEMPLATES_DIR / 'execution-log.py.template'

# Marketplace inventory script
MARKETPLACE_ROOT = Path('marketplace/bundles')
INVENTORY_SCRIPT = MARKETPLACE_ROOT / 'pm-core/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py'

# ============================================================================
# SCRIPT DISCOVERY
# ============================================================================

def discover_scripts() -> dict[str, str]:
    """
    Discover all scripts from marketplace bundles.

    Returns:
        dict mapping notation to absolute path
    """
    if not INVENTORY_SCRIPT.exists():
        print(f"Error: Inventory script not found: {INVENTORY_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    # Run inventory scan
    result = subprocess.run(
        ['python3', str(INVENTORY_SCRIPT), '--scope', 'marketplace', '--resource-types', 'scripts'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error running inventory scan: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    inventory = json.loads(result.stdout)

    # Build notation mappings
    mappings = {}

    for bundle in inventory.get('bundles', []):
        for script in bundle.get('scripts', []):
            notation = script.get('notation', '')
            path_formats = script.get('path_formats', {})
            abs_path = path_formats.get('absolute', '')

            if notation and abs_path:
                mappings[notation] = abs_path

    return mappings


def discover_scripts_fallback() -> dict[str, str]:
    """
    Fallback script discovery using glob patterns.

    Returns:
        dict mapping notation to absolute path
    """
    mappings = {}

    for bundle_dir in MARKETPLACE_ROOT.iterdir():
        if not bundle_dir.is_dir():
            continue

        bundle_name = bundle_dir.name
        skills_dir = bundle_dir / 'skills'

        if not skills_dir.exists():
            continue

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_name = skill_dir.name
            scripts_dir = skill_dir / 'scripts'

            if not scripts_dir.exists():
                continue

            # Find the main script (usually {skill_name}.py or similar)
            for script_file in scripts_dir.glob('*.py'):
                # Skip __init__.py and test files
                if script_file.name.startswith('_') or 'test' in script_file.name.lower():
                    continue

                # Use simplified notation
                notation = f"{bundle_name}:{skill_name}"
                abs_path = str(script_file.resolve())
                mappings[notation] = abs_path
                break  # Only take first script per skill

    return mappings


# ============================================================================
# GENERATION
# ============================================================================

def generate_mappings_code(mappings: dict[str, str]) -> str:
    """Generate Python code for script mappings dict."""
    lines = []
    for notation, path in sorted(mappings.items()):
        lines.append(f'    "{notation}": "{path}",')
    return '\n'.join(lines)


def generate_executor(mappings: dict[str, str], dry_run: bool = False) -> bool:
    """
    Generate execute-script.py with embedded mappings.

    Returns:
        True if successful
    """
    if not EXECUTOR_TEMPLATE.exists():
        print(f"Error: Template not found: {EXECUTOR_TEMPLATE}", file=sys.stderr)
        return False

    template = EXECUTOR_TEMPLATE.read_text()
    mappings_code = generate_mappings_code(mappings)

    # execution_log.py location (same directory as this script)
    log_module_dir = str(SCRIPT_DIR.resolve())

    content = template.replace('{{SCRIPT_MAPPINGS}}', mappings_code)
    content = content.replace('{{EXECUTION_LOG_DIR}}', log_module_dir)

    if dry_run:
        print("=== execute-script.py ===")
        print(content[:2000])
        print("... (truncated)")
        return True

    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTOR_PATH.write_text(content)
    return True


def generate_log_module(dry_run: bool = False) -> bool:
    """
    Generate execution_log.py module.

    Returns:
        True if successful
    """
    if not LOG_MODULE_TEMPLATE.exists():
        print(f"Error: Template not found: {LOG_MODULE_TEMPLATE}", file=sys.stderr)
        return False

    content = LOG_MODULE_TEMPLATE.read_text()

    if dry_run:
        print("=== execution_log.py ===")
        print(content[:1000])
        print("... (truncated)")
        return True

    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_MODULE_PATH.write_text(content)
    return True


def compute_checksum(mappings: dict[str, str]) -> str:
    """Compute checksum of mappings for change detection."""
    content = json.dumps(mappings, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()[:8]


def update_state(script_count: int, checksum: str, logs_cleaned: int) -> None:
    """Update marshall-state.toon with generation metadata."""
    timestamp = datetime.now().isoformat()
    content = f"""status\tgenerated\tscript_count\tchecksum\tlogs_cleaned
success\t{timestamp}\t{script_count}\t{checksum}\t{logs_cleaned}
"""
    STATE_PATH.write_text(content)


def cleanup_old_logs(max_age_days: int = 7) -> int:
    """
    Clean up old global logs.

    Returns:
        Number of logs deleted
    """
    import time

    deleted = 0
    cutoff = time.time() - (max_age_days * 86400)

    if not LOGS_DIR.exists():
        return 0

    for log_file in LOGS_DIR.glob('script-execution-*.log'):
        try:
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                deleted += 1
        except Exception:
            pass

    return deleted


# ============================================================================
# VERIFICATION
# ============================================================================

def verify_executor() -> bool:
    """
    Verify existing executor is valid.

    Returns:
        True if valid
    """
    if not EXECUTOR_PATH.exists():
        print(f"Error: Executor not found: {EXECUTOR_PATH}", file=sys.stderr)
        return False

    if not LOG_MODULE_PATH.exists():
        print(f"Error: Log module not found: {LOG_MODULE_PATH}", file=sys.stderr)
        return False

    # Try to import and validate
    try:
        result = subprocess.run(
            ['python3', '-c', f"import sys; sys.path.insert(0, '{PLAN_DIR}'); import execute_script; print(len(execute_script.SCRIPTS))"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error validating executor: {result.stderr}", file=sys.stderr)
            return False

        script_count = int(result.stdout.strip())
        print(f"Executor valid: {script_count} scripts mapped")

    except Exception as e:
        print(f"Error validating executor: {e}", file=sys.stderr)
        return False

    # Verify log module
    try:
        result = subprocess.run(
            ['python3', '-c', f"import sys; sys.path.insert(0, '{PLAN_DIR}'); import execution_log; print('OK')"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error validating log module: {result.stderr}", file=sys.stderr)
            return False

        print("Log module valid")

    except Exception as e:
        print(f"Error validating log module: {e}", file=sys.stderr)
        return False

    return True


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_generate(args):
    """Generate executor (log module is pre-existing)."""
    # Discover scripts
    print("Discovering scripts...")
    try:
        mappings = discover_scripts()
    except Exception as e:
        print(f"Falling back to glob discovery: {e}", file=sys.stderr)
        mappings = discover_scripts_fallback()

    print(f"Found {len(mappings)} scripts")

    if args.dry_run:
        print("\n=== Script Mappings ===")
        for notation, path in sorted(mappings.items()):
            print(f"  {notation} -> {path}")
        print()

    # Generate executor (log module exists at SCRIPT_DIR/execution_log.py)
    print("Generating executor...")
    if not generate_executor(mappings, dry_run=args.dry_run):
        sys.exit(1)

    if args.dry_run:
        print("\nDry run complete. No files written.")
        return

    # Cleanup old logs
    logs_cleaned = cleanup_old_logs()
    if logs_cleaned > 0:
        print(f"Cleaned up {logs_cleaned} old log files")

    # Update state
    checksum = compute_checksum(mappings)
    update_state(len(mappings), checksum, logs_cleaned)

    # Output summary in TOON format
    print(f"\nstatus\tscripts_discovered\texecutor_generated\tlog_module_generated\tlogs_cleaned")
    print(f"success\t{len(mappings)}\t{EXECUTOR_PATH}\t{LOG_MODULE_PATH}\t{logs_cleaned}")


def cmd_verify(args):
    """Verify existing executor."""
    if verify_executor():
        print("\nVerification passed")
        sys.exit(0)
    else:
        print("\nVerification failed")
        sys.exit(1)


def cmd_cleanup(args):
    """Clean up old global logs."""
    deleted = cleanup_old_logs(max_age_days=args.max_age_days)
    print(f"Deleted {deleted} old log files")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate execute-script.py with embedded script mappings'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # generate subcommand
    gen_parser = subparsers.add_parser('generate', help='Generate executor and log module')
    gen_parser.add_argument('--force', action='store_true', help='Force regeneration')
    gen_parser.add_argument('--dry-run', action='store_true', help='Show what would be generated')
    gen_parser.set_defaults(func=cmd_generate)

    # verify subcommand
    verify_parser = subparsers.add_parser('verify', help='Verify existing executor')
    verify_parser.set_defaults(func=cmd_verify)

    # cleanup subcommand
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old global logs')
    cleanup_parser.add_argument('--max-age-days', type=int, default=7, help='Max age in days (default: 7)')
    cleanup_parser.set_defaults(func=cmd_cleanup)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
