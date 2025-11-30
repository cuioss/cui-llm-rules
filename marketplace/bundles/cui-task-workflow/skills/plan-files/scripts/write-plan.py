#!/usr/bin/env python3
"""
Create or update plan.md from structured input.

Creates a plan file with phase progress table and task sections.
Uses atomic file operations to write to .plan/plans/ directory.

Output: JSON with created/updated file path.
"""

import argparse
import json
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
# Navigate: scripts -> plan-files -> skills -> cui-task-workflow -> bundles -> marketplace -> bundles -> cui-utilities -> skills -> file-operations-base -> scripts
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]  # marketplace/bundles/cui-task-workflow/skills/plan-files -> marketplace
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'cui-utilities' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, ensure_directory, output_success, output_error


def generate_phase_progress_table(phases: list[dict]) -> str:
    """Generate the phase progress table.

    Args:
        phases: List of phase dicts with name, status, tasks, completed

    Returns:
        Formatted markdown table
    """
    lines = [
        "| Phase | Status | Tasks | Completed |",
        "|-------|--------|-------|-----------|"
    ]

    for phase in phases:
        name = phase.get('name', '')
        status = phase.get('status', 'pending')
        tasks = phase.get('tasks', 0)
        completed = phase.get('completed', 0)
        lines.append(f"| {name} | {status} | {tasks} | {completed}/{tasks} |")

    return '\n'.join(lines)


def generate_task_section(task: dict, task_num: int) -> str:
    """Generate a task section.

    Args:
        task: Task dict with name, phase, goal, acceptance_criteria, checklist
        task_num: Task number

    Returns:
        Formatted markdown section
    """
    name = task.get('name', f'Task {task_num}')
    phase = task.get('phase', '')
    goal = task.get('goal', '')
    criteria = task.get('acceptance_criteria', [])
    checklist = task.get('checklist', [])

    lines = [
        f"### Task {task_num}: {name}",
        "",
        f"**Phase**: {phase}",
        f"**Goal**: {goal}",
        ""
    ]

    if criteria:
        lines.append("**Acceptance Criteria**:")
        for c in criteria:
            lines.append(f"- {c}")
        lines.append("")

    if checklist:
        lines.append("**Checklist**:")
        for item in checklist:
            if isinstance(item, str):
                text = item
                checked = False
                # Parse existing checkbox marker from string
                if text.startswith('[x] '):
                    checked = True
                    text = text[4:]  # Remove "[x] " prefix
                elif text.startswith('[ ] '):
                    checked = False
                    text = text[4:]  # Remove "[ ] " prefix
                elif text.startswith('x '):
                    # Handle bare "x " prefix as checked item
                    checked = True
                    text = text[2:]  # Remove "x " prefix
            elif isinstance(item, dict):
                checked = item.get('done', False)
                text = item.get('text', '')
            else:
                text = str(item)
                checked = False
            mark = "x" if checked else " "
            lines.append(f"- [{mark}] {text}")
        lines.append("")

    return '\n'.join(lines)


def generate_plan_content(
    title: str,
    current_phase: str,
    current_task: str,
    phases: list[dict]
) -> str:
    """Generate complete plan.md content.

    Args:
        title: Plan title
        current_phase: Current phase name
        current_task: Current task ID
        phases: List of phase dicts, each containing:
            - name: phase name
            - status: pending|in_progress|completed
            - tasks: count or list of task dicts

    Returns:
        Complete plan markdown content
    """
    # Build phase list for progress table
    phase_summary = []
    phase_sections = []

    for phase in phases:
        name = phase.get('name', '')
        status = phase.get('status', 'pending')
        tasks = phase.get('tasks', [])

        # Handle tasks as either count or list
        if isinstance(tasks, int):
            task_count = tasks
            task_list = []
        else:
            task_count = len(tasks)
            task_list = tasks

        # Count completed
        completed = sum(1 for t in task_list if t.get('status') == 'completed') if task_list else 0

        phase_summary.append({
            'name': name,
            'status': status,
            'tasks': task_count,
            'completed': completed
        })

        # Generate phase section
        if task_list:
            section_lines = [
                f"## Phase: {name} ({status})",
                ""
            ]
            for i, task in enumerate(task_list, 1):
                section_lines.append(generate_task_section(task, i))
            section_lines.append("---")
            section_lines.append("")
            phase_sections.append('\n'.join(section_lines))
        elif task_count > 0:
            # Placeholder for dynamic tasks
            section_lines = [
                f"## Phase: {name} ({status})",
                "",
                "{Tasks generated dynamically}",
                "",
                "---",
                ""
            ]
            phase_sections.append('\n'.join(section_lines))

    # Build full content
    content_parts = [
        f"# Task Plan: {title}",
        "",
        "**Configuration**: See [config.toon](./config.toon)",
        "**References**: See [references.toon](./references.toon)",
        "",
        f"**Current Phase**: {current_phase}",
        f"**Current Task**: {current_task}",
        "",
        "---",
        "",
        "## Phase Progress",
        "",
        generate_phase_progress_table(phase_summary),
        "",
        "---",
        ""
    ]

    # Add phase sections
    for section in phase_sections:
        content_parts.append(section)

    # Add completion criteria
    content_parts.extend([
        "## Completion Criteria",
        "",
        "All phases must be completed and all tasks marked with `[x]` before plan is complete.",
        "",
        "**Final Verification**:",
        "- [ ] All phases completed",
        "- [ ] All acceptance criteria met",
        "- [ ] All tests passing",
        "- [ ] Build successful",
        "- [ ] Documentation updated",
        "- [ ] PR merged (if applicable)",
        ""
    ])

    return '\n'.join(content_parts)


def main():
    parser = argparse.ArgumentParser(
        description='Create or update plan.md from structured input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create simple plan
  %(prog)s --plan-dir .plan/plans/my-task \\
           --title "My Task" \\
           --current-phase init \\
           --current-task task-1 \\
           --phases-json '[{"name":"init","status":"in_progress","tasks":3}]'

  # Create plan with detailed tasks
  %(prog)s --plan-dir .plan/plans/my-task \\
           --title "Feature Implementation" \\
           --current-phase init \\
           --current-task task-1 \\
           --phases-json '[
             {"name":"init","status":"in_progress","tasks":[
               {"name":"Setup","phase":"init","goal":"Setup environment","checklist":["Install deps","Configure tools"]}
             ]},
             {"name":"implement","status":"pending","tasks":5}
           ]'
"""
    )

    parser.add_argument('--plan-dir', required=True,
                        help='Directory for plan files')
    parser.add_argument('--title', required=True,
                        help='Plan title')
    parser.add_argument('--current-phase', required=True,
                        help='Current phase name')
    parser.add_argument('--current-task', required=True,
                        help='Current task identifier')
    parser.add_argument('--phases-json', required=True,
                        help='JSON array of phase objects')

    args = parser.parse_args()

    try:
        plan_dir = Path(args.plan_dir)

        # Ensure directory exists
        ensure_directory(plan_dir)

        # Parse phases JSON
        try:
            phases = json.loads(args.phases_json)
        except json.JSONDecodeError as e:
            output_error('write-plan', f"Invalid phases JSON: {e}")
            return 1

        # Generate content
        content = generate_plan_content(
            title=args.title,
            current_phase=args.current_phase,
            current_task=args.current_task,
            phases=phases
        )

        # Write file
        file_path = plan_dir / "plan.md"
        atomic_write_file(file_path, content)

        output_success(
            'write-plan',
            file=str(file_path),
            title=args.title,
            current_phase=args.current_phase
        )
        return 0

    except Exception as e:
        output_error('write-plan', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
