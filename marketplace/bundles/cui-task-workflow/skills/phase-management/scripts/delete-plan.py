#!/usr/bin/env python3
"""
Delete a plan directory safely.

Usage:
    python3 delete-plan.py <plan_directory>
    python3 delete-plan.py <plan_directory> --dry-run
    python3 delete-plan.py --help

Output: JSON with deletion result.

Safety checks:
    - Validates plan directory exists
    - Validates plan.md exists (confirms it's a plan)
    - Only deletes within .cui/plans/ hierarchy
    - Supports dry-run mode
"""

import argparse
import json
import os
import shutil
import sys
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

    # Safety: ensure path contains .cui/plans/
    plan_str = str(plan_dir.resolve())
    if '.cui/plans/' not in plan_str and '.claude\\plans\\' not in plan_str:
        errors.append(f"Directory is not within .cui/plans/ hierarchy: {plan_dir}")
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


def delete_plan(plan_directory: str, dry_run: bool = False) -> dict:
    """Delete a plan directory safely.

    Args:
        plan_directory: Path to the plan directory
        dry_run: If True, only simulate deletion

    Returns:
        Dictionary with deletion result
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

    if dry_run:
        return {
            'success': True,
            'dry_run': True,
            'plan_name': plan_name,
            'plan_directory': plan_directory,
            'would_delete': contents,
            'message': f"Would delete plan '{plan_name}' ({contents['files']} files, {contents['total_size_human']})"
        }

    # Perform deletion
    try:
        shutil.rmtree(plan_dir)
        return {
            'success': True,
            'dry_run': False,
            'plan_name': plan_name,
            'plan_directory': plan_directory,
            'deleted': contents,
            'message': f"Deleted plan '{plan_name}' ({contents['files']} files, {contents['total_size_human']})"
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
                'message': f"OS error during deletion: {e}",
                'plan_directory': plan_directory
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description='Delete a plan directory safely.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure (success):
{
  "success": true,
  "plan_name": "my-plan",
  "plan_directory": ".cui/plans/my-plan/",
  "deleted": {
    "files": 5,
    "directories": 2,
    "total_size_bytes": 4096,
    "total_size_human": "4.0 KB"
  },
  "message": "Deleted plan 'my-plan' (5 files, 4.0 KB)"
}

Output JSON structure (dry-run):
{
  "success": true,
  "dry_run": true,
  "plan_name": "my-plan",
  "would_delete": { ... },
  "message": "Would delete plan 'my-plan' (5 files, 4.0 KB)"
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
        help='Path to the plan directory to delete'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate deletion without actually removing files'
    )

    args = parser.parse_args()

    result = delete_plan(args.plan_directory, args.dry_run)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
