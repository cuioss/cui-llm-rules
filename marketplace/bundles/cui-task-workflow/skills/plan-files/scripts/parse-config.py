#!/usr/bin/env python3
"""
Parse config.toon or config.md and extract structured configuration data.

Usage:
    python3 parse-config.py <config-file>
    python3 parse-config.py <plan-directory>
    python3 parse-config.py --help

Output: JSON with configuration structure.

Supports both TOON format (.toon) and legacy markdown format (.md).
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_toon(content: str) -> dict:
    """Parse TOON format config (key: value pairs)."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        # Parse key: value
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            if value:  # Only add non-empty values
                result[key] = value
    return result


def parse_plan_type_md(content: str) -> str:
    """Extract plan type from markdown config."""
    match = re.search(r'\*\*Plan Type\*\*:\s*(\w+)', content)
    return match.group(1).lower() if match else ''


def parse_table(content: str, section_name: str) -> dict:
    """Parse a key-value table from a markdown section."""
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


def find_config_file(path: Path) -> Path:
    """Find config file, preferring .toon over .md."""
    if path.is_file():
        return path

    # If directory, look for config.toon first, then config.md
    if path.is_dir():
        toon_file = path / 'config.toon'
        if toon_file.exists():
            return toon_file
        md_file = path / 'config.md'
        if md_file.exists():
            return md_file

    return path  # Return original for error handling


def parse_config_toon(content: str) -> dict:
    """Parse TOON format and return structured data."""
    raw = parse_toon(content)

    # Extract with defaults
    plan_type = raw.get('plan_type', '').lower()
    technology = raw.get('technology', 'none').lower()
    build_system = raw.get('build_system', 'none').lower()
    compatibility = raw.get('compatibility', 'deprecations').lower()
    commit_strategy = raw.get('commit_strategy', 'fine-granular').lower()
    finalizing = raw.get('finalizing', 'pr-workflow').lower()
    branch = raw.get('branch', '')
    issue = raw.get('issue', 'none')
    issue_url = raw.get('issue_url', '')

    # Parse issue if it's a URL
    issue_id = issue
    if issue and issue.startswith('http'):
        issue_url = issue
        # Extract issue ID from URL (e.g., /issues/123)
        match = re.search(r'/issues?/(\d+)', issue)
        if match:
            issue_id = f'#{match.group(1)}'

    return {
        'configuration': {
            'plan_type': plan_type,
            'technology': technology,
            'build_system': build_system,
            'compatibility': compatibility,
            'commit_strategy': commit_strategy,
            'finalizing': finalizing,
            'branch': branch,
            'issue': issue_id if issue_id and issue_id != 'none' else 'none',
            'issue_url': issue_url
        },
        'raw': raw,
        'validation': {
            'has_plan_type': bool(plan_type),
            'has_technology': bool(technology and technology != 'none'),
            'has_build_system': bool(build_system and build_system != 'none'),
            'has_branch': bool(branch),
            'has_issue': bool(issue_id and issue_id != 'none'),
            'is_complete': bool(plan_type and branch)
        },
        'format': 'toon'
    }


def parse_config_md(content: str) -> dict:
    """Parse markdown format and return structured data."""
    plan_type = parse_plan_type_md(content)
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
        },
        'format': 'markdown'
    }


def parse_config(config_path: Path) -> dict:
    """Parse config file and return structured data."""
    config_file = find_config_file(config_path)

    if not config_file.exists():
        return {
            'error': {
                'type': 'file_not_found',
                'message': f'Config file not found: {config_path}'
            }
        }

    content = config_file.read_text()

    # Determine format by extension
    if config_file.suffix == '.toon':
        return parse_config_toon(content)
    else:
        return parse_config_md(content)


def main():
    parser = argparse.ArgumentParser(
        description='Parse config.toon or config.md and extract structured configuration.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supports both TOON format (.toon) and legacy markdown format (.md).
When given a directory, prefers config.toon over config.md.

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
  "validation": {...},
  "format": "toon|markdown"
}
"""
    )
    parser.add_argument('config_file', help='Path to config file or plan directory')

    args = parser.parse_args()

    config_path = Path(args.config_file)
    result = parse_config(config_path)

    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
