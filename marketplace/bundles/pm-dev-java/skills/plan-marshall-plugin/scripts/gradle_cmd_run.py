#!/usr/bin/env python3
"""Run subcommand for Gradle - combines execute + parse on failure.

Uses gradle_execute as the foundation layer for all Gradle execution.
Uses shared build_parse, build_format, build_result for unified output.
"""

import sys
from pathlib import Path

# Import base library for log file management and result construction
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'))
from build_result import (
    success_result,
    error_result,
    timeout_result,
    ERROR_BUILD_FAILED,
    ERROR_EXECUTION_FAILED,
    ERROR_LOG_FILE_FAILED,
)
from build_format import format_toon, format_json
from build_parse import (
    filter_warnings,
    load_acceptable_warnings,
    partition_issues,
)

# Import from gradle_execute (foundation layer)
from gradle_execute import execute_direct, DEFAULT_TIMEOUT_SECONDS

# Import parser (BuildParser protocol implementation)
from gradle_cmd_parse import parse_log


# =============================================================================
# Command Handler
# =============================================================================

def cmd_run(args):
    """Handle run subcommand - execute + auto-parse on failure.

    Delegates to execute_direct() for all Gradle execution.

    Supports:
    - --format toon (default) or --format json
    - --mode actionable (default), structured, or errors
    """
    fmt = getattr(args, 'format', 'toon')
    mode = getattr(args, 'mode', 'actionable')
    project_dir = getattr(args, 'project_dir', '.')

    # Select formatter based on output format
    formatter = format_json if fmt == 'json' else format_toon

    # Build command key for timeout learning (use first task as key)
    command_args = args.commandArgs
    first_task = command_args.split()[0] if command_args else "default"
    # Clean up task name for command key (remove leading colons)
    task_name = first_task.lstrip(':').replace(':', '_')
    command_key = f"gradle:{task_name}"

    # Get timeout (convert ms to seconds if needed)
    if hasattr(args, 'timeout') and args.timeout:
        timeout_seconds = args.timeout // 1000 if args.timeout > 1000 else args.timeout
    else:
        timeout_seconds = DEFAULT_TIMEOUT_SECONDS

    # Execute via direct_command foundation layer
    # commandArgs is complete and self-contained (includes :module:task prefix)
    result = execute_direct(
        args=command_args,
        command_key=command_key,
        default_timeout=timeout_seconds,
        project_dir=project_dir
    )

    log_file = result['log_file']
    command_str = result['command']
    print(f"[EXEC] {command_str}", file=sys.stderr)

    # Handle execution errors (wrapper not found, log file creation failed)
    if result['status'] == 'error' and result['exit_code'] == -1:
        error_type = ERROR_EXECUTION_FAILED
        if 'log file' in result.get('error', '').lower():
            error_type = ERROR_LOG_FILE_FAILED

        output = error_result(
            error=error_type,
            exit_code=-1,
            duration_seconds=0,
            log_file=log_file,
            command=command_str,
        )
        print(formatter(output))
        return 1

    # Handle timeout
    if result['status'] == 'timeout':
        output = timeout_result(
            timeout_used_seconds=result['timeout_used_seconds'],
            duration_seconds=result['duration_seconds'],
            log_file=log_file,
            command=command_str,
        )
        print(formatter(output))
        return 1

    # Success case
    if result['status'] == 'success':
        output = success_result(
            duration_seconds=result['duration_seconds'],
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
            exit_code=result["exit_code"],
            duration_seconds=result["duration_seconds"],
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
            exit_code=result["exit_code"],
            duration_seconds=result["duration_seconds"],
            log_file=log_file,
            command=command_str,
        )
        print(formatter(output))

    return 1
