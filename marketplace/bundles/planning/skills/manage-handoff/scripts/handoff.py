#!/usr/bin/env python3
"""
Handoff management script for workflow state transfer between components.

Provides CRUD operations for handoffs using the TOON protocol.
Handoffs are stored plan-locally in .plan/plans/{plan_id}/handoffs/

Usage:
    python3 handoff.py save --plan_id <id> --step <step> --content '<toon>'
    python3 handoff.py load --plan_id <id> --step <step>
    python3 handoff.py list --plan_id <id> [--status <status>]
    python3 handoff.py get --plan_id <id> --file <filename>

Output: TOON format
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import from general-tools bundle (file-operations-base and toon-usage)
SCRIPT_DIR = Path(__file__).parent
GENERAL_TOOLS_DIR = SCRIPT_DIR.parent.parent.parent.parent / 'general-tools' / 'skills'
FILE_OPS_DIR = GENERAL_TOOLS_DIR / 'file-operations-base' / 'scripts'
TOON_DIR = GENERAL_TOOLS_DIR / 'toon-usage' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))
sys.path.insert(0, str(TOON_DIR))

from file_ops import get_base_dir, atomic_write_file, ensure_directory
from toon_parser import parse_toon, serialize_toon, ToonParseError


# =============================================================================
# Constants
# =============================================================================

VALID_STATUSES = {'pending', 'in_progress', 'completed', 'failed', 'blocked'}
REQUIRED_FIELDS = {'from', 'to', 'plan_id'}
REQUIRED_TASK_FIELDS = {'status'}


# =============================================================================
# Path Helpers
# =============================================================================

def get_handoff_dir(plan_id: str) -> Path:
    """Get the handoff directory for a specific plan."""
    return get_base_dir() / 'plans' / plan_id / 'handoffs'


# =============================================================================
# Validation
# =============================================================================

def validate_handoff(data: dict) -> tuple[bool, list[str]]:
    """Validate handoff data structure.

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Check required top-level fields
    missing_fields = REQUIRED_FIELDS - set(data.keys())
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(sorted(missing_fields))}")

    # Check task.status if task exists
    task = data.get('task', {})
    if isinstance(task, dict):
        if 'status' not in task:
            errors.append("Missing required field: task.status")
        elif task.get('status') not in VALID_STATUSES:
            errors.append(f"Invalid task.status '{task.get('status')}'. Valid: {', '.join(sorted(VALID_STATUSES))}")

        # Validate progress if present
        progress = task.get('progress')
        if progress is not None:
            if isinstance(progress, (int, float)):
                if progress < 0 or progress > 100:
                    # Clamp and warn (not an error per spec)
                    pass
            else:
                errors.append(f"Invalid task.progress type: {type(progress).__name__}")
    else:
        errors.append("Missing required field: task.status")

    return len(errors) == 0, errors


def generate_timestamp() -> str:
    """Generate ISO timestamp with timezone."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def generate_filename(step: str) -> str:
    """Generate handoff filename with timestamp (no plan_id prefix)."""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    # Sanitize step for filename
    safe_step = re.sub(r'[^\w\-]', '-', step)
    return f"{safe_step}-{timestamp}.toon"


# =============================================================================
# TOON Output Helpers
# =============================================================================

def output_success(operation: str, **kwargs) -> None:
    """Print TOON success output."""
    data = {'status': 'success', 'operation': operation}
    data.update(kwargs)
    print(serialize_toon(data))


def output_error(error_type: str, message: str, **kwargs) -> None:
    """Print TOON error output."""
    data = {
        'status': 'error',
        'error': {
            'type': error_type,
            'message': message
        }
    }
    data['error'].update(kwargs)
    print(serialize_toon(data))
    sys.exit(1)


# =============================================================================
# Commands
# =============================================================================

def cmd_save(args):
    """Save a handoff to the plan's handoff directory."""
    # Parse the handoff content
    try:
        data = parse_toon(args.content)
    except ToonParseError as e:
        output_error('parse_error', f'Failed to parse TOON content: {e}')
        return

    # Ensure plan_id is set
    if 'plan_id' not in data:
        data['plan_id'] = args.plan_id

    # Add timestamp if not present
    if 'timestamp' not in data:
        data['timestamp'] = generate_timestamp()

    # Validate the handoff
    is_valid, errors = validate_handoff(data)
    if not is_valid:
        output_error('validation_error', 'Invalid handoff structure', missing_fields=errors)
        return

    # Generate filename and path (plan-local)
    filename = generate_filename(args.step)
    handoff_path = get_handoff_dir(args.plan_id) / filename

    # Ensure directory exists
    ensure_directory(handoff_path)

    # Write the handoff
    content = serialize_toon(data)
    atomic_write_file(handoff_path, content)

    output_success('save', file=filename, handoff={
        'plan_id': args.plan_id,
        'step': args.step,
        'timestamp': data['timestamp']
    })


def cmd_load(args):
    """Load most recent handoff by plan_id and step."""
    handoff_dir = get_handoff_dir(args.plan_id)

    if not handoff_dir.exists():
        output_error('not_found', f'No handoffs found for plan_id={args.plan_id}, step={args.step}')
        return

    # Find matching files (filename no longer has plan_id prefix)
    pattern = f"{args.step}-*.toon"
    matches = sorted(handoff_dir.glob(pattern), reverse=True)

    if not matches:
        output_error('not_found', f'No handoffs found for plan_id={args.plan_id}, step={args.step}')
        return

    # Load the most recent one
    latest = matches[0]
    try:
        content = latest.read_text()
        data = parse_toon(content)
    except Exception as e:
        output_error('read_error', f'Failed to read handoff: {e}')
        return

    output_success('load', file=latest.name, handoff=data)


def cmd_list(args):
    """List handoffs for a specific plan."""
    handoff_dir = get_handoff_dir(args.plan_id)

    if not handoff_dir.exists():
        output_success('list', counts={'total': 0}, handoffs=[])
        return

    # Get all handoff files
    files = list(handoff_dir.glob('*.toon'))

    # Load and optionally filter by status
    handoffs = []
    status_counts = {'pending': 0, 'in_progress': 0, 'completed': 0, 'failed': 0, 'blocked': 0}

    for f in sorted(files, reverse=True):
        try:
            content = f.read_text()
            data = parse_toon(content)

            task_status = data.get('task', {}).get('status', 'unknown')
            if task_status in status_counts:
                status_counts[task_status] += 1

            # Filter by status if specified
            if args.status and task_status != args.status:
                continue

            # Extract step from filename (format: {step}-{timestamp}.toon)
            parts = f.stem.rsplit('-', 1)
            step = parts[0] if len(parts) >= 1 else 'unknown'

            handoffs.append({
                'step': step,
                'status': task_status,
                'timestamp': data.get('timestamp', ''),
                'file': f.name
            })
        except Exception:
            # Skip malformed files
            continue

    output_success('list',
        counts={
            'total': len(handoffs),
            **{k: v for k, v in status_counts.items() if v > 0}
        },
        handoffs=handoffs
    )


def cmd_get(args):
    """Get a specific handoff by filename."""
    handoff_path = get_handoff_dir(args.plan_id) / args.file

    if not handoff_path.exists():
        output_error('not_found', f'Handoff file not found: {args.file}')
        return

    try:
        content = handoff_path.read_text()
        data = parse_toon(content)
    except Exception as e:
        output_error('read_error', f'Failed to read handoff: {e}')
        return

    output_success('get', file=args.file, handoff=data)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Handoff management for workflow state transfer',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # save command
    save_parser = subparsers.add_parser('save', help='Save a handoff')
    save_parser.add_argument('--plan_id', required=True, help='Plan identifier')
    save_parser.add_argument('--step', required=True, help='Step name (e.g., init-complete)')
    save_parser.add_argument('--content', required=True, help='TOON handoff content')

    # load command
    load_parser = subparsers.add_parser('load', help='Load most recent handoff')
    load_parser.add_argument('--plan_id', required=True, help='Plan identifier')
    load_parser.add_argument('--step', required=True, help='Step name')

    # list command
    list_parser = subparsers.add_parser('list', help='List handoffs for a plan')
    list_parser.add_argument('--plan_id', required=True, help='Plan identifier')
    list_parser.add_argument('--status', choices=list(VALID_STATUSES), help='Filter by status')

    # get command
    get_parser = subparsers.add_parser('get', help='Get specific handoff')
    get_parser.add_argument('--plan_id', required=True, help='Plan identifier')
    get_parser.add_argument('--file', required=True, help='Handoff filename')

    args = parser.parse_args()

    # Dispatch to command handler
    commands = {
        'save': cmd_save,
        'load': cmd_load,
        'list': cmd_list,
        'get': cmd_get
    }

    commands[args.command](args)


if __name__ == '__main__':
    main()
