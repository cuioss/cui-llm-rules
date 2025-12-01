#!/usr/bin/env python3
"""
Calculate progress metrics from plan data.

Usage:
    python3 calculate-progress.py <plan-file>
    python3 calculate-progress.py --help

Output: JSON with progress metrics including completion percentages and estimates.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_phase_progress(content: str) -> list[dict]:
    """Parse the Phase Progress Table and return phase data."""
    phases = []

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
            completed = cols[3].strip()

            completed_match = re.match(r'(\d+)/(\d+)', completed)
            if completed_match:
                completed_count = int(completed_match.group(1))
                total_count = int(completed_match.group(2))
            else:
                completed_count = 0
                total_count = 0

            phases.append({
                'name': phase_name,
                'status': status,
                'completed': completed_count,
                'total': total_count
            })

    return phases


def parse_tasks_with_checklist(content: str) -> list[dict]:
    """Parse tasks and extract checklist progress."""
    tasks = []

    task_pattern = r'### Task (\d+):\s*([^\n]+)\n(.*?)(?=### Task \d+:|## Phase:|## Completion Criteria|$)'
    matches = re.finditer(task_pattern, content, re.DOTALL)

    for match in matches:
        task_id = int(match.group(1))
        task_name = match.group(2).strip()
        task_content = match.group(3)

        # Extract phase
        phase_match = re.search(r'\*\*Phase\*\*:\s*(\w+)', task_content)
        phase = phase_match.group(1) if phase_match else ''

        # Count checklist items
        checklist_items = re.findall(r'-\s*\[([x ])\]', task_content, re.IGNORECASE)
        total_items = len(checklist_items)
        completed_items = sum(1 for item in checklist_items if item.lower() == 'x')

        tasks.append({
            'id': task_id,
            'name': task_name,
            'phase': phase,
            'checklist_completed': completed_items,
            'checklist_total': total_items
        })

    return tasks


def calculate_progress(plan_file: Path) -> dict:
    """Calculate progress metrics from plan.md."""
    if not plan_file.exists():
        return {
            'error': {
                'type': 'file_not_found',
                'message': f'Plan file not found: {plan_file}'
            }
        }

    content = plan_file.read_text()

    phases = parse_phase_progress(content)
    tasks = parse_tasks_with_checklist(content)

    # Calculate phase progress
    phase_progress = []
    total_phase_tasks = 0
    completed_phase_tasks = 0

    for phase in phases:
        total_phase_tasks += phase['total']
        completed_phase_tasks += phase['completed']

        percentage = round(phase['completed'] / phase['total'] * 100, 1) if phase['total'] > 0 else 0
        phase_progress.append({
            'phase': phase['name'],
            'status': phase['status'],
            'completed': phase['completed'],
            'total': phase['total'],
            'percentage': percentage
        })

    # Calculate task progress
    total_checklist_items = sum(t['checklist_total'] for t in tasks)
    completed_checklist_items = sum(t['checklist_completed'] for t in tasks)

    # Calculate by phase
    progress_by_phase = {}
    for task in tasks:
        phase = task['phase']
        if phase not in progress_by_phase:
            progress_by_phase[phase] = {
                'tasks': 0,
                'checklist_completed': 0,
                'checklist_total': 0
            }
        progress_by_phase[phase]['tasks'] += 1
        progress_by_phase[phase]['checklist_completed'] += task['checklist_completed']
        progress_by_phase[phase]['checklist_total'] += task['checklist_total']

    # Calculate overall progress
    overall_percentage = round(completed_phase_tasks / total_phase_tasks * 100, 1) if total_phase_tasks > 0 else 0
    checklist_percentage = round(completed_checklist_items / total_checklist_items * 100, 1) if total_checklist_items > 0 else 0

    # Determine current phase
    current_phase = ''
    for phase in phase_progress:
        if phase['status'] == 'in_progress':
            current_phase = phase['phase']
            break

    # Calculate remaining work
    remaining_tasks = total_phase_tasks - completed_phase_tasks
    remaining_checklist = total_checklist_items - completed_checklist_items

    return {
        'overall': {
            'total_tasks': total_phase_tasks,
            'completed_tasks': completed_phase_tasks,
            'remaining_tasks': remaining_tasks,
            'percentage': overall_percentage,
            'current_phase': current_phase
        },
        'checklist': {
            'total_items': total_checklist_items,
            'completed_items': completed_checklist_items,
            'remaining_items': remaining_checklist,
            'percentage': checklist_percentage
        },
        'phases': phase_progress,
        'tasks': tasks,
        'by_phase': progress_by_phase,
        'status': {
            'is_started': completed_phase_tasks > 0 or any(p['status'] == 'in_progress' for p in phases),
            'is_completed': all(p['status'] == 'completed' for p in phases) if phases else False,
            'phases_completed': sum(1 for p in phases if p['status'] == 'completed'),
            'phases_total': len(phases)
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Calculate progress metrics from plan.md.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "overall": {
    "total_tasks": 20,
    "completed_tasks": 10,
    "percentage": 50.0
  },
  "checklist": {...},
  "phases": [...],
  "tasks": [...],
  "by_phase": {...},
  "status": {...}
}
"""
    )
    parser.add_argument('plan_file', help='Path to plan.md file')

    args = parser.parse_args()

    plan_file = Path(args.plan_file)
    result = calculate_progress(plan_file)

    print(json.dumps(result, indent=2))

    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
