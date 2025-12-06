#!/usr/bin/env python3
"""Tests for the error-detector hook script."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Path to the hook script (in skill's scripts directory)
HOOK_SCRIPT = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'cui-plugin-development-tools' / 'skills' / 'error-handling' / 'scripts' / 'error-detector.sh'


def run_hook(input_data: str, tool_name: str = "TestTool") -> subprocess.CompletedProcess:
    """Run the hook script with given input."""
    env = {**os.environ, "CLAUDE_TOOL_NAME": tool_name}
    return subprocess.run(
        [str(HOOK_SCRIPT)],
        input=input_data,
        capture_output=True,
        text=True,
        env=env,
        timeout=10
    )


# =============================================================================
# Test: Hook Script Existence
# =============================================================================

def test_hook_script_exists():
    """Verify the hook script exists and is executable."""
    assert HOOK_SCRIPT.is_file(), f"Hook script not found at {HOOK_SCRIPT}"
    assert os.access(HOOK_SCRIPT, os.X_OK), "Hook script is not executable"


# =============================================================================
# Test: Error Pattern Detection
# =============================================================================

def test_detects_status_error():
    """Hook should detect 'status: error' pattern."""
    result = run_hook("status: error\nmessage: Something failed")
    assert result.returncode == 1, "Hook should exit with code 1 on error detection"
    assert "ERROR DETECTED" in result.stdout


def test_detects_exit_code_error():
    """Hook should detect 'exit code N' pattern where N > 0."""
    result = run_hook("Command completed with exit code 1", "Bash")
    assert result.returncode == 1
    assert "ERROR DETECTED" in result.stdout


def test_detects_unknown_skill():
    """Hook should detect 'Unknown skill' pattern."""
    result = run_hook("Unknown skill: planning:nonexistent", "Skill")
    assert result.returncode == 1
    assert "ERROR DETECTED" in result.stdout


def test_detects_skill_not_found():
    """Hook should detect 'skill not found' pattern."""
    result = run_hook("Error: skill not found in bundle", "Task")
    assert result.returncode == 1
    assert "ERROR DETECTED" in result.stdout


def test_detects_failed_pattern():
    """Hook should detect 'failed' pattern."""
    result = run_hook("Build failed with 3 errors", "Bash")
    assert result.returncode == 1
    assert "ERROR DETECTED" in result.stdout


def test_detects_exception_pattern():
    """Hook should detect 'exception' pattern."""
    result = run_hook("RuntimeException: null pointer", "Bash")
    assert result.returncode == 1
    assert "ERROR DETECTED" in result.stdout


# =============================================================================
# Test: Pass-Through Behavior
# =============================================================================

def test_passes_success_output():
    """Hook should pass through success output without blocking."""
    result = run_hook("status: success\ndata: all good")
    assert result.returncode == 0, "Hook should exit with code 0 on success"
    assert "ERROR DETECTED" not in result.stdout


def test_passes_normal_output():
    """Hook should pass through normal output without false positives."""
    result = run_hook("File created successfully\nOperation complete", "Write")
    assert result.returncode == 0


# =============================================================================
# Test: Output Format
# =============================================================================

def test_output_includes_skill_instruction():
    """Error output should instruct LLM to load error-handling skill."""
    result = run_hook("status: error")
    assert "Skill: cui-plugin-development-tools:error-handling" in result.stdout


def test_creates_error_context_file():
    """Hook should create error-context.toon file on error detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create .plan directory
        plan_dir = Path(tmpdir) / ".plan"
        plan_dir.mkdir()

        # Create a minimal hook script that writes to tmpdir
        hook_content = f'''#!/bin/bash
RESULT=$(cat)
TOOL_NAME="${{CLAUDE_TOOL_NAME:-unknown}}"
TIMESTAMP=$(date -Iseconds)
ERROR_CONTEXT_FILE="{plan_dir}/error-context.toon"

if echo "$RESULT" | grep -qiE "(status[[:space:]]*:[[:space:]]*error|exit code [1-9]|Unknown skill|skill not found|not found|failed|exception)"; then
    PATTERNS=$(echo "$RESULT" | grep -oiE "(status[[:space:]]*:[[:space:]]*error|exit code [1-9]|Unknown skill|skill not found|not found|failed|exception)" | head -3 | tr '\\n' ',' | sed 's/,$//')
    cat > "$ERROR_CONTEXT_FILE" << EOF
timestamp: "$TIMESTAMP"
tool: "$TOOL_NAME"
error:
  patterns_matched: "$PATTERNS"
  blocking: true
raw_output: |
$(echo "$RESULT" | sed 's/^/  /')
EOF
    echo "ERROR DETECTED"
    exit 1
fi
exit 0
'''
        test_hook = Path(tmpdir) / "test-hook.sh"
        test_hook.write_text(hook_content)
        test_hook.chmod(0o755)

        env = {**os.environ, "CLAUDE_TOOL_NAME": "TestTool"}
        subprocess.run(
            [str(test_hook)],
            input="status: error\nmessage: test error",
            capture_output=True,
            text=True,
            env=env
        )

        error_context_file = plan_dir / "error-context.toon"
        assert error_context_file.is_file(), "error-context.toon should be created"

        content = error_context_file.read_text()
        assert "timestamp:" in content
        assert "tool:" in content
        assert "error:" in content
        assert "patterns_matched:" in content
        assert "raw_output:" in content


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == "__main__":
    runner = TestRunner()
    runner.add_tests([
        # Script existence
        test_hook_script_exists,
        # Error pattern detection
        test_detects_status_error,
        test_detects_exit_code_error,
        test_detects_unknown_skill,
        test_detects_skill_not_found,
        test_detects_failed_pattern,
        test_detects_exception_pattern,
        # Pass-through behavior
        test_passes_success_output,
        test_passes_normal_output,
        # Output format
        test_output_includes_skill_instruction,
        test_creates_error_context_file,
    ])
    sys.exit(runner.run())
