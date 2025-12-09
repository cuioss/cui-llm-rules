#!/usr/bin/env python3
"""
Manage numbered goals within a plan.

Single CLI with subcommands for CRUD operations on goal files.
Uses TOON format for both storage and output.

Subcommands:
  add      - Add a new goal
  update   - Update an existing goal
  remove   - Remove a goal
  list     - List all goals (summary)
  findAll  - Get all goals with full content
  get      - Get a single goal by number
  check    - Mark goal done/pending

Output: TOON format for all operations.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Import file operations from base module
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent.parent.parent / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, base_path


def now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def slugify(title: str, max_length: int = 40) -> str:
    """Convert title to kebab-case slug.

    Args:
        title: The title to convert
        max_length: Maximum slug length (default 40)

    Returns:
        Kebab-case slug
    """
    # Lowercase and replace spaces with hyphens
    slug = title.lower().replace(' ', '-')
    # Remove special characters (keep alphanumeric and hyphens)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Truncate
    slug = slug[:max_length]
    # Remove trailing hyphens
    slug = slug.rstrip('-')
    return slug


def get_goals_dir(plan_id: str) -> Path:
    """Get the goals directory for a plan.

    Args:
        plan_id: The plan identifier

    Returns:
        Path to goals directory
    """
    return base_path('plans', plan_id, 'goals')


def parse_goal_file(content: str) -> dict:
    """Parse a goal TOON file into a dictionary.

    Args:
        content: File content

    Returns:
        Dictionary with goal fields
    """
    result = {}
    lines = content.split('\n')
    i = 0

    # Parse key: value lines until we hit body
    while i < len(lines):
        line = lines[i]

        if line.startswith('body:'):
            # Check for multiline body (body: |)
            if line.strip() == 'body: |':
                # Collect indented lines
                body_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].startswith('  '):
                        body_lines.append(lines[i][2:])  # Remove 2-space indent
                    elif lines[i].strip() == '':
                        body_lines.append('')
                    else:
                        break
                    i += 1
                result['body'] = '\n'.join(body_lines).strip()
            else:
                # Single line body
                result['body'] = line[5:].strip()
                i += 1
        elif ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Convert number to int
            if key == 'number':
                value = int(value)
            result[key] = value
            i += 1
        else:
            i += 1

    return result


def format_goal_file(goal: dict) -> str:
    """Format a goal dictionary as TOON file content.

    Args:
        goal: Goal dictionary

    Returns:
        TOON formatted string
    """
    lines = [
        f"number: {goal['number']}",
        f"title: {goal['title']}",
        f"status: {goal['status']}",
        f"created: {goal['created']}",
        f"updated: {goal['updated']}",
        "",
        "body: |",
    ]

    # Add body with 2-space indent
    for body_line in goal['body'].split('\n'):
        lines.append(f"  {body_line}")

    return '\n'.join(lines)


def find_goal_file(goal_dir: Path, number: int) -> Optional[Path]:
    """Find goal file by number.

    Args:
        goal_dir: Goals directory
        number: Goal number

    Returns:
        Path to file or None if not found
    """
    pattern = f"GOAL-{number:03d}-*.toon"
    matches = list(goal_dir.glob(pattern))
    return matches[0] if matches else None


def get_next_number(goal_dir: Path) -> int:
    """Get next available goal number.

    Args:
        goal_dir: Goals directory

    Returns:
        Next available number
    """
    if not goal_dir.exists():
        return 1

    max_num = 0
    for f in goal_dir.glob("GOAL-*.toon"):
        try:
            # Extract number from GOAL-NNN-slug.toon
            num = int(f.name[5:8])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass

    return max_num + 1


def get_all_goals(goal_dir: Path) -> list:
    """Get all goals sorted by number.

    Args:
        goal_dir: Goals directory

    Returns:
        List of (path, goal_dict) tuples
    """
    if not goal_dir.exists():
        return []

    goals = []
    for f in sorted(goal_dir.glob("GOAL-*.toon")):
        content = f.read_text(encoding='utf-8')
        goal = parse_goal_file(content)
        goals.append((f, goal))

    return sorted(goals, key=lambda x: x[1].get('number', 0))


def output_toon(data: dict) -> None:
    """Print TOON formatted output."""
    lines = []

    # Top-level simple fields
    for key in ['status', 'plan_id', 'file', 'renamed', 'total_goals']:
        if key in data:
            lines.append(f"{key}: {data[key]}")

    # Counts block
    if 'counts' in data:
        lines.append("")
        lines.append("counts:")
        for k, v in data['counts'].items():
            lines.append(f"  {k}: {v}")

    # Single goal block
    if 'goal' in data:
        lines.append("")
        lines.append("goal:")
        goal = data['goal']
        for key in ['number', 'title', 'status', 'created', 'updated']:
            if key in goal:
                lines.append(f"  {key}: {goal[key]}")
        if 'body' in goal:
            lines.append(f"  body: {goal['body']}")

    # Removed block
    if 'removed' in data:
        lines.append("")
        lines.append("removed:")
        rem = data['removed']
        for key in ['number', 'title', 'file']:
            if key in rem:
                lines.append(f"  {key}: {rem[key]}")

    # Goals list (tabular)
    if 'goals_table' in data:
        goals = data['goals_table']
        lines.append("")
        lines.append(f"goals[{len(goals)}]{{number,title,status,file}}:")
        for g in goals:
            lines.append(f"{g['number']},{g['title']},{g['status']},{g['file']}")

    # Goals list (full)
    if 'goals_full' in data:
        goals = data['goals_full']
        lines.append("")
        lines.append("goals:")
        for g in goals:
            lines.append(f"  - number: {g['number']}")
            lines.append(f"    title: {g['title']}")
            lines.append(f"    status: {g['status']}")
            lines.append(f"    created: {g['created']}")
            lines.append(f"    updated: {g['updated']}")
            # Body on single line for full output
            body_oneline = g.get('body', '').replace('\n', ' ').strip()
            lines.append(f"    body: {body_oneline}")
            lines.append("")

    print('\n'.join(lines))


def output_error(message: str) -> None:
    """Print TOON error output to stderr."""
    print(f"status: error\nmessage: {message}", file=sys.stderr)


# ============================================================================
# Subcommand handlers
# ============================================================================

def cmd_add(args) -> int:
    """Handle 'add' subcommand."""
    goal_dir = get_goals_dir(args.plan_id)

    # Get next number
    number = get_next_number(goal_dir)

    # Generate slug and filename
    slug = slugify(args.title)
    filename = f"GOAL-{number:03d}-{slug}.toon"
    filepath = goal_dir / filename

    # Create goal
    now = now_iso()
    goal = {
        'number': number,
        'title': args.title,
        'status': 'pending',
        'created': now,
        'updated': now,
        'body': args.body
    }

    # Write file
    content = format_goal_file(goal)
    atomic_write_file(filepath, content)

    # Count total
    total = len(list(goal_dir.glob("GOAL-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filename,
        'total_goals': total,
        'goal': {
            'number': number,
            'title': args.title,
            'status': 'pending'
        }
    })
    return 0


def cmd_update(args) -> int:
    """Handle 'update' subcommand."""
    goal_dir = get_goals_dir(args.plan_id)

    # Find existing file
    filepath = find_goal_file(goal_dir, args.number)
    if not filepath:
        output_error(f"Goal GOAL-{args.number} not found")
        return 1

    # Read current content
    content = filepath.read_text(encoding='utf-8')
    goal = parse_goal_file(content)

    # Update fields
    renamed = False
    old_title = goal['title']

    if args.title:
        goal['title'] = args.title
    if args.body:
        goal['body'] = args.body
    if args.status:
        if args.status not in ('pending', 'done'):
            output_error(f"Invalid status: {args.status}. Must be 'pending' or 'done'")
            return 1
        goal['status'] = args.status

    goal['updated'] = now_iso()

    # Check if rename needed
    new_filename = filepath.name
    if args.title and args.title != old_title:
        new_slug = slugify(args.title)
        new_filename = f"GOAL-{args.number:03d}-{new_slug}.toon"
        renamed = True

    # Write file
    new_content = format_goal_file(goal)
    new_filepath = goal_dir / new_filename

    if renamed:
        atomic_write_file(new_filepath, new_content)
        filepath.unlink()
    else:
        atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': new_filename,
        'renamed': renamed,
        'goal': {
            'number': goal['number'],
            'title': goal['title'],
            'status': goal['status']
        }
    })
    return 0


def cmd_remove(args) -> int:
    """Handle 'remove' subcommand."""
    goal_dir = get_goals_dir(args.plan_id)

    # Find existing file
    filepath = find_goal_file(goal_dir, args.number)
    if not filepath:
        output_error(f"Goal GOAL-{args.number} not found")
        return 1

    # Read for output
    content = filepath.read_text(encoding='utf-8')
    goal = parse_goal_file(content)
    filename = filepath.name

    # Delete file
    filepath.unlink()

    # Count remaining
    total = len(list(goal_dir.glob("GOAL-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'total_goals': total,
        'removed': {
            'number': goal['number'],
            'title': goal['title'],
            'file': filename
        }
    })
    return 0


def cmd_list(args) -> int:
    """Handle 'list' subcommand."""
    goal_dir = get_goals_dir(args.plan_id)
    all_goals = get_all_goals(goal_dir)

    # Filter by status
    if args.status and args.status != 'all':
        all_goals = [(p, g) for p, g in all_goals if g.get('status') == args.status]

    # Compute counts from all (not filtered)
    all_for_counts = get_all_goals(goal_dir)
    pending = sum(1 for _, g in all_for_counts if g.get('status') == 'pending')
    done = sum(1 for _, g in all_for_counts if g.get('status') == 'done')

    # Build table data
    table = []
    for path, goal in all_goals:
        table.append({
            'number': goal['number'],
            'title': goal['title'],
            'status': goal['status'],
            'file': path.name
        })

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'counts': {
            'total': len(all_for_counts),
            'pending': pending,
            'done': done
        },
        'goals_table': table
    })
    return 0


def cmd_find_all(args) -> int:
    """Handle 'findAll' subcommand."""
    goal_dir = get_goals_dir(args.plan_id)
    all_goals = get_all_goals(goal_dir)

    # Compute counts
    pending = sum(1 for _, g in all_goals if g.get('status') == 'pending')
    done = sum(1 for _, g in all_goals if g.get('status') == 'done')

    # Build full data
    full = []
    for _, goal in all_goals:
        full.append({
            'number': goal['number'],
            'title': goal['title'],
            'status': goal['status'],
            'created': goal.get('created', ''),
            'updated': goal.get('updated', ''),
            'body': goal.get('body', '')
        })

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'counts': {
            'total': len(all_goals),
            'pending': pending,
            'done': done
        },
        'goals_full': full
    })
    return 0


def cmd_get(args) -> int:
    """Handle 'get' subcommand."""
    goal_dir = get_goals_dir(args.plan_id)

    # Find file
    filepath = find_goal_file(goal_dir, args.number)
    if not filepath:
        output_error(f"Goal GOAL-{args.number} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    goal = parse_goal_file(content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filepath.name,
        'goal': {
            'number': goal['number'],
            'title': goal['title'],
            'status': goal['status'],
            'created': goal.get('created', ''),
            'updated': goal.get('updated', ''),
            'body': goal.get('body', '')
        }
    })
    return 0


def cmd_check(args) -> int:
    """Handle 'check' subcommand."""
    goal_dir = get_goals_dir(args.plan_id)

    # Validate status
    if args.status not in ('pending', 'done'):
        output_error(f"Invalid status: {args.status}. Must be 'pending' or 'done'")
        return 1

    # Find file
    filepath = find_goal_file(goal_dir, args.number)
    if not filepath:
        output_error(f"Goal GOAL-{args.number} not found")
        return 1

    # Read and update
    content = filepath.read_text(encoding='utf-8')
    goal = parse_goal_file(content)
    goal['status'] = args.status
    goal['updated'] = now_iso()

    # Write back
    new_content = format_goal_file(goal)
    atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filepath.name,
        'goal': {
            'number': goal['number'],
            'title': goal['title'],
            'status': goal['status']
        }
    })
    return 0


# ============================================================================
# CLI setup
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description='Manage numbered goals within a plan',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # add
    p_add = subparsers.add_parser('add', help='Add a new goal')
    p_add.add_argument('--plan-id', required=True, help='Plan identifier')
    p_add.add_argument('--title', required=True, help='Goal title')
    p_add.add_argument('--body', required=True, help='Goal body/description')

    # update
    p_update = subparsers.add_parser('update', help='Update an existing goal')
    p_update.add_argument('--plan-id', required=True, help='Plan identifier')
    p_update.add_argument('--number', required=True, type=int, help='Goal number')
    p_update.add_argument('--title', help='New title')
    p_update.add_argument('--body', help='New body')
    p_update.add_argument('--status', help='New status (pending/done)')

    # remove
    p_remove = subparsers.add_parser('remove', help='Remove a goal')
    p_remove.add_argument('--plan-id', required=True, help='Plan identifier')
    p_remove.add_argument('--number', required=True, type=int, help='Goal number')

    # list
    p_list = subparsers.add_parser('list', help='List all goals')
    p_list.add_argument('--plan-id', required=True, help='Plan identifier')
    p_list.add_argument('--status', choices=['pending', 'done', 'all'],
                        default='all', help='Filter by status')

    # findAll
    p_find_all = subparsers.add_parser('findAll', help='Get all goals with full content')
    p_find_all.add_argument('--plan-id', required=True, help='Plan identifier')

    # get
    p_get = subparsers.add_parser('get', help='Get a single goal')
    p_get.add_argument('--plan-id', required=True, help='Plan identifier')
    p_get.add_argument('--number', required=True, type=int, help='Goal number')

    # check
    p_check = subparsers.add_parser('check', help='Mark goal done/pending')
    p_check.add_argument('--plan-id', required=True, help='Plan identifier')
    p_check.add_argument('--number', required=True, type=int, help='Goal number')
    p_check.add_argument('--status', required=True, choices=['pending', 'done'],
                         help='New status')

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == 'add':
            return cmd_add(args)
        elif args.command == 'update':
            return cmd_update(args)
        elif args.command == 'remove':
            return cmd_remove(args)
        elif args.command == 'list':
            return cmd_list(args)
        elif args.command == 'findAll':
            return cmd_find_all(args)
        elif args.command == 'get':
            return cmd_get(args)
        elif args.command == 'check':
            return cmd_check(args)
        else:
            output_error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        output_error(str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
