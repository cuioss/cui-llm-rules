#!/usr/bin/env python3
"""Tests for route-phase.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-task-workflow', 'phase-management', 'route-phase.py')


# =============================================================================
# Tests - Valid Phase Routing
# =============================================================================

def test_route_init_phase():
    """Test routing init phase to plan-init skill."""
    result = run_script(SCRIPT_PATH, 'init')
    assert result.success, f"Script failed: {result.stderr}"
    data = result.json()

    assert data['routing']['current_phase'] == 'init'
    assert data['routing']['target_skill'] == 'plan-init'
    assert data['routing']['skill_full_name'] == 'cui-task-workflow:plan-init'
    assert data['phase_status']['phase_index'] == 0
    assert data['phase_status']['completed_phases'] == []
    assert 'refine' in data['phase_status']['pending_phases']


def test_route_refine_phase():
    """Test routing refine phase to plan-refine skill."""
    result = run_script(SCRIPT_PATH, 'refine')
    assert result.success
    data = result.json()

    assert data['routing']['target_skill'] == 'plan-refine'
    assert data['phase_status']['phase_index'] == 1
    assert data['phase_status']['completed_phases'] == ['init']


def test_route_implement_phase():
    """Test routing implement phase to plan-implement skill."""
    result = run_script(SCRIPT_PATH, 'implement')
    assert result.success
    data = result.json()

    assert data['routing']['target_skill'] == 'plan-implement'
    assert data['phase_status']['phase_index'] == 2
    assert 'init' in data['phase_status']['completed_phases']
    assert 'refine' in data['phase_status']['completed_phases']


def test_route_verify_phase():
    """Test routing verify phase to plan-verify skill."""
    result = run_script(SCRIPT_PATH, 'verify')
    assert result.success
    data = result.json()

    assert data['routing']['target_skill'] == 'plan-verify'
    assert data['phase_status']['phase_index'] == 3


def test_route_finalize_phase():
    """Test routing finalize phase to plan-finalize skill."""
    result = run_script(SCRIPT_PATH, 'finalize')
    assert result.success
    data = result.json()

    assert data['routing']['target_skill'] == 'plan-finalize'
    assert data['phase_status']['phase_index'] == 4
    assert data['phase_status']['pending_phases'] == []


# =============================================================================
# Tests - Phase Override
# =============================================================================

def test_override_same_phase():
    """Test explicit override to same phase (resume)."""
    result = run_script(SCRIPT_PATH, 'implement', 'implement')
    assert result.success
    data = result.json()

    assert data['routing']['target_phase'] == 'implement'
    assert data['override_applied'] is False  # Same phase = no override


def test_override_skip_fails():
    """Test that skipping phases fails."""
    result = run_script(SCRIPT_PATH, 'init', 'implement')
    assert not result.success
    data = result.json()

    assert 'error' in data
    assert data['error']['type'] == 'invalid_skip'
    assert 'Cannot skip' in data['error']['message']


def test_override_backward_fails():
    """Test that going backward fails."""
    result = run_script(SCRIPT_PATH, 'implement', 'init')
    assert not result.success
    data = result.json()

    assert 'error' in data
    assert data['error']['type'] == 'invalid_backward'


def test_override_next_phase_suggests_transition():
    """Test that requesting next phase suggests using transition."""
    result = run_script(SCRIPT_PATH, 'implement', 'verify')
    assert not result.success
    data = result.json()

    assert 'error' in data
    assert data['error']['type'] == 'use_transition'


# =============================================================================
# Tests - Invalid Input
# =============================================================================

def test_invalid_current_phase():
    """Test handling of invalid current phase."""
    result = run_script(SCRIPT_PATH, 'invalid_phase')
    assert not result.success
    data = result.json()

    assert 'error' in data
    assert data['error']['type'] == 'invalid_phase'
    assert 'valid_phases' in data['error']


def test_invalid_explicit_phase():
    """Test handling of invalid explicit phase."""
    result = run_script(SCRIPT_PATH, 'implement', 'invalid_phase')
    assert not result.success
    data = result.json()

    assert 'error' in data
    assert data['error']['type'] == 'invalid_explicit_phase'


def test_help_output():
    """Test --help output."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0
    assert 'Phase order:' in result.stdout
    assert 'init' in result.stdout
    assert 'finalize' in result.stdout


# =============================================================================
# Tests - Phase Status
# =============================================================================

def test_phase_status_structure():
    """Test that phase status contains expected fields."""
    result = run_script(SCRIPT_PATH, 'implement')
    assert result.success
    data = result.json()

    status = data['phase_status']
    assert 'completed_phases' in status
    assert 'current_phase' in status
    assert 'pending_phases' in status
    assert 'phase_index' in status
    assert 'total_phases' in status
    assert status['total_phases'] == 5


def test_all_phases_route_correctly():
    """Test that all 5 phases route to correct skills."""
    phase_skill_map = {
        'init': 'plan-init',
        'refine': 'plan-refine',
        'implement': 'plan-implement',
        'verify': 'plan-verify',
        'finalize': 'plan-finalize'
    }

    for phase, expected_skill in phase_skill_map.items():
        result = run_script(SCRIPT_PATH, phase)
        assert result.success, f"Failed for phase: {phase}"
        data = result.json()
        assert data['routing']['target_skill'] == expected_skill, f"Wrong skill for {phase}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_route_init_phase,
        test_route_refine_phase,
        test_route_implement_phase,
        test_route_verify_phase,
        test_route_finalize_phase,
        test_override_same_phase,
        test_override_skip_fails,
        test_override_backward_fails,
        test_override_next_phase_suggests_transition,
        test_invalid_current_phase,
        test_invalid_explicit_phase,
        test_help_output,
        test_phase_status_structure,
        test_all_phases_route_correctly,
    ])
    sys.exit(runner.run())
