#!/usr/bin/env python3
"""Tests for write-plan.py script."""

import json
import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-task-workflow', 'plan-files', 'write-plan.py')


# =============================================================================
# Test Fixtures
# =============================================================================

def create_phases_json(tasks_with_checklist):
    """Helper to create phases JSON with tasks."""
    return json.dumps([{
        "name": "execute",
        "status": "in_progress",
        "tasks": tasks_with_checklist
    }])


# =============================================================================
# Tests
# =============================================================================

def test_write_basic_plan():
    """Test writing a basic plan."""
    temp_dir = create_temp_dir()
    try:
        phases_json = json.dumps([
            {"name": "init", "status": "completed", "tasks": 2},
            {"name": "execute", "status": "pending", "tasks": 1}
        ])

        result = run_script(
            SCRIPT_PATH,
            '--plan-dir', str(temp_dir),
            '--title', 'Test Plan',
            '--current-phase', 'init',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        )

        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()
        assert data['success'] is True
        assert 'file' in data

        # Verify file was created
        plan_file = temp_dir / 'plan.md'
        assert plan_file.exists()
        content = plan_file.read_text()
        assert '# Task Plan: Test Plan' in content
        assert '**Current Phase**: init' in content
    finally:
        shutil.rmtree(temp_dir)


def test_write_plan_with_checklist():
    """Test writing a plan with checklist items."""
    temp_dir = create_temp_dir()
    try:
        phases_json = create_phases_json([{
            "name": "Test Task",
            "phase": "execute",
            "goal": "Test goal",
            "checklist": ["Item one", "Item two"]
        }])

        result = run_script(
            SCRIPT_PATH,
            '--plan-dir', str(temp_dir),
            '--title', 'Checklist Test',
            '--current-phase', 'execute',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        )

        assert result.success, f"Script failed: {result.stderr}"

        plan_file = temp_dir / 'plan.md'
        content = plan_file.read_text()
        assert '- [ ] Item one' in content
        assert '- [ ] Item two' in content
    finally:
        shutil.rmtree(temp_dir)


def test_write_plan_with_checked_items():
    """Test writing a plan with already checked items using [x] prefix."""
    temp_dir = create_temp_dir()
    try:
        phases_json = create_phases_json([{
            "name": "Test Task",
            "phase": "execute",
            "goal": "Test goal",
            "checklist": ["[x] Completed item", "[ ] Pending item"]
        }])

        result = run_script(
            SCRIPT_PATH,
            '--plan-dir', str(temp_dir),
            '--title', 'Checked Items Test',
            '--current-phase', 'execute',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        )

        assert result.success, f"Script failed: {result.stderr}"

        plan_file = temp_dir / 'plan.md'
        content = plan_file.read_text()
        # Should have exactly one [x] (not [x] [x])
        assert '- [x] Completed item' in content
        assert '- [ ] Pending item' in content
        # Should NOT have double checkbox markers
        assert '- [x] [x]' not in content
        assert '- [ ] [ ]' not in content
    finally:
        shutil.rmtree(temp_dir)


def test_write_plan_with_x_prefix():
    """Test writing a plan where checklist items have 'x ' prefix (should be treated as checked).

    This is the bug case - when checklist items come in as "x Item text" they should
    be converted to "[x] Item text", not "[ ] x Item text".
    """
    temp_dir = create_temp_dir()
    try:
        phases_json = create_phases_json([{
            "name": "Test Task",
            "phase": "execute",
            "goal": "Test goal",
            "checklist": ["x Completed item", "Pending item"]
        }])

        result = run_script(
            SCRIPT_PATH,
            '--plan-dir', str(temp_dir),
            '--title', 'X Prefix Test',
            '--current-phase', 'execute',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        )

        assert result.success, f"Script failed: {result.stderr}"

        plan_file = temp_dir / 'plan.md'
        content = plan_file.read_text()

        # The item starting with "x " should become checked "[x]" without the "x " prefix
        assert '- [x] Completed item' in content, f"Expected '- [x] Completed item' but got: {content}"
        assert '- [ ] Pending item' in content

        # Should NOT have "x " remaining in the text
        assert '- [x] x Completed' not in content, "Should not have 'x ' prefix remaining"
        assert '- [ ] x Completed' not in content, "Should not treat 'x ' prefix as unchecked"
    finally:
        shutil.rmtree(temp_dir)


def test_write_plan_with_dict_checklist():
    """Test writing a plan with dict-format checklist items."""
    temp_dir = create_temp_dir()
    try:
        phases_json = create_phases_json([{
            "name": "Test Task",
            "phase": "execute",
            "goal": "Test goal",
            "checklist": [
                {"text": "Done item", "done": True},
                {"text": "Pending item", "done": False}
            ]
        }])

        result = run_script(
            SCRIPT_PATH,
            '--plan-dir', str(temp_dir),
            '--title', 'Dict Checklist Test',
            '--current-phase', 'execute',
            '--current-task', 'task-1',
            '--phases-json', phases_json
        )

        assert result.success, f"Script failed: {result.stderr}"

        plan_file = temp_dir / 'plan.md'
        content = plan_file.read_text()
        assert '- [x] Done item' in content
        assert '- [ ] Pending item' in content
    finally:
        shutil.rmtree(temp_dir)


def test_missing_plan_dir():
    """Test error when plan directory is not provided."""
    result = run_script(
        SCRIPT_PATH,
        '--title', 'Test',
        '--current-phase', 'init',
        '--current-task', 'task-1',
        '--phases-json', '[]'
    )

    assert not result.success


def test_invalid_phases_json():
    """Test error when phases JSON is invalid."""
    temp_dir = create_temp_dir()
    try:
        result = run_script(
            SCRIPT_PATH,
            '--plan-dir', str(temp_dir),
            '--title', 'Test',
            '--current-phase', 'init',
            '--current-task', 'task-1',
            '--phases-json', 'not valid json'
        )

        assert not result.success
        # Error output goes to stderr
        data = result.json_or_error()
        assert data['success'] is False
        assert 'Invalid phases JSON' in data['error']
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_write_basic_plan,
        test_write_plan_with_checklist,
        test_write_plan_with_checked_items,
        test_write_plan_with_x_prefix,
        test_write_plan_with_dict_checklist,
        test_missing_plan_dir,
        test_invalid_phases_json,
    ])
    sys.exit(runner.run())
