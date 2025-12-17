#!/usr/bin/env python3
"""
Synchronous polling utility for blocking until an async operation completes.

Inspired by the Awaitility JUnit library. Provides a blocking mechanism that
polls a condition until satisfied, timed out, or permanently failed.

Output: TOON format with status, duration, polls, and final result.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

# Constants
DEFAULT_TIMEOUT_MS = 300_000  # 5 minutes
DEFAULT_INTERVAL_MS = 30_000  # 30 seconds
MINIMUM_TIMEOUT_MS = 60_000  # 1 minute
MAXIMUM_TIMEOUT_MS = 600_000  # 10 minutes
BUFFER_FACTOR = 1.5
RUN_CONFIG_PATH = ".plan/run-configuration.json"


def parse_toon_output(output: str) -> dict:
    """Parse TOON format output into a dictionary.

    Handles key: value pairs and basic nested dotted keys.
    """
    result = {}
    for line in output.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Handle tab-separated (key\tvalue)
        if '\t' in line:
            parts = line.split('\t', 1)
            if len(parts) == 2:
                key, value = parts
                result[key.strip()] = value.strip()
        # Handle colon-separated (key: value)
        elif ':' in line and not line.endswith(':'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                key, value = parts
                key = key.strip()
                value = value.strip()
                if value:
                    result[key] = value

    return result


def check_condition(parsed: dict, success_field: str, failure_field: Optional[str]) -> str:
    """Check if condition is satisfied, failed, or pending.

    Args:
        parsed: Parsed TOON output dictionary
        success_field: Field=value pattern for success (e.g., "status=success")
        failure_field: Optional field=value pattern for failure

    Returns:
        "success", "failure", or "pending"
    """
    def matches_pattern(pattern: str) -> bool:
        if '=' in pattern:
            field, expected = pattern.split('=', 1)
            actual = parsed.get(field, '')
            return str(actual).lower() == expected.lower()
        else:
            # Just check if field exists and is truthy
            return bool(parsed.get(pattern))

    # Check for failure first (permanent)
    if failure_field and matches_pattern(failure_field):
        return "failure"

    # Check for success
    if matches_pattern(success_field):
        return "success"

    return "pending"


def run_check_command(check_cmd: str) -> Tuple[int, str, str]:
    """Execute the check command and return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            check_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60  # Individual check timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Check command timed out after 60s"
    except Exception as e:
        return 1, "", str(e)


def read_run_config() -> dict:
    """Read run configuration file."""
    config_path = Path(RUN_CONFIG_PATH)
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": 1, "commands": {}}


def write_run_config(config: dict) -> None:
    """Write run configuration file."""
    config_path = Path(RUN_CONFIG_PATH)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write('\n')


def get_adaptive_timeout(command_key: str) -> Optional[int]:
    """Get adaptive timeout from run-config history.

    Returns timeout in milliseconds or None if no history.
    """
    config = read_run_config()
    commands = config.get("commands", {})

    # Normalize key for JSON path (replace : with .)
    cmd_entry = commands.get(command_key, {})
    last_exec = cmd_entry.get("last_execution", {})

    if not last_exec:
        return None

    duration_ms = last_exec.get("duration_ms")
    if duration_ms is None:
        return None

    # Calculate adaptive timeout with buffer
    adaptive = int(duration_ms * BUFFER_FACTOR)

    # Clamp to bounds
    return max(MINIMUM_TIMEOUT_MS, min(adaptive, MAXIMUM_TIMEOUT_MS))


def update_execution_history(command_key: str, duration_ms: int, status: str) -> None:
    """Update run-config with execution result."""
    config = read_run_config()

    if "commands" not in config:
        config["commands"] = {}

    if command_key not in config["commands"]:
        config["commands"][command_key] = {}

    config["commands"][command_key]["last_execution"] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "duration_ms": duration_ms,
        "status": status.upper()
    }

    write_run_config(config)


def output_toon(status: str, duration_ms: int, polls: int, timeout_used_ms: int,
                timeout_source: str, command_key: Optional[str],
                final_result: dict, error: Optional[str] = None) -> None:
    """Output result in TOON format."""
    print(f"status\t{status}")
    print(f"duration_ms\t{duration_ms}")
    print(f"polls\t{polls}")
    print(f"timeout_used_ms\t{timeout_used_ms}")
    print(f"timeout_source\t{timeout_source}")

    if command_key:
        print(f"command_key\t{command_key}")

    # Flatten final result
    for key, value in final_result.items():
        print(f"final_result.{key}\t{value}")

    if error:
        print(f"error\t{error}")


def cmd_poll(args) -> int:
    """Execute poll loop until condition is satisfied or timeout."""
    check_cmd = args.check_cmd
    success_field = args.success_field
    failure_field = args.failure_field
    command_key = args.command_key

    # Determine timeout
    timeout_ms: int
    timeout_source: str

    if args.timeout is not None:
        # Explicit mode
        timeout_ms = args.timeout * 1000
        timeout_source = "explicit"
    elif command_key:
        # Adaptive mode
        adaptive = get_adaptive_timeout(command_key)
        if adaptive is not None:
            timeout_ms = adaptive
            timeout_source = "adaptive"
        else:
            timeout_ms = DEFAULT_TIMEOUT_MS
            timeout_source = "default"
    else:
        timeout_ms = DEFAULT_TIMEOUT_MS
        timeout_source = "default"

    # Determine poll interval
    interval_ms = (args.interval * 1000) if args.interval else DEFAULT_INTERVAL_MS

    # Poll loop
    start_time = time.time()
    polls = 0
    final_result = {}
    status = "pending"
    error_msg = None

    while True:
        polls += 1
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Execute check command
        exit_code, stdout, stderr = run_check_command(check_cmd)

        if exit_code != 0:
            # Command failed - treat as pending unless we hit timeout
            final_result = {"check_error": stderr or "Command failed"}
        else:
            # Parse output and check condition
            final_result = parse_toon_output(stdout)
            status = check_condition(final_result, success_field, failure_field)

        # Check for terminal conditions
        if status == "success":
            duration_ms = int((time.time() - start_time) * 1000)

            # Update history if adaptive mode
            if command_key:
                update_execution_history(command_key, duration_ms, "SUCCESS")

            output_toon(status, duration_ms, polls, timeout_ms, timeout_source,
                       command_key, final_result)
            return 0

        if status == "failure":
            duration_ms = int((time.time() - start_time) * 1000)

            # Update history if adaptive mode
            if command_key:
                update_execution_history(command_key, duration_ms, "FAILURE")

            error_msg = "Condition returned permanent failure"
            output_toon(status, duration_ms, polls, timeout_ms, timeout_source,
                       command_key, final_result, error_msg)
            return 1

        # Check timeout
        elapsed_ms = int((time.time() - start_time) * 1000)
        if elapsed_ms >= timeout_ms:
            duration_ms = elapsed_ms

            # Update history if adaptive mode
            if command_key:
                update_execution_history(command_key, duration_ms, "TIMEOUT")

            error_msg = f"Timeout after {duration_ms}ms ({polls} polls)"
            output_toon("timeout", duration_ms, polls, timeout_ms, timeout_source,
                       command_key, final_result, error_msg)
            return 1

        # Sleep before next poll
        time.sleep(interval_ms / 1000)


def main():
    parser = argparse.ArgumentParser(
        description='Synchronous polling utility for blocking until async operations complete',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Adaptive mode (timeout managed via run-config)
  %(prog)s poll \\
    --check-cmd "python3 .plan/execute-script.py pm-ci:ci-api:ci-provider-api ci check-status --pr 123" \\
    --success-field "status=success" \\
    --failure-field "status=failure" \\
    --command-key "ci:pr_checks"

  # Explicit mode (manual timeout)
  %(prog)s poll \\
    --check-cmd "gh pr checks 123 --json state --jq '.[] | .state'" \\
    --success-field "status=success" \\
    --timeout 300 \\
    --interval 30

Output (TOON format):
  status          success|timeout|failure
  duration_ms     Actual wait duration
  polls           Number of condition checks
  timeout_used_ms Timeout value used
  timeout_source  explicit|adaptive|default
  command_key     The command key (if adaptive)
  final_result.*  Flattened fields from last check
"""
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # poll subcommand
    poll_parser = subparsers.add_parser('poll', help='Poll until condition is satisfied')
    poll_parser.add_argument(
        '--check-cmd',
        required=True,
        help='Command to execute for checking condition (must output TOON format)'
    )
    poll_parser.add_argument(
        '--success-field',
        required=True,
        help='Field=value pattern for success (e.g., "status=success")'
    )
    poll_parser.add_argument(
        '--failure-field',
        help='Optional field=value pattern for permanent failure'
    )
    poll_parser.add_argument(
        '--command-key',
        help='Command key for adaptive timeout (e.g., "ci:pr_checks")'
    )
    poll_parser.add_argument(
        '--timeout',
        type=int,
        help='Explicit timeout in seconds (overrides adaptive)'
    )
    poll_parser.add_argument(
        '--interval',
        type=int,
        help='Poll interval in seconds (default: 30)'
    )
    poll_parser.set_defaults(func=cmd_poll)

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
