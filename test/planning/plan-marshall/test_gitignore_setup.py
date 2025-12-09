#!/usr/bin/env python3
"""Tests for gitignore-setup.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, create_temp_dir

import shutil

# Get script path
SCRIPT_PATH = get_script_path('planning', 'plan-marshall', 'gitignore-setup.py')


def parse_toon_output(output: str) -> dict:
    """Parse TOON format output into a dictionary."""
    result = {}
    for line in output.strip().split("\n"):
        if "\t" in line:
            key, value = line.split("\t", 1)
            result[key] = value
    return result


# =============================================================================
# Tests
# =============================================================================

def test_creates_gitignore_when_missing():
    """Should create .gitignore with planning entries when file doesn't exist."""
    temp_dir = create_temp_dir()
    try:
        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir))

        assert result.success, f"Script failed: {result.stderr}"
        output = parse_toon_output(result.stdout)
        assert output["status"] == "created"
        assert output["entries_added"] == "2"

        # Verify file content
        gitignore = temp_dir / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert ".plan/" in content
        assert "!.plan/marshal.json" in content
        assert "# Planning system" in content
    finally:
        shutil.rmtree(temp_dir)


def test_updates_existing_gitignore():
    """Should add planning entries to existing .gitignore."""
    temp_dir = create_temp_dir()
    try:
        gitignore = temp_dir / ".gitignore"
        gitignore.write_text("node_modules/\n*.log\n")

        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir))

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["status"] == "updated"
        assert output["entries_added"] == "2"

        # Verify existing content preserved
        content = gitignore.read_text()
        assert "node_modules/" in content
        assert "*.log" in content
        assert ".plan/" in content
        assert "!.plan/marshal.json" in content
    finally:
        shutil.rmtree(temp_dir)


def test_unchanged_when_entries_exist():
    """Should report unchanged when entries already exist."""
    temp_dir = create_temp_dir()
    try:
        gitignore = temp_dir / ".gitignore"
        gitignore.write_text("# Existing\n.plan/\n!.plan/marshal.json\n")

        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir))

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["status"] == "unchanged"
        assert output["entries_added"] == "0"
    finally:
        shutil.rmtree(temp_dir)


def test_adds_only_missing_entries():
    """Should add only missing entries."""
    temp_dir = create_temp_dir()
    try:
        gitignore = temp_dir / ".gitignore"
        gitignore.write_text(".plan/\n")  # Has plan dir, missing exception

        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir))

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["status"] == "updated"
        assert output["entries_added"] == "1"

        content = gitignore.read_text()
        assert "!.plan/marshal.json" in content
    finally:
        shutil.rmtree(temp_dir)


def test_dry_run_does_not_modify():
    """Should not modify files in dry-run mode."""
    temp_dir = create_temp_dir()
    try:
        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir), "--dry-run")

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["status"] == "created"
        assert output["dry_run"] == "true"

        # File should NOT exist
        gitignore = temp_dir / ".gitignore"
        assert not gitignore.exists()
    finally:
        shutil.rmtree(temp_dir)


def test_dry_run_on_existing_file():
    """Should report what would be done without modifying existing file."""
    temp_dir = create_temp_dir()
    try:
        gitignore = temp_dir / ".gitignore"
        original_content = "node_modules/\n"
        gitignore.write_text(original_content)

        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir), "--dry-run")

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["status"] == "updated"
        assert output["dry_run"] == "true"

        # File should be unchanged
        assert gitignore.read_text() == original_content
    finally:
        shutil.rmtree(temp_dir)


def test_error_when_project_root_not_found():
    """Should return error when project root doesn't exist."""
    result = run_script(SCRIPT_PATH, "--project-root", "/nonexistent/path")

    assert not result.success
    assert "project_root_not_found" in result.stderr


def test_preserves_trailing_newline():
    """Should preserve proper formatting with trailing newlines."""
    temp_dir = create_temp_dir()
    try:
        gitignore = temp_dir / ".gitignore"
        gitignore.write_text("node_modules/")  # No trailing newline

        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir))

        assert result.success
        content = gitignore.read_text()
        # Should have blank line before new section
        assert "\n\n# Planning system" in content
    finally:
        shutil.rmtree(temp_dir)


def test_toon_output_format():
    """Should output valid TOON format with tab separators."""
    temp_dir = create_temp_dir()
    try:
        result = run_script(SCRIPT_PATH, "--project-root", str(temp_dir))

        assert result.success
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 3, f"Expected at least 3 lines, got {len(lines)}"
        for line in lines:
            assert "\t" in line, f"Line missing tab: {line}"
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    runner = TestRunner()
    runner.add_tests([
        test_creates_gitignore_when_missing,
        test_updates_existing_gitignore,
        test_unchanged_when_entries_exist,
        test_adds_only_missing_entries,
        test_dry_run_does_not_modify,
        test_dry_run_on_existing_file,
        test_error_when_project_root_not_found,
        test_preserves_trailing_newline,
        test_toon_output_format,
    ])
    sys.exit(runner.run())
