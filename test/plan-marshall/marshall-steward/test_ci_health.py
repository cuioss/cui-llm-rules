#!/usr/bin/env python3
"""Tests for ci-health.py script."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, create_temp_dir

SCRIPT_PATH = get_script_path('plan-marshall', 'marshall-steward', 'ci-health.py')


# =============================================================================
# Test: detect subcommand
# =============================================================================

def test_detect_returns_json():
    """detect returns valid JSON with GitHub provider."""
    tmp_path = create_temp_dir()
    try:
        # Setup git repo with github remote
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/org/repo"],
            cwd=tmp_path,
            capture_output=True,
        )

        result = run_script(SCRIPT_PATH, "detect", cwd=tmp_path)

        assert result.success, f"Should succeed: {result.stderr}"
        data = result.json()
        assert data["status"] == "success"
        assert data["provider"] == "github"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_detect_gitlab():
    """detect identifies GitLab from remote URL."""
    tmp_path = create_temp_dir()
    try:
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://gitlab.com/org/repo"],
            cwd=tmp_path,
            capture_output=True,
        )

        result = run_script(SCRIPT_PATH, "detect", cwd=tmp_path)

        data = result.json()
        assert data["provider"] == "gitlab"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_detect_unknown_no_remote():
    """detect returns unknown when no remote."""
    tmp_path = create_temp_dir()
    try:
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        result = run_script(SCRIPT_PATH, "detect", cwd=tmp_path)

        data = result.json()
        assert data["provider"] == "unknown"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_detect_github_from_directory():
    """detect identifies GitHub from .github directory."""
    tmp_path = create_temp_dir()
    try:
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://example.com/org/repo"],
            cwd=tmp_path,
            capture_output=True,
        )
        (tmp_path / ".github").mkdir()

        result = run_script(SCRIPT_PATH, "detect", cwd=tmp_path)

        data = result.json()
        assert data["provider"] == "github"
        assert data["confidence"] == "medium"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


# =============================================================================
# Test: verify subcommand
# =============================================================================

def test_verify_git_installed():
    """verify detects git is installed."""
    result = run_script(SCRIPT_PATH, "verify", "--tool", "git")

    assert result.success, f"Should succeed: {result.stderr}"
    data = result.json()
    assert data["tools"]["git"]["installed"] is True


def test_verify_returns_all_tools():
    """verify returns status for all tools."""
    result = run_script(SCRIPT_PATH, "verify")

    data = result.json()
    assert "git" in data["tools"]
    assert "gh" in data["tools"]
    assert "glab" in data["tools"]


def test_verify_unknown_tool_returns_error():
    """verify returns error for unknown tool."""
    result = run_script(SCRIPT_PATH, "verify", "--tool", "unknown_tool")

    assert not result.success, "Should fail for unknown tool"
    data = json.loads(result.stderr)
    assert data["status"] == "error"


# =============================================================================
# Test: status subcommand
# =============================================================================

def test_status_combines_detect_and_verify():
    """status returns both provider and tool info."""
    tmp_path = create_temp_dir()
    try:
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/org/repo"],
            cwd=tmp_path,
            capture_output=True,
        )

        result = run_script(SCRIPT_PATH, "status", cwd=tmp_path)

        data = result.json()
        assert "provider" in data
        assert "tools" in data
        assert "overall" in data
        assert "required_tool" in data
        assert "required_tool_ready" in data
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_status_unknown_when_no_provider():
    """status returns unknown overall when provider is unknown."""
    tmp_path = create_temp_dir()
    try:
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        result = run_script(SCRIPT_PATH, "status", cwd=tmp_path)

        data = result.json()
        assert data["provider"]["name"] == "unknown"
        assert data["overall"] == "unknown"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


# =============================================================================
# Test: persist subcommand
# =============================================================================

def test_persist_updates_marshal_json():
    """persist updates marshal.json with CI provider config."""
    tmp_path = create_temp_dir()
    try:
        # Setup git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/org/repo"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create .plan directory with marshal.json
        plan_dir = tmp_path / ".plan"
        plan_dir.mkdir()
        marshal_path = plan_dir / "marshal.json"
        marshal_path.write_text('{"skill_domains": {}}')

        result = run_script(
            SCRIPT_PATH, "persist", "--plan-dir", str(plan_dir),
            cwd=tmp_path
        )

        assert result.success, f"Should succeed: {result.stderr}"
        data = result.json()
        assert data["status"] == "success"
        assert "persisted" in data
        assert data["persisted"]["marshal_json"]["provider"] == "github"

        # Verify marshal.json was updated with provider info (not tools)
        updated_config = json.loads(marshal_path.read_text())
        assert "ci" in updated_config
        assert updated_config["ci"]["provider"] == "github"
        assert "repo_url" in updated_config["ci"]
        assert "detected_at" in updated_config["ci"]
        # authenticated_tools should NOT be in marshal.json
        assert "authenticated_tools" not in updated_config["ci"]
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_persist_writes_tools_to_run_config():
    """persist writes authenticated_tools and git_present to run-configuration.json."""
    tmp_path = create_temp_dir()
    try:
        # Setup git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/org/repo"],
            cwd=tmp_path,
            capture_output=True,
        )

        # Create .plan directory with marshal.json
        plan_dir = tmp_path / ".plan"
        plan_dir.mkdir()
        marshal_path = plan_dir / "marshal.json"
        marshal_path.write_text('{"skill_domains": {}}')
        run_config_path = plan_dir / "run-configuration.json"

        result = run_script(
            SCRIPT_PATH, "persist", "--plan-dir", str(plan_dir),
            cwd=tmp_path
        )

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify run-configuration.json was created with tools
        assert run_config_path.exists(), "run-configuration.json should be created"
        run_config = json.loads(run_config_path.read_text())
        assert "ci" in run_config
        assert "git_present" in run_config["ci"], "git_present should be in run-config"
        assert run_config["ci"]["git_present"] is True, "git_present should be True when git is installed"
        assert "authenticated_tools" in run_config["ci"]
        assert "verified_at" in run_config["ci"]
        # git should be authenticated (installed)
        assert "git" in run_config["ci"]["authenticated_tools"]
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_persist_error_when_no_marshal_json():
    """persist returns error when marshal.json doesn't exist."""
    tmp_path = create_temp_dir()
    try:
        plan_dir = tmp_path / ".plan"
        plan_dir.mkdir()

        result = run_script(
            SCRIPT_PATH, "persist", "--plan-dir", str(plan_dir),
            cwd=tmp_path
        )

        assert not result.success, "Should fail without marshal.json"
        data = json.loads(result.stderr)
        assert data["status"] == "error"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


# =============================================================================
# Test: help output
# =============================================================================

def test_main_help():
    """Main script shows help."""
    result = run_script(SCRIPT_PATH, "--help")

    assert result.success, "Help should succeed"
    assert "detect" in result.stdout
    assert "verify" in result.stdout
    assert "status" in result.stdout
    assert "persist" in result.stdout


def test_detect_help():
    """detect subcommand shows help."""
    result = run_script(SCRIPT_PATH, "detect", "--help")
    assert result.success


def test_verify_help():
    """verify subcommand shows help."""
    result = run_script(SCRIPT_PATH, "verify", "--help")
    assert result.success


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_detect_returns_json,
        test_detect_gitlab,
        test_detect_unknown_no_remote,
        test_detect_github_from_directory,
        test_verify_git_installed,
        test_verify_returns_all_tools,
        test_verify_unknown_tool_returns_error,
        test_status_combines_detect_and_verify,
        test_status_unknown_when_no_provider,
        test_persist_updates_marshal_json,
        test_persist_writes_tools_to_run_config,
        test_persist_error_when_no_marshal_json,
        test_main_help,
        test_detect_help,
        test_verify_help,
    ])
    sys.exit(runner.run())
