#!/usr/bin/env python3
"""
Create or update references.md.

Creates or modifies references file with sections for issue, branch, ADRs,
interfaces, implementation files, external docs, and dependencies.
Uses atomic file operations to avoid prompts when writing to .claude/ directory.

Output: JSON with changes made.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'cui-utilities' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, ensure_directory, output_success, output_error


# Valid sections
VALID_SECTIONS = [
    'issue', 'branch', 'adrs', 'interfaces',
    'implementation_files', 'external_docs', 'dependencies'
]

# Valid actions
VALID_ACTIONS = ['add', 'update', 'remove', 'set']


def get_default_references_content() -> str:
    """Get default references.md template content."""
    return """# References

## Issue

**GitHub Issue**: (not set)

**Branch**: `(not set)`
**Base Branch**: `main`

## Related Files

**Implementation Files**:
- (populated during implement phase)

**Configuration Files**:
- (populated during implement phase)

**Test Files**:
- (populated during implement phase)

## Architecture Decision Records (ADRs)

**Related ADRs** (managed via `adr-management` skill):
- (populated during refine phase)

**To create new ADR**: Use `adr-management` skill operations
**To read ADR**: Use `adr-management` skill with ADR identifier

## Interface Specifications

**Related Interfaces** (managed via `interface-management` skill):
- (populated during refine phase)

**To create new interface**: Use `interface-management` skill operations
**To read interface**: Use `interface-management` skill with interface identifier

## External Documentation

**Standards and Specifications**:
- (add relevant external docs)

**Libraries and Tools**:
- (add relevant library docs)

## Dependencies

**Maven Dependencies**:
- (populated during implement phase)

**Related Plans**:
- (add related plan references)
"""


def update_issue_section(content: str, action: str, value: str, key: str = None) -> str:
    """Update the issue section."""
    if action in ['set', 'update']:
        # Parse value as JSON if it looks like JSON
        if value.startswith('{'):
            try:
                data = json.loads(value)
                issue_id = data.get('id', '')
                title = data.get('title', '')
                url = data.get('url', '')
                issue_line = f"**GitHub Issue**: [{issue_id}: {title}]({url})"
            except json.JSONDecodeError:
                issue_line = f"**GitHub Issue**: {value}"
        else:
            issue_line = f"**GitHub Issue**: {value}"

        # Replace the issue line
        content = re.sub(
            r'\*\*GitHub Issue\*\*:.*',
            issue_line,
            content
        )
    return content


def update_branch_section(content: str, action: str, value: str, key: str = None) -> str:
    """Update the branch section."""
    if action in ['set', 'update']:
        content = re.sub(
            r'\*\*Branch\*\*:.*',
            f"**Branch**: `{value}`",
            content
        )
    return content


def update_list_section(content: str, section_pattern: str, action: str, value: str) -> str:
    """Update a list section (ADRs, interfaces, files, etc.)."""
    # Find the section
    pattern = rf'(\*\*{section_pattern}\*\*.*?:)\n((?:- .*\n)*)'

    def replace_section(match):
        header = match.group(1)
        items_str = match.group(2)

        # Parse existing items
        items = [line[2:].strip() for line in items_str.strip().split('\n') if line.startswith('- ')]

        # Remove placeholder items
        items = [i for i in items if not i.startswith('(')]

        if action == 'add':
            if value not in items:
                items.append(value)
        elif action == 'remove':
            items = [i for i in items if i != value]
        elif action == 'set':
            # Value can be comma-separated list
            items = [v.strip() for v in value.split(',') if v.strip()]

        # Rebuild section
        if items:
            items_str = '\n'.join(f"- {item}" for item in items) + '\n'
        else:
            items_str = "- (none)\n"

        return f"{header}\n{items_str}"

    return re.sub(pattern, replace_section, content, flags=re.MULTILINE)


def update_references(content: str, section: str, action: str, value: str, key: str = None) -> tuple[str, dict]:
    """Update references content based on action and section.

    Args:
        content: Current file content
        section: Section to update
        action: Action to perform (add, update, remove, set)
        value: Value for the action
        key: Optional key for update/remove in objects

    Returns:
        Tuple of (updated_content, changes_dict)
    """
    changes = {'section': section, 'action': action, 'value': value}

    if section == 'issue':
        content = update_issue_section(content, action, value, key)
    elif section == 'branch':
        content = update_branch_section(content, action, value, key)
    elif section == 'adrs':
        content = update_list_section(content, 'Related ADRs', action, value)
    elif section == 'interfaces':
        content = update_list_section(content, 'Related Interfaces', action, value)
    elif section == 'implementation_files':
        content = update_list_section(content, 'Implementation Files', action, value)
    elif section == 'external_docs':
        content = update_list_section(content, 'Standards and Specifications', action, value)
    elif section == 'dependencies':
        content = update_list_section(content, 'Maven Dependencies', action, value)

    return content, changes


def main():
    parser = argparse.ArgumentParser(
        description='Create or update references.md',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set issue
  %(prog)s --plan-dir .claude/plans/my-task \\
           --action set \\
           --section issue \\
           --value '{"id":"#123","title":"My Issue","url":"https://github.com/..."}'

  # Set branch
  %(prog)s --plan-dir .claude/plans/my-task \\
           --action set \\
           --section branch \\
           --value "feature/my-feature"

  # Add implementation file
  %(prog)s --plan-dir .claude/plans/my-task \\
           --action add \\
           --section implementation_files \\
           --value "src/main/java/Foo.java"

  # Add ADR reference
  %(prog)s --plan-dir .claude/plans/my-task \\
           --action add \\
           --section adrs \\
           --value "ADR-0015: Use Strategy Pattern"

  # Remove file
  %(prog)s --plan-dir .claude/plans/my-task \\
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
    parser.add_argument('--key', default=None,
                        help='Key for update/remove in objects')

    args = parser.parse_args()

    try:
        plan_dir = Path(args.plan_dir)
        file_path = plan_dir / "references.md"

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
            args.value,
            args.key
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
