#!/usr/bin/env python3
"""Run subcommand for Maven - combines execute + parse on failure.

Uses direct_command as the foundation layer for all Maven execution.
"""

import json
import re
import sys
from pathlib import Path

# Import from direct_command (foundation layer)
from direct_command import (
    execute_direct,
    DEFAULT_TIMEOUT_SECONDS
)
from maven_cmd_parse import (
    detect_build_status,
    extract_duration,
    extract_test_summary,
    extract_issues,
    generate_summary
)

def load_acceptable_warnings(project_dir: str = '.') -> dict:
    """Load acceptable_warnings from run-configuration.json.

    Args:
        project_dir: Project root directory

    Returns:
        Dict with warning patterns by category: {category: [patterns]}
    """
    config_path = Path(project_dir).resolve() / '.plan' / 'run-configuration.json'
    if not config_path.exists():
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('maven', {}).get('acceptable_warnings', {})
    except (json.JSONDecodeError, IOError):
        return {}


def is_warning_accepted(warning: dict, acceptable: dict) -> bool:
    """Check if a warning matches any acceptable pattern.

    Args:
        warning: Warning dict with 'message', 'file', etc.
        acceptable: Dict of {category: [patterns]}

    Returns:
        True if warning matches any acceptable pattern
    """
    message = warning.get('message', '')
    if not message:
        return False

    # Check all patterns across all categories
    for category, patterns in acceptable.items():
        for pattern in patterns:
            # Support simple substring match and regex
            try:
                if pattern in message or re.search(pattern, message, re.IGNORECASE):
                    return True
            except re.error:
                # Invalid regex, try substring only
                if pattern in message:
                    return True

    return False


def filter_warnings(warnings: list, acceptable: dict, mode: str = 'actionable') -> list:
    """Filter warnings based on acceptable patterns and mode.

    Args:
        warnings: List of warning dicts
        acceptable: Dict of {category: [patterns]}
        mode: 'actionable' (filter out accepted), 'structured' (mark accepted), 'errors' (no warnings)

    Returns:
        Filtered/annotated list of warnings
    """
    if mode == 'errors':
        return []

    if not acceptable:
        return warnings

    result = []
    for warning in warnings:
        accepted = is_warning_accepted(warning, acceptable)

        if mode == 'actionable':
            # Filter out accepted warnings
            if not accepted:
                result.append(warning)
        elif mode == 'structured':
            # Keep all, mark accepted ones
            warning_copy = warning.copy()
            warning_copy['accepted'] = accepted
            result.append(warning_copy)
        else:
            result.append(warning)

    return result


def format_toon_success(log_file: str, exit_code: int, duration_seconds: int, command: str) -> str:
    """Format success result in TOON format."""
    return f"""status: success
log_file: {log_file}
exit_code: {exit_code}
duration_seconds: {duration_seconds}
command_executed: {command}"""


def format_toon_error(
    error_type: str,
    message: str,
    log_file: str,
    exit_code: int,
    duration_seconds: int,
    command: str,
    issues: list = None,
    test_summary: dict = None,
    mode: str = "actionable"
) -> str:
    """Format error result in TOON format with optional parsed errors.

    Args:
        error_type: Error type identifier
        message: Error message
        log_file: Path to log file
        exit_code: Process exit code
        duration_seconds: Duration in seconds
        command: Executed command string
        issues: List of parsed issues (already filtered based on mode)
        test_summary: Test summary dict
        mode: Output mode (actionable, structured, errors)

    Returns:
        TOON formatted string
    """
    lines = [
        f"status: error",
        f"error: {error_type}",
        f"log_file: {log_file}",
        f"exit_code: {exit_code}",
        f"duration_seconds: {duration_seconds}",
        f"command_executed: {command}",
    ]

    if issues:
        errors = [i for i in issues if i.get('severity') == 'ERROR']
        warnings = [i for i in issues if i.get('severity') == 'WARNING']

        if errors:
            lines.append("")
            lines.append(f"errors[{len(errors)}]{{file,line,message,category}}:")
            for e in errors[:20]:  # Limit to 20 errors
                file = e.get('file') or '-'
                line = e.get('line') or '-'
                msg = (e.get('message') or '')[:80]
                cat = e.get('type') or 'other'
                lines.append(f"{file}    {line}    {msg}    {cat}")

        if mode != "errors" and warnings:
            lines.append("")
            # In structured mode, show accepted status
            if mode == "structured":
                lines.append(f"warnings[{len(warnings)}]{{file,line,message,accepted}}:")
                for w in warnings[:10]:  # Limit to 10 warnings
                    file = w.get('file') or '-'
                    line = w.get('line') or '-'
                    msg = (w.get('message') or '')[:80]
                    accepted = "[accepted]" if w.get('accepted') else ""
                    lines.append(f"{file}    {line}    {msg}    {accepted}")
            else:
                lines.append(f"warnings[{len(warnings)}]{{file,line,message}}:")
                for w in warnings[:10]:  # Limit to 10 warnings
                    file = w.get('file') or '-'
                    line = w.get('line') or '-'
                    msg = (w.get('message') or '')[:80]
                    lines.append(f"{file}    {line}    {msg}")

    if test_summary and test_summary.get('tests_run', 0) > 0:
        lines.append("")
        lines.append("tests:")
        passed = test_summary['tests_run'] - test_summary['failures'] - test_summary['errors']
        lines.append(f"  passed: {passed}")
        lines.append(f"  failed: {test_summary['failures'] + test_summary['errors']}")
        lines.append(f"  skipped: {test_summary['skipped']}")

    return "\n".join(lines)


def cmd_run(args):
    """Handle run subcommand - execute + auto-parse on failure.

    Delegates to execute_direct() for all Maven execution.
    """
    project_dir = getattr(args, 'project_dir', '.')

    # Build command key for timeout learning
    targets_key = args.targets.replace(' ', '_').replace('-', '_')
    command_key = f"maven:{targets_key}"

    # Get timeout (convert ms to seconds if needed)
    if hasattr(args, 'timeout') and args.timeout:
        timeout_seconds = args.timeout // 1000 if args.timeout > 1000 else args.timeout
    else:
        timeout_seconds = DEFAULT_TIMEOUT_SECONDS

    # Execute via direct_command foundation layer
    result = execute_direct(
        args=args.targets,
        command_key=command_key,
        default_timeout=timeout_seconds,
        project_dir=project_dir,
        profile=args.profile,
        module=args.module,
        wrapper=getattr(args, 'mvnw', None)
    )

    log_file = result['log_file']
    command_str = result['command']
    print(f"[EXEC] {command_str}", file=sys.stderr)

    # Handle execution errors (wrapper not found, log file creation failed)
    if result['status'] == 'error' and result['exit_code'] == -1:
        error_type = 'execution_failed'
        if 'log file' in result.get('error', '').lower():
            error_type = 'log_file_creation_failed'
        print(format_toon_error(error_type, result.get('error', 'Execution failed'), log_file, -1, 0, command_str))
        return 1

    # Handle timeout
    if result['status'] == 'timeout':
        print(format_toon_error(
            "timeout",
            result.get('error', f"Build timed out after {result['timeout_used_seconds']}s"),
            log_file,
            -1,
            result['duration_seconds'],
            command_str
        ))
        return 1

    # Success case
    if result['status'] == 'success':
        print(format_toon_success(log_file, 0, result['duration_seconds'], command_str))
        return 0

    # Build failed - parse the log file for errors
    try:
        content = Path(log_file).read_text(encoding='utf-8', errors='replace')
        issues = extract_issues(content, include_warnings=(args.mode != "errors"))
        test_summary = extract_test_summary(content)

        # Load acceptable warnings and filter based on mode
        acceptable = load_acceptable_warnings(project_dir)
        warnings = [i for i in issues if i.get('severity') == 'WARNING']
        errors = [i for i in issues if i.get('severity') == 'ERROR']

        # Apply warning filtering
        filtered_warnings = filter_warnings(warnings, acceptable, args.mode)

        # Reconstruct issues with filtered warnings
        filtered_issues = errors + filtered_warnings

        print(format_toon_error(
            "build_failed",
            f"Build failed with exit code {result['exit_code']}",
            log_file,
            result['exit_code'],
            result['duration_seconds'],
            command_str,
            filtered_issues,
            test_summary,
            args.mode
        ))
    except Exception:
        # If parsing fails, still return the build failure
        print(format_toon_error(
            "build_failed",
            f"Build failed with exit code {result['exit_code']}",
            log_file,
            result['exit_code'],
            result['duration_seconds'],
            command_str
        ))

    return 1
