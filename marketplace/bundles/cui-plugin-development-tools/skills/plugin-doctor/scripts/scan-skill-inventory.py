#!/usr/bin/env python3
"""
scan-skill-inventory.py

Scans a skill directory and returns structured inventory of all content files.

Usage:
    python3 scan-skill-inventory.py --skill-path <path> [--include-hidden]

Options:
    --skill-path <path>    Path to the skill directory (required)
    --include-hidden       Include hidden files (default: false)

Output: JSON with inventory including:
    - skill_name: Name of the skill (from directory name)
    - skill_path: Absolute path to skill directory
    - directories: Array of subdirectories with their files
    - root_files: Files in the root of the skill directory
    - statistics: Aggregate counts and metrics

Exit codes:
    0 - Success
    1 - Error (missing argument, directory not found)
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return sum(1 for _ in f)
    except (OSError, IOError):
        return 0


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    try:
        return file_path.stat().st_size
    except OSError:
        return 0


def should_skip_directory(dir_name: str, include_hidden: bool) -> bool:
    """Check if directory should be skipped."""
    # Skip common non-content directories
    skip_dirs = {'__pycache__', 'node_modules', '.git'}
    if dir_name in skip_dirs:
        return True
    # Skip hidden directories unless requested
    if not include_hidden and dir_name.startswith('.'):
        return True
    return False


def should_skip_file(file_name: str, include_hidden: bool) -> bool:
    """Check if file should be skipped."""
    if not include_hidden and file_name.startswith('.'):
        return True
    return False


def scan_directory(skill_path: Path, include_hidden: bool) -> dict:
    """Scan skill directory and return inventory."""
    skill_name = skill_path.name
    abs_skill_path = str(skill_path.resolve())

    directories = []
    root_files = []
    total_dirs = 0
    total_files = 0
    total_lines = 0
    extensions = defaultdict(int)

    # Scan subdirectories
    try:
        for entry in sorted(skill_path.iterdir()):
            if entry.is_dir():
                dir_name = entry.name

                if should_skip_directory(dir_name, include_hidden):
                    continue

                total_dirs += 1
                dir_files = []

                # Scan files in subdirectory (non-recursive for first level)
                for file_entry in sorted(entry.iterdir()):
                    if not file_entry.is_file():
                        continue

                    file_name = file_entry.name
                    if should_skip_file(file_name, include_hidden):
                        continue

                    total_files += 1
                    lines = count_lines(file_entry)
                    total_lines += lines
                    size = get_file_size(file_entry)

                    # Track extension
                    if '.' in file_name:
                        ext = '.' + file_name.rsplit('.', 1)[1]
                        extensions[ext] += 1

                    # Relative path from skill root
                    rel_path = str(file_entry.relative_to(skill_path))

                    dir_files.append({
                        "name": file_name,
                        "path": rel_path,
                        "lines": lines,
                        "size_bytes": size
                    })

                directories.append({
                    "name": dir_name,
                    "path": f"{dir_name}/",
                    "files": dir_files
                })

            elif entry.is_file():
                file_name = entry.name
                if should_skip_file(file_name, include_hidden):
                    continue

                total_files += 1
                lines = count_lines(entry)
                total_lines += lines
                size = get_file_size(entry)

                # Track extension
                if '.' in file_name:
                    ext = '.' + file_name.rsplit('.', 1)[1]
                    extensions[ext] += 1

                root_files.append({
                    "name": file_name,
                    "path": file_name,
                    "lines": lines,
                    "size_bytes": size
                })

    except OSError as e:
        return {"error": f"Failed to scan directory: {e}"}

    # Build result
    result = {
        "skill_name": skill_name,
        "skill_path": abs_skill_path,
        "directories": directories,
        "root_files": root_files,
        "statistics": {
            "total_directories": total_dirs,
            "total_files": total_files,
            "total_lines": total_lines,
            "by_extension": dict(sorted(extensions.items()))
        }
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Scan a skill directory and return structured inventory"
    )
    parser.add_argument(
        "--skill-path",
        required=True,
        help="Path to the skill directory"
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files (default: false)"
    )

    args = parser.parse_args()

    skill_path = Path(args.skill_path)

    # Validate path
    if not skill_path.exists():
        print(json.dumps({"error": f"Directory not found: {args.skill_path}"}), file=sys.stderr)
        return 1

    if not skill_path.is_dir():
        print(json.dumps({"error": f"Not a directory: {args.skill_path}"}), file=sys.stderr)
        return 1

    # Resolve to absolute path
    skill_path = skill_path.resolve()

    # Scan directory
    result = scan_directory(skill_path, args.include_hidden)

    if "error" in result:
        print(json.dumps(result), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
