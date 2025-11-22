#!/usr/bin/env python3
"""
Validate acceptance criteria for completed tasks.

Checks whether acceptance criteria are met based on verification methods
and project state.

Usage:
    validate-acceptance.py <plan-file> [--task <id>]
    validate-acceptance.py --help

Arguments:
    plan-file    Path to plan markdown file

Options:
    --task       Specific task ID to validate (default: most recently completed)
    --help       Show this help message

Output:
    JSON object with validation results:
    {
        "task_id": N,
        "task_name": "...",
        "criteria": [
            {
                "description": "...",
                "status": "passed|failed|not_verifiable",
                "verification_method": "grep|file_exists|coverage|manual",
                "details": "..."
            }
        ],
        "overall_status": "all_passed|some_failed|not_verifiable"
    }
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate acceptance criteria for tasks"
    )
    parser.add_argument(
        "plan_file",
        help="Path to plan markdown file"
    )
    parser.add_argument(
        "--task",
        type=int,
        help="Specific task ID to validate"
    )
    return parser.parse_args()


def extract_task(content: str, task_id: Optional[int] = None) -> Optional[dict]:
    """Extract specific task or find most recently completed task."""
    task_pattern = r'### Task (\d+): (.+?)(?=\n)'
    task_matches = list(re.finditer(task_pattern, content))

    tasks = []
    for i, match in enumerate(task_matches):
        tid = int(match.group(1))
        name = match.group(2).strip()

        # Get task content
        start = match.end()
        end = task_matches[i + 1].start() if i + 1 < len(task_matches) else len(content)
        task_content = content[start:end]

        # Check if completed
        checklist = list(re.finditer(r'- \[([ x])\]', task_content))
        is_completed = all(m.group(1) == 'x' for m in checklist) if checklist else False

        # Extract acceptance criteria section
        ac_pattern = r'\*\*Acceptance Criteria:\*\*\n(.*?)(?=\n\n|\n---|\Z)'
        ac_match = re.search(ac_pattern, task_content, re.DOTALL)
        criteria = []
        if ac_match:
            for line in ac_match.group(1).split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    criteria.append(line[2:])

        tasks.append({
            "id": tid,
            "name": name,
            "is_completed": is_completed,
            "criteria": criteria,
            "content": task_content
        })

    if task_id:
        for task in tasks:
            if task["id"] == task_id:
                return task
        return None

    # Find most recently completed task
    completed = [t for t in tasks if t["is_completed"]]
    return completed[-1] if completed else None


def infer_verification_method(criterion: str) -> str:
    """Infer verification method from criterion text."""
    criterion_lower = criterion.lower()

    if any(word in criterion_lower for word in ['coverage', '%', 'percent']):
        return "coverage_report"
    elif any(word in criterion_lower for word in ['exists', 'created', 'file']):
        return "file_exists"
    elif any(word in criterion_lower for word in ['test', 'pass']):
        return "test_run"
    elif any(word in criterion_lower for word in ['javadoc', 'documentation', 'comment']):
        return "grep"
    elif any(word in criterion_lower for word in ['implemented', 'method', 'class', 'field']):
        return "grep"
    else:
        return "manual"


def validate_criterion(criterion: str, task_content: str) -> dict:
    """Validate a single acceptance criterion."""
    method = infer_verification_method(criterion)

    # For this script, we provide structure for Claude to verify
    # Actual verification happens at Claude level with appropriate tools

    return {
        "description": criterion,
        "verification_method": method,
        "status": "not_verified",
        "verification_instruction": get_verification_instruction(criterion, method),
        "details": "Requires Claude verification with appropriate tools"
    }


def get_verification_instruction(criterion: str, method: str) -> str:
    """Get instruction for how to verify this criterion."""
    instructions = {
        "coverage_report": "Check JaCoCo report in target/site/jacoco/index.html or jacoco.xml",
        "file_exists": "Use Glob tool to verify file exists at expected path",
        "test_run": "Run tests and verify all pass (exit code 0, no failures)",
        "grep": "Use Grep tool to search for expected code patterns",
        "manual": "Requires manual review by Claude"
    }
    return instructions.get(method, "Manual verification required")


def validate_acceptance(file_path: str, task_id: Optional[int] = None) -> dict:
    """Validate acceptance criteria for a task."""
    path = Path(file_path)

    if not path.exists():
        return {
            "error": f"File not found: {file_path}",
            "status": "failure"
        }

    content = path.read_text()
    task = extract_task(content, task_id)

    if not task:
        return {
            "error": "No completed task found" if not task_id else f"Task {task_id} not found",
            "status": "failure"
        }

    # Validate each criterion
    validated_criteria = []
    for criterion in task["criteria"]:
        validated_criteria.append(validate_criterion(criterion, task["content"]))

    # Determine overall status
    statuses = [c["status"] for c in validated_criteria]
    if all(s == "passed" for s in statuses):
        overall = "all_passed"
    elif any(s == "failed" for s in statuses):
        overall = "some_failed"
    else:
        overall = "not_verified"

    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "criteria": validated_criteria,
        "criteria_count": len(validated_criteria),
        "overall_status": overall,
        "status": "success"
    }


def main():
    """Main entry point."""
    args = parse_args()

    result = validate_acceptance(args.plan_file, args.task)

    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
