#!/usr/bin/env python3
"""Run subcommand for Gradle - combines execute + parse on failure.

Implements the build-return specification with:
- Tab-separated TOON format (default)
- JSON format (--format json)
- Mode-based warning filtering (--mode actionable/structured/errors)
"""

import json
import sys
from pathlib import Path

# Import base library for log file management
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'))
from build_result import create_log_file, STATUS_SUCCESS, STATUS_ERROR, STATUS_TIMEOUT, ERROR_BUILD_FAILED, ERROR_TIMEOUT, ERROR_EXECUTION_FAILED, ERROR_WRAPPER_NOT_FOUND, ERROR_LOG_FILE_FAILED

from gradle_cmd_parse import parse_metrics, categorize_line, extract_file_location


# =============================================================================
# Gradle Command Building and Execution (moved from gradle_cmd_execute.py)
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
    import subprocess
    import time

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
# TOON Format Functions
# =============================================================================

def format_toon_success(log_file: str, exit_code: int, duration_seconds: int, command: str) -> str:
    """Format success result in TOON format (tab-separated)."""
    return f"status\tsuccess\nexit_code\t{exit_code}\nduration_seconds\t{duration_seconds}\nlog_file\t{log_file}\ncommand\t{command}"


def format_toon_error(error_type: str, log_file: str, exit_code: int, duration_seconds: int, command: str, issues: list = None, metrics: dict = None, mode: str = "actionable") -> str:
    """Format error result in TOON format (tab-separated) with optional parsed errors."""
    lines = [
        f"status\terror",
        f"exit_code\t{exit_code}",
        f"duration_seconds\t{duration_seconds}",
        f"log_file\t{log_file}",
        f"command\t{command}",
        f"error\t{error_type}",
    ]

    if issues:
        errors = [i for i in issues if i.get('severity') == 'ERROR']
        warnings = [i for i in issues if i.get('severity') == 'WARNING']

        if errors:
            lines.append("")
            lines.append(f"errors[{len(errors)}]{{file,line,message,category}}:")
            for e in errors[:20]:
                file = e.get('file') or '-'
                line_num = e.get('line') or '-'
                msg = (e.get('message') or '')[:80]
                cat = e.get('type') or 'other'
                lines.append(f"{file}\t{line_num}\t{msg}\t{cat}")

        if mode != "errors" and warnings:
            lines.append("")
            lines.append(f"warnings[{len(warnings)}]{{file,line,message}}:")
            for w in warnings[:10]:
                file = w.get('file') or '-'
                line_num = w.get('line') or '-'
                msg = (w.get('message') or '')[:80]
                lines.append(f"{file}\t{line_num}\t{msg}")

    if metrics and metrics.get('tests_run', 0) > 0:
        lines.append("")
        lines.append("tests:")
        lines.append(f"  passed\t{metrics['tests_run'] - metrics['tests_failed']}")
        lines.append(f"  failed\t{metrics['tests_failed']}")

    return "\n".join(lines)


def format_toon_timeout(timeout_used_seconds: int, duration_seconds: int, log_file: str, command: str) -> str:
    """Format timeout result in TOON format (tab-separated)."""
    lines = [
        f"status\ttimeout",
        f"exit_code\t-1",
        f"duration_seconds\t{duration_seconds}",
        f"log_file\t{log_file}",
        f"command\t{command}",
        f"error\ttimeout",
        f"timeout_used_seconds\t{timeout_used_seconds}",
    ]
    return "\n".join(lines)


# =============================================================================
# JSON Format Functions
# =============================================================================

def format_json_success(log_file: str, exit_code: int, duration_seconds: int, command: str) -> str:
    """Format success result in JSON format."""
    return json.dumps({
        "status": "success",
        "exit_code": exit_code,
        "duration_seconds": duration_seconds,
        "log_file": log_file,
        "command": command
    }, indent=2)


def format_json_error(error_type: str, log_file: str, exit_code: int, duration_seconds: int, command: str, issues: list = None, metrics: dict = None, mode: str = "actionable") -> str:
    """Format error result in JSON format with optional parsed errors."""
    result = {
        "status": "error",
        "exit_code": exit_code,
        "duration_seconds": duration_seconds,
        "log_file": log_file,
        "command": command,
        "error": error_type
    }

    if issues:
        errors = [i for i in issues if i.get('severity') == 'ERROR']
        warnings = [i for i in issues if i.get('severity') == 'WARNING']

        if errors:
            result["errors"] = [
                {"file": e.get('file'), "line": e.get('line'), "message": (e.get('message') or '')[:80], "category": e.get('type') or 'other'}
                for e in errors[:20]
            ]

        if mode != "errors" and warnings:
            result["warnings"] = [
                {"file": w.get('file'), "line": w.get('line'), "message": (w.get('message') or '')[:80]}
                for w in warnings[:10]
            ]

    if metrics and metrics.get('tests_run', 0) > 0:
        result["tests"] = {
            "passed": metrics['tests_run'] - metrics['tests_failed'],
            "failed": metrics['tests_failed'],
            "skipped": 0
        }

    return json.dumps(result, indent=2)


def format_json_timeout(timeout_used_seconds: int, duration_seconds: int, log_file: str, command: str) -> str:
    """Format timeout result in JSON format."""
    return json.dumps({
        "status": "timeout",
        "exit_code": -1,
        "duration_seconds": duration_seconds,
        "log_file": log_file,
        "command": command,
        "error": "timeout",
        "timeout_used_seconds": timeout_used_seconds
    }, indent=2)


# =============================================================================
# Helpers
# =============================================================================

def parse_issues_from_log(log_file: str) -> tuple:
    """Parse issues from log file."""
    issues = []
    seen = set()

    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            log_lines = f.readlines()
    except OSError:
        return [], {}

    for line_num, line in enumerate(log_lines, 1):
        issue_type = categorize_line(line)
        if issue_type:
            file_path, file_line, file_col = extract_file_location(line)
            message = line.strip()
            dedup_key = f"{issue_type}:{file_path}:{file_line}:{message[:100]}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            severity = "ERROR" if "error" in issue_type else "WARNING"
            issues.append({
                "type": issue_type,
                "file": file_path,
                "line": file_line,
                "column": file_col,
                "message": message[:500],
                "severity": severity,
                "log_line": line_num
            })

    metrics = parse_metrics(log_lines)
    return issues, metrics


def output_result(fmt: str, toon_func, json_func, *args, **kwargs):
    """Output result in specified format."""
    if fmt == "json":
        print(json_func(*args, **kwargs))
    else:
        print(toon_func(*args, **kwargs))


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

    # Check for Gradle wrapper
    if not Path(args.gradlew).exists():
        if fmt == "json":
            print(format_json_error(ERROR_WRAPPER_NOT_FOUND, "", -1, 0, ""))
        else:
            print(format_toon_error(ERROR_WRAPPER_NOT_FOUND, "", -1, 0, ""))
        return 1

    # Determine scope from module/project parameter
    scope = args.project if args.project else "default"

    # Create log file using base library
    log_file = create_log_file("gradle", scope, ".")
    if not log_file:
        if fmt == "json":
            print(format_json_error(ERROR_LOG_FILE_FAILED, "", -1, 0, ""))
        else:
            print(format_toon_error(ERROR_LOG_FILE_FAILED, "", -1, 0, ""))
        return 1

    # Build command using --targets parameter
    cmd = build_gradle_command(args.targets, args.project, args.skip_tests, False, args.gradlew)
    command_str = " ".join(cmd)
    print(f"[EXEC] {command_str}", file=sys.stderr)

    exec_result = execute_gradle(cmd, args.timeout, log_file)
    duration_seconds = exec_result["duration_ms"] // 1000

    # Handle execution errors
    if "error" in exec_result:
        if fmt == "json":
            print(format_json_error(ERROR_EXECUTION_FAILED, log_file, -1, 0, command_str))
        else:
            print(format_toon_error(ERROR_EXECUTION_FAILED, log_file, -1, 0, command_str))
        return 1

    # Handle timeout
    if exec_result["timed_out"]:
        timeout_seconds = args.timeout // 1000
        if fmt == "json":
            print(format_json_timeout(timeout_seconds, duration_seconds, log_file, command_str))
        else:
            print(format_toon_timeout(timeout_seconds, duration_seconds, log_file, command_str))
        return 1

    # Success case
    if exec_result["exit_code"] == 0:
        if fmt == "json":
            print(format_json_success(log_file, 0, duration_seconds, command_str))
        else:
            print(format_toon_success(log_file, 0, duration_seconds, command_str))
        return 0

    # Build failed - parse the log file for errors
    try:
        issues, metrics = parse_issues_from_log(log_file)
        if fmt == "json":
            print(format_json_error(ERROR_BUILD_FAILED, log_file, exec_result["exit_code"], duration_seconds, command_str, issues, metrics, mode))
        else:
            print(format_toon_error(ERROR_BUILD_FAILED, log_file, exec_result["exit_code"], duration_seconds, command_str, issues, metrics, mode))
    except Exception:
        if fmt == "json":
            print(format_json_error(ERROR_BUILD_FAILED, log_file, exec_result["exit_code"], duration_seconds, command_str))
        else:
            print(format_toon_error(ERROR_BUILD_FAILED, log_file, exec_result["exit_code"], duration_seconds, command_str))

    return 1
