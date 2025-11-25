#!/usr/bin/env python3
"""
Manage the .claude/memory/ layer for session persistence.

Provides CRUD operations for memory files organized by category:
context, decisions, interfaces, handoffs.

Output: JSON to stdout with operation results.
"""

import argparse
import json
import os
import re
import shutil
import sys
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Suppress deprecation warnings in output
warnings.filterwarnings('ignore', category=DeprecationWarning)


MEMORY_BASE = Path('.claude/memory')
CATEGORIES = ['context', 'handoffs']
ARCHIVE_DIR = 'archive'


def parse_duration(duration_str: str) -> timedelta:
    """Parse duration string like '7d', '24h', '30m' into timedelta."""
    match = re.match(r'^(\d+)([dhm])$', duration_str.lower())
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}. Use format like '7d', '24h', '30m'")

    value = int(match.group(1))
    unit = match.group(2)

    if unit == 'd':
        return timedelta(days=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'm':
        return timedelta(minutes=value)

    raise ValueError(f"Unknown duration unit: {unit}")


def get_memory_path(category: str, identifier: Optional[str] = None) -> Path:
    """Get path to memory category or specific file."""
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Must be one of: {', '.join(CATEGORIES)}")

    path = MEMORY_BASE / category
    if identifier:
        # Sanitize identifier for filename
        safe_id = re.sub(r'[^\w\-.]', '_', identifier)
        if not safe_id.endswith('.json'):
            safe_id += '.json'
        path = path / safe_id

    return path


def create_memory_envelope(category: str, identifier: str, content: Any, session_id: Optional[str] = None) -> Dict:
    """Create memory file with metadata envelope."""
    return {
        "meta": {
            "created": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "category": category,
            "summary": identifier,
            "session_id": session_id
        },
        "content": content
    }


def read_memory_file(file_path: Path) -> Dict:
    """Read and parse a memory file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_memory_file(file_path: Path, data: Dict) -> None:
    """Write memory file with proper formatting."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def get_file_info(file_path: Path) -> Dict:
    """Get metadata about a memory file."""
    stat = file_path.stat()
    try:
        data = read_memory_file(file_path)
        meta = data.get('meta', {})
    except (json.JSONDecodeError, KeyError):
        meta = {}

    return {
        "name": file_path.name,
        "path": str(file_path),
        "created": meta.get('created', datetime.fromtimestamp(stat.st_ctime).isoformat() + 'Z'),
        "size": stat.st_size,
        "summary": meta.get('summary', file_path.stem),
        "category": meta.get('category')
    }


def output_success(operation: str, **kwargs) -> None:
    """Output success result as JSON."""
    result = {"success": True, "operation": operation}
    result.update(kwargs)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def output_error(operation: str, error: str) -> None:
    """Output error result as JSON to stderr."""
    result = {"success": False, "operation": operation, "error": error}
    print(json.dumps(result, indent=2), file=sys.stderr)


def cmd_init(args) -> int:
    """Initialize memory directory structure."""
    try:
        created = []
        for category in CATEGORIES:
            cat_path = MEMORY_BASE / category
            if not cat_path.exists():
                cat_path.mkdir(parents=True)
                created.append(str(cat_path))

        # Create archive directory
        archive_path = MEMORY_BASE / ARCHIVE_DIR
        if not archive_path.exists():
            archive_path.mkdir(parents=True)
            created.append(str(archive_path))

        output_success("init", created=created, base_path=str(MEMORY_BASE))
        return 0
    except Exception as e:
        output_error("init", str(e))
        return 1


def cmd_save(args) -> int:
    """Save content to memory file."""
    try:
        if not args.category:
            output_error("save", "Category required")
            return 1
        if not args.identifier:
            output_error("save", "Identifier required")
            return 1
        if not args.content:
            output_error("save", "Content required")
            return 1

        content = json.loads(args.content)

        # Generate timestamped filename for context category
        if args.category == 'context':
            date_prefix = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            identifier = f"{date_prefix}-{args.identifier}"
        else:
            identifier = args.identifier

        file_path = get_memory_path(args.category, identifier)
        data = create_memory_envelope(args.category, args.identifier, content, args.session_id)

        write_memory_file(file_path, data)

        output_success("save",
                       path=str(file_path),
                       category=args.category,
                       identifier=identifier)
        return 0
    except json.JSONDecodeError as e:
        output_error("save", f"Invalid JSON content: {e}")
        return 1
    except Exception as e:
        output_error("save", str(e))
        return 1


def cmd_load(args) -> int:
    """Load content from memory file."""
    try:
        if not args.category:
            output_error("load", "Category required")
            return 1
        if not args.identifier:
            output_error("load", "Identifier required")
            return 1

        file_path = get_memory_path(args.category, args.identifier)

        if not file_path.exists():
            output_error("load", f"File not found: {file_path}")
            return 1

        data = read_memory_file(file_path)

        output_success("load",
                       path=str(file_path),
                       meta=data.get('meta', {}),
                       content=data.get('content', {}))
        return 0
    except Exception as e:
        output_error("load", str(e))
        return 1


def cmd_list(args) -> int:
    """List memory files in category."""
    try:
        files = []

        if args.category:
            categories = [args.category]
        else:
            categories = CATEGORIES

        for category in categories:
            cat_path = MEMORY_BASE / category
            if not cat_path.exists():
                continue

            for file_path in cat_path.glob('*.json'):
                info = get_file_info(file_path)

                # Apply --since filter
                if args.since:
                    try:
                        duration = parse_duration(args.since)
                        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - duration
                        created_str = info.get('created', '')
                        if created_str:
                            created = datetime.fromisoformat(created_str.rstrip('Z'))
                            if created < cutoff:
                                continue
                    except (ValueError, TypeError):
                        pass

                files.append(info)

        # Sort by created date, newest first
        files.sort(key=lambda x: x.get('created', ''), reverse=True)

        output_success("list",
                       category=args.category,
                       count=len(files),
                       files=files)
        return 0
    except Exception as e:
        output_error("list", str(e))
        return 1


def cmd_query(args) -> int:
    """Find memory files matching pattern."""
    try:
        if not args.pattern:
            output_error("query", "Pattern required")
            return 1

        # Convert glob pattern to regex
        pattern = args.pattern.replace('*', '.*').replace('?', '.')
        regex = re.compile(pattern, re.IGNORECASE)

        files = []
        categories = [args.category] if args.category else CATEGORIES

        for category in categories:
            cat_path = MEMORY_BASE / category
            if not cat_path.exists():
                continue

            for file_path in cat_path.glob('*.json'):
                # Match against filename and summary
                info = get_file_info(file_path)
                if regex.search(file_path.stem) or regex.search(info.get('summary', '')):
                    files.append(info)

        files.sort(key=lambda x: x.get('created', ''), reverse=True)

        output_success("query",
                       pattern=args.pattern,
                       count=len(files),
                       files=files)
        return 0
    except Exception as e:
        output_error("query", str(e))
        return 1


def cmd_cleanup(args) -> int:
    """Remove old memory files based on age."""
    try:
        if not args.older_than:
            output_error("cleanup", "--older-than duration required")
            return 1

        duration = parse_duration(args.older_than)
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - duration

        removed = []
        categories = [args.category] if args.category else CATEGORIES

        for category in categories:
            cat_path = MEMORY_BASE / category
            if not cat_path.exists():
                continue

            for file_path in cat_path.glob('*.json'):
                try:
                    data = read_memory_file(file_path)
                    created_str = data.get('meta', {}).get('created', '')
                    if created_str:
                        created = datetime.fromisoformat(created_str.rstrip('Z'))
                        if created < cutoff:
                            file_path.unlink()
                            removed.append(str(file_path))
                except (json.JSONDecodeError, ValueError, KeyError):
                    # If we can't read the file, check file modification time
                    stat = file_path.stat()
                    if datetime.fromtimestamp(stat.st_mtime) < cutoff:
                        file_path.unlink()
                        removed.append(str(file_path))

        output_success("cleanup",
                       older_than=args.older_than,
                       removed_count=len(removed),
                       removed=removed)
        return 0
    except Exception as e:
        output_error("cleanup", str(e))
        return 1


def cmd_archive(args) -> int:
    """Move memory file to archive."""
    try:
        if not args.category:
            output_error("archive", "Category required")
            return 1
        if not args.identifier:
            output_error("archive", "Identifier required")
            return 1

        source_path = get_memory_path(args.category, args.identifier)
        if not source_path.exists():
            output_error("archive", f"File not found: {source_path}")
            return 1

        # Create archive path preserving category structure
        archive_path = MEMORY_BASE / ARCHIVE_DIR / args.category
        archive_path.mkdir(parents=True, exist_ok=True)
        dest_path = archive_path / source_path.name

        # If file exists in archive, add timestamp
        if dest_path.exists():
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
            dest_path = archive_path / f"{source_path.stem}_{timestamp}.json"

        shutil.move(str(source_path), str(dest_path))

        output_success("archive",
                       source=str(source_path),
                       destination=str(dest_path))
        return 0
    except Exception as e:
        output_error("archive", str(e))
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Manage .claude/memory/ layer for session persistence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Categories:
  context     - Session context snapshots (short-lived)
  handoffs    - Pending handoff state (until completed)

Examples:
  # Initialize memory structure
  %(prog)s init

  # Save context snapshot
  %(prog)s save --category context --identifier "feature-auth" --content '{"notes": "Working on auth"}'

  # Load memory file
  %(prog)s load --category handoffs --identifier "task-42"

  # List context files from last 7 days
  %(prog)s list --category context --since 7d

  # Find files matching pattern
  %(prog)s query --pattern "auth*" --category context

  # Cleanup old context files
  %(prog)s cleanup --category context --older-than 7d

  # Archive completed handoff
  %(prog)s archive --category handoffs --identifier "task-42"
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # init command
    p_init = subparsers.add_parser('init', help='Initialize memory directory structure')
    p_init.set_defaults(func=cmd_init)

    # save command
    p_save = subparsers.add_parser('save', help='Save content to memory file')
    p_save.add_argument('--category', choices=CATEGORIES, help='Memory category')
    p_save.add_argument('--identifier', help='File identifier/summary')
    p_save.add_argument('--content', help='JSON content to save')
    p_save.add_argument('--session-id', dest='session_id', help='Optional session ID')
    p_save.set_defaults(func=cmd_save)

    # load command
    p_load = subparsers.add_parser('load', help='Load content from memory file')
    p_load.add_argument('--category', choices=CATEGORIES, help='Memory category')
    p_load.add_argument('--identifier', help='File identifier')
    p_load.set_defaults(func=cmd_load)

    # list command
    p_list = subparsers.add_parser('list', help='List memory files')
    p_list.add_argument('--category', choices=CATEGORIES, help='Filter by category')
    p_list.add_argument('--since', help='Filter by age (e.g., 7d, 24h)')
    p_list.set_defaults(func=cmd_list)

    # query command
    p_query = subparsers.add_parser('query', help='Find files matching pattern')
    p_query.add_argument('--pattern', help='Glob pattern to match')
    p_query.add_argument('--category', choices=CATEGORIES, help='Filter by category')
    p_query.set_defaults(func=cmd_query)

    # cleanup command
    p_cleanup = subparsers.add_parser('cleanup', help='Remove old memory files')
    p_cleanup.add_argument('--category', choices=CATEGORIES, help='Filter by category')
    p_cleanup.add_argument('--older-than', dest='older_than', help='Remove files older than (e.g., 7d, 24h)')
    p_cleanup.set_defaults(func=cmd_cleanup)

    # archive command
    p_archive = subparsers.add_parser('archive', help='Move memory file to archive')
    p_archive.add_argument('--category', choices=CATEGORIES, help='Memory category')
    p_archive.add_argument('--identifier', help='File identifier')
    p_archive.set_defaults(func=cmd_archive)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
