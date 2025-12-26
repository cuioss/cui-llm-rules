#!/usr/bin/env python3
"""Run subcommand for Gradle - combines execute + parse on failure."""

import sys
from pathlib import Path

from gradle_cmd_execute import generate_log_filename, pre_create_log_file, build_gradle_command, execute_gradle
from gradle_cmd_parse import parse_build_status, parse_metrics, categorize_line, extract_file_location


def format_toon_success(log_file: str, exit_code: int, duration_ms: int, command: str) -> str:
    """Format success result in TOON format."""
    duration_sec = duration_ms // 1000
    return f"""status: success
log_file: {log_file}
exit_code: {exit_code}
duration_seconds: {duration_sec}
command_executed: {command}"""


def format_toon_error(error_type: str, message: str, log_file: str, exit_code: int, duration_ms: int, command: str, issues: list = None, metrics: dict = None, mode: str = "actionable") -> str:
    """Format error result in TOON format with optional parsed errors."""
    duration_sec = duration_ms // 1000
    lines = [
        f"status: error",
        f"error: {error_type}",
        f"log_file: {log_file}",
        f"exit_code: {exit_code}",
        f"duration_seconds: {duration_sec}",
        f"command_executed: {command}",
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
                lines.append(f"{file}    {line_num}    {msg}    {cat}")

        if mode != "errors" and warnings:
            lines.append("")
            lines.append(f"warnings[{len(warnings)}]{{file,line,message}}:")
            for w in warnings[:10]:
                file = w.get('file') or '-'
                line_num = w.get('line') or '-'
                msg = (w.get('message') or '')[:80]
                lines.append(f"{file}    {line_num}    {msg}")

    if metrics and metrics.get('tests_run', 0) > 0:
        lines.append("")
        lines.append("tests:")
        passed = metrics['tests_run'] - metrics['tests_failed']
        lines.append(f"  passed: {passed}")
        lines.append(f"  failed: {metrics['tests_failed']}")

    return "\n".join(lines)


def parse_issues_from_log(log_file: str) -> tuple:
    """Parse issues from log file."""
    issues = []
    seen = set()

    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
        log_lines = f.readlines()

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


def cmd_run(args):
    """Handle run subcommand - execute + auto-parse on failure."""
    if not Path(args.gradlew).exists():
        print(f"status: error\nerror: gradlew_not_found\nmessage: Gradle wrapper not found at {args.gradlew}")
        return 1

    log_file = generate_log_filename()
    if not pre_create_log_file(log_file):
        print(f"status: error\nerror: log_file_creation_failed\nmessage: Failed to create log file: {log_file}")
        return 1

    # Build command using --targets parameter (mapped to tasks internally)
    cmd = build_gradle_command(args.targets, args.project, args.skip_tests, False, args.gradlew)
    command_str = " ".join(cmd)
    print(f"[EXEC] {command_str}", file=sys.stderr)

    exec_result = execute_gradle(cmd, args.timeout, log_file)

    # Handle execution errors
    if "error" in exec_result:
        print(format_toon_error("execution_failed", exec_result["error"], log_file, -1, 0, command_str))
        return 1

    # Handle timeout
    if exec_result["timed_out"]:
        print(format_toon_error("timeout", f"Build timed out after {args.timeout}ms", log_file, -1, exec_result["duration_ms"], command_str))
        return 1

    # Success case
    if exec_result["exit_code"] == 0:
        print(format_toon_success(log_file, 0, exec_result["duration_ms"], command_str))
        return 0

    # Build failed - parse the log file for errors
    try:
        issues, metrics = parse_issues_from_log(log_file)
        print(format_toon_error(
            "build_failed",
            f"Build failed with exit code {exec_result['exit_code']}",
            log_file,
            exec_result["exit_code"],
            exec_result["duration_ms"],
            command_str,
            issues,
            metrics,
            args.mode
        ))
    except Exception:
        print(format_toon_error(
            "build_failed",
            f"Build failed with exit code {exec_result['exit_code']}",
            log_file,
            exec_result["exit_code"],
            exec_result["duration_ms"],
            command_str
        ))

    return 1
