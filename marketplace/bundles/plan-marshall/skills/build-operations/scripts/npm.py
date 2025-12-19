#!/usr/bin/env python3
"""
npm/npx build operations - execute and parse.

Usage:
    npm.py execute --command <command> [options]
    npm.py parse --log <path> [--mode <mode>]
    npm.py --help

Subcommands:
    execute     Execute npm/npx build with automatic log file handling
    parse       Parse npm/npx build output and categorize issues
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple, List


# ============================================================================
# EXECUTE SUBCOMMAND
# ============================================================================

def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"target/npm-output-{timestamp}.log"


def pre_create_log_file(log_file: str) -> bool:
    """Pre-create log file and parent directories."""
    try:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)
        return True
    except Exception:
        return False


def determine_command_type(command: str) -> str:
    """Determine whether to use npm or npx based on the command."""
    npx_commands = ['playwright', 'eslint', 'prettier', 'stylelint', 'tsc', 'jest', 'vitest']
    command_lower = command.lower().strip()
    for npx_cmd in npx_commands:
        if command_lower.startswith(npx_cmd):
            return "npx"
    return "npm"


def construct_command(command: str, workspace: Optional[str]) -> Tuple[str, List[str]]:
    """Construct the full command with all parameters."""
    command_type = determine_command_type(command)
    command_parts = [command_type]
    command_parts.extend(command.strip().split())
    if workspace and command_type == "npm":
        command_parts.append(f"--workspace={workspace}")
    return command_type, command_parts


def execute_build(command_parts: List[str], log_file: str, timeout: int, working_dir: Optional[str], env_str: Optional[str]) -> Tuple[int, float]:
    """Execute the npm/npx command and capture output to log file."""
    env = os.environ.copy()
    if env_str:
        for env_pair in env_str.split():
            if '=' in env_pair:
                key, value = env_pair.split('=', 1)
                env[key] = value

    cwd = working_dir if working_dir else os.getcwd()
    start_time = time.time()

    try:
        with open(log_file, 'w') as log:
            result = subprocess.run(command_parts, stdout=log, stderr=subprocess.STDOUT, cwd=cwd, env=env, timeout=timeout / 1000.0)
            exit_code = result.returncode
    except subprocess.TimeoutExpired:
        exit_code = 124
    except Exception as e:
        with open(log_file, 'a') as log:
            log.write(f"\nCommand execution failed: {str(e)}\n")
        exit_code = 1

    duration_ms = int((time.time() - start_time) * 1000)
    return exit_code, duration_ms


def cmd_execute(args):
    """Handle execute subcommand."""
    log_file = generate_log_filename()
    if not pre_create_log_file(log_file):
        print(json.dumps({"status": "error", "error": "log_file_creation_failed", "message": f"Failed to create log file: {log_file}"}, indent=2))
        return 1

    command_type, command_parts = construct_command(args.command, args.workspace)

    display_cmd = " ".join(command_parts)
    if args.env:
        display_cmd = f"{args.env} {display_cmd}"
    if args.working_dir:
        display_cmd = f"cd {args.working_dir} && {display_cmd}"

    print(f"[EXEC] {display_cmd}", file=sys.stderr)

    exit_code, duration_ms = execute_build(command_parts, log_file, args.timeout, args.working_dir, args.env)

    result = {"status": "success", "data": {"log_file": log_file, "exit_code": exit_code, "duration_ms": duration_ms, "command_executed": display_cmd, "command_type": command_type}}
    print(json.dumps(result, indent=2))
    return 0


# ============================================================================
# PARSE SUBCOMMAND
# ============================================================================

ERROR_PATTERNS = {
    'compilation_error': [
        re.compile(r'SyntaxError:\s*(.+)', re.IGNORECASE),
        re.compile(r'TypeError:\s*(.+)', re.IGNORECASE),
        re.compile(r'ReferenceError:\s*(.+)', re.IGNORECASE),
        re.compile(r'error TS\d+:\s*(.+)', re.IGNORECASE),
    ],
    'test_failure': [
        re.compile(r'✘|✖'),
        re.compile(r'FAIL\s+(.+)', re.IGNORECASE),
        re.compile(r'Expected.*to.*but.*received', re.IGNORECASE),
        re.compile(r'(\d+)\s+(?:test|tests)\s+failed', re.IGNORECASE),
        re.compile(r'Test\s+Suites?:\s+\d+\s+failed', re.IGNORECASE),
    ],
    'lint_error': [
        re.compile(r'eslint', re.IGNORECASE),
        re.compile(r'stylelint', re.IGNORECASE),
        re.compile(r'prettier', re.IGNORECASE),
        re.compile(r'(\d+):(\d+)\s+(error|warning)\s+(.+?)\s+(\S+)$'),
    ],
    'dependency_error': [
        re.compile(r'Cannot find module\s+[\'"]([^\'"]+)[\'"]', re.IGNORECASE),
        re.compile(r'Module not found:\s*(.+)', re.IGNORECASE),
        re.compile(r'npm ERR! 404\s*(.+)', re.IGNORECASE),
        re.compile(r'ERESOLVE\s+(.+)', re.IGNORECASE),
    ],
    'playwright_error': [
        re.compile(r'playwright', re.IGNORECASE),
        re.compile(r'browser.*error', re.IGNORECASE),
        re.compile(r'page\.goto:\s*Timeout', re.IGNORECASE),
        re.compile(r'locator\.\w+:\s*Timeout', re.IGNORECASE),
    ],
}

GENERAL_ERROR_PATTERN = re.compile(r'(?:Error|ERROR|error)[:\s]+(.+)', re.IGNORECASE)
GENERAL_WARNING_PATTERN = re.compile(r'(?:Warning|WARN|warning)[:\s]+(.+)', re.IGNORECASE)
NPM_ERROR_PATTERN = re.compile(r'npm ERR!\s*(.+)')

FILE_LOCATION_PATTERNS = [
    re.compile(r'([^\s:]+\.[jt]sx?):(\d+):(\d+)'),
    re.compile(r'@\s+([^\s]+\.[jt]sx?)\s+(\d+):(\d+)'),
    re.compile(r'\(([^\s:]+\.[jt]sx?):(\d+):(\d+)\)'),
    re.compile(r'(tests?/[^\s:]+\.[jt]sx?):(\d+):(\d+)'),
]


def extract_file_location(line: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """Extract file path, line, and column from an error line."""
    for pattern in FILE_LOCATION_PATTERNS:
        match = pattern.search(line)
        if match:
            groups = match.groups()
            return groups[0], int(groups[1]) if len(groups) > 1 else None, int(groups[2]) if len(groups) > 2 else None
    return None, None, None


def categorize_line(line: str) -> Tuple[Optional[str], Optional[str]]:
    """Categorize a line and return (category, severity)."""
    for category, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(line):
                if category == 'lint_error' and 'warning' in line.lower():
                    return category, 'WARNING'
                return category, 'ERROR'

    if NPM_ERROR_PATTERN.search(line):
        return 'npm_error', 'ERROR'
    if GENERAL_ERROR_PATTERN.search(line):
        return 'other', 'ERROR'
    if GENERAL_WARNING_PATTERN.search(line):
        return 'other', 'WARNING'
    return None, None


def determine_build_status(lines: List[str]) -> str:
    """Determine overall build status from output."""
    for line in lines:
        if 'npm ERR!' in line or '✘' in line or '✖' in line:
            return 'FAILURE'
        if re.search(r'Test Suites?:\s+\d+\s+failed', line, re.IGNORECASE):
            return 'FAILURE'
        if re.search(r'FAIL\s+', line):
            return 'FAILURE'
    return 'SUCCESS'


def cmd_parse(args):
    """Handle parse subcommand."""
    if not os.path.exists(args.log):
        print(json.dumps({'status': 'error', 'error': 'LOG_NOT_FOUND', 'message': f'Log file not found: {args.log}'}, indent=2))
        return 1

    try:
        with open(args.log, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': 'READ_ERROR', 'message': f'Failed to read log file: {e}'}, indent=2))
        return 1

    lines = content.split('\n')
    build_status = determine_build_status(lines)

    issues, errors_only, warnings = [], [], []

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        category, severity = categorize_line(line)
        if category:
            file_path, file_line, column = extract_file_location(line)
            issue = {'type': category, 'file': file_path, 'line': file_line, 'column': column, 'message': line, 'severity': severity, 'log_line': line_num}
            issues.append(issue)
            if severity == 'ERROR':
                errors_only.append(f'{line_num}: {line}')
            else:
                warnings.append(f'{line_num}: {line}')

    summary = {
        'compilation_errors': sum(1 for i in issues if i['type'] == 'compilation_error'),
        'test_failures': sum(1 for i in issues if i['type'] == 'test_failure'),
        'lint_errors': sum(1 for i in issues if i['type'] == 'lint_error' and i['severity'] == 'ERROR'),
        'lint_warnings': sum(1 for i in issues if i['type'] == 'lint_error' and i['severity'] == 'WARNING'),
        'dependency_errors': sum(1 for i in issues if i['type'] == 'dependency_error'),
        'playwright_errors': sum(1 for i in issues if i['type'] == 'playwright_error'),
        'total_errors': sum(1 for i in issues if i['severity'] == 'ERROR'),
        'total_warnings': sum(1 for i in issues if i['severity'] == 'WARNING'),
        'total_issues': len(issues)
    }

    if args.mode == 'structured':
        result = {'status': build_status.lower(), 'data': {'output_file': args.log, 'issues': issues}, 'metrics': summary}
    elif args.mode == 'errors':
        result = {'status': build_status.lower(), 'data': {'output_file': args.log, 'errors': errors_only}, 'metrics': {'total_errors': summary['total_errors']}}
    else:
        result = {'status': build_status.lower(), 'data': {'output_file': args.log, 'errors': errors_only, 'warnings': warnings}, 'metrics': {'total_errors': summary['total_errors'], 'total_warnings': summary['total_warnings']}}

    print(json.dumps(result, indent=2))
    return 0 if build_status == 'SUCCESS' else 2


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="npm/npx build operations", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # execute subcommand
    exec_parser = subparsers.add_parser("execute", help="Execute npm/npx build with automatic log file handling")
    exec_parser.add_argument("--command", required=True, help="npm/npx command to execute")
    exec_parser.add_argument("--workspace", help="Workspace name for monorepo projects")
    exec_parser.add_argument("--working-dir", dest="working_dir", help="Working directory for command execution")
    exec_parser.add_argument("--env", help="Environment variables (e.g., 'NODE_ENV=test CI=true')")
    exec_parser.add_argument("--timeout", type=int, default=120000, help="Build timeout in milliseconds (default: 120000 = 2 min)")
    exec_parser.set_defaults(func=cmd_execute)

    # parse subcommand
    parse_parser = subparsers.add_parser("parse", help="Parse npm/npx build output and categorize issues")
    parse_parser.add_argument("--log", required=True, help="Path to npm output log file")
    parse_parser.add_argument("--mode", choices=["default", "errors", "structured"], default="default", help="Output mode")
    parse_parser.set_defaults(func=cmd_parse)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
