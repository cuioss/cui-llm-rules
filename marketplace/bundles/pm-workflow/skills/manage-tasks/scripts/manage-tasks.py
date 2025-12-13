#!/usr/bin/env python3
"""
Manage implementation tasks with sequential sub-steps within a plan.

Single CLI with subcommands for CRUD operations on task files.
Uses TOON format for both storage and output.
Each task references deliverables from solution_outline.md.

Subcommands:
  add              - Add a new task (reads task definition from stdin)
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

Add command usage (stdin-based API):
  python3 manage-task.py add --plan-id my-plan <<'EOF'
  title: My Task Title
  deliverables: [1, 2, 3]
  domain: plugin
  phase: execute
  description: |
    Task description here
  steps:
    - First step
    - Second step
  depends_on: none
  delegation:
    skill: pm-plugin-development:plugin-maintain
    workflow: update-component
  verification:
    commands:
      - grep -l '```json' *.md | wc -l
    criteria: All grep commands return 0
  EOF
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
FILE_OPS_DIR = SCRIPT_DIR.parent.parent.parent.parent / 'plan-marshall' / 'skills' / 'file-operations-base' / 'scripts'
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


def validate_deliverables(deliverables_input) -> List[int]:
    """Validate deliverables list.

    Args:
        deliverables_input: List of deliverable numbers (positive integers referencing
                           solution_outline.md sections)

    Returns:
        Validated list of deliverable numbers as integers

    Raises:
        ValueError: If format is invalid or list is empty
    """
    if deliverables_input is None or len(deliverables_input) == 0:
        raise ValueError("At least one deliverable is required")

    result = []
    for item in deliverables_input:
        # Handle numeric input directly
        if isinstance(item, int):
            if item < 1:
                raise ValueError(f"Invalid deliverable number: {item}. Must be positive integer.")
            result.append(item)
        else:
            # Handle string input
            item_str = str(item).strip()
            if not item_str:
                continue
            if item_str.isdigit():
                num = int(item_str)
                if num < 1:
                    raise ValueError(f"Invalid deliverable number: {num}. Must be positive integer.")
                result.append(num)
            else:
                raise ValueError(f"Invalid deliverable format: {item_str}. Expected positive integer.")

    if len(result) == 0:
        raise ValueError("At least one deliverable is required")

    return result


# Valid domains for skill loading
VALID_DOMAINS = ['java', 'java-testing', 'javascript', 'javascript-testing', 'plugin', 'generic']

# Valid phases
VALID_PHASES = ['init', 'refine', 'execute', 'finalize']


def validate_domain(domain: str) -> str:
    """Validate domain value.

    Args:
        domain: Domain string

    Returns:
        Validated domain string

    Raises:
        ValueError: If domain is invalid
    """
    if domain not in VALID_DOMAINS:
        raise ValueError(f"Invalid domain: {domain}. Must be one of: {', '.join(VALID_DOMAINS)}")
    return domain


def validate_phase(phase: str) -> str:
    """Validate phase value.

    Args:
        phase: Phase string

    Returns:
        Validated phase string

    Raises:
        ValueError: If phase is invalid
    """
    if phase not in VALID_PHASES:
        raise ValueError(f"Invalid phase: {phase}. Must be one of: {', '.join(VALID_PHASES)}")
    return phase


# Valid file extensions for step validation
VALID_FILE_EXTENSIONS = [
    '.md', '.py', '.java', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml',
    '.xml', '.sh', '.bash', '.properties', '.adoc', '.toon', '.html', '.css'
]


def validate_steps_are_file_paths(steps: list[str]) -> tuple[list[str], list[str]]:
    """Validate that steps are file paths, not descriptive text.

    Steps MUST be file paths from the deliverable's `affected_files` section.
    This enforces the task contract from plan-type-api/standards/task-contract.md.

    Args:
        steps: List of step strings

    Returns:
        Tuple of (errors, warnings)

    Contract reference: pm-workflow:plan-type-api/standards/task-contract.md lines 156-159
    """
    errors = []
    warnings = []

    for i, step in enumerate(steps, 1):
        step = step.strip()

        # Check 1: Step must contain a path separator OR end with a known file extension
        has_path_separator = '/' in step
        has_valid_extension = any(step.endswith(ext) for ext in VALID_FILE_EXTENSIONS)

        if not has_path_separator and not has_valid_extension:
            errors.append(
                f"Step {i}: '{step[:50]}...' is not a file path. "
                f"Steps MUST be file paths from deliverable's Affected files section."
            )
            continue

        # Check 2: Warn if step looks like descriptive text (contains common verbs)
        descriptive_patterns = [
            'update ', 'create ', 'implement ', 'add ', 'fix ', 'migrate ',
            'convert ', 'modify ', 'change ', 'remove ', 'delete ',
            ' to ', ' from ', ' with ', ' for '
        ]
        step_lower = step.lower()
        for pattern in descriptive_patterns:
            if pattern in step_lower:
                warnings.append(
                    f"Step {i}: '{step[:50]}' looks like descriptive text rather than a file path."
                )
                break

    return errors, warnings


def parse_depends_on(depends_str: str) -> List[str]:
    """Parse depends_on field from TOON format.

    Args:
        depends_str: String like 'none', 'TASK-1', or 'TASK-1, TASK-2'

    Returns:
        List of task references or empty list for 'none'
    """
    if not depends_str or depends_str.strip().lower() == 'none':
        return []

    # Split by comma and clean up
    parts = [p.strip() for p in depends_str.split(',')]
    result = []
    for part in parts:
        if part.startswith('TASK-'):
            result.append(part)
        elif part.isdigit():
            result.append(f"TASK-{int(part)}")
    return result


def format_depends_on(deps: List[str]) -> str:
    """Format depends_on for file storage.

    Args:
        deps: List of task references

    Returns:
        String like 'none' or 'TASK-1, TASK-2'
    """
    if not deps:
        return 'none'
    return ', '.join(deps)


def parse_deliverables_block(lines: List[str], start_idx: int) -> Tuple[List[int], int]:
    """Parse deliverables block from TOON format.

    Args:
        lines: All lines of the file
        start_idx: Index of the 'deliverables[N]:' line

    Returns:
        Tuple of (list of deliverable numbers, next line index)
    """
    deliverables = []
    i = start_idx + 1

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('- '):
            try:
                deliverables.append(int(line[2:].strip()))
            except ValueError:
                pass
            i += 1
        elif line == '' or line.startswith('-'):
            i += 1
        else:
            break

    return deliverables, i


def parse_delegation_block(lines: List[str], start_idx: int) -> Tuple[dict, int]:
    """Parse delegation block from TOON format.

    Args:
        lines: All lines of the file
        start_idx: Index of the 'delegation:' line

    Returns:
        Tuple of (delegation dict, next line index)
    """
    delegation = {
        'skill': '',
        'workflow': '',
        'domain': '',
        'context_skills': []
    }
    i = start_idx + 1

    while i < len(lines):
        line = lines[i]
        if not line.startswith('  '):
            break

        stripped = line.strip()
        if stripped.startswith('skill:'):
            delegation['skill'] = stripped[6:].strip()
        elif stripped.startswith('workflow:'):
            delegation['workflow'] = stripped[9:].strip()
        elif stripped.startswith('domain:'):
            delegation['domain'] = stripped[7:].strip()
        elif stripped.startswith('context_skills:'):
            # Start of context_skills list
            i += 1
            while i < len(lines) and lines[i].startswith('  - '):
                skill = lines[i].strip()[2:].strip()
                if skill:
                    delegation['context_skills'].append(skill)
                i += 1
            continue
        i += 1

    return delegation, i


def parse_verification_block(lines: List[str], start_idx: int) -> Tuple[dict, int]:
    """Parse verification block from TOON format.

    Args:
        lines: All lines of the file
        start_idx: Index of the 'verification:' line

    Returns:
        Tuple of (verification dict, next line index)
    """
    verification = {
        'commands': [],
        'criteria': '',
        'manual': False
    }
    i = start_idx + 1

    while i < len(lines):
        line = lines[i]
        if not line.startswith('  '):
            break

        stripped = line.strip()
        if stripped.startswith('commands['):
            # Start of commands list
            i += 1
            while i < len(lines) and lines[i].startswith('  - '):
                cmd = lines[i].strip()[2:].strip()
                if cmd:
                    verification['commands'].append(cmd)
                i += 1
            continue
        elif stripped.startswith('criteria:'):
            verification['criteria'] = stripped[9:].strip()
        elif stripped.startswith('manual:'):
            val = stripped[7:].strip().lower()
            verification['manual'] = val == 'true'
        i += 1

    return verification, i


def get_deliverable_context(deliverables: List[int]) -> dict:
    """Get deliverable details for including in task context.

    Args:
        deliverables: List of deliverable numbers

    Returns:
        Dictionary with deliverable context (basic info only)
    """
    # Return basic context - detailed info is in solution_outline.md
    return {
        'deliverables_found': True,
        'deliverable_count': len(deliverables),
        'deliverables': deliverables,
        'deliverables_source': f'See solution_outline.md sections: {", ".join(f"### {d}." for d in deliverables)}'
    }


def parse_stdin_task(stdin_content: str) -> dict:
    """Parse task definition from stdin TOON format.

    Expected format:
        title: My Task Title
        deliverables: [1, 2, 3]
        domain: plugin
        phase: execute
        description: |
          Multi-line description
        steps:
          - First step
          - Second step
        depends_on: none | TASK-1, TASK-2
        delegation:
          skill: pm-plugin-development:plugin-maintain
          workflow: update-component
          context_skills:
            - skill1
            - skill2
        verification:
          commands:
            - command1
            - command2
          criteria: Success criteria text
          manual: false

    Args:
        stdin_content: Raw stdin content

    Returns:
        Dictionary with parsed task fields

    Raises:
        ValueError: If required fields are missing or invalid
    """
    result = {
        'title': '',
        'deliverables': [],
        'domain': '',
        'phase': 'execute',
        'description': '',
        'steps': [],
        'depends_on': [],
        'delegation': {
            'skill': '',
            'workflow': '',
            'domain': '',
            'context_skills': []
        },
        'verification': {
            'commands': [],
            'criteria': '',
            'manual': False
        }
    }

    lines = stdin_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines at top level
        if not line.strip():
            i += 1
            continue

        # Parse top-level fields
        if line.startswith('title:'):
            result['title'] = line[6:].strip()
            i += 1

        elif line.startswith('deliverables:'):
            # Parse [1, 2, 3] format
            value = line[13:].strip()
            if value.startswith('[') and value.endswith(']'):
                # Parse inline array
                inner = value[1:-1]
                if inner.strip():
                    result['deliverables'] = [int(x.strip()) for x in inner.split(',')]
            i += 1

        elif line.startswith('domain:'):
            result['domain'] = line[7:].strip()
            i += 1

        elif line.startswith('phase:'):
            result['phase'] = line[6:].strip()
            i += 1

        elif line.startswith('description:'):
            rest = line[12:].strip()
            if rest == '|':
                # Multi-line description
                desc_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].startswith('  '):
                        desc_lines.append(lines[i][2:])
                    elif lines[i].strip() == '':
                        # Empty line within description
                        desc_lines.append('')
                    else:
                        break
                    i += 1
                result['description'] = '\n'.join(desc_lines).strip()
            else:
                result['description'] = rest
                i += 1

        elif line.startswith('steps:'):
            # Parse list of steps
            i += 1
            while i < len(lines) and lines[i].startswith('  - '):
                step_title = lines[i][4:].strip()
                if step_title:
                    result['steps'].append(step_title)
                i += 1

        elif line.startswith('depends_on:'):
            value = line[11:].strip()
            result['depends_on'] = parse_depends_on(value)
            i += 1

        elif line.startswith('delegation:'):
            # Parse delegation block
            i += 1
            while i < len(lines) and lines[i].startswith('  '):
                stripped = lines[i].strip()
                if stripped.startswith('skill:'):
                    result['delegation']['skill'] = stripped[6:].strip()
                elif stripped.startswith('workflow:'):
                    result['delegation']['workflow'] = stripped[9:].strip()
                elif stripped.startswith('context_skills:'):
                    i += 1
                    while i < len(lines) and lines[i].startswith('    - '):
                        skill = lines[i][6:].strip()
                        if skill:
                            result['delegation']['context_skills'].append(skill)
                        i += 1
                    continue
                i += 1

        elif line.startswith('verification:'):
            # Parse verification block
            i += 1
            while i < len(lines) and lines[i].startswith('  '):
                stripped = lines[i].strip()
                if stripped.startswith('commands:'):
                    i += 1
                    while i < len(lines) and lines[i].startswith('    - '):
                        cmd = lines[i][6:].strip()
                        if cmd:
                            result['verification']['commands'].append(cmd)
                        i += 1
                    continue
                elif stripped.startswith('criteria:'):
                    result['verification']['criteria'] = stripped[9:].strip()
                elif stripped.startswith('manual:'):
                    val = stripped[7:].strip().lower()
                    result['verification']['manual'] = val == 'true'
                i += 1

        else:
            i += 1

    # Copy domain to delegation block
    if result['domain']:
        result['delegation']['domain'] = result['domain']

    # Validate required fields
    if not result['title']:
        raise ValueError("Missing required field: title")
    if not result['deliverables']:
        raise ValueError("Missing required field: deliverables")
    if not result['domain']:
        raise ValueError("Missing required field: domain")
    if not result['steps']:
        raise ValueError("Missing required field: steps (at least one step required)")

    # Validate domain
    validate_domain(result['domain'])

    # Validate phase
    validate_phase(result['phase'])

    # Validate deliverables
    validate_deliverables(result['deliverables'])

    # Validate steps are file paths (task contract enforcement)
    step_errors, step_warnings = validate_steps_are_file_paths(result['steps'])
    if step_errors:
        raise ValueError(
            "Task contract violation - steps must be file paths:\n" +
            "\n".join(step_errors) +
            "\n\nContract reference: pm-workflow:plan-type-api/standards/task-contract.md"
        )

    return result


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
        Dictionary with task fields including steps, deliverables, delegation, verification
    """
    result = {
        'steps': [],
        'deliverables': [],
        'depends_on': [],
        'delegation': {
            'skill': '',
            'workflow': '',
            'domain': '',
            'context_skills': []
        },
        'verification': {
            'commands': [],
            'criteria': '',
            'manual': False
        }
    }
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
        elif line.startswith('deliverables['):
            # Parse deliverables block
            result['deliverables'], i = parse_deliverables_block(lines, i)
        elif line.startswith('delegation:'):
            # Parse delegation block
            result['delegation'], i = parse_delegation_block(lines, i)
        elif line.startswith('verification:'):
            # Parse verification block
            result['verification'], i = parse_verification_block(lines, i)
        elif line.startswith('steps['):
            # Parse steps table header: steps[N]{number,title,status}:
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('current_step:') and not lines[i].startswith('verification:'):
                parts = lines[i].split(',', 2)
                if len(parts) == 3:
                    result['steps'].append({
                        'number': int(parts[0]),
                        'title': parts[1],
                        'status': parts[2]
                    })
                i += 1
        elif line.startswith('depends_on:'):
            # Parse depends_on field
            value = line[11:].strip()
            result['depends_on'] = parse_depends_on(value)
            i += 1
        elif ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Convert numeric fields to int
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
        task: Task dictionary with steps, deliverables, delegation, verification

    Returns:
        TOON formatted string
    """
    lines = [
        f"number: {task['number']}",
        f"title: {task['title']}",
        f"status: {task['status']}",
        f"phase: {task.get('phase', 'execute')}",
        f"created: {task['created']}",
        f"updated: {task['updated']}",
        "",
    ]

    # Add deliverables block
    deliverables = task.get('deliverables', [])
    lines.append(f"deliverables[{len(deliverables)}]:")
    for d in deliverables:
        lines.append(f"- {d}")

    lines.append("")

    # Add depends_on
    depends_on = task.get('depends_on', [])
    lines.append(f"depends_on: {format_depends_on(depends_on)}")

    lines.append("")

    # Add description
    lines.append("description: |")
    for desc_line in task.get('description', '').split('\n'):
        lines.append(f"  {desc_line}")

    lines.append("")

    # Add delegation block
    delegation = task.get('delegation', {})
    lines.append("delegation:")
    lines.append(f"  skill: {delegation.get('skill', '')}")
    lines.append(f"  workflow: {delegation.get('workflow', '')}")
    lines.append(f"  domain: {delegation.get('domain', '')}")
    context_skills = delegation.get('context_skills', [])
    if context_skills:
        lines.append("  context_skills:")
        for skill in context_skills:
            lines.append(f"  - {skill}")

    lines.append("")

    # Add steps table
    steps = task.get('steps', [])
    lines.append(f"steps[{len(steps)}]{{number,title,status}}:")
    for step in steps:
        lines.append(f"{step['number']},{step['title']},{step['status']}")

    lines.append("")

    # Add verification block
    verification = task.get('verification', {})
    lines.append("verification:")
    commands = verification.get('commands', [])
    lines.append(f"  commands[{len(commands)}]:")
    for cmd in commands:
        lines.append(f"  - {cmd}")
    lines.append(f"  criteria: {verification.get('criteria', '')}")
    lines.append(f"  manual: {'true' if verification.get('manual', False) else 'false'}")

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


def format_list_value(val) -> str:
    """Format a list value for TOON output."""
    if isinstance(val, list):
        return f"[{', '.join(str(v) for v in val)}]"
    return str(val)


def output_toon(data: dict) -> None:
    """Print TOON formatted output."""
    lines = []

    # Top-level simple fields
    for key in ['status', 'plan_id', 'file', 'renamed', 'total_tasks', 'task_number', 'step', 'phase_filter']:
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
            if isinstance(v, dict):
                # Handle nested dict like by_phase
                lines.append(f"  {k}:")
                for k2, v2 in v.items():
                    lines.append(f"    {k2}: {v2}")
            else:
                lines.append(f"  {k}: {v}")

    # Single task block
    if 'task' in data:
        lines.append("")
        lines.append("task:")
        task = data['task']
        for key in ['number', 'title', 'phase', 'status', 'current_step', 'created', 'updated', 'step_count']:
            if key in task:
                lines.append(f"  {key}: {task[key]}")
        # Handle deliverables array
        if 'deliverables' in task:
            lines.append(f"  deliverables: {format_list_value(task['deliverables'])}")
        # Handle depends_on array
        if 'depends_on' in task:
            deps = task['depends_on']
            if deps:
                lines.append(f"  depends_on: {format_list_value(deps)}")
            else:
                lines.append("  depends_on: none")
        if 'description' in task:
            lines.append(f"  description: {task['description']}")
        # Handle delegation block
        if 'delegation' in task:
            deleg = task['delegation']
            lines.append("  delegation:")
            lines.append(f"    skill: {deleg.get('skill', '')}")
            lines.append(f"    workflow: {deleg.get('workflow', '')}")
            lines.append(f"    domain: {deleg.get('domain', '')}")
            ctx_skills = deleg.get('context_skills', [])
            if ctx_skills:
                lines.append(f"    context_skills: {format_list_value(ctx_skills)}")
        if 'steps' in task:
            steps = task['steps']
            lines.append(f"  steps[{len(steps)}]{{number,title,status}}:")
            for s in steps:
                lines.append(f"  {s['number']},{s['title']},{s['status']}")
        # Handle verification block
        if 'verification' in task:
            verif = task['verification']
            lines.append("  verification:")
            cmds = verif.get('commands', [])
            lines.append(f"    commands[{len(cmds)}]:")
            for cmd in cmds:
                lines.append(f"    - {cmd}")
            lines.append(f"    criteria: {verif.get('criteria', '')}")
            lines.append(f"    manual: {'true' if verif.get('manual', False) else 'false'}")

    # Removed block
    if 'removed' in data:
        lines.append("")
        lines.append("removed:")
        rem = data['removed']
        for key in ['number', 'title', 'file']:
            if key in rem:
                lines.append(f"  {key}: {rem[key]}")

    # Blocked tasks block
    if 'blocked_tasks' in data:
        blocked = data['blocked_tasks']
        lines.append("")
        lines.append(f"blocked_tasks[{len(blocked)}]{{number,title,waiting_for}}:")
        for bt in blocked:
            lines.append(f"{bt['number']},{bt['title']},{bt['waiting_for']}")

    # Next block
    if 'next' in data:
        lines.append("")
        if data['next'] is None:
            lines.append("next: null")
        else:
            lines.append("next:")
            nxt = data['next']
            for key in ['task_number', 'task_title', 'phase', 'step_number', 'step_title',
                        'deliverables_found', 'deliverable_count', 'deliverables_source']:
                if key in nxt:
                    val = nxt[key]
                    # Convert Python booleans to lowercase for TOON format
                    if isinstance(val, bool):
                        val = 'true' if val else 'false'
                    lines.append(f"  {key}: {val}")
            # Handle deliverables array
            if 'deliverables' in nxt:
                lines.append(f"  deliverables: {format_list_value(nxt['deliverables'])}")

    # Context block
    if 'context' in data:
        lines.append("")
        lines.append("context:")
        ctx = data['context']
        for k, v in ctx.items():
            lines.append(f"  {k}: {v}")

    # Tasks list (tabular) - updated format with phase and deliverables
    if 'tasks_table' in data:
        tasks = data['tasks_table']
        lines.append("")
        lines.append(f"tasks[{len(tasks)}]{{number,title,phase,deliverables,status,progress}}:")
        for t in tasks:
            delivs = format_list_value(t.get('deliverables', []))
            lines.append(f"{t['number']},{t['title']},{t.get('phase', 'execute')},{delivs},{t['status']},{t['progress']}")

    print('\n'.join(lines))


def output_error(message: str) -> None:
    """Print TOON error output to stderr."""
    print(f"status: error\nmessage: {message}", file=sys.stderr)


# ============================================================================
# Subcommand handlers
# ============================================================================

def cmd_add(args) -> int:
    """Handle 'add' subcommand.

    Reads task definition from stdin in TOON format.
    Only --plan-id is passed as CLI argument.
    """
    # Read task definition from stdin
    stdin_content = sys.stdin.read()
    if not stdin_content.strip():
        output_error("No task definition provided on stdin")
        return 1

    # Parse stdin content
    try:
        parsed = parse_stdin_task(stdin_content)
    except ValueError as e:
        output_error(str(e))
        return 1

    task_dir = get_tasks_dir(args.plan_id)

    # Get next number
    number = get_next_number(task_dir)

    # Generate slug and filename
    slug = slugify(parsed['title'])
    filename = f"TASK-{number:03d}-{slug}.toon"
    filepath = task_dir / filename

    # Create steps
    steps = []
    for i, step_title in enumerate(parsed['steps'], 1):
        steps.append({
            'number': i,
            'title': step_title,
            'status': 'pending'
        })

    # Create task
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
    if args.depends_on is not None:
        # Parse depends_on - handle 'none' or task references
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

    # Build set of done task numbers for dependency checking
    done_tasks = {f"TASK-{t['number']}" for _, t in all_tasks if t.get('status') == 'done'}

    # Filter by phase if specified
    if args.phase:
        all_tasks = [
            (p, t) for p, t in all_tasks
            if t.get('phase', 'execute') == args.phase
        ]

    # Filter by deliverable if specified
    if args.deliverable:
        all_tasks = [
            (p, t) for p, t in all_tasks
            if args.deliverable in t.get('deliverables', [])
        ]

    # Filter by ready (dependencies satisfied) if specified
    if args.ready:
        all_tasks = [
            (p, t) for p, t in all_tasks
            if all(dep in done_tasks for dep in t.get('depends_on', []))
        ]

    # Get filtered list for status filtering
    filtered_tasks = all_tasks
    if args.status and args.status != 'all':
        filtered_tasks = [(p, t) for p, t in all_tasks if t.get('status') == args.status]

    # Compute counts from filtered list
    pending = sum(1 for _, t in all_tasks if t.get('status') == 'pending')
    in_progress = sum(1 for _, t in all_tasks if t.get('status') == 'in_progress')
    done_count = sum(1 for _, t in all_tasks if t.get('status') == 'done')
    blocked = sum(1 for _, t in all_tasks if t.get('status') == 'blocked')

    # Compute counts by phase
    by_phase = {}
    for _, t in all_tasks:
        phase = t.get('phase', 'execute')
        by_phase[phase] = by_phase.get(phase, 0) + 1

    # Build table data
    table = []
    for path, task in filtered_tasks:
        completed, total = calculate_progress(task)
        deliverables = task.get('deliverables', [])
        table.append({
            'number': task['number'],
            'title': task['title'],
            'phase': task.get('phase', 'execute'),
            'deliverables': deliverables,
            'status': task['status'],
            'progress': f"{completed}/{total}"
        })

    result = {
        'status': 'success',
        'plan_id': args.plan_id,
        'phase_filter': args.phase if args.phase else 'all',
        'counts': {
            'total': len(all_tasks),
            'pending': pending,
            'in_progress': in_progress,
            'done': done_count,
            'blocked': blocked
        },
        'tasks_table': table
    }

    # Add by_phase counts if showing all phases
    if not args.phase and by_phase:
        result['counts']['by_phase'] = by_phase

    output_toon(result)
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
            'deliverables': task.get('deliverables', []),
            'depends_on': task.get('depends_on', []),
            'phase': task.get('phase', 'execute'),
            'status': task['status'],
            'current_step': task.get('current_step', 1),
            'created': task.get('created', ''),
            'updated': task.get('updated', ''),
            'description': task.get('description', ''),
            'delegation': task.get('delegation', {}),
            'steps': task.get('steps', []),
            'verification': task.get('verification', {})
        }
    })
    return 0


def cmd_next(args) -> int:
    """Handle 'next' subcommand."""
    task_dir = get_tasks_dir(args.plan_id)
    all_tasks = get_all_tasks(task_dir)

    # Build set of done task numbers for dependency checking
    done_tasks = {f"TASK-{t['number']}" for _, t in all_tasks if t.get('status') == 'done'}

    # Filter by phase if specified
    filtered_tasks = all_tasks
    if args.phase:
        filtered_tasks = [
            (p, t) for p, t in all_tasks
            if t.get('phase', 'execute') == args.phase
        ]

    total_tasks = len(filtered_tasks)
    completed_tasks = sum(1 for _, t in filtered_tasks if t.get('status') == 'done')
    in_progress_count = sum(1 for _, t in filtered_tasks if t.get('status') == 'in_progress')

    # Helper to check if dependencies are satisfied
    def deps_satisfied(task):
        if getattr(args, 'ignore_deps', False):
            return True
        deps = task.get('depends_on', [])
        return all(dep in done_tasks for dep in deps)

    # Find first in_progress or pending task with satisfied dependencies
    next_task = None
    blocked_tasks = []

    # First, look for in_progress tasks
    for path, task in filtered_tasks:
        if task.get('status') == 'in_progress':
            next_task = task
            break

    # If no in_progress, find first pending with satisfied deps
    if not next_task:
        for path, task in filtered_tasks:
            if task.get('status') == 'pending':
                if deps_satisfied(task):
                    next_task = task
                    break
                else:
                    # Track blocked tasks
                    waiting_for = [dep for dep in task.get('depends_on', []) if dep not in done_tasks]
                    blocked_tasks.append({
                        'number': task['number'],
                        'title': task['title'],
                        'waiting_for': ', '.join(waiting_for)
                    })

    if not next_task:
        # Check if blocked by dependencies or all done
        if blocked_tasks:
            output_toon({
                'status': 'success',
                'plan_id': args.plan_id,
                'next': None,
                'blocked_tasks': blocked_tasks,
                'context': {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'in_progress': in_progress_count,
                    'blocked_by_deps': len(blocked_tasks),
                    'message': 'Waiting for in-progress tasks to complete'
                }
            })
        else:
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

    for step in steps:
        if step['status'] in ('done', 'skipped'):
            completed_steps += 1
        elif step['status'] == 'in_progress':
            next_step = step
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
            'phase': next_task.get('phase', 'execute'),
            'deliverables': next_task.get('deliverables', []),
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

    # Include deliverable context if requested
    if getattr(args, 'include_context', False):
        deliverables = next_task.get('deliverables', [])
        if deliverables:
            deliverable_context = get_deliverable_context(deliverables)
            result['next'].update(deliverable_context)

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

    # add (stdin-based API)
    p_add = subparsers.add_parser('add', help='Add a new task (reads definition from stdin)')
    p_add.add_argument('--plan-id', required=True, help='Plan identifier')

    # update
    p_update = subparsers.add_parser('update', help='Update an existing task')
    p_update.add_argument('--plan-id', required=True, help='Plan identifier')
    p_update.add_argument('--number', required=True, type=int, help='Task number')
    p_update.add_argument('--title', help='New title')
    p_update.add_argument('--description', help='New description')
    p_update.add_argument('--depends-on', nargs='*',
                          help='Update dependencies (TASK-N references or "none" to clear)')
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
    p_list.add_argument('--phase', choices=['init', 'refine', 'execute', 'finalize'],
                        help='Filter by phase')
    p_list.add_argument('--deliverable', type=int, help='Filter by deliverable number')
    p_list.add_argument('--ready', action='store_true',
                        help='Only show tasks with no unmet dependencies')

    # get
    p_get = subparsers.add_parser('get', help='Get a single task')
    p_get.add_argument('--plan-id', required=True, help='Plan identifier')
    p_get.add_argument('--number', required=True, type=int, help='Task number')

    # next
    p_next = subparsers.add_parser('next', help='Get next pending task/step')
    p_next.add_argument('--plan-id', required=True, help='Plan identifier')
    p_next.add_argument('--phase', choices=['init', 'refine', 'execute', 'finalize'],
                        help='Filter by phase')
    p_next.add_argument('--include-context', action='store_true',
                        help='Include deliverable details in output')
    p_next.add_argument('--ignore-deps', action='store_true',
                        help='Ignore dependency constraints')

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
