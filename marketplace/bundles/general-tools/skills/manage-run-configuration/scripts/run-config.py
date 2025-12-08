#!/usr/bin/env python3
"""
Manage run-configuration.json - initialization and validation.

Consolidated from:
- init-run-config.py → init subcommand
- validate-run-config.py → validate subcommand

Provides operations for managing .plan/run-configuration.json files
including creation, validation, and structure verification.

Output: JSON to stdout with operation results.
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Import file operations from base module
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import base_path


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


# =============================================================================
# Init Subcommand
# =============================================================================

def cmd_init(args) -> int:
    """Initialize run-configuration.json with base structure."""
    try:
        project_dir = Path(args.project_dir).resolve()
        config_path = project_dir / base_path('run-configuration.json')

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


# =============================================================================
# Validate Subcommand
# =============================================================================

def check_required_fields(data: Dict, required: List[str]) -> Tuple[bool, List[str]]:
    """Check if required fields exist."""
    missing = [f for f in required if f not in data]
    return len(missing) == 0, missing


def check_field_type(data: Dict, field: str, expected_type: type) -> Tuple[bool, str]:
    """Check if field has expected type."""
    if field not in data:
        return False, f"Field '{field}' not found"

    actual = type(data[field])
    if actual != expected_type:
        return False, f"Expected {expected_type.__name__}, got {actual.__name__}"

    return True, f"Field '{field}' is {expected_type.__name__}"


def validate_run_config(data: Dict) -> List[Dict]:
    """Validate run-configuration.json format."""
    checks = []

    # Check required fields
    required = ['version', 'commands']
    passed, missing = check_required_fields(data, required)
    checks.append({
        "check": "required_fields",
        "passed": passed,
        "fields": required,
        "missing": missing if not passed else []
    })

    # Check version is integer
    if 'version' in data:
        passed, msg = check_field_type(data, 'version', int)
        checks.append({
            "check": "version_type",
            "passed": passed,
            "message": msg
        })

    # Check commands is object
    if 'commands' in data:
        passed, msg = check_field_type(data, 'commands', dict)
        checks.append({
            "check": "commands_object",
            "passed": passed,
            "message": msg
        })

        # Validate command entries
        if passed:
            invalid_commands = []
            for cmd_name, cmd_data in data['commands'].items():
                if not isinstance(cmd_data, dict):
                    invalid_commands.append(f"{cmd_name} (not an object)")

            if invalid_commands:
                checks.append({
                    "check": "command_entries",
                    "passed": False,
                    "invalid": invalid_commands
                })
            else:
                checks.append({
                    "check": "command_entries",
                    "passed": True,
                    "count": len(data['commands'])
                })

    # Check maven section if present
    if 'maven' in data:
        passed, msg = check_field_type(data, 'maven', dict)
        checks.append({
            "check": "maven_object",
            "passed": passed,
            "message": msg
        })

    return checks


def cmd_validate(args) -> int:
    """Validate run-configuration.json format and structure."""
    try:
        file_path = Path(args.file)

        if not file_path.exists():
            output_error(f"File not found: {file_path}")
            return 1

        # Parse JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            result = {
                "success": True,
                "valid": False,
                "file": str(file_path),
                "format": "run-config",
                "checks": [{"check": "json_syntax", "passed": False, "error": str(e)}]
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

        # Add JSON syntax check
        checks = [{"check": "json_syntax", "passed": True}]

        # Run validation
        checks.extend(validate_run_config(data))

        # Determine overall validity
        valid = all(c.get('passed', True) for c in checks)

        result = {
            "success": True,
            "valid": valid,
            "file": str(file_path),
            "format": "run-config",
            "checks": checks
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    except Exception as e:
        output_error(str(e))
        return 1


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Manage run-configuration.json files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize in current project
  %(prog)s init

  # Initialize in specific directory
  %(prog)s init --project-dir /path/to/project

  # Force reinitialize (overwrites existing)
  %(prog)s init --force

  # Validate run configuration
  %(prog)s validate --file .plan/run-configuration.json
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # init command
    p_init = subparsers.add_parser('init', help='Initialize run-configuration.json')
    p_init.add_argument(
        '--project-dir',
        default='.',
        help='Project directory (default: current directory)'
    )
    p_init.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing file'
    )
    p_init.set_defaults(func=cmd_init)

    # validate command
    p_validate = subparsers.add_parser('validate', help='Validate run-configuration.json')
    p_validate.add_argument('--file', required=True, help='Path to run-configuration.json')
    p_validate.set_defaults(func=cmd_validate)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
