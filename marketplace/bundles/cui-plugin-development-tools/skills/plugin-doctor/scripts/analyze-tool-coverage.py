#!/usr/bin/env python3
"""
analyze-tool-coverage.py

Analyzes tool declarations vs actual usage in agents and commands.

Usage:
    python3 analyze-tool-coverage.py <file_path>

Arguments:
    file_path    Path to the agent or command markdown file

Output: JSON with tool coverage analysis including:
    - tool_coverage.declared_count: Number of tools declared in frontmatter
    - tool_coverage.used_count: Number of declared tools actually used
    - tool_coverage.missing_tools: Tools used but not declared
    - tool_coverage.unused_tools: Tools declared but not used
    - tool_coverage.tool_fit_score: Score 0-100
    - tool_coverage.rating: Excellent, Good, Needs improvement, or Poor
    - critical_violations: Rule 6 (Task tool), Rule 7 (Maven), backup patterns

Exit codes:
    0 - Success
    1 - Error (missing argument, file not found, no frontmatter)
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_frontmatter(content: str) -> tuple[bool, str]:
    """Extract YAML frontmatter from content."""
    if not content.startswith('---'):
        return False, ''

    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        return True, match.group(1)
    return False, ''


def extract_content_after_frontmatter(content: str) -> str:
    """Extract content after frontmatter."""
    match = re.match(r'^---\s*\n.*?\n---\s*\n?(.*)', content, re.DOTALL)
    if match:
        return match.group(1)
    return content


def parse_declared_tools(frontmatter: str) -> list[str]:
    """Parse tools from frontmatter."""
    tools_match = re.search(r'^tools:\s*(.*)$', frontmatter, re.MULTILINE)
    if not tools_match:
        return []

    tools_line = tools_match.group(1).strip()
    # Parse comma-separated tools
    tools = [t.strip() for t in tools_line.replace(',', ' ').split() if t.strip()]
    return tools


def check_tool_usage(content: str, tool: str) -> bool:
    """Check if a tool is referenced in content (case-insensitive)."""
    return bool(re.search(re.escape(tool), content, re.IGNORECASE))


def find_missing_tools(content: str, declared_tools: list[str]) -> list[str]:
    """Find common tools used but not declared."""
    common_tools = [
        'Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash',
        'WebFetch', 'WebSearch', 'AskUserQuestion', 'TodoWrite',
        'Skill', 'Task', 'SlashCommand'
    ]

    missing = []
    declared_lower = [t.lower() for t in declared_tools]

    for tool in common_tools:
        if check_tool_usage(content, tool) and tool.lower() not in declared_lower:
            missing.append(tool)

    return missing


def calculate_fit_score(used_count: int, declared_count: int,
                        missing_count: int, unused_count: int) -> float:
    """Calculate tool fit score."""
    if declared_count == 0:
        return 0.0

    if missing_count == 0 and unused_count == 0:
        return 100.0

    if missing_count == 0:
        # Only unused tools
        return (used_count / declared_count) * 100

    # Both issues or only missing
    total_needed = used_count + missing_count
    if total_needed == 0:
        return 0.0
    return (used_count / total_needed) * 100


def get_rating(score: float) -> str:
    """Get rating based on score."""
    if score >= 90:
        return 'Excellent'
    elif score >= 70:
        return 'Good'
    elif score >= 50:
        return 'Needs improvement'
    return 'Poor'


def find_maven_calls(content: str) -> list[dict]:
    """Find Maven call patterns in content."""
    maven_calls = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        if re.search(r'Bash.*mvn|Bash.*./mvnw|Bash.*maven', line, re.IGNORECASE):
            maven_calls.append({
                'line': i,
                'text': line.strip()
            })

    return maven_calls


def find_backup_patterns(content: str) -> list[dict]:
    """Find backup file patterns in content."""
    backup_patterns = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        if re.search(r'\.backup|\.bak|\.old|\.orig', line):
            backup_patterns.append({
                'line': i,
                'pattern': line.strip()
            })

    return backup_patterns


def analyze_tool_coverage(file_path: Path) -> dict:
    """Analyze tool coverage in file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'error': f'Failed to read file: {e}'}

    # Extract frontmatter
    frontmatter_present, frontmatter = extract_frontmatter(content)
    if not frontmatter_present:
        return {'error': 'No frontmatter found'}

    # Parse declared tools
    declared_tools = parse_declared_tools(frontmatter)
    declared_count = len(declared_tools)

    # Extract content after frontmatter
    body_content = extract_content_after_frontmatter(content)

    # Check usage of declared tools
    used_tools = []
    unused_tools = []

    for tool in declared_tools:
        if check_tool_usage(body_content, tool):
            used_tools.append(tool)
        else:
            unused_tools.append(tool)

    used_count = len(used_tools)
    unused_count = len(unused_tools)

    # Find missing tools (common tools used but not declared)
    missing_tools = find_missing_tools(body_content, declared_tools)
    missing_count = len(missing_tools)

    # Calculate fit score and rating
    tool_fit_score = calculate_fit_score(used_count, declared_count, missing_count, unused_count)
    rating = get_rating(tool_fit_score)

    # Check critical violations
    has_task_tool = 'Task' in declared_tools or 'task' in [t.lower() for t in declared_tools]
    has_task_calls = bool(re.search(r'Task tool|invoke.*Task|subagent_type', body_content, re.IGNORECASE))
    maven_calls = find_maven_calls(body_content)
    backup_patterns = find_backup_patterns(body_content)

    return {
        'file_path': str(file_path),
        'tool_coverage': {
            'declared_count': declared_count,
            'used_count': used_count,
            'missing_count': missing_count,
            'unused_count': unused_count,
            'tool_fit_score': round(tool_fit_score, 1),
            'rating': rating,
            'missing_tools': missing_tools,
            'unused_tools': unused_tools
        },
        'critical_violations': {
            'has_task_tool': has_task_tool,
            'has_task_calls': has_task_calls,
            'maven_calls': maven_calls,
            'backup_file_patterns': backup_patterns
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze tool declarations vs actual usage in agents and commands"
    )
    parser.add_argument(
        'file_path',
        help="Path to the agent or command markdown file"
    )

    args = parser.parse_args()

    file_path = Path(args.file_path)

    # Validate path
    if not file_path.exists():
        print(json.dumps({'error': f'File not found: {args.file_path}'}), file=sys.stderr)
        return 1

    if not file_path.is_file():
        print(json.dumps({'error': f'Not a file: {args.file_path}'}), file=sys.stderr)
        return 1

    # Analyze file
    result = analyze_tool_coverage(file_path)

    if 'error' in result:
        print(json.dumps(result), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
