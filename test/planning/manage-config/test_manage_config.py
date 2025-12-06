#!/usr/bin/env python3
"""Tests for manage-config.py script."""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('planning', 'manage-config', 'manage-config.py')

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


# =============================================================================
# Test: Create Command
# =============================================================================

def test_create_config():
    """Test creating a config file with qualified plan type."""
    with TestContext(plan_id='config-create'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-create',
            '--plan-type', 'planning:plan-type-java'
        )
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['config']['plan_type'] == 'planning:plan-type-java'


def test_create_config_with_all_fields():
    """Test creating a config file with all fields."""
    with TestContext(plan_id='config-full'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-full',
            '--plan-type', 'planning:plan-type-simple',
            '--compatibility', 'breaking',
            '--commit-strategy', 'fine-granular'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_create_config_invalid_type_format():
    """Test that invalid plan type format fails."""
    with TestContext(plan_id='config-invalid-format'):
        result = run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-invalid-format',
            '--plan-type', 'java'  # Missing bundle:skill notation
        )
        assert not result.success, "Expected failure for invalid plan type format"
        data = parse_toon(result.stdout)
        assert data['error'] == 'invalid_plan_type'


# =============================================================================
# Test: Get/Set Operations
# =============================================================================

def test_set_and_get_field():
    """Test setting and getting a config field."""
    with TestContext(plan_id='config-getset'):
        # Create config first
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-getset',
            '--plan-type', 'planning:plan-type-java'
        )
        # Set a field
        set_result = run_script(SCRIPT_PATH, 'set',
            '--plan-id', 'config-getset',
            '--field', 'compatibility',
            '--value', 'breaking'
        )
        assert set_result.success, f"Set failed: {set_result.stderr}"

        # Get the field
        get_result = run_script(SCRIPT_PATH, 'get',
            '--plan-id', 'config-getset',
            '--field', 'compatibility'
        )
        assert get_result.success, f"Get failed: {get_result.stderr}"
        data = parse_toon(get_result.stdout)
        assert data['value'] == 'breaking'


def test_read_config():
    """Test reading entire config."""
    with TestContext(plan_id='config-read'):
        # Create config first
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-read',
            '--plan-type', 'planning:plan-type-simple'
        )
        # Read it
        result = run_script(SCRIPT_PATH, 'read',
            '--plan-id', 'config-read'
        )
        assert result.success, f"Script failed: {result.stderr}"


def test_set_invalid_plan_type_format():
    """Test that setting invalid plan_type format fails."""
    with TestContext(plan_id='config-invalid'):
        # Create config first
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-invalid',
            '--plan-type', 'planning:plan-type-java'
        )
        # Try to set invalid value (missing bundle:skill notation)
        result = run_script(SCRIPT_PATH, 'set',
            '--plan-id', 'config-invalid',
            '--field', 'plan_type',
            '--value', 'unknown'
        )
        assert not result.success, "Expected failure for invalid plan_type format"


def test_set_valid_plan_type():
    """Test that setting valid plan_type works."""
    with TestContext(plan_id='config-valid-set'):
        # Create config first
        run_script(SCRIPT_PATH, 'create',
            '--plan-id', 'config-valid-set',
            '--plan-type', 'planning:plan-type-java'
        )
        # Set to another valid type
        result = run_script(SCRIPT_PATH, 'set',
            '--plan-id', 'config-valid-set',
            '--field', 'plan_type',
            '--value', 'planning:plan-type-simple'
        )
        assert result.success, f"Set failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['value'] == 'planning:plan-type-simple'


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Create command
        test_create_config,
        test_create_config_with_all_fields,
        test_create_config_invalid_type_format,
        # Get/Set operations
        test_set_and_get_field,
        test_read_config,
        test_set_invalid_plan_type_format,
        test_set_valid_plan_type,
    ])
    sys.exit(runner.run())
