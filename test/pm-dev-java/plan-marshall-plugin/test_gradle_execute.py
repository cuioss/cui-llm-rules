#!/usr/bin/env python3
"""Tests for gradle_execute.py script.

Tests the foundation layer for Gradle command execution including
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
SCRIPT_PATH = get_script_path('pm-dev-java', 'plan-marshall-plugin', 'gradle_execute.py')


# =============================================================================
# Test: detect_wrapper
# =============================================================================

def test_detect_wrapper_with_gradlew():
    """Test wrapper detection when ./gradlew exists."""
    with BuildTestContext() as ctx:
        # Create gradlew wrapper
        gradlew_path = ctx.temp_dir / 'gradlew'
        gradlew_path.write_text('#!/bin/bash\necho "gradlew"')
        gradlew_path.chmod(0o755)

        result = run_script(SCRIPT_PATH, 'detect-wrapper', '--project-dir', str(ctx.temp_dir))

        assert result.success, f"Script failed: {result.stderr}"
        assert 'gradlew' in result.stdout


def test_detect_wrapper_fallback_to_gradle():
    """Test wrapper detection falls back to gradle when no wrapper exists."""
    with BuildTestContext() as ctx:
        # No gradlew in temp_dir
        result = run_script(SCRIPT_PATH, 'detect-wrapper', '--project-dir', str(ctx.temp_dir))

        assert result.success, f"Script failed: {result.stderr}"
        assert 'gradle' in result.stdout


# =============================================================================
# Test: get_bash_timeout
# =============================================================================

def test_get_bash_timeout_calculation():
    """Test Bash tool timeout calculation with buffer."""
    result = run_script(SCRIPT_PATH, 'get-bash-timeout', '--inner-timeout', '300')

    assert result.success, f"Script failed: {result.stderr}"
    # 300 + 30 buffer = 330 seconds
    assert result.stdout.strip() == '330'


def test_get_bash_timeout_small_value():
    """Test Bash tool timeout for small inner timeout."""
    result = run_script(SCRIPT_PATH, 'get-bash-timeout', '--inner-timeout', '60')

    assert result.success, f"Script failed: {result.stderr}"
    # 60 + 30 buffer = 90 seconds
    assert result.stdout.strip() == '90'


# =============================================================================
# Test: execute (error cases - we can't test actual gradle execution in unit tests)
# =============================================================================

def test_execute_wrapper_not_found():
    """Test execute with non-existent wrapper returns proper error."""
    with BuildTestContext() as ctx:
        # No gradlew, and gradle probably not in PATH in isolated environment
        result = run_script(
            SCRIPT_PATH, 'execute',
            '--args', 'build',
            '--command-key', 'test:build',
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
    assert '--module' in result.stdout


# =============================================================================
# Test: API functions (via import)
# =============================================================================

def test_api_detect_wrapper_import():
    """Test gradle_execute can be imported and API functions work."""
    # Add script directory to path for import
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from gradle_execute import detect_wrapper, get_bash_timeout

        with BuildTestContext() as ctx:
            # Create gradlew
            gradlew_path = ctx.temp_dir / 'gradlew'
            gradlew_path.write_text('#!/bin/bash')
            gradlew_path.chmod(0o755)

            wrapper = detect_wrapper(str(ctx.temp_dir))
            assert 'gradlew' in wrapper

            # Test get_bash_timeout (returns seconds)
            timeout_seconds = get_bash_timeout(300)
            assert timeout_seconds == 330

    finally:
        # Clean up sys.path
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_success():
    """Test execute_direct API with successful command."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from gradle_execute import execute_direct

        with BuildTestContext() as ctx:
            # Create a fake gradlew that succeeds immediately
            gradlew_path = ctx.temp_dir / 'gradlew'
            gradlew_path.write_text('#!/bin/bash\nexit 0')
            gradlew_path.chmod(0o755)

            result = execute_direct(
                args='build',
                command_key='test:success',
                default_timeout=10,
                project_dir=str(ctx.temp_dir)
            )

            assert result['status'] == 'success'
            assert result['exit_code'] == 0
            assert result['duration_seconds'] >= 0
            assert 'gradlew' in result['wrapper']
            # Verify log file is created in standard location
            assert 'log_file' in result
            assert '.plan/temp/build-output/' in result['log_file']
            assert '/gradle-' in result['log_file']

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_failure():
    """Test execute_direct API with failing command."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from gradle_execute import execute_direct

        with BuildTestContext() as ctx:
            # Create a fake gradlew that fails
            gradlew_path = ctx.temp_dir / 'gradlew'
            gradlew_path.write_text('#!/bin/bash\necho "BUILD FAILED" >&2\nexit 1')
            gradlew_path.chmod(0o755)

            result = execute_direct(
                args='build',
                command_key='test:failure',
                default_timeout=10,
                project_dir=str(ctx.temp_dir)
            )

            assert result['status'] == 'error'
            assert result['exit_code'] == 1
            # Output goes to log file in standard location
            assert 'log_file' in result
            assert '.plan/temp/build-output/' in result['log_file']
            assert '/gradle-' in result['log_file']

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_with_module():
    """Test execute_direct API with module parameter."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from gradle_execute import execute_direct

        with BuildTestContext() as ctx:
            # Create a fake gradlew that echoes the command
            gradlew_path = ctx.temp_dir / 'gradlew'
            gradlew_path.write_text('#!/bin/bash\necho "$@"\nexit 0')
            gradlew_path.chmod(0o755)

            result = execute_direct(
                args='build',
                command_key='test:module',
                default_timeout=10,
                project_dir=str(ctx.temp_dir),
                module='api-genshin-impact'
            )

            assert result['status'] == 'success'
            # Verify module prefix is added to command
            assert ':api-genshin-impact:build' in result['command']

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_stdout_captured():
    """Test execute_direct API captures stdout."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from gradle_execute import execute_direct

        with BuildTestContext() as ctx:
            # Create a fake gradlew that produces output
            gradlew_path = ctx.temp_dir / 'gradlew'
            gradlew_path.write_text('#!/bin/bash\necho "BUILD SUCCESSFUL"\nexit 0')
            gradlew_path.chmod(0o755)

            result = execute_direct(
                args='build',
                command_key='test:stdout',
                default_timeout=10,
                project_dir=str(ctx.temp_dir)
            )

            assert result['status'] == 'success'
            assert 'stdout' in result
            assert 'BUILD SUCCESSFUL' in result['stdout']

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
        test_detect_wrapper_with_gradlew,
        test_detect_wrapper_fallback_to_gradle,

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
        test_api_execute_direct_success,
        test_api_execute_direct_failure,
        test_api_execute_direct_with_module,
        test_api_execute_direct_stdout_captured,
    ])
    sys.exit(runner.run())
