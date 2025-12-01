#!/usr/bin/env python3
"""
Copy a lesson file to a plan directory and remove the original.

Performs a transactional move: copies to destination, verifies content,
then removes original only after successful verification.

Uses ID-based access pattern: takes lesson ID and resolves file path
internally via base_path. This ensures orchestrators don't construct
paths to resources in other domains.

Output: JSON with operation status.
"""

import argparse
import json
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]  # marketplace/bundles/planning/skills/plan-files -> marketplace
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, output_success, output_error, base_path


def copy_lesson_to_plan(lesson_file: Path, plan_dir: Path, dry_run: bool = False) -> dict:
    """Copy lesson file to plan directory and remove original.

    Args:
        lesson_file: Path to the lesson file
        plan_dir: Path to the plan directory
        dry_run: If True, only simulate the operation

    Returns:
        dict with operation result
    """
    # Validate lesson file exists
    if not lesson_file.exists():
        return {
            "success": False,
            "error": f"Lesson file not found: {lesson_file}"
        }

    if not lesson_file.is_file():
        return {
            "success": False,
            "error": f"Not a file: {lesson_file}"
        }

    # Validate plan directory exists
    if not plan_dir.exists():
        return {
            "success": False,
            "error": f"Plan directory not found: {plan_dir}"
        }

    if not plan_dir.is_dir():
        return {
            "success": False,
            "error": f"Not a directory: {plan_dir}"
        }

    # Verify it's a valid plan directory (has plan.md)
    plan_md = plan_dir / "plan.md"
    if not plan_md.exists():
        return {
            "success": False,
            "error": f"Not a valid plan directory (missing plan.md): {plan_dir}"
        }

    # Read lesson content
    try:
        lesson_content = lesson_file.read_text(encoding='utf-8')
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read lesson file: {e}"
        }

    # Destination file
    dest_file = plan_dir / "lesson-source.md"

    if dry_run:
        return {
            "success": True,
            "operation": "copy-lesson-to-plan",
            "dry_run": True,
            "would_copy": str(lesson_file),
            "would_create": str(dest_file),
            "would_remove": str(lesson_file),
            "content_size": len(lesson_content)
        }

    # Step 1: Write to destination (atomic)
    try:
        atomic_write_file(dest_file, lesson_content)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to write destination file: {e}"
        }

    # Step 2: Verify content was written correctly
    try:
        written_content = dest_file.read_text(encoding='utf-8')
        if written_content != lesson_content:
            # Content mismatch - abort without removing original
            return {
                "success": False,
                "error": "Content verification failed - original preserved",
                "destination_created": True,
                "original_preserved": True
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to verify destination file: {e}",
            "destination_created": True,
            "original_preserved": True
        }

    # Step 3: Remove original only after successful verification
    try:
        lesson_file.unlink()
    except Exception as e:
        return {
            "success": True,  # Copy succeeded, just cleanup failed
            "warning": f"Copy succeeded but failed to remove original: {e}",
            "operation": "copy-lesson-to-plan",
            "source": str(lesson_file),
            "destination": str(dest_file),
            "original_preserved": True
        }

    return {
        "success": True,
        "operation": "copy-lesson-to-plan",
        "source": str(lesson_file),
        "destination": str(dest_file),
        "original_removed": True,
        "content_size": len(lesson_content)
    }


def main():
    parser = argparse.ArgumentParser(
        description='Copy lesson file to plan directory (transactional move)'
    )
    parser.add_argument(
        '--lesson-file',
        required=True,
        help='Path to the lesson file to copy'
    )
    parser.add_argument(
        '--plan-dir',
        required=True,
        help='Path to the plan directory'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate operation without making changes'
    )

    args = parser.parse_args()

    lesson_file = Path(args.lesson_file).resolve()
    plan_dir = Path(args.plan_dir).resolve()

    result = copy_lesson_to_plan(lesson_file, plan_dir, args.dry_run)

    if result.get("success"):
        output_success(result)
    else:
        output_error(result.get("error", "Unknown error"), result)


if __name__ == '__main__':
    main()
