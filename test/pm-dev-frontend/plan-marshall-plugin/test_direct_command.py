#!/usr/bin/env python3
"""Tests for direct_command.py script for npm.

Tests the foundation layer for npm command execution including
command type detection, timeout handling, and command execution.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    run_script,
    get_script_path,
    TestRunner,
    BuildTestContext
)

# Get script path
SCRIPT_PATH = get_script_path('pm-dev-frontend', 'plan-marshall-plugin', 'direct_command.py')


# =============================================================================
# Test: detect_command_type
# =============================================================================

def test_detect_command_type_npm_run():
    """Test command type detection for npm run commands."""
    result = run_script(SCRIPT_PATH, 'detect-command-type', '--args', 'run test')

    assert result.success, f"Script failed: {result.stderr}"
    assert 'npm' in result.stdout


def test_detect_command_type_npx_playwright():
    """Test command type detection for npx playwright."""
    result = run_script(SCRIPT_PATH, 'detect-command-type', '--args', 'playwright test')

    assert result.success, f"Script failed: {result.stderr}"
    assert 'npx' in result.stdout


def test_detect_command_type_npx_eslint():
    """Test command type detection for npx eslint."""
    result = run_script(SCRIPT_PATH, 'detect-command-type', '--args', 'eslint src/')

    assert result.success, f"Script failed: {result.stderr}"
    assert 'npx' in result.stdout


def test_detect_command_type_npx_jest():
    """Test command type detection for npx jest."""
    result = run_script(SCRIPT_PATH, 'detect-command-type', '--args', 'jest --coverage')

    assert result.success, f"Script failed: {result.stderr}"
    assert 'npx' in result.stdout


def test_detect_command_type_npm_install():
    """Test command type detection for npm install."""
    result = run_script(SCRIPT_PATH, 'detect-command-type', '--args', 'install')

    assert result.success, f"Script failed: {result.stderr}"
    assert 'npm' in result.stdout


# =============================================================================
# Test: get_bash_timeout
# =============================================================================

def test_get_bash_timeout_calculation():
    """Test Bash tool timeout calculation with buffer."""
    result = run_script(SCRIPT_PATH, 'get-bash-timeout', '--inner-timeout', '300')

    assert result.success, f"Script failed: {result.stderr}"
    # 300 + 30 buffer = 330 seconds = 330000 ms
    assert result.stdout.strip() == '330000'


def test_get_bash_timeout_small_value():
    """Test Bash tool timeout for small inner timeout."""
    result = run_script(SCRIPT_PATH, 'get-bash-timeout', '--inner-timeout', '60')

    assert result.success, f"Script failed: {result.stderr}"
    # 60 + 30 buffer = 90 seconds = 90000 ms
    assert result.stdout.strip() == '90000'


# =============================================================================
# Test: execute (error cases)
# =============================================================================

def test_execute_missing_required_args():
    """Test execute with missing required arguments."""
    result = run_script(SCRIPT_PATH, 'execute')

    # Should fail with missing required args
    assert not result.success
    assert 'required' in result.stderr.lower() or 'error' in result.stderr.lower()


# =============================================================================
# Test: CLI help
# =============================================================================

def test_main_help():
    """Test main help displays available commands."""
    result = run_script(SCRIPT_PATH, '--help')

    assert result.success, f"Script failed: {result.stderr}"
    assert 'execute' in result.stdout
    assert 'detect-command-type' in result.stdout
    assert 'get-bash-timeout' in result.stdout


def test_execute_help():
    """Test execute subcommand help."""
    result = run_script(SCRIPT_PATH, 'execute', '--help')

    assert result.success, f"Script failed: {result.stderr}"
    assert '--args' in result.stdout
    assert '--command-key' in result.stdout
    assert '--default-timeout' in result.stdout
    assert '--workspace' in result.stdout


# =============================================================================
# Test: API functions (via import)
# =============================================================================

# Use importlib to avoid module naming conflicts with Maven's direct_command
import importlib.util

def _load_npm_direct_command():
    """Load npm direct_command module avoiding conflicts."""
    spec = importlib.util.spec_from_file_location("npm_direct_command", SCRIPT_PATH)
    npm_dc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(npm_dc)
    return npm_dc


def test_api_detect_command_type_import():
    """Test direct_command can be imported and API functions work."""
    npm_dc = _load_npm_direct_command()

    # Test npm commands
    assert npm_dc.detect_command_type('run test') == 'npm'
    assert npm_dc.detect_command_type('install') == 'npm'
    assert npm_dc.detect_command_type('run build') == 'npm'

    # Test npx commands
    assert npm_dc.detect_command_type('playwright test') == 'npx'
    assert npm_dc.detect_command_type('eslint src/') == 'npx'
    assert npm_dc.detect_command_type('jest --coverage') == 'npx'
    assert npm_dc.detect_command_type('prettier --check .') == 'npx'

    # Test get_bash_timeout_ms
    timeout_ms = npm_dc.get_bash_timeout_ms(300)
    assert timeout_ms == 330000


def test_api_execute_direct_success():
    """Test execute_direct API with successful command."""
    npm_dc = _load_npm_direct_command()

    with BuildTestContext() as ctx:
        # Create a minimal package.json
        (ctx.temp_dir / 'package.json').write_text('{"name": "test", "scripts": {"test": "exit 0"}}')

        result = npm_dc.execute_direct(
            args='--version',
            command_key='test:version',
            default_timeout=10,
            project_dir=str(ctx.temp_dir)
        )

        # npm --version should succeed (npm is available in most environments)
        assert result['status'] == 'success'
        assert result['exit_code'] == 0
        assert result['command_type'] == 'npm'


def test_api_execute_direct_with_workspace():
    """Test execute_direct API with workspace parameter."""
    npm_dc = _load_npm_direct_command()

    with BuildTestContext() as ctx:
        result = npm_dc.execute_direct(
            args='--version',
            command_key='test:workspace',
            default_timeout=10,
            project_dir=str(ctx.temp_dir),
            workspace='my-package'
        )

        # The workspace should be added to npm commands
        assert '--workspace=my-package' in result.get('command', '')
        assert result['command_type'] == 'npm'


# =============================================================================
# Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Command type detection
        test_detect_command_type_npm_run,
        test_detect_command_type_npx_playwright,
        test_detect_command_type_npx_eslint,
        test_detect_command_type_npx_jest,
        test_detect_command_type_npm_install,

        # Bash timeout calculation
        test_get_bash_timeout_calculation,
        test_get_bash_timeout_small_value,

        # CLI error cases
        test_execute_missing_required_args,

        # Help
        test_main_help,
        test_execute_help,

        # API functions
        test_api_detect_command_type_import,
        test_api_execute_direct_success,
        test_api_execute_direct_with_workspace,
    ])
    sys.exit(runner.run())
