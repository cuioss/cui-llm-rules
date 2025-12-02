#!/usr/bin/env python3
"""
Create or update references.toon.

Creates or modifies references file with sections for issue, branch, ADRs,
interfaces, implementation files, external docs, and dependencies.
Uses atomic file operations to write to .plan/plans/ directory.

TOON format only - no markdown support.

Output: JSON with changes made.
"""

import argparse
import json
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
TOON_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))
sys.path.insert(0, str(TOON_DIR))

from file_ops import atomic_write_file, ensure_directory, output_success, output_error
from toon_parser import parse_toon


# Valid sections
VALID_SECTIONS = [
    'issue', 'issue_url', 'issue_title', 'branch', 'base_branch',
    'implementation_files', 'config_files', 'test_files',
    'adrs', 'interfaces', 'external_docs', 'dependencies', 'related_plans'
]

# Valid actions
VALID_ACTIONS = ['add', 'update', 'remove', 'set']


def get_default_references_content(branch: str = '') -> str:
    """Get default references.toon template content."""
    return f"""# Plan References

issue: (not set)
issue_url: (not set)
issue_title: (not set)
branch: {branch if branch else '(not set)'}
base_branch: main

implementation_files[0]:

config_files[0]:

test_files[0]:

adrs[0]{{id,path,status}}:

interfaces[0]{{name,path}}:

external_docs[0]{{name,url}}:

dependencies[0]:

related_plans[0]:
"""


def parse_toon_content(content: str) -> dict:
    """Parse TOON content into a structured dict.

    Uses shared toon_parser and transforms output to the expected format.
    """
    raw = parse_toon(content)

    result = {
        'scalars': {},
        'simple_lists': {},
        'structured_arrays': {}
    }

    # Known structured arrays with their field definitions
    structured_array_fields = {
        'adrs': ['id', 'path', 'status'],
        'interfaces': ['name', 'path'],
        'external_docs': ['name', 'url']
    }

    # Known simple lists
    simple_list_keys = {'implementation_files', 'config_files', 'test_files', 'dependencies', 'related_plans'}

    # Known scalars
    scalar_keys = {'issue', 'issue_url', 'issue_title', 'branch', 'base_branch'}

    for key, value in raw.items():
        key_lower = key.lower()

        if key_lower in scalar_keys:
            result['scalars'][key_lower] = str(value) if value is not None else '(not set)'
        elif key_lower in simple_list_keys:
            if isinstance(value, list):
                # Filter out placeholders and non-strings
                result['simple_lists'][key_lower] = [
                    item for item in value
                    if isinstance(item, str) and not item.startswith('(')
                ]
            else:
                result['simple_lists'][key_lower] = []
        elif key_lower in structured_array_fields:
            fields = structured_array_fields[key_lower]
            if isinstance(value, list):
                items = [item for item in value if isinstance(item, dict)]
                result['structured_arrays'][key_lower] = {'fields': fields, 'items': items}
            else:
                result['structured_arrays'][key_lower] = {'fields': fields, 'items': []}

    return result


def generate_toon_content(data: dict) -> str:
    """Generate TOON content from structured data."""
    lines = ['# Plan References', '']

    # Scalars
    scalars = data.get('scalars', {})
    for key in ['issue', 'issue_url', 'issue_title', 'branch', 'base_branch']:
        value = scalars.get(key, '(not set)')
        lines.append(f"{key}: {value}")

    lines.append('')

    # Simple lists
    simple_lists = data.get('simple_lists', {})
    for key in ['implementation_files', 'config_files', 'test_files']:
        items = simple_lists.get(key, [])
        lines.append(f"{key}[{len(items)}]:")
        for item in items:
            lines.append(f"- {item}")
        lines.append('')

    # Structured arrays
    structured_arrays = data.get('structured_arrays', {})

    # ADRs
    adrs = structured_arrays.get('adrs', {'fields': ['id', 'path', 'status'], 'items': []})
    fields_str = ','.join(adrs['fields'])
    lines.append(f"adrs[{len(adrs['items'])}]{{{fields_str}}}:")
    for item in adrs['items']:
        values = [item.get(f, '') for f in adrs['fields']]
        lines.append(','.join(values))
    lines.append('')

    # Interfaces
    interfaces = structured_arrays.get('interfaces', {'fields': ['name', 'path'], 'items': []})
    fields_str = ','.join(interfaces['fields'])
    lines.append(f"interfaces[{len(interfaces['items'])}]{{{fields_str}}}:")
    for item in interfaces['items']:
        values = [item.get(f, '') for f in interfaces['fields']]
        lines.append(','.join(values))
    lines.append('')

    # External docs
    external_docs = structured_arrays.get('external_docs', {'fields': ['name', 'url'], 'items': []})
    fields_str = ','.join(external_docs['fields'])
    lines.append(f"external_docs[{len(external_docs['items'])}]{{{fields_str}}}:")
    for item in external_docs['items']:
        values = [item.get(f, '') for f in external_docs['fields']]
        lines.append(','.join(values))
    lines.append('')

    # Dependencies and related_plans (simple lists)
    for key in ['dependencies', 'related_plans']:
        items = simple_lists.get(key, [])
        lines.append(f"{key}[{len(items)}]:")
        for item in items:
            lines.append(f"- {item}")
        lines.append('')

    return '\n'.join(lines)


def update_references(content: str, section: str, action: str, value: str) -> tuple[str, dict]:
    """Update references content based on action and section.

    Args:
        content: Current file content
        section: Section to update
        action: Action to perform (add, update, remove, set)
        value: Value for the action

    Returns:
        Tuple of (updated_content, changes_dict)
    """
    data = parse_toon_content(content)
    changes = {'section': section, 'action': action, 'value': value}

    # Handle scalar sections
    if section in ['issue', 'issue_url', 'issue_title', 'branch', 'base_branch']:
        if action in ['set', 'update']:
            # Check if value is JSON (for issue with full details)
            if value.startswith('{'):
                try:
                    parsed = json.loads(value)
                    if section == 'issue':
                        data['scalars']['issue'] = parsed.get('id', value)
                        if 'url' in parsed:
                            data['scalars']['issue_url'] = parsed['url']
                        if 'title' in parsed:
                            data['scalars']['issue_title'] = parsed['title']
                except json.JSONDecodeError:
                    data['scalars'][section] = value
            else:
                data['scalars'][section] = value

    # Handle simple list sections
    elif section in ['implementation_files', 'config_files', 'test_files', 'dependencies', 'related_plans']:
        if section not in data['simple_lists']:
            data['simple_lists'][section] = []
        items = data['simple_lists'][section]

        if action == 'add':
            if value not in items:
                items.append(value)
        elif action == 'remove':
            items[:] = [i for i in items if i != value]
        elif action == 'set':
            items[:] = [v.strip() for v in value.split(',') if v.strip()]

    # Handle structured array sections
    elif section == 'adrs':
        if 'adrs' not in data['structured_arrays']:
            data['structured_arrays']['adrs'] = {'fields': ['id', 'path', 'status'], 'items': []}
        arr = data['structured_arrays']['adrs']

        if action == 'add':
            # Parse value as "ID,path,status" or JSON
            if value.startswith('{'):
                try:
                    item = json.loads(value)
                except json.JSONDecodeError:
                    parts = value.split(',')
                    item = {'id': parts[0] if parts else '', 'path': parts[1] if len(parts) > 1 else '', 'status': parts[2] if len(parts) > 2 else 'proposed'}
            else:
                parts = value.split(',')
                item = {'id': parts[0].strip() if parts else '', 'path': parts[1].strip() if len(parts) > 1 else '', 'status': parts[2].strip() if len(parts) > 2 else 'proposed'}
            if not any(i['id'] == item['id'] for i in arr['items']):
                arr['items'].append(item)
        elif action == 'remove':
            arr['items'][:] = [i for i in arr['items'] if i.get('id') != value]

    elif section == 'interfaces':
        if 'interfaces' not in data['structured_arrays']:
            data['structured_arrays']['interfaces'] = {'fields': ['name', 'path'], 'items': []}
        arr = data['structured_arrays']['interfaces']

        if action == 'add':
            if value.startswith('{'):
                try:
                    item = json.loads(value)
                except json.JSONDecodeError:
                    parts = value.split(',')
                    item = {'name': parts[0] if parts else '', 'path': parts[1] if len(parts) > 1 else ''}
            else:
                parts = value.split(',')
                item = {'name': parts[0].strip() if parts else '', 'path': parts[1].strip() if len(parts) > 1 else ''}
            if not any(i['name'] == item['name'] for i in arr['items']):
                arr['items'].append(item)
        elif action == 'remove':
            arr['items'][:] = [i for i in arr['items'] if i.get('name') != value]

    elif section == 'external_docs':
        if 'external_docs' not in data['structured_arrays']:
            data['structured_arrays']['external_docs'] = {'fields': ['name', 'url'], 'items': []}
        arr = data['structured_arrays']['external_docs']

        if action == 'add':
            if value.startswith('{'):
                try:
                    item = json.loads(value)
                except json.JSONDecodeError:
                    parts = value.split(',')
                    item = {'name': parts[0] if parts else '', 'url': parts[1] if len(parts) > 1 else ''}
            else:
                parts = value.split(',')
                item = {'name': parts[0].strip() if parts else '', 'url': parts[1].strip() if len(parts) > 1 else ''}
            if not any(i['name'] == item['name'] for i in arr['items']):
                arr['items'].append(item)
        elif action == 'remove':
            arr['items'][:] = [i for i in arr['items'] if i.get('name') != value]

    new_content = generate_toon_content(data)
    return new_content, changes


def main():
    parser = argparse.ArgumentParser(
        description='Create or update references.toon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
TOON format only - outputs references.toon (not .md).

Examples:
  # Set issue (with full JSON)
  %(prog)s --plan-dir .plan/plans/my-task \\
           --action set \\
           --section issue \\
           --value '{"id":"#123","title":"My Issue","url":"https://github.com/..."}'

  # Set branch
  %(prog)s --plan-dir .plan/plans/my-task \\
           --action set \\
           --section branch \\
           --value "feature/my-feature"

  # Add implementation file
  %(prog)s --plan-dir .plan/plans/my-task \\
           --action add \\
           --section implementation_files \\
           --value "src/main/java/Foo.java"

  # Add ADR reference (CSV format: id,path,status)
  %(prog)s --plan-dir .plan/plans/my-task \\
           --action add \\
           --section adrs \\
           --value "ADR-001,../adr/ADR-001.md,proposed"

  # Add external doc
  %(prog)s --plan-dir .plan/plans/my-task \\
           --action add \\
           --section external_docs \\
           --value "JWT Guide,https://jwt.io/introduction"

  # Remove file
  %(prog)s --plan-dir .plan/plans/my-task \\
           --action remove \\
           --section implementation_files \\
           --value "src/main/java/OldFile.java"
"""
    )

    parser.add_argument('--plan-dir', required=True,
                        help='Directory for plan files')
    parser.add_argument('--action', required=True,
                        choices=VALID_ACTIONS,
                        help='Action: add, update, remove, set')
    parser.add_argument('--section', required=True,
                        choices=VALID_SECTIONS,
                        help='Section to modify')
    parser.add_argument('--value', required=True,
                        help='Value for the action')

    args = parser.parse_args()

    try:
        plan_dir = Path(args.plan_dir)
        file_path = plan_dir / "references.toon"

        # Ensure directory exists
        ensure_directory(plan_dir)

        # Read existing or create default
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            created = False
        else:
            content = get_default_references_content()
            created = True

        # Apply update
        content, changes = update_references(
            content,
            args.section,
            args.action,
            args.value
        )

        # Write file
        atomic_write_file(file_path, content)

        output_success(
            'write-references',
            file=str(file_path),
            created=created,
            changes=changes
        )
        return 0

    except Exception as e:
        output_error('write-references', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
