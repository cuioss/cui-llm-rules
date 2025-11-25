#!/usr/bin/env python3
"""
Check build warnings against acceptable warnings list.

Compares warnings from parsed Maven output against the acceptable warnings
configuration and categorizes them as acceptable, fixable, or unknown.

Usage:
    python3 check-acceptable-warnings.py --parsed-output <json-file> --config <config-file>
    python3 check-acceptable-warnings.py --help

Input:
    Expects pre-parsed JSON from parse-maven-output.py (not raw log file)

Output:
    JSON with categorized warnings:
    {
        "status": "success",
        "data": {
            "total_warnings": 15,
            "acceptable": 3,
            "fixable": 10,
            "unknown": 2,
            "fixable_warnings": [...],
            "unknown_warnings": [...]
        }
    }
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# Warning types that are ALWAYS fixable (never acceptable)
ALWAYS_FIXABLE_TYPES = [
    "javadoc_warning",
    "compilation_error",
    "deprecation_warning",
    "unchecked_warning",
]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Check build warnings against acceptable warnings list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check warnings against config
    python3 check-acceptable-warnings.py \\
        --parsed-output build-result.json \\
        --config .claude/run-configuration.md

    # Use default config location
    python3 check-acceptable-warnings.py \\
        --parsed-output build-result.json
        """,
    )
    parser.add_argument(
        "--parsed-output",
        type=str,
        required=True,
        help="Path to parsed Maven output JSON (from parse-maven-output.py)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=".claude/run-configuration.md",
        help="Path to acceptable warnings config (default: .claude/run-configuration.md)"
    )
    return parser.parse_args()


def load_parsed_output(path: str) -> dict:
    """Load and validate parsed Maven output JSON."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate structure
        if "data" not in data or "issues" not in data.get("data", {}):
            return {
                "error": "Invalid parsed output format: missing data.issues"
            }

        return data
    except FileNotFoundError:
        return {"error": f"Parsed output file not found: {path}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in parsed output: {e}"}


def load_acceptable_patterns(config_path: str) -> list:
    """
    Load acceptable warning patterns from config file.

    Parses markdown format looking for patterns in "Acceptable Warnings" section.
    """
    patterns = []

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        # Config file doesn't exist - no acceptable warnings
        return []

    # Find "Acceptable Warnings" section
    in_acceptable_section = False

    for line in content.split('\n'):
        # Check for section headers
        if re.match(r'^#{1,4}\s+Acceptable\s+Warnings', line, re.IGNORECASE):
            in_acceptable_section = True
            continue

        # End of section (next header)
        if in_acceptable_section and re.match(r'^#{1,4}\s+', line):
            if not re.match(r'^#{1,4}\s+(Transitive|Plugin|Platform)', line, re.IGNORECASE):
                in_acceptable_section = False
                continue

        # Extract patterns (lines starting with - ` or - [WARNING])
        if in_acceptable_section:
            # Pattern: - `[WARNING] ...`
            match = re.match(r'^-\s+`\[WARNING\]\s*(.+?)`', line)
            if match:
                patterns.append(match.group(1).strip())
                continue

            # Pattern: - [WARNING] ...
            match = re.match(r'^-\s+\[WARNING\]\s*(.+)', line)
            if match:
                patterns.append(match.group(1).strip())
                continue

    return patterns


def is_acceptable(warning_message: str, patterns: list) -> bool:
    """Check if a warning matches any acceptable pattern."""
    for pattern in patterns:
        # Exact match
        if pattern in warning_message:
            return True

        # Try as regex pattern
        try:
            if re.search(pattern, warning_message, re.IGNORECASE):
                return True
        except re.error:
            # Invalid regex, treat as literal
            pass

    return False


def categorize_warning(warning: dict, acceptable_patterns: list) -> str:
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
    if is_acceptable(message, acceptable_patterns):
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


def check_warnings(parsed_output: dict, acceptable_patterns: list) -> dict:
    """
    Check all warnings and categorize them.

    Returns categorized results.
    """
    issues = parsed_output.get("data", {}).get("issues", [])

    # Filter to warnings only (not errors)
    warnings = [i for i in issues if i.get("severity") == "WARNING"]

    acceptable = []
    fixable = []
    unknown = []

    for warning in warnings:
        category = categorize_warning(warning, acceptable_patterns)

        if category == "acceptable":
            acceptable.append(warning)
        elif category == "fixable":
            fixable.append(warning)
        else:
            unknown.append(warning)

    return {
        "status": "success",
        "data": {
            "total_warnings": len(warnings),
            "acceptable": len(acceptable),
            "fixable": len(fixable),
            "unknown": len(unknown),
            "acceptable_warnings": acceptable,
            "fixable_warnings": fixable,
            "unknown_warnings": [
                {
                    **w,
                    "requires_classification": True
                }
                for w in unknown
            ]
        }
    }


def main():
    """Main entry point."""
    args = parse_args()

    # Load parsed Maven output
    parsed_output = load_parsed_output(args.parsed_output)
    if "error" in parsed_output:
        result = {
            "status": "error",
            "error": "load_failed",
            "message": parsed_output["error"]
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Load acceptable patterns
    acceptable_patterns = load_acceptable_patterns(args.config)

    # Check and categorize warnings
    result = check_warnings(parsed_output, acceptable_patterns)

    print(json.dumps(result, indent=2))

    # Exit with non-zero if there are fixable or unknown warnings
    if result["data"]["fixable"] > 0 or result["data"]["unknown"] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
