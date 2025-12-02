#!/usr/bin/env python3
"""Tests for manage-files.py script."""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('planning', 'manage-files', 'manage-files.py')

# Import toon_parser for output parsing
TOON_PARSER_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'
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

    @property
    def plan_dir(self):
        return self.temp_dir / 'plans' / self.plan_id


# =============================================================================
# Test: Write and Read
# =============================================================================

def test_write_file():
    """Test writing a file."""
    with TestContext(plan_id='file-write') as ctx:
        result = run_script(SCRIPT_PATH, 'write',
            '--plan-id', 'file-write',
            '--file', 'task.md',
            '--content', '# Task\nDo something'
        )
        assert result.success, f"Script failed: {result.stderr}"
        # Verify file was created
        assert (ctx.plan_dir / 'task.md').exists()


def test_read_file():
    """Test reading a file."""
    with TestContext(plan_id='file-read') as ctx:
        # Create file first
        (ctx.plan_dir / 'test.md').write_text('Test content')

        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'file-read',
            '--file', 'test.md'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_read_nonexistent_file():
    """Test reading a file that doesn't exist."""
    with TestContext(plan_id='file-noexist'):
        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'file-noexist',
            '--file', 'missing.md'
        )
        assert not result.success, "Expected failure for missing file"


# =============================================================================
# Test: List and Exists
# =============================================================================

def test_list_empty():
    """Test listing files in empty plan."""
    with TestContext(plan_id='file-list-empty'):
        result = run_script(SCRIPT_PATH, 'list',
            '--plan-id', 'file-list-empty'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_list_with_files():
    """Test listing files."""
    with TestContext(plan_id='file-list') as ctx:
        # Create some files
        (ctx.plan_dir / 'task.md').write_text('Task')
        (ctx.plan_dir / 'config.toon').write_text('plan_type: simple')

        result = run_script(SCRIPT_PATH, 'list',
            '--plan-id', 'file-list'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_exists_present():
    """Test checking if file exists (present)."""
    with TestContext(plan_id='file-exists') as ctx:
        (ctx.plan_dir / 'test.md').write_text('Test')

        result = run_script(SCRIPT_PATH, 'exists',
            '--plan-id', 'file-exists',
            '--file', 'test.md'
        )
        assert result.success, f"Script failed: {result.stderr}"
        # Output should indicate file exists
        assert 'true' in result.stdout.lower() or result.returncode == 0


def test_exists_absent():
    """Test checking if file exists (absent)."""
    with TestContext(plan_id='file-absent'):
        result = run_script(SCRIPT_PATH, 'exists',
            '--plan-id', 'file-absent',
            '--file', 'missing.md'
        )
        # Script returns exit code 1 when file doesn't exist
        assert not result.success, "Expected exit code 1 for missing file"


# =============================================================================
# Test: Remove and Mkdir
# =============================================================================

def test_remove_file():
    """Test removing a file."""
    with TestContext(plan_id='file-remove') as ctx:
        (ctx.plan_dir / 'delete-me.md').write_text('Goodbye')

        result = run_script(SCRIPT_PATH, 'remove',
            '--plan-id', 'file-remove',
            '--file', 'delete-me.md'
        )
        assert result.success, f"Script failed: {result.stderr}"
        assert not (ctx.plan_dir / 'delete-me.md').exists()


def test_mkdir():
    """Test creating a directory."""
    with TestContext(plan_id='file-mkdir') as ctx:
        result = run_script(SCRIPT_PATH, 'mkdir',
            '--plan-id', 'file-mkdir',
            '--dir', 'requirements'
        )
        assert result.success, f"Script failed: {result.stderr}"
        assert (ctx.plan_dir / 'requirements').is_dir()


# =============================================================================
# Test: Invalid Plan IDs
# =============================================================================

def test_invalid_plan_id_uppercase():
    """Test that uppercase plan IDs are rejected."""
    with TestContext():
        result = run_script(SCRIPT_PATH, 'list',
            '--plan-id', 'My-Plan'
        )
        assert not result.success, "Expected failure for uppercase plan ID"


def test_invalid_plan_id_underscore():
    """Test that underscore in plan IDs are rejected."""
    with TestContext():
        result = run_script(SCRIPT_PATH, 'list',
            '--plan-id', 'my_plan'
        )
        assert not result.success, "Expected failure for underscore in plan ID"


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Write and Read
        test_write_file,
        test_read_file,
        test_read_nonexistent_file,
        # List and Exists
        test_list_empty,
        test_list_with_files,
        test_exists_present,
        test_exists_absent,
        # Remove and Mkdir
        test_remove_file,
        test_mkdir,
        # Invalid plan IDs
        test_invalid_plan_id_uppercase,
        test_invalid_plan_id_underscore,
    ])
    sys.exit(runner.run())
