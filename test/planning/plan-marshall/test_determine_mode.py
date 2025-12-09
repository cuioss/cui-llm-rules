#!/usr/bin/env python3
"""Tests for determine-mode.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path, create_temp_dir

import shutil

# Get script path
SCRIPT_PATH = get_script_path('planning', 'plan-marshall', 'determine-mode.py')


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

def test_wizard_mode_when_nothing_exists():
    """Should return wizard mode when .plan directory is empty."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / ".plan"
        plan_dir.mkdir()

        result = run_script(SCRIPT_PATH, "--plan-dir", str(plan_dir))

        assert result.success, f"Script failed: {result.stderr}"
        output = parse_toon_output(result.stdout)
        assert output["mode"] == "wizard", f"Expected wizard, got {output['mode']}"
        assert output["reason"] == "executor_missing"
    finally:
        shutil.rmtree(temp_dir)


def test_wizard_mode_when_only_marshal_exists():
    """Should return wizard mode when only marshal.json exists."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / ".plan"
        plan_dir.mkdir()
        (plan_dir / "marshal.json").write_text("{}")

        result = run_script(SCRIPT_PATH, "--plan-dir", str(plan_dir))

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["mode"] == "wizard"
        assert output["reason"] == "executor_missing"
    finally:
        shutil.rmtree(temp_dir)


def test_wizard_mode_when_only_executor_exists():
    """Should return wizard mode when only executor exists."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / ".plan"
        plan_dir.mkdir()
        (plan_dir / "execute-script.py").write_text("# executor")

        result = run_script(SCRIPT_PATH, "--plan-dir", str(plan_dir))

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["mode"] == "wizard"
        assert output["reason"] == "marshal_missing"
    finally:
        shutil.rmtree(temp_dir)


def test_menu_mode_when_both_exist():
    """Should return menu mode when both files exist."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / ".plan"
        plan_dir.mkdir()
        (plan_dir / "execute-script.py").write_text("# executor")
        (plan_dir / "marshal.json").write_text("{}")

        result = run_script(SCRIPT_PATH, "--plan-dir", str(plan_dir))

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["mode"] == "menu"
        assert output["reason"] == "both_exist"
    finally:
        shutil.rmtree(temp_dir)


def test_wizard_mode_when_plan_dir_does_not_exist():
    """Should return wizard mode when .plan directory doesn't exist."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / ".plan"
        # Don't create the directory

        result = run_script(SCRIPT_PATH, "--plan-dir", str(plan_dir))

        assert result.success
        output = parse_toon_output(result.stdout)
        assert output["mode"] == "wizard"
        assert output["reason"] == "executor_missing"
    finally:
        shutil.rmtree(temp_dir)


def test_toon_output_format():
    """Should output valid TOON format with tab separators."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / ".plan"
        plan_dir.mkdir()

        result = run_script(SCRIPT_PATH, "--plan-dir", str(plan_dir))

        assert result.success
        lines = result.stdout.strip().split("\n")
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
        for line in lines:
            assert "\t" in line, f"Line missing tab: {line}"
            parts = line.split("\t")
            assert len(parts) == 2, f"Expected 2 parts, got {len(parts)}: {line}"
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    runner = TestRunner()
    runner.add_tests([
        test_wizard_mode_when_nothing_exists,
        test_wizard_mode_when_only_marshal_exists,
        test_wizard_mode_when_only_executor_exists,
        test_menu_mode_when_both_exist,
        test_wizard_mode_when_plan_dir_does_not_exist,
        test_toon_output_format,
    ])
    sys.exit(runner.run())
