#!/usr/bin/env python3
"""Unit tests for await-until.py synchronous polling utility."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner, run_script, get_script_path

# Path to the script
SCRIPT_PATH = get_script_path('plan-marshall', 'script-executor', 'await-until.py')


# =============================================================================
# Helper Functions
# =============================================================================

def parse_toon_result(stdout: str) -> dict:
    """Parse TOON output into dict."""
    result = {}
    for line in stdout.strip().split('\n'):
        if '\t' in line:
            key, value = line.split('\t', 1)
            result[key.strip()] = value.strip()
    return result


# =============================================================================
# TESTS: Help output
# =============================================================================

def test_help_output():
    """Script shows help with poll subcommand."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.success, f"Script failed: {result.stderr}"
    assert 'poll' in result.stdout, "Help should mention poll subcommand"


def test_poll_help_output():
    """Poll subcommand shows help with all options."""
    result = run_script(SCRIPT_PATH, 'poll', '--help')
    assert result.success, f"Script failed: {result.stderr}"
    assert '--check-cmd' in result.stdout, "Help should mention --check-cmd"
    assert '--success-field' in result.stdout, "Help should mention --success-field"
    assert '--timeout' in result.stdout, "Help should mention --timeout"
    assert '--command-key' in result.stdout, "Help should mention --command-key"


# =============================================================================
# TESTS: Immediate success
# =============================================================================

def test_immediate_success():
    """Poll returns success on first check if condition satisfied."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', "printf 'status\\tsuccess\\n'",
        '--success-field', 'status=success',
        '--timeout', '10',
        '--interval', '1'
    )
    assert result.success, f"Script failed: {result.stderr}"

    parsed = parse_toon_result(result.stdout)
    assert parsed.get('status') == 'success', f"Expected status=success, got {parsed.get('status')}"
    assert parsed.get('polls') == '1', f"Expected 1 poll, got {parsed.get('polls')}"
    assert 'duration_ms' in parsed, "Missing duration_ms"


def test_success_with_different_field():
    """Poll checks custom success field."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', "printf 'state\\tcompleted\\nresult\\tpassed\\n'",
        '--success-field', 'state=completed',
        '--timeout', '10',
        '--interval', '1'
    )
    assert result.success, f"Script failed: {result.stderr}"

    parsed = parse_toon_result(result.stdout)
    assert parsed.get('status') == 'success'


# =============================================================================
# TESTS: Timeout
# =============================================================================

def test_timeout_when_never_satisfied():
    """Poll returns timeout when condition never satisfied."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', "printf 'status\\tpending\\n'",
        '--success-field', 'status=success',
        '--timeout', '2',
        '--interval', '1'
    )
    assert not result.success, "Should fail on timeout"

    parsed = parse_toon_result(result.stdout)
    assert parsed.get('status') == 'timeout', f"Expected status=timeout, got {parsed.get('status')}"
    assert 'error' in parsed, "Should have error message"


def test_explicit_timeout_source():
    """Explicit timeout is reflected in timeout_source."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', "printf 'status\\tsuccess\\n'",
        '--success-field', 'status=success',
        '--timeout', '60',
        '--interval', '1'
    )
    assert result.success

    parsed = parse_toon_result(result.stdout)
    assert parsed.get('timeout_source') == 'explicit', f"Expected explicit, got {parsed.get('timeout_source')}"
    assert parsed.get('timeout_used_ms') == '60000', f"Expected 60000ms, got {parsed.get('timeout_used_ms')}"


# =============================================================================
# TESTS: Failure detection
# =============================================================================

def test_failure_detection():
    """Poll returns failure when failure condition matches."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', "printf 'status\\tfailure\\nerror\\tBuild failed\\n'",
        '--success-field', 'status=success',
        '--failure-field', 'status=failure',
        '--timeout', '10',
        '--interval', '1'
    )
    assert not result.success, "Should fail on failure condition"

    parsed = parse_toon_result(result.stdout)
    assert parsed.get('status') == 'failure', f"Expected status=failure, got {parsed.get('status')}"
    assert parsed.get('polls') == '1', "Should detect failure on first poll"


# =============================================================================
# TESTS: Multiple polls
# =============================================================================

def test_multiple_polls_before_success():
    """Poll continues until condition is satisfied."""
    # Create a script that returns pending first, then success
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''#!/usr/bin/env python3
import os
import sys

state_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/poll_state.txt'

try:
    with open(state_file) as f:
        count = int(f.read().strip())
except:
    count = 0

count += 1
with open(state_file, 'w') as f:
    f.write(str(count))

if count >= 2:
    print("status\\tsuccess")
else:
    print("status\\tpending")
''')
        temp_script = f.name

    state_file = tempfile.mktemp()
    try:
        result = run_script(
            SCRIPT_PATH, 'poll',
            '--check-cmd', f"python3 {temp_script} {state_file}",
            '--success-field', 'status=success',
            '--timeout', '10',
            '--interval', '1'
        )
        assert result.success, f"Script failed: {result.stderr}"

        parsed = parse_toon_result(result.stdout)
        polls = int(parsed.get('polls', 0))
        assert polls >= 2, f"Expected at least 2 polls, got {polls}"
    finally:
        os.unlink(temp_script)
        if os.path.exists(state_file):
            os.unlink(state_file)


# =============================================================================
# TESTS: Adaptive timeout with run-config
# =============================================================================

def test_adaptive_timeout_from_run_config():
    """Adaptive timeout uses run-config history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create run-configuration.json with execution history
        run_config = {
            "version": 1,
            "commands": {
                "test:operation": {
                    "last_execution": {
                        "date": "2025-01-15",
                        "duration_ms": 100000,  # 100s -> adaptive should be 150s
                        "status": "SUCCESS"
                    }
                }
            }
        }
        config_path = Path(tmpdir) / '.plan' / 'run-configuration.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(run_config))

        # Run with command-key (adaptive mode)
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), 'poll',
             '--check-cmd', "printf 'status\\tsuccess\\n'",
             '--success-field', 'status=success',
             '--command-key', 'test:operation',
             '--interval', '1'],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=30
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        parsed = parse_toon_result(result.stdout)
        assert parsed.get('timeout_source') == 'adaptive', f"Expected adaptive, got {parsed.get('timeout_source')}"
        # 100000ms * 1.5 = 150000ms, clamped to bounds
        timeout_ms = int(parsed.get('timeout_used_ms', 0))
        assert timeout_ms == 150000, f"Expected 150000ms (100s * 1.5), got {timeout_ms}"


def test_default_timeout_without_history():
    """Default timeout used when no run-config history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create empty run-configuration.json
        run_config = {"version": 1, "commands": {}}
        config_path = Path(tmpdir) / '.plan' / 'run-configuration.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(run_config))

        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), 'poll',
             '--check-cmd', "printf 'status\\tsuccess\\n'",
             '--success-field', 'status=success',
             '--command-key', 'unknown:operation',
             '--interval', '1'],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=30
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        parsed = parse_toon_result(result.stdout)
        assert parsed.get('timeout_source') == 'default', f"Expected default, got {parsed.get('timeout_source')}"
        assert parsed.get('timeout_used_ms') == '300000', f"Expected 300000ms default, got {parsed.get('timeout_used_ms')}"


def test_execution_history_updated():
    """Execution history is updated after successful poll."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create empty run-configuration.json
        run_config = {"version": 1, "commands": {}}
        config_path = Path(tmpdir) / '.plan' / 'run-configuration.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(run_config))

        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), 'poll',
             '--check-cmd', "printf 'status\\tsuccess\\n'",
             '--success-field', 'status=success',
             '--command-key', 'new:operation',
             '--interval', '1'],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=30
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Check run-config was updated
        updated_config = json.loads(config_path.read_text())
        assert 'new:operation' in updated_config.get('commands', {}), "Command entry should be created"
        cmd_entry = updated_config['commands']['new:operation']
        assert 'last_execution' in cmd_entry, "last_execution should be set"
        assert cmd_entry['last_execution']['status'] == 'SUCCESS', "Status should be SUCCESS"
        assert 'duration_ms' in cmd_entry['last_execution'], "duration_ms should be recorded"


# =============================================================================
# TESTS: Final result fields
# =============================================================================

def test_final_result_fields():
    """Final result fields are flattened in output."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', "printf 'status\\tsuccess\\nstate\\tcompleted\\nconclusion\\tpassed\\n'",
        '--success-field', 'status=success',
        '--timeout', '10',
        '--interval', '1'
    )
    assert result.success

    parsed = parse_toon_result(result.stdout)
    assert parsed.get('final_result.status') == 'success', "Should include final_result.status"
    assert parsed.get('final_result.state') == 'completed', "Should include final_result.state"
    assert parsed.get('final_result.conclusion') == 'passed', "Should include final_result.conclusion"


# =============================================================================
# TESTS: Error handling
# =============================================================================

def test_check_command_error():
    """Handle check command failures gracefully."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', 'exit 1',
        '--success-field', 'status=success',
        '--timeout', '2',
        '--interval', '1'
    )
    # Should timeout (command failure = pending, not immediate failure)
    assert not result.success, "Should fail (timeout)"

    parsed = parse_toon_result(result.stdout)
    assert parsed.get('status') == 'timeout'


def test_missing_required_args():
    """Missing required arguments cause error."""
    result = run_script(SCRIPT_PATH, 'poll', '--check-cmd', 'echo test')
    assert not result.success, "Should fail without --success-field"
    assert 'required' in result.stderr.lower() or 'success-field' in result.stderr.lower()


# =============================================================================
# TESTS: Case insensitive matching
# =============================================================================

def test_case_insensitive_matching():
    """Success/failure field matching is case insensitive."""
    result = run_script(
        SCRIPT_PATH, 'poll',
        '--check-cmd', "printf 'status\\tSUCCESS\\n'",
        '--success-field', 'status=success',
        '--timeout', '10',
        '--interval', '1'
    )
    assert result.success, f"Should match SUCCESS to success: {result.stderr}"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_help_output,
        test_poll_help_output,
        test_immediate_success,
        test_success_with_different_field,
        test_timeout_when_never_satisfied,
        test_explicit_timeout_source,
        test_failure_detection,
        test_multiple_polls_before_success,
        test_adaptive_timeout_from_run_config,
        test_default_timeout_without_history,
        test_execution_history_updated,
        test_final_result_fields,
        test_check_command_error,
        test_missing_required_args,
        test_case_insensitive_matching,
    ])
    sys.exit(runner.run())
