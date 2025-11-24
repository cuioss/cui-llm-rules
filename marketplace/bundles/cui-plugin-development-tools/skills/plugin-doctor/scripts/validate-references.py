#!/usr/bin/env python3
"""
Validates plugin references in agent/command/skill markdown files.
Extracts references with pre-filtering to reduce false positives.

Usage: validate-references.py <file_path>
Output: JSON with detected references
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set


def show_help():
    """Display help message."""
    help_text = """
Usage: validate-references.py <file_path>

Validates plugin references in agent/command/skill markdown files.
Uses pre-filtering to reduce false positives from documentation examples.

Arguments:
  file_path    Path to the markdown file to analyze

Output: JSON with detected references including:
  - file_type: Detected component type (agent, command, skill)
  - total_lines: Total lines in file
  - references: Array of detected references with type, line, and raw_text
  - pre_filter.excluded_lines_count: Lines excluded by pre-filtering
  - pre_filter.exclusion_rate: Percentage of lines excluded

Reference types detected:
  - SlashCommand: /command-name invocations
  - Task: subagent_type declarations
  - Skill: Skill: bundle:skill-name invocations

Exit codes:
  0 - Success
  1 - Error (missing argument, file not found)

Examples:
  validate-references.py marketplace/bundles/cui-java-expert/agents/java-analyzer.md
  validate-references.py ./commands/my-command.md
"""
    print(help_text.strip())
    sys.exit(0)


def detect_file_type(file_path: str) -> str:
    """Detect if file is agent, command, or skill."""
    if "/agents/" in file_path:
        return "agent"
    elif "/commands/" in file_path:
        return "command"
    elif "/skills/" in file_path:
        return "skill"
    return "unknown"


def pre_filter_documentation_lines(content: str) -> Set[int]:
    """
    Pre-filter documentation lines to exclude from reference detection.
    Returns set of line numbers (0-indexed) to exclude.

    Filters:
    - Example/Usage/Demonstration sections
    - Workflow step Markdown bold label lines (- **Label**: value)
    - Pseudo-YAML documentation (Task:/Agent:/Command: with indented fields)
    - CONTINUOUS IMPROVEMENT RULE instructions
    - RELATED/SEE ALSO sections
    """
    lines = content.split('\n')
    excluded = set()

    in_example = False
    in_workflow_step = False
    in_related = False
    example_level = 0

    for i, line in enumerate(lines):
        # Check for Example/Usage/Demonstration sections
        example_match = re.match(r'^(#{2,3})\s+(Example|Usage|Demonstration|USAGE|EXAMPLES)', line, re.IGNORECASE)
        if example_match:
            in_example = True
            example_level = len(example_match.group(1))
            excluded.add(i)
            continue

        # Check if we're exiting example section (new header at same/higher level)
        if in_example:
            header_match = re.match(r'^(#{2,3})\s+', line)
            if header_match and len(header_match.group(1)) <= example_level:
                in_example = False
            else:
                excluded.add(i)
                continue

        # Check for workflow step with Markdown list patterns
        workflow_match = re.match(r'^(#{2,3})\s+Step\s+\d+:', line)
        if workflow_match:
            in_workflow_step = True
            excluded.add(i)
            continue

        # Within workflow steps, exclude Markdown bold label lines
        if in_workflow_step:
            # Check for new header (exit workflow step)
            header_match = re.match(r'^#{2,3}\s+', line)
            if header_match:
                in_workflow_step = False
            # Exclude lines with Markdown bold labels: - **Label**: value
            elif re.match(r'^\s*-\s+\*\*[^*]+\*\*:', line):
                excluded.add(i)
                continue

        # Check for CONTINUOUS IMPROVEMENT RULE instructions
        if re.search(r'caller can then invoke|invoke `/plugin-update', line, re.IGNORECASE):
            excluded.add(i)
            continue

        # Check for pseudo-YAML documentation (Task:, Agent:, Command: labels)
        if re.match(r'^(Task|Agent|Command):$', line.strip()):
            excluded.add(i)
            # Check next lines for indentation (part of pseudo-YAML)
            for j in range(i + 1, min(i + 20, len(lines))):
                if lines[j].startswith((' ', '\t')):
                    excluded.add(j)
                elif lines[j].strip():  # Non-empty, non-indented = end of block
                    break
            continue

        # Check for RELATED or SEE ALSO sections
        if re.match(r'^#{2,3}\s+(RELATED|SEE ALSO|Related|See Also)', line, re.IGNORECASE):
            in_related = True
            excluded.add(i)
            continue

        if in_related:
            # Exit on next header
            if re.match(r'^#{2,3}\s+', line):
                in_related = False
            else:
                excluded.add(i)
                continue

    return excluded


def extract_references(content: str, excluded_lines: Set[int]) -> List[Dict]:
    """
    Extract plugin references from content.
    Returns list of references with line numbers and types.

    Detects:
    - SlashCommand: /command-name
    - Task: subagent_type: "agent-name"
    - Skill: Skill: bundle:skill-name
    """
    lines = content.split('\n')
    references = []

    # Pattern 1: SlashCommand invocations
    slash_pattern = re.compile(r'SlashCommand:\s*/([a-z0-9:-]+)')

    # Pattern 2: Task subagent_type
    task_pattern = re.compile(r'subagent_type[:\s]+["\']?([a-z0-9:-]+)["\']?')

    # Pattern 3: Skill invocations
    skill_pattern = re.compile(r'Skill:\s*([a-z0-9:-]+)')

    for i, line in enumerate(lines):
        # Skip excluded lines
        if i in excluded_lines:
            continue

        # Check SlashCommand
        for match in slash_pattern.finditer(line):
            references.append({
                "line": i + 1,  # 1-indexed for display
                "type": "SlashCommand",
                "reference": f"/{match.group(1)}",
                "raw_text": match.group(0)
            })

        # Check Task
        for match in task_pattern.finditer(line):
            references.append({
                "line": i + 1,
                "type": "Task",
                "reference": match.group(1),
                "raw_text": match.group(0)
            })

        # Check Skill
        for match in skill_pattern.finditer(line):
            references.append({
                "line": i + 1,
                "type": "Skill",
                "reference": match.group(1),
                "raw_text": match.group(0)
            })

    return references


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "File path required. Use --help for usage."}), file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] in ("-h", "--help"):
        show_help()

    file_path = sys.argv[1]

    if not Path(file_path).is_file():
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(1)

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(json.dumps({"error": f"Failed to read file: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    # Detect file type
    file_type = detect_file_type(file_path)

    # Pre-filter documentation lines
    excluded_lines = pre_filter_documentation_lines(content)

    # Extract references
    references = extract_references(content, excluded_lines)

    # Calculate statistics
    total_lines = len(content.split('\n'))
    excluded_count = len(excluded_lines)
    exclusion_rate = (excluded_count / total_lines * 100) if total_lines > 0 else 0.0

    # Output JSON
    result = {
        "file_path": file_path,
        "file_type": file_type,
        "total_lines": total_lines,
        "references": references,
        "pre_filter": {
            "excluded_lines_count": excluded_count,
            "exclusion_rate": round(exclusion_rate, 1)
        }
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
