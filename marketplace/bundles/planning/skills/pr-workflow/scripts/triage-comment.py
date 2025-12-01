#!/usr/bin/env python3
"""
Triage a single PR review comment.

Analyzes comment content and determines appropriate action:
code_change, explain, or ignore.

Usage:
    triage-comment.py --comment <json>
    triage-comment.py --help

Options:
    --comment    JSON string with comment data
    --help       Show this help message

Input JSON format:
    {
        "id": "...",
        "body": "...",
        "path": "...",
        "line": N,
        "author": "..."
    }

Output:
    JSON object with triage decision:
    {
        "comment_id": "...",
        "action": "code_change|explain|ignore",
        "reason": "...",
        "priority": "high|medium|low|none",
        "suggested_implementation": "..."
    }
"""

import argparse
import json
import re
import sys


# Patterns for classification
PATTERNS = {
    "code_change": {
        "high": [
            r"security",
            r"vulnerability",
            r"injection",
            r"xss",
            r"csrf",
            r"bug",
            r"error",
            r"fix",
            r"broken",
            r"crash",
            r"null pointer",
            r"memory leak"
        ],
        "medium": [
            r"please\s+(?:add|remove|change|fix|update)",
            r"should\s+(?:be|have|use)",
            r"missing",
            r"incorrect",
            r"wrong"
        ],
        "low": [
            r"rename",
            r"variable name",
            r"naming",
            r"typo",
            r"spelling",
            r"formatting",
            r"style"
        ]
    },
    "explain": [
        r"why",
        r"explain",
        r"reasoning",
        r"rationale",
        r"how does",
        r"what is",
        r"can you clarify",
        r"\?"
    ],
    "ignore": [
        r"^lgtm",
        r"^approved",
        r"looks good",
        r"^nice",
        r"^thanks",
        r"\[bot\]",
        r"^nit:",
        r"^nitpick:"
    ]
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Triage a single PR review comment"
    )
    parser.add_argument(
        "--comment",
        required=True,
        help="JSON string with comment data"
    )
    return parser.parse_args()


def classify_comment(body: str) -> tuple:
    """Classify comment and determine action and priority."""
    body_lower = body.lower()

    # Check for ignore patterns first
    for pattern in PATTERNS["ignore"]:
        if re.search(pattern, body_lower):
            return "ignore", "none", "Automated or acknowledgment comment"

    # Check for code change patterns with priority
    for priority in ["high", "medium", "low"]:
        for pattern in PATTERNS["code_change"][priority]:
            if re.search(pattern, body_lower):
                return "code_change", priority, f"Matches {priority} priority pattern: {pattern}"

    # Check for explanation patterns
    for pattern in PATTERNS["explain"]:
        if re.search(pattern, body_lower):
            return "explain", "low", "Question or clarification request"

    # Default to code_change with low priority if none match
    if len(body) > 50:  # Substantial comment likely needs attention
        return "code_change", "low", "Substantial review comment requires attention"

    return "ignore", "none", "Brief comment with no actionable content"


def suggest_implementation(action: str, body: str, path: str, line: int) -> str:
    """Generate implementation suggestion based on action type."""
    if action == "ignore":
        return None

    if action == "explain":
        return f"Reply to comment at {path}:{line} with explanation of design decision"

    # For code_change, try to extract specific action
    body_lower = body.lower()

    if "add" in body_lower:
        return f"Add requested code/functionality at {path}:{line}"
    elif "remove" in body_lower or "delete" in body_lower:
        return f"Remove indicated code at {path}:{line}"
    elif "rename" in body_lower:
        return f"Rename as suggested at {path}:{line}"
    elif "fix" in body_lower:
        return f"Fix the issue indicated at {path}:{line}"
    else:
        return f"Review and address comment at {path}:{line}"


def triage_comment(comment: dict) -> dict:
    """Triage a single comment and return decision."""
    comment_id = comment.get("id", "unknown")
    body = comment.get("body", "")
    path = comment.get("path")
    line = comment.get("line")
    author = comment.get("author", "unknown")

    if not body:
        return {
            "comment_id": comment_id,
            "action": "ignore",
            "reason": "Empty comment body",
            "priority": "none",
            "suggested_implementation": None,
            "status": "success"
        }

    action, priority, reason = classify_comment(body)
    suggestion = suggest_implementation(action, body, path, line)

    return {
        "comment_id": comment_id,
        "author": author,
        "action": action,
        "reason": reason,
        "priority": priority,
        "location": f"{path}:{line}" if path and line else None,
        "suggested_implementation": suggestion,
        "status": "success"
    }


def main():
    """Main entry point."""
    args = parse_args()

    try:
        comment = json.loads(args.comment)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"Invalid JSON input: {e}",
            "status": "failure"
        }, indent=2))
        return 1

    result = triage_comment(comment)

    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
