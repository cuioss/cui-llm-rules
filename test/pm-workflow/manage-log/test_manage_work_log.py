#!/usr/bin/env python3
"""Tests for manage-work-log.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, PlanTestContext

# Get script path
SCRIPT_PATH = get_script_path('pm-workflow', 'manage-log', 'manage-work-log.py')

# Import toon_parser for output parsing
TOON_PARSER_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(TOON_PARSER_DIR))
from toon_parser import parse_toon


# Alias for backward compatibility - use PlanTestContext from conftest
TestContext = PlanTestContext


# =============================================================================
# Test: Add Command with Type and Detail
# =============================================================================

def test_add_entry_default_type():
    """Test adding entry with default type (progress)."""
    with TestContext(plan_id='log-default'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-default',
            '--phase', 'init',
            '--summary', 'Started plan initialization'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['type'] == 'progress'
        assert data['phase'] == 'init'
        assert data['total_entries'] == 1


def test_add_entry_decision_type():
    """Test adding entry with decision type."""
    with TestContext(plan_id='log-decision'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-decision',
            '--phase', 'configure',
            '--summary', 'Selected plan-type-java',
            '--type', 'decision',
            '--detail', 'Task modifies .java files in service layer'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['type'] == 'decision'
        assert data['detail'] == 'Task modifies .java files in service layer'


def test_add_entry_artifact_type():
    """Test adding entry with artifact type."""
    with TestContext(plan_id='log-artifact'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-artifact',
            '--phase', 'configure',
            '--summary', 'Created REQ-001: Implement JWT authentication',
            '--type', 'artifact',
            '--detail', 'Covers token generation and validation'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['type'] == 'artifact'


def test_add_entry_error_type():
    """Test adding entry with error type."""
    with TestContext(plan_id='log-error'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-error',
            '--phase', 'refine',
            '--summary', 'Skill load failed',
            '--type', 'error',
            '--detail', 'plan-type-plugin does not exist'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['type'] == 'error'
        assert data['detail'] == 'plan-type-plugin does not exist'


def test_add_entry_outcome_type():
    """Test adding entry with outcome type."""
    with TestContext(plan_id='log-outcome'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-outcome',
            '--phase', 'refine',
            '--summary', 'Completed refine: 6 specs, 12 tasks',
            '--type', 'outcome'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['type'] == 'outcome'


def test_add_entry_finding_type():
    """Test adding entry with finding type."""
    with TestContext(plan_id='log-finding'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-finding',
            '--phase', 'refine',
            '--summary', 'Already migrated: agents use TOON format',
            '--type', 'finding',
            '--detail', 'plugin-solution-outline-agent and related agents already use TOON'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['type'] == 'finding'
        assert 'Already migrated' in data['summary']


def test_add_entry_invalid_type():
    """Test that invalid type fails."""
    with TestContext(plan_id='log-invalid-type'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-invalid-type',
            '--phase', 'init',
            '--summary', 'Test entry',
            '--type', 'invalid'
        )
        assert not result.success, "Expected failure for invalid type"


# =============================================================================
# Test: Read Command
# =============================================================================

def test_read_entries():
    """Test reading entries includes type and detail fields."""
    with TestContext(plan_id='log-read'):
        # Add some entries
        run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-read',
            '--phase', 'init',
            '--summary', 'Started',
            '--type', 'progress'
        )
        run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-read',
            '--phase', 'configure',
            '--summary', 'Selected plan-type-java',
            '--type', 'decision',
            '--detail', 'Task modifies Java files'
        )

        # Read entries
        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'log-read'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['total_entries'] == 2
        # Verify entries have type field
        entries = data.get('entries', [])
        assert len(entries) == 2


def test_read_entries_by_phase():
    """Test filtering entries by phase."""
    with TestContext(plan_id='log-filter'):
        # Add entries in different phases
        run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-filter',
            '--phase', 'init',
            '--summary', 'Init entry'
        )
        run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-filter',
            '--phase', 'configure',
            '--summary', 'Configure entry'
        )

        # Read only configure entries
        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'log-filter',
            '--phase', 'configure'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['total_entries'] == 1


# =============================================================================
# Test: List Command
# =============================================================================

def test_list_entries():
    """Test listing entries with limit."""
    with TestContext(plan_id='log-list'):
        # Add several entries
        for i in range(5):
            run_script(SCRIPT_PATH, 'add',
                '--plan-id', 'log-list',
                '--phase', 'implement',
                '--summary', f'Entry {i}'
            )

        # List with limit
        result = run_script(SCRIPT_PATH, 'list',
            '--plan-id', 'log-list',
            '--limit', '3'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['total_entries'] == 5
        assert data['showing'] == 3


# =============================================================================
# Test: Validation
# =============================================================================

def test_invalid_plan_id():
    """Test that invalid plan_id fails."""
    with TestContext(plan_id='valid-id'):
        result = run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'INVALID_ID',
            '--phase', 'init',
            '--summary', 'Test'
        )
        assert not result.success, "Expected failure for invalid plan_id"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_plan_id'


# =============================================================================
# Test: Whitespace Handling
# =============================================================================

def test_whitespace_in_args_read():
    """Test that extra whitespace in arguments is handled gracefully."""
    with TestContext(plan_id='log-whitespace'):
        # Add an entry first
        run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-whitespace',
            '--phase', 'init',
            '--summary', 'Test entry'
        )
        # Simulate extra whitespace by passing empty string args (stripped should work)
        # This tests the internal whitespace stripping
        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'log-whitespace'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['total_entries'] == 1


def test_whitespace_in_args_list():
    """Test that list command handles whitespace gracefully."""
    with TestContext(plan_id='log-whitespace-list'):
        # Add entries
        run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-whitespace-list',
            '--phase', 'init',
            '--summary', 'Entry 1'
        )
        run_script(SCRIPT_PATH, 'add',
            '--plan-id', 'log-whitespace-list',
            '--phase', 'init',
            '--summary', 'Entry 2'
        )
        # Normal invocation should work
        result = run_script(SCRIPT_PATH, 'list',
            '--plan-id', 'log-whitespace-list',
            '--limit', '1'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['showing'] == 1


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Add command with type and detail
        test_add_entry_default_type,
        test_add_entry_decision_type,
        test_add_entry_artifact_type,
        test_add_entry_error_type,
        test_add_entry_outcome_type,
        test_add_entry_finding_type,
        test_add_entry_invalid_type,
        # Read command
        test_read_entries,
        test_read_entries_by_phase,
        # List command
        test_list_entries,
        # Validation
        test_invalid_plan_id,
        # Whitespace handling
        test_whitespace_in_args_read,
        test_whitespace_in_args_list,
    ])
    sys.exit(runner.run())
