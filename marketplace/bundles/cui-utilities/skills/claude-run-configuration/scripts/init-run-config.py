#!/usr/bin/env python3
"""
Initialize run-configuration.json with base structure if it doesn't exist.

Creates .claude/run-configuration.json with the required base structure
for tracking command execution history and configurations.

Output: JSON to stdout with initialization result.
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path


DEFAULT_STRUCTURE = {
    "version": 1,
    "commands": {},
    "maven": {
        "acceptable_warnings": {
            "transitive_dependency": [],
            "plugin_compatibility": [],
            "platform_specific": []
        }
    }
}


def write_json_file(file_path: Path, data: dict) -> None:
    """Write JSON data to file atomically."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(
        suffix='.json',
        prefix='.tmp_',
        dir=file_path.parent
    )
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        os.replace(temp_path, file_path)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def output_success(action: str, **kwargs) -> None:
    """Output success result as JSON."""
    result = {"success": True, "action": action}
    result.update(kwargs)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def output_error(error: str) -> None:
    """Output error result as JSON to stderr."""
    result = {"success": False, "error": error}
    print(json.dumps(result, indent=2), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Initialize run-configuration.json with base structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize in current project
  %(prog)s

  # Initialize in specific directory
  %(prog)s --project-dir /path/to/project

  # Force reinitialize (overwrites existing)
  %(prog)s --force
"""
    )

    parser.add_argument(
        '--project-dir',
        default='.',
        help='Project directory (default: current directory)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing file'
    )

    args = parser.parse_args()

    try:
        project_dir = Path(args.project_dir).resolve()
        config_path = project_dir / '.claude' / 'run-configuration.json'

        if config_path.exists() and not args.force:
            output_success(
                "skipped",
                path=str(config_path),
                reason="File already exists (use --force to overwrite)"
            )
            return 0

        write_json_file(config_path, DEFAULT_STRUCTURE)

        action = "recreated" if args.force and config_path.exists() else "created"
        output_success(
            action,
            path=str(config_path),
            structure=DEFAULT_STRUCTURE
        )
        return 0

    except Exception as e:
        output_error(str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
