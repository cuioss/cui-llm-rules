#!/usr/bin/env python3
"""Tests for maven_execute.py script.

Tests the foundation layer for Maven command execution including
wrapper detection, timeout handling, and command execution.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    get_script_path,
    TestRunner,
    BuildTestContext,
)

# Get script path
SCRIPT_PATH = get_script_path('pm-dev-java', 'plan-marshall-plugin', 'maven_execute.py')


# =============================================================================
# Test: API functions (via import)
# =============================================================================

def test_api_detect_wrapper_import():
    """Test maven_execute can be imported and API functions work."""
    # Add script directory to path for import
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from maven_execute import detect_wrapper, get_bash_timeout

        with BuildTestContext() as ctx:
            # Create mvnw
            mvnw_path = ctx.temp_dir / 'mvnw'
            mvnw_path.write_text('#!/bin/bash')
            mvnw_path.chmod(0o755)

            wrapper = detect_wrapper(str(ctx.temp_dir))
            assert 'mvnw' in wrapper

            # Test get_bash_timeout (returns seconds)
            timeout_seconds = get_bash_timeout(300)
            assert timeout_seconds == 330

    finally:
        # Clean up sys.path
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_detect_wrapper_fallback():
    """Test detect_wrapper API falls back to mvn when no wrapper exists."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from maven_execute import detect_wrapper

        with BuildTestContext() as ctx:
            # No mvnw in temp_dir
            wrapper = detect_wrapper(str(ctx.temp_dir))
            assert wrapper == 'mvn'

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_get_bash_timeout():
    """Test get_bash_timeout API adds buffer correctly."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from maven_execute import get_bash_timeout

        # Test various values
        assert get_bash_timeout(300) == 330  # 300 + 30 buffer
        assert get_bash_timeout(60) == 90    # 60 + 30 buffer
        assert get_bash_timeout(120) == 150  # 120 + 30 buffer

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_success():
    """Test execute_direct API with successful command."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from maven_execute import execute_direct

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
            # Verify log file is created in standard location
            assert 'log_file' in result
            assert '.plan/temp/build-output/' in result['log_file']
            assert '/maven-' in result['log_file']
            # Verify command includes wrapper
            assert 'mvnw' in result['command']

    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))


def test_api_execute_direct_failure():
    """Test execute_direct API with failing command."""
    script_dir = SCRIPT_PATH.parent
    sys.path.insert(0, str(script_dir))

    try:
        from maven_execute import execute_direct

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
        # API functions
        test_api_detect_wrapper_import,
        test_api_detect_wrapper_fallback,
        test_api_get_bash_timeout,
        test_api_execute_direct_success,
        test_api_execute_direct_failure,
    ])
    sys.exit(runner.run())
