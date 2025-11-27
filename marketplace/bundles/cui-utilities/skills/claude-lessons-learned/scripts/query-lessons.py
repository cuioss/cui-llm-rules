#!/usr/bin/env python3
"""
Query lessons learned from Markdown files.

This script parses YAML frontmatter from lesson MD files and filters
by component, category, and applied status.

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
  JSON array of matching lessons with frontmatter and content
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import frontmatter
except ImportError:
    print("Error: python-frontmatter library not installed", file=sys.stderr)
    print("Install with: pip install python-frontmatter", file=sys.stderr)
    sys.exit(1)


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


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert Python objects to JSON-serializable format.

    Args:
        obj: Object to convert

    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj


def read_lesson(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Read a lesson MD file and extract frontmatter + content.

    Args:
        file_path: Path to the lesson MD file

    Returns:
        Dictionary with filename, frontmatter, and content, or None if invalid
    """
    try:
        post = frontmatter.load(file_path)
        return {
            "filename": file_path.name,
            "frontmatter": convert_to_json_serializable(post.metadata),
            "content": post.content
        }
    except Exception as e:
        print(f"Warning: Failed to parse {file_path}: {e}", file=sys.stderr)
        return None


def matches_filters(lesson: Dict[str, Any], args: argparse.Namespace) -> bool:
    """
    Check if a lesson matches all filter criteria.

    Args:
        lesson: Lesson dictionary with frontmatter
        args: Parsed command line arguments

    Returns:
        True if lesson matches all filters, False otherwise
    """
    fm = lesson.get("frontmatter", {})
    component = fm.get("component", {})

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
    if args.category and fm.get("category") != args.category:
        return False

    # Applied status filter
    if args.applied:
        applied_value = fm.get("applied", False)
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
