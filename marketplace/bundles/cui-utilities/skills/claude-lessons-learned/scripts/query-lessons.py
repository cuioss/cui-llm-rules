#!/usr/bin/env python3
"""
Query lessons learned from Markdown files.

This script parses key=value metadata from lesson MD files and filters
by component, category, and applied status.

Format: Simple key=value pairs separated by blank line from content.
Nested objects use dot notation (e.g., component.type=command).

Usage:
  query-lessons.py --all
  query-lessons.py --component maven-build-and-fix
  query-lessons.py --applied false
  query-lessons.py --category bug
  query-lessons.py --bundle cui-maven
  query-lessons.py --component maven-build-and-fix --applied false

Exit Codes:
  0 - Success
  1 - Error (invalid arguments, directory not found, etc.)

Output:
  JSON array of matching lessons with metadata and content
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


def parse_metadata(metadata_text: str) -> Dict[str, Any]:
    """
    Parse simple key=value metadata (no external dependencies).

    Handles:
    - Simple key=value pairs
    - Nested objects using dot notation (component.type=command)
    - Booleans (true/false)
    - Strings and dates

    Args:
        metadata_text: Metadata text to parse

    Returns:
        Dictionary of parsed metadata
    """
    result: Dict[str, Any] = {}

    for line in metadata_text.strip().split('\n'):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Parse key=value
        if '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Handle nested objects (component.type=command)
        if '.' in key:
            parts = key.split('.')
            current = result

            # Navigate/create nested structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the value
            current[parts[-1]] = parse_value(value)
        else:
            # Simple key=value
            result[key] = parse_value(value)

    return result


def parse_value(value: str) -> Any:
    """Parse a value string to its appropriate type."""
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        return value


def extract_metadata(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """
    Extract key=value metadata and content from Markdown file.

    Args:
        file_path: Path to Markdown file

    Returns:
        Tuple of (metadata dict, content string)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find first blank line (separates metadata from content)
    parts = content.split('\n\n', 1)

    if len(parts) == 1:
        # No blank line found, treat as content only
        return {}, content

    metadata_text, markdown_content = parts
    metadata = parse_metadata(metadata_text)

    return metadata, markdown_content.strip()


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Query lessons learned from Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query all lessons
  %(prog)s --all

  # Query by component name
  %(prog)s --component maven-build-and-fix

  # Query unapplied lessons
  %(prog)s --applied false

  # Query by category
  %(prog)s --category bug

  # Combine filters
  %(prog)s --component maven-build-and-fix --applied false --category bug
"""
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Return all lessons"
    )
    parser.add_argument(
        "--component",
        type=str,
        help="Filter by component name"
    )
    parser.add_argument(
        "--bundle",
        type=str,
        help="Filter by bundle name"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["command", "agent", "skill"],
        help="Filter by component type"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=["bug", "improvement", "pattern", "anti-pattern"],
        help="Filter by lesson category"
    )
    parser.add_argument(
        "--applied",
        type=str,
        choices=["true", "false"],
        help="Filter by applied status (true or false)"
    )
    parser.add_argument(
        "--lessons-dir",
        type=Path,
        default=Path(".claude/lessons-learned"),
        help="Directory containing lesson files (default: .claude/lessons-learned)"
    )

    return parser.parse_args()


def read_lesson(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Read a lesson MD file and extract metadata + content.

    Args:
        file_path: Path to the lesson MD file

    Returns:
        Dictionary with filename, metadata, and content, or None if invalid
    """
    try:
        metadata, content = extract_metadata(file_path)
        return {
            "filename": file_path.name,
            "metadata": metadata,
            "content": content
        }
    except Exception as e:
        print(f"Warning: Failed to parse {file_path}: {e}", file=sys.stderr)
        return None


def matches_filters(lesson: Dict[str, Any], args: argparse.Namespace) -> bool:
    """
    Check if a lesson matches all filter criteria.

    Args:
        lesson: Lesson dictionary with metadata
        args: Parsed command line arguments

    Returns:
        True if lesson matches all filters, False otherwise
    """
    metadata = lesson.get("metadata", {})
    component = metadata.get("component", {})

    # Component name filter
    if args.component and component.get("name") != args.component:
        return False

    # Bundle filter
    if args.bundle and component.get("bundle") != args.bundle:
        return False

    # Component type filter
    if args.type and component.get("type") != args.type:
        return False

    # Category filter
    if args.category and metadata.get("category") != args.category:
        return False

    # Applied status filter
    if args.applied:
        applied_value = metadata.get("applied", False)
        expected = args.applied == "true"
        if applied_value != expected:
            return False

    return True


def query_lessons(args: argparse.Namespace) -> List[Dict[str, Any]]:
    """
    Query lesson files based on filter criteria.

    Args:
        args: Parsed command line arguments

    Returns:
        List of matching lessons
    """
    lessons_dir = args.lessons_dir

    # Check if directory exists
    if not lessons_dir.exists():
        print(f"Error: Lessons directory not found: {lessons_dir}", file=sys.stderr)
        return []

    if not lessons_dir.is_dir():
        print(f"Error: Not a directory: {lessons_dir}", file=sys.stderr)
        return []

    # Find all MD files
    lesson_files = sorted(lessons_dir.glob("*.md"))

    if not lesson_files:
        # Empty directory is valid, just return empty array
        return []

    # Read and filter lessons
    results = []
    for file_path in lesson_files:
        lesson = read_lesson(file_path)
        if lesson is None:
            continue

        if matches_filters(lesson, args):
            results.append(lesson)

    return results


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    # Query lessons
    lessons = query_lessons(args)

    # Output JSON
    print(json.dumps(lessons, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
