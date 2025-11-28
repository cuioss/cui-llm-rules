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
PHASE_ORDER = ['init', 'refine', 'implement', 'verify', 'finalize']

# Phase to skill mapping
PHASE_SKILL_MAP = {
    'init': 'plan-init',
    'refine': 'plan-refine',
    'implement': 'plan-implement',
    'verify': 'plan-verify',
    'finalize': 'plan-finalize'
}


def get_phase_index(phase: str) -> int:
    """Get index of phase in sequence. Returns -1 if not found."""
    try:
        return PHASE_ORDER.index(phase)
    except ValueError:
        return -1


def validate_phase_override(current_phase: str, explicit_phase: str) -> dict:
    """Validate if explicit phase override is allowed."""
    current_idx = get_phase_index(current_phase)
    explicit_idx = get_phase_index(explicit_phase)

    if current_idx == -1:
        return {
            'valid': False,
            'error': {
                'type': 'invalid_current_phase',
                'message': f"Unknown current phase: '{current_phase}'",
                'valid_phases': PHASE_ORDER
            }
        }

    if explicit_idx == -1:
        return {
            'valid': False,
            'error': {
                'type': 'invalid_explicit_phase',
                'message': f"Unknown explicit phase: '{explicit_phase}'",
                'valid_phases': PHASE_ORDER
            }
        }

    # Same phase is allowed (resume)
    if explicit_idx == current_idx:
        return {'valid': True, 'reason': 'resume_current'}

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
        return {
            'valid': False,
            'error': {
                'type': 'invalid_skip',
                'message': f"Cannot skip from '{current_phase}' to '{explicit_phase}'",
                'reason': 'Must complete phases in sequence',
                'next_valid_phase': PHASE_ORDER[current_idx + 1] if current_idx < len(PHASE_ORDER) - 1 else None
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
    current_idx = get_phase_index(current_phase)
    if current_idx == -1:
        return {
            'error': {
                'type': 'invalid_phase',
                'message': f"Unknown phase: '{current_phase}'",
                'valid_phases': PHASE_ORDER
            }
        }

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
    completed_phases = PHASE_ORDER[:current_idx]
    pending_phases = PHASE_ORDER[current_idx + 1:]

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
            'total_phases': len(PHASE_ORDER)
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
    "current_phase": "implement",
    "target_phase": "implement",
    "target_skill": "plan-implement",
    "skill_full_name": "cui-task-workflow:plan-implement"
  },
  "phase_status": {
    "completed_phases": ["init", "refine"],
    "current_phase": "implement",
    "pending_phases": ["verify", "finalize"],
    "phase_index": 2,
    "total_phases": 5
  },
  "override_applied": false
}

Phase order: init -> refine -> implement -> verify -> finalize
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
