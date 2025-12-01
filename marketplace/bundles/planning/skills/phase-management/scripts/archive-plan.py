#!/usr/bin/env python3
"""
Archive a plan directory safely.

Usage:
    python3 archive-plan.py <plan_directory>
    python3 archive-plan.py <plan_directory> --dry-run
    python3 archive-plan.py --help

Output: JSON with archive result.

Archive behavior:
    - Moves plan to .plan/archived-plans/{yyyy-mm-dd}-{plan-name}/
    - Creates archive directory if needed
    - Validates plan directory exists and contains plan.md
    - Supports dry-run mode
"""

import argparse
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path


def validate_plan_directory(plan_dir: Path) -> dict:
    """Validate that the directory is a legitimate plan directory.

    Args:
        plan_dir: Path to the plan directory

    Returns:
        Dictionary with validation result
    """
    errors = []

    # Check directory exists
    if not plan_dir.exists():
        errors.append(f"Directory does not exist: {plan_dir}")
        return {'valid': False, 'errors': errors}

    if not plan_dir.is_dir():
        errors.append(f"Path is not a directory: {plan_dir}")
        return {'valid': False, 'errors': errors}

    # Check plan.md exists (confirms it's a plan directory)
    plan_file = plan_dir / 'plan.md'
    if not plan_file.exists():
        errors.append(f"No plan.md found in directory: {plan_dir}")
        return {'valid': False, 'errors': errors}

    # Safety: ensure path contains .plan/plans/
    plan_str = str(plan_dir.resolve())
    if '.plan/plans/' not in plan_str and '.plan\\plans\\' not in plan_str:
        errors.append(f"Directory is not within .plan/plans/ hierarchy: {plan_dir}")
        return {'valid': False, 'errors': errors}

    return {'valid': True, 'errors': []}


def get_plan_contents(plan_dir: Path) -> dict:
    """Get summary of plan directory contents.

    Args:
        plan_dir: Path to the plan directory

    Returns:
        Dictionary with file counts and total size
    """
    file_count = 0
    dir_count = 0
    total_size = 0

    for item in plan_dir.rglob('*'):
        if item.is_file():
            file_count += 1
            total_size += item.stat().st_size
        elif item.is_dir():
            dir_count += 1

    return {
        'files': file_count,
        'directories': dir_count,
        'total_size_bytes': total_size,
        'total_size_human': format_size(total_size)
    }


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_archive_directory(plan_dir: Path) -> Path:
    """Determine the archive directory path.

    Args:
        plan_dir: Path to the plan directory

    Returns:
        Path to the archived-plans directory
    """
    # Navigate up from plan directory to find .plan root
    # plan_dir is like /path/to/.plan/plans/my-plan
    # We want /path/to/.plan/archived-plans/
    plans_parent = plan_dir.parent  # .plan/plans/
    plan_root = plans_parent.parent  # .plan/
    return plan_root / 'archived-plans'


def archive_plan(plan_directory: str, dry_run: bool = False) -> dict:
    """Archive a plan directory safely.

    Args:
        plan_directory: Path to the plan directory
        dry_run: If True, only simulate archiving

    Returns:
        Dictionary with archive result
    """
    plan_dir = Path(plan_directory)

    # Validate
    validation = validate_plan_directory(plan_dir)
    if not validation['valid']:
        return {
            'success': False,
            'error': {
                'type': 'validation_failed',
                'message': 'Plan directory validation failed',
                'details': validation['errors']
            },
            'plan_directory': plan_directory
        }

    # Get contents summary
    contents = get_plan_contents(plan_dir)
    plan_name = plan_dir.name

    # Generate archive path with date prefix
    today = date.today().isoformat()  # yyyy-mm-dd
    archive_name = f"{today}-{plan_name}"
    archive_dir = get_archive_directory(plan_dir)
    archive_path = archive_dir / archive_name

    if dry_run:
        return {
            'success': True,
            'dry_run': True,
            'plan_name': plan_name,
            'plan_directory': plan_directory,
            'archive_path': str(archive_path),
            'would_archive': contents,
            'message': f"Would archive plan '{plan_name}' to '{archive_path}' ({contents['files']} files, {contents['total_size_human']})"
        }

    # Create archive directory if needed
    try:
        archive_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        return {
            'success': False,
            'error': {
                'type': 'permission_error',
                'message': f"Cannot create archive directory: {e}",
                'archive_directory': str(archive_dir)
            }
        }

    # Check if archive path already exists
    if archive_path.exists():
        # Add a suffix to make it unique
        counter = 1
        while archive_path.exists():
            archive_path = archive_dir / f"{today}-{plan_name}-{counter}"
            counter += 1

    # Perform archive (move)
    try:
        shutil.move(str(plan_dir), str(archive_path))
        return {
            'success': True,
            'dry_run': False,
            'plan_name': plan_name,
            'plan_directory': plan_directory,
            'archive_path': str(archive_path),
            'archived': contents,
            'message': f"Archived plan '{plan_name}' to '{archive_path}' ({contents['files']} files, {contents['total_size_human']})"
        }
    except PermissionError as e:
        return {
            'success': False,
            'error': {
                'type': 'permission_error',
                'message': f"Permission denied: {e}",
                'plan_directory': plan_directory
            }
        }
    except OSError as e:
        return {
            'success': False,
            'error': {
                'type': 'os_error',
                'message': f"OS error during archive: {e}",
                'plan_directory': plan_directory
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description='Archive a plan directory safely.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure (success):
{
  "success": true,
  "plan_name": "my-plan",
  "plan_directory": ".plan/plans/my-plan/",
  "archive_path": ".plan/archived-plans/2025-12-01-my-plan/",
  "archived": {
    "files": 5,
    "directories": 2,
    "total_size_bytes": 4096,
    "total_size_human": "4.0 KB"
  },
  "message": "Archived plan 'my-plan' to '...' (5 files, 4.0 KB)"
}

Output JSON structure (dry-run):
{
  "success": true,
  "dry_run": true,
  "plan_name": "my-plan",
  "archive_path": ".plan/archived-plans/2025-12-01-my-plan/",
  "would_archive": { ... },
  "message": "Would archive plan 'my-plan' to '...' (5 files, 4.0 KB)"
}

Output JSON structure (error):
{
  "success": false,
  "error": {
    "type": "validation_failed",
    "message": "Plan directory validation failed",
    "details": ["No plan.md found in directory"]
  }
}
"""
    )
    parser.add_argument(
        'plan_directory',
        help='Path to the plan directory to archive'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate archiving without actually moving files'
    )

    args = parser.parse_args()

    result = archive_plan(args.plan_directory, args.dry_run)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
