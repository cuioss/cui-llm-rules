#!/usr/bin/env python3
"""Tests for build-systems command in plan-marshall-config.

Tests build-systems command variants and edge cases.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, PlanTestContext
from test_helpers import SCRIPT_PATH, create_marshal_json


# =============================================================================
# build-systems Command Tests
# =============================================================================

def test_build_systems_list():
    """Test build-systems list."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'list')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()
        assert 'npm' in result.stdout.lower()


def test_build_systems_get():
    """Test build-systems get."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'maven')

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'pm-dev-builder:builder-maven-rules' in result.stdout
        assert 'verify' in result.stdout.lower()


def test_build_systems_get_command():
    """Test build-systems get-command."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'build-systems', 'get-command',
            '--system', 'maven',
            '--label', 'verify'
        )

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'clean verify' in result.stdout


def test_build_systems_add():
    """Test build-systems add."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'add', '--system', 'gradle')

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify added
        verify = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'gradle')
        assert 'pm-dev-builder:builder-gradle-rules' in verify.stdout


def test_build_systems_remove():
    """Test build-systems remove."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'remove', '--system', 'npm')

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify removed
        verify = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'npm')
        assert 'error' in verify.stdout.lower()


def test_build_systems_get_unknown():
    """Test build-systems get with unknown system returns error."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'get', '--system', 'unknown')

        assert 'error' in result.stdout.lower(), "Should report error"


def test_build_systems_add_duplicate_fails():
    """Test build-systems add fails for existing system."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'add', '--system', 'maven')

        assert 'error' in result.stdout.lower() or 'exists' in result.stdout.lower()


def test_build_systems_get_command_unknown_label():
    """Test build-systems get-command with unknown label returns error."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(
            SCRIPT_PATH, 'build-systems', 'get-command',
            '--system', 'maven',
            '--label', 'nonexistent'
        )

        assert 'error' in result.stdout.lower(), "Should report error"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_build_systems_list,
        test_build_systems_get,
        test_build_systems_get_command,
        test_build_systems_add,
        test_build_systems_remove,
        test_build_systems_get_unknown,
        test_build_systems_add_duplicate_fails,
        test_build_systems_get_command_unknown_label,
    ])
    sys.exit(runner.run())
