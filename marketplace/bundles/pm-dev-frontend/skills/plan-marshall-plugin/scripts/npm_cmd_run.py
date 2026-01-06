#!/usr/bin/env python3
"""Run subcommand for npm/npx - combines execute + parse on failure.

Uses shared build_parse, build_format, build_result for unified output.
Delegates to npm_execute.py for all execution (like Maven pattern).
Delegates to tool-specific parsers (TypeScript, Jest, TAP, ESLint, npm errors).
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Add extension-api scripts to path for imports
SCRIPT_DIR = Path(__file__).parent
BUNDLES_DIR = SCRIPT_DIR.parent.parent.parent.parent
EXTENSION_API_DIR = BUNDLES_DIR / "plan-marshall" / "skills" / "extension-api" / "scripts"
sys.path.insert(0, str(EXTENSION_API_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

# Import npm_execute foundation layer
from npm_execute import execute_direct

# Import shared build infrastructure
from build_result import (
    success_result,
    error_result,
    timeout_result,
    ERROR_BUILD_FAILED,
    ERROR_LOG_FILE_FAILED,
    ERROR_EXECUTION_FAILED,
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
# Command Handler
# =============================================================================

def cmd_run(args):
    """Handle run subcommand - execute + auto-parse on failure.

    Delegates to execute_direct() for all npm execution.
    """
    project_dir = getattr(args, 'project_dir', '.')
    output_format = getattr(args, 'format', 'toon')
    mode = getattr(args, 'mode', 'actionable')

    # Select formatter based on output format
    formatter = format_json if output_format == 'json' else format_toon

    # Build command key for timeout learning
    targets_key = args.targets.replace(' ', '_').replace('-', '_')
    command_key = f"npm:{targets_key}"

    # Execute via execute_direct foundation layer
    result = execute_direct(
        args=args.targets,
        command_key=command_key,
        default_timeout=args.timeout,
        project_dir=project_dir,
        workspace=args.workspace,
        working_dir=args.working_dir,
        env_vars=args.env
    )

    log_file = result['log_file']
    command_str = result['command']
    print(f"[EXEC] {command_str}", file=sys.stderr)

    # Handle execution errors (npm not found, log file creation failed)
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
        issues, test_summary, build_status = parse_with_detector(log_file, command_str)

        # Partition issues into errors and warnings
        errors, warnings = partition_issues(issues)

        # Load acceptable warnings and filter based on mode
        patterns = load_acceptable_warnings(project_dir, "npm")
        filtered_warnings = filter_warnings(warnings, patterns, mode)

        # Build result dict
        output = error_result(
            error=ERROR_BUILD_FAILED,
            exit_code=result['exit_code'],
            duration_seconds=result['duration_seconds'],
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
            exit_code=result['exit_code'],
            duration_seconds=result['duration_seconds'],
            log_file=log_file,
            command=command_str,
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
    run_parser.add_argument("--timeout", type=int, default=120, help="Build timeout in seconds (default: 120 = 2 min)")
    run_parser.add_argument("--mode", choices=["actionable", "structured", "errors"], default="actionable", help="Output mode")
    run_parser.add_argument("--format", choices=["toon", "json"], default="toon", help="Output format")
    run_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project root directory")
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
