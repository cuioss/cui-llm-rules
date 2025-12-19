#!/usr/bin/env python3
"""Execute subcommand for Gradle build operations."""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"build/build-output-{timestamp}.log"


def pre_create_log_file(log_file: str) -> bool:
    """Pre-create log file and parent directory."""
    try:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return True
    except OSError:
        return False


def build_gradle_command(tasks: str, project: str, skip_tests: bool, fail_at_end: bool, gradlew: str) -> list:
    """Build Gradle command list from arguments."""
    cmd = [gradlew]
    cmd.extend(tasks.split())
    if project:
        if project.startswith(":"):
            cmd.append(project)
        else:
            cmd.extend(["-p", project])
    if skip_tests:
        cmd.extend(["-x", "test"])
    if fail_at_end:
        cmd.append("--continue")
    cmd.append("--console=plain")
    return cmd


def execute_gradle(cmd: list, timeout_ms: int, log_file: str) -> dict:
    """Execute Gradle command and return result."""
    timeout_seconds = timeout_ms / 1000.0
    start_time = time.time()

    try:
        with open(log_file, "w", encoding="utf-8") as log_fh:
            result = subprocess.run(cmd, timeout=timeout_seconds, stdout=log_fh, stderr=subprocess.STDOUT, check=False)
        duration_ms = int((time.time() - start_time) * 1000)
        return {"exit_code": result.returncode, "duration_ms": duration_ms, "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "duration_ms": int((time.time() - start_time) * 1000), "timed_out": True}
    except FileNotFoundError:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": f"Gradle wrapper not found: {cmd[0]}"}
    except OSError as e:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": str(e)}


def cmd_execute(args):
    """Handle execute subcommand."""
    if not Path(args.gradlew).exists():
        print(json.dumps({"status": "error", "error": "gradlew_not_found", "message": f"Gradle wrapper not found at {args.gradlew}. Run 'gradle wrapper' to generate it."}, indent=2))
        return 1

    log_file = generate_log_filename()
    if not pre_create_log_file(log_file):
        print(json.dumps({"status": "error", "error": "log_file_creation_failed", "message": f"Failed to create log file: {log_file}"}, indent=2))
        return 1

    cmd = build_gradle_command(args.tasks, args.project, args.skip_tests, args.fail_at_end, args.gradlew)
    command_str = " ".join(cmd)
    print(f"[EXEC] {command_str}", file=sys.stderr)

    exec_result = execute_gradle(cmd, args.timeout, log_file)

    if "error" in exec_result:
        print(json.dumps({"status": "error", "error": "execution_failed", "message": exec_result["error"], "data": {"log_file": log_file, "command_executed": command_str}}, indent=2))
        return 1

    if exec_result["timed_out"]:
        print(json.dumps({"status": "error", "error": "timeout", "message": f"Build timed out after {args.timeout}ms", "data": {"log_file": log_file, "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}, indent=2))
        return 1

    result = {"status": "success", "data": {"log_file": log_file, "exit_code": exec_result["exit_code"], "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}
    print(json.dumps(result, indent=2))
    return 0
