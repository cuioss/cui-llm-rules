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
import sys
from pathlib import Path

# Phase order (strict sequence)
PHASE_ORDER = ['init', 'refine', 'implement', 'verify', 'finalize']

# Simple plan phases (alternative workflow)
SIMPLE_PHASE_ORDER = ['init', 'execute', 'finalize']


def detect_plan_type(plan_content: str) -> str:
    """Detect if plan is 'implementation' or 'simple' type."""
    # Check for refine or implement phases (only in implementation type)
    if '## Phase: refine' in plan_content or '## Phase: implement' in plan_content:
        return 'implementation'
    if '## Phase: execute' in plan_content:
        return 'simple'
    # Default to implementation
    return 'implementation'


def get_phase_order(plan_type: str) -> list:
    """Get phase order based on plan type."""
    if plan_type == 'simple':
        return SIMPLE_PHASE_ORDER
    return PHASE_ORDER


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
            'all_complete': False
        }

    phase_content = phase_match.group(1)

    # Count all checklist items
    all_items = re.findall(r'[-*]\s+\[[x ]\]', phase_content, re.IGNORECASE)
    completed_items = re.findall(r'[-*]\s+\[x\]', phase_content, re.IGNORECASE)

    total = len(all_items)
    completed = len(completed_items)

    return {
        'found': True,
        'tasks_total': total,
        'tasks_completed': completed,
        'all_complete': total > 0 and completed == total
    }


def get_current_phase_from_plan(plan_content: str) -> str:
    """Extract current phase from plan header."""
    match = re.search(r'\*\*Current Phase\*\*:\s*(\w+)', plan_content)
    return match.group(1) if match else ''


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

    # Detect plan type and get phase order
    plan_type = detect_plan_type(plan_content)
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
                'tasks_remaining': phase_status['tasks_total'] - phase_status['tasks_completed']
            }
        }

    # Determine next phase
    phase_index = phases.index(completed_phase)
    is_last_phase = phase_index == len(phases) - 1

    if is_last_phase:
        # Plan complete
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
            'next_action': 'Plan completed - archive or close'
        }

    # Normal transition
    next_phase = phases[phase_index + 1]

    return {
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
        'next_action': f'Execute {next_phase} phase tasks'
    }


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
Phase order (simple): init -> execute -> finalize
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
