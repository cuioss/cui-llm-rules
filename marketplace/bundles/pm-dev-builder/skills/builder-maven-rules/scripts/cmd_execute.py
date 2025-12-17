#!/usr/bin/env python3
"""Execute subcommand for Maven build operations."""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"target/build-output-{timestamp}.log"


def pre_create_log_file(log_file: str) -> bool:
    """Pre-create log file and parent directory."""
    try:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return True
    except OSError:
        return False


def build_maven_command(goals: str, profile: str, module: str, mvnw: str, log_file: str) -> list:
    """Build Maven command list from arguments."""
    cmd = [mvnw, "-l", log_file]
    if profile:
        cmd.append(f"-P{profile}")
    cmd.extend(goals.split())
    if module:
        cmd.extend(["-pl", module])
    return cmd


def execute_maven(cmd: list, timeout_ms: int) -> dict:
    """Execute Maven command and return result."""
    timeout_seconds = timeout_ms / 1000.0
    start_time = time.time()

    try:
        result = subprocess.run(cmd, timeout=timeout_seconds, capture_output=False, check=False)
        duration_ms = int((time.time() - start_time) * 1000)
        return {"exit_code": result.returncode, "duration_ms": duration_ms, "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "duration_ms": int((time.time() - start_time) * 1000), "timed_out": True}
    except FileNotFoundError:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": f"Maven wrapper not found: {cmd[0]}"}
    except OSError as e:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": str(e)}


def cmd_execute(args):
    """Handle execute subcommand."""
    log_file = generate_log_filename()
    if not pre_create_log_file(log_file):
        print(json.dumps({"status": "error", "error": "log_file_creation_failed", "message": f"Failed to create log file: {log_file}"}, indent=2))
        return 1

    cmd = build_maven_command(args.goals, args.profile, args.module, args.mvnw, log_file)
    command_str = " ".join(cmd)
    print(f"[EXEC] {command_str}", file=sys.stderr)

    exec_result = execute_maven(cmd, args.timeout)

    if "error" in exec_result:
        print(json.dumps({"status": "error", "error": "execution_failed", "message": exec_result["error"], "data": {"log_file": log_file, "command_executed": command_str}}, indent=2))
        return 1

    if exec_result["timed_out"]:
        print(json.dumps({"status": "error", "error": "timeout", "message": f"Build timed out after {args.timeout}ms", "data": {"log_file": log_file, "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}, indent=2))
        return 1

    result = {"status": "success" if exec_result["exit_code"] == 0 else "error", "data": {"log_file": log_file, "exit_code": exec_result["exit_code"], "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}
    if exec_result["exit_code"] != 0:
        result["error"] = "build_failed"
        result["message"] = f"Maven build failed with exit code {exec_result['exit_code']}"
    print(json.dumps(result, indent=2))
    return 0 if exec_result["exit_code"] == 0 else 1
