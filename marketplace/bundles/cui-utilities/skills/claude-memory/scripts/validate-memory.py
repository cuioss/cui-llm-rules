#!/usr/bin/env python3
"""
Validate memory file format and structure integrity.

Validates .claude/memory/ files against expected schema
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

            # Validate category value
            if 'category' in data['meta']:
                valid_categories = ['context', 'decisions', 'interfaces', 'handoffs']
                cat = data['meta']['category']
                checks.append({
                    "check": "category_valid",
                    "passed": cat in valid_categories,
                    "value": cat,
                    "valid_values": valid_categories
                })

    # Check content exists (can be any type)
    if 'content' in data:
        checks.append({
            "check": "content_present",
            "passed": True,
            "message": f"Content is {type(data['content']).__name__}"
        })

    return checks


def output_success(file_path: str, valid: bool, checks: List[Dict]) -> None:
    """Output validation result as JSON."""
    result = {
        "success": True,
        "valid": valid,
        "file": file_path,
        "format": "memory",
        "checks": checks
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def output_error(error: str) -> None:
    """Output error result as JSON to stderr."""
    result = {"success": False, "error": error}
    print(json.dumps(result, indent=2), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Validate memory file format and structure integrity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate memory file
  %(prog)s .claude/memory/context/2025-11-25-auth.json

  # Validate decisions file
  %(prog)s .claude/memory/decisions/auth-implementation.json
"""
    )

    parser.add_argument('file_path', help='Path to memory file to validate')

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
    checks.extend(validate_memory(data))

    # Determine overall validity
    valid = all(c.get('passed', True) for c in checks)

    output_success(str(file_path), valid, checks)
    return 0


if __name__ == '__main__':
    sys.exit(main())
