#!/usr/bin/env python3
"""
Validate JSON file format and structure integrity.

Validates .claude/ configuration files against expected schemas
and reports detailed check results.

Output: JSON to stdout with validation results.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Format detection patterns
FORMAT_PATTERNS = {
    'run-config': ['run-configuration.json'],
    'scripts-local': ['scripts.local.json'],
    'settings-local': ['settings.local.json', 'settings.json'],
    'memory': ['memory/'],
}


def detect_format(file_path: Path) -> Optional[str]:
    """Auto-detect format based on file path."""
    path_str = str(file_path)

    for format_name, patterns in FORMAT_PATTERNS.items():
        for pattern in patterns:
            if pattern in path_str:
                return format_name

    return None


def check_json_syntax(data: Any) -> Tuple[bool, str]:
    """Check if data is valid (already parsed JSON)."""
    return True, "Valid JSON syntax"


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

    # Check maven section if present
    if 'maven' in data:
        passed, msg = check_field_type(data, 'maven', dict)
        checks.append({
            "check": "maven_object",
            "passed": passed,
            "message": msg
        })

    # Check agent_decisions section if present
    if 'agent_decisions' in data:
        passed, msg = check_field_type(data, 'agent_decisions', dict)
        checks.append({
            "check": "agent_decisions_object",
            "passed": passed,
            "message": msg
        })

    return checks


def validate_scripts_local(data: Dict) -> List[Dict]:
    """Validate scripts.local.json format."""
    checks = []

    # Check required fields
    required = ['version', 'scripts', 'permissions']
    passed, missing = check_required_fields(data, required)
    checks.append({
        "check": "required_fields",
        "passed": passed,
        "fields": required,
        "missing": missing if not passed else []
    })

    # Check scripts is object
    if 'scripts' in data:
        passed, msg = check_field_type(data, 'scripts', dict)
        checks.append({
            "check": "scripts_object",
            "passed": passed,
            "message": msg
        })

        # Validate script entries
        if passed:
            invalid_scripts = []
            for key, value in data['scripts'].items():
                if not isinstance(value, dict):
                    invalid_scripts.append(key)
                elif 'absolute' not in value:
                    invalid_scripts.append(f"{key} (missing 'absolute')")

            checks.append({
                "check": "script_entries",
                "passed": len(invalid_scripts) == 0,
                "invalid": invalid_scripts
            })

    # Check permissions is array
    if 'permissions' in data:
        passed, msg = check_field_type(data, 'permissions', list)
        checks.append({
            "check": "permissions_array",
            "passed": passed,
            "message": msg
        })

    return checks


def validate_settings_local(data: Dict) -> List[Dict]:
    """Validate settings.local.json format."""
    checks = []

    # Just needs to be a valid JSON object
    checks.append({
        "check": "json_object",
        "passed": isinstance(data, dict),
        "message": "Valid JSON object" if isinstance(data, dict) else "Must be JSON object"
    })

    # Check known arrays if present
    for field in ['allow', 'deny', 'ask']:
        if field in data:
            passed, msg = check_field_type(data, field, list)
            checks.append({
                "check": f"{field}_array",
                "passed": passed,
                "message": msg
            })

    return checks


def validate_memory(data: Dict) -> List[Dict]:
    """Validate memory file format."""
    checks = []

    # Check required envelope
    required = ['meta', 'content']
    passed, missing = check_required_fields(data, required)
    checks.append({
        "check": "required_fields",
        "passed": passed,
        "fields": required,
        "missing": missing if not passed else []
    })

    # Check meta structure
    if 'meta' in data:
        passed, msg = check_field_type(data, 'meta', dict)
        checks.append({
            "check": "meta_object",
            "passed": passed,
            "message": msg
        })

        if passed:
            meta_required = ['created', 'category', 'summary']
            meta_passed, meta_missing = check_required_fields(data['meta'], meta_required)
            checks.append({
                "check": "meta_required_fields",
                "passed": meta_passed,
                "fields": meta_required,
                "missing": meta_missing if not meta_passed else []
            })

    # Check content exists (can be any type)
    if 'content' in data:
        checks.append({
            "check": "content_present",
            "passed": True,
            "message": f"Content is {type(data['content']).__name__}"
        })

    return checks


VALIDATORS = {
    'run-config': validate_run_config,
    'scripts-local': validate_scripts_local,
    'settings-local': validate_settings_local,
    'memory': validate_memory,
}


def output_success(file_path: str, format_type: str, valid: bool, checks: List[Dict]) -> None:
    """Output validation result as JSON."""
    result = {
        "success": True,
        "valid": valid,
        "file": file_path,
        "format": format_type,
        "checks": checks
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def output_error(error: str) -> None:
    """Output error result as JSON to stderr."""
    result = {"success": False, "error": error}
    print(json.dumps(result, indent=2), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Validate JSON file format and structure integrity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Format types:
  run-config     - .claude/run-configuration.json
  scripts-local  - .claude/scripts.local.json
  settings-local - .claude/settings.local.json
  memory         - .claude/memory/**/*.json

Examples:
  # Validate with auto-detection
  %(prog)s .claude/run-configuration.json

  # Validate with explicit format
  %(prog)s .claude/settings.local.json --format settings-local

  # Validate memory file
  %(prog)s .claude/memory/context/2025-11-25-auth.json --format memory
"""
    )

    parser.add_argument('file_path', help='Path to JSON file to validate')
    parser.add_argument('--format', choices=list(VALIDATORS.keys()),
                        help='Expected format type (auto-detected if omitted)')

    args = parser.parse_args()

    file_path = Path(args.file_path)

    # Check file exists
    if not file_path.exists():
        output_error(f"File not found: {file_path}")
        return 1

    # Determine format
    format_type = args.format or detect_format(file_path)
    if not format_type:
        output_error(f"Cannot auto-detect format. Please specify --format")
        return 1

    if format_type not in VALIDATORS:
        output_error(f"Unknown format: {format_type}")
        return 1

    # Parse JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        output_success(
            str(file_path),
            format_type,
            False,
            [{"check": "json_syntax", "passed": False, "error": str(e)}]
        )
        return 0  # Not an error, just invalid

    # Add JSON syntax check
    checks = [{"check": "json_syntax", "passed": True}]

    # Run format-specific validation
    validator = VALIDATORS[format_type]
    checks.extend(validator(data))

    # Determine overall validity
    valid = all(c.get('passed', True) for c in checks)

    output_success(str(file_path), format_type, valid, checks)
    return 0


if __name__ == '__main__':
    sys.exit(main())
