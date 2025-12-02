#!/usr/bin/env python3
"""
Read and query work-log entries from a plan's work-log.toon file.

Parses TOON format and outputs JSON. Supports filtering by phase and task.

Output: JSON with entries array and metadata.
"""

import argparse
import re
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
# Navigate: scripts -> work-log -> skills -> planning -> bundles -> marketplace -> bundles -> general-tools -> skills -> file-operations-base -> scripts
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]  # marketplace/bundles/planning/skills/work-log -> marketplace
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
TOON_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))
sys.path.insert(0, str(TOON_DIR))

from file_ops import output_success, output_error
from toon_parser import parse_toon


def parse_work_log(content: str) -> tuple[list[dict], dict]:
    """Parse work-log.toon content.

    Uses shared toon_parser for parsing.

    Args:
        content: File content

    Returns:
        Tuple of (entries list, metadata dict)
    """
    # Extract metadata from comments before parsing
    metadata = {
        'plan': None,
        'created': None
    }

    for line in content.splitlines():
        if line.startswith('# Plan:'):
            metadata['plan'] = line.replace('# Plan:', '').strip()
        elif line.startswith('# Created:'):
            metadata['created'] = line.replace('# Created:', '').strip()

    # Use shared TOON parser
    data = parse_toon(content)

    # Extract entries array
    entries = data.get('entries', [])
    if not isinstance(entries, list):
        entries = []

    # Ensure all entries are dicts
    entries = [entry for entry in entries if isinstance(entry, dict)]

    return entries, metadata


def filter_entries(entries: list[dict], phase: str | None, task: str | None) -> list[dict]:
    """Filter entries by phase and/or task.

    Args:
        entries: List of entry dicts
        phase: Phase filter (optional)
        task: Task filter (optional)

    Returns:
        Filtered entries list
    """
    result = entries

    if phase:
        result = [e for e in result if e.get('phase') == phase]

    if task:
        result = [e for e in result if e.get('task') == task]

    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Read work-log entries from a plan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --plan-dir .plan/plans/my-task
  %(prog)s --plan-dir .plan/plans/my-task --phase implement
  %(prog)s --plan-dir .plan/plans/my-task --task task-1
  %(prog)s --plan-dir .plan/plans/my-task --phase implement --task task-2
"""
    )
    parser.add_argument(
        '--plan-dir',
        required=True,
        help='Path to plan directory'
    )
    parser.add_argument(
        '--phase',
        help='Filter by phase (init, refine, implement, verify, finalize)'
    )
    parser.add_argument(
        '--task',
        help='Filter by task identifier (e.g., task-1)'
    )

    args = parser.parse_args()

    # Validate plan directory
    plan_dir = Path(args.plan_dir)
    if not plan_dir.exists():
        output_error(f"Plan directory not found: {plan_dir}")
        return

    # Work-log file path
    log_file = plan_dir / 'work-log.toon'

    # Handle missing file gracefully
    if not log_file.exists():
        output_success({
            'operation': 'read-log',
            'file': str(log_file),
            'total_entries': 0,
            'filtered_entries': 0,
            'entries': [],
            'note': 'No work-log exists yet'
        })
        return

    # Read and parse
    content = log_file.read_text(encoding='utf-8')
    entries, metadata = parse_work_log(content)

    # Filter if requested
    filtered = filter_entries(entries, args.phase, args.task)

    output_success({
        'operation': 'read-log',
        'file': str(log_file),
        'total_entries': len(entries),
        'filtered_entries': len(filtered),
        'entries': filtered,
        'metadata': metadata
    })


if __name__ == '__main__':
    main()
