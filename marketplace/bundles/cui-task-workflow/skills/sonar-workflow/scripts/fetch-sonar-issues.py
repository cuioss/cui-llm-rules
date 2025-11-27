#!/usr/bin/env python3
"""
Fetch Sonar issues for a PR.

Retrieves issues from SonarQube API with optional filtering.
Returns structured JSON for triage.

Usage:
    fetch-sonar-issues.py --project <key> [options]
    fetch-sonar-issues.py --help

Options:
    --project    SonarQube project key (required)
    --pr         Pull request ID
    --severities Filter by severities (comma-separated: BLOCKER,CRITICAL,MAJOR,MINOR,INFO)
    --types      Filter by types (comma-separated: BUG,CODE_SMELL,VULNERABILITY)
    --help       Show this help message

Output:
    JSON object with Sonar issues:
    {
        "project_key": "...",
        "pull_request_id": "...",
        "issues": [...],
        "statistics": {
            "total_issues_fetched": N,
            "by_severity": {...},
            "by_type": {...}
        }
    }

Note:
    This script provides structure for Claude to use with
    mcp__sonarqube__search_sonar_issues_in_projects MCP tool.
"""

import argparse
import json
import sys


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch Sonar issues for a PR"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="SonarQube project key"
    )
    parser.add_argument(
        "--pr",
        help="Pull request ID"
    )
    parser.add_argument(
        "--severities",
        help="Filter by severities (comma-separated)"
    )
    parser.add_argument(
        "--types",
        help="Filter by types (comma-separated)"
    )
    return parser.parse_args()


def generate_mcp_instruction(args) -> dict:
    """Generate MCP tool invocation instruction for Claude."""
    instruction = {
        "tool": "mcp__sonarqube__search_sonar_issues_in_projects",
        "parameters": {
            "projects": [args.project]
        }
    }

    if args.pr:
        instruction["parameters"]["pullRequestId"] = args.pr

    if args.severities:
        instruction["parameters"]["severities"] = args.severities

    return instruction


def create_sample_output(args) -> dict:
    """Create sample output structure showing expected format."""
    return {
        "project_key": args.project,
        "pull_request_id": args.pr,
        "issues": [
            {
                "key": "EXAMPLE-001",
                "type": "BUG",
                "severity": "MAJOR",
                "file": "src/main/java/Example.java",
                "line": 42,
                "rule": "java:S1234",
                "message": "Example issue message",
                "_note": "This is sample structure - actual issues from MCP tool"
            }
        ],
        "statistics": {
            "total_issues_fetched": 0,
            "issues_after_filtering": 0,
            "by_severity": {},
            "by_type": {}
        },
        "mcp_instruction": generate_mcp_instruction(args),
        "status": "instruction_generated"
    }


def main():
    """Main entry point."""
    args = parse_args()

    # This script primarily generates the MCP tool instruction
    # Actual fetching is done by Claude using the MCP tool
    result = create_sample_output(args)

    print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
