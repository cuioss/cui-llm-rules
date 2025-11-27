#!/usr/bin/env python3
"""
Parse plan.md and extract structured data.

Usage:
    python3 parse-plan.py <plan-file>
    python3 parse-plan.py --help

Output: JSON with plan structure including phases, tasks, and status.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_phase_progress_table(content: str) -> list[dict]:
    """Parse the Phase Progress Table and return phase data."""
    phases = []

    # Find the table after "## Phase Progress"
    table_pattern = r'\|\s*Phase\s*\|\s*Status\s*\|\s*Tasks\s*\|\s*Completed\s*\|.*?\n\|[-\s|]+\n((?:\|[^\n]+\n)+)'
    match = re.search(table_pattern, content, re.IGNORECASE)

    if not match:
        return phases

    table_rows = match.group(1).strip().split('\n')

    for row in table_rows:
        cols = [c.strip() for c in row.split('|')[1:-1]]
        if len(cols) >= 4:
            phase_name = cols[0].strip()
            status = cols[1].strip()
            task_count = cols[2].strip()
            completed = cols[3].strip()

            # Parse completed (e.g., "3/5" -> completed=3, total=5)
            completed_match = re.match(r'(\d+)/(\d+)', completed)
            if completed_match:
                completed_count = int(completed_match.group(1))
                total_count = int(completed_match.group(2))
            else:
                completed_count = 0
                total_count = int(task_count) if task_count.isdigit() else 0

            phases.append({
                'name': phase_name,
                'status': status,
                'tasks_total': total_count,
                'tasks_completed': completed_count,
                'completion_percentage': round(completed_count / total_count * 100, 1) if total_count > 0 else 0
            })

    return phases


def parse_current_phase_and_task(content: str) -> tuple[str, str]:
    """Extract current phase and task from plan header."""
    current_phase = ''
    current_task = ''

    phase_match = re.search(r'\*\*Current Phase\*\*:\s*(\w+)', content)
    if phase_match:
        current_phase = phase_match.group(1)

    task_match = re.search(r'\*\*Current Task\*\*:\s*([^\n]+)', content)
    if task_match:
        current_task = task_match.group(1).strip()

    return current_phase, current_task


def parse_tasks(content: str) -> list[dict]:
    """Parse all tasks from the plan."""
    tasks = []

    # Pattern for task headers: ### Task N: Name
    task_pattern = r'### Task (\d+):\s*([^\n]+)\n(.*?)(?=### Task \d+:|## Phase:|## Completion Criteria|$)'
    matches = re.finditer(task_pattern, content, re.DOTALL)

    for match in matches:
        task_id = int(match.group(1))
        task_name = match.group(2).strip()
        task_content = match.group(3)

        # Extract phase
        phase_match = re.search(r'\*\*Phase\*\*:\s*(\w+)', task_content)
        phase = phase_match.group(1) if phase_match else ''

        # Extract goal
        goal_match = re.search(r'\*\*Goal\*\*:\s*([^\n]+)', task_content)
        goal = goal_match.group(1).strip() if goal_match else ''

        # Extract acceptance criteria
        acceptance_criteria = []
        ac_section = re.search(r'\*\*Acceptance Criteria\*\*:\s*\n((?:[-*]\s+[^\n]+\n?)+)', task_content)
        if ac_section:
            criteria_lines = ac_section.group(1).strip().split('\n')
            for line in criteria_lines:
                line = re.sub(r'^[-*]\s+', '', line.strip())
                if line:
                    acceptance_criteria.append(line)

        # Extract checklist items
        checklist = []
        checklist_section = re.search(r'\*\*Checklist\*\*:\s*\n((?:[-*]\s+\[[x ]\][^\n]+\n?)+)', task_content, re.IGNORECASE)
        if checklist_section:
            checklist_lines = checklist_section.group(1).strip().split('\n')
            for line in checklist_lines:
                item_match = re.match(r'[-*]\s+\[([x ])\]\s+(.+)', line.strip(), re.IGNORECASE)
                if item_match:
                    completed = item_match.group(1).lower() == 'x'
                    description = item_match.group(2).strip()
                    checklist.append({
                        'completed': completed,
                        'description': description
                    })

        # Determine task status based on checklist
        total_items = len(checklist)
        completed_items = sum(1 for item in checklist if item['completed'])

        if total_items == 0:
            status = 'pending'
        elif completed_items == total_items:
            status = 'completed'
        elif completed_items > 0:
            status = 'in_progress'
        else:
            status = 'pending'

        tasks.append({
            'id': task_id,
            'name': task_name,
            'phase': phase,
            'goal': goal,
            'status': status,
            'acceptance_criteria': acceptance_criteria,
            'checklist': checklist,
            'checklist_completed': completed_items,
            'checklist_total': total_items
        })

    return tasks


def parse_plan_title(content: str) -> str:
    """Extract the plan title from the first H1 header."""
    match = re.search(r'^#\s+(?:Task Plan:\s*)?(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else ''


def parse_plan(plan_file: Path) -> dict:
    """Parse plan.md and return structured data."""
    if not plan_file.exists():
        return {
            'error': {
                'type': 'file_not_found',
                'message': f'Plan file not found: {plan_file}'
            }
        }

    content = plan_file.read_text()

    title = parse_plan_title(content)
    current_phase, current_task = parse_current_phase_and_task(content)
    phases = parse_phase_progress_table(content)
    tasks = parse_tasks(content)

    # Determine overall status
    all_completed = all(p['status'] == 'completed' for p in phases) if phases else False
    any_in_progress = any(p['status'] == 'in_progress' for p in phases) if phases else False

    if all_completed:
        overall_status = 'completed'
    elif any_in_progress or current_phase:
        overall_status = 'in_progress'
    else:
        overall_status = 'pending'

    # Group tasks by phase
    tasks_by_phase = {}
    for task in tasks:
        phase = task['phase']
        if phase not in tasks_by_phase:
            tasks_by_phase[phase] = []
        tasks_by_phase[phase].append(task)

    return {
        'title': title,
        'plan_status': {
            'current_phase': current_phase,
            'current_task': current_task,
            'overall_status': overall_status
        },
        'phases': phases,
        'tasks': tasks,
        'tasks_by_phase': tasks_by_phase,
        'summary': {
            'total_phases': len(phases),
            'total_tasks': len(tasks),
            'completed_tasks': sum(1 for t in tasks if t['status'] == 'completed'),
            'in_progress_tasks': sum(1 for t in tasks if t['status'] == 'in_progress'),
            'pending_tasks': sum(1 for t in tasks if t['status'] == 'pending')
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Parse plan.md and extract structured data.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "title": "Plan title",
  "plan_status": {
    "current_phase": "implement",
    "current_task": "task-6",
    "overall_status": "in_progress"
  },
  "phases": [...],
  "tasks": [...],
  "tasks_by_phase": {...},
  "summary": {...}
}
"""
    )
    parser.add_argument('plan_file', help='Path to plan.md file')

    args = parser.parse_args()

    plan_file = Path(args.plan_file)
    result = parse_plan(plan_file)

    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
