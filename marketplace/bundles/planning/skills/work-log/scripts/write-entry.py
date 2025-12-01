#!/usr/bin/env python3
"""
Add a work-log entry to a plan's work-log.toon file.

Creates work-log.toon if it doesn't exist, appends new entry with timestamp.
Uses TOON format for token efficiency.

Output: JSON with success status and entry details.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
# Navigate: scripts -> work-log -> skills -> planning -> bundles -> marketplace -> bundles -> general-tools -> skills -> file-operations-base -> scripts
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]  # marketplace/bundles/planning/skills/work-log -> marketplace
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, output_success, output_error


def escape_toon_value(value: str) -> str:
    """Escape value for TOON CSV format if needed.

    Args:
        value: String value to escape

    Returns:
        Escaped string (quoted if contains comma or newline)
    """
    if ',' in value or '\n' in value or '"' in value:
        # Escape internal quotes and wrap in quotes
        escaped = value.replace('"', '""')
        return f'"{escaped}"'
    return value


def parse_existing_log(content: str) -> tuple[list[str], int]:
    """Parse existing work-log.toon to get header and entry count.

    Args:
        content: File content

    Returns:
        Tuple of (header lines, entry count)
    """
    lines = content.strip().split('\n') if content.strip() else []
    header_lines = []
    entry_count = 0

    for line in lines:
        if line.startswith('#') or line.startswith('entries[') or not line.strip():
            header_lines.append(line)
        else:
            entry_count += 1

    return header_lines, entry_count


def create_new_log(plan_name: str) -> str:
    """Create initial work-log.toon content.

    Args:
        plan_name: Name of the plan

    Returns:
        Initial file content with header
    """
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    return f"""# Work Log
# Plan: {plan_name}
# Created: {now}

entries[0]{{timestamp,phase,task,action,result}}:
"""


def add_entry(content: str, phase: str, task: str, action: str, result: str) -> tuple[str, dict]:
    """Add entry to work-log content.

    Args:
        content: Existing file content
        phase: Plan phase
        task: Task identifier
        action: Action description
        result: Result/artifact

    Returns:
        Tuple of (updated content, entry dict)
    """
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = content.strip().split('\n') if content.strip() else []

    # Find and update the entries header
    new_lines = []
    entry_count = 0
    header_updated = False

    for line in lines:
        if line.startswith('entries[') and not header_updated:
            # Count existing entries (lines after header that aren't empty/comments)
            idx = lines.index(line)
            for subsequent in lines[idx + 1:]:
                if subsequent.strip() and not subsequent.startswith('#'):
                    entry_count += 1
            # Update count in header
            new_count = entry_count + 1
            new_lines.append(f'entries[{new_count}]{{timestamp,phase,task,action,result}}:')
            header_updated = True
        else:
            new_lines.append(line)

    # Create entry line
    entry_line = ','.join([
        timestamp,
        escape_toon_value(phase),
        escape_toon_value(task),
        escape_toon_value(action),
        escape_toon_value(result)
    ])
    new_lines.append(entry_line)

    entry = {
        'timestamp': timestamp,
        'phase': phase,
        'task': task,
        'action': action,
        'result': result
    }

    return '\n'.join(new_lines), entry


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Add a work-log entry to a plan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --plan-dir .plan/plans/my-task --phase implement --task task-1 \\
           --action "Created service class" --result "src/Service.java"

  %(prog)s --plan-dir /path/to/plan --phase verify --task task-2 \\
           --action "Ran build with tests" --result "Build passed, 15 tests"
"""
    )
    parser.add_argument(
        '--plan-dir',
        required=True,
        help='Path to plan directory'
    )
    parser.add_argument(
        '--phase',
        required=True,
        help='Current phase (init, refine, implement, verify, finalize)'
    )
    parser.add_argument(
        '--task',
        required=True,
        help='Task identifier (e.g., task-1)'
    )
    parser.add_argument(
        '--action',
        required=True,
        help='Action description (result-oriented, past tense)'
    )
    parser.add_argument(
        '--result',
        required=True,
        help='Result or artifact (file path, status, decision rationale)'
    )

    args = parser.parse_args()

    # Validate plan directory
    plan_dir = Path(args.plan_dir)
    if not plan_dir.exists():
        output_error(f"Plan directory not found: {plan_dir}")
        return

    # Get plan name from directory
    plan_name = plan_dir.name

    # Work-log file path
    log_file = plan_dir / 'work-log.toon'

    # Read or create content
    if log_file.exists():
        content = log_file.read_text(encoding='utf-8')
    else:
        content = create_new_log(plan_name)

    # Add entry
    updated_content, entry = add_entry(
        content,
        args.phase,
        args.task,
        args.action,
        args.result
    )

    # Write file
    try:
        atomic_write_file(log_file, updated_content)
    except OSError as e:
        output_error(f"Failed to write log file: {e}")
        return

    # Count entries for output
    _, entry_count = parse_existing_log(updated_content)

    output_success({
        'operation': 'log-entry',
        'file': str(log_file),
        'entry_count': entry_count,
        'entry': entry
    })


if __name__ == '__main__':
    main()
