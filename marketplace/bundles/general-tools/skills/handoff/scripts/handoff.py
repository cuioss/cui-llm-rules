#!/usr/bin/env python3
"""
Handoff management script for workflow state transfer between components.

Provides CRUD operations for handoffs using the TOON protocol.

Usage:
    python3 handoff.py save --plan_id <id> --step <step> --content '<toon>'
    python3 handoff.py load --plan_id <id> --step <step>
    python3 handoff.py list [--plan_id <id>] [--since 7d] [--status <status>]
    python3 handoff.py get --file <filename>
    python3 handoff.py cleanup [--older-than 7d] [--plan_id <id>]

Output: TOON format
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Import from file-operations-base and toon-usage
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent / 'file-operations-base' / 'scripts'
TOON_DIR = SCRIPT_DIR.parent.parent / 'toon-usage' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))
sys.path.insert(0, str(TOON_DIR))

from file_ops import get_base_dir, atomic_write_file, ensure_directory
from toon_parser import parse_toon, serialize_toon, ToonParseError


# =============================================================================
# Constants
# =============================================================================

HANDOFF_DIR = 'memory/handoffs'
VALID_STATUSES = {'pending', 'in_progress', 'completed', 'failed', 'blocked'}
REQUIRED_FIELDS = {'from', 'to', 'plan_id'}
REQUIRED_TASK_FIELDS = {'status'}


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


def generate_filename(plan_id: str, step: str) -> str:
    """Generate handoff filename with timestamp."""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    # Sanitize plan_id and step for filename
    safe_plan_id = re.sub(r'[^\w\-]', '-', plan_id)
    safe_step = re.sub(r'[^\w\-]', '-', step)
    return f"{safe_plan_id}-{safe_step}-{timestamp}.toon"


def parse_duration(duration_str: str) -> timedelta:
    """Parse duration string like '7d', '24h', '30m'."""
    match = re.match(r'^(\d+)([dhm])$', duration_str)
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}. Use format like '7d', '24h', '30m'")

    value = int(match.group(1))
    unit = match.group(2)

    if unit == 'd':
        return timedelta(days=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'm':
        return timedelta(minutes=value)

    raise ValueError(f"Unknown duration unit: {unit}")


def parse_timestamp_from_filename(filename: str) -> datetime | None:
    """Extract timestamp from handoff filename."""
    # Format: {plan_id}-{step}-{timestamp}.toon
    # Timestamp format: YYYYMMDDTHHMMSSZ
    match = re.search(r'-(\d{8}T\d{6}Z)\.toon$', filename)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


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
    """Save a handoff to the memory layer."""
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

    # Generate filename and path
    filename = generate_filename(args.plan_id, args.step)
    handoff_path = get_base_dir() / HANDOFF_DIR / filename

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
    handoff_dir = get_base_dir() / HANDOFF_DIR

    if not handoff_dir.exists():
        output_error('not_found', f'No handoffs found for plan_id={args.plan_id}, step={args.step}')
        return

    # Find matching files
    pattern = f"{args.plan_id}-{args.step}-*.toon"
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
    """List handoffs with optional filtering."""
    handoff_dir = get_base_dir() / HANDOFF_DIR

    if not handoff_dir.exists():
        output_success('list', counts={'total': 0}, handoffs=[])
        return

    # Get all handoff files
    files = list(handoff_dir.glob('*.toon'))

    # Filter by plan_id if specified
    if args.plan_id:
        files = [f for f in files if f.name.startswith(f"{args.plan_id}-")]

    # Filter by age if specified
    if args.since:
        try:
            max_age = parse_duration(args.since)
            cutoff = datetime.now(timezone.utc) - max_age
            filtered = []
            for f in files:
                ts = parse_timestamp_from_filename(f.name)
                if ts and ts >= cutoff:
                    filtered.append(f)
            files = filtered
        except ValueError as e:
            output_error('invalid_argument', str(e))
            return

    # Load and filter by status if specified
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

            # Extract parts from filename
            parts = f.stem.rsplit('-', 2)
            if len(parts) >= 3:
                plan_id = '-'.join(parts[:-2])
                step = parts[-2]
            else:
                plan_id = data.get('plan_id', 'unknown')
                step = 'unknown'

            handoffs.append({
                'plan_id': plan_id,
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
    handoff_path = get_base_dir() / HANDOFF_DIR / args.file

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


def cmd_cleanup(args):
    """Remove old handoffs based on age."""
    handoff_dir = get_base_dir() / HANDOFF_DIR

    if not handoff_dir.exists():
        output_success('cleanup', removed_count=0, removed=[])
        return

    # Parse the age threshold
    try:
        max_age = parse_duration(args.older_than)
    except ValueError as e:
        output_error('invalid_argument', str(e))
        return

    cutoff = datetime.now(timezone.utc) - max_age

    # Get all handoff files
    files = list(handoff_dir.glob('*.toon'))

    # Filter by plan_id if specified
    if args.plan_id:
        files = [f for f in files if f.name.startswith(f"{args.plan_id}-")]

    # Find and remove old files
    removed = []
    for f in files:
        ts = parse_timestamp_from_filename(f.name)
        if ts and ts < cutoff:
            age_days = (datetime.now(timezone.utc) - ts).days
            try:
                f.unlink()
                # Extract plan_id from filename
                parts = f.stem.rsplit('-', 2)
                plan_id = '-'.join(parts[:-2]) if len(parts) >= 3 else 'unknown'
                removed.append({
                    'file': f.name,
                    'plan_id': plan_id,
                    'age': f'{age_days}d'
                })
            except OSError:
                pass  # Skip files we can't remove

    output_success('cleanup', removed_count=len(removed), removed=removed)


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
    list_parser = subparsers.add_parser('list', help='List handoffs')
    list_parser.add_argument('--plan_id', help='Filter by plan ID')
    list_parser.add_argument('--since', help='Filter by age (e.g., 7d, 24h)')
    list_parser.add_argument('--status', choices=list(VALID_STATUSES), help='Filter by status')

    # get command
    get_parser = subparsers.add_parser('get', help='Get specific handoff')
    get_parser.add_argument('--file', required=True, help='Handoff filename')

    # cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove old handoffs')
    cleanup_parser.add_argument('--older-than', dest='older_than', default='7d',
                                help='Remove handoffs older than (e.g., 7d, 24h)')
    cleanup_parser.add_argument('--plan_id', help='Filter by plan ID')

    args = parser.parse_args()

    # Dispatch to command handler
    commands = {
        'save': cmd_save,
        'load': cmd_load,
        'list': cmd_list,
        'get': cmd_get,
        'cleanup': cmd_cleanup
    }

    commands[args.command](args)


if __name__ == '__main__':
    main()
