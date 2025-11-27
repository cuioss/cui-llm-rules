#!/usr/bin/env python3
"""Tests for init-run-config.py script.

Migrated from test-init-run-config.sh - tests run-configuration.json
initialization including file creation, skip existing, and force overwrite.
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-utilities', 'claude-run-configuration', 'init-run-config.py')


# =============================================================================
# Test Helpers
# =============================================================================

class TempDirContext:
    """Context manager for tests that need a fresh temp directory."""

    def __init__(self):
        self.temp_dir = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# =============================================================================
# Tests
# =============================================================================

def test_create_new_config():
    """Test create new run-configuration.json."""
    with TempDirContext() as temp_dir:
        result = run_script(SCRIPT_PATH, '--project-dir', str(temp_dir))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('action') == 'created', "Action should be 'created'"

        # Verify file exists
        config_file = temp_dir / '.claude' / 'run-configuration.json'
        assert config_file.exists(), "Config file should be created"


def test_skip_existing():
    """Test skip if file already exists."""
    with TempDirContext() as temp_dir:
        # Create existing file
        claude_dir = temp_dir / '.claude'
        claude_dir.mkdir(parents=True)
        (claude_dir / 'run-configuration.json').write_text('{"version": 1, "commands": {}}')

        result = run_script(SCRIPT_PATH, '--project-dir', str(temp_dir))
        data = result.json()

        assert data.get('success') is True, "Should succeed"
        assert data.get('action') == 'skipped', "Action should be 'skipped'"


def test_force_overwrite():
    """Test force overwrite existing file."""
    with TempDirContext() as temp_dir:
        # Create existing file with old content
        claude_dir = temp_dir / '.claude'
        claude_dir.mkdir(parents=True)
        (claude_dir / 'run-configuration.json').write_text('{"version": 1, "commands": {"old": {}}}')

        result = run_script(SCRIPT_PATH, '--project-dir', str(temp_dir), '--force')
        data = result.json()

        assert data.get('success') is True, "Should succeed"

        # Verify old command entry is gone
        import json
        content = json.loads((claude_dir / 'run-configuration.json').read_text())
        assert 'old' not in content.get('commands', {}), "Old command should be removed"


def test_correct_structure():
    """Test created file has correct structure."""
    with TempDirContext() as temp_dir:
        run_script(SCRIPT_PATH, '--project-dir', str(temp_dir))

        import json
        config_file = temp_dir / '.claude' / 'run-configuration.json'
        content = json.loads(config_file.read_text())

        # Check version
        assert content.get('version') == 1, "Version should be 1"

        # Check commands is empty object
        assert content.get('commands') == {}, "Commands should be empty object"

        # Check maven section with acceptable_warnings
        maven = content.get('maven', {})
        aw = maven.get('acceptable_warnings', {})
        assert 'transitive_dependency' in aw, "Should have transitive_dependency category"
        assert 'plugin_compatibility' in aw, "Should have plugin_compatibility category"
        assert 'platform_specific' in aw, "Should have platform_specific category"


def test_creates_claude_dir():
    """Test creates .claude directory if needed."""
    with TempDirContext() as temp_dir:
        # Ensure .claude doesn't exist
        claude_dir = temp_dir / '.claude'
        if claude_dir.exists():
            shutil.rmtree(claude_dir)

        run_script(SCRIPT_PATH, '--project-dir', str(temp_dir))

        assert claude_dir.exists(), ".claude directory should be created"
        assert (claude_dir / 'run-configuration.json').exists(), "Config file should be created"


def test_output_includes_path():
    """Test output includes path."""
    with TempDirContext() as temp_dir:
        result = run_script(SCRIPT_PATH, '--project-dir', str(temp_dir))
        data = result.json()

        assert 'path' in data, "Output should include path field"


def test_output_includes_structure():
    """Test output includes structure when created."""
    with TempDirContext() as temp_dir:
        result = run_script(SCRIPT_PATH, '--project-dir', str(temp_dir))
        data = result.json()

        assert data.get('action') == 'created', "Should be created"
        assert 'structure' in data, "Output should include structure field"


def test_default_project_dir():
    """Test default project dir is current directory."""
    with TempDirContext() as temp_dir:
        # Run from temp_dir
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            proc = subprocess.run(
                ['python3', str(SCRIPT_PATH)],
                capture_output=True,
                text=True
            )
        finally:
            os.chdir(old_cwd)

        config_file = temp_dir / '.claude' / 'run-configuration.json'
        assert config_file.exists(), "Config file should be created in current directory"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_create_new_config,
        test_skip_existing,
        test_force_overwrite,
        test_correct_structure,
        test_creates_claude_dir,
        test_output_includes_path,
        test_output_includes_structure,
        test_default_project_dir,
    ])
    sys.exit(runner.run())
