#!/usr/bin/env python3
"""
Create task breakdown from issue content.

Analyzes issue content and generates a structured task breakdown
with dependencies, acceptance criteria, and references.

Usage:
    create-task-breakdown.py <issue-file> [--output <file>]
    create-task-breakdown.py --help

Arguments:
    issue-file    Path to issue file (markdown) or JSON with issue content

Options:
    --output      Output file path (default: stdout)
    --help        Show this help message

Output:
    JSON object with task breakdown structure:
    {
        "issue": { "title": "...", "source": "..." },
        "tasks": [
            {
                "id": 1,
                "name": "...",
                "goal": "...",
                "references": [...],
                "acceptance_criteria": [...],
                "dependencies": []
            }
        ],
        "total_tasks": N
    }
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create task breakdown from issue content"
    )
    parser.add_argument(
        "issue_file",
        help="Path to issue file (markdown or JSON)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)"
    )
    return parser.parse_args()


def extract_title(content: str) -> str:
    """Extract issue title from markdown content."""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled Issue"


def extract_sections(content: str) -> dict:
    """Extract sections from markdown content."""
    sections = {}
    current_section = None
    current_content = []

    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip().lower()
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def extract_checklist_items(content: str) -> list:
    """Extract checklist items from markdown content."""
    items = []
    pattern = r'- \[ \] (.+)'
    for match in re.finditer(pattern, content):
        items.append(match.group(1).strip())
    return items


def identify_task_categories(sections: dict) -> list:
    """Identify task categories based on section content."""
    categories = []

    # Check for requirements
    if 'requirements' in sections or 'functional requirements' in sections:
        categories.append('implementation')

    # Check for acceptance criteria
    if 'acceptance criteria' in sections:
        categories.append('verification')

    # Check for edge cases
    if 'edge cases' in sections:
        categories.append('edge_case_handling')

    # Check for documentation
    if any(word in str(sections).lower() for word in ['documentation', 'readme', 'javadoc']):
        categories.append('documentation')

    # Always include testing
    categories.append('testing')

    return categories


def generate_tasks(title: str, sections: dict) -> list:
    """Generate task breakdown from analyzed sections."""
    tasks = []
    task_id = 0

    # Task 1: Research and understand
    task_id += 1
    tasks.append({
        "id": task_id,
        "name": "Research and understand requirements",
        "goal": f"Fully understand the requirements for: {title}",
        "references": [
            {"type": "issue", "location": "Full issue content"}
        ],
        "acceptance_criteria": [
            "All requirements understood",
            "Technical approach identified",
            "Dependencies mapped"
        ],
        "dependencies": []
    })

    # Task 2+: Implementation tasks based on requirements
    requirements = sections.get('requirements', sections.get('functional requirements', ''))
    if requirements:
        req_items = extract_checklist_items(requirements)
        if not req_items:
            # Try to extract numbered items
            req_pattern = r'\d+\.\s+\*\*(.+?)\*\*'
            req_items = re.findall(req_pattern, requirements)

        for req in req_items[:5]:  # Limit to 5 implementation tasks
            task_id += 1
            tasks.append({
                "id": task_id,
                "name": f"Implement: {req[:50]}{'...' if len(req) > 50 else ''}",
                "goal": f"Complete implementation of {req}",
                "references": [
                    {"type": "issue_section", "location": "Requirements"}
                ],
                "acceptance_criteria": [
                    f"{req} is fully implemented",
                    "Code follows project standards",
                    "Unit tests added"
                ],
                "dependencies": [1] if task_id == 2 else [task_id - 1]
            })

    # Testing task
    task_id += 1
    tasks.append({
        "id": task_id,
        "name": "Add comprehensive tests",
        "goal": "Achieve >= 80% test coverage for new code",
        "references": [
            {"type": "test_pattern", "location": "Existing test files"}
        ],
        "acceptance_criteria": [
            "Unit tests cover all new methods",
            "Integration tests if applicable",
            "Test coverage >= 80%",
            "All tests pass"
        ],
        "dependencies": list(range(2, task_id))
    })

    # Documentation task
    task_id += 1
    tasks.append({
        "id": task_id,
        "name": "Update documentation",
        "goal": "Document all new functionality",
        "references": [
            {"type": "documentation", "location": "README.md, JavaDoc"}
        ],
        "acceptance_criteria": [
            "JavaDoc on all public APIs",
            "README updated if needed",
            "Usage examples included"
        ],
        "dependencies": [task_id - 1]
    })

    return tasks


def process_issue(file_path: str) -> dict:
    """Process issue file and generate task breakdown."""
    path = Path(file_path)

    if not path.exists():
        return {
            "error": f"File not found: {file_path}",
            "status": "failure"
        }

    content = path.read_text()

    # Check if JSON input
    if path.suffix == '.json':
        try:
            data = json.loads(content)
            title = data.get('title', 'Untitled')
            content = data.get('body', data.get('description', ''))
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON file",
                "status": "failure"
            }
    else:
        title = extract_title(content)

    sections = extract_sections(content)
    tasks = generate_tasks(title, sections)

    return {
        "issue": {
            "title": title,
            "source": str(path)
        },
        "tasks": tasks,
        "total_tasks": len(tasks),
        "status": "success"
    }


def main():
    """Main entry point."""
    args = parse_args()

    result = process_issue(args.issue_file)

    output = json.dumps(result, indent=2)

    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
