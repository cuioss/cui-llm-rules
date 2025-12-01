#!/usr/bin/env python3
"""
Determine next phase transition.

Usage:
    python3 transition-phase.py <plan_directory> <completed_phase>
    python3 transition-phase.py --help

Output: JSON with transition info (from_phase, to_phase, is_complete).
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
PLAN_FILES_SCRIPTS = MARKETPLACE_DIR / 'bundles' / 'planning' / 'skills' / 'plan-files' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file

# Phase orders for each plan type
# Implementation (5-phase): Full development workflow with verify phase
PHASE_ORDER_IMPLEMENTATION = ['init', 'refine', 'implement', 'verify', 'finalize']

# Plugin-Development (4-phase): Development without verify phase
PHASE_ORDER_PLUGIN_DEV = ['init', 'refine', 'execute', 'finalize']

# Simple (3-phase): Quick tasks without refine phase
PHASE_ORDER_SIMPLE = ['init', 'execute', 'finalize']

# Map plan types to phase orders
PLAN_TYPE_PHASES = {
    'implementation': PHASE_ORDER_IMPLEMENTATION,
    'plugin-development': PHASE_ORDER_PLUGIN_DEV,
    'simple': PHASE_ORDER_SIMPLE,
}


def parse_config_toon(config_file: Path) -> dict:
    """Parse config.toon for plan configuration (TOON format)."""
    if not config_file.exists():
        return {}

    content = config_file.read_text()

    config = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line and not line.endswith(':'):
            key, value = line.split(':', 1)
            config[key.strip().lower().replace(' ', '_')] = value.strip()

    return config


def get_plan_type(plan_dir: Path, plan_content: str) -> str:
    """Get plan type from config.toon, with fallback to content detection."""
    # First, try to read from config.toon
    config_file = plan_dir / 'config.toon'
    config = parse_config_toon(config_file)
    plan_type = config.get('plan_type', '').lower()

    if plan_type in PLAN_TYPE_PHASES:
        return plan_type

    # Fallback: detect from plan content (for backwards compatibility)
    if '## Phase: refine' in plan_content and '## Phase: implement' in plan_content:
        return 'implementation'
    if '## Phase: execute' in plan_content and '## Phase: refine' not in plan_content:
        return 'simple'
    if '## Phase: execute' in plan_content:
        return 'plugin-development'

    # Default to implementation
    return 'implementation'


def get_phase_order(plan_type: str) -> list:
    """Get phase order based on plan type."""
    return PLAN_TYPE_PHASES.get(plan_type, PHASE_ORDER_IMPLEMENTATION)


def parse_phase_tasks(plan_content: str, phase: str) -> dict:
    """Parse tasks for a specific phase and check completion."""
    # Find phase section
    phase_pattern = rf'## Phase: {phase}.*?\n(.*?)(?=## Phase:|## Completion Criteria|$)'
    phase_match = re.search(phase_pattern, plan_content, re.DOTALL | re.IGNORECASE)

    if not phase_match:
        return {
            'found': False,
            'tasks_total': 0,
            'tasks_completed': 0,
            'all_complete': False,
            'incomplete_items': []
        }

    phase_content = phase_match.group(1)

    # Find all checklist items with their text
    all_item_matches = re.findall(r'[-*]\s+\[([x ])\]\s*([^\n]+)', phase_content, re.IGNORECASE)

    total = len(all_item_matches)
    completed = sum(1 for mark, _ in all_item_matches if mark.lower() == 'x')

    # Extract incomplete items (those with [ ] not [x])
    incomplete_items = [
        text.strip() for mark, text in all_item_matches
        if mark == ' '
    ]

    return {
        'found': True,
        'tasks_total': total,
        'tasks_completed': completed,
        'all_complete': total > 0 and completed == total,
        'incomplete_items': incomplete_items
    }


def get_current_phase_from_plan(plan_content: str) -> str:
    """Extract current phase from plan header."""
    match = re.search(r'\*\*Current Phase\*\*:\s*(\w+)', plan_content)
    return match.group(1) if match else ''


def find_first_task_in_phase(plan_content: str, phase: str) -> str:
    """Find the first task identifier in a phase.

    Args:
        plan_content: Plan file content
        phase: Phase name to search

    Returns:
        Task identifier (e.g., "task-1") or "none" if no tasks found
    """
    # Find phase section
    phase_pattern = rf'## Phase: {re.escape(phase)}.*?(?=\n## |\Z)'
    phase_match = re.search(phase_pattern, plan_content, re.DOTALL)

    if not phase_match:
        return "none"

    phase_content = phase_match.group(0)

    # Find first task header
    task_match = re.search(r'### Task (\d+):', phase_content)
    if task_match:
        return f"task-{task_match.group(1)}"

    return "none"


def collect_modified_files(plan_dir: Path, base_branch: str = 'main') -> dict:
    """Collect modified files from git diff and add to references.toon.

    Called during phase transition from implement/execute to capture
    all files modified during the implementation phase.

    Args:
        plan_dir: Path to plan directory
        base_branch: Base branch to compare against (default: 'main')

    Returns:
        Collection result dict or None if collection failed
    """
    collect_script = PLAN_FILES_SCRIPTS / 'collect-modified-files.py'

    if not collect_script.exists():
        return {'skipped': True, 'reason': 'collect-modified-files.py not found'}

    try:
        result = subprocess.run(
            ['python3', str(collect_script),
             '--plan-dir', str(plan_dir),
             '--base-branch', base_branch],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {'skipped': True, 'reason': result.stderr or 'Collection failed'}

    except subprocess.TimeoutExpired:
        return {'skipped': True, 'reason': 'Collection timed out'}
    except json.JSONDecodeError:
        return {'skipped': True, 'reason': 'Invalid JSON from collection script'}
    except Exception as e:
        return {'skipped': True, 'reason': str(e)}


def get_base_branch_from_references(plan_dir: Path) -> str:
    """Get base branch from references.toon."""
    ref_file = plan_dir / 'references.toon'
    if not ref_file.exists():
        return 'main'

    content = ref_file.read_text()
    for line in content.splitlines():
        if line.strip().startswith('base_branch:'):
            return line.split(':', 1)[1].strip() or 'main'

    return 'main'


def update_plan_phase_pointer(plan_file: Path, plan_content: str, new_phase: str,
                               new_task: str = None) -> str:
    """Update the Current Phase and Current Task pointers in plan.md.

    Args:
        plan_file: Path to plan.md file
        plan_content: Current plan content
        new_phase: New phase to set
        new_task: New task to set (if None, finds first task in new phase)

    Returns:
        Updated plan content
    """
    # Update Current Phase pointer
    updated_content = re.sub(
        r'\*\*Current Phase\*\*:.*',
        f'**Current Phase**: {new_phase}',
        plan_content
    )

    # Determine new task
    if new_task is None:
        new_task = find_first_task_in_phase(plan_content, new_phase)

    # Update Current Task pointer
    updated_content = re.sub(
        r'\*\*Current Task\*\*:.*',
        f'**Current Task**: {new_task}',
        updated_content
    )

    # Write atomically
    atomic_write_file(plan_file, updated_content)

    return updated_content


def transition_phase(plan_directory: str, completed_phase: str) -> dict:
    """Determine next phase transition."""
    plan_dir = Path(plan_directory)
    plan_file = plan_dir / 'plan.md'

    # Validate plan file exists
    if not plan_file.exists():
        return {
            'error': {
                'type': 'plan_not_found',
                'message': f'Plan file not found: {plan_file}'
            }
        }

    plan_content = plan_file.read_text()

    # Get plan type from config.toon (or fallback to content detection)
    plan_type = get_plan_type(plan_dir, plan_content)
    phases = get_phase_order(plan_type)

    # Validate completed phase is valid
    if completed_phase not in phases:
        return {
            'error': {
                'type': 'invalid_phase',
                'message': f"Unknown phase: '{completed_phase}'",
                'valid_phases': phases,
                'plan_type': plan_type
            }
        }

    # Get current phase from plan
    current_phase = get_current_phase_from_plan(plan_content)

    # Validate completed_phase matches current
    if current_phase and current_phase != completed_phase:
        return {
            'error': {
                'type': 'phase_mismatch',
                'message': f"Cannot complete '{completed_phase}' - current phase is '{current_phase}'",
                'current_phase': current_phase,
                'requested_phase': completed_phase
            }
        }

    # Check if phase tasks are complete
    phase_status = parse_phase_tasks(plan_content, completed_phase)

    if not phase_status['found']:
        return {
            'error': {
                'type': 'phase_not_found',
                'message': f"Phase '{completed_phase}' not found in plan",
                'plan_directory': plan_directory
            }
        }

    if not phase_status['all_complete']:
        return {
            'error': {
                'type': 'incomplete_phase',
                'message': f"Phase '{completed_phase}' has incomplete tasks",
                'tasks_total': phase_status['tasks_total'],
                'tasks_completed': phase_status['tasks_completed'],
                'tasks_remaining': phase_status['tasks_total'] - phase_status['tasks_completed'],
                'incomplete_items': phase_status['incomplete_items']
            }
        }

    # Determine next phase
    phase_index = phases.index(completed_phase)
    is_last_phase = phase_index == len(phases) - 1

    if is_last_phase:
        # Plan complete - no phase pointer update needed
        return {
            'transition': {
                'from_phase': completed_phase,
                'to_phase': None,
                'success': True,
                'plan_complete': True
            },
            'plan_status': {
                'status': 'completed',
                'plan_type': plan_type,
                'phases_completed': phases
            },
            'next_action': 'Plan completed - archive or close',
            'updated': False  # No update needed for completion
        }

    # Normal transition - update plan.md phase pointer
    next_phase = phases[phase_index + 1]
    first_task = find_first_task_in_phase(plan_content, next_phase)

    # Collect modified files when transitioning from implement/execute phases
    # This captures all files changed during the implementation work
    file_collection = None
    if completed_phase in ('implement', 'execute'):
        base_branch = get_base_branch_from_references(plan_dir)
        file_collection = collect_modified_files(plan_dir, base_branch)

    # Update plan.md with new phase and task
    update_plan_phase_pointer(plan_file, plan_content, next_phase, first_task)

    result = {
        'transition': {
            'from_phase': completed_phase,
            'to_phase': next_phase,
            'success': True,
            'plan_complete': False
        },
        'plan_status': {
            'status': 'in_progress',
            'plan_type': plan_type,
            'current_phase': next_phase,
            'phases_completed': phases[:phase_index + 1],
            'phases_remaining': phases[phase_index + 1:]
        },
        'next_action': f'Execute {next_phase} phase tasks',
        'updated': True
    }

    # Include file collection results if collection was performed
    if file_collection is not None:
        result['file_collection'] = file_collection

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Determine next phase transition.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure (successful transition):
{
  "transition": {
    "from_phase": "implement",
    "to_phase": "verify",
    "success": true,
    "plan_complete": false
  },
  "plan_status": {
    "status": "in_progress",
    "plan_type": "implementation",
    "current_phase": "verify",
    "phases_completed": ["init", "refine", "implement"],
    "phases_remaining": ["verify", "finalize"]
  },
  "next_action": "Execute verify phase tasks"
}

Output JSON structure (plan complete):
{
  "transition": {
    "from_phase": "finalize",
    "to_phase": null,
    "success": true,
    "plan_complete": true
  },
  "plan_status": {
    "status": "completed",
    "plan_type": "implementation",
    "phases_completed": ["init", "refine", "implement", "verify", "finalize"]
  },
  "next_action": "Plan completed - archive or close"
}

Phase order (implementation): init -> refine -> implement -> verify -> finalize
Phase order (plugin-development): init -> refine -> execute -> finalize
Phase order (simple): init -> execute -> finalize

Note: Plan type is read from config.toon (plan_type field). Falls back to content detection.
"""
    )
    parser.add_argument('plan_directory', help='Path to plan directory')
    parser.add_argument('completed_phase', help='Phase being completed')

    args = parser.parse_args()

    result = transition_phase(args.plan_directory, args.completed_phase)
    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
