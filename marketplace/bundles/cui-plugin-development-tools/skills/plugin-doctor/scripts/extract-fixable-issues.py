#!/usr/bin/env python3
"""
Extract fixable issues from diagnosis JSON output.

Filters diagnosis results to only include issues that can be fixed
by the plugin-fix skill's automated workflows.

Usage:
    extract-fixable-issues.py <diagnosis_json_file>
    cat diagnosis.json | extract-fixable-issues.py -

Output: JSON with only fixable issues
"""

import json
import sys
import argparse

# Issue types that can be fixed automatically or with user confirmation
FIXABLE_ISSUE_TYPES = {
    # Safe fixes (auto-applicable)
    "missing-frontmatter",
    "invalid-yaml",
    "missing-name-field",
    "missing-description-field",
    "missing-tools-field",
    "array-syntax-tools",
    "trailing-whitespace",
    "improper-indentation",
    "missing-blank-line-before-list",

    # Risky fixes (require confirmation)
    "unused-tool-declared",
    "tool-not-declared",
    "rule-6-violation",
    "rule-7-violation",
    "pattern-22-violation",
    "backup-file-pattern",
    "ci-rule-self-update",
}


def is_fixable(issue_type: str) -> bool:
    """Check if an issue type is fixable by the plugin-fix skill."""
    return issue_type in FIXABLE_ISSUE_TYPES


def extract_fixable_issues(diagnosis: dict) -> dict:
    """
    Extract only fixable issues from diagnosis results.

    Args:
        diagnosis: Full diagnosis JSON from plugin-diagnose

    Returns:
        Dict with only fixable issues
    """
    issues = diagnosis.get("issues", [])

    fixable_issues = []
    for issue in issues:
        issue_type = issue.get("type", "")

        # Check both the type field and the fixable flag if present
        if is_fixable(issue_type) or issue.get("fixable", False):
            fixable_issues.append(issue)

    return {
        "fixable_issues": fixable_issues,
        "total_count": len(fixable_issues),
        "source_bundle": diagnosis.get("bundle", "unknown"),
        "original_total": len(issues),
        "filtered_count": len(issues) - len(fixable_issues)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract fixable issues from diagnosis JSON"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="-",
        help="Path to diagnosis JSON file, or '-' for stdin"
    )

    args = parser.parse_args()

    try:
        # Read input
        if args.input_file == "-":
            content = sys.stdin.read()
        else:
            with open(args.input_file, "r", encoding="utf-8") as f:
                content = f.read()

        # Handle empty input
        if not content.strip():
            result = {
                "fixable_issues": [],
                "total_count": 0,
                "source_bundle": "unknown",
                "original_total": 0,
                "filtered_count": 0,
                "error": None
            }
            print(json.dumps(result, indent=2))
            return 0

        # Parse JSON
        try:
            diagnosis = json.loads(content)
        except json.JSONDecodeError as e:
            error_result = {
                "error": f"Invalid JSON: {str(e)}",
                "fixable_issues": [],
                "total_count": 0
            }
            print(json.dumps(error_result, indent=2))
            return 1

        # Extract fixable issues
        result = extract_fixable_issues(diagnosis)
        result["error"] = None

        # Output JSON
        print(json.dumps(result, indent=2))
        return 0

    except FileNotFoundError:
        error_result = {
            "error": f"File not found: {args.input_file}",
            "fixable_issues": [],
            "total_count": 0
        }
        print(json.dumps(error_result, indent=2))
        return 1
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}",
            "fixable_issues": [],
            "total_count": 0
        }
        print(json.dumps(error_result, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
