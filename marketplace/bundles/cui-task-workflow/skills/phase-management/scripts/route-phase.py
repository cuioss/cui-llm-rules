#!/usr/bin/env python3
"""
Route current phase to target skill.

Usage:
    python3 route-phase.py <current_phase> [explicit_phase]
    python3 route-phase.py --help

Output: JSON with target skill and phase info.
"""

import argparse
import json
import sys

# Phase order (strict sequence)
# Note: Two plan types exist:
# - Implementation (5-phase): init → refine → implement → verify → finalize
# - Simple/Plugin-Development (3-phase): init → execute → finalize
# The 'execute' phase is equivalent to 'implement' for Simple plans
PHASE_ORDER_IMPLEMENTATION = ['init', 'refine', 'implement', 'verify', 'finalize']
PHASE_ORDER_SIMPLE = ['init', 'execute', 'finalize']

# Combined for validation (all valid phases)
ALL_VALID_PHASES = {'init', 'refine', 'implement', 'execute', 'verify', 'finalize'}

# Phase to skill mapping
# Note: 'execute' (Simple plans) routes to same skill as 'implement'
PHASE_SKILL_MAP = {
    'init': 'plan-init',
    'refine': 'plan-refine',
    'implement': 'plan-implement',
    'execute': 'plan-implement',  # Simple/Plugin-Development plans
    'verify': 'plan-verify',
    'finalize': 'plan-finalize'
}


def get_phase_order(phase: str) -> list:
    """Determine which phase order to use based on the phase."""
    if phase in ['refine', 'implement', 'verify']:
        return PHASE_ORDER_IMPLEMENTATION
    elif phase == 'execute':
        return PHASE_ORDER_SIMPLE
    else:
        # init and finalize exist in both - default to implementation
        return PHASE_ORDER_IMPLEMENTATION


def get_phase_index(phase: str, phase_order: list = None) -> int:
    """Get index of phase in sequence. Returns -1 if not found."""
    if phase_order is None:
        phase_order = get_phase_order(phase)
    try:
        return phase_order.index(phase)
    except ValueError:
        return -1


def validate_phase_override(current_phase: str, explicit_phase: str) -> dict:
    """Validate if explicit phase override is allowed."""
    # Check if phases are valid
    if current_phase not in ALL_VALID_PHASES:
        return {
            'valid': False,
            'error': {
                'type': 'invalid_current_phase',
                'message': f"Unknown current phase: '{current_phase}'",
                'valid_phases': list(ALL_VALID_PHASES)
            }
        }

    if explicit_phase not in ALL_VALID_PHASES:
        return {
            'valid': False,
            'error': {
                'type': 'invalid_explicit_phase',
                'message': f"Unknown explicit phase: '{explicit_phase}'",
                'valid_phases': list(ALL_VALID_PHASES)
            }
        }

    # Same phase is always allowed (resume)
    if explicit_phase == current_phase:
        return {'valid': True, 'reason': 'resume_current'}

    # Determine phase order based on current phase
    phase_order = get_phase_order(current_phase)
    current_idx = get_phase_index(current_phase, phase_order)
    explicit_idx = get_phase_index(explicit_phase, phase_order)

    # If explicit phase is not in the same phase order, check compatibility
    if explicit_idx == -1:
        # Mixing phase orders (e.g., trying to go from 'execute' to 'verify')
        return {
            'valid': False,
            'error': {
                'type': 'incompatible_phases',
                'message': f"Phase '{explicit_phase}' is not compatible with '{current_phase}' plan type",
                'current_phase_order': phase_order
            }
        }

    # Next phase is allowed only (handled by transition, not override)
    if explicit_idx == current_idx + 1:
        return {
            'valid': False,
            'error': {
                'type': 'use_transition',
                'message': f"Use transition-phase to move from '{current_phase}' to '{explicit_phase}'",
                'suggestion': 'Complete current phase tasks first'
            }
        }

    # Skip forward is NOT allowed
    if explicit_idx > current_idx:
        next_phase = phase_order[current_idx + 1] if current_idx < len(phase_order) - 1 else None
        return {
            'valid': False,
            'error': {
                'type': 'invalid_skip',
                'message': f"Cannot skip from '{current_phase}' to '{explicit_phase}'",
                'reason': 'Must complete phases in sequence',
                'next_valid_phase': next_phase
            }
        }

    # Going backward is NOT allowed
    return {
        'valid': False,
        'error': {
            'type': 'invalid_backward',
            'message': f"Cannot go back from '{current_phase}' to '{explicit_phase}'",
            'reason': 'Backward transitions not allowed'
        }
    }


def route_phase(current_phase: str, explicit_phase: str = None) -> dict:
    """Route phase to target skill."""
    # Validate current phase
    if current_phase not in ALL_VALID_PHASES:
        return {
            'error': {
                'type': 'invalid_phase',
                'message': f"Unknown phase: '{current_phase}'",
                'valid_phases': list(ALL_VALID_PHASES)
            }
        }

    # Determine phase order based on current phase
    phase_order = get_phase_order(current_phase)
    current_idx = get_phase_index(current_phase, phase_order)

    # If explicit phase provided, validate override
    if explicit_phase:
        validation = validate_phase_override(current_phase, explicit_phase)
        if not validation['valid']:
            return validation

    # Determine target phase
    target_phase = explicit_phase if explicit_phase else current_phase

    # Get target skill
    target_skill = PHASE_SKILL_MAP.get(target_phase)

    # Build phase status
    completed_phases = phase_order[:current_idx]
    pending_phases = phase_order[current_idx + 1:]

    return {
        'routing': {
            'current_phase': current_phase,
            'target_phase': target_phase,
            'target_skill': target_skill,
            'skill_full_name': f'cui-task-workflow:{target_skill}'
        },
        'phase_status': {
            'completed_phases': completed_phases,
            'current_phase': current_phase,
            'pending_phases': pending_phases,
            'phase_index': current_idx,
            'total_phases': len(phase_order),
            'plan_type': 'simple' if phase_order == PHASE_ORDER_SIMPLE else 'implementation'
        },
        'override_applied': explicit_phase is not None and explicit_phase != current_phase
    }


def main():
    parser = argparse.ArgumentParser(
        description='Route current phase to target skill.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "routing": {
    "current_phase": "execute",
    "target_phase": "execute",
    "target_skill": "plan-implement",
    "skill_full_name": "cui-task-workflow:plan-implement"
  },
  "phase_status": {
    "completed_phases": ["init"],
    "current_phase": "execute",
    "pending_phases": ["finalize"],
    "phase_index": 1,
    "total_phases": 3,
    "plan_type": "simple"
  },
  "override_applied": false
}

Plan types:
- Implementation (5-phase): init -> refine -> implement -> verify -> finalize
- Simple/Plugin-Development (3-phase): init -> execute -> finalize

Note: 'execute' (Simple plans) routes to the same skill as 'implement'
"""
    )
    parser.add_argument('current_phase', help='Current phase from plan.md')
    parser.add_argument(
        'explicit_phase',
        nargs='?',
        default=None,
        help='Optional explicit phase override (must be valid)'
    )

    args = parser.parse_args()

    result = route_phase(args.current_phase, args.explicit_phase)
    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
