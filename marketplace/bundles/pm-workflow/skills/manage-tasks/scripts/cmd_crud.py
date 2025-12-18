#!/usr/bin/env python3
"""
CRUD command handlers for manage-tasks.py.

Contains: add, update, remove subcommands.
"""

import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).parent
FILE_OPS_DIR = SCRIPT_DIR.parent.parent.parent.parent / 'plan-marshall' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file

from manage_tasks_shared import (
    now_iso, slugify, parse_depends_on,
    get_tasks_dir, parse_task_file, format_task_file,
    find_task_file, get_next_number,
    parse_stdin_task, output_toon, output_error
)


def cmd_add(args) -> int:
    """Handle 'add' subcommand.

    Reads task definition from stdin in TOON format.
    Only --plan-id is passed as CLI argument.
    """
    stdin_content = sys.stdin.read()
    if not stdin_content.strip():
        output_error("No task definition provided on stdin")
        return 1

    try:
        parsed = parse_stdin_task(stdin_content)
    except ValueError as e:
        output_error(str(e))
        return 1

    task_dir = get_tasks_dir(args.plan_id)

    number = get_next_number(task_dir)

    slug = slugify(parsed['title'])
    filename = f"TASK-{number:03d}-{slug}.toon"
    filepath = task_dir / filename

    steps = []
    for i, step_title in enumerate(parsed['steps'], 1):
        steps.append({
            'number': i,
            'title': step_title,
            'status': 'pending'
        })

    now = now_iso()
    task = {
        'number': number,
        'title': parsed['title'],
        'status': 'pending',
        'phase': parsed['phase'],
        'created': now,
        'updated': now,
        'deliverables': parsed['deliverables'],
        'depends_on': parsed['depends_on'],
        'description': parsed['description'],
        'delegation': parsed['delegation'],
        'verification': parsed['verification'],
        'steps': steps,
        'current_step': 1
    }

    content = format_task_file(task)
    atomic_write_file(filepath, content)

    total = len(list(task_dir.glob("TASK-*.toon")))

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': filename,
        'total_tasks': total,
        'task': {
            'number': number,
            'title': parsed['title'],
            'deliverables': parsed['deliverables'],
            'depends_on': parsed['depends_on'],
            'phase': parsed['phase'],
            'status': 'pending',
            'step_count': len(steps)
        }
    })
    return 0


def cmd_update(args) -> int:
    """Handle 'update' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    filepath = find_task_file(task_dir, args.number)
    if not filepath:
        output_error(f"Task TASK-{args.number} not found")
        return 1

    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)

    renamed = False
    old_title = task['title']

    if args.title:
        task['title'] = args.title
    if args.description:
        task['description'] = args.description
    if args.depends_on is not None:
        depends_on = []
        for dep in args.depends_on:
            if dep.lower() != 'none':
                depends_on.extend(parse_depends_on(dep))
        task['depends_on'] = depends_on
    if args.status:
        if args.status not in ('pending', 'in_progress', 'done', 'blocked'):
            output_error(f"Invalid status: {args.status}. Must be pending, in_progress, done, or blocked")
            return 1
        task['status'] = args.status

    task['updated'] = now_iso()

    new_filename = filepath.name
    if args.title and args.title != old_title:
        new_slug = slugify(args.title)
        new_filename = f"TASK-{args.number:03d}-{new_slug}.toon"
        renamed = True

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
            'status': task['status']
        }
    })
    return 0


def cmd_remove(args) -> int:
    """Handle 'remove' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)

    filepath = find_task_file(task_dir, args.number)
    if not filepath:
        output_error(f"Task TASK-{args.number} not found")
        return 1

    content = filepath.read_text(encoding='utf-8')
    task = parse_task_file(content)
    filename = filepath.name

    filepath.unlink()

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
