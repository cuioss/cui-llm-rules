#!/usr/bin/env python3
"""
Execute npm/npx build with automatic log file handling.

Handles timestamp generation, log file pre-creation, command construction,
and npm/npx execution in a single atomic operation. Automatically determines
whether to use npm or npx based on the command.

Usage:
    python3 execute-npm-build.py --command <command> [options]
    python3 execute-npm-build.py --help

Options:
    --command    npm/npx command to execute (required, e.g., "run test", "playwright test")
    --workspace  Workspace name for monorepo projects (--workspace flag)
    --working-dir Working directory for command execution
    --env        Environment variables (e.g., "NODE_ENV=test CI=true")
    --timeout    Build timeout in milliseconds (default: 120000)

Output:
    Prints [EXEC] line showing executed command, then JSON result:
    {
        "status": "success|error",
        "data": {
            "log_file": "target/npm-output-2025-11-26-143022.log",
            "exit_code": 0,
            "duration_ms": 45000,
            "command_executed": "npm run test",
            "command_type": "npm"
        }
    }
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute npm/npx build with automatic log file handling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic test run
    python3 execute-npm-build.py --command "run test"

    # Playwright tests
    python3 execute-npm-build.py --command "playwright test"

    # Workspace-specific build
    python3 execute-npm-build.py --command "run build" --workspace e-2-e-playwright

    # With environment variables
    python3 execute-npm-build.py --command "run test" --env "CI=true NODE_ENV=test"

    # With custom timeout (3 minutes)
    python3 execute-npm-build.py --command "run test:e2e" --timeout 180000
        """,
    )
    parser.add_argument(
        "--command",
        type=str,
        required=True,
        help="npm/npx command to execute (e.g., 'run test', 'playwright test')"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        help="Workspace name for monorepo projects"
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        help="Working directory for command execution"
    )
    parser.add_argument(
        "--env",
        type=str,
        help="Environment variables (e.g., 'NODE_ENV=test CI=true')"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120000,
        help="Build timeout in milliseconds (default: 120000)"
    )
    return parser.parse_args()


def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"target/npm-output-{timestamp}.log"


def pre_create_log_file(log_file: str) -> bool:
    """
    Pre-create log file and parent directories.

    Returns True if successful, False otherwise.
    """
    try:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)
        return True
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": f"Failed to create log file: {str(e)}"
        }), file=sys.stderr)
        return False


def determine_command_type(command: str) -> str:
    """
    Determine whether to use npm or npx based on the command.

    Returns "npm" or "npx".
    """
    # Commands that should use npx
    npx_commands = [
        'playwright',
        'eslint',
        'prettier',
        'stylelint',
        'tsc',
        'jest',
        'vitest'
    ]

    # Check if command starts with any npx command
    command_lower = command.lower().strip()
    for npx_cmd in npx_commands:
        if command_lower.startswith(npx_cmd):
            return "npx"

    # Default to npm
    return "npm"


def construct_command(
    command: str,
    workspace: str | None,
    working_dir: str | None,
    env: str | None
) -> tuple[str, list[str]]:
    """
    Construct the full command with all parameters.

    Returns (command_type, command_parts) where command_parts is a list
    of command components.
    """
    command_type = determine_command_type(command)

    # Start with npm or npx
    command_parts = [command_type]

    # Add the command itself
    command_parts.extend(command.strip().split())

    # Add workspace flag if provided (only for npm)
    if workspace and command_type == "npm":
        command_parts.append(f"--workspace={workspace}")

    return command_type, command_parts


def execute_build(
    command_parts: list[str],
    log_file: str,
    timeout: int,
    working_dir: str | None,
    env_str: str | None
) -> tuple[int, float]:
    """
    Execute the npm/npx command and capture output to log file.

    Returns (exit_code, duration_ms).
    """
    # Prepare environment
    env = os.environ.copy()
    if env_str:
        # Parse environment variables from string like "NODE_ENV=test CI=true"
        for env_pair in env_str.split():
            if '=' in env_pair:
                key, value = env_pair.split('=', 1)
                env[key] = value

    # Determine working directory
    cwd = working_dir if working_dir else os.getcwd()

    # Execute command
    start_time = time.time()
    try:
        with open(log_file, 'w') as log:
            result = subprocess.run(
                command_parts,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=env,
                timeout=timeout / 1000.0  # Convert ms to seconds
            )
            exit_code = result.returncode
    except subprocess.TimeoutExpired:
        exit_code = 124  # Standard timeout exit code
    except Exception as e:
        # Log error to file
        with open(log_file, 'a') as log:
            log.write(f"\nCommand execution failed: {str(e)}\n")
        exit_code = 1

    end_time = time.time()
    duration_ms = int((end_time - start_time) * 1000)

    return exit_code, duration_ms


def main():
    """Main execution function."""
    args = parse_args()

    # Generate log filename
    log_file = generate_log_filename()

    # Pre-create log file
    if not pre_create_log_file(log_file):
        sys.exit(1)

    # Construct command
    command_type, command_parts = construct_command(
        args.command,
        args.workspace,
        args.working_dir,
        args.env
    )

    # Build display command for [EXEC] output
    display_cmd = " ".join(command_parts)
    if args.env:
        display_cmd = f"{args.env} {display_cmd}"
    if args.working_dir:
        display_cmd = f"cd {args.working_dir} && {display_cmd}"

    # Print executed command to stderr for visibility
    print(f"[EXEC] {display_cmd}", file=sys.stderr)

    # Execute build
    exit_code, duration_ms = execute_build(
        command_parts,
        log_file,
        args.timeout,
        args.working_dir,
        args.env
    )

    # Return structured JSON result
    result = {
        "status": "success",
        "data": {
            "log_file": log_file,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "command_executed": display_cmd,
            "command_type": command_type
        }
    }

    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
