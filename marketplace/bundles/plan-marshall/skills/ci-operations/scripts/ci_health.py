#!/usr/bin/env python3
"""
CI health verification script for detecting CI providers and verifying tool availability.

Subcommands:
    detect      Detect CI provider from repository configuration
    verify      Verify CLI tools are installed and authenticated
    status      Full health check (detect + verify)
    persist     Detect and persist CI configuration to marshal.json

Usage:
    python3 ci-health.py detect
    python3 ci-health.py verify [--tool TOOL]
    python3 ci-health.py status
    python3 ci-health.py persist

Output (JSON format):
    All subcommands return JSON with status field.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# Tool definitions: {tool: requires_auth}
# Note: python3 not checked - if it wasn't available, this script couldn't run
TOOLS = {
    "git": False,
    "gh": True,
    "glab": True,
}

# Provider to required tool mapping
PROVIDER_TOOLS = {
    "github": "gh",
    "gitlab": "glab",
    "unknown": None,
}


def run_command(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=10,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timed out: {' '.join(cmd)}"
    except Exception as e:
        return 1, "", str(e)


def parse_version(output: str) -> str | None:
    """Extract version string from command output."""
    # Common patterns: "git version 2.43.0", "gh version 2.45.0", "Python 3.12.0"
    patterns = [
        r"version\s+(\d+\.\d+(?:\.\d+)?)",
        r"Python\s+(\d+\.\d+(?:\.\d+)?)",
        r"(\d+\.\d+\.\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1)
    return None


def verify_tool(tool: str) -> dict:
    """
    Verify a tool is installed and authenticated.

    Returns: {"installed": bool, "authenticated": bool, "version": str | None}
    """
    # Check installed
    returncode, stdout, stderr = run_command([tool, "--version"])
    if returncode != 0:
        return {"installed": False, "authenticated": False, "version": None}

    version = parse_version(stdout + stderr)

    # Check authenticated (if applicable)
    requires_auth = TOOLS.get(tool, False)
    if requires_auth:
        auth_returncode, _, _ = run_command([tool, "auth", "status"])
        authenticated = auth_returncode == 0
    else:
        authenticated = True  # No auth needed

    return {"installed": True, "authenticated": authenticated, "version": version}


def is_gitlab_enterprise(url: str) -> bool:
    """Check if URL matches GitLab enterprise patterns."""
    gitlab_patterns = [
        r"gitlab\.",
        r"\.gitlab\.",
    ]
    url_lower = url.lower()
    return any(re.search(pattern, url_lower) for pattern in gitlab_patterns)


def detect_provider(cwd: str | None = None) -> dict:
    """
    Detect CI provider from repository configuration.

    Returns: {"provider": str, "repo_url": str | None, "confidence": str}
    """
    # Get remote URL
    returncode, stdout, _ = run_command(["git", "remote", "get-url", "origin"], cwd=cwd)
    if returncode != 0:
        # Check for provider-specific files as fallback
        check_path = Path(cwd) if cwd else Path.cwd()
        if (check_path / ".github").exists():
            return {"provider": "github", "repo_url": None, "confidence": "medium"}
        elif (check_path / ".gitlab-ci.yml").exists():
            return {"provider": "gitlab", "repo_url": None, "confidence": "medium"}
        return {"provider": "unknown", "repo_url": None, "confidence": "none"}

    repo_url = stdout.strip()

    # Check URL patterns
    if "github.com" in repo_url:
        return {"provider": "github", "repo_url": repo_url, "confidence": "high"}
    elif "gitlab.com" in repo_url or is_gitlab_enterprise(repo_url):
        return {"provider": "gitlab", "repo_url": repo_url, "confidence": "high"}

    # Check for provider-specific files
    check_path = Path(cwd) if cwd else Path.cwd()
    if (check_path / ".github").exists():
        return {"provider": "github", "repo_url": repo_url, "confidence": "medium"}
    elif (check_path / ".gitlab-ci.yml").exists():
        return {"provider": "gitlab", "repo_url": repo_url, "confidence": "medium"}

    return {"provider": "unknown", "repo_url": repo_url, "confidence": "none"}


def get_required_ci_tool(provider: str) -> str | None:
    """Return required CI CLI tool for provider."""
    return PROVIDER_TOOLS.get(provider)


def determine_overall_health(provider: str, tools: dict) -> str:
    """Determine overall health status."""
    required_tool = get_required_ci_tool(provider)

    if provider == "unknown":
        return "unknown"

    if required_tool is None:
        return "healthy"

    tool_status = tools.get(required_tool, {})
    if not tool_status.get("installed", False):
        return "degraded"
    if not tool_status.get("authenticated", False):
        return "degraded"

    return "healthy"


def output_json(data: dict) -> None:
    """Output JSON to stdout."""
    print(json.dumps(data, indent=2))


def error_json(message: str, **extra) -> int:
    """Output error JSON to stderr and return error exit code."""
    print(json.dumps({"status": "error", "error": message, **extra}), file=sys.stderr)
    return 1


def cmd_detect(args: argparse.Namespace) -> int:
    """Handle the 'detect' subcommand."""
    result = detect_provider()
    output_json({
        "status": "success",
        "provider": result["provider"],
        "repo_url": result["repo_url"],
        "confidence": result["confidence"],
    })
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Handle the 'verify' subcommand."""
    if args.tool:
        # Verify specific tool
        if args.tool not in TOOLS:
            return error_json(f"Unknown tool: {args.tool}", known_tools=list(TOOLS.keys()))
        tool_result = verify_tool(args.tool)
        output_json({
            "status": "success",
            "tools": {args.tool: tool_result},
            "all_required_available": tool_result["installed"] and tool_result["authenticated"],
        })
    else:
        # Verify all tools
        tools_result = {}
        all_available = True
        for tool in TOOLS:
            tools_result[tool] = verify_tool(tool)
            if TOOLS[tool]:  # Only check auth-required tools for "all available"
                if not tools_result[tool]["installed"] or not tools_result[tool]["authenticated"]:
                    all_available = False

        output_json({
            "status": "success",
            "tools": tools_result,
            "all_required_available": all_available,
        })
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Handle the 'status' subcommand."""
    # Detect provider
    provider_result = detect_provider()

    # Verify all tools
    tools_result = {}
    for tool in TOOLS:
        tools_result[tool] = verify_tool(tool)

    # Determine required tool and readiness
    required_tool = get_required_ci_tool(provider_result["provider"])
    if required_tool:
        tool_status = tools_result.get(required_tool, {})
        required_tool_ready = tool_status.get("installed", False) and tool_status.get("authenticated", False)
    else:
        required_tool_ready = True  # No required tool means ready

    # Determine overall health
    overall = determine_overall_health(provider_result["provider"], tools_result)

    output_json({
        "status": "success",
        "provider": {
            "name": provider_result["provider"],
            "repo_url": provider_result["repo_url"],
            "confidence": provider_result["confidence"],
        },
        "tools": tools_result,
        "required_tool": required_tool,
        "required_tool_ready": required_tool_ready,
        "overall": overall,
    })
    return 0


def generate_ci_commands(provider: str) -> dict:
    """Generate static CI commands for the detected provider.

    Returns dict of command_name -> full command string.
    """
    if provider not in ("github", "gitlab"):
        return {}

    executor = "python3 .plan/execute-script.py"
    script = f"ci-operations:{provider}"  # Notation: {skill}:{script}

    return {
        "pr-create": f"{executor} {script} pr create",
        "pr-reviews": f"{executor} {script} pr reviews",
        "ci-status": f"{executor} {script} ci status",
        "ci-wait": f"{executor} {script} ci wait",
        "issue-create": f"{executor} {script} issue create",
    }


def cmd_persist(args: argparse.Namespace) -> int:
    """Handle the 'persist' subcommand.

    Splits CI config between two files:
    - marshal.json (shared): provider, repo_url, detected_at, commands
    - run-configuration.json (local): authenticated_tools, verified_at
    """
    plan_dir = Path(args.plan_dir)
    marshal_path = plan_dir / "marshal.json"
    run_config_path = plan_dir / "run-configuration.json"

    if not marshal_path.exists():
        return error_json(f"marshal.json not found at {marshal_path}. Run /marshall-steward first.")

    # Detect provider
    provider_result = detect_provider()

    # Verify all tools and collect authenticated ones
    authenticated_tools = []
    git_present = False
    for tool in TOOLS:
        tool_status = verify_tool(tool)
        if tool_status["installed"] and tool_status["authenticated"]:
            authenticated_tools.append(tool)
        if tool == "git" and tool_status["installed"]:
            git_present = True

    # Timestamps
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    # Generate static commands for provider
    ci_commands = generate_ci_commands(provider_result["provider"])

    # Build marshal.json CI config (project-level, shared)
    marshal_ci_config = {
        "repo_url": provider_result["repo_url"],
        "provider": provider_result["provider"],
        "detected_at": now,
        "commands": ci_commands,
    }

    # Build run-configuration.json CI config (local, machine-specific)
    run_config_ci = {
        "git_present": git_present,
        "authenticated_tools": authenticated_tools,
        "verified_at": now,
    }

    # Update marshal.json
    try:
        config = json.loads(marshal_path.read_text(encoding="utf-8"))
        config["ci"] = marshal_ci_config
        marshal_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    except json.JSONDecodeError as e:
        return error_json(f"Invalid JSON in marshal.json: {e}")
    except Exception as e:
        return error_json(f"Failed to update marshal.json: {e}")

    # Update run-configuration.json
    try:
        if run_config_path.exists():
            run_config = json.loads(run_config_path.read_text(encoding="utf-8"))
        else:
            run_config = {"version": 1, "commands": {}}
        run_config["ci"] = run_config_ci
        run_config_path.write_text(json.dumps(run_config, indent=2), encoding="utf-8")
    except json.JSONDecodeError as e:
        return error_json(f"Invalid JSON in run-configuration.json: {e}")
    except Exception as e:
        return error_json(f"Failed to update run-configuration.json: {e}")

    # Output in TOON format
    print("status: success")
    print("persisted_to: marshal.json")
    print()
    print("ci_config{key,value}:")
    print(f"provider\t{provider_result['provider']}")
    print(f"repo_url\t{provider_result['repo_url'] or 'none'}")
    print()
    if ci_commands:
        print(f"ci_commands[{len(ci_commands)}]{{name,command}}:")
        for name, command in ci_commands.items():
            print(f"{name}\t{command}")
    else:
        print("ci_commands[0]{name,command}:")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CI health verification for detecting providers and verifying tools"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # detect subcommand
    subparsers.add_parser(
        "detect",
        help="Detect CI provider from repository configuration"
    )

    # verify subcommand
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify CLI tools are installed and authenticated"
    )
    verify_parser.add_argument(
        "--tool",
        type=str,
        help="Specific tool to verify (git, gh, glab)"
    )

    # status subcommand
    subparsers.add_parser(
        "status",
        help="Full health check (detect + verify)"
    )

    # persist subcommand
    persist_parser = subparsers.add_parser(
        "persist",
        help="Detect and persist CI configuration to marshal.json"
    )
    persist_parser.add_argument(
        "--plan-dir",
        type=str,
        default=".plan",
        help="Path to .plan directory (default: .plan)"
    )

    args = parser.parse_args()

    if args.command == "detect":
        return cmd_detect(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "persist":
        return cmd_persist(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
