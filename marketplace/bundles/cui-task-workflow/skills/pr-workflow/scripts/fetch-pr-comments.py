#!/usr/bin/env python3
"""
Fetch PR review comments from GitHub.

Uses gh CLI to fetch review comments for a PR and returns
structured JSON output for triage.

Usage:
    fetch-pr-comments.py [--pr <number>]
    fetch-pr-comments.py --help

Options:
    --pr         PR number (default: current branch's PR)
    --help       Show this help message

Output:
    JSON object with PR comments:
    {
        "pr_number": N,
        "comments": [
            {
                "id": "...",
                "author": "...",
                "body": "...",
                "path": "...",
                "line": N,
                "resolved": true/false
            }
        ],
        "total_comments": N
    }

Note:
    Requires gh CLI to be installed and authenticated.
"""

import argparse
import json
import subprocess
import sys


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch PR review comments from GitHub"
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="PR number (default: current branch's PR)"
    )
    return parser.parse_args()


def run_gh_command(args: list) -> tuple:
    """Run gh CLI command and return stdout, stderr, return code."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        return "", "gh CLI not installed or not in PATH", 1


def get_current_pr_number() -> int:
    """Get PR number for current branch."""
    stdout, stderr, code = run_gh_command([
        "pr", "view", "--json", "number", "--jq", ".number"
    ])

    if code != 0:
        return None

    try:
        return int(stdout.strip())
    except ValueError:
        return None


def fetch_comments(pr_number: int) -> dict:
    """Fetch review comments for a PR."""
    # Fetch review threads with comments
    stdout, stderr, code = run_gh_command([
        "pr", "view", str(pr_number),
        "--json", "reviewThreads",
        "--jq", ".reviewThreads"
    ])

    if code != 0:
        return {
            "error": f"Failed to fetch PR: {stderr}",
            "status": "failure"
        }

    try:
        threads = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        return {
            "error": f"Failed to parse gh output: {stdout}",
            "status": "failure"
        }

    # Extract comments from threads
    comments = []
    for thread in threads:
        if "comments" not in thread:
            continue

        for comment in thread["comments"]:
            comments.append({
                "id": comment.get("id", "unknown"),
                "author": comment.get("author", {}).get("login", "unknown"),
                "body": comment.get("body", ""),
                "path": comment.get("path"),
                "line": comment.get("line"),
                "resolved": thread.get("isResolved", False)
            })

    return {
        "pr_number": pr_number,
        "comments": comments,
        "total_comments": len(comments),
        "unresolved_count": sum(1 for c in comments if not c["resolved"]),
        "status": "success"
    }


def main():
    """Main entry point."""
    args = parse_args()

    # Determine PR number
    pr_number = args.pr
    if not pr_number:
        pr_number = get_current_pr_number()
        if not pr_number:
            print(json.dumps({
                "error": "No PR found for current branch. Use --pr to specify.",
                "status": "failure"
            }, indent=2))
            return 1

    result = fetch_comments(pr_number)

    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
