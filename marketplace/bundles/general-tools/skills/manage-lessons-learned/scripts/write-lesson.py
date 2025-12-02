#!/usr/bin/env python3
"""
Create new lesson MD files for the lessons-learned system.

Creates a new lesson file with proper metadata and content structure.
Uses atomic file operations to write to .plan/ directory.

Supports --from-error flag for automatic lesson creation from script failures.

Output: JSON with created file path and lesson ID.
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, base_path, output_success, output_error


def parse_error_context(error_json: str) -> dict:
    """Parse error context JSON from --from-error flag.

    Args:
        error_json: JSON string with error context

    Returns:
        Dictionary with parsed error context

    Expected JSON format:
    {
        "script": "script-name.py",
        "exit_code": 1,
        "error_output": "Error message...",
        "plan_context": "plan-name (optional)"
    }
    """
    try:
        ctx = json.loads(error_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in --from-error: {e}")

    # Validate required fields
    if 'script' not in ctx:
        raise ValueError("--from-error JSON must contain 'script' field")

    return {
        'script': ctx.get('script', 'unknown-script'),
        'exit_code': ctx.get('exit_code', 1),
        'error_output': ctx.get('error_output', 'No error output captured'),
        'plan_context': ctx.get('plan_context', '')
    }


def derive_component_from_script(script_name: str) -> tuple:
    """Derive component type, name, and bundle from script path.

    Args:
        script_name: Script name or path

    Returns:
        Tuple of (component_type, component_name, component_bundle)
    """
    # Extract just the filename if it's a path
    script_path = Path(script_name)
    name = script_path.stem  # Remove .py extension

    # Try to extract bundle from path (e.g., marketplace/bundles/BUNDLE/skills/SKILL/scripts/name.py)
    parts = script_path.parts
    bundle = 'unknown-bundle'
    skill_name = name

    if 'bundles' in parts:
        try:
            bundles_idx = parts.index('bundles')
            if bundles_idx + 1 < len(parts):
                bundle = parts[bundles_idx + 1]
            if 'skills' in parts:
                skills_idx = parts.index('skills')
                if skills_idx + 1 < len(parts):
                    skill_name = parts[skills_idx + 1]
        except (ValueError, IndexError):
            pass

    return ('skill', skill_name, bundle)


def generate_error_lesson_content(error_ctx: dict) -> tuple:
    """Generate lesson title and detail from error context.

    Args:
        error_ctx: Parsed error context dictionary

    Returns:
        Tuple of (title, detail)
    """
    script = error_ctx['script']
    exit_code = error_ctx['exit_code']
    error_output = error_ctx['error_output']
    plan_context = error_ctx['plan_context']

    # Generate title
    script_name = Path(script).stem
    title = f"Script failure: {script_name} (exit {exit_code})"

    # Generate detail
    detail_parts = [
        f"Script `{script}` failed with exit code {exit_code}.",
        "",
        "**Error Output**:",
        "```",
        error_output[:2000] if len(error_output) > 2000 else error_output,  # Truncate if too long
        "```"
    ]

    if plan_context:
        detail_parts.extend([
            "",
            f"**Plan Context**: {plan_context}"
        ])

    detail_parts.extend([
        "",
        "**Analysis**: [Add root cause analysis here]",
        "",
        "**Resolution**: [Add resolution steps here]"
    ])

    return (title, '\n'.join(detail_parts))


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


def resolve_from_error_mode(args) -> dict:
    """Resolve lesson fields from error context.

    Args:
        args: Parsed command line arguments with from_error set

    Returns:
        Dictionary with resolved lesson fields
    """
    error_ctx = parse_error_context(args.from_error)
    comp_type, comp_name, comp_bundle = derive_component_from_script(error_ctx['script'])
    title, detail = generate_error_lesson_content(error_ctx)

    return {
        'component_type': args.component_type or comp_type,
        'component_name': args.component_name or comp_name,
        'component_bundle': args.component_bundle or comp_bundle,
        'category': args.category or 'bug',
        'title': args.title or title,
        'detail': args.detail or detail
    }


def resolve_manual_mode(args, parser) -> dict:
    """Resolve lesson fields from manual arguments.

    Args:
        args: Parsed command line arguments
        parser: Argument parser for error reporting

    Returns:
        Dictionary with resolved lesson fields
    """
    required_fields = [
        ('component_type', '--component-type'),
        ('component_name', '--component-name'),
        ('component_bundle', '--component-bundle'),
        ('category', '--category'),
        ('title', '--title'),
        ('detail', '--detail')
    ]

    missing = [flag for attr, flag in required_fields if not getattr(args, attr)]
    if missing:
        parser.error(f"The following arguments are required: {', '.join(missing)}")

    return {
        'component_type': args.component_type,
        'component_name': args.component_name,
        'component_bundle': args.component_bundle,
        'category': args.category,
        'title': args.title,
        'detail': args.detail
    }


def build_argument_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
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

  # Create from script error (auto-populates fields)
  %(prog)s --from-error '{"script": "update-progress.py", "exit_code": 1, \\
           "error_output": "FileNotFoundError: plan.md not found", \\
           "plan_context": "my-plan"}'

  # Custom lessons directory
  %(prog)s --component-type skill --component-name cui-java-core \\
           --component-bundle cui-java-expert --category improvement \\
           --title "Add null safety section" \\
           --detail "The skill should include null safety guidelines..." \\
           --lessons-dir /path/to/lessons
"""
    )

    parser.add_argument('--from-error', default=None,
                        help='JSON with error context: {"script": "...", "exit_code": N, '
                             '"error_output": "...", "plan_context": "..."}')
    parser.add_argument('--component-type', default=None,
                        choices=['command', 'agent', 'skill'],
                        help='Type of component (auto-derived if --from-error)')
    parser.add_argument('--component-name', default=None,
                        help='Name of the component (auto-derived if --from-error)')
    parser.add_argument('--component-bundle', default=None,
                        help='Bundle containing the component (auto-derived if --from-error)')
    parser.add_argument('--category', default=None,
                        choices=['bug', 'improvement', 'pattern', 'anti-pattern'],
                        help='Lesson category (defaults to "bug" if --from-error)')
    parser.add_argument('--title', default=None,
                        help='Brief summary title (auto-generated if --from-error)')
    parser.add_argument('--detail', default=None,
                        help='Full explanation of the lesson (auto-generated if --from-error)')
    parser.add_argument('--example', default='',
                        help='Optional code example')
    parser.add_argument('--related', default='',
                        help='Optional related components')
    parser.add_argument('--lessons-dir', default=None,
                        help='Directory for lesson files (default: .plan/lessons-learned)')

    return parser


def main():
    parser = build_argument_parser()
    args = parser.parse_args()

    try:
        # Resolve fields based on mode
        if args.from_error:
            fields = resolve_from_error_mode(args)
        else:
            fields = resolve_manual_mode(args, parser)

        # Determine lessons directory
        lessons_dir = Path(args.lessons_dir) if args.lessons_dir else base_path('lessons-learned')

        # Generate unique ID
        lesson_id = generate_lesson_id(lessons_dir)

        # Create content
        content = create_lesson_content(
            lesson_id=lesson_id,
            component_type=fields['component_type'],
            component_name=fields['component_name'],
            component_bundle=fields['component_bundle'],
            category=fields['category'],
            title=fields['title'],
            detail=fields['detail'],
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
            component=f"{fields['component_bundle']}:{fields['component_name']}"
        )
        return 0

    except Exception as e:
        output_error('write-lesson', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
