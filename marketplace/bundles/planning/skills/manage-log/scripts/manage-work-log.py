#!/usr/bin/env python3
"""
Manage work-log.toon files with timestamped entries.

Tracks work progress across phases.

Usage:
    python3 manage-work-log.py add --plan-id my-plan --phase implement --summary "Did X"
    python3 manage-work-log.py read --plan-id my-plan
    python3 manage-work-log.py list --plan-id my-plan --limit 10
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent paths for imports
script_dir = Path(__file__).parent
BUNDLES_DIR = script_dir.parent.parent.parent.parent  # .../bundles/
sys.path.insert(0, str(BUNDLES_DIR / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'))
sys.path.insert(0, str(BUNDLES_DIR / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'))

from file_ops import atomic_write_file, base_path
from toon_parser import parse_toon, serialize_toon


def validate_plan_id(plan_id: str) -> bool:
    """Validate plan_id is kebab-case with no special characters."""
    return bool(re.match(r'^[a-z][a-z0-9-]*$', plan_id))


def get_log_path(plan_id: str) -> Path:
    """Get the work-log.toon file path."""
    return base_path('plans', plan_id, 'work-log.toon')


def now_iso() -> str:
    """Get current time in ISO format (UTC)."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def read_log(plan_id: str) -> dict:
    """Read work-log.toon for a plan."""
    path = get_log_path(plan_id)
    if not path.exists():
        return {'entries': []}
    return parse_toon(path.read_text(encoding='utf-8'))


def write_log(plan_id: str, log: dict):
    """Write work-log.toon for a plan."""
    path = get_log_path(plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"# Plan: {plan_id}\n# Updated: {now_iso()}\n\n"
    atomic_write_file(path, header + serialize_toon(log))


def output_toon(data: dict):
    """Output TOON format to stdout."""
    print(serialize_toon(data))


def cmd_add(args):
    """Add a new log entry."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    # Validate entry type
    valid_types = ['decision', 'artifact', 'progress', 'error', 'outcome']
    entry_type = args.type or 'progress'
    if entry_type not in valid_types:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_type',
            'message': f"Invalid type '{entry_type}'. Valid: {', '.join(valid_types)}"
        })
        sys.exit(1)

    log = read_log(args.plan_id)
    timestamp = now_iso()

    entry = {
        'timestamp': timestamp,
        'type': entry_type,
        'phase': args.phase,
        'summary': args.summary
    }

    # Add detail if provided
    if args.detail:
        entry['detail'] = args.detail

    log['entries'].append(entry)
    write_log(args.plan_id, log)

    result = {
        'status': 'success',
        'plan_id': args.plan_id,
        'type': entry_type,
        'phase': args.phase,
        'timestamp': timestamp,
        'summary': args.summary,
        'total_entries': len(log['entries'])
    }
    if args.detail:
        result['detail'] = args.detail

    output_toon(result)


def cmd_read(args):
    """Read all log entries."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    log = read_log(args.plan_id)
    entries = log.get('entries', [])

    # Filter by phase if specified
    if args.phase:
        entries = [e for e in entries if e.get('phase') == args.phase]

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'total_entries': len(entries),
        'entries': entries
    })


def cmd_list(args):
    """List entries summary."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    log = read_log(args.plan_id)
    entries = log.get('entries', [])
    total = len(entries)

    # Apply limit
    limit = args.limit or total
    entries = entries[-limit:]  # Get most recent

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'total_entries': total,
        'showing': len(entries),
        'entries': entries
    })


def main():
    parser = argparse.ArgumentParser(
        description='Manage work-log.toon files'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # add
    add_parser = subparsers.add_parser('add', help='Add log entry')
    add_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    add_parser.add_argument('--phase', required=True, help='Current phase')
    add_parser.add_argument('--summary', required=True, help='Work summary')
    add_parser.add_argument('--type', choices=['decision', 'artifact', 'progress', 'error', 'outcome'],
                           help='Entry type (default: progress)')
    add_parser.add_argument('--detail', help='Additional context or reasoning (optional)')
    add_parser.set_defaults(func=cmd_add)

    # read
    read_parser = subparsers.add_parser('read', help='Read all entries')
    read_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    read_parser.add_argument('--phase', help='Filter by phase')
    read_parser.set_defaults(func=cmd_read)

    # list
    list_parser = subparsers.add_parser('list', help='List entries summary')
    list_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    list_parser.add_argument('--limit', type=int, help='Max entries to show')
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
