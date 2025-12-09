#!/usr/bin/env python3
"""
Manage implementation tasks with sequential sub-steps within a plan.

Single CLI with subcommands for CRUD operations on task files.
Uses TOON format for both storage and output.
Each task must reference exactly one goal.

Subcommands:
  add              - Add a new task
  update           - Update an existing task
  remove           - Remove a task
  list             - List all tasks (summary)
  get              - Get a single task by number
  next             - Get next pending task/step for execution
  step-start       - Mark a step as in_progress
  step-done        - Mark a step as done
  step-skip        - Skip a step
  add-step         - Add a new step to a task
  remove-step      - Remove a step from a task

Output: TOON format for all operations.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Tuple

# Import file operations from base module
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent.parent.parent / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, base_path


def now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def slugify(title: str, max_length: int = 40) -> str:
    """Convert title to kebab-case slug.

    Args:
        title: The title to convert
        max_length: Maximum slug length (default 40)

    Returns:
        Kebab-case slug
    """
    # Lowercase and replace spaces with hyphens
    slug = title.lower().replace(' ', '-')
    # Remove special characters (keep alphanumeric and hyphens)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Truncate
    slug = slug[:max_length]
    # Remove trailing hyphens
    slug = slug.rstrip('-')
    return slug


def validate_goal(goal_str: str) -> str:
    """Validate goal reference.

    Args:
        goal_str: GOAL reference (e.g., "GOAL-1")

    Returns:
        Validated GOAL reference

    Raises:
        ValueError: If format is invalid
    """
    if not goal_str or not goal_str.strip():
        raise ValueError("Goal reference is required")

    goal_str = goal_str.strip()
    pattern = re.compile(r'^GOAL-\d+$')
    if not pattern.match(goal_str):
        raise ValueError(f"Invalid goal format: {goal_str}. Expected GOAL-N (e.g., GOAL-1)")

    return goal_str


def get_goals_dir(plan_id: str) -> Path:
    """Get the goals directory for a plan.

    Args:
        plan_id: The plan identifier

    Returns:
        Path to goals directory
    """
    return base_path('plans', plan_id, 'goals')


def find_goal_file(goal_dir: Path, number: int) -> Optional[Path]:
    """Find goal file by number.

    Args:
        goal_dir: Goals directory
        number: Goal number

    Returns:
        Path to file or None if not found
    """
    pattern = f"GOAL-{number:03d}-*.toon"
    matches = list(goal_dir.glob(pattern))
    return matches[0] if matches else None


def parse_goal_file(content: str) -> dict:
    """Parse a goal TOON file into a dictionary.

    Args:
        content: File content

    Returns:
        Dictionary with goal fields
    """
    result = {}
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith('body:'):
            if line.strip() == 'body: |':
                body_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].startswith('  '):
                        body_lines.append(lines[i][2:])
                    elif lines[i].strip() == '':
                        body_lines.append('')
                    else:
                        break
                    i += 1
                result['body'] = '\n'.join(body_lines).strip()
            else:
                result['body'] = line[5:].strip()
                i += 1
        elif ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key == 'number':
                value = int(value)
            result[key] = value
            i += 1
        else:
            i += 1

    return result


def get_goal_context(plan_id: str, goal_ref: str) -> Optional[dict]:
    """Get goal details for including in task context.

    Args:
        plan_id: The plan identifier
        goal_ref: Goal reference (e.g., "GOAL-1")

    Returns:
        Dictionary with goal context or None if not found
    """
    # Extract number from GOAL-N reference
    match = re.match(r'^GOAL-(\d+)$', goal_ref)
    if not match:
        return None

    goal_num = int(match.group(1))
    goal_dir = get_goals_dir(plan_id)

    if not goal_dir.exists():
        return None

    goal_file = find_goal_file(goal_dir, goal_num)
    if not goal_file:
        return None

    try:
        content = goal_file.read_text(encoding='utf-8')
        goal = parse_goal_file(content)
        return {
            'goal_found': True,
            'goal_number': goal.get('number', goal_num),
            'goal_title': goal.get('title', ''),
            'goal_body': goal.get('body', '')
        }
    except Exception:
        return None


def get_tasks_dir(plan_id: str) -> Path:
    """Get the tasks directory for a plan.

    Args:
        plan_id: The plan identifier

    Returns:
        Path to tasks directory
    """
    return base_path('plans', plan_id, 'tasks')


def parse_task_file(content: str) -> dict:
    """Parse a task TOON file into a dictionary.

    Args:
        content: File content

    Returns:
        Dictionary with task fields including steps list
    """
    result = {'steps': []}
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith('description:'):
            # Check for multiline description (description: |)
            if line.strip() == 'description: |':
                # Collect indented lines
                desc_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].startswith('  '):
                        desc_lines.append(lines[i][2:])  # Remove 2-space indent
                    elif lines[i].strip() == '':
                        desc_lines.append('')
                    else:
                        break
                    i += 1
                result['description'] = '\n'.join(desc_lines).strip()
            else:
                # Single line description
                result['description'] = line[12:].strip()
                i += 1
        elif line.startswith('steps['):
            # Parse steps table header: steps[N]{number,title,status}:
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('current_step:'):
                parts = lines[i].split(',', 2)
                if len(parts) == 3:
                    result['steps'].append({
                        'number': int(parts[0]),
                        'title': parts[1],
                        'status': parts[2]
                    })
                i += 1
        elif ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Convert number to int
            if key in ('number', 'current_step'):
                value = int(value) if value else 1
            result[key] = value
            i += 1
        else:
            i += 1

    return result


def format_task_file(task: dict) -> str:
    """Format a task dictionary as TOON file content.

    Args:
        task: Task dictionary with steps

    Returns:
        TOON formatted string
    """
    lines = [
        f"number: {task['number']}",
        f"title: {task['title']}",
        f"status: {task['status']}",
        f"goal: {task['goal']}",
        f"created: {task['created']}",
        f"updated: {task['updated']}",
        "",
        "description: |",
    ]

    # Add description with 2-space indent
    for desc_line in task['description'].split('\n'):
        lines.append(f"  {desc_line}")

    lines.append("")

    # Add steps table
    steps = task.get('steps', [])
    lines.append(f"steps[{len(steps)}]{{number,title,status}}:")
    for step in steps:
        lines.append(f"{step['number']},{step['title']},{step['status']}")

    lines.append("")
    lines.append(f"current_step: {task.get('current_step', 1)}")

    return '\n'.join(lines)


def find_task_file(task_dir: Path, number: int) -> Optional[Path]:
    """Find task file by number.

    Args:
        task_dir: Tasks directory
        number: Task number

    Returns:
        Path to file or None if not found
    """
    pattern = f"TASK-{number:03d}-*.toon"
    matches = list(task_dir.glob(pattern))
    return matches[0] if matches else None


def get_next_number(task_dir: Path) -> int:
    """Get next available task number.

    Args:
        task_dir: Tasks directory

    Returns:
        Next available number
    """
    if not task_dir.exists():
        return 1

    max_num = 0
    for f in task_dir.glob("TASK-*.toon"):
        try:
            # Extract number from TASK-NNN-slug.toon
            num = int(f.name[5:8])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass

    return max_num + 1


def get_all_tasks(task_dir: Path) -> list:
    """Get all tasks sorted by number.

    Args:
        task_dir: Tasks directory

    Returns:
        List of (path, task_dict) tuples
    """
    if not task_dir.exists():
        return []

    tasks = []
    for f in sorted(task_dir.glob("TASK-*.toon")):
        content = f.read_text(encoding='utf-8')
        task = parse_task_file(content)
        tasks.append((f, task))

    return sorted(tasks, key=lambda x: x[1].get('number', 0))


def calculate_progress(task: dict) -> Tuple[int, int]:
    """Calculate step completion progress.

    Args:
        task: Task dictionary

    Returns:
        Tuple of (completed_steps, total_steps)
    """
    steps = task.get('steps', [])
    completed = sum(1 for s in steps if s['status'] in ('done', 'skipped'))
    return completed, len(steps)


def output_toon(data: dict) -> None:
    """Print TOON formatted output."""
    lines = []

    # Top-level simple fields
    for key in ['status', 'plan_id', 'file', 'renamed', 'total_tasks', 'task_number', 'step']:
        if key in data:
            lines.append(f"{key}: {data[key]}")

    # Task/step status fields
    for key in ['task_status', 'step_status', 'step_title', 'next_step', 'next_step_title', 'message']:
        if key in data:
            val = data[key]
            if val is None:
                lines.append(f"{key}: null")
            else:
                lines.append(f"{key}: {val}")

    # Counts block
    if 'counts' in data:
        lines.append("")
        lines.append("counts:")
        for k, v in data['counts'].items():
            lines.append(f"  {k}: {v}")

    # Single task block
    if 'task' in data:
        lines.append("")
        lines.append("task:")
        task = data['task']
        for key in ['number', 'title', 'goal', 'status', 'current_step', 'created', 'updated', 'step_count']:
            if key in task:
                lines.append(f"  {key}: {task[key]}")
        if 'description' in task:
            lines.append(f"  description: {task['description']}")
        if 'steps' in task:
            steps = task['steps']
            lines.append(f"  steps[{len(steps)}]{{number,title,status}}:")
            for s in steps:
                lines.append(f"  {s['number']},{s['title']},{s['status']}")

    # Removed block
    if 'removed' in data:
        lines.append("")
        lines.append("removed:")
        rem = data['removed']
        for key in ['number', 'title', 'file']:
            if key in rem:
                lines.append(f"  {key}: {rem[key]}")

    # Next block
    if 'next' in data:
        lines.append("")
        if data['next'] is None:
            lines.append("next: null")
        else:
            lines.append("next:")
            nxt = data['next']
            for key in ['task_number', 'task_title', 'goal', 'step_number', 'step_title',
                        'goal_found', 'goal_number', 'goal_title', 'goal_body']:
                if key in nxt:
                    val = nxt[key]
                    # Convert Python booleans to lowercase for TOON format
                    if isinstance(val, bool):
                        val = 'true' if val else 'false'
                    lines.append(f"  {key}: {val}")

    # Context block
    if 'context' in data:
        lines.append("")
        lines.append("context:")
        ctx = data['context']
        for k, v in ctx.items():
            lines.append(f"  {k}: {v}")

    # Tasks list (tabular)
    if 'tasks_table' in data:
        tasks = data['tasks_table']
        lines.append("")
        lines.append(f"tasks[{len(tasks)}]{{number,title,goal,status,progress}}:")
        for t in tasks:
            lines.append(f"{t['number']},{t['title']},{t['goal']},{t['status']},{t['progress']}")

    print('\n'.join(lines))


def output_error(message: str) -> None:
    """Print TOON error output to stderr."""
    print(f"status: error\nmessage: {message}", file=sys.stderr)


# ============================================================================
# Subcommand handlers
# ============================================================================

def cmd_add(args) -> int:
    """Handle 'add' subcommand."""
    # Validate goal
    try:
        goal = validate_goal(args.goal)
    except ValueError as e:
        output_error(str(e))
        return 1

    # Validate steps
    if not args.steps or len(args.steps) == 0:
        output_error("At least one step is required")
        return 1

    task_dir = get_tasks_dir(args.plan_id)

    # Get next number
    number = get_next_number(task_dir)

    # Generate slug and filename
    slug = slugify(args.title)
    filename = f"TASK-{number:03d}-{slug}.toon"
    filepath = task_dir / filename

    # Create steps
    steps = []
    for i, step_title in enumerate(args.steps, 1):
        steps.append({
            'number': i,
            'title': step_title,
            'status': 'pending'
        })

    # Create task
    now = now_iso()
    task = {
        'number': number,
        'title': args.title,
        'status': 'pending',
        'goal': goal,
        'created': now,
        'updated': now,
        'description': args.description,
        'steps': steps,
        'current_step': 1
    }

    # Write file
    content = format_task_file(task)
    atomic_write_file(filepath, content)

    # Count total
    total = len(list(task_dir.glob("TASK-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filename,
        'total_tasks': total,
        'task': {
            'number': number,
            'title': args.title,
            'goal': goal,
            'status': 'pending',
            'step_count': len(steps)
        }
    })
    return 0


def cmd_update(args) -> int:
    """Handle 'update' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find existing file
    filepath = find_task_file(task_dir, args.number)
    if not filepath:
        output_error(f"Task TASK-{args.number} not found")
        return 1

    # Read current content
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    # Update fields
    renamed = False
    old_title = task['title']

    if args.title:
        task['title'] = args.title
    if args.description:
        task['description'] = args.description
    if args.goal:
        try:
            task['goal'] = validate_goal(args.goal)
        except ValueError as e:
            output_error(str(e))
            return 1
    if args.status:
        if args.status not in ('pending', 'in_progress', 'done', 'blocked'):
            output_error(f"Invalid status: {args.status}. Must be pending, in_progress, done, or blocked")
            return 1
        task['status'] = args.status

    task['updated'] = now_iso()

    # Check if rename needed
    new_filename = filepath.name
    if args.title and args.title != old_title:
        new_slug = slugify(args.title)
        new_filename = f"TASK-{args.number:03d}-{new_slug}.toon"
        renamed = True

    # Write file
    new_content = format_task_file(task)
    new_filepath = task_dir / new_filename

    if renamed:
        atomic_write_file(new_filepath, new_content)
        filepath.unlink()
    else:
        atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': new_filename,
        'renamed': renamed,
        'task': {
            'number': task['number'],
            'title': task['title'],
            'goal': task['goal'],
            'status': task['status']
        }
    })
    return 0


def cmd_remove(args) -> int:
    """Handle 'remove' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find existing file
    filepath = find_task_file(task_dir, args.number)
    if not filepath:
        output_error(f"Task TASK-{args.number} not found")
        return 1

    # Read for output
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)
    filename = filepath.name

    # Delete file
    filepath.unlink()

    # Count remaining
    total = len(list(task_dir.glob("TASK-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'total_tasks': total,
        'removed': {
            'number': task['number'],
            'title': task['title'],
            'file': filename
        }
    })
    return 0


def cmd_list(args) -> int:
    """Handle 'list' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)
    all_tasks = get_all_tasks(task_dir)

    # Filter by goal if specified
    if args.goal:
        all_tasks = [
            (p, t) for p, t in all_tasks
            if t.get('goal') == args.goal
        ]

    # Get filtered list for status filtering
    filtered_tasks = all_tasks
    if args.status and args.status != 'all':
        filtered_tasks = [(p, t) for p, t in all_tasks if t.get('status') == args.status]

    # Compute counts from all (not status-filtered, but goal-filtered)
    pending = sum(1 for _, t in all_tasks if t.get('status') == 'pending')
    in_progress = sum(1 for _, t in all_tasks if t.get('status') == 'in_progress')
    done = sum(1 for _, t in all_tasks if t.get('status') == 'done')
    blocked = sum(1 for _, t in all_tasks if t.get('status') == 'blocked')

    # Build table data
    table = []
    for path, task in filtered_tasks:
        completed, total = calculate_progress(task)
        table.append({
            'number': task['number'],
            'title': task['title'],
            'goal': task.get('goal', ''),
            'status': task['status'],
            'progress': f"{completed}/{total}"
        })

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'counts': {
            'total': len(all_tasks),
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'blocked': blocked
        },
        'tasks_table': table
    })
    return 0


def cmd_get(args) -> int:
    """Handle 'get' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find file
    filepath = find_task_file(task_dir, args.number)
    if not filepath:
        output_error(f"Task TASK-{args.number} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filepath.name,
        'task': {
            'number': task['number'],
            'title': task['title'],
            'goal': task.get('goal', ''),
            'status': task['status'],
            'current_step': task.get('current_step', 1),
            'created': task.get('created', ''),
            'updated': task.get('updated', ''),
            'description': task.get('description', ''),
            'steps': task.get('steps', [])
        }
    })
    return 0


def cmd_next(args) -> int:
    """Handle 'next' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)
    all_tasks = get_all_tasks(task_dir)

    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for _, t in all_tasks if t.get('status') == 'done')

    # Find first in_progress or pending task
    next_task = None
    next_task_path = None

    # First, look for in_progress tasks
    for path, task in all_tasks:
        if task.get('status') == 'in_progress':
            next_task = task
            next_task_path = path
            break

    # If no in_progress, find first pending
    if not next_task:
        for path, task in all_tasks:
            if task.get('status') == 'pending':
                next_task = task
                next_task_path = path
                break

    if not next_task:
        # All done
        output_toon({
            'status': 'success',
            'plan_id': args.plan_id,
            'next': None,
            'context': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'message': 'All tasks completed'
            }
        })
        return 0

    # Find next pending step in this task
    steps = next_task.get('steps', [])
    next_step = None
    completed_steps = 0
    remaining_steps = 0

    for step in steps:
        if step['status'] in ('done', 'skipped'):
            completed_steps += 1
        elif step['status'] == 'in_progress':
            next_step = step
            remaining_steps = len(steps) - completed_steps
        elif step['status'] == 'pending' and not next_step:
            next_step = step
            remaining_steps = len(steps) - completed_steps

    if not next_step:
        # Task has no pending steps but isn't marked done - edge case
        output_toon({
            'status': 'success',
            'plan_id': args.plan_id,
            'next': None,
            'context': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'message': 'All tasks completed'
            }
        })
        return 0

    # Build base result
    result = {
        'status': 'success',
        'plan_id': args.plan_id,
        'next': {
            'task_number': next_task['number'],
            'task_title': next_task['title'],
            'goal': next_task.get('goal', ''),
            'step_number': next_step['number'],
            'step_title': next_step['title']
        },
        'context': {
            'completed_steps': completed_steps,
            'remaining_steps': remaining_steps,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks
        }
    }

    # Include goal context if requested
    if getattr(args, 'include_context', False):
        goal_ref = next_task.get('goal', '')
        goal_context = get_goal_context(args.plan_id, goal_ref)
        if goal_context:
            result['next'].update(goal_context)
        else:
            result['next']['goal_found'] = False

    output_toon(result)
    return 0


def cmd_step_start(args) -> int:
    """Handle 'step-start' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find task file
    filepath = find_task_file(task_dir, args.task)
    if not filepath:
        output_error(f"Task TASK-{args.task} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    # Find step
    steps = task.get('steps', [])
    step_found = None
    for step in steps:
        if step['number'] == args.step:
            step_found = step
            break

    if not step_found:
        output_error(f"Step {args.step} not found in TASK-{args.task}")
        return 1

    # Update step and task status
    step_found['status'] = 'in_progress'
    task['status'] = 'in_progress'
    task['current_step'] = args.step
    task['updated'] = now_iso()

    # Write back
    new_content = format_task_file(task)
    atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'task_number': args.task,
        'step': args.step,
        'task_status': 'in_progress',
        'step_status': 'in_progress',
        'step_title': step_found['title']
    })
    return 0


def cmd_step_done(args) -> int:
    """Handle 'step-done' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find task file
    filepath = find_task_file(task_dir, args.task)
    if not filepath:
        output_error(f"Task TASK-{args.task} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    # Find step
    steps = task.get('steps', [])
    step_found = None
    step_index = -1
    for i, step in enumerate(steps):
        if step['number'] == args.step:
            step_found = step
            step_index = i
            break

    if not step_found:
        output_error(f"Step {args.step} not found in TASK-{args.task}")
        return 1

    # Update step status
    step_found['status'] = 'done'
    task['updated'] = now_iso()

    # Check if all steps done
    all_done = all(s['status'] in ('done', 'skipped') for s in steps)

    # Find next step
    next_step = None
    next_step_title = None
    for step in steps:
        if step['status'] == 'pending':
            next_step = step['number']
            next_step_title = step['title']
            break

    if all_done:
        task['status'] = 'done'
        task['current_step'] = len(steps)
    elif next_step:
        task['current_step'] = next_step

    # Write back
    new_content = format_task_file(task)
    atomic_write_file(filepath, new_content)

    result = {
        'status': 'success',
        'plan_id': args.plan_id,
        'task_number': args.task,
        'step': args.step,
        'step_status': 'done',
        'task_status': task['status'],
        'next_step': next_step,
        'next_step_title': next_step_title
    }

    if all_done:
        result['message'] = 'Task completed'

    output_toon(result)
    return 0


def cmd_step_skip(args) -> int:
    """Handle 'step-skip' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find task file
    filepath = find_task_file(task_dir, args.task)
    if not filepath:
        output_error(f"Task TASK-{args.task} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    # Find step
    steps = task.get('steps', [])
    step_found = None
    for step in steps:
        if step['number'] == args.step:
            step_found = step
            break

    if not step_found:
        output_error(f"Step {args.step} not found in TASK-{args.task}")
        return 1

    # Update step status
    step_found['status'] = 'skipped'
    task['updated'] = now_iso()

    # Check if all steps done/skipped
    all_done = all(s['status'] in ('done', 'skipped') for s in steps)

    # Find next step
    next_step = None
    next_step_title = None
    for step in steps:
        if step['status'] == 'pending':
            next_step = step['number']
            next_step_title = step['title']
            break

    if all_done:
        task['status'] = 'done'
        task['current_step'] = len(steps)
    elif next_step:
        task['current_step'] = next_step

    # Write back
    new_content = format_task_file(task)
    atomic_write_file(filepath, new_content)

    result = {
        'status': 'success',
        'plan_id': args.plan_id,
        'task_number': args.task,
        'step': args.step,
        'step_status': 'skipped',
        'task_status': task['status'],
        'next_step': next_step,
        'next_step_title': next_step_title
    }

    if args.reason:
        result['reason'] = args.reason

    if all_done:
        result['message'] = 'Task completed'

    output_toon(result)
    return 0


def cmd_add_step(args) -> int:
    """Handle 'add-step' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find task file
    filepath = find_task_file(task_dir, args.task)
    if not filepath:
        output_error(f"Task TASK-{args.task} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    steps = task.get('steps', [])

    # Determine position
    if args.after is not None:
        # Insert after specified step
        insert_pos = args.after
        if insert_pos < 0 or insert_pos > len(steps):
            output_error(f"Invalid position: after step {insert_pos}")
            return 1
    else:
        # Append at end
        insert_pos = len(steps)

    # Create new step
    new_step = {
        'number': insert_pos + 1,
        'title': args.title,
        'status': 'pending'
    }

    # Insert and renumber
    steps.insert(insert_pos, new_step)
    for i, step in enumerate(steps):
        step['number'] = i + 1

    task['steps'] = steps
    task['updated'] = now_iso()

    # Write back
    new_content = format_task_file(task)
    atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'task_number': args.task,
        'step': new_step['number'],
        'step_title': new_step['title'],
        'message': f"Step added at position {new_step['number']}"
    })
    return 0


def cmd_remove_step(args) -> int:
    """Handle 'remove-step' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    # Find task file
    filepath = find_task_file(task_dir, args.task)
    if not filepath:
        output_error(f"Task TASK-{args.task} not found")
        return 1

    # Read content
    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    steps = task.get('steps', [])

    # Find step to remove
    step_index = None
    removed_step = None
    for i, step in enumerate(steps):
        if step['number'] == args.step:
            step_index = i
            removed_step = step
            break

    if step_index is None:
        output_error(f"Step {args.step} not found in TASK-{args.task}")
        return 1

    # Must have at least one step
    if len(steps) <= 1:
        output_error("Cannot remove the last step - task must have at least one step")
        return 1

    # Remove and renumber
    steps.pop(step_index)
    for i, step in enumerate(steps):
        step['number'] = i + 1

    task['steps'] = steps
    task['updated'] = now_iso()

    # Adjust current_step if needed
    if task.get('current_step', 1) > len(steps):
        task['current_step'] = len(steps)

    # Write back
    new_content = format_task_file(task)
    atomic_write_file(filepath, new_content)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'task_number': args.task,
        'step': args.step,
        'step_title': removed_step['title'],
        'message': f"Step {args.step} removed"
    })
    return 0


# ============================================================================
# CLI setup
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description='Manage implementation tasks with sequential sub-steps',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # add
    p_add = subparsers.add_parser('add', help='Add a new task')
    p_add.add_argument('--plan-id', required=True, help='Plan identifier')
    p_add.add_argument('--title', required=True, help='Task title')
    p_add.add_argument('--goal', required=True,
                       help='Specification reference (e.g., GOAL-1)')
    p_add.add_argument('--description', required=True, help='Task description')
    p_add.add_argument('--steps', nargs='+', required=True,
                       help='Step titles (space-separated, order matters)')

    # update
    p_update = subparsers.add_parser('update', help='Update an existing task')
    p_update.add_argument('--plan-id', required=True, help='Plan identifier')
    p_update.add_argument('--number', required=True, type=int, help='Task number')
    p_update.add_argument('--title', help='New title')
    p_update.add_argument('--description', help='New description')
    p_update.add_argument('--goal', help='New goal reference')
    p_update.add_argument('--status', help='New status (pending/in_progress/done/blocked)')

    # remove
    p_remove = subparsers.add_parser('remove', help='Remove a task')
    p_remove.add_argument('--plan-id', required=True, help='Plan identifier')
    p_remove.add_argument('--number', required=True, type=int, help='Task number')

    # list
    p_list = subparsers.add_parser('list', help='List all tasks')
    p_list.add_argument('--plan-id', required=True, help='Plan identifier')
    p_list.add_argument('--status', choices=['pending', 'in_progress', 'done', 'blocked', 'all'],
                        default='all', help='Filter by status')
    p_list.add_argument('--goal', help='Filter by goal reference')

    # get
    p_get = subparsers.add_parser('get', help='Get a single task')
    p_get.add_argument('--plan-id', required=True, help='Plan identifier')
    p_get.add_argument('--number', required=True, type=int, help='Task number')

    # next
    p_next = subparsers.add_parser('next', help='Get next pending task/step')
    p_next.add_argument('--plan-id', required=True, help='Plan identifier')
    p_next.add_argument('--include-context', action='store_true',
                        help='Include goal details in output')

    # step-start
    p_step_start = subparsers.add_parser('step-start', help='Mark a step as in_progress')
    p_step_start.add_argument('--plan-id', required=True, help='Plan identifier')
    p_step_start.add_argument('--task', required=True, type=int, help='Task number')
    p_step_start.add_argument('--step', required=True, type=int, help='Step number')

    # step-done
    p_step_done = subparsers.add_parser('step-done', help='Mark a step as done')
    p_step_done.add_argument('--plan-id', required=True, help='Plan identifier')
    p_step_done.add_argument('--task', required=True, type=int, help='Task number')
    p_step_done.add_argument('--step', required=True, type=int, help='Step number')

    # step-skip
    p_step_skip = subparsers.add_parser('step-skip', help='Skip a step')
    p_step_skip.add_argument('--plan-id', required=True, help='Plan identifier')
    p_step_skip.add_argument('--task', required=True, type=int, help='Task number')
    p_step_skip.add_argument('--step', required=True, type=int, help='Step number')
    p_step_skip.add_argument('--reason', help='Reason for skipping')

    # add-step
    p_add_step = subparsers.add_parser('add-step', help='Add a new step to a task')
    p_add_step.add_argument('--plan-id', required=True, help='Plan identifier')
    p_add_step.add_argument('--task', required=True, type=int, help='Task number')
    p_add_step.add_argument('--title', required=True, help='Step title')
    p_add_step.add_argument('--after', type=int, help='Insert after this step number')

    # remove-step
    p_remove_step = subparsers.add_parser('remove-step', help='Remove a step from a task')
    p_remove_step.add_argument('--plan-id', required=True, help='Plan identifier')
    p_remove_step.add_argument('--task', required=True, type=int, help='Task number')
    p_remove_step.add_argument('--step', required=True, type=int, help='Step number')

    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == 'add':
            return cmd_add(args)
        elif args.command == 'update':
            return cmd_update(args)
        elif args.command == 'remove':
            return cmd_remove(args)
        elif args.command == 'list':
            return cmd_list(args)
        elif args.command == 'get':
            return cmd_get(args)
        elif args.command == 'next':
            return cmd_next(args)
        elif args.command == 'step-start':
            return cmd_step_start(args)
        elif args.command == 'step-done':
            return cmd_step_done(args)
        elif args.command == 'step-skip':
            return cmd_step_skip(args)
        elif args.command == 'add-step':
            return cmd_add_step(args)
        elif args.command == 'remove-step':
            return cmd_remove_step(args)
        else:
            output_error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        output_error(str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
