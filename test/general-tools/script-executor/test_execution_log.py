#!/usr/bin/env python3
"""Unit tests for execution_log module."""

import os
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Add the scripts directory to path for importing
SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "marketplace/bundles/general-tools/skills/script-executor/scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import execution_log as module


# =============================================================================
# TESTS: extract_plan_id
# =============================================================================

def test_extract_plan_id_with_space_separator():
    """Extract plan-id with --plan-id value format."""
    args = ['add', '--plan-id', 'my-plan', '--file', 'test.md']
    result = module.extract_plan_id(args)
    assert result == 'my-plan', f"Expected 'my-plan', got {result}"


def test_extract_plan_id_with_equals_separator():
    """Extract plan-id with --plan-id=value format."""
    args = ['add', '--plan-id=my-plan', '--file', 'test.md']
    result = module.extract_plan_id(args)
    assert result == 'my-plan', f"Expected 'my-plan', got {result}"


def test_extract_plan_id_missing():
    """Return None when --plan-id is not present."""
    args = ['add', '--file', 'test.md']
    result = module.extract_plan_id(args)
    assert result is None, f"Expected None, got {result}"


def test_extract_plan_id_empty_args():
    """Return None for empty args list."""
    result = module.extract_plan_id([])
    assert result is None, f"Expected None, got {result}"


# =============================================================================
# TESTS: format_success_entry
# =============================================================================

def test_success_entry_format():
    """Success entry is compact single-line."""
    entry = module.format_success_entry(
        notation='planning:manage-files',
        subcommand='add',
        exit_code=0,
        duration=0.15
    )

    # Should be single line ending with newline
    lines = entry.strip().split('\n')
    assert len(lines) == 1, f"Expected 1 line, got {len(lines)}"

    # Should contain expected fields
    assert 'planning:manage-files' in entry, "Missing notation"
    assert 'add' in entry, "Missing subcommand"
    assert '0.15s' in entry, "Missing duration"


def test_success_entry_tab_separated():
    """Success entry uses tab separators."""
    entry = module.format_success_entry(
        notation='test:skill',
        subcommand='verb',
        exit_code=0,
        duration=1.0
    )

    parts = entry.strip().split('\t')
    assert len(parts) >= 4, f"Expected at least 4 tab-separated parts, got {len(parts)}"


# =============================================================================
# TESTS: format_error_entry
# =============================================================================

def test_error_entry_multiline():
    """Error entry is multi-line with details."""
    entry = module.format_error_entry(
        notation='planning:manage-files',
        subcommand='add',
        exit_code=1,
        duration=0.23,
        args=['--plan-id', 'my-plan', '--file', 'missing.md'],
        stdout='',
        stderr='FileNotFoundError: missing.md not found'
    )

    lines = entry.strip().split('\n')
    assert len(lines) >= 2, f"Expected at least 2 lines, got {len(lines)}"

    # First line should have ERROR marker
    assert 'ERROR' in lines[0], "Missing ERROR marker in first line"

    # Should include args
    assert any('args:' in line for line in lines), "Missing args line"


def test_error_entry_includes_stderr():
    """Error entry includes stderr when present."""
    entry = module.format_error_entry(
        notation='test:skill',
        subcommand='verb',
        exit_code=1,
        duration=0.5,
        args=['--arg', 'value'],
        stdout='',
        stderr='Error message here'
    )

    assert 'stderr:' in entry, "Missing stderr line"
    assert 'Error message' in entry, "Missing error message content"


# =============================================================================
# TESTS: cleanup_old_global_logs
# =============================================================================

def test_cleanup_deletes_old_logs():
    """Cleanup deletes logs older than max_age_days."""
    with tempfile.TemporaryDirectory() as tmp:
        # Create .plan/logs structure
        plan_base = Path(tmp)
        log_dir = plan_base / 'logs'
        log_dir.mkdir()

        # Create an old log file
        old_log = log_dir / 'script-execution-2020-01-01.log'
        old_log.write_text('old log')

        # Set modification time to 30 days ago
        old_time = time.time() - (30 * 86400)
        os.utime(old_log, (old_time, old_time))

        # Use PLAN_BASE_DIR environment variable for test isolation
        original_env = os.environ.get('PLAN_BASE_DIR')
        os.environ['PLAN_BASE_DIR'] = str(plan_base)

        try:
            deleted = module.cleanup_old_global_logs(max_age_days=7)
            assert deleted == 1, f"Expected 1 deleted, got {deleted}"
            assert not old_log.exists(), "Old log should be deleted"
        finally:
            if original_env is not None:
                os.environ['PLAN_BASE_DIR'] = original_env
            elif 'PLAN_BASE_DIR' in os.environ:
                del os.environ['PLAN_BASE_DIR']


def test_cleanup_preserves_recent_logs():
    """Cleanup preserves logs newer than max_age_days."""
    with tempfile.TemporaryDirectory() as tmp:
        # Create .plan/logs structure
        plan_base = Path(tmp)
        log_dir = plan_base / 'logs'
        log_dir.mkdir()

        # Create a recent log file
        recent_log = log_dir / f'script-execution-{date.today()}.log'
        recent_log.write_text('recent log')

        original_env = os.environ.get('PLAN_BASE_DIR')
        os.environ['PLAN_BASE_DIR'] = str(plan_base)

        try:
            deleted = module.cleanup_old_global_logs(max_age_days=7)
            assert deleted == 0, f"Expected 0 deleted, got {deleted}"
            assert recent_log.exists(), "Recent log should be preserved"
        finally:
            if original_env is not None:
                os.environ['PLAN_BASE_DIR'] = original_env
            elif 'PLAN_BASE_DIR' in os.environ:
                del os.environ['PLAN_BASE_DIR']


def test_cleanup_returns_zero_for_missing_dir():
    """Cleanup returns 0 when log directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmp:
        # Point to a directory without logs subdirectory
        nonexistent_base = Path(tmp) / 'nonexistent'

        original_env = os.environ.get('PLAN_BASE_DIR')
        os.environ['PLAN_BASE_DIR'] = str(nonexistent_base)

        try:
            deleted = module.cleanup_old_global_logs()
            assert deleted == 0, f"Expected 0 deleted, got {deleted}"
        finally:
            if original_env is not None:
                os.environ['PLAN_BASE_DIR'] = original_env
            elif 'PLAN_BASE_DIR' in os.environ:
                del os.environ['PLAN_BASE_DIR']


if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_extract_plan_id_with_space_separator,
        test_extract_plan_id_with_equals_separator,
        test_extract_plan_id_missing,
        test_extract_plan_id_empty_args,
        test_success_entry_format,
        test_success_entry_tab_separated,
        test_error_entry_multiline,
        test_error_entry_includes_stderr,
        test_cleanup_deletes_old_logs,
        test_cleanup_preserves_recent_logs,
        test_cleanup_returns_zero_for_missing_dir,
    ])
    sys.exit(runner.run())
