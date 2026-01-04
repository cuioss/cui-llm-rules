#!/usr/bin/env python3
"""Tests for direct_command.py script.

Tests the foundation layer for Maven command execution including
wrapper detection, timeout handling, and command execution.
"""

import json
import os
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    run_script,
    get_script_path,
    TestRunner,
    BuildTestContext,
    create_marshal_json
)

# Get script path
SCRIPT_PATH = get_script_path('pm-dev-java', 'plan-marshall-plugin', 'direct_command.py')


# =============================================================================
# Test: detect_wrapper
# =============================================================================

def test_detect_wrapper_with_mvnw():
    """Test wrapper detection when ./mvnw exists."""
    with BuildTestContext() as ctx:
        # Create mvnw wrapper
        mvnw_path = ctx.temp_dir / 'mvnw'
        mvnw_path.write_text('#!/bin/bash\necho "mvnw"')
        mvnw_path.chmod(0o755)

        result = run_script(SCRIPT_PATH, 'detect-wrapper', '--project-dir', str(ctx.temp_dir))

        assert result.success, f"Script failed: {result.stderr}"
        assert 'mvnw' in result.stdout


def test_detect_wrapper_fallback_to_mvn():
    """Test wrapper detection falls back to mvn when no wrapper exists."""
    with BuildTestContext() as ctx:
        # No mvnw in temp_dir
        result = run_script(SCRIPT_PATH, 'detect-wrapper', '--project-dir', str(ctx.temp_dir))

        assert result.success, f"Script failed: {result.stderr}"
        assert 'mvn' in result.stdout


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
# Test: execute (error cases - we can't test actual maven execution in unit tests)
# =============================================================================

def test_execute_wrapper_not_found():
    """Test execute with non-existent wrapper returns proper error."""
    with BuildTestContext() as ctx:
        # No mvnw, and mvn probably not in PATH in isolated environment
        # We'll use a definitely non-existent wrapper by using a fake project dir
        result = run_script(
            SCRIPT_PATH, 'execute',
            '--args', 'clean verify',
            '--command-key', 'test:verify',
            '--default-timeout', '10',
            '--project-dir', str(ctx.temp_dir)
        )

        # Parse TOON output
        lines = result.stdout.strip().split('\n')
        output = {}
        for line in lines:
            if '\t' in line:
                key, val = line.split('\t', 1)
                output[key] = val

        # Should have status and error fields
        assert 'status' in output
        # Status could be 'error' or 'timeout' depending on environment
        # If mvn is in PATH, it would fail differently


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
    assert 'detect-wrapper' in result.stdout
    assert 'get-bash-timeout' in result.stdout


def test_execute_help():
    """Test execute subcommand help."""
    result = run_script(SCRIPT_PATH, 'execute', '--help')

    assert result.success, f"Script failed: {result.stderr}"
    assert '--args' in result.stdout
    assert '--command-key' in result.stdout
    assert '--default-timeout' in result.stdout


# =============================================================================
# Test: API functions (via import)
# =============================================================================

def test_api_detect_wrapper_import():
    """Test direct_command can be imported and API functions work."""
    # Add script directory to path for import
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from direct_command import detect_wrapper, get_bash_timeout_ms

        with BuildTestContext() as ctx:
            # Create mvnw
            mvnw_path = ctx.temp_dir / 'mvnw'
            mvnw_path.write_text('#!/bin/bash')
            mvnw_path.chmod(0o755)

            wrapper = detect_wrapper(str(ctx.temp_dir))
            assert 'mvnw' in wrapper

            # Test get_bash_timeout_ms
            timeout_ms = get_bash_timeout_ms(300)
            assert timeout_ms == 330000

    finally:
        # Clean up sys.path
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_timeout():
    """Test execute_direct API with timeout (fast failure case)."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from direct_command import execute_direct

        with BuildTestContext() as ctx:
            # Create a fake mvnw that sleeps forever
            mvnw_path = ctx.temp_dir / 'mvnw'
            mvnw_path.write_text('#!/bin/bash\nsleep 100')
            mvnw_path.chmod(0o755)

            # Execute with very short timeout (should timeout quickly)
            result = execute_direct(
                args='verify',
                command_key='test:timeout',
                default_timeout=1,  # 1 second timeout
                project_dir=str(ctx.temp_dir)
            )

            assert result['status'] == 'timeout'
            assert result['exit_code'] == -1
            assert 'timed out' in result.get('error', '').lower()

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_success():
    """Test execute_direct API with successful command."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from direct_command import execute_direct

        with BuildTestContext() as ctx:
            # Create a fake mvnw that succeeds immediately
            mvnw_path = ctx.temp_dir / 'mvnw'
            mvnw_path.write_text('#!/bin/bash\nexit 0')
            mvnw_path.chmod(0o755)

            result = execute_direct(
                args='verify',
                command_key='test:success',
                default_timeout=10,
                project_dir=str(ctx.temp_dir)
            )

            assert result['status'] == 'success'
            assert result['exit_code'] == 0
            assert result['duration_seconds'] >= 0
            assert 'mvnw' in result['wrapper']
            # Verify log file is created in standard location
            assert 'log_file' in result
            assert '.plan/temp/build-output/' in result['log_file']
            assert '/maven-' in result['log_file']

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_failure():
    """Test execute_direct API with failing command."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from direct_command import execute_direct

        with BuildTestContext() as ctx:
            # Create a fake mvnw that fails
            mvnw_path = ctx.temp_dir / 'mvnw'
            mvnw_path.write_text('#!/bin/bash\necho "BUILD FAILURE" >&2\nexit 1')
            mvnw_path.chmod(0o755)

            result = execute_direct(
                args='verify',
                command_key='test:failure',
                default_timeout=10,
                project_dir=str(ctx.temp_dir)
            )

            assert result['status'] == 'error'
            assert result['exit_code'] == 1
            # Output goes to log file in standard location
            assert 'log_file' in result
            assert '.plan/temp/build-output/' in result['log_file']
            assert '/maven-' in result['log_file']

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


# =============================================================================
# Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Wrapper detection
        test_detect_wrapper_with_mvnw,
        test_detect_wrapper_fallback_to_mvn,

        # Bash timeout calculation
        test_get_bash_timeout_calculation,
        test_get_bash_timeout_small_value,

        # CLI error cases
        test_execute_wrapper_not_found,
        test_execute_missing_required_args,

        # Help
        test_main_help,
        test_execute_help,

        # API functions
        test_api_detect_wrapper_import,
        test_api_execute_direct_timeout,
        test_api_execute_direct_success,
        test_api_execute_direct_failure,
    ])
    sys.exit(runner.run())
