#!/usr/bin/env python3
"""Tests for handoff.py script."""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('general-tools', 'manage-handoff', 'handoff.py')

# Import toon_parser for output parsing
TOON_PARSER_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(TOON_PARSER_DIR))
from toon_parser import parse_toon


# =============================================================================
# Test Fixtures
# =============================================================================

VALID_HANDOFF = """
from: plan-init-skill
to: plan-configure-skill
plan_id: test-plan

task:
  description: Initialize plan
  status: completed
  progress: 100

next_action: Configure plan type
"""

ERROR_HANDOFF = """
from: build-verify-agent
to: java-fix-build-agent
plan_id: test-plan

task:
  status: failed

error:
  type: build_failure
  message: Compilation failed
"""

INVALID_HANDOFF_MISSING_FIELDS = """
from: some-skill
task:
  status: completed
"""

INVALID_HANDOFF_BAD_STATUS = """
from: skill-a
to: skill-b
plan_id: test

task:
  status: invalid_status
"""


# =============================================================================
# Test Helpers
# =============================================================================

class TestContext:
    """Context manager for test with temp directory.

    Uses PLAN_BASE_DIR environment variable to communicate base dir to subprocess.
    """

    def __init__(self):
        self.temp_dir = None
        self.original_env = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.get('PLAN_BASE_DIR')
        os.environ['PLAN_BASE_DIR'] = str(self.temp_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_env is None:
            os.environ.pop('PLAN_BASE_DIR', None)
        else:
            os.environ['PLAN_BASE_DIR'] = self.original_env
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def run_handoff(*args):
    """Run handoff script with arguments."""
    return run_script(SCRIPT_PATH, *args)


def parse_output(result):
    """Parse TOON output from script result."""
    if result.stdout.strip():
        return parse_toon(result.stdout)
    return {}


# =============================================================================
# Test: Save Command
# =============================================================================

def test_save_valid_handoff():
    """Test saving a valid handoff."""
    with TestContext():
        result = run_handoff('save',
            '--plan_id', 'jwt-auth',
            '--step', 'init-complete',
            '--content', VALID_HANDOFF
        )
        assert result.success, f"Script failed: {result.stderr}"

        data = parse_output(result)
        assert data['status'] == 'success'
        assert data['operation'] == 'save'
        assert 'file' in data
        assert data['file'].endswith('.toon')
        assert 'jwt-auth' in data['file']


def test_save_error_handoff():
    """Test saving an error handoff."""
    with TestContext():
        result = run_handoff('save',
            '--plan_id', 'build-fix',
            '--step', 'verify-error',
            '--content', ERROR_HANDOFF
        )
        assert result.success, f"Script failed: {result.stderr}"

        data = parse_output(result)
        assert data['status'] == 'success'


def test_save_invalid_missing_fields():
    """Test validation error for missing required fields."""
    with TestContext():
        result = run_handoff('save',
            '--plan_id', 'test',
            '--step', 'init',
            '--content', INVALID_HANDOFF_MISSING_FIELDS
        )
        assert not result.success

        data = parse_output(result)
        assert data['status'] == 'error'
        assert data['error']['type'] == 'validation_error'


def test_save_invalid_status():
    """Test validation error for invalid task.status."""
    with TestContext():
        result = run_handoff('save',
            '--plan_id', 'test',
            '--step', 'init',
            '--content', INVALID_HANDOFF_BAD_STATUS
        )
        assert not result.success

        data = parse_output(result)
        assert data['status'] == 'error'
        assert 'invalid' in data['error']['message'].lower() or 'status' in str(data['error']).lower()


# =============================================================================
# Test: Load Command
# =============================================================================

def test_load_existing_handoff():
    """Test loading an existing handoff."""
    with TestContext():
        # First save a handoff
        run_handoff('save',
            '--plan_id', 'jwt-auth',
            '--step', 'init-complete',
            '--content', VALID_HANDOFF
        )

        # Then load it
        result = run_handoff('load',
            '--plan_id', 'jwt-auth',
            '--step', 'init-complete'
        )
        assert result.success, f"Script failed: {result.stderr}"

        data = parse_output(result)
        assert data['status'] == 'success'
        assert data['operation'] == 'load'
        assert 'handoff' in data
        assert data['handoff']['from'] == 'plan-init-skill'


def test_load_nonexistent_handoff():
    """Test loading a handoff that doesn't exist."""
    with TestContext():
        result = run_handoff('load',
            '--plan_id', 'nonexistent',
            '--step', 'missing'
        )
        assert not result.success

        data = parse_output(result)
        assert data['status'] == 'error'
        assert data['error']['type'] == 'not_found'


def test_load_most_recent():
    """Test that load returns the most recent handoff."""
    with TestContext():
        # Save two handoffs with same plan_id and step
        run_handoff('save',
            '--plan_id', 'test',
            '--step', 'step1',
            '--content', """
from: skill-a
to: skill-b
plan_id: test
task:
  status: pending
version: 1
"""
        )

        # Save another one (will be more recent)
        run_handoff('save',
            '--plan_id', 'test',
            '--step', 'step1',
            '--content', """
from: skill-a
to: skill-b
plan_id: test
task:
  status: completed
version: 2
"""
        )

        # Load should return the most recent (version 2)
        result = run_handoff('load', '--plan_id', 'test', '--step', 'step1')
        assert result.success

        data = parse_output(result)
        assert data['handoff']['version'] == 2


# =============================================================================
# Test: List Command
# =============================================================================

def test_list_empty():
    """Test listing when no handoffs exist."""
    with TestContext():
        result = run_handoff('list')
        assert result.success

        data = parse_output(result)
        assert data['status'] == 'success'
        assert data['counts']['total'] == 0


def test_list_all():
    """Test listing all handoffs."""
    with TestContext():
        # Save a few handoffs
        run_handoff('save', '--plan_id', 'plan1', '--step', 'init', '--content', VALID_HANDOFF)
        run_handoff('save', '--plan_id', 'plan2', '--step', 'init', '--content', VALID_HANDOFF)

        result = run_handoff('list')
        assert result.success

        data = parse_output(result)
        assert data['counts']['total'] == 2


def test_list_filter_by_plan_id():
    """Test filtering list by plan_id."""
    with TestContext():
        run_handoff('save', '--plan_id', 'plan-a', '--step', 'init', '--content', VALID_HANDOFF)
        run_handoff('save', '--plan_id', 'plan-b', '--step', 'init', '--content', VALID_HANDOFF)

        result = run_handoff('list', '--plan_id', 'plan-a')
        assert result.success

        data = parse_output(result)
        assert data['counts']['total'] == 1
        assert data['handoffs'][0]['plan_id'] == 'plan-a'


def test_list_filter_by_status():
    """Test filtering list by status."""
    with TestContext():
        run_handoff('save', '--plan_id', 'plan1', '--step', 'init', '--content', VALID_HANDOFF)  # completed
        run_handoff('save', '--plan_id', 'plan2', '--step', 'init', '--content', ERROR_HANDOFF)  # failed

        result = run_handoff('list', '--status', 'failed')
        assert result.success

        data = parse_output(result)
        assert data['counts']['total'] == 1


# =============================================================================
# Test: Get Command
# =============================================================================

def test_get_existing_file():
    """Test getting a specific handoff by filename."""
    with TestContext():
        # Save a handoff
        save_result = run_handoff('save',
            '--plan_id', 'jwt-auth',
            '--step', 'init-complete',
            '--content', VALID_HANDOFF
        )
        save_data = parse_output(save_result)
        filename = save_data['file']

        # Get it by filename
        result = run_handoff('get', '--file', filename)
        assert result.success

        data = parse_output(result)
        assert data['status'] == 'success'
        assert data['operation'] == 'get'
        assert data['file'] == filename


def test_get_nonexistent_file():
    """Test getting a file that doesn't exist."""
    with TestContext():
        result = run_handoff('get', '--file', 'nonexistent-file.toon')
        assert not result.success

        data = parse_output(result)
        assert data['status'] == 'error'
        assert data['error']['type'] == 'not_found'


# =============================================================================
# Test: Cleanup Command
# =============================================================================

def test_cleanup_removes_old_files():
    """Test that cleanup removes old files (simulated via directory manipulation)."""
    with TestContext() as ctx:
        # Save a handoff
        run_handoff('save', '--plan_id', 'old-plan', '--step', 'init', '--content', VALID_HANDOFF)

        # Manually rename to simulate old timestamp
        handoff_dir = ctx.temp_dir / 'memory' / 'handoffs'
        files = list(handoff_dir.glob('*.toon'))
        if files:
            old_file = files[0]
            # Rename to have an old timestamp (more than 7 days ago)
            new_name = 'old-plan-init-20200101T000000Z.toon'
            old_file.rename(handoff_dir / new_name)

        # Run cleanup
        result = run_handoff('cleanup', '--older-than', '1d')
        assert result.success

        data = parse_output(result)
        assert data['status'] == 'success'
        assert data['removed_count'] == 1


def test_cleanup_preserves_recent_files():
    """Test that cleanup preserves recent files."""
    with TestContext():
        # Save a handoff (will have current timestamp)
        run_handoff('save', '--plan_id', 'recent-plan', '--step', 'init', '--content', VALID_HANDOFF)

        # Run cleanup with 7 day threshold
        result = run_handoff('cleanup', '--older-than', '7d')
        assert result.success

        data = parse_output(result)
        assert data['removed_count'] == 0


# =============================================================================
# Test: Edge Cases
# =============================================================================

def test_special_characters_in_plan_id():
    """Test handling of special characters in plan_id."""
    with TestContext():
        result = run_handoff('save',
            '--plan_id', 'feature/auth-impl',
            '--step', 'init',
            '--content', VALID_HANDOFF
        )
        assert result.success

        data = parse_output(result)
        # Special chars should be sanitized in filename
        assert '/' not in data['file']


def test_auto_generated_timestamp():
    """Test that timestamp is auto-generated if not provided."""
    with TestContext():
        handoff_without_timestamp = """
from: skill-a
to: skill-b
plan_id: test

task:
  status: pending
"""
        result = run_handoff('save',
            '--plan_id', 'test',
            '--step', 'init',
            '--content', handoff_without_timestamp
        )
        assert result.success

        # Load and verify timestamp was added
        load_result = run_handoff('load', '--plan_id', 'test', '--step', 'init')
        load_data = parse_output(load_result)
        assert 'timestamp' in load_data['handoff']


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Save command
        test_save_valid_handoff,
        test_save_error_handoff,
        test_save_invalid_missing_fields,
        test_save_invalid_status,
        # Load command
        test_load_existing_handoff,
        test_load_nonexistent_handoff,
        test_load_most_recent,
        # List command
        test_list_empty,
        test_list_all,
        test_list_filter_by_plan_id,
        test_list_filter_by_status,
        # Get command
        test_get_existing_file,
        test_get_nonexistent_file,
        # Cleanup command
        test_cleanup_removes_old_files,
        test_cleanup_preserves_recent_files,
        # Edge cases
        test_special_characters_in_plan_id,
        test_auto_generated_timestamp,
    ])
    sys.exit(runner.run())
