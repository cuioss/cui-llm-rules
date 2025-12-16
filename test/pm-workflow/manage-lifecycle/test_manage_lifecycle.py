#!/usr/bin/env python3
"""Tests for manage-lifecycle.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, PlanTestContext

# Get script path
SCRIPT_PATH = get_script_path('pm-workflow', 'manage-lifecycle', 'manage-lifecycle.py')

# Import toon_parser for output parsing
TOON_PARSER_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(TOON_PARSER_DIR))
from toon_parser import parse_toon


# Alias for backward compatibility
TestContext = PlanTestContext


# =============================================================================
# Test: Create Command
# =============================================================================

def test_create_java_plan():
    """Test creating a plan with java domain."""
    with TestContext(plan_id='java-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'java-plan',
            '--title', 'Test Plan',
            '--domain', 'java',
            '--phases', 'init,refine,execute,finalize'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['plan']['domain'] == 'java'


def test_create_generic_plan():
    """Test creating a plan with generic domain."""
    with TestContext(plan_id='generic-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'generic-plan',
            '--title', 'Generic Test',
            '--domain', 'generic',
            '--phases', 'init,execute,finalize'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_create_plan_invalid_domain():
    """Test that creating a plan with invalid domain fails."""
    with TestContext(plan_id='bad-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'bad-plan',
            '--title', 'Bad Plan',
            '--domain', 'invalid-domain',  # Not a valid domain
            '--phases', 'init,execute,finalize'
        )
        assert not result.success, "Expected failure for invalid domain"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_domain'


def test_create_plugin_plan():
    """Test creating a plan with plan-marshall-plugin-dev domain."""
    with TestContext(plan_id='plugin-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'plugin-plan',
            '--title', 'Plugin Plan',
            '--domain', 'plan-marshall-plugin-dev',
            '--phases', 'init,implement,verify,finalize'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['plan']['domain'] == 'plan-marshall-plugin-dev'


# =============================================================================
# Test: Phase Operations
# =============================================================================

def test_set_phase():
    """Test setting phase."""
    with TestContext(plan_id='phase-plan'):
        # First create the plan
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'phase-plan',
            '--title', 'Phase Test',
            '--domain', 'java',
            '--phases', 'init,refine,execute,finalize'
        )
        # Then set phase
        result = run_script(SCRIPT_PATH, 'set-phase',
            '--plan-id', 'phase-plan',
            '--phase', 'execute'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_read_plan():
    """Test reading plan status."""
    with TestContext(plan_id='read-plan'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'read-plan',
            '--title', 'Read Test',
            '--domain', 'java',
            '--phases', 'init,refine,execute,finalize'
        )
        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'read-plan'
        )
        assert result.success, f"Script failed: {result.stderr}"


# =============================================================================
# Test: Get Routing Context
# =============================================================================

def test_get_routing_context():
    """Test getting routing context combines phase, skill, and progress."""
    with TestContext(plan_id='routing-plan'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'routing-plan',
            '--title', 'Routing Test',
            '--domain', 'java',
            '--phases', 'init,refine,execute,finalize'
        )
        result = run_script(SCRIPT_PATH, 'get-routing-context',
            '--plan-id', 'routing-plan'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        # Should have current phase
        assert data['current_phase'] == 'init'
        # Should have skill routing
        assert data['skill'] == 'plan-init'
        # Should have progress
        assert 'total_phases' in data
        assert 'completed_phases' in data


def test_get_routing_context_after_transition():
    """Test routing context updates after phase transition."""
    with TestContext(plan_id='transition-routing'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'transition-routing',
            '--title', 'Transition Test',
            '--domain', 'java',
            '--phases', 'init,refine,execute,finalize'
        )
        run_script(SCRIPT_PATH, 'transition',
            '--plan-id', 'transition-routing',
            '--completed', 'init'
        )
        result = run_script(SCRIPT_PATH, 'get-routing-context',
            '--plan-id', 'transition-routing'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['current_phase'] == 'refine'
        assert data['skill'] == 'plan-refine'
        assert data['completed_phases'] == 1


def test_get_routing_context_not_found():
    """Test get-routing-context with missing plan."""
    with TestContext():
        result = run_script(SCRIPT_PATH, 'get-routing-context',
            '--plan-id', 'nonexistent'
        )
        assert not result.success, "Expected failure for missing plan"


# =============================================================================
# Test: List Command
# =============================================================================

def test_list_empty():
    """Test listing when no plans exist."""
    with TestContext():
        result = run_script(SCRIPT_PATH, 'list')
        assert result.success, f"Script failed: {result.stderr}"


def test_list_with_plan():
    """Test listing when a plan exists."""
    with TestContext(plan_id='list-plan'):
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'list-plan',
            '--title', 'List Test',
            '--domain', 'generic',
            '--phases', 'init,execute,finalize'
        )
        result = run_script(SCRIPT_PATH, 'list')
        assert result.success, f"Script failed: {result.stderr}"


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Create command
        test_create_java_plan,
        test_create_generic_plan,
        test_create_plan_invalid_domain,
        test_create_plugin_plan,
        # Phase operations
        test_set_phase,
        test_read_plan,
        # Get routing context
        test_get_routing_context,
        test_get_routing_context_after_transition,
        test_get_routing_context_not_found,
        # List command
        test_list_empty,
        test_list_with_plan,
    ])
    sys.exit(runner.run())
