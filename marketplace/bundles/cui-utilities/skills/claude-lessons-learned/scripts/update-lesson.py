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
    update_markdown_metadata
)


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


def main():
    parser = argparse.ArgumentParser(
        description='Update metadata in existing lesson files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mark lesson as applied
  %(prog)s --file .claude/lessons-learned/2025-11-28-001.md --set applied=true

  # Update multiple fields
  %(prog)s --file .claude/lessons-learned/2025-11-28-001.md \\
           --set applied=true --set category=pattern

  # Update component info
  %(prog)s --file lesson.md --set component.name=new-name
"""
    )

    parser.add_argument('--file', required=True,
                        help='Path to lesson file to update')
    parser.add_argument('--set', action='append', required=True, dest='updates',
                        metavar='KEY=VALUE',
                        help='Metadata field to update (can be specified multiple times)')

    args = parser.parse_args()

    try:
        file_path = Path(args.file)

        # Verify file exists
        if not file_path.exists():
            output_error('update-lesson', f"File not found: {file_path}")
            return 1

        # Parse all updates
        updates = {}
        for kv in args.updates:
            key, value = parse_key_value(kv)
            updates[key] = value

        # Read existing content
        content = file_path.read_text(encoding='utf-8')

        # Update metadata
        updated_content = update_markdown_metadata(content, updates)

        # Write atomically
        atomic_write_file(file_path, updated_content)

        output_success(
            'update-lesson',
            file=str(file_path),
            updated_fields=list(updates.keys())
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
