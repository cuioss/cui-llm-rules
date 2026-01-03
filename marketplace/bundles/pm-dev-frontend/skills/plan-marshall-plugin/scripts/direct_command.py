#!/usr/bin/env python3
"""Direct command execution foundation layer for npm.

Provides the base execution layer that all higher-level npm commands use internally.
Handles adaptive timeout learning and structured output.

Usage:
    # As API (direct import)
    from direct_command import execute_direct

    result = execute_direct(
        args="run test",
        command_key="npm:test",
        default_timeout=300
    )

    # As CLI
    python3 direct_command.py execute --args "run test" --command-key "npm:test" --default-timeout 300
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Import timeout API from run_config
SCRIPT_DIR = Path(__file__).parent
BUNDLES_DIR = SCRIPT_DIR.parent.parent.parent.parent  # marketplace/bundles
RUN_CONFIG_DIR = BUNDLES_DIR / 'plan-marshall' / 'skills' / 'run-config' / 'scripts'
sys.path.insert(0, str(RUN_CONFIG_DIR))

from run_config import timeout_get, timeout_set


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
    workspace: str = None
) -> dict:
    """Execute npm command with adaptive timeout learning.

    This is the foundation layer for all npm command execution.
    Uses run-config for timeout retrieval and learning.

    Args:
        args: npm arguments (e.g., "run test", "install")
        command_key: Command identifier for timeout learning (e.g., "npm:test")
        default_timeout: Default timeout in seconds if no learned value exists
        project_dir: Project root directory
        workspace: Optional workspace name for monorepo projects

    Returns:
        Dict with execution result:
        {
            "status": "success" | "error" | "timeout",
            "exit_code": int,
            "duration_seconds": int,
            "timeout_used_seconds": int,
            "command": str,
            "command_type": str,  # "npm" or "npx"
            "stdout": str (on error/timeout only),
            "stderr": str (on error/timeout only),
            "error": str (on error only)
        }
    """
    # Step 1: Detect command type (npm or npx)
    command_type = detect_command_type(args)

    # Step 2: Get timeout from run-config (with safety margin)
    timeout_seconds = timeout_get(command_key, default_timeout, project_dir)

    # Step 3: Build command
    cmd_parts = [command_type] + args.split()
    if workspace and command_type == 'npm':
        cmd_parts.append(f'--workspace={workspace}')
    command_str = ' '.join(cmd_parts)

    # Step 4: Execute with shell timeout
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd_parts,
            timeout=timeout_seconds,
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        duration_seconds = int(time.time() - start_time)

        # Step 5: Record duration for adaptive learning (only on completion)
        timeout_set(command_key, duration_seconds, project_dir)

        # Step 6: Return structured result
        if result.returncode == 0:
            return {
                "status": "success",
                "exit_code": 0,
                "duration_seconds": duration_seconds,
                "timeout_used_seconds": timeout_seconds,
                "command": command_str,
                "command_type": command_type
            }
        else:
            return {
                "status": "error",
                "exit_code": result.returncode,
                "duration_seconds": duration_seconds,
                "timeout_used_seconds": timeout_seconds,
                "command": command_str,
                "command_type": command_type,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

    except subprocess.TimeoutExpired as e:
        duration_seconds = int(time.time() - start_time)
        return {
            "status": "timeout",
            "exit_code": -1,
            "duration_seconds": duration_seconds,
            "timeout_used_seconds": timeout_seconds,
            "command": command_str,
            "command_type": command_type,
            "stdout": e.stdout.decode() if e.stdout else "",
            "stderr": e.stderr.decode() if e.stderr else "",
            "error": f"Command timed out after {timeout_seconds} seconds"
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "timeout_used_seconds": timeout_seconds,
            "command": command_str,
            "command_type": command_type,
            "error": f"Command not found: {command_type}"
        }

    except OSError as e:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "timeout_used_seconds": timeout_seconds,
            "command": command_str,
            "command_type": command_type,
            "error": str(e)
        }


def get_bash_timeout_ms(inner_timeout_seconds: int) -> int:
    """Calculate Bash tool timeout parameter (milliseconds).

    The Bash tool has a default 120-second timeout. For long-running builds,
    we need to set the outer timeout higher than the inner (shell) timeout.

    Args:
        inner_timeout_seconds: The shell timeout in seconds.

    Returns:
        Bash tool timeout in milliseconds.
    """
    return (inner_timeout_seconds + OUTER_TIMEOUT_BUFFER) * 1000


# =============================================================================
# CLI Output Helpers
# =============================================================================

def output_toon(result: dict) -> None:
    """Output result in TOON format."""
    print(f"status\t{result['status']}")
    print(f"exit_code\t{result['exit_code']}")
    print(f"duration_seconds\t{result['duration_seconds']}")
    print(f"timeout_used_seconds\t{result['timeout_used_seconds']}")
    print(f"command\t{result['command']}")
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
        workspace=getattr(args, 'workspace', None)
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
    """CLI wrapper for get_bash_timeout_ms."""
    timeout_ms = get_bash_timeout_ms(args.inner_timeout)
    print(timeout_ms)
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

  # Get Bash tool timeout (ms) for inner timeout
  %(prog)s get-bash-timeout --inner-timeout 300
"""
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # execute subcommand
    p_execute = subparsers.add_parser('execute', help='Execute npm command')
    p_execute.add_argument(
        '--args',
        required=True,
        help='npm arguments (e.g., "run test")'
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
        '--workspace',
        help='Workspace name for monorepo projects'
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
    p_bash = subparsers.add_parser('get-bash-timeout', help='Get Bash tool timeout (ms)')
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
