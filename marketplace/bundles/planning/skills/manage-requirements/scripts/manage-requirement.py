#!/usr/bin/env python3
"""
Manage numbered requirements within a plan.

Single CLI with subcommands for CRUD operations on requirement files.
Uses TOON format for both storage and output.

Subcommands:
  add      - Add a new requirement
  update   - Update an existing requirement
  remove   - Remove a requirement
  list     - List all requirements (summary)
  findAll  - Get all requirements with full content
  get      - Get a single requirement by number
  check    - Mark requirement done/pending

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


def get_requirements_dir(plan_id: str) -> Path:
    """Get the requirements directory for a plan.

    Args:
        plan_id: The plan identifier

    Returns:
        Path to requirements directory
    """
    return base_path('plans', plan_id, 'requirements')


def parse_requirement_file(content: str) -> dict:
    """Parse a requirement TOON file into a dictionary.

    Args:
        content: File content

    Returns:
        Dictionary with requirement fields
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


def format_requirement_file(req: dict) -> str:
    """Format a requirement dictionary as TOON file content.

    Args:
        req: Requirement dictionary

    Returns:
        TOON formatted string
    """
    lines = [
        f"number: {req['number']}",
        f"title: {req['title']}",
        f"status: {req['status']}",
        f"created: {req['created']}",
        f"updated: {req['updated']}",
        "",
        "body: |",
    ]

    # Add body with 2-space indent
    for body_line in req['body'].split('\n'):
        lines.append(f"  {body_line}")

    return '\n'.join(lines)


def find_requirement_file(req_dir: Path, number: int) -> Optional[Path]:
    """Find requirement file by number.

    Args:
        req_dir: Requirements directory
        number: Requirement number

    Returns:
        Path to file or None if not found
    """
    pattern = f"REQ-{number:03d}-*.toon"
    matches = list(req_dir.glob(pattern))
    return matches[0] if matches else None


def get_next_number(req_dir: Path) -> int:
    """Get next available requirement number.

    Args:
        req_dir: Requirements directory

    Returns:
        Next available number
    """
    if not req_dir.exists():
        return 1

    max_num = 0
    for f in req_dir.glob("REQ-*.toon"):
        try:
            # Extract number from REQ-NNN-slug.toon
            num = int(f.name[4:7])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass

    return max_num + 1


def get_all_requirements(req_dir: Path) -> list:
    """Get all requirements sorted by number.

    Args:
        req_dir: Requirements directory

    Returns:
        List of (path, requirement_dict) tuples
    """
    if not req_dir.exists():
        return []

    reqs = []
    for f in sorted(req_dir.glob("REQ-*.toon")):
        content = f.read_text(encoding='utf-8')
        req = parse_requirement_file(content)
        reqs.append((f, req))

    return sorted(reqs, key=lambda x: x[1].get('number', 0))


def output_toon(data: dict) -> None:
    """Print TOON formatted output."""
    lines = []

    # Top-level simple fields
    for key in ['status', 'plan_id', 'file', 'renamed', 'total_requirements']:
        if key in data:
            lines.append(f"{key}: {data[key]}")

    # Counts block
    if 'counts' in data:
        lines.append("")
        lines.append("counts:")
        for k, v in data['counts'].items():
            lines.append(f"  {k}: {v}")

    # Single requirement block
    if 'requirement' in data:
        lines.append("")
        lines.append("requirement:")
        req = data['requirement']
        for key in ['number', 'title', 'status', 'created', 'updated']:
            if key in req:
                lines.append(f"  {key}: {req[key]}")
        if 'body' in req:
            lines.append(f"  body: {req['body']}")

    # Removed block
    if 'removed' in data:
        lines.append("")
        lines.append("removed:")
        rem = data['removed']
        for key in ['number', 'title', 'file']:
            if key in rem:
                lines.append(f"  {key}: {rem[key]}")

    # Requirements list (tabular)
    if 'requirements_table' in data:
        reqs = data['requirements_table']
        lines.append("")
        lines.append(f"requirements[{len(reqs)}]{{number,title,status,file}}:")
        for r in reqs:
            lines.append(f"{r['number']},{r['title']},{r['status']},{r['file']}")

    # Requirements list (full)
    if 'requirements_full' in data:
        reqs = data['requirements_full']
        lines.append("")
        lines.append("requirements:")
        for r in reqs:
            lines.append(f"  - number: {r['number']}")
            lines.append(f"    title: {r['title']}")
            lines.append(f"    status: {r['status']}")
            lines.append(f"    created: {r['created']}")
            lines.append(f"    updated: {r['updated']}")
            # Body on single line for full output
            body_oneline = r.get('body', '').replace('\n', ' ').strip()
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
    req_dir = get_requirements_dir(args.plan_id)

    # Get next number
    number = get_next_number(req_dir)

    # Generate slug and filename
    slug = slugify(args.title)
    filename = f"REQ-{number:03d}-{slug}.toon"
    filepath = req_dir / filename

    # Create requirement
    now = now_iso()
    req = {
        'number': number,
        'title': args.title,
        'status': 'pending',
        'created': now,
        'updated': now,
        'body': args.body
    }

    # Write file
    content = format_requirement_file(req)
    atomic_write_file(filepath, content)

    # Count total
    total = len(list(req_dir.glob("REQ-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filename,
        'total_requirements': total,
        'requirement': {
            'number': number,
            'title': args.title,
            'status': 'pending'
        }
    })
    return 0


def cmd_update(args) -> int:
    """Handle 'update' subcommand."""
    req_dir = get_requirements_dir(args.plan_id)

    # Find existing file
    filepath = find_requirement_file(req_dir, args.number)
    if not filepath:
        output_error(f"Requirement REQ-{args.number} not found")
        return 1

    # Read current content
    content = filepath.read_text(encoding='utf-8')
    req = parse_requirement_file(content)

    # Update fields
    renamed = False
    old_title = req['title']

    if args.title:
        req['title'] = args.title
    if args.body:
        req['body'] = args.body
    if args.status:
        if args.status not in ('pending', 'done'):
            output_error(f"Invalid status: {args.status}. Must be 'pending' or 'done'")
            return 1
        req['status'] = args.status

    req['updated'] = now_iso()

    # Check if rename needed
    new_filename = filepath.name
    if args.title and args.title != old_title:
        new_slug = slugify(args.title)
        new_filename = f"REQ-{args.number:03d}-{new_slug}.toon"
        renamed = True

    # Write file
    new_content = format_requirement_file(req)
    new_filepath = req_dir / new_filename

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
        'requirement': {
            'number': req['number'],
            'title': req['title'],
            'status': req['status']
        }
    })
    return 0


def cmd_remove(args) -> int:
    """Handle 'remove' subcommand."""
    req_dir = get_requirements_dir(args.plan_id)

    # Find existing file
    filepath = find_requirement_file(req_dir, args.number)
    if not filepath:
        output_error(f"Requirement REQ-{args.number} not found")
        return 1

    # Read for output
    content = filepath.read_text(encoding='utf-8')
    req = parse_requirement_file(content)
    filename = filepath.name

    # Delete file
    filepath.unlink()

    # Count remaining
    total = len(list(req_dir.glob("REQ-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'total_requirements': total,
        'removed': {
            'number': req['number'],
            'title': req['title'],
            'file': filename
        }
    })
    return 0


def cmd_list(args) -> int:
    """Handle 'list' subcommand."""
    req_dir = get_requirements_dir(args.plan_id)
    all_reqs = get_all_requirements(req_dir)

    # Filter by status
    if args.status and args.status != 'all':
        all_reqs = [(p, r) for p, r in all_reqs if r.get('status') == args.status]

    # Compute counts from all (not filtered)
    all_for_counts = get_all_requirements(req_dir)
    pending = sum(1 for _, r in all_for_counts if r.get('status') == 'pending')
    done = sum(1 for _, r in all_for_counts if r.get('status') == 'done')

    # Build table data
    table = []
    for path, req in all_reqs:
        table.append({
            'number': req['number'],
            'title': req['title'],
            'status': req['status'],
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
        'requirements_table': table
    })
    return 0


def cmd_find_all(args) -> int:
    """Handle 'findAll' subcommand."""
    req_dir = get_requirements_dir(args.plan_id)
    all_reqs = get_all_requirements(req_dir)

    # Compute counts
    pending = sum(1 for _, r in all_reqs if r.get('status') == 'pending')
    done = sum(1 for _, r in all_reqs if r.get('status') == 'done')

    # Build full data
    full = []
    for _, req in all_reqs:
        full.append({
            'number': req['number'],
            'title': req['title'],
            'status': req['status'],
            'created': req.get('created', ''),
            'updated': req.get('updated', ''),
            'body': req.get('body', '')
        })

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'counts': {
            'total': len(all_reqs),
            'pending': pending,
            'done': done
        },
        'requirements_full': full
    })
    return 0


def cmd_get(args) -> int:
    """Handle 'get' subcommand."""
    req_dir = get_requirements_dir(args.plan_id)

    # Find file
    filepath = find_requirement_file(req_dir, args.number)
    if not filepath:
        output_error(f"Requirement REQ-{args.number} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    req = parse_requirement_file(content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filepath.name,
        'requirement': {
            'number': req['number'],
            'title': req['title'],
            'status': req['status'],
            'created': req.get('created', ''),
            'updated': req.get('updated', ''),
            'body': req.get('body', '')
        }
    })
    return 0


def get_specifications_dir(plan_id: str) -> Path:
    """Get the specifications directory for a plan."""
    return base_path('plans', plan_id, 'specifications')


def get_all_specifications(spec_dir: Path) -> list:
    """Get all specifications sorted by number."""
    if not spec_dir.exists():
        return []

    specs = []
    for f in sorted(spec_dir.glob("SPEC-*.toon")):
        content = f.read_text(encoding='utf-8')
        # Simple parsing for requirements field
        spec = {}
        for line in content.split('\n'):
            if line.startswith('requirements:'):
                spec['requirements'] = line.split(':', 1)[1].strip()
                break
        specs.append(spec)

    return specs


def cmd_validate(args) -> int:
    """Handle 'validate' subcommand - validate requirements coverage."""
    req_dir = get_requirements_dir(args.plan_id)
    spec_dir = get_specifications_dir(args.plan_id)

    # Get all requirements
    all_reqs = get_all_requirements(req_dir)
    total_reqs = len(all_reqs)

    if total_reqs == 0:
        output_toon({
            'status': 'success',
            'plan_id': args.plan_id,
            'total_requirements': 0,
            'covered': 0,
            'uncovered': 0,
            'coverage_percent': 100
        })
        return 0

    # Get all specifications and extract covered requirements
    all_specs = get_all_specifications(spec_dir)
    covered_reqs = set()

    for spec in all_specs:
        req_str = spec.get('requirements', '')
        for req in req_str.split(','):
            req = req.strip()
            if req.startswith('REQ-'):
                covered_reqs.add(req)

    # Find uncovered requirements
    uncovered_list = []
    for _, req in all_reqs:
        req_ref = f"REQ-{req['number']}"
        if req_ref not in covered_reqs:
            uncovered_list.append({
                'ref': req_ref,
                'title': req['title']
            })

    covered_count = total_reqs - len(uncovered_list)
    coverage_percent = int((covered_count / total_reqs) * 100) if total_reqs > 0 else 100

    # Build output
    lines = [
        "status: success",
        f"plan_id: {args.plan_id}",
        f"total_requirements: {total_reqs}",
        f"covered: {covered_count}",
        f"uncovered: {len(uncovered_list)}",
        f"coverage_percent: {coverage_percent}"
    ]

    if uncovered_list:
        lines.append("")
        lines.append("uncovered_requirements:")
        for req in uncovered_list:
            lines.append(f"  - {req['ref']}: {req['title']}")

    print('\n'.join(lines))
    return 0


def cmd_check(args) -> int:
    """Handle 'check' subcommand."""
    req_dir = get_requirements_dir(args.plan_id)

    # Validate status
    if args.status not in ('pending', 'done'):
        output_error(f"Invalid status: {args.status}. Must be 'pending' or 'done'")
        return 1

    # Find file
    filepath = find_requirement_file(req_dir, args.number)
    if not filepath:
        output_error(f"Requirement REQ-{args.number} not found")
        return 1

    # Read and update
    content = filepath.read_text(encoding='utf-8')
    req = parse_requirement_file(content)
    req['status'] = args.status
    req['updated'] = now_iso()

    # Write back
    new_content = format_requirement_file(req)
    atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filepath.name,
        'requirement': {
            'number': req['number'],
            'title': req['title'],
            'status': req['status']
        }
    })
    return 0


# ============================================================================
# CLI setup
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description='Manage numbered requirements within a plan',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # add
    p_add = subparsers.add_parser('add', help='Add a new requirement')
    p_add.add_argument('--plan-id', required=True, help='Plan identifier')
    p_add.add_argument('--title', required=True, help='Requirement title')
    p_add.add_argument('--body', required=True, help='Requirement body/description')

    # update
    p_update = subparsers.add_parser('update', help='Update an existing requirement')
    p_update.add_argument('--plan-id', required=True, help='Plan identifier')
    p_update.add_argument('--number', required=True, type=int, help='Requirement number')
    p_update.add_argument('--title', help='New title')
    p_update.add_argument('--body', help='New body')
    p_update.add_argument('--status', help='New status (pending/done)')

    # remove
    p_remove = subparsers.add_parser('remove', help='Remove a requirement')
    p_remove.add_argument('--plan-id', required=True, help='Plan identifier')
    p_remove.add_argument('--number', required=True, type=int, help='Requirement number')

    # list
    p_list = subparsers.add_parser('list', help='List all requirements')
    p_list.add_argument('--plan-id', required=True, help='Plan identifier')
    p_list.add_argument('--status', choices=['pending', 'done', 'all'],
                        default='all', help='Filter by status')

    # findAll
    p_find_all = subparsers.add_parser('findAll', help='Get all requirements with full content')
    p_find_all.add_argument('--plan-id', required=True, help='Plan identifier')

    # get
    p_get = subparsers.add_parser('get', help='Get a single requirement')
    p_get.add_argument('--plan-id', required=True, help='Plan identifier')
    p_get.add_argument('--number', required=True, type=int, help='Requirement number')

    # check
    p_check = subparsers.add_parser('check', help='Mark requirement done/pending')
    p_check.add_argument('--plan-id', required=True, help='Plan identifier')
    p_check.add_argument('--number', required=True, type=int, help='Requirement number')
    p_check.add_argument('--status', required=True, choices=['pending', 'done'],
                         help='New status')

    # validate
    p_validate = subparsers.add_parser('validate', help='Validate requirements coverage')
    p_validate.add_argument('--plan-id', required=True, help='Plan identifier')

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
        elif args.command == 'validate':
            return cmd_validate(args)
        else:
            output_error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        output_error(str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
