#!/usr/bin/env python3
"""Run subcommand for Gradle - combines execute + parse on failure.

Uses shared build_parse, build_format, build_result for unified output.
"""

import subprocess
import sys
import time
from pathlib import Path

# Import base library for log file management and result construction
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'))
from build_result import (
    create_log_file,
    success_result,
    error_result,
    timeout_result,
    ERROR_BUILD_FAILED,
    ERROR_EXECUTION_FAILED,
    ERROR_WRAPPER_NOT_FOUND,
    ERROR_LOG_FILE_FAILED,
)
from build_format import format_toon, format_json
from build_parse import (
    filter_warnings,
    load_acceptable_warnings,
    partition_issues,
)

# Import parser (BuildParser protocol implementation)
from gradle_cmd_parse import parse_log


# =============================================================================
# Gradle Command Building and Execution
# =============================================================================

def build_gradle_command(tasks: str, project: str, skip_tests: bool, fail_at_end: bool, gradlew: str) -> list:
    """Build Gradle command list from arguments."""
    cmd = [gradlew]
    cmd.extend(tasks.split())
    if project:
        if project.startswith(":"):
            cmd.append(project)
        else:
            cmd.extend(["-p", project])
    if skip_tests:
        cmd.extend(["-x", "test"])
    if fail_at_end:
        cmd.append("--continue")
    cmd.append("--console=plain")
    return cmd


def execute_gradle(cmd: list, timeout_ms: int, log_file: str) -> dict:
    """Execute Gradle command and return result."""
    timeout_seconds = timeout_ms / 1000.0
    start_time = time.time()

    try:
        with open(log_file, "w", encoding="utf-8") as log_fh:
            result = subprocess.run(cmd, timeout=timeout_seconds, stdout=log_fh, stderr=subprocess.STDOUT, check=False)
        duration_ms = int((time.time() - start_time) * 1000)
        return {"exit_code": result.returncode, "duration_ms": duration_ms, "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "duration_ms": int((time.time() - start_time) * 1000), "timed_out": True}
    except FileNotFoundError:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": f"Gradle wrapper not found: {cmd[0]}"}
    except OSError as e:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": str(e)}


# =============================================================================
# Command Handler
# =============================================================================

def cmd_run(args):
    """Handle run subcommand - execute + auto-parse on failure.

    Supports:
    - --format toon (default) or --format json
    - --mode actionable (default), structured, or errors
    """
    fmt = getattr(args, 'format', 'toon')
    mode = getattr(args, 'mode', 'actionable')
    project_dir = getattr(args, 'project_dir', '.')

    # Select formatter based on output format
    formatter = format_json if fmt == 'json' else format_toon

    # Check for Gradle wrapper
    if not Path(args.gradlew).exists():
        output = error_result(
            error=ERROR_WRAPPER_NOT_FOUND,
            exit_code=-1,
            duration_seconds=0,
            log_file="",
            command="",
        )
        print(formatter(output))
        return 1

    # Determine scope from module/project parameter
    scope = args.project if args.project else "default"

    # Create log file using base library
    log_file = create_log_file("gradle", scope, project_dir)
    if not log_file:
        output = error_result(
            error=ERROR_LOG_FILE_FAILED,
            exit_code=-1,
            duration_seconds=0,
            log_file="",
            command="",
        )
        print(formatter(output))
        return 1

    # Build command using --targets parameter
    cmd = build_gradle_command(args.targets, args.project, args.skip_tests, False, args.gradlew)
    command_str = " ".join(cmd)
    print(f"[EXEC] {command_str}", file=sys.stderr)

    exec_result = execute_gradle(cmd, args.timeout, log_file)
    duration_seconds = exec_result["duration_ms"] // 1000

    # Handle execution errors
    if "error" in exec_result:
        output = error_result(
            error=ERROR_EXECUTION_FAILED,
            exit_code=-1,
            duration_seconds=0,
            log_file=log_file,
            command=command_str,
        )
        print(formatter(output))
        return 1

    # Handle timeout
    if exec_result["timed_out"]:
        timeout_seconds = args.timeout // 1000
        output = timeout_result(
            timeout_used_seconds=timeout_seconds,
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=command_str,
        )
        print(formatter(output))
        return 1

    # Success case
    if exec_result["exit_code"] == 0:
        output = success_result(
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=command_str,
        )
        print(formatter(output))
        return 0

    # Build failed - parse the log file for errors
    try:
        issues, test_summary, build_status = parse_log(log_file)

        # Partition issues into errors and warnings
        errors, warnings = partition_issues(issues)

        # Load acceptable warnings and filter based on mode
        patterns = load_acceptable_warnings(project_dir, "gradle")
        filtered_warnings = filter_warnings(warnings, patterns, mode)

        # Build result dict
        output = error_result(
            error=ERROR_BUILD_FAILED,
            exit_code=exec_result["exit_code"],
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=command_str,
        )

        # Add errors if present
        if errors:
            output["errors"] = errors[:20]

        # Add warnings if present (mode != errors already handled by filter_warnings)
        if filtered_warnings:
            output["warnings"] = filtered_warnings[:10]

        # Add test summary if present
        if test_summary:
            output["tests"] = test_summary

        print(formatter(output))

    except Exception:
        # If parsing fails, still return the build failure
        output = error_result(
            error=ERROR_BUILD_FAILED,
            exit_code=exec_result["exit_code"],
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=command_str,
        )
        print(formatter(output))

    return 1
