#!/usr/bin/env python3
"""
Execute Gradle build with automatic log file handling.

Handles timestamp generation, log file creation, and Gradle execution
in a single atomic operation. Prints executed commands for visibility.

Usage:
    python3 execute-gradle-build.py --tasks <tasks> [options]
    python3 execute-gradle-build.py --help

Options:
    --tasks      Gradle tasks to execute (required)
    --project    Specific subproject (-p flag or :project:path)
    --skip-tests Skip tests (-x test)
    --fail-at-end Continue on failure (--continue)
    --timeout    Build timeout in milliseconds (default: 120000)
    --gradlew    Path to Gradle wrapper (default: ./gradlew)

Output:
    Prints [EXEC] line showing executed command, then JSON result:
    {
        "status": "success|error",
        "data": {
            "log_file": "build/build-output-2025-11-25-143022.log",
            "exit_code": 0,
            "duration_ms": 45000,
            "command_executed": "./gradlew clean build"
        }
    }
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute Gradle build with automatic log file handling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic build
    python3 execute-gradle-build.py --tasks "clean build"

    # With project and skip tests
    python3 execute-gradle-build.py --tasks "build" --project ":core" --skip-tests

    # With custom timeout
    python3 execute-gradle-build.py --tasks "clean test" --timeout 300000
        """,
    )
    parser.add_argument(
        "--tasks",
        type=str,
        required=True,
        help="Gradle tasks to execute (e.g., 'clean build', 'test')"
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Specific subproject (-p flag or :project:path notation)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip tests (-x test)"
    )
    parser.add_argument(
        "--fail-at-end",
        action="store_true",
        help="Continue on failure (--continue)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120000,
        help="Build timeout in milliseconds (default: 120000)"
    )
    parser.add_argument(
        "--gradlew",
        type=str,
        default="./gradlew",
        help="Path to Gradle wrapper executable (default: ./gradlew)"
    )
    return parser.parse_args()


def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"build/build-output-{timestamp}.log"


def pre_create_log_file(log_file: str) -> bool:
    """
    Pre-create log file and parent directory.

    Returns True on success, False on failure.
    """
    try:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return True
    except OSError:
        return False


def build_gradle_command(args) -> list:
    """Build Gradle command list from arguments."""
    cmd = [args.gradlew]

    # Add tasks (split by space)
    cmd.extend(args.tasks.split())

    # Add project flag if specified
    if args.project:
        if args.project.startswith(":"):
            # Project path notation - add as argument
            cmd.append(args.project)
        else:
            # Directory path
            cmd.extend(["-p", args.project])

    # Add skip tests flag
    if args.skip_tests:
        cmd.extend(["-x", "test"])

    # Add fail at end flag
    if args.fail_at_end:
        cmd.append("--continue")

    # Use plain console for parseable output
    cmd.append("--console=plain")

    return cmd


def execute_gradle(cmd: list, timeout_ms: int, log_file: str) -> dict:
    """
    Execute Gradle command and return result.

    Returns dict with exit_code, duration_ms, timed_out.
    """
    timeout_seconds = timeout_ms / 1000.0
    start_time = time.time()

    try:
        # Open log file for writing
        with open(log_file, "w", encoding="utf-8") as log_fh:
            result = subprocess.run(
                cmd,
                timeout=timeout_seconds,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                check=False
            )
        duration_ms = int((time.time() - start_time) * 1000)

        return {
            "exit_code": result.returncode,
            "duration_ms": duration_ms,
            "timed_out": False
        }
    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "exit_code": -1,
            "duration_ms": duration_ms,
            "timed_out": True
        }
    except FileNotFoundError:
        return {
            "exit_code": -1,
            "duration_ms": 0,
            "timed_out": False,
            "error": f"Gradle wrapper not found: {cmd[0]}"
        }
    except OSError as e:
        return {
            "exit_code": -1,
            "duration_ms": 0,
            "timed_out": False,
            "error": str(e)
        }


def main():
    """Main entry point."""
    args = parse_args()

    # Check if gradlew exists
    if not Path(args.gradlew).exists():
        result = {
            "status": "error",
            "error": "gradlew_not_found",
            "message": f"Gradle wrapper not found at {args.gradlew}. "
                       "Run 'gradle wrapper' to generate it."
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Generate log filename
    log_file = generate_log_filename()

    # Pre-create log file
    if not pre_create_log_file(log_file):
        result = {
            "status": "error",
            "error": "log_file_creation_failed",
            "message": f"Failed to create log file: {log_file}"
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Build command
    cmd = build_gradle_command(args)
    command_str = " ".join(cmd)

    # Print executed command for visibility
    print(f"[EXEC] {command_str}", file=sys.stderr)

    # Execute Gradle
    exec_result = execute_gradle(cmd, args.timeout, log_file)

    # Handle errors
    if "error" in exec_result:
        result = {
            "status": "error",
            "error": "execution_failed",
            "message": exec_result["error"],
            "data": {
                "log_file": log_file,
                "command_executed": command_str
            }
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    if exec_result["timed_out"]:
        result = {
            "status": "error",
            "error": "timeout",
            "message": f"Build timed out after {args.timeout}ms",
            "data": {
                "log_file": log_file,
                "duration_ms": exec_result["duration_ms"],
                "command_executed": command_str
            }
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Success result (even if build failed, execution succeeded)
    result = {
        "status": "success",
        "data": {
            "log_file": log_file,
            "exit_code": exec_result["exit_code"],
            "duration_ms": exec_result["duration_ms"],
            "command_executed": command_str
        }
    }

    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
