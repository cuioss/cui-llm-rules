#!/usr/bin/env python3
"""
Update checklist items and progress in plan.md.

Updates checklist items from [ ] to [x], recalculates phase progress,
and updates current task pointer. Uses atomic file operations.

Output: JSON with progress status.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'cui-utilities' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, output_success, output_error


def parse_phase_progress(content: str) -> dict:
    """Parse phase progress table from plan.md.

    Returns:
        Dict mapping phase names to their current progress
    """
    progress = {}

    # Find phase progress table
    table_pattern = r'\| Phase \| Status \| Tasks \| Completed \|.*?\n\|[-|\s]+\|\n((?:\|.*?\n)*)'
    match = re.search(table_pattern, content)

    if match:
        rows = match.group(1).strip().split('\n')
        for row in rows:
            parts = [p.strip() for p in row.split('|')[1:-1]]  # Skip empty first/last
            if len(parts) >= 4:
                phase_name = parts[0]
                status = parts[1]
                tasks = int(parts[2])
                completed_str = parts[3]
                completed = int(completed_str.split('/')[0])
                progress[phase_name] = {
                    'status': status,
                    'tasks': tasks,
                    'completed': completed
                }

    return progress


def find_task_section(content: str, phase: str, task_id: str) -> tuple[int, int]:
    """Find the start and end positions of a task section.

    Args:
        content: Plan content
        phase: Phase name
        task_id: Task identifier (e.g., "1" or "task-1")

    Returns:
        Tuple of (start_pos, end_pos) or (-1, -1) if not found
    """
    # Normalize task_id
    if task_id.startswith('task-'):
        task_num = task_id[5:]
    else:
        task_num = task_id

    # Find task header in phase
    phase_pattern = rf'## Phase: {re.escape(phase)}.*?\n'
    phase_match = re.search(phase_pattern, content)

    if not phase_match:
        return -1, -1

    # Search for task within phase
    task_pattern = rf'### Task {task_num}:.*?(?=### Task|\n## |\Z)'
    task_match = re.search(task_pattern, content[phase_match.end():], re.DOTALL)

    if not task_match:
        return -1, -1

    start = phase_match.end() + task_match.start()
    end = phase_match.end() + task_match.end()

    return start, end


def complete_checklist_items(content: str, phase: str, task_id: str, items: list[str]) -> tuple[str, int]:
    """Mark checklist items as complete.

    Args:
        content: Plan content
        phase: Phase name
        task_id: Task identifier
        items: List of item texts to complete

    Returns:
        Tuple of (updated_content, items_completed_count)
    """
    start, end = find_task_section(content, phase, task_id)

    if start == -1:
        return content, 0

    task_section = content[start:end]
    completed_count = 0

    for item in items:
        # Escape special regex characters in item
        escaped_item = re.escape(item)
        # Match the checklist item pattern
        pattern = rf'- \[ \] {escaped_item}'
        replacement = f'- [x] {item}'

        if re.search(pattern, task_section):
            task_section = re.sub(pattern, replacement, task_section)
            completed_count += 1

    # Rebuild content
    content = content[:start] + task_section + content[end:]

    return content, completed_count


def count_checklist_items(content: str, phase: str) -> tuple[int, int]:
    """Count total and completed checklist items in a phase.

    Args:
        content: Plan content
        phase: Phase name

    Returns:
        Tuple of (total_items, completed_items)
    """
    # Find phase section
    phase_pattern = rf'## Phase: {re.escape(phase)}.*?(?=\n## |\Z)'
    phase_match = re.search(phase_pattern, content, re.DOTALL)

    if not phase_match:
        return 0, 0

    phase_content = phase_match.group(0)

    total = len(re.findall(r'- \[[ x]\]', phase_content))
    completed = len(re.findall(r'- \[x\]', phase_content))

    return total, completed


def update_phase_progress_table(content: str, phase: str, total: int, completed: int) -> str:
    """Update the phase progress table with new counts.

    Args:
        content: Plan content
        phase: Phase name
        total: Total items
        completed: Completed items

    Returns:
        Updated content
    """
    # Determine status
    if completed == 0:
        status = 'pending'
    elif completed >= total:
        status = 'completed'
    else:
        status = 'in_progress'

    # Update the table row for this phase
    pattern = rf'(\| {re.escape(phase)} \|) \w+ \| \d+ \| \d+/\d+ \|'
    replacement = f'\\1 {status} | {total} | {completed}/{total} |'

    return re.sub(pattern, replacement, content)


def update_current_phase_status(content: str, phase: str, status: str) -> str:
    """Update the phase header status.

    Args:
        content: Plan content
        phase: Phase name
        status: New status

    Returns:
        Updated content
    """
    pattern = rf'## Phase: {re.escape(phase)} \(\w+\)'
    replacement = f'## Phase: {phase} ({status})'
    return re.sub(pattern, replacement, content)


def find_next_incomplete_task(content: str, phase: str) -> str:
    """Find the next incomplete task in a phase.

    Args:
        content: Plan content
        phase: Phase name

    Returns:
        Task identifier or "none" if all complete
    """
    # Find phase section
    phase_pattern = rf'## Phase: {re.escape(phase)}.*?(?=\n## |\Z)'
    phase_match = re.search(phase_pattern, content, re.DOTALL)

    if not phase_match:
        return "none"

    phase_content = phase_match.group(0)

    # Find all task sections
    task_pattern = r'### Task (\d+):.*?(?=### Task|\Z)'
    tasks = re.findall(task_pattern, phase_content, re.DOTALL)

    for task_match in re.finditer(task_pattern, phase_content, re.DOTALL):
        task_num = task_match.group(1)
        task_content = task_match.group(0)

        # Check if task has incomplete items
        if '- [ ]' in task_content:
            return f"task-{task_num}"

    return "none"


def update_current_task_pointer(content: str, new_task: str) -> str:
    """Update the current task pointer.

    Args:
        content: Plan content
        new_task: New current task identifier

    Returns:
        Updated content
    """
    return re.sub(
        r'\*\*Current Task\*\*:.*',
        f'**Current Task**: {new_task}',
        content
    )


def update_current_phase_pointer(content: str, new_phase: str) -> str:
    """Update the current phase pointer.

    Args:
        content: Plan content
        new_phase: New current phase name

    Returns:
        Updated content
    """
    return re.sub(
        r'\*\*Current Phase\*\*:.*',
        f'**Current Phase**: {new_phase}',
        content
    )


def main():
    parser = argparse.ArgumentParser(
        description='Update checklist items and progress in plan.md',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete specific checklist items
  %(prog)s --plan-dir .plan/plans/my-task \\
           --phase init \\
           --task-id 1 \\
           --complete-items "Check current git branch,Detect build system"

  # Complete items and set task status
  %(prog)s --plan-dir .plan/plans/my-task \\
           --phase implement \\
           --task-id 3 \\
           --complete-items "Implement feature,Add tests" \\
           --set-status completed
"""
    )

    parser.add_argument('--plan-dir', required=True,
                        help='Directory containing plan.md')
    parser.add_argument('--phase', required=True,
                        help='Phase containing the task')
    parser.add_argument('--task-id', required=True,
                        help='Task identifier (e.g., "1" or "task-1")')
    parser.add_argument('--complete-items', required=True,
                        help='Comma-separated list of checklist items to complete')
    parser.add_argument('--set-status', choices=['pending', 'in_progress', 'completed'],
                        default=None,
                        help='Optional: Force task status')

    args = parser.parse_args()

    try:
        plan_dir = Path(args.plan_dir)
        file_path = plan_dir / "plan.md"

        if not file_path.exists():
            output_error('update-progress', f"Plan file not found: {file_path}")
            return 1

        # Read current content
        content = file_path.read_text(encoding='utf-8')

        # Parse items to complete
        items = [item.strip() for item in args.complete_items.split(',') if item.strip()]

        # Complete checklist items
        content, items_completed = complete_checklist_items(
            content, args.phase, args.task_id, items
        )

        # Count progress in phase
        total, completed = count_checklist_items(content, args.phase)

        # Update phase progress table
        content = update_phase_progress_table(content, args.phase, total, completed)

        # Determine phase status
        if completed == 0:
            phase_status = 'pending'
        elif completed >= total:
            phase_status = 'completed'
        else:
            phase_status = 'in_progress'

        # Update phase header status
        content = update_current_phase_status(content, args.phase, phase_status)

        # Find next incomplete task
        next_task = find_next_incomplete_task(content, args.phase)

        # Update current task pointer
        content = update_current_task_pointer(content, next_task)

        # Update current phase pointer if --phase differs from header
        current_phase_match = re.search(r'\*\*Current Phase\*\*:\s*(\w+)', content)
        if current_phase_match:
            current_phase_in_header = current_phase_match.group(1)
            if current_phase_in_header != args.phase:
                content = update_current_phase_pointer(content, args.phase)

        # Write updated content
        atomic_write_file(file_path, content)

        output_success(
            'update-progress',
            file=str(file_path),
            phase=args.phase,
            task_id=args.task_id,
            items_completed=items_completed,
            phase_status={
                'total': total,
                'completed': completed,
                'status': phase_status,
                'phase_complete': completed >= total
            },
            next_task=next_task
        )
        return 0

    except Exception as e:
        output_error('update-progress', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
