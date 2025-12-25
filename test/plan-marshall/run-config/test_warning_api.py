#!/usr/bin/env python3
"""Tests for warning API in run_config.py.

Tests:
- warning add - adds pattern to acceptable list
- warning list - lists accepted warning patterns
- warning remove - removes pattern from acceptable list
- Filtering behavior (actionable mode filters accepted warnings)
- Structured mode shows all with [accepted] markers
"""

import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('plan-marshall', 'run-config', 'run_config.py')


# =============================================================================
# Test Helpers
# =============================================================================

class WarningTestContext:
    """Context manager for warning API tests."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        (self.temp_dir / '.plan').mkdir()
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Warning Add Tests
# =============================================================================

def test_warning_add_creates_entry():
    """Test warning add creates entry in run-configuration.json."""
    with WarningTestContext() as temp_dir:
        # First init the config
        run_script(
            SCRIPT_PATH,
            'init',
            '--project-dir', str(temp_dir)
        )

        # Add a warning pattern
        result = run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'transitive_dependency',
            '--pattern', 'uses commons-logging via spring-core',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        data = result.json()
        assert data['success'] is True, "Should return success"
        assert data['action'] == 'added', "Action should be 'added'"

        # Verify in config file
        config_path = temp_dir / '.plan' / 'run-configuration.json'
        config = json.loads(config_path.read_text())
        warnings = config['maven']['acceptable_warnings']['transitive_dependency']
        assert 'uses commons-logging via spring-core' in warnings, \
            f"Pattern should be in config: {warnings}"


def test_warning_add_skips_duplicate():
    """Test warning add skips duplicate pattern."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        # Add same pattern twice
        run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'transitive_dependency',
            '--pattern', 'duplicate pattern',
            '--project-dir', str(temp_dir)
        )
        result = run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'transitive_dependency',
            '--pattern', 'duplicate pattern',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        data = result.json()
        assert data['action'] == 'skipped', "Should skip duplicate"


def test_warning_add_invalid_category():
    """Test warning add rejects invalid category."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        result = run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'invalid_category',
            '--pattern', 'some pattern',
            '--project-dir', str(temp_dir)
        )

        # argparse should reject invalid category
        assert result.returncode != 0, "Should reject invalid category"


# =============================================================================
# Warning List Tests
# =============================================================================

def test_warning_list_all_categories():
    """Test warning list returns all categories."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        # Add patterns to different categories
        run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'transitive_dependency',
            '--pattern', 'pattern1',
            '--project-dir', str(temp_dir)
        )
        run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'plugin_compatibility',
            '--pattern', 'pattern2',
            '--project-dir', str(temp_dir)
        )

        result = run_script(
            SCRIPT_PATH,
            'warning', 'list',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        data = result.json()
        assert 'categories' in data, "Should return categories"
        assert 'transitive_dependency' in data['categories'], \
            "Should have transitive_dependency"
        assert 'plugin_compatibility' in data['categories'], \
            "Should have plugin_compatibility"


def test_warning_list_single_category():
    """Test warning list with --category filter."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'transitive_dependency',
            '--pattern', 'filtered pattern',
            '--project-dir', str(temp_dir)
        )

        result = run_script(
            SCRIPT_PATH,
            'warning', 'list',
            '--category', 'transitive_dependency',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        data = result.json()
        assert 'patterns' in data, "Should return patterns"
        assert 'filtered pattern' in data['patterns'], \
            f"Should contain the pattern: {data['patterns']}"


def test_warning_list_empty():
    """Test warning list on empty config."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        result = run_script(
            SCRIPT_PATH,
            'warning', 'list',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        data = result.json()
        assert data['success'] is True, "Should succeed with empty list"


# =============================================================================
# Warning Remove Tests
# =============================================================================

def test_warning_remove_existing():
    """Test warning remove removes existing pattern."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        # Add then remove
        run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'transitive_dependency',
            '--pattern', 'to be removed',
            '--project-dir', str(temp_dir)
        )
        result = run_script(
            SCRIPT_PATH,
            'warning', 'remove',
            '--category', 'transitive_dependency',
            '--pattern', 'to be removed',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        data = result.json()
        assert data['action'] == 'removed', "Action should be 'removed'"

        # Verify removed from config
        config_path = temp_dir / '.plan' / 'run-configuration.json'
        config = json.loads(config_path.read_text())
        warnings = config['maven']['acceptable_warnings']['transitive_dependency']
        assert 'to be removed' not in warnings, "Pattern should be removed"


def test_warning_remove_nonexistent():
    """Test warning remove skips non-existent pattern."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        result = run_script(
            SCRIPT_PATH,
            'warning', 'remove',
            '--category', 'transitive_dependency',
            '--pattern', 'nonexistent',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"
        data = result.json()
        assert data['action'] == 'skipped', "Should skip nonexistent"


# =============================================================================
# Build System Parameter Tests
# =============================================================================

def test_warning_add_with_build_system():
    """Test warning add with --build-system parameter."""
    with WarningTestContext() as temp_dir:
        run_script(SCRIPT_PATH, 'init', '--project-dir', str(temp_dir))

        result = run_script(
            SCRIPT_PATH,
            'warning', 'add',
            '--category', 'transitive_dependency',
            '--pattern', 'npm warning',
            '--build-system', 'npm',
            '--project-dir', str(temp_dir)
        )

        assert result.returncode == 0, f"Should succeed: {result.stderr}"

        # Verify in npm section, not maven
        config_path = temp_dir / '.plan' / 'run-configuration.json'
        config = json.loads(config_path.read_text())
        npm_warnings = config.get('npm', {}).get('acceptable_warnings', {}).get('transitive_dependency', [])
        assert 'npm warning' in npm_warnings, f"Should be in npm section: {config}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_warning_add_creates_entry,
        test_warning_add_skips_duplicate,
        test_warning_add_invalid_category,
        test_warning_list_all_categories,
        test_warning_list_single_category,
        test_warning_list_empty,
        test_warning_remove_existing,
        test_warning_remove_nonexistent,
        test_warning_add_with_build_system,
    ])
    sys.exit(runner.run())
