#!/usr/bin/env python3
"""Tests for modules command in plan-marshall-config.

Tests modules command variants including command resolution and edge cases.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, PlanTestContext
from test_helpers import SCRIPT_PATH, create_marshal_json


# =============================================================================
# modules Command Tests
# =============================================================================

def test_modules_list():
    """Test modules list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'my-core' in result.stdout
        assert 'my-ui' in result.stdout


def test_modules_get():
    """Test modules get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'my-core')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout.lower()
        assert 'maven' in result.stdout.lower()


def test_modules_get_domains():
    """Test modules get-domains."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get-domains', '--module', 'my-ui')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout.lower()
        assert 'javascript' in result.stdout.lower()


def test_modules_get_build_systems():
    """Test modules get-build-systems."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get-build-systems', '--module', 'my-ui')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()
        assert 'npm' in result.stdout.lower()


def test_modules_get_command_from_default():
    """Test modules get-command falls back to default module."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'get-command',
            '--module', 'my-core',
            '--label', 'verify'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'clean verify' in result.stdout
        assert 'source: default' in result.stdout


def test_modules_get_command_from_module():
    """Test modules get-command returns module-specific command."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'get-command',
            '--module', 'my-ui',
            '--label', 'test'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'npm' in result.stdout  # Contains npm in the command
        assert 'source: module' in result.stdout


def test_modules_set_command():
    """Test modules set-command sets command for module."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'set-command',
            '--module', 'my-core',
            '--label', 'custom',
            '--command', 'python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals "custom"'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify the command was set
        verify = run_script(
            SCRIPT_PATH, 'modules', 'get-command',
            '--module', 'my-core',
            '--label', 'custom'
        )
        assert 'custom' in verify.stdout
        assert 'source: module' in verify.stdout


def test_modules_add():
    """Test modules add."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'add',
            '--module', 'new-module',
            '--path', 'path/to/new-module',
            '--domains', 'java,java-testing',
            '--build-systems', 'maven'
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify added
        verify = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'new-module')
        assert 'path/to/new-module' in verify.stdout


def test_modules_remove():
    """Test modules remove."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'remove', '--module', 'my-core')

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify removed
        verify = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'my-core')
        assert 'error' in verify.stdout.lower()


def test_modules_get_unknown_module():
    """Test modules get with unknown module returns error."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'get', '--module', 'nonexistent')

        assert 'error' in result.stdout.lower(), "Should report error"


def test_modules_add_duplicate_fails():
    """Test modules add fails for existing module."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'modules', 'add',
            '--module', 'my-core',  # Already exists
            '--domains', 'java'
        )

        assert 'error' in result.stdout.lower() or 'exists' in result.stdout.lower()


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_modules_list,
        test_modules_get,
        test_modules_get_domains,
        test_modules_get_build_systems,
        test_modules_get_command_from_default,
        test_modules_get_command_from_module,
        test_modules_set_command,
        test_modules_add,
        test_modules_remove,
        test_modules_get_unknown_module,
        test_modules_add_duplicate_fails,
    ])
    sys.exit(runner.run())
