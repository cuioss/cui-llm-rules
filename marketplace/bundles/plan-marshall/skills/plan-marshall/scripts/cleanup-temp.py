#!/usr/bin/env python3
"""
Clean temporary files and directories.

Cleans the .plan/temp/ directory used for transient files during operations.

Usage:
    python3 cleanup-temp.py clean [--plan-dir PATH] [--dry-run]
    python3 cleanup-temp.py status [--plan-dir PATH]

Subcommands:
    clean     Remove all files from temp directory
    status    Show temp directory status without modifying

Options:
    --plan-dir PATH    Base plan directory (default: .plan)
    --dry-run          Show what would be deleted without deleting

Output (TOON format):
    status	success
    files_deleted	5
    bytes_freed	1024
"""

import argparse
import shutil
import sys
from pathlib import Path


def get_temp_stats(temp_dir: Path) -> tuple[int, int]:
    """
    Get statistics for temp directory.

    Args:
        temp_dir: Path to temp directory

    Returns:
        Tuple of (file_count, total_bytes)
    """
    if not temp_dir.exists():
        return 0, 0

    file_count = 0
    total_bytes = 0

    for item in temp_dir.rglob("*"):
        if item.is_file():
            file_count += 1
            try:
                total_bytes += item.stat().st_size
            except OSError:
                pass

    return file_count, total_bytes


def clean_temp(temp_dir: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Clean the temp directory.

    Args:
        temp_dir: Path to temp directory
        dry_run: If True, don't actually delete

    Returns:
        Tuple of (files_deleted, bytes_freed)
    """
    if not temp_dir.exists():
        return 0, 0

    file_count, total_bytes = get_temp_stats(temp_dir)

    if dry_run:
        return file_count, total_bytes

    # Remove all contents but keep the directory
    for item in temp_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    return file_count, total_bytes


def cmd_clean(args) -> int:
    """Clean temp directory."""
    plan_dir = Path(args.plan_dir)
    temp_dir = plan_dir / "temp"

    files_deleted, bytes_freed = clean_temp(temp_dir, dry_run=args.dry_run)

    status = "dry_run" if args.dry_run else "success"
    print(f"status\t{status}")
    print(f"files_deleted\t{files_deleted}")
    print(f"bytes_freed\t{bytes_freed}")

    return 0


def cmd_status(args) -> int:
    """Show temp directory status."""
    plan_dir = Path(args.plan_dir)
    temp_dir = plan_dir / "temp"

    exists = temp_dir.exists()
    file_count, total_bytes = get_temp_stats(temp_dir)

    print(f"exists\t{str(exists).lower()}")
    print(f"file_count\t{file_count}")
    print(f"total_bytes\t{total_bytes}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clean temporary files and directories"
    )
    parser.add_argument(
        "--plan-dir",
        type=str,
        default=".plan",
        help="Base plan directory (default: .plan)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # clean subcommand
    clean_parser = subparsers.add_parser("clean", help="Clean temp directory")
    clean_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting"
    )
    clean_parser.set_defaults(func=cmd_clean)

    # status subcommand
    status_parser = subparsers.add_parser("status", help="Show temp status")
    status_parser.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
