#!/usr/bin/env python3
"""
Validate run-configuration.json format and structure integrity.

Validates .claude/run-configuration.json against expected schema
and reports detailed check results.

Output: JSON to stdout with validation results.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


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


def output_success(file_path: str, valid: bool, checks: List[Dict]) -> None:
    """Output validation result as JSON."""
    result = {
        "success": True,
        "valid": valid,
        "file": file_path,
        "format": "run-config",
        "checks": checks
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def output_error(error: str) -> None:
    """Output error result as JSON to stderr."""
    result = {"success": False, "error": error}
    print(json.dumps(result, indent=2), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Validate run-configuration.json format and structure integrity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate run configuration
  %(prog)s .claude/run-configuration.json

  # Validate specific project's config
  %(prog)s /path/to/project/.claude/run-configuration.json
"""
    )

    parser.add_argument('file_path', help='Path to run-configuration.json to validate')

    args = parser.parse_args()

    file_path = Path(args.file_path)

    # Check file exists
    if not file_path.exists():
        output_error(f"File not found: {file_path}")
        return 1

    # Parse JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        output_success(
            str(file_path),
            False,
            [{"check": "json_syntax", "passed": False, "error": str(e)}]
        )
        return 0  # Not an error, just invalid

    # Add JSON syntax check
    checks = [{"check": "json_syntax", "passed": True}]

    # Run validation
    checks.extend(validate_run_config(data))

    # Determine overall validity
    valid = all(c.get('passed', True) for c in checks)

    output_success(str(file_path), valid, checks)
    return 0


if __name__ == '__main__':
    sys.exit(main())
