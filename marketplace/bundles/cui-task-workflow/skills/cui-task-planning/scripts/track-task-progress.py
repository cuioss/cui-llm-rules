#!/usr/bin/env python3
"""
Track task progress in plan files.

Analyzes plan file to determine current progress, identify next task,
and provide execution statistics.

Usage:
    track-task-progress.py <plan-file>
    track-task-progress.py --help

Arguments:
    plan-file    Path to plan markdown file

Output:
    JSON object with progress tracking:
    {
        "plan_file": "...",
        "current_task": { "id": N, "name": "...", "status": "in_progress" },
        "next_task": { "id": N+1, "name": "...", "status": "pending" },
        "progress": {
            "total_tasks": N,
            "completed": N,
            "in_progress": N,
            "pending": N,
            "completion_percentage": N
        },
        "checklist_progress": {
            "total_items": N,
            "completed_items": N,
            "current_task_items": { "done": N, "total": N }
        }
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
        description="Track task progress in plan files"
    )
    parser.add_argument(
        "plan_file",
        help="Path to plan markdown file"
    )
    return parser.parse_args()


def extract_tasks(content: str) -> list:
    """Extract tasks from plan markdown content."""
    tasks = []
    # Pattern: ### Task N: Name
    task_pattern = r'### Task (\d+): (.+?)(?=\n)'
    task_matches = list(re.finditer(task_pattern, content))

    for i, match in enumerate(task_matches):
        task_id = int(match.group(1))
        task_name = match.group(2).strip()

        # Find task content (between this task and next task or end)
        start = match.end()
        end = task_matches[i + 1].start() if i + 1 < len(task_matches) else len(content)
        task_content = content[start:end]

        # Extract checklist items
        checklist = []
        for item_match in re.finditer(r'- \[([ x])\] (.+)', task_content):
            done = item_match.group(1) == 'x'
            text = item_match.group(2).strip()
            checklist.append({"item": text, "done": done})

        # Determine task status
        if not checklist:
            status = "pending"
        elif all(item["done"] for item in checklist):
            status = "completed"
        elif any(item["done"] for item in checklist):
            status = "in_progress"
        else:
            status = "pending"

        tasks.append({
            "id": task_id,
            "name": task_name,
            "status": status,
            "checklist": checklist
        })

    return tasks


def find_current_task(tasks: list) -> Optional[dict]:
    """Find the current task being worked on."""
    for task in tasks:
        if task["status"] == "in_progress":
            return task
    return None


def find_next_task(tasks: list) -> Optional[dict]:
    """Find the next pending task."""
    for task in tasks:
        if task["status"] == "pending":
            return task
    return None


def calculate_progress(tasks: list) -> dict:
    """Calculate overall progress statistics."""
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "completed")
    in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
    pending = sum(1 for t in tasks if t["status"] == "pending")

    percentage = (completed / total * 100) if total > 0 else 0

    return {
        "total_tasks": total,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "completion_percentage": round(percentage, 1)
    }


def calculate_checklist_progress(tasks: list, current_task: Optional[dict]) -> dict:
    """Calculate checklist progress statistics."""
    total_items = 0
    completed_items = 0

    for task in tasks:
        for item in task["checklist"]:
            total_items += 1
            if item["done"]:
                completed_items += 1

    current_task_items = {"done": 0, "total": 0}
    if current_task:
        current_task_items["total"] = len(current_task["checklist"])
        current_task_items["done"] = sum(1 for i in current_task["checklist"] if i["done"])

    return {
        "total_items": total_items,
        "completed_items": completed_items,
        "current_task_items": current_task_items
    }


def track_progress(file_path: str) -> dict:
    """Track progress in plan file."""
    path = Path(file_path)

    if not path.exists():
        return {
            "error": f"File not found: {file_path}",
            "status": "failure"
        }

    content = path.read_text()
    tasks = extract_tasks(content)

    if not tasks:
        return {
            "error": "No tasks found in plan file",
            "status": "failure",
            "plan_file": str(path)
        }

    current_task = find_current_task(tasks)
    next_task = find_next_task(tasks)

    # If no current task but there's a pending one, that's the next to work on
    if not current_task and next_task:
        current_task = next_task
        next_task = find_next_task([t for t in tasks if t["id"] != current_task["id"]])

    progress = calculate_progress(tasks)
    checklist_progress = calculate_checklist_progress(tasks, current_task)

    return {
        "plan_file": str(path),
        "current_task": current_task,
        "next_task": next_task,
        "progress": progress,
        "checklist_progress": checklist_progress,
        "all_completed": progress["completed"] == progress["total_tasks"],
        "status": "success"
    }


def main():
    """Main entry point."""
    args = parse_args()

    result = track_progress(args.plan_file)

    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
