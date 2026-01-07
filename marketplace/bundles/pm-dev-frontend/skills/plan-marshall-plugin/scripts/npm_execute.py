#!/usr/bin/env python3
"""npm command execution foundation layer.

Provides the base execution layer that all higher-level npm commands use internally.
Handles adaptive timeout learning and structured output.

Usage:
    # As API (direct import)
    from npm_execute import execute_direct

    result = execute_direct(
        args="run test",
        command_key="npm:test",
        default_timeout=300
    )

    # As CLI
    python3 npm_execute.py execute --args "run test" --command-key "npm:test" --default-timeout 300
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Import from plan-marshall skills
SCRIPT_DIR = Path(__file__).parent
BUNDLES_DIR = SCRIPT_DIR.parent.parent.parent.parent  # marketplace/bundles
RUN_CONFIG_DIR = BUNDLES_DIR / 'plan-marshall' / 'skills' / 'run-config' / 'scripts'
EXTENSION_API_DIR = BUNDLES_DIR / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'
sys.path.insert(0, str(RUN_CONFIG_DIR))
sys.path.insert(0, str(EXTENSION_API_DIR))

from run_config import timeout_get, timeout_set
from build_result import DirectCommandResult, create_log_file


# =============================================================================
# Constants
# =============================================================================

# npm executable (no wrapper needed unlike Maven)
NPM_COMMAND = 'npm'

# Commands that should use npx instead of npm
NPX_COMMANDS = ['playwright', 'eslint', 'prettier', 'stylelint', 'tsc', 'jest', 'vitest']

# Bash tool outer timeout buffer (seconds) - ensures outer > inner
OUTER_TIMEOUT_BUFFER = 30


# =============================================================================
# API Functions (no argparse dependency)
# =============================================================================

def detect_command_type(args: str) -> str:
    """Detect whether to use npm or npx based on the command.

    Args:
        args: Command arguments.

    Returns:
        'npm' or 'npx'.
    """
    args_lower = args.lower().strip()
    for npx_cmd in NPX_COMMANDS:
        if args_lower.startswith(npx_cmd):
            return 'npx'
    return 'npm'


def execute_direct(
    args: str,
    command_key: str,
    default_timeout: int = 300,
    project_dir: str = '.',
    working_dir: str = None,
    env_vars: str = None
) -> DirectCommandResult:
    """Execute npm command with adaptive timeout learning.

    This is the foundation layer for all npm command execution.
    Uses run-config for timeout retrieval and learning.
    Conforms to R1 requirement: all output goes to log file, not memory.

    Args:
        args: Complete npm arguments with all routing embedded
              (e.g., "run test", "run test --workspace=pkg", "--prefix ./pkg run test")
        command_key: Command identifier for timeout learning (e.g., "npm:test")
        default_timeout: Default timeout in seconds if no learned value exists
        project_dir: Project root directory
        working_dir: Working directory for command execution (overrides project_dir for cwd)
        env_vars: Environment variables string (e.g., "NODE_ENV=test CI=true")

    Returns:
        DirectCommandResult with:
        - status: "success" | "error" | "timeout"
        - exit_code: int
        - duration_seconds: int
        - log_file: str (path to captured output)
        - command: str
        - timeout_used_seconds: int (optional)
        - command_type: str ("npm" or "npx")
        - error: str (on error/timeout only)
    """
    import os
    import re

    # Step 1: Detect command type (npm or npx)
    command_type = detect_command_type(args)

    # Step 2: Get timeout from run-config (with safety margin)
    timeout_seconds = timeout_get(command_key, default_timeout, project_dir)

    # Step 3: Build command (args is complete and self-contained)
    cmd_parts = [command_type] + args.split()
    command_str = ' '.join(cmd_parts)

    # Step 4: Determine scope for log file (extract from embedded routing)
    scope = "default"
    workspace_match = re.search(r'--workspace[=\s]+(\S+)', args)
    if workspace_match:
        scope = workspace_match.group(1)
    else:
        prefix_match = re.search(r'--prefix\s+(\S+)', args)
        if prefix_match:
            scope = prefix_match.group(1)

    # Step 5: Create log file for output (R1 requirement)
    log_file = create_log_file("npm", scope, project_dir)
    if not log_file:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "log_file": "",
            "command": command_str,
            "command_type": command_type,
            "error": "Failed to create log file"
        }

    # Step 6: Prepare environment
    env = os.environ.copy()
    if env_vars:
        for env_pair in env_vars.split():
            if '=' in env_pair:
                key, value = env_pair.split('=', 1)
                env[key] = value

    # Step 7: Determine working directory
    cwd = working_dir if working_dir else project_dir

    # Step 8: Execute with output to log file
    start_time = time.time()

    try:
        with open(log_file, 'w') as log:
            result = subprocess.run(
                cmd_parts,
                timeout=timeout_seconds,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=env
            )
        duration_seconds = int(time.time() - start_time)

        # Step 6: Record duration for adaptive learning (only on completion)
        timeout_set(command_key, duration_seconds, project_dir)

        # Step 7: Return structured result
        if result.returncode == 0:
            return {
                "status": "success",
                "exit_code": 0,
                "duration_seconds": duration_seconds,
                "log_file": log_file,
                "command": command_str,
                "timeout_used_seconds": timeout_seconds,
                "command_type": command_type
            }
        else:
            return {
                "status": "error",
                "exit_code": result.returncode,
                "duration_seconds": duration_seconds,
                "log_file": log_file,
                "command": command_str,
                "timeout_used_seconds": timeout_seconds,
                "command_type": command_type,
                "error": f"Build failed with exit code {result.returncode}"
            }

    except subprocess.TimeoutExpired:
        duration_seconds = int(time.time() - start_time)
        return {
            "status": "timeout",
            "exit_code": -1,
            "duration_seconds": duration_seconds,
            "log_file": log_file,
            "command": command_str,
            "timeout_used_seconds": timeout_seconds,
            "command_type": command_type,
            "error": f"Command timed out after {timeout_seconds} seconds"
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "log_file": log_file,
            "command": command_str,
            "timeout_used_seconds": timeout_seconds,
            "command_type": command_type,
            "error": f"Command not found: {command_type}"
        }

    except OSError as e:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "log_file": log_file,
            "command": command_str,
            "timeout_used_seconds": timeout_seconds,
            "command_type": command_type,
            "error": str(e)
        }


def get_bash_timeout(inner_timeout_seconds: int) -> int:
    """Calculate Bash tool timeout with buffer.

    The Bash tool has a default 120-second timeout. For long-running builds,
    we need to set the outer timeout higher than the inner (shell) timeout.

    Args:
        inner_timeout_seconds: The shell timeout in seconds.

    Returns:
        Bash tool timeout in seconds (inner + buffer).
    """
    return inner_timeout_seconds + OUTER_TIMEOUT_BUFFER


# =============================================================================
# CLI Output Helpers
# =============================================================================

def output_toon(result: dict) -> None:
    """Output result in TOON format."""
    print(f"status\t{result['status']}")
    print(f"exit_code\t{result['exit_code']}")
    print(f"duration_seconds\t{result['duration_seconds']}")
    print(f"log_file\t{result['log_file']}")
    print(f"command\t{result['command']}")
    if 'timeout_used_seconds' in result:
        print(f"timeout_used_seconds\t{result['timeout_used_seconds']}")
    print(f"command_type\t{result['command_type']}")

    if 'error' in result:
        print(f"error\t{result['error']}")


# =============================================================================
# CLI Wrappers
# =============================================================================

def cmd_execute(args) -> int:
    """CLI wrapper for execute_direct."""
    result = execute_direct(
        args=args.args,
        command_key=args.command_key,
        default_timeout=args.default_timeout,
        project_dir=args.project_dir,
        working_dir=getattr(args, 'working_dir', None),
        env_vars=getattr(args, 'env', None)
    )

    output_toon(result)

    # Return 0 for success, 1 for error/timeout
    return 0 if result['status'] == 'success' else 1


def cmd_detect_command_type(args) -> int:
    """CLI wrapper for detect_command_type."""
    command_type = detect_command_type(args.args)
    print(f"command_type\t{command_type}")
    return 0


def cmd_get_bash_timeout(args) -> int:
    """CLI wrapper for get_bash_timeout."""
    timeout_seconds = get_bash_timeout(args.inner_timeout)
    print(timeout_seconds)
    return 0


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Direct command execution foundation layer for npm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute npm command with adaptive timeout
  %(prog)s execute --args "run test" --command-key "npm:test" --default-timeout 300

  # Detect command type (npm vs npx)
  %(prog)s detect-command-type --args "playwright test"

  # Get Bash tool timeout (seconds) for inner timeout
  %(prog)s get-bash-timeout --inner-timeout 300
"""
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # execute subcommand
    p_execute = subparsers.add_parser('execute', help='Execute npm command')
    p_execute.add_argument(
        '--args',
        required=True,
        help='Complete npm arguments with routing (e.g., "run test" or "run test --workspace=pkg")'
    )
    p_execute.add_argument(
        '--command-key',
        required=True,
        help='Command identifier for timeout learning (e.g., "npm:test")'
    )
    p_execute.add_argument(
        '--default-timeout',
        type=int,
        default=300,
        help='Default timeout in seconds (default: 300)'
    )
    p_execute.add_argument(
        '--project-dir',
        default='.',
        help='Project directory (default: current)'
    )
    p_execute.add_argument(
        '--working-dir',
        dest='working_dir',
        help='Working directory for command execution'
    )
    p_execute.add_argument(
        '--env',
        help='Environment variables (e.g., "NODE_ENV=test CI=true")'
    )
    p_execute.set_defaults(func=cmd_execute)

    # detect-command-type subcommand
    p_detect = subparsers.add_parser('detect-command-type', help='Detect npm vs npx')
    p_detect.add_argument(
        '--args',
        required=True,
        help='Command arguments to analyze'
    )
    p_detect.set_defaults(func=cmd_detect_command_type)

    # get-bash-timeout subcommand
    p_bash = subparsers.add_parser('get-bash-timeout', help='Get Bash tool timeout (seconds)')
    p_bash.add_argument(
        '--inner-timeout',
        type=int,
        required=True,
        help='Inner shell timeout in seconds'
    )
    p_bash.set_defaults(func=cmd_get_bash_timeout)

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
