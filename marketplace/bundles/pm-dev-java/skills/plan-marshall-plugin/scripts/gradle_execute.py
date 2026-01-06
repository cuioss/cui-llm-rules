#!/usr/bin/env python3
"""Gradle command execution foundation layer.

Provides the base execution layer that all higher-level Gradle commands use internally.
Handles wrapper detection, log file output capture, adaptive timeout learning,
and structured output.

Usage:
    # As API (direct import)
    from gradle_execute import execute_direct, detect_wrapper

    result = execute_direct(
        args="build",
        command_key="gradle:build",
        default_timeout=300
    )

    # As CLI
    python3 gradle_execute.py execute --args "build" --command-key "gradle:build" --default-timeout 300
"""

import argparse
import subprocess
import shutil
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
from build_result import create_log_file, DirectCommandResult


# =============================================================================
# Constants
# =============================================================================

# Wrapper detection order
GRADLE_WRAPPERS = ['./gradlew', 'gradlew.bat']

# Default timeout in seconds for Gradle builds
DEFAULT_TIMEOUT_SECONDS = 300

# Bash tool outer timeout buffer (seconds) - ensures outer > inner
OUTER_TIMEOUT_BUFFER = 30


# =============================================================================
# API Functions (no argparse dependency)
# =============================================================================

def detect_wrapper(project_dir: str = '.') -> str:
    """Detect Gradle wrapper or fallback to gradle.

    Args:
        project_dir: Project root directory.

    Returns:
        Path to wrapper script or 'gradle' if no wrapper found.
    """
    root = Path(project_dir).resolve()

    for wrapper in GRADLE_WRAPPERS:
        wrapper_path = root / wrapper
        if wrapper_path.exists() and wrapper_path.is_file():
            return str(wrapper_path)

    # Fallback to gradle on PATH
    if shutil.which('gradle'):
        return 'gradle'

    return 'gradle'  # Return gradle even if not found, let execution fail with clear error


def execute_direct(
    args: str,
    command_key: str,
    default_timeout: int = 300,
    project_dir: str = '.',
    module: str = None,
    wrapper: str = None
) -> DirectCommandResult:
    """Execute Gradle command with log file output and adaptive timeout learning.

    This is the foundation layer for all Gradle command execution.
    Captures output to log file and uses run-config for timeout learning.

    Note: The timeout system enforces a minimum of 120 seconds (via run-config)
    to prevent unreasonably short timeouts from warm daemon runs affecting cold starts.

    Args:
        args: Gradle tasks/arguments (e.g., "build", "test", ":module:properties")
        command_key: Command identifier for timeout learning (e.g., "gradle:build")
        default_timeout: Default timeout in seconds if no learned value exists
        project_dir: Project root directory
        module: Module path for task prefix (optional, e.g., "api-genshin-impact")
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
            "stdout": str (captured output),
            "stderr": str (captured errors),
            "error": str (on error only)
        }
    """
    # Step 1: Create log file in standard location
    scope = module if module else "default"
    log_file = create_log_file("gradle", scope, project_dir)
    if not log_file:
        return {
            "status": "error",
            "exit_code": -1,
            "duration_seconds": 0,
            "timeout_used_seconds": 0,
            "log_file": "",
            "command": "",
            "wrapper": "",
            "stdout": "",
            "stderr": "",
            "error": "Failed to create log file"
        }

    # Step 2: Detect wrapper (or use explicit one)
    if not wrapper:
        wrapper = detect_wrapper(project_dir)

    # Step 3: Get timeout from run-config (enforces minimum of 120 seconds)
    timeout_seconds = timeout_get(command_key, default_timeout, project_dir)

    # Step 4: Build command
    cmd_parts = [wrapper]

    # Add module prefix if specified (for multi-module projects)
    if module:
        # Convert module path to Gradle task prefix
        module_prefix = f":{module.replace('/', ':')}"
        # Prepend module prefix to each task in args
        tasks = args.split()
        prefixed_tasks = []
        for task in tasks:
            if task.startswith('-'):
                # Keep flags as-is
                prefixed_tasks.append(task)
            elif task.startswith(':'):
                # Already has prefix
                prefixed_tasks.append(task)
            else:
                # Add module prefix
                prefixed_tasks.append(f"{module_prefix}:{task}")
        cmd_parts.extend(prefixed_tasks)
    else:
        cmd_parts.extend(args.split())

    # Add console and quiet flags for cleaner output
    cmd_parts.extend(['--console=plain'])

    command_str = ' '.join(cmd_parts)

    # Step 5: Execute and capture output
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

        # Write output to log file
        with open(log_file, 'w') as f:
            f.write(f"Command: {command_str}\n")
            f.write(f"Exit code: {result.returncode}\n")
            f.write(f"Duration: {duration_seconds}s\n")
            f.write("\n=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n=== STDERR ===\n")
            f.write(result.stderr)

        # Step 6: Record duration for adaptive learning
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
                "wrapper": wrapper,
                "stdout": result.stdout,
                "stderr": result.stderr
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
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": f"Build failed with exit code {result.returncode}"
            }

    except subprocess.TimeoutExpired as e:
        duration_seconds = int(time.time() - start_time)

        # Write timeout info to log file
        with open(log_file, 'w') as f:
            f.write(f"Command: {command_str}\n")
            f.write(f"Status: TIMEOUT after {timeout_seconds}s\n")
            if e.stdout:
                f.write("\n=== STDOUT (partial) ===\n")
                f.write(e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout)
            if e.stderr:
                f.write("\n=== STDERR (partial) ===\n")
                f.write(e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr)

        return {
            "status": "timeout",
            "exit_code": -1,
            "duration_seconds": duration_seconds,
            "timeout_used_seconds": timeout_seconds,
            "log_file": log_file,
            "command": command_str,
            "wrapper": wrapper,
            "stdout": "",
            "stderr": "",
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
            "stdout": "",
            "stderr": "",
            "error": f"Gradle wrapper not found: {wrapper}"
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
            "stdout": "",
            "stderr": "",
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
    """CLI wrapper for get_bash_timeout."""
    timeout_seconds = get_bash_timeout(args.inner_timeout)
    print(timeout_seconds)
    return 0


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Direct command execution foundation layer for Gradle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute Gradle command with adaptive timeout
  %(prog)s execute --args "build" --command-key "gradle:build" --default-timeout 300

  # Execute for specific module
  %(prog)s execute --args "test" --command-key "gradle:test" --module api-genshin-impact

  # Detect Gradle wrapper
  %(prog)s detect-wrapper

  # Get Bash tool timeout (seconds) for inner timeout
  %(prog)s get-bash-timeout --inner-timeout 300
"""
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # execute subcommand
    p_execute = subparsers.add_parser('execute', help='Execute Gradle command')
    p_execute.add_argument(
        '--args',
        required=True,
        help='Gradle tasks (e.g., "build", "test")'
    )
    p_execute.add_argument(
        '--command-key',
        required=True,
        help='Command identifier for timeout learning (e.g., "gradle:build")'
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
        '--module',
        help='Module path for task prefix (optional)'
    )
    p_execute.set_defaults(func=cmd_execute)

    # detect-wrapper subcommand
    p_detect = subparsers.add_parser('detect-wrapper', help='Detect Gradle wrapper')
    p_detect.add_argument(
        '--project-dir',
        default='.',
        help='Project directory (default: current)'
    )
    p_detect.set_defaults(func=cmd_detect_wrapper)

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
