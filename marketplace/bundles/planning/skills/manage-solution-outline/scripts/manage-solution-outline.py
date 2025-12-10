#!/usr/bin/env python3
"""
Manage solution outline documents.

Solution outlines are written using manage-files with --stdin to support ASCII
diagrams with box-drawing characters, then validated and queried via this script.

Write: echo "$content" | manage-files write --plan-id X --file solution_outline.md --stdin
Validate: manage-solution-outline validate --plan-id X
Read: manage-solution-outline read --plan-id X [--raw]
List: manage-solution-outline list-deliverables --plan-id X

Usage:
    python3 manage-solution-outline.py validate --plan-id my-plan
    python3 manage-solution-outline.py list-deliverables --plan-id my-plan
    python3 manage-solution-outline.py read --plan-id my-plan [--raw]
    python3 manage-solution-outline.py exists --plan-id my-plan
"""

import argparse
import re
import sys
from pathlib import Path

# Add parent paths for imports
script_dir = Path(__file__).parent
SKILL_DIR = script_dir.parent
BUNDLES_DIR = SKILL_DIR.parent.parent.parent

sys.path.insert(0, str(BUNDLES_DIR / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'))
sys.path.insert(0, str(BUNDLES_DIR / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'))

from toon_parser import serialize_toon
from file_ops import base_path

SOLUTION_FILE = 'solution_outline.md'


def validate_plan_id(plan_id: str) -> bool:
    """Validate plan_id is kebab-case with no special characters."""
    return bool(re.match(r'^[a-z][a-z0-9-]*$', plan_id))


def get_solution_path(plan_id: str) -> Path:
    """Get the solution outline file path."""
    return base_path('plans', plan_id, SOLUTION_FILE)


def parse_document_sections(content: str) -> dict[str, str]:
    """Parse markdown document into sections by heading."""
    sections = {}
    current_section = '_header'
    current_content = []

    for line in content.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            # Start new section
            current_section = line[3:].strip().lower().replace(' ', '_')
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def extract_deliverables(deliverables_section: str) -> list[dict]:
    """Extract numbered deliverables from Deliverables section.

    Parses `### N. Title` headings and returns structured deliverable info.
    """
    deliverables = []
    pattern = re.compile(r'^###\s+(\d+)\.\s+(.+)$', re.MULTILINE)

    for match in pattern.finditer(deliverables_section):
        number = int(match.group(1))
        title = match.group(2).strip()
        deliverables.append({
            'number': number,
            'title': title,
            'reference': f"{number}. {title}"
        })

    return sorted(deliverables, key=lambda d: d['number'])


def validate_solution_structure(content: str) -> tuple[list[str], dict]:
    """Validate solution outline document structure.

    Returns (issues, info) where issues is a list of validation errors
    and info contains validation metadata.
    """
    issues = []
    info = {
        'sections_found': [],
        'deliverable_count': 0,
        'deliverables': []
    }

    sections = parse_document_sections(content)

    # Required sections
    required_sections = ['summary', 'overview', 'deliverables']
    for section in required_sections:
        if section in sections:
            info['sections_found'].append(section)
        else:
            issues.append(f"Missing required section: {section.replace('_', ' ').title()}")

    # Optional sections
    optional_sections = ['approach', 'dependencies', 'risks_and_mitigations', 'risks']
    for section in optional_sections:
        if section in sections:
            info['sections_found'].append(section)

    # Validate deliverables section has numbered items
    if 'deliverables' in sections:
        deliverables = extract_deliverables(sections['deliverables'])
        info['deliverable_count'] = len(deliverables)
        info['deliverables'] = [d['reference'] for d in deliverables]

        if not deliverables:
            issues.append("No numbered deliverables found in Deliverables section (expected ### N. Title)")

    return issues, info


# =============================================================================
# Commands
# =============================================================================

def cmd_validate(args) -> int:
    """Validate solution outline structure."""
    if not validate_plan_id(args.plan_id):
        print(serialize_toon({
            'status': 'error',
            'error': 'invalid_plan_id',
            'plan_id': args.plan_id,
            'message': 'Plan ID must be kebab-case (lowercase, hyphens only)'
        }))
        return 1

    file_path = get_solution_path(args.plan_id)

    if not file_path.exists():
        print(serialize_toon({
            'status': 'error',
            'error': 'document_not_found',
            'plan_id': args.plan_id,
            'file': SOLUTION_FILE,
            'suggestions': [
                'Write solution_outline.md using manage-files write --stdin',
                'Check plan_id spelling'
            ]
        }))
        return 1

    content = file_path.read_text(encoding='utf-8')
    issues, info = validate_solution_structure(content)

    if issues:
        print(serialize_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'validation_failed',
            'issues': issues
        }))
        return 1

    print(serialize_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': SOLUTION_FILE,
        'validation': {
            'sections_found': ','.join(info['sections_found']),
            'deliverable_count': info['deliverable_count'],
            'deliverables': info['deliverables']
        }
    }))
    return 0


def cmd_list_deliverables(args) -> int:
    """List deliverables from solution outline."""
    if not validate_plan_id(args.plan_id):
        print(serialize_toon({
            'status': 'error',
            'error': 'invalid_plan_id',
            'plan_id': args.plan_id
        }))
        return 1

    file_path = get_solution_path(args.plan_id)

    if not file_path.exists():
        print(serialize_toon({
            'status': 'error',
            'error': 'document_not_found',
            'plan_id': args.plan_id,
            'file': SOLUTION_FILE
        }))
        return 1

    content = file_path.read_text(encoding='utf-8')
    sections = parse_document_sections(content)

    if 'deliverables' not in sections:
        print(serialize_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'section_not_found',
            'message': 'Deliverables section not found'
        }))
        return 1

    deliverables = extract_deliverables(sections['deliverables'])

    print(serialize_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'deliverable_count': len(deliverables),
        'deliverables': deliverables
    }))
    return 0


def cmd_read(args) -> int:
    """Read solution outline."""
    if not validate_plan_id(args.plan_id):
        print(serialize_toon({
            'status': 'error',
            'error': 'invalid_plan_id',
            'plan_id': args.plan_id
        }))
        return 1

    file_path = get_solution_path(args.plan_id)

    if not file_path.exists():
        print(serialize_toon({
            'status': 'error',
            'error': 'document_not_found',
            'plan_id': args.plan_id,
            'file': SOLUTION_FILE,
            'suggestions': [
                'Write solution_outline.md using manage-files write --stdin',
                'Check plan_id spelling'
            ]
        }))
        return 1

    content = file_path.read_text(encoding='utf-8')

    if getattr(args, 'raw', False):
        print(content)
    else:
        sections = parse_document_sections(content)
        print(serialize_toon({
            'status': 'success',
            'plan_id': args.plan_id,
            'file': SOLUTION_FILE,
            'content': sections
        }))

    return 0


def cmd_exists(args) -> int:
    """Check if solution outline exists."""
    if not validate_plan_id(args.plan_id):
        print(serialize_toon({
            'status': 'error',
            'error': 'invalid_plan_id',
            'plan_id': args.plan_id
        }))
        return 1

    file_path = get_solution_path(args.plan_id)
    exists = file_path.exists()

    print(serialize_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': SOLUTION_FILE,
        'exists': exists
    }))

    return 0 if exists else 1


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Manage solution outline documents'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command')

    # validate
    validate_parser = subparsers.add_parser('validate', help='Validate solution structure')
    validate_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    validate_parser.set_defaults(func=cmd_validate)

    # list-deliverables
    list_parser = subparsers.add_parser('list-deliverables', help='Extract deliverables')
    list_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    list_parser.set_defaults(func=cmd_list_deliverables)

    # read
    read_parser = subparsers.add_parser('read', help='Read solution outline')
    read_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    read_parser.add_argument('--raw', action='store_true', help='Output raw content')
    read_parser.set_defaults(func=cmd_read)

    # exists
    exists_parser = subparsers.add_parser('exists', help='Check if solution exists')
    exists_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    exists_parser.set_defaults(func=cmd_exists)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
