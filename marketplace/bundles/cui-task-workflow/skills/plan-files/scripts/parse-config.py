#!/usr/bin/env python3
"""
Parse config.md and extract structured configuration data.

Usage:
    python3 parse-config.py <config-file>
    python3 parse-config.py --help

Output: JSON with configuration structure.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_plan_type(content: str) -> str:
    """Extract plan type from config."""
    match = re.search(r'\*\*Plan Type\*\*:\s*(\w+)', content)
    return match.group(1).lower() if match else ''


def parse_table(content: str, section_name: str) -> dict:
    """Parse a key-value table from a section."""
    result = {}

    # Find the section
    section_pattern = rf'##\s*{section_name}\s*\n(.*?)(?=\n##|\n---|\Z)'
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    if not section_match:
        return result

    section_content = section_match.group(1)

    # Find table rows (| Property | Value |)
    row_pattern = r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
    matches = re.finditer(row_pattern, section_content)

    for match in matches:
        key = match.group(1).strip()
        value = match.group(2).strip()

        # Skip header row
        if key.lower() in ['property', 'key', '---', '-']:
            continue
        if value.lower() in ['value', '---', '-']:
            continue

        # Normalize key to snake_case
        key_normalized = key.lower().replace(' ', '_')
        result[key_normalized] = value

    return result


def parse_config(config_file: Path) -> dict:
    """Parse config.md and return structured data."""
    if not config_file.exists():
        return {
            'error': {
                'type': 'file_not_found',
                'message': f'Config file not found: {config_file}'
            }
        }

    content = config_file.read_text()

    plan_type = parse_plan_type(content)
    build_config = parse_table(content, 'Build Configuration')
    workflow_config = parse_table(content, 'Workflow Configuration')
    context = parse_table(content, 'Context')

    # Normalize values
    technology = build_config.get('technology', 'none').lower()
    build_system = build_config.get('build_system', 'none').lower()
    compatibility = workflow_config.get('compatibility', 'deprecations').lower()
    commit_strategy = workflow_config.get('commit_strategy', 'fine-granular').lower()
    finalizing = workflow_config.get('finalizing', 'pr-workflow').lower()
    branch = context.get('branch', '')
    issue = context.get('issue', 'none')

    # Parse issue URL if present
    issue_url = ''
    issue_id = ''
    if issue and issue != 'none':
        # Check for markdown link format: [ID](URL)
        link_match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', issue)
        if link_match:
            issue_id = link_match.group(1)
            issue_url = link_match.group(2)
        else:
            issue_id = issue

    return {
        'configuration': {
            'plan_type': plan_type,
            'technology': technology,
            'build_system': build_system,
            'compatibility': compatibility,
            'commit_strategy': commit_strategy,
            'finalizing': finalizing,
            'branch': branch,
            'issue': issue_id if issue_id else 'none',
            'issue_url': issue_url
        },
        'raw': {
            'build_configuration': build_config,
            'workflow_configuration': workflow_config,
            'context': context
        },
        'validation': {
            'has_plan_type': bool(plan_type),
            'has_technology': bool(technology and technology != 'none'),
            'has_build_system': bool(build_system and build_system != 'none'),
            'has_branch': bool(branch),
            'has_issue': bool(issue_id and issue_id != 'none'),
            'is_complete': bool(plan_type and branch)
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Parse config.md and extract structured configuration.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "configuration": {
    "plan_type": "implementation",
    "technology": "java",
    "build_system": "maven",
    "compatibility": "deprecations",
    "commit_strategy": "fine-granular",
    "finalizing": "pr-workflow",
    "branch": "feature/jwt-auth",
    "issue": "PROJ-123",
    "issue_url": "https://..."
  },
  "raw": {...},
  "validation": {...}
}
"""
    )
    parser.add_argument('config_file', help='Path to config.md file')

    args = parser.parse_args()

    config_file = Path(args.config_file)
    result = parse_config(config_file)

    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
