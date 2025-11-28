#!/usr/bin/env python3
"""
Create new lesson MD files for the lessons-learned system.

Creates a new lesson file with proper metadata and content structure.
Uses atomic file operations to avoid prompts when writing to .claude/ directory.

Output: JSON with created file path and lesson ID.
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, ensure_directory, output_success, output_error


def generate_lesson_id(lessons_dir: Path) -> str:
    """Generate unique lesson ID in YYYY-MM-DD-NNN format.

    Args:
        lessons_dir: Directory containing lesson files

    Returns:
        New unique lesson ID
    """
    today = date.today().isoformat()

    # Find highest sequence number for today
    max_seq = 0
    if lessons_dir.exists():
        for f in lessons_dir.glob(f"{today}-*.md"):
            try:
                seq = int(f.stem.split('-')[-1])
                max_seq = max(max_seq, seq)
            except (ValueError, IndexError):
                pass

    return f"{today}-{max_seq + 1:03d}"


def create_lesson_content(
    lesson_id: str,
    component_type: str,
    component_name: str,
    component_bundle: str,
    category: str,
    title: str,
    detail: str,
    example: str = "",
    related: str = ""
) -> str:
    """Create lesson markdown content with metadata.

    Args:
        lesson_id: Unique lesson identifier
        component_type: Type of component (command, agent, skill)
        component_name: Name of the component
        component_bundle: Bundle containing the component
        category: Lesson category (bug, improvement, pattern, anti-pattern)
        title: Brief summary title
        detail: Full explanation of the lesson
        example: Optional code example
        related: Optional related components

    Returns:
        Formatted markdown content
    """
    today = date.today().isoformat()

    # Build metadata block
    metadata_lines = [
        f"id={lesson_id}",
        f"component.type={component_type}",
        f"component.name={component_name}",
        f"component.bundle={component_bundle}",
        f"date={today}",
        f"category={category}",
        "applied=false"
    ]
    metadata = '\n'.join(metadata_lines)

    # Build content sections
    content_parts = [
        metadata,
        "",
        f"# {title}",
        "",
        "## Detail",
        "",
        detail
    ]

    if example:
        content_parts.extend([
            "",
            "## Example",
            "",
            example
        ])

    if related:
        content_parts.extend([
            "",
            "## Related",
            "",
            related
        ])

    return '\n'.join(content_parts)


def main():
    parser = argparse.ArgumentParser(
        description='Create new lesson MD file for lessons-learned system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a bug lesson
  %(prog)s --component-type command --component-name maven-build-and-fix \\
           --component-bundle builder-maven --category bug \\
           --title "Build fails on special characters" \\
           --detail "The build command fails when paths contain special characters..."

  # Create with example and related
  %(prog)s --component-type agent --component-name java-fix-agent \\
           --component-bundle cui-java-expert --category pattern \\
           --title "Effective error handling pattern" \\
           --detail "Always wrap tool calls in try-catch..." \\
           --example "try:\\n    result = tool()\\nexcept Exception as e:\\n    handle(e)" \\
           --related "Similar pattern in python-fix-agent"

  # Custom lessons directory
  %(prog)s --component-type skill --component-name cui-java-core \\
           --component-bundle cui-java-expert --category improvement \\
           --title "Add null safety section" \\
           --detail "The skill should include null safety guidelines..." \\
           --lessons-dir /path/to/lessons
"""
    )

    parser.add_argument('--component-type', required=True,
                        choices=['command', 'agent', 'skill'],
                        help='Type of component')
    parser.add_argument('--component-name', required=True,
                        help='Name of the component')
    parser.add_argument('--component-bundle', required=True,
                        help='Bundle containing the component')
    parser.add_argument('--category', required=True,
                        choices=['bug', 'improvement', 'pattern', 'anti-pattern'],
                        help='Lesson category')
    parser.add_argument('--title', required=True,
                        help='Brief summary title')
    parser.add_argument('--detail', required=True,
                        help='Full explanation of the lesson')
    parser.add_argument('--example', default='',
                        help='Optional code example')
    parser.add_argument('--related', default='',
                        help='Optional related components')
    parser.add_argument('--lessons-dir', default='.claude/lessons-learned',
                        help='Directory for lesson files (default: .claude/lessons-learned)')

    args = parser.parse_args()

    try:
        lessons_dir = Path(args.lessons_dir)

        # Ensure directory exists
        ensure_directory(lessons_dir)

        # Generate unique ID
        lesson_id = generate_lesson_id(lessons_dir)

        # Create content
        content = create_lesson_content(
            lesson_id=lesson_id,
            component_type=args.component_type,
            component_name=args.component_name,
            component_bundle=args.component_bundle,
            category=args.category,
            title=args.title,
            detail=args.detail,
            example=args.example,
            related=args.related
        )

        # Write file
        file_path = lessons_dir / f"{lesson_id}.md"
        atomic_write_file(file_path, content)

        output_success(
            'write-lesson',
            file=str(file_path),
            id=lesson_id,
            component=f"{args.component_bundle}:{args.component_name}"
        )
        return 0

    except Exception as e:
        output_error('write-lesson', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
