#!/usr/bin/env python3
"""
Categorize fixable issues as safe (auto-apply) or risky (require confirmation).

Uses the categorization patterns from cui-fix-workflow to determine
which fixes can be applied automatically vs which need user approval.

Usage:
    categorize-fixes.py <extracted_issues_json>
    cat extracted.json | categorize-fixes.py -

Output: JSON with {safe: [...], risky: [...]}
"""

import json
import sys
import argparse

# Safe fix types - can be auto-applied without user confirmation
# These are mechanical fixes that don't risk losing information
SAFE_FIX_TYPES = {
    # Frontmatter fixes
    "missing-frontmatter",
    "invalid-yaml",
    "missing-name-field",
    "missing-description-field",
    "missing-tools-field",
    "array-syntax-tools",

    # Formatting fixes
    "trailing-whitespace",
    "improper-indentation",
    "missing-blank-line-before-list",
}

# Risky fix types - require user confirmation
# These may involve judgment calls or structural changes
RISKY_FIX_TYPES = {
    # Tool declaration changes
    "unused-tool-declared",      # Might be intentionally declared for future use
    "tool-not-declared",         # Adding tools changes component capabilities

    # Architectural violations
    "rule-6-violation",          # Task tool removal affects component design
    "rule-7-violation",          # Maven pattern changes affect build logic
    "pattern-22-violation",      # Self-update pattern needs restructuring

    # Content changes
    "backup-file-pattern",       # Might be intentional documentation
    "ci-rule-self-update",       # Continuous improvement section changes
}


def categorize_fix(issue: dict) -> str:
    """
    Categorize a single issue as 'safe' or 'risky'.

    Args:
        issue: Issue dict with 'type' field

    Returns:
        'safe' or 'risky'
    """
    issue_type = issue.get("type", "")

    if issue_type in SAFE_FIX_TYPES:
        return "safe"
    elif issue_type in RISKY_FIX_TYPES:
        return "risky"
    else:
        # Default to risky for unknown types (safer approach)
        return "risky"


def categorize_issues(extracted: dict) -> dict:
    """
    Categorize all fixable issues into safe and risky categories.

    Args:
        extracted: Output from extract-fixable-issues.py

    Returns:
        Dict with categorized issues
    """
    issues = extracted.get("fixable_issues", [])

    safe_fixes = []
    risky_fixes = []

    for issue in issues:
        category = categorize_fix(issue)
        if category == "safe":
            safe_fixes.append(issue)
        else:
            risky_fixes.append(issue)

    return {
        "safe": safe_fixes,
        "risky": risky_fixes,
        "summary": {
            "safe_count": len(safe_fixes),
            "risky_count": len(risky_fixes),
            "total_count": len(issues)
        },
        "source_bundle": extracted.get("source_bundle", "unknown")
    }


def main():
    parser = argparse.ArgumentParser(
        description="Categorize fixable issues as safe or risky"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="-",
        help="Path to extracted issues JSON, or '-' for stdin"
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
                "safe": [],
                "risky": [],
                "summary": {
                    "safe_count": 0,
                    "risky_count": 0,
                    "total_count": 0
                },
                "error": None
            }
            print(json.dumps(result, indent=2))
            return 0

        # Parse JSON
        try:
            extracted = json.loads(content)
        except json.JSONDecodeError as e:
            error_result = {
                "error": f"Invalid JSON: {str(e)}",
                "safe": [],
                "risky": [],
                "summary": {"safe_count": 0, "risky_count": 0, "total_count": 0}
            }
            print(json.dumps(error_result, indent=2))
            return 1

        # Categorize issues
        result = categorize_issues(extracted)
        result["error"] = None

        # Output JSON
        print(json.dumps(result, indent=2))
        return 0

    except FileNotFoundError:
        error_result = {
            "error": f"File not found: {args.input_file}",
            "safe": [],
            "risky": [],
            "summary": {"safe_count": 0, "risky_count": 0, "total_count": 0}
        }
        print(json.dumps(error_result, indent=2))
        return 1
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}",
            "safe": [],
            "risky": [],
            "summary": {"safe_count": 0, "risky_count": 0, "total_count": 0}
        }
        print(json.dumps(error_result, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
