#!/usr/bin/env python3
"""
Manage numbered specifications within a plan.

Single CLI with subcommands for CRUD operations on specification files.
Uses TOON format for both storage and output.
Each specification must reference at least one requirement.

Subcommands:
  add              - Add a new specification
  update           - Update an existing specification
  remove           - Remove a specification
  list             - List all specifications (summary)
  findAll          - Get all specifications with full content
  get              - Get a single specification by number
  check            - Mark specification done/pending
  findByRequirement - Find specifications by requirement reference

Output: TOON format for all operations.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

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


def validate_requirements(requirements_str: str) -> List[str]:
    """Validate and parse requirements string.

    Args:
        requirements_str: Comma-separated REQ references (e.g., "REQ-1,REQ-3")

    Returns:
        List of validated REQ references

    Raises:
        ValueError: If format is invalid or empty
    """
    if not requirements_str or not requirements_str.strip():
        raise ValueError("At least one requirement reference is required")

    # Split and clean
    reqs = [r.strip() for r in requirements_str.split(',')]
    reqs = [r for r in reqs if r]  # Remove empty strings

    if not reqs:
        raise ValueError("At least one requirement reference is required")

    # Validate format
    pattern = re.compile(r'^REQ-\d+$')
    for req in reqs:
        if not pattern.match(req):
            raise ValueError(f"Invalid requirement format: {req}. Expected REQ-N (e.g., REQ-1)")

    return reqs


def format_requirements(reqs: List[str]) -> str:
    """Format requirements list as string for storage.

    Args:
        reqs: List of REQ references

    Returns:
        Comma-separated string
    """
    return ', '.join(reqs)


def parse_requirements(requirements_str: str) -> List[str]:
    """Parse requirements string from file.

    Args:
        requirements_str: Stored requirements string

    Returns:
        List of REQ references
    """
    if not requirements_str:
        return []
    return [r.strip() for r in requirements_str.split(',') if r.strip()]


def get_specifications_dir(plan_id: str) -> Path:
    """Get the specifications directory for a plan.

    Args:
        plan_id: The plan identifier

    Returns:
        Path to specifications directory
    """
    return base_path('plans', plan_id, 'specifications')


def parse_specification_file(content: str) -> dict:
    """Parse a specification TOON file into a dictionary.

    Args:
        content: File content

    Returns:
        Dictionary with specification fields
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


def format_specification_file(spec: dict) -> str:
    """Format a specification dictionary as TOON file content.

    Args:
        spec: Specification dictionary

    Returns:
        TOON formatted string
    """
    lines = [
        f"number: {spec['number']}",
        f"title: {spec['title']}",
        f"status: {spec['status']}",
        f"created: {spec['created']}",
        f"updated: {spec['updated']}",
        f"requirements: {spec['requirements']}",
        "",
        "body: |",
    ]

    # Add body with 2-space indent
    for body_line in spec['body'].split('\n'):
        lines.append(f"  {body_line}")

    return '\n'.join(lines)


def find_specification_file(spec_dir: Path, number: int) -> Optional[Path]:
    """Find specification file by number.

    Args:
        spec_dir: Specifications directory
        number: Specification number

    Returns:
        Path to file or None if not found
    """
    pattern = f"SPEC-{number:03d}-*.toon"
    matches = list(spec_dir.glob(pattern))
    return matches[0] if matches else None


def get_next_number(spec_dir: Path) -> int:
    """Get next available specification number.

    Args:
        spec_dir: Specifications directory

    Returns:
        Next available number
    """
    if not spec_dir.exists():
        return 1

    max_num = 0
    for f in spec_dir.glob("SPEC-*.toon"):
        try:
            # Extract number from SPEC-NNN-slug.toon
            num = int(f.name[5:8])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass

    return max_num + 1


def get_all_specifications(spec_dir: Path) -> list:
    """Get all specifications sorted by number.

    Args:
        spec_dir: Specifications directory

    Returns:
        List of (path, specification_dict) tuples
    """
    if not spec_dir.exists():
        return []

    specs = []
    for f in sorted(spec_dir.glob("SPEC-*.toon")):
        content = f.read_text(encoding='utf-8')
        spec = parse_specification_file(content)
        specs.append((f, spec))

    return sorted(specs, key=lambda x: x[1].get('number', 0))


def output_toon(data: dict) -> None:
    """Print TOON formatted output."""
    lines = []

    # Top-level simple fields
    for key in ['status', 'plan_id', 'file', 'renamed', 'total_specifications', 'requirement']:
        if key in data:
            lines.append(f"{key}: {data[key]}")

    # Counts block
    if 'counts' in data:
        lines.append("")
        lines.append("counts:")
        for k, v in data['counts'].items():
            lines.append(f"  {k}: {v}")

    # Single specification block
    if 'specification' in data:
        lines.append("")
        lines.append("specification:")
        spec = data['specification']
        for key in ['number', 'title', 'requirements', 'status', 'created', 'updated']:
            if key in spec:
                lines.append(f"  {key}: {spec[key]}")
        if 'body' in spec:
            lines.append(f"  body: {spec['body']}")

    # Removed block
    if 'removed' in data:
        lines.append("")
        lines.append("removed:")
        rem = data['removed']
        for key in ['number', 'title', 'file']:
            if key in rem:
                lines.append(f"  {key}: {rem[key]}")

    # Specifications list (tabular)
    if 'specifications_table' in data:
        specs = data['specifications_table']
        lines.append("")
        lines.append(f"specifications[{len(specs)}]{{number,title,requirements,status,file}}:")
        for s in specs:
            # Quote requirements if they contain commas
            reqs = s['requirements']
            if ',' in reqs:
                reqs = f'"{reqs}"'
            lines.append(f"{s['number']},{s['title']},{reqs},{s['status']},{s['file']}")

    # Specifications list (tabular, simple - for findByRequirement)
    if 'specifications_table_simple' in data:
        specs = data['specifications_table_simple']
        lines.append("")
        lines.append(f"specifications[{len(specs)}]{{number,title,status,file}}:")
        for s in specs:
            lines.append(f"{s['number']},{s['title']},{s['status']},{s['file']}")

    # Specifications list (full)
    if 'specifications_full' in data:
        specs = data['specifications_full']
        lines.append("")
        lines.append("specifications:")
        for s in specs:
            lines.append(f"  - number: {s['number']}")
            lines.append(f"    title: {s['title']}")
            lines.append(f"    requirements: {s['requirements']}")
            lines.append(f"    status: {s['status']}")
            lines.append(f"    created: {s['created']}")
            lines.append(f"    updated: {s['updated']}")
            # Body on single line for full output
            body_oneline = s.get('body', '').replace('\n', ' ').strip()
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
    # Validate requirements
    try:
        reqs = validate_requirements(args.requirements)
    except ValueError as e:
        output_error(str(e))
        return 1

    spec_dir = get_specifications_dir(args.plan_id)

    # Get next number
    number = get_next_number(spec_dir)

    # Generate slug and filename
    slug = slugify(args.title)
    filename = f"SPEC-{number:03d}-{slug}.toon"
    filepath = spec_dir / filename

    # Create specification
    now = now_iso()
    spec = {
        'number': number,
        'title': args.title,
        'status': 'pending',
        'created': now,
        'updated': now,
        'requirements': format_requirements(reqs),
        'body': args.body
    }

    # Write file
    content = format_specification_file(spec)
    atomic_write_file(filepath, content)

    # Count total
    total = len(list(spec_dir.glob("SPEC-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filename,
        'total_specifications': total,
        'specification': {
            'number': number,
            'title': args.title,
            'requirements': format_requirements(reqs),
            'status': 'pending'
        }
    })
    return 0


def cmd_update(args) -> int:
    """Handle 'update' subcommand."""
    spec_dir = get_specifications_dir(args.plan_id)

    # Find existing file
    filepath = find_specification_file(spec_dir, args.number)
    if not filepath:
        output_error(f"Specification SPEC-{args.number} not found")
        return 1

    # Read current content
    content = filepath.read_text(encoding='utf-8')
    spec = parse_specification_file(content)

    # Update fields
    renamed = False
    old_title = spec['title']

    if args.title:
        spec['title'] = args.title
    if args.body:
        spec['body'] = args.body
    if args.requirements:
        try:
            reqs = validate_requirements(args.requirements)
            spec['requirements'] = format_requirements(reqs)
        except ValueError as e:
            output_error(str(e))
            return 1
    if args.status:
        if args.status not in ('pending', 'done'):
            output_error(f"Invalid status: {args.status}. Must be 'pending' or 'done'")
            return 1
        spec['status'] = args.status

    spec['updated'] = now_iso()

    # Check if rename needed
    new_filename = filepath.name
    if args.title and args.title != old_title:
        new_slug = slugify(args.title)
        new_filename = f"SPEC-{args.number:03d}-{new_slug}.toon"
        renamed = True

    # Write file
    new_content = format_specification_file(spec)
    new_filepath = spec_dir / new_filename

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
        'specification': {
            'number': spec['number'],
            'title': spec['title'],
            'requirements': spec['requirements'],
            'status': spec['status']
        }
    })
    return 0


def cmd_remove(args) -> int:
    """Handle 'remove' subcommand."""
    spec_dir = get_specifications_dir(args.plan_id)

    # Find existing file
    filepath = find_specification_file(spec_dir, args.number)
    if not filepath:
        output_error(f"Specification SPEC-{args.number} not found")
        return 1

    # Read for output
    content = filepath.read_text(encoding='utf-8')
    spec = parse_specification_file(content)
    filename = filepath.name

    # Delete file
    filepath.unlink()

    # Count remaining
    total = len(list(spec_dir.glob("SPEC-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'total_specifications': total,
        'removed': {
            'number': spec['number'],
            'title': spec['title'],
            'file': filename
        }
    })
    return 0


def cmd_list(args) -> int:
    """Handle 'list' subcommand."""
    spec_dir = get_specifications_dir(args.plan_id)
    all_specs = get_all_specifications(spec_dir)

    # Filter by requirement if specified
    if args.requirement:
        all_specs = [
            (p, s) for p, s in all_specs
            if args.requirement in parse_requirements(s.get('requirements', ''))
        ]

    # Get filtered list for status filtering
    filtered_specs = all_specs
    if args.status and args.status != 'all':
        filtered_specs = [(p, s) for p, s in all_specs if s.get('status') == args.status]

    # Compute counts from all (not status-filtered, but requirement-filtered)
    pending = sum(1 for _, s in all_specs if s.get('status') == 'pending')
    done = sum(1 for _, s in all_specs if s.get('status') == 'done')

    # Build table data
    table = []
    for path, spec in filtered_specs:
        table.append({
            'number': spec['number'],
            'title': spec['title'],
            'requirements': spec.get('requirements', ''),
            'status': spec['status'],
            'file': path.name
        })

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'counts': {
            'total': len(all_specs),
            'pending': pending,
            'done': done
        },
        'specifications_table': table
    })
    return 0


def cmd_find_all(args) -> int:
    """Handle 'findAll' subcommand."""
    spec_dir = get_specifications_dir(args.plan_id)
    all_specs = get_all_specifications(spec_dir)

    # Compute counts
    pending = sum(1 for _, s in all_specs if s.get('status') == 'pending')
    done = sum(1 for _, s in all_specs if s.get('status') == 'done')

    # Build full data
    full = []
    for _, spec in all_specs:
        full.append({
            'number': spec['number'],
            'title': spec['title'],
            'requirements': spec.get('requirements', ''),
            'status': spec['status'],
            'created': spec.get('created', ''),
            'updated': spec.get('updated', ''),
            'body': spec.get('body', '')
        })

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'counts': {
            'total': len(all_specs),
            'pending': pending,
            'done': done
        },
        'specifications_full': full
    })
    return 0


def cmd_get(args) -> int:
    """Handle 'get' subcommand."""
    spec_dir = get_specifications_dir(args.plan_id)

    # Find file
    filepath = find_specification_file(spec_dir, args.number)
    if not filepath:
        output_error(f"Specification SPEC-{args.number} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    spec = parse_specification_file(content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filepath.name,
        'specification': {
            'number': spec['number'],
            'title': spec['title'],
            'requirements': spec.get('requirements', ''),
            'status': spec['status'],
            'created': spec.get('created', ''),
            'updated': spec.get('updated', ''),
            'body': spec.get('body', '')
        }
    })
    return 0


def cmd_check(args) -> int:
    """Handle 'check' subcommand."""
    spec_dir = get_specifications_dir(args.plan_id)

    # Validate status
    if args.status not in ('pending', 'done'):
        output_error(f"Invalid status: {args.status}. Must be 'pending' or 'done'")
        return 1

    # Find file
    filepath = find_specification_file(spec_dir, args.number)
    if not filepath:
        output_error(f"Specification SPEC-{args.number} not found")
        return 1

    # Read and update
    content = filepath.read_text(encoding='utf-8')
    spec = parse_specification_file(content)
    spec['status'] = args.status
    spec['updated'] = now_iso()

    # Write back
    new_content = format_specification_file(spec)
    atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filepath.name,
        'specification': {
            'number': spec['number'],
            'title': spec['title'],
            'requirements': spec.get('requirements', ''),
            'status': spec['status']
        }
    })
    return 0


def cmd_find_by_requirement(args) -> int:
    """Handle 'findByRequirement' subcommand."""
    spec_dir = get_specifications_dir(args.plan_id)
    all_specs = get_all_specifications(spec_dir)

    # Filter by requirement
    matching = [
        (p, s) for p, s in all_specs
        if args.requirement in parse_requirements(s.get('requirements', ''))
    ]

    # Compute counts
    pending = sum(1 for _, s in matching if s.get('status') == 'pending')
    done = sum(1 for _, s in matching if s.get('status') == 'done')

    # Build table data (simple format without requirements column)
    table = []
    for path, spec in matching:
        table.append({
            'number': spec['number'],
            'title': spec['title'],
            'status': spec['status'],
            'file': path.name
        })

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'requirement': args.requirement,
        'counts': {
            'total': len(matching),
            'pending': pending,
            'done': done
        },
        'specifications_table_simple': table
    })
    return 0


# ============================================================================
# CLI setup
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description='Manage numbered specifications within a plan',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # add
    p_add = subparsers.add_parser('add', help='Add a new specification')
    p_add.add_argument('--plan-id', required=True, help='Plan identifier')
    p_add.add_argument('--title', required=True, help='Specification title')
    p_add.add_argument('--requirements', required=True,
                       help='Comma-separated requirement references (e.g., REQ-1,REQ-3)')
    p_add.add_argument('--body', required=True, help='Specification body/description')

    # update
    p_update = subparsers.add_parser('update', help='Update an existing specification')
    p_update.add_argument('--plan-id', required=True, help='Plan identifier')
    p_update.add_argument('--number', required=True, type=int, help='Specification number')
    p_update.add_argument('--title', help='New title')
    p_update.add_argument('--requirements', help='New requirements (comma-separated)')
    p_update.add_argument('--body', help='New body')
    p_update.add_argument('--status', help='New status (pending/done)')

    # remove
    p_remove = subparsers.add_parser('remove', help='Remove a specification')
    p_remove.add_argument('--plan-id', required=True, help='Plan identifier')
    p_remove.add_argument('--number', required=True, type=int, help='Specification number')

    # list
    p_list = subparsers.add_parser('list', help='List all specifications')
    p_list.add_argument('--plan-id', required=True, help='Plan identifier')
    p_list.add_argument('--status', choices=['pending', 'done', 'all'],
                        default='all', help='Filter by status')
    p_list.add_argument('--requirement', help='Filter by requirement reference (e.g., REQ-1)')

    # findAll
    p_find_all = subparsers.add_parser('findAll', help='Get all specifications with full content')
    p_find_all.add_argument('--plan-id', required=True, help='Plan identifier')

    # get
    p_get = subparsers.add_parser('get', help='Get a single specification')
    p_get.add_argument('--plan-id', required=True, help='Plan identifier')
    p_get.add_argument('--number', required=True, type=int, help='Specification number')

    # check
    p_check = subparsers.add_parser('check', help='Mark specification done/pending')
    p_check.add_argument('--plan-id', required=True, help='Plan identifier')
    p_check.add_argument('--number', required=True, type=int, help='Specification number')
    p_check.add_argument('--status', required=True, choices=['pending', 'done'],
                         help='New status')

    # findByRequirement
    p_find_by_req = subparsers.add_parser('findByRequirement',
                                          help='Find specifications by requirement reference')
    p_find_by_req.add_argument('--plan-id', required=True, help='Plan identifier')
    p_find_by_req.add_argument('--requirement', required=True,
                               help='Requirement reference (e.g., REQ-1)')

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
        elif args.command == 'findByRequirement':
            return cmd_find_by_requirement(args)
        else:
            output_error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        output_error(str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
