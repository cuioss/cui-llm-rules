#!/usr/bin/env python3
"""Direct command execution foundation layer for Maven.

Provides the base execution layer that all higher-level Maven commands use internally.
Handles wrapper detection, log file output capture, adaptive timeout learning,
and structured output.

Usage:
    # As API (direct import)
    from direct_command import execute_direct

    result = execute_direct(
        args="clean verify",
        command_key="maven:verify",
        default_timeout=300
    )

    # As CLI
    python3 direct_command.py execute --args "clean verify" --command-key "maven:verify" --default-timeout 300
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
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

# Wrapper detection order
MAVEN_WRAPPERS = ['./mvnw', 'mvn']

# Default timeout in seconds for Maven builds
DEFAULT_TIMEOUT_SECONDS = 300

# Bash tool outer timeout buffer (seconds) - ensures outer > inner
OUTER_TIMEOUT_BUFFER = 30


# =============================================================================
# API Functions (no argparse dependency)
# =============================================================================

def detect_wrapper(project_dir: str = '.') -> str:
    """Detect Maven wrapper or fallback to mvn.

    Args:
        project_dir: Project root directory.

    Returns:
        Path to wrapper script or 'mvn' if no wrapper found.
    """
    root = Path(project_dir).resolve()

    for wrapper in MAVEN_WRAPPERS:
        wrapper_path = root / wrapper
        if wrapper_path.exists() and wrapper_path.is_file():
            return str(wrapper_path)

    # Fallback to mvn on PATH
    return 'mvn'


def generate_log_filename() -> str:
    """Generate timestamped log filename.

    Returns:
        Log file path like 'target/build-output-2025-01-15-143022.log'
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"target/build-output-{timestamp}.log"


def pre_create_log_file(log_file: str, project_dir: str = '.') -> bool:
    """Pre-create log file and parent directory.

    CRITICAL: When using Maven's -l flag with 'clean', the clean phase
    deletes target/ before Maven can create the log file. Pre-creating
    ensures the log file exists.

    Args:
        log_file: Relative path to log file
        project_dir: Project root directory

    Returns:
        True if log file was created successfully
    """
    try:
        path = Path(project_dir) / log_file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return True
    except OSError:
        return False


def execute_direct(
    args: str,
    command_key: str,
    default_timeout: int = 300,
    project_dir: str = '.',
    profile: str = None,
    module: str = None,
    wrapper: str = None
) -> dict:
    """Execute Maven command with log file output and adaptive timeout learning.

    This is the foundation layer for all Maven command execution.
    Uses Maven's -l flag for output capture and run-config for timeout learning.

    Args:
        args: Maven goals (e.g., "clean verify", "test")
        command_key: Command identifier for timeout learning (e.g., "maven:verify")
        default_timeout: Default timeout in seconds if no learned value exists
        project_dir: Project root directory
        profile: Maven profile to activate (optional)
        module: Module path for -pl (optional)
        wrapper: Explicit wrapper path (optional, auto-detected if not provided)

    Returns:
        Dict with execution result:
        {
            "status": "success" | "error" | "timeout",
            "exit_code": int,
            "duration_seconds": int,
            "timeout_used_seconds": int,
            "log_file": str,
            "command": str,
            "wrapper": str,
            "error": str (on error only)
        }
    """
    # Step 1: Generate and pre-create log file
    log_file = generate_log_filename()
    if not pre_create_log_file(log_file, project_dir):
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "timeout_used_seconds": 0,
            "log_file": log_file,
            "command": "",
            "wrapper": "",
            "error": f"Failed to create log file: {log_file}"
        }

    # Step 2: Detect wrapper (or use explicit one)
    if not wrapper:
        wrapper = detect_wrapper(project_dir)

    # Step 3: Get timeout from run-config (with safety margin)
    timeout_seconds = timeout_get(command_key, default_timeout, project_dir)

    # Step 4: Build command with -l flag for log file output
    cmd_parts = [wrapper, "-l", log_file]
    if profile:
        cmd_parts.append(f"-P{profile}")
    cmd_parts.extend(args.split())
    if module:
        cmd_parts.extend(["-pl", module])
    command_str = ' '.join(cmd_parts)

    # Step 5: Execute (output goes to log file, not captured)
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd_parts,
            timeout=timeout_seconds,
            capture_output=False,  # Output goes to log file via -l
            check=False,
            cwd=project_dir
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
                "timeout_used_seconds": timeout_seconds,
                "log_file": log_file,
                "command": command_str,
                "wrapper": wrapper
            }
        else:
            return {
                "status": "error",
                "exit_code": result.returncode,
                "duration_seconds": duration_seconds,
                "timeout_used_seconds": timeout_seconds,
                "log_file": log_file,
                "command": command_str,
                "wrapper": wrapper,
                "error": f"Build failed with exit code {result.returncode}"
            }

    except subprocess.TimeoutExpired:
        duration_seconds = int(time.time() - start_time)
        return {
            "status": "timeout",
            "exit_code": -1,
            "duration_seconds": duration_seconds,
            "timeout_used_seconds": timeout_seconds,
            "log_file": log_file,
            "command": command_str,
            "wrapper": wrapper,
            "error": f"Command timed out after {timeout_seconds} seconds"
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "timeout_used_seconds": timeout_seconds,
            "log_file": log_file,
            "command": command_str,
            "wrapper": wrapper,
            "error": f"Maven wrapper not found: {wrapper}"
        }

    except OSError as e:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "timeout_used_seconds": timeout_seconds,
            "log_file": log_file,
            "command": command_str,
            "wrapper": wrapper,
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
    print(f"log_file\t{result.get('log_file', '')}")
    print(f"exit_code\t{result['exit_code']}")
    print(f"duration_seconds\t{result['duration_seconds']}")
    print(f"timeout_used_seconds\t{result['timeout_used_seconds']}")
    print(f"command\t{result['command']}")
    print(f"wrapper\t{result['wrapper']}")

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
        profile=getattr(args, 'profile', None),
        module=getattr(args, 'module', None)
    )

    output_toon(result)

    # Return 0 for success, 1 for error/timeout
    return 0 if result['status'] == 'success' else 1


def cmd_detect_wrapper(args) -> int:
    """CLI wrapper for detect_wrapper."""
    wrapper = detect_wrapper(args.project_dir)
    print(f"wrapper\t{wrapper}")
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
        description='Direct command execution foundation layer for Maven',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute Maven command with adaptive timeout
  %(prog)s execute --args "clean verify" --command-key "maven:verify" --default-timeout 300

  # Detect Maven wrapper
  %(prog)s detect-wrapper

  # Get Bash tool timeout (ms) for inner timeout
  %(prog)s get-bash-timeout --inner-timeout 300
"""
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # execute subcommand
    p_execute = subparsers.add_parser('execute', help='Execute Maven command')
    p_execute.add_argument(
        '--args',
        required=True,
        help='Maven goals (e.g., "clean verify")'
    )
    p_execute.add_argument(
        '--command-key',
        required=True,
        help='Command identifier for timeout learning (e.g., "maven:verify")'
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
        '--profile',
        help='Maven profile to activate (optional)'
    )
    p_execute.add_argument(
        '--module',
        help='Module path for -pl (optional)'
    )
    p_execute.set_defaults(func=cmd_execute)

    # detect-wrapper subcommand
    p_detect = subparsers.add_parser('detect-wrapper', help='Detect Maven wrapper')
    p_detect.add_argument(
        '--project-dir',
        default='.',
        help='Project directory (default: current)'
    )
    p_detect.set_defaults(func=cmd_detect_wrapper)

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
