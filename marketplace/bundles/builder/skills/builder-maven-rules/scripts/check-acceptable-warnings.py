#!/usr/bin/env python3
"""
Categorize build warnings against acceptable patterns.

Pure categorization logic - no file I/O. Receives data via stdin or arguments.

Usage:
    # Via stdin (JSON object with warnings and patterns)
    echo '{"warnings": [...], "patterns": [...]}' | python3 check-acceptable-warnings.py

    # Via arguments
    python3 check-acceptable-warnings.py --warnings '[...]' --patterns '[...]'

Input:
    warnings: Array of warning objects from parse-maven-output.py
        [{"type": "...", "message": "...", "severity": "WARNING"}, ...]

    patterns: Array of acceptable warning patterns (strings)
        ["pattern1", "pattern2", ...]

Output:
    {
        "success": true,
        "total": 15,
        "acceptable": 3,
        "fixable": 10,
        "unknown": 2,
        "categorized": {
            "acceptable": [...],
            "fixable": [...],
            "unknown": [...]
        }
    }

Integration:
    This script is called by the builder-maven-rules skill workflow.
    Patterns are loaded via cui-utilities:json-file-operations from
    .claude/run-configuration.json at path maven.acceptable_warnings.
"""

import argparse
import json
import re
import sys
from typing import List


# Warning types that are ALWAYS fixable (never acceptable)
ALWAYS_FIXABLE_TYPES = [
    "javadoc_warning",
    "compilation_error",
    "deprecation_warning",
    "unchecked_warning",
]


def is_acceptable(warning_message: str, patterns: List[str]) -> bool:
    """Check if a warning matches any acceptable pattern."""
    for pattern in patterns:
        # Strip [WARNING] prefix if present
        clean_pattern = pattern
        if clean_pattern.startswith('[WARNING]'):
            clean_pattern = clean_pattern[9:].strip()

        # Exact match (substring)
        if clean_pattern in warning_message:
            return True

        # Try as regex pattern
        try:
            if re.search(clean_pattern, warning_message, re.IGNORECASE):
                return True
        except re.error:
            # Invalid regex, treat as literal only
            pass

    return False


def categorize_warning(warning: dict, patterns: List[str]) -> str:
    """
    Categorize a warning as 'acceptable', 'fixable', or 'unknown'.

    Returns: 'acceptable', 'fixable', or 'unknown'
    """
    warning_type = warning.get("type", "other")
    message = warning.get("message", "")

    # Always fixable types cannot be acceptable
    if warning_type in ALWAYS_FIXABLE_TYPES:
        return "fixable"

    # Check against acceptable patterns
    if is_acceptable(message, patterns):
        return "acceptable"

    # Known warning types are fixable
    known_fixable_types = [
        "compilation_error",
        "test_failure",
        "dependency_error",
    ]
    if warning_type in known_fixable_types:
        return "fixable"

    # OpenRewrite info is acceptable (handled separately)
    if warning_type == "openrewrite_info":
        return "acceptable"

    # Unknown warnings need classification
    if warning_type in ["other", "other_warnings"]:
        return "unknown"

    # Default to fixable for known types
    return "fixable"


def categorize_warnings(warnings: List[dict], patterns: List[str]) -> dict:
    """
    Categorize all warnings.

    Args:
        warnings: List of warning objects with type, message, severity
        patterns: List of acceptable warning patterns

    Returns:
        Categorized results with counts and warning lists
    """
    # Filter to warnings only (not errors)
    warning_items = [w for w in warnings if w.get("severity") == "WARNING"]

    acceptable = []
    fixable = []
    unknown = []

    for warning in warning_items:
        category = categorize_warning(warning, patterns)

        if category == "acceptable":
            acceptable.append(warning)
        elif category == "fixable":
            fixable.append(warning)
        else:
            unknown.append({
                **warning,
                "requires_classification": True
            })

    return {
        "success": True,
        "total": len(warning_items),
        "acceptable": len(acceptable),
        "fixable": len(fixable),
        "unknown": len(unknown),
        "categorized": {
            "acceptable": acceptable,
            "fixable": fixable,
            "unknown": unknown
        }
    }


def flatten_patterns(acceptable_warnings: dict) -> List[str]:
    """
    Flatten acceptable_warnings object into a list of patterns.

    Handles structure like:
    {
        "transitive_dependency": ["pattern1"],
        "plugin_compatibility": ["pattern2"],
        "platform_specific": ["pattern3"]
    }
    """
    patterns = []
    if isinstance(acceptable_warnings, dict):
        for key, value in acceptable_warnings.items():
            if isinstance(value, list):
                patterns.extend(str(p) for p in value if p)
    elif isinstance(acceptable_warnings, list):
        patterns.extend(str(p) for p in acceptable_warnings if p)
    return patterns


def output_error(error: str) -> None:
    """Output error as JSON."""
    result = {"success": False, "error": error}
    print(json.dumps(result, indent=2))
    sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Categorize build warnings against acceptable patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Via stdin
    echo '{"warnings": [...], "patterns": [...]}' | python3 %(prog)s

    # Via arguments
    python3 %(prog)s --warnings '[{"type":"other","message":"test","severity":"WARNING"}]' --patterns '["test"]'

    # With acceptable_warnings object (will be flattened)
    python3 %(prog)s --warnings '[...]' --acceptable-warnings '{"transitive_dependency": ["pattern1"]}'
        """
    )
    parser.add_argument(
        "--warnings",
        type=str,
        help="JSON array of warning objects"
    )
    parser.add_argument(
        "--patterns",
        type=str,
        help="JSON array of acceptable patterns"
    )
    parser.add_argument(
        "--acceptable-warnings",
        type=str,
        dest="acceptable_warnings",
        help="JSON object with categorized patterns (will be flattened)"
    )

    args = parser.parse_args()

    # Determine input source
    warnings = None
    patterns = []

    if args.warnings:
        # From arguments
        try:
            warnings = json.loads(args.warnings)
        except json.JSONDecodeError as e:
            output_error(f"Invalid JSON in --warnings: {e}")

        if args.patterns:
            try:
                patterns = json.loads(args.patterns)
            except json.JSONDecodeError as e:
                output_error(f"Invalid JSON in --patterns: {e}")
        elif args.acceptable_warnings:
            try:
                acceptable = json.loads(args.acceptable_warnings)
                patterns = flatten_patterns(acceptable)
            except json.JSONDecodeError as e:
                output_error(f"Invalid JSON in --acceptable-warnings: {e}")
    else:
        # From stdin
        if sys.stdin.isatty():
            output_error("No input provided. Use --warnings/--patterns or pipe JSON to stdin.")

        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            output_error(f"Invalid JSON from stdin: {e}")

        warnings = input_data.get("warnings", [])

        # Support both "patterns" array and "acceptable_warnings" object
        if "patterns" in input_data:
            patterns = input_data["patterns"]
        elif "acceptable_warnings" in input_data:
            patterns = flatten_patterns(input_data["acceptable_warnings"])

    # Validate inputs
    if warnings is None:
        output_error("No warnings provided")

    if not isinstance(warnings, list):
        output_error("warnings must be an array")

    if not isinstance(patterns, list):
        output_error("patterns must be an array")

    # Categorize warnings
    result = categorize_warnings(warnings, patterns)

    print(json.dumps(result, indent=2))

    # Exit with non-zero if there are fixable or unknown warnings
    if result["fixable"] > 0 or result["unknown"] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
