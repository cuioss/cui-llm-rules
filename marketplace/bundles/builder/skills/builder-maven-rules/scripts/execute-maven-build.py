#!/usr/bin/env python3
"""
Execute Maven build with automatic log file handling.

Handles timestamp generation, log file pre-creation, and Maven execution
in a single atomic operation. Prints executed commands for visibility.

Usage:
    python3 execute-maven-build.py --goals <goals> [options]
    python3 execute-maven-build.py --help

Options:
    --goals      Maven goals to execute (required)
    --profile    Maven profile to activate (-P flag)
    --module     Specific module to build (-pl flag)
    --timeout    Build timeout in milliseconds (default: 120000)
    --mvnw       Path to Maven wrapper (default: ./mvnw)

Output:
    Prints [EXEC] line showing executed command, then JSON result:
    {
        "status": "success|error",
        "data": {
            "log_file": "target/build-output-2025-11-25-143022.log",
            "exit_code": 0,
            "duration_ms": 45000,
            "command_executed": "./mvnw -l ... clean install"
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
        description="Execute Maven build with automatic log file handling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic build
    python3 execute-maven-build.py --goals "clean install"

    # With profile and module
    python3 execute-maven-build.py --goals "clean install" --profile pre-commit --module auth-service

    # With custom timeout
    python3 execute-maven-build.py --goals "clean verify" --timeout 300000

    # Using mock for testing
    python3 execute-maven-build.py --goals "clean install" --mvnw test/builder-maven/mocks/mvnw-success.sh
        """,
    )
    parser.add_argument(
        "--goals",
        type=str,
        required=True,
        help="Maven goals to execute (e.g., 'clean install', 'clean verify')"
    )
    parser.add_argument(
        "--profile",
        type=str,
        help="Maven profile to activate (-P flag)"
    )
    parser.add_argument(
        "--module",
        type=str,
        help="Specific module to build (-pl flag)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120000,
        help="Build timeout in milliseconds (default: 120000)"
    )
    parser.add_argument(
        "--mvnw",
        type=str,
        default="./mvnw",
        help="Path to Maven wrapper executable (default: ./mvnw)"
    )
    return parser.parse_args()


def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"target/build-output-{timestamp}.log"


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
    except OSError as e:
        return False


def build_maven_command(args, log_file: str) -> list:
    """Build Maven command list from arguments."""
    cmd = [args.mvnw, "-l", log_file]

    if args.profile:
        cmd.append(f"-P{args.profile}")

    # Add goals (split by space)
    cmd.extend(args.goals.split())

    if args.module:
        cmd.extend(["-pl", args.module])

    return cmd


def execute_maven(cmd: list, timeout_ms: int) -> dict:
    """
    Execute Maven command and return result.

    Returns dict with exit_code, duration_ms, timed_out.
    """
    timeout_seconds = timeout_ms / 1000.0
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            timeout=timeout_seconds,
            capture_output=False,  # Let output go to log file
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
            "error": f"Maven wrapper not found: {cmd[0]}"
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

    # Generate log filename
    log_file = generate_log_filename()

    # Pre-create log file (CRITICAL for clean goal)
    if not pre_create_log_file(log_file):
        result = {
            "status": "error",
            "error": "log_file_creation_failed",
            "message": f"Failed to create log file: {log_file}"
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Build command
    cmd = build_maven_command(args, log_file)
    command_str = " ".join(cmd)

    # Print executed command for visibility
    print(f"[EXEC] {command_str}", file=sys.stderr)

    # Execute Maven
    exec_result = execute_maven(cmd, args.timeout)

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

    # Success result
    result = {
        "status": "success" if exec_result["exit_code"] == 0 else "error",
        "data": {
            "log_file": log_file,
            "exit_code": exec_result["exit_code"],
            "duration_ms": exec_result["duration_ms"],
            "command_executed": command_str
        }
    }

    if exec_result["exit_code"] != 0:
        result["error"] = "build_failed"
        result["message"] = f"Maven build failed with exit code {exec_result['exit_code']}"

    print(json.dumps(result, indent=2))
    sys.exit(0 if exec_result["exit_code"] == 0 else 1)


if __name__ == "__main__":
    main()
