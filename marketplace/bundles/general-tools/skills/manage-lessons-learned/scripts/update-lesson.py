#!/usr/bin/env python3
"""
Update metadata in existing lesson files.

Updates specific key=value pairs in lesson file metadata while preserving
all content unchanged. Uses atomic file operations.

Output: JSON with updated file path.
"""

import argparse
import json
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import (
    atomic_write_file,
    output_success,
    output_error,
    update_markdown_metadata,
    base_path
)


def resolve_lesson_path(lesson_id: str) -> Path:
    """Resolve lesson ID to file path using base_path.

    Uses ID-based access pattern: takes lesson ID and resolves file path
    internally via base_path. This ensures orchestrators don't construct
    paths to resources in other domains.

    Args:
        lesson_id: Lesson identifier (e.g., "2025-12-01-004")

    Returns:
        Path to the lesson file
    """
    filename = f"{lesson_id}.md"
    return base_path("lessons-learned", filename)


def parse_key_value(kv_string: str) -> tuple[str, str]:
    """Parse a KEY=VALUE string.

    Args:
        kv_string: String in KEY=VALUE format

    Returns:
        Tuple of (key, value)

    Raises:
        ValueError: If format is invalid
    """
    if '=' not in kv_string:
        raise ValueError(f"Invalid format '{kv_string}'. Expected KEY=VALUE")

    key, value = kv_string.split('=', 1)
    key = key.strip()
    value = value.strip()

    if not key:
        raise ValueError(f"Empty key in '{kv_string}'")

    return key, value


def update_section(content: str, section_name: str, new_content: str) -> str:
    """Update content of a specific ## section in markdown.

    Finds a section starting with '## {section_name}' and replaces everything
    between that header and the next ## header (or end of file).

    Args:
        content: Full markdown file content
        section_name: Name of section to update (e.g., 'Detail', 'Example')
        new_content: New content for the section (without the ## header)

    Returns:
        Updated content with section replaced

    Raises:
        ValueError: If section not found
    """
    import re

    # Pattern to find the section header
    section_pattern = rf'^## {re.escape(section_name)}\s*$'

    lines = content.split('\n')
    section_start = None
    section_end = None

    # Find section start
    for i, line in enumerate(lines):
        if re.match(section_pattern, line):
            section_start = i
            break

    if section_start is None:
        raise ValueError(f"Section '## {section_name}' not found in file")

    # Find section end (next ## header or end of file)
    for i in range(section_start + 1, len(lines)):
        if re.match(r'^## ', lines[i]):
            section_end = i
            break

    if section_end is None:
        section_end = len(lines)

    # Build new content: preserve header, replace body
    new_lines = lines[:section_start + 1]  # Include the ## header
    new_lines.append('')  # Blank line after header
    new_lines.append(new_content.strip())
    new_lines.append('')  # Blank line before next section

    # Add remaining content
    if section_end < len(lines):
        new_lines.extend(lines[section_end:])

    return '\n'.join(new_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Update metadata or content sections in existing lesson files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update lesson by ID
  %(prog)s --lesson-id 2025-11-28-001 --set applied=true

  # Update multiple fields
  %(prog)s --lesson-id 2025-11-28-001 --set applied=true --set category=pattern

  # Update component info
  %(prog)s --lesson-id 2025-11-28-001 --set component.name=new-name

  # Update content sections
  %(prog)s --lesson-id 2025-11-28-001 --set-detail "New detailed description"
  %(prog)s --lesson-id 2025-11-28-001 --set-example "New example code"
  %(prog)s --lesson-id 2025-11-28-001 --set-related "component-a, component-b"

  # Combine metadata and section updates
  %(prog)s --lesson-id 2025-11-28-001 --set applied=true --set-detail "Updated description"
"""
    )

    # Mutually exclusive group for file identification
    file_group = parser.add_mutually_exclusive_group(required=True)
    file_group.add_argument('--lesson-id',
                            help='Lesson identifier (e.g., 2025-11-28-001) - path resolved internally')
    file_group.add_argument('--file',
                            help=argparse.SUPPRESS)  # Internal use for testing only
    parser.add_argument('--set', action='append', dest='updates',
                        metavar='KEY=VALUE',
                        help='Metadata field to update (can be specified multiple times)')
    parser.add_argument('--set-detail',
                        help='Replace content of ## Detail section')
    parser.add_argument('--set-example',
                        help='Replace content of ## Example section')
    parser.add_argument('--set-related',
                        help='Replace content of ## Related section')

    args = parser.parse_args()

    # Require at least one update operation
    if not args.updates and not args.set_detail and not args.set_example and not args.set_related:
        parser.error('At least one of --set, --set-detail, --set-example, or --set-related is required')

    try:
        # Resolve file path from --lesson-id or --file
        if args.lesson_id:
            file_path = resolve_lesson_path(args.lesson_id)
        else:
            file_path = Path(args.file)

        # Verify file exists
        if not file_path.exists():
            if args.lesson_id:
                output_error('update-lesson', f"Lesson not found: {args.lesson_id} (expected at {file_path})")
            else:
                output_error('update-lesson', f"File not found: {file_path}")
            return 1

        # Read existing content
        content = file_path.read_text(encoding='utf-8')

        # Track what was updated
        updated_fields = []
        updated_sections = []

        # Parse and apply metadata updates if provided
        if args.updates:
            updates = {}
            for kv in args.updates:
                key, value = parse_key_value(kv)
                updates[key] = value
            content = update_markdown_metadata(content, updates)
            updated_fields = list(updates.keys())

        # Apply section updates
        if args.set_detail:
            content = update_section(content, 'Detail', args.set_detail)
            updated_sections.append('Detail')

        if args.set_example:
            content = update_section(content, 'Example', args.set_example)
            updated_sections.append('Example')

        if args.set_related:
            content = update_section(content, 'Related', args.set_related)
            updated_sections.append('Related')

        # Write atomically
        atomic_write_file(file_path, content)

        output_success(
            'update-lesson',
            file=str(file_path),
            updated_fields=updated_fields,
            updated_sections=updated_sections
        )
        return 0

    except ValueError as e:
        output_error('update-lesson', str(e))
        return 1
    except Exception as e:
        output_error('update-lesson', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
