#!/usr/bin/env python3
"""Tests for task.py script."""

import os
import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'manage-tasks', 'manage-task.py')


# =============================================================================
# Test Helpers
# =============================================================================

def setup_plan_dir():
    """Create temp plan directory and set PLAN_BASE_DIR."""
    temp_dir = create_temp_dir()
    plan_base = temp_dir / '.plan'
    plan_base.mkdir()
    os.environ['PLAN_BASE_DIR'] = str(plan_base)

    # Create plan directory
    plan_dir = plan_base / 'plans' / 'test-plan'
    plan_dir.mkdir(parents=True)

    return temp_dir


def cleanup(temp_dir):
    """Clean up temp directory and env var."""
    if 'PLAN_BASE_DIR' in os.environ:
        del os.environ['PLAN_BASE_DIR']
    shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# Tests: add
# =============================================================================

def test_add_first_task():
    """Add first task creates TASK-001."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add',
                            '--plan-id', 'test-plan',
                            '--title', 'First task',
                            '--specification', 'SPEC-1',
                            '--description', 'Task description',
                            '--steps', 'Step one', 'Step two')

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert 'status: success' in result.stdout
        assert 'TASK-001' in result.stdout
        assert 'total_tasks: 1' in result.stdout

        # Verify file exists
        task_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'tasks'
        files = list(task_dir.glob('TASK-001-*.toon'))
        assert len(files) == 1, f"Expected 1 file, got {files}"
    finally:
        cleanup(temp_dir)


def test_add_sequential_numbering():
    """Adding multiple tasks gets sequential numbers."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--specification', 'SPEC-1', '--description', 'Desc 1',
                   '--steps', 'Step 1')
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                            '--specification', 'SPEC-2', '--description', 'Desc 2',
                            '--steps', 'Step 1', 'Step 2')

        assert result.returncode == 0
        assert 'TASK-002' in result.stdout
        assert 'total_tasks: 2' in result.stdout
    finally:
        cleanup(temp_dir)


def test_add_creates_slug_from_title():
    """Slug is generated from title."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Implement JWT Service!',
                   '--specification', 'SPEC-1',
                   '--description', 'Details here',
                   '--steps', 'Step 1')

        task_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'tasks'
        files = list(task_dir.glob('TASK-001-*.toon'))
        assert len(files) == 1
        assert 'implement-jwt-service' in files[0].name
    finally:
        cleanup(temp_dir)


def test_add_fails_without_specification():
    """Add fails if specification is invalid."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                            '--title', 'No spec',
                            '--specification', '',
                            '--description', 'Desc',
                            '--steps', 'Step 1')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
    finally:
        cleanup(temp_dir)


def test_add_fails_with_invalid_specification_format():
    """Add fails with invalid specification format."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                            '--title', 'Bad format',
                            '--specification', 'SPECIFICATION-1',
                            '--description', 'Desc',
                            '--steps', 'Step 1')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
        assert 'Invalid specification format' in result.stderr
    finally:
        cleanup(temp_dir)


def test_add_fails_without_steps():
    """Add fails if no steps provided."""
    temp_dir = setup_plan_dir()
    try:
        # argparse will catch this before our validation
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                            '--title', 'No steps',
                            '--specification', 'SPEC-1',
                            '--description', 'Desc')

        assert result.returncode != 0
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: get
# =============================================================================

def test_get_existing_task():
    """Get returns full task details."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Test task',
                   '--specification', 'SPEC-1',
                   '--description', 'Test description',
                   '--steps', 'Step one', 'Step two', 'Step three')

        result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')

        assert result.returncode == 0
        assert 'status: success' in result.stdout
        assert 'number: 1' in result.stdout
        assert 'Test task' in result.stdout
        assert 'SPEC-1' in result.stdout
        assert 'Test description' in result.stdout
        assert 'Step one' in result.stdout
        assert 'Step two' in result.stdout
    finally:
        cleanup(temp_dir)


def test_get_nonexistent_returns_error():
    """Get nonexistent task returns error."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '99')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
        assert 'TASK-99' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: list
# =============================================================================

def test_list_empty():
    """List with no tasks shows zero counts."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 0' in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_with_tasks():
    """List shows all tasks in table format."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--specification', 'SPEC-1', '--description', 'D1', '--steps', 'S1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--specification', 'SPEC-2', '--description', 'D2', '--steps', 'S1', 'S2')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 2' in result.stdout
        assert 'tasks[2]' in result.stdout
        assert '1,First,SPEC-1,pending,0/1' in result.stdout
        assert '2,Second,SPEC-2,pending,0/2' in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_filter_by_status():
    """List can filter by status."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--specification', 'SPEC-1', '--description', 'D1', '--steps', 'S1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--specification', 'SPEC-2', '--description', 'D2', '--steps', 'S1')
        # Mark first task as in_progress
        run_script(SCRIPT_PATH, 'step-start', '--plan-id', 'test-plan', '--task', '1', '--step', '1')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan', '--status', 'pending')

        assert result.returncode == 0
        assert 'tasks[1]' in result.stdout
        assert '2,Second' in result.stdout
        assert '1,First' not in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_filter_by_specification():
    """List can filter by specification reference."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--specification', 'SPEC-1', '--description', 'D1', '--steps', 'S1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--specification', 'SPEC-1', '--description', 'D2', '--steps', 'S1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Third',
                   '--specification', 'SPEC-2', '--description', 'D3', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan', '--specification', 'SPEC-1')

        assert result.returncode == 0
        assert 'total: 2' in result.stdout
        assert 'First' in result.stdout
        assert 'Second' in result.stdout
        assert 'Third' not in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: next
# =============================================================================

def test_next_returns_first_pending():
    """Next returns first pending task and step."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First Task',
                   '--specification', 'SPEC-1', '--description', 'D1',
                   '--steps', 'Step one', 'Step two')

        result = run_script(SCRIPT_PATH, 'next', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'task_number: 1' in result.stdout
        assert 'task_title: First Task' in result.stdout
        assert 'step_number: 1' in result.stdout
        assert 'step_title: Step one' in result.stdout
    finally:
        cleanup(temp_dir)


def test_next_returns_in_progress_task():
    """Next prioritizes in_progress tasks."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--specification', 'SPEC-1', '--description', 'D1', '--steps', 'S1', 'S2')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--specification', 'SPEC-2', '--description', 'D2', '--steps', 'S1')
        # Start first task
        run_script(SCRIPT_PATH, 'step-start', '--plan-id', 'test-plan', '--task', '1', '--step', '1')

        result = run_script(SCRIPT_PATH, 'next', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'task_number: 1' in result.stdout
        assert 'step_number: 1' in result.stdout
    finally:
        cleanup(temp_dir)


def test_next_returns_null_when_all_done():
    """Next returns null when all tasks complete."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Only Task',
                   '--specification', 'SPEC-1', '--description', 'D1', '--steps', 'S1')
        run_script(SCRIPT_PATH, 'step-done', '--plan-id', 'test-plan', '--task', '1', '--step', '1')

        result = run_script(SCRIPT_PATH, 'next', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'next: null' in result.stdout
        assert 'All tasks completed' in result.stdout
    finally:
        cleanup(temp_dir)


def test_next_empty_plan():
    """Next on empty plan returns null."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'next', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'next: null' in result.stdout
    finally:
        cleanup(temp_dir)


def test_next_include_context():
    """Next with --include-context embeds specification details."""
    temp_dir = setup_plan_dir()
    try:
        # Create a specification first
        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_content = """number: 1
title: Test Specification
status: pending
created: 2025-01-01T00:00:00Z
updated: 2025-01-01T00:00:00Z
requirements: REQ-1, REQ-2

body: |
  This is the specification body.
"""
        (spec_dir / 'SPEC-001-test-specification.toon').write_text(spec_content)

        # Create a task referencing that spec
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Implement feature',
                   '--specification', 'SPEC-1',
                   '--description', 'Task description',
                   '--steps', 'Step one', 'Step two')

        # Get next with context
        result = run_script(SCRIPT_PATH, 'next', '--plan-id', 'test-plan', '--include-context')

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert 'task_number: 1' in result.stdout
        assert 'specification_title: Test Specification' in result.stdout
        assert 'specification_body:' in result.stdout
    finally:
        cleanup(temp_dir)


def test_next_include_context_no_spec():
    """Next with --include-context handles missing specification gracefully."""
    temp_dir = setup_plan_dir()
    try:
        # Create a task without corresponding spec file
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Orphan task',
                   '--specification', 'SPEC-99',
                   '--description', 'No spec file',
                   '--steps', 'Step one')

        result = run_script(SCRIPT_PATH, 'next', '--plan-id', 'test-plan', '--include-context')

        assert result.returncode == 0
        assert 'task_number: 1' in result.stdout
        assert 'specification_found: false' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: step-start
# =============================================================================

def test_step_start_marks_in_progress():
    """Step-start marks step and task as in_progress."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1', 'S2')

        result = run_script(SCRIPT_PATH, 'step-start', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '1')

        assert result.returncode == 0
        assert 'task_status: in_progress' in result.stdout
        assert 'step_status: in_progress' in result.stdout
    finally:
        cleanup(temp_dir)


def test_step_start_invalid_step():
    """Step-start with invalid step number fails."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'step-start', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '99')

        assert result.returncode == 1
        assert 'Step 99 not found' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: step-done
# =============================================================================

def test_step_done_marks_completed():
    """Step-done marks step as done."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1', 'S2')

        result = run_script(SCRIPT_PATH, 'step-done', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '1')

        assert result.returncode == 0
        assert 'step_status: done' in result.stdout
        assert 'next_step: 2' in result.stdout
    finally:
        cleanup(temp_dir)


def test_step_done_completes_task():
    """Step-done on last step marks task as done."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'step-done', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '1')

        assert result.returncode == 0
        assert 'task_status: done' in result.stdout
        assert 'next_step: null' in result.stdout
        assert 'Task completed' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: step-skip
# =============================================================================

def test_step_skip_marks_skipped():
    """Step-skip marks step as skipped."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1', 'S2')

        result = run_script(SCRIPT_PATH, 'step-skip', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '1', '--reason', 'Already done')

        assert result.returncode == 0
        assert 'step_status: skipped' in result.stdout
        assert 'next_step: 2' in result.stdout
    finally:
        cleanup(temp_dir)


def test_step_skip_completes_task():
    """Skipping last step marks task as done."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'step-skip', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '1')

        assert result.returncode == 0
        assert 'task_status: done' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: add-step
# =============================================================================

def test_add_step_appends():
    """Add-step appends to end by default."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1', 'S2')

        result = run_script(SCRIPT_PATH, 'add-step', '--plan-id', 'test-plan',
                            '--task', '1', '--title', 'New Step')

        assert result.returncode == 0
        assert 'step: 3' in result.stdout

        # Verify step count
        get_result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')
        assert 'steps[3]' in get_result.stdout
    finally:
        cleanup(temp_dir)


def test_add_step_after():
    """Add-step inserts after specified position."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1', 'S3')

        result = run_script(SCRIPT_PATH, 'add-step', '--plan-id', 'test-plan',
                            '--task', '1', '--title', 'S2', '--after', '1')

        assert result.returncode == 0
        assert 'step: 2' in result.stdout

        # Verify order
        get_result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')
        assert '1,S1' in get_result.stdout
        assert '2,S2' in get_result.stdout
        assert '3,S3' in get_result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: remove-step
# =============================================================================

def test_remove_step():
    """Remove-step removes and renumbers."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1', 'S2', 'S3')

        result = run_script(SCRIPT_PATH, 'remove-step', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '2')

        assert result.returncode == 0
        assert 'Step 2 removed' in result.stdout

        # Verify renumbering
        get_result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')
        assert 'steps[2]' in get_result.stdout
        assert '1,S1' in get_result.stdout
        assert '2,S3' in get_result.stdout
    finally:
        cleanup(temp_dir)


def test_remove_step_last_fails():
    """Cannot remove the last step."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'remove-step', '--plan-id', 'test-plan',
                            '--task', '1', '--step', '1')

        assert result.returncode == 1
        assert 'Cannot remove the last step' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: update
# =============================================================================

def test_update_title_renames_file():
    """Updating title renames the file."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Old Title',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan',
                            '--number', '1', '--title', 'New Title')

        assert result.returncode == 0
        assert 'renamed: True' in result.stdout
        assert 'new-title' in result.stdout

        # Verify old file gone, new file exists
        task_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'tasks'
        old_files = list(task_dir.glob('*old-title*'))
        new_files = list(task_dir.glob('*new-title*'))
        assert len(old_files) == 0
        assert len(new_files) == 1
    finally:
        cleanup(temp_dir)


def test_update_specification():
    """Update specification reference."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan',
                            '--number', '1', '--specification', 'SPEC-2')

        assert result.returncode == 0
        assert 'SPEC-2' in result.stdout
    finally:
        cleanup(temp_dir)


def test_update_invalid_specification_fails():
    """Update with invalid specification format fails."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan',
                            '--number', '1', '--specification', 'INVALID')

        assert result.returncode == 1
        assert 'Invalid specification format' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: remove
# =============================================================================

def test_remove_deletes_file():
    """Remove deletes the task file."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'To Delete',
                   '--specification', 'SPEC-1', '--description', 'D', '--steps', 'S1')

        result = run_script(SCRIPT_PATH, 'remove', '--plan-id', 'test-plan', '--number', '1')

        assert result.returncode == 0
        assert 'status: success' in result.stdout
        assert 'total_tasks: 0' in result.stdout

        # Verify file gone
        task_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'tasks'
        files = list(task_dir.glob('TASK-*.toon'))
        assert len(files) == 0
    finally:
        cleanup(temp_dir)


def test_remove_preserves_gaps():
    """Removing a task preserves number gaps."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--specification', 'SPEC-1', '--description', 'D1', '--steps', 'S1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--specification', 'SPEC-2', '--description', 'D2', '--steps', 'S1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Third',
                   '--specification', 'SPEC-3', '--description', 'D3', '--steps', 'S1')

        # Remove middle
        run_script(SCRIPT_PATH, 'remove', '--plan-id', 'test-plan', '--number', '2')

        # Next add should be 4, not 2
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Fourth',
                            '--specification', 'SPEC-4', '--description', 'D4', '--steps', 'S1')

        assert 'TASK-004' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: progress tracking
# =============================================================================

def test_progress_calculation():
    """Progress is correctly calculated in list output."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--specification', 'SPEC-1', '--description', 'D',
                   '--steps', 'S1', 'S2', 'S3')
        run_script(SCRIPT_PATH, 'step-done', '--plan-id', 'test-plan', '--task', '1', '--step', '1')
        run_script(SCRIPT_PATH, 'step-skip', '--plan-id', 'test-plan', '--task', '1', '--step', '2')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert '2/3' in result.stdout  # 2 completed (done + skipped) out of 3
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: file content verification
# =============================================================================

def test_file_contains_specification_field():
    """Created file contains specification field."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Test task',
                   '--specification', 'SPEC-1',
                   '--description', 'Test description',
                   '--steps', 'Step 1', 'Step 2')

        task_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'tasks'
        files = list(task_dir.glob('TASK-001-*.toon'))
        content = files[0].read_text(encoding='utf-8')

        assert 'specification: SPEC-1' in content
        assert 'number: 1' in content
        assert 'status: pending' in content
        assert 'description: |' in content
        assert 'steps[2]{number,title,status}:' in content
        assert '1,Step 1,pending' in content
        assert '2,Step 2,pending' in content
        assert 'current_step: 1' in content
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: slug generation
# =============================================================================

def test_slug_special_characters():
    """Special characters are removed from slug."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Test@#$%Special!!!Characters',
                   '--specification', 'SPEC-1',
                   '--description', 'D',
                   '--steps', 'S1')

        task_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'tasks'
        files = list(task_dir.glob('TASK-001-*.toon'))
        assert len(files) == 1
        assert '@' not in files[0].name
        assert '#' not in files[0].name
    finally:
        cleanup(temp_dir)


def test_slug_truncation():
    """Long titles are truncated in slug."""
    temp_dir = setup_plan_dir()
    try:
        long_title = 'A' * 100
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', long_title,
                   '--specification', 'SPEC-1',
                   '--description', 'D',
                   '--steps', 'S1')

        task_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'tasks'
        files = list(task_dir.glob('TASK-001-*.toon'))
        assert len(files) == 1
        # Slug should be max 40 chars + TASK-001- prefix + .toon suffix
        slug_part = files[0].stem[9:]  # Remove 'TASK-001-'
        assert len(slug_part) <= 40
    finally:
        cleanup(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # add
        test_add_first_task,
        test_add_sequential_numbering,
        test_add_creates_slug_from_title,
        test_add_fails_without_specification,
        test_add_fails_with_invalid_specification_format,
        test_add_fails_without_steps,
        # get
        test_get_existing_task,
        test_get_nonexistent_returns_error,
        # list
        test_list_empty,
        test_list_with_tasks,
        test_list_filter_by_status,
        test_list_filter_by_specification,
        # next
        test_next_returns_first_pending,
        test_next_returns_in_progress_task,
        test_next_returns_null_when_all_done,
        test_next_empty_plan,
        test_next_include_context,
        test_next_include_context_no_spec,
        # step-start
        test_step_start_marks_in_progress,
        test_step_start_invalid_step,
        # step-done
        test_step_done_marks_completed,
        test_step_done_completes_task,
        # step-skip
        test_step_skip_marks_skipped,
        test_step_skip_completes_task,
        # add-step
        test_add_step_appends,
        test_add_step_after,
        # remove-step
        test_remove_step,
        test_remove_step_last_fails,
        # update
        test_update_title_renames_file,
        test_update_specification,
        test_update_invalid_specification_fails,
        # remove
        test_remove_deletes_file,
        test_remove_preserves_gaps,
        # progress
        test_progress_calculation,
        # file content
        test_file_contains_specification_field,
        # slug
        test_slug_special_characters,
        test_slug_truncation,
    ])
    sys.exit(runner.run())
