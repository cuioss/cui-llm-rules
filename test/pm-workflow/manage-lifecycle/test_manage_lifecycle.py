#!/usr/bin/env python3
"""Tests for manage-lifecycle.py script."""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('pm-workflow', 'manage-lifecycle', 'manage-lifecycle.py')

# Import toon_parser for output parsing
TOON_PARSER_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(TOON_PARSER_DIR))
from toon_parser import parse_toon


# =============================================================================
# Test Context
# =============================================================================

class TestContext:
    """Context manager for test with temp directory."""

    def __init__(self, plan_id='test-plan'):
        self.temp_dir = None
        self.original_env = None
        self.plan_id = plan_id

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.get('PLAN_BASE_DIR')
        os.environ['PLAN_BASE_DIR'] = str(self.temp_dir)
        # Create plan directory
        plan_dir = self.temp_dir / 'plans' / self.plan_id
        plan_dir.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_env is None:
            os.environ.pop('PLAN_BASE_DIR', None)
        else:
            os.environ['PLAN_BASE_DIR'] = self.original_env
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Test: Create Command
# =============================================================================

def test_create_java_plan():
    """Test creating a plan with java type (qualified notation)."""
    with TestContext(plan_id='java-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'java-plan',
            '--title', 'Test Plan',
            '--plan-type', 'pm-workflow:plan-type-java',
            '--phases', 'init,refine,execute,finalize'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['plan']['plan_type'] == 'pm-workflow:plan-type-java'


def test_create_generic_plan():
    """Test creating a plan with generic type."""
    with TestContext(plan_id='generic-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'generic-plan',
            '--title', 'Generic Test',
            '--plan-type', 'pm-workflow:plan-type-generic',
            '--phases', 'init,execute,finalize'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_create_plan_invalid_type_format():
    """Test that creating a plan with invalid type format fails."""
    with TestContext(plan_id='bad-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'bad-plan',
            '--title', 'Bad Plan',
            '--plan-type', 'invalid-type',  # Missing bundle:skill notation
            '--phases', 'init,execute,finalize'
        )
        assert not result.success, "Expected failure for invalid plan type format"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_plan_type'


def test_create_plan_qualified_plugin_type():
    """Test creating a plan with custom bundle plan type."""
    with TestContext(plan_id='plugin-plan'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'plugin-plan',
            '--title', 'Plugin Plan',
            '--plan-type', 'pm-workflow:plan-type-plugin',
            '--phases', 'init,implement,verify,finalize'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['plan']['plan_type'] == 'pm-workflow:plan-type-plugin'


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
            '--plan-type', 'pm-workflow:plan-type-java',
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
            '--plan-type', 'pm-workflow:plan-type-java',
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
            '--plan-type', 'pm-workflow:plan-type-java',
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
            '--plan-type', 'pm-workflow:plan-type-java',
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
            '--plan-type', 'pm-workflow:plan-type-generic',
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
        test_create_plan_invalid_type_format,
        test_create_plan_qualified_plugin_type,
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
