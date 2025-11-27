#!/usr/bin/env python3
"""
Categorize warnings against acceptable patterns.

Pure logic script that categorizes build warnings as:
- acceptable: match known acceptable patterns
- fixable: always require fixing
- unknown: need user decision
"""

import argparse
import json
import re
import sys


# Types that should always be fixed, never acceptable
ALWAYS_FIXABLE_TYPES = [
    "javadoc_warning",
    "compilation_error",
    "deprecation_warning",
    "unchecked_warning",
]


def match_pattern(message: str, pattern: str) -> bool:
    """Check if message matches pattern (exact, prefix, contains, or regex)."""
    # Exact match
    if message == pattern:
        return True

    # Prefix match (pattern ends with *)
    if pattern.endswith("*") and message.startswith(pattern[:-1]):
        return True

    # Contains match (pattern starts and ends with *)
    if pattern.startswith("*") and pattern.endswith("*"):
        return pattern[1:-1] in message

    # Contains match (pattern starts with *)
    if pattern.startswith("*") and message.endswith(pattern[1:]):
        return True

    # Regex match (pattern starts with ^)
    if pattern.startswith("^"):
        try:
            if re.match(pattern, message):
                return True
        except re.error:
            pass

    return False


def categorize_warnings(
    warnings: list[dict], acceptable_patterns: dict
) -> dict:
    """Categorize warnings against acceptable patterns."""
    categorized = {
        "acceptable": [],
        "fixable": [],
        "unknown": [],
    }

    for warning in warnings:
        warning_type = warning.get("type", "other")
        message = warning.get("message", "")
        severity = warning.get("severity", "WARNING")

        # Always fixable types
        if warning_type in ALWAYS_FIXABLE_TYPES:
            categorized["fixable"].append(
                {
                    **warning,
                    "reason": f"Type '{warning_type}' is always fixable",
                }
            )
            continue

        # Check against acceptable patterns
        is_acceptable = False
        matched_category = None

        for category, patterns in acceptable_patterns.items():
            for pattern in patterns:
                if match_pattern(message, pattern):
                    is_acceptable = True
                    matched_category = category
                    break
            if is_acceptable:
                break

        if is_acceptable:
            categorized["acceptable"].append(
                {
                    **warning,
                    "reason": f"Matches acceptable pattern in '{matched_category}'",
                }
            )
        else:
            categorized["unknown"].append(
                {
                    **warning,
                    "reason": "No matching acceptable pattern",
                }
            )

    # Calculate totals
    result = {
        "success": True,
        "total": len(warnings),
        "acceptable": len(categorized["acceptable"]),
        "fixable": len(categorized["fixable"]),
        "unknown": len(categorized["unknown"]),
        "categorized": categorized,
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Categorize warnings against acceptable patterns"
    )
    parser.add_argument(
        "--warnings",
        help="JSON array of warnings",
    )
    parser.add_argument(
        "--acceptable-warnings",
        help="JSON object with acceptable patterns by category",
    )

    args = parser.parse_args()

    # Parse warnings from args or stdin
    if args.warnings:
        try:
            warnings = json.loads(args.warnings)
        except json.JSONDecodeError as e:
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid warnings JSON: {e}",
                    }
                )
            )
            sys.exit(1)
    else:
        # Read from stdin
        stdin_data = sys.stdin.read()
        try:
            data = json.loads(stdin_data)
            warnings = data.get("warnings", [])
        except json.JSONDecodeError as e:
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": f"Invalid stdin JSON: {e}",
                    }
                )
            )
            sys.exit(1)

    # Parse acceptable patterns
    acceptable_patterns = {}
    if args.acceptable_warnings:
        try:
            acceptable_patterns = json.loads(args.acceptable_warnings)
        except json.JSONDecodeError:
            acceptable_patterns = {}

    # Categorize
    result = categorize_warnings(warnings, acceptable_patterns)

    # Output
    print(json.dumps(result, indent=2))

    # Exit code: 0 if no fixable/unknown, 1 otherwise
    if result["fixable"] > 0 or result["unknown"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
