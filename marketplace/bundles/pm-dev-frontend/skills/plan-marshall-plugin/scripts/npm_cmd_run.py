#!/usr/bin/env python3
"""Run subcommand for npm/npx - combines execute + parse on failure.

Uses shared build_parse, build_format, build_result for unified output.
Delegates to tool-specific parsers (TypeScript, Jest, TAP, ESLint, npm errors).
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# Add extension-api scripts to path for imports
SCRIPT_DIR = Path(__file__).parent
BUNDLES_DIR = SCRIPT_DIR.parent.parent.parent.parent
EXTENSION_API_DIR = BUNDLES_DIR / "plan-marshall" / "skills" / "extension-api" / "scripts"
sys.path.insert(0, str(EXTENSION_API_DIR))

# Import shared build infrastructure
from build_result import (
    create_log_file,
    success_result,
    error_result,
    timeout_result,
    ERROR_BUILD_FAILED,
    ERROR_LOG_FILE_FAILED,
)
from build_format import format_toon, format_json
from build_parse import (
    Issue,
    TestSummary,
    filter_warnings,
    load_acceptable_warnings,
    partition_issues,
    SEVERITY_ERROR,
    SEVERITY_WARNING,
)

# Import npm parsers (BuildParser protocol implementations)
from npm_parse_typescript import parse_log as parse_typescript
from npm_parse_jest import parse_log as parse_jest
from npm_parse_tap import parse_log as parse_tap
from npm_parse_eslint import parse_log as parse_eslint
from npm_parse_errors import parse_log as parse_npm_errors


# =============================================================================
# Tool Detection
# =============================================================================

def detect_tool_type(content: str, command: str) -> str:
    """Detect which tool produced the output.

    Args:
        content: Log file content.
        command: Original command string.

    Returns:
        Tool type: "typescript", "jest", "tap", "eslint", "npm_error", or "generic"
    """
    command_lower = command.lower()

    # Check command first
    if "tsc" in command_lower or "typescript" in command_lower:
        return "typescript"
    if "jest" in command_lower:
        return "jest"
    if "eslint" in command_lower:
        return "eslint"

    # Check content patterns
    if "npm ERR!" in content:
        return "npm_error"
    if "TAP version" in content or "# tests" in content:
        return "tap"
    if "error TS" in content or "): error TS" in content or ": error TS" in content:
        return "typescript"
    if "FAIL " in content and ("Tests:" in content or "Test Suites:" in content):
        return "jest"
    if "problem" in content.lower() and "error" in content.lower():
        # Check for ESLint-style output
        if any(line.strip().endswith(")") for line in content.split("\n") if "error" in line.lower()):
            return "eslint"

    return "generic"


def parse_with_detector(log_file: str, command: str) -> Tuple[List[Issue], Optional[TestSummary], str]:
    """Parse log file using appropriate tool-specific parser.

    Args:
        log_file: Path to the log file.
        command: Original command string.

    Returns:
        Tuple of (issues, test_summary, build_status)
    """
    content = Path(log_file).read_text(encoding="utf-8", errors="replace")
    tool_type = detect_tool_type(content, command)

    try:
        if tool_type == "typescript":
            return parse_typescript(log_file)
        elif tool_type == "jest":
            return parse_jest(log_file)
        elif tool_type == "tap":
            return parse_tap(log_file)
        elif tool_type == "eslint":
            return parse_eslint(log_file)
        elif tool_type == "npm_error":
            return parse_npm_errors(log_file)
        else:
            # Generic fallback - try each parser and use first with results
            parsers = [parse_npm_errors, parse_typescript, parse_eslint, parse_jest, parse_tap]
            for parser in parsers:
                try:
                    issues, test_summary, build_status = parser(log_file)
                    if issues:
                        return issues, test_summary, build_status
                except Exception:
                    continue
            return [], None, "FAILURE"
    except Exception:
        return [], None, "FAILURE"


# =============================================================================
# Command Building and Execution
# =============================================================================

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


# =============================================================================
# Command Handler
# =============================================================================

def cmd_run(args):
    """Handle run subcommand - execute + auto-parse on failure."""
    project_dir = getattr(args, 'project_dir', '.')
    output_format = getattr(args, 'format', 'toon')
    mode = getattr(args, 'mode', 'actionable')

    # Select formatter based on output format
    formatter = format_json if output_format == 'json' else format_toon

    # Determine scope from workspace parameter
    scope = args.workspace if args.workspace else "default"

    # Create log file using base library
    log_file = create_log_file("npm", scope, project_dir)
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

    command_type, command_parts = construct_command(args.targets, args.workspace)
    display_cmd = " ".join(command_parts)
    if args.env:
        display_cmd = f"{args.env} {display_cmd}"
    if args.working_dir:
        display_cmd = f"cd {args.working_dir} && {display_cmd}"

    print(f"[EXEC] {display_cmd}", file=sys.stderr)

    exit_code, duration_ms = execute_build(command_parts, log_file, args.timeout, args.working_dir, args.env)
    duration_seconds = duration_ms // 1000

    # Handle timeout
    if exit_code == 124:
        timeout_seconds = args.timeout // 1000
        output = timeout_result(
            timeout_used_seconds=timeout_seconds,
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=display_cmd,
        )
        print(formatter(output))
        return 1

    # Success case
    if exit_code == 0:
        output = success_result(
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=display_cmd,
        )
        print(formatter(output))
        return 0

    # Build failed - parse the log file for errors
    try:
        issues, test_summary, build_status = parse_with_detector(log_file, display_cmd)

        # Partition issues into errors and warnings
        errors, warnings = partition_issues(issues)

        # Load acceptable warnings and filter based on mode
        patterns = load_acceptable_warnings(project_dir, "npm")
        filtered_warnings = filter_warnings(warnings, patterns, mode)

        # Build result dict
        output = error_result(
            error=ERROR_BUILD_FAILED,
            exit_code=exit_code,
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=display_cmd,
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
            exit_code=exit_code,
            duration_seconds=duration_seconds,
            log_file=log_file,
            command=display_cmd,
        )
        print(formatter(output))

    return 1


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="npm/npx build operations", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run subcommand (primary API)
    run_parser = subparsers.add_parser("run", help="Execute build and auto-parse on failure (primary API)")
    run_parser.add_argument("--targets", required=True, help="Build targets to execute")
    run_parser.add_argument("--workspace", help="Workspace name for monorepo projects")
    run_parser.add_argument("--working-dir", dest="working_dir", help="Working directory for command execution")
    run_parser.add_argument("--env", help="Environment variables (e.g., 'NODE_ENV=test CI=true')")
    run_parser.add_argument("--timeout", type=int, default=120000, help="Build timeout in milliseconds (default: 120000 = 2 min)")
    run_parser.add_argument("--mode", choices=["actionable", "structured", "errors"], default="actionable", help="Output mode")
    run_parser.add_argument("--format", choices=["toon", "json"], default="toon", help="Output format")
    run_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project root directory")
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
