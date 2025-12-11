#!/usr/bin/env python3
"""Tests for manage-log.py CLI script.

New simplified API: manage-log {type} {plan_id} {level} "{message}"
- type: script or work
- plan_id: plan identifier
- level: SUCCESS, ERROR, INFO, WARN
- message: log message

No stdout output, exit code only.
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, PlanTestContext

# Get script path
SCRIPT_PATH = get_script_path('plan-marshall', 'logging', 'manage-log.py')


def read_log_file(plan_dir: Path, log_type: str) -> str:
    """Read log file content."""
    filename = 'work.log' if log_type == 'work' else 'script-execution.log'
    log_file = plan_dir / filename
    if log_file.exists():
        return log_file.read_text()
    return ''


# =============================================================================
# Test: Script Type Logging
# =============================================================================

def test_script_success():
    """Test script type logs SUCCESS entry."""
    with PlanTestContext(plan_id='log-script-success') as ctx:
        result = run_script(SCRIPT_PATH,
            'script', 'log-script-success', 'SUCCESS', 'test:skill:script add (0.15s)'
        )
        assert result.success, f"Script failed: {result.stderr}"
        assert result.stdout == '', "Expected no stdout output"

        log_content = read_log_file(ctx.plan_dir, 'script')
        assert '[SUCCESS]' in log_content
        assert '[SCRIPT]' in log_content
        assert 'test:skill:script add (0.15s)' in log_content


def test_script_error():
    """Test script type logs ERROR entry."""
    with PlanTestContext(plan_id='log-script-error') as ctx:
        result = run_script(SCRIPT_PATH,
            'script', 'log-script-error', 'ERROR', 'test:skill:script add failed'
        )
        assert result.success, f"Script failed: {result.stderr}"

        log_content = read_log_file(ctx.plan_dir, 'script')
        assert '[ERROR]' in log_content
        assert '[SCRIPT]' in log_content


# =============================================================================
# Test: Work Type Logging
# =============================================================================

def test_work_info():
    """Test work type logs INFO entry."""
    with PlanTestContext(plan_id='log-work-info') as ctx:
        result = run_script(SCRIPT_PATH,
            'work', 'log-work-info', 'INFO', 'Created deliverable: auth module'
        )
        assert result.success, f"Script failed: {result.stderr}"
        assert result.stdout == '', "Expected no stdout output"

        log_content = read_log_file(ctx.plan_dir, 'work')
        assert '[INFO]' in log_content
        assert '[WORK]' in log_content
        assert 'Created deliverable: auth module' in log_content


def test_work_warn():
    """Test work type logs WARN entry."""
    with PlanTestContext(plan_id='log-work-warn') as ctx:
        result = run_script(SCRIPT_PATH,
            'work', 'log-work-warn', 'WARN', 'Skipped validation step'
        )
        assert result.success, f"Script failed: {result.stderr}"

        log_content = read_log_file(ctx.plan_dir, 'work')
        assert '[WARN]' in log_content
        assert '[WORK]' in log_content


# =============================================================================
# Test: Validation
# =============================================================================

def test_invalid_type():
    """Test that invalid type fails."""
    with PlanTestContext(plan_id='log-invalid-type'):
        result = run_script(SCRIPT_PATH,
            'invalid', 'log-invalid-type', 'INFO', 'Test message'
        )
        assert not result.success, "Expected failure for invalid type"
        assert "type must be one of" in result.stderr


def test_invalid_level():
    """Test that invalid level fails."""
    with PlanTestContext(plan_id='log-invalid-level'):
        result = run_script(SCRIPT_PATH,
            'work', 'log-invalid-level', 'INVALID', 'Test message'
        )
        assert not result.success, "Expected failure for invalid level"
        assert "level must be one of" in result.stderr


def test_missing_args():
    """Test that missing args fails."""
    result = run_script(SCRIPT_PATH, 'work', 'my-plan', 'INFO')
    assert not result.success, "Expected failure for missing args"
    assert "Usage:" in result.stderr


def test_multiple_entries():
    """Test multiple log entries append correctly."""
    with PlanTestContext(plan_id='log-multiple') as ctx:
        run_script(SCRIPT_PATH, 'work', 'log-multiple', 'INFO', 'First entry')
        run_script(SCRIPT_PATH, 'work', 'log-multiple', 'SUCCESS', 'Second entry')
        run_script(SCRIPT_PATH, 'work', 'log-multiple', 'WARN', 'Third entry')

        log_content = read_log_file(ctx.plan_dir, 'work')
        assert 'First entry' in log_content
        assert 'Second entry' in log_content
        assert 'Third entry' in log_content


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # script type
        test_script_success,
        test_script_error,
        # work type
        test_work_info,
        test_work_warn,
        # validation
        test_invalid_type,
        test_invalid_level,
        test_missing_args,
        test_multiple_entries,
    ])
    sys.exit(runner.run())
