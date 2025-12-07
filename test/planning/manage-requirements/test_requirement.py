#!/usr/bin/env python3
"""Tests for requirement.py script."""

import os
import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'manage-requirements', 'manage-requirement.py')


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

def test_add_first_requirement():
    """Add first requirement creates REQ-001."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add',
                            '--plan-id', 'test-plan',
                            '--title', 'First requirement',
                            '--body', 'This is the body')

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert 'status: success' in result.stdout
        assert 'REQ-001' in result.stdout
        assert 'total_requirements: 1' in result.stdout

        # Verify file exists
        req_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'requirements'
        files = list(req_dir.glob('REQ-001-*.toon'))
        assert len(files) == 1, f"Expected 1 file, got {files}"
    finally:
        cleanup(temp_dir)


def test_add_sequential_numbering():
    """Adding multiple requirements gets sequential numbers."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First', '--body', 'Body 1')
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second', '--body', 'Body 2')

        assert result.returncode == 0
        assert 'REQ-002' in result.stdout
        assert 'total_requirements: 2' in result.stdout
    finally:
        cleanup(temp_dir)


def test_add_creates_slug_from_title():
    """Slug is generated from title."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Implement User Authentication!',
                   '--body', 'Details here')

        req_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'requirements'
        files = list(req_dir.glob('REQ-001-*.toon'))
        assert len(files) == 1
        assert 'implement-user-authentication' in files[0].name
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: get
# =============================================================================

def test_get_existing_requirement():
    """Get returns full requirement details."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Test requirement', '--body', 'Test body content')

        result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')

        assert result.returncode == 0
        assert 'status: success' in result.stdout
        assert 'number: 1' in result.stdout
        assert 'Test requirement' in result.stdout
        assert 'Test body content' in result.stdout
    finally:
        cleanup(temp_dir)


def test_get_nonexistent_returns_error():
    """Get nonexistent requirement returns error."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '99')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
        assert 'REQ-99' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: list
# =============================================================================

def test_list_empty():
    """List with no requirements shows zero counts."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 0' in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_with_requirements():
    """List shows all requirements in table format."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second', '--body', 'B2')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 2' in result.stdout
        assert 'requirements[2]' in result.stdout
        assert '1,First,pending' in result.stdout
        assert '2,Second,pending' in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_filter_by_status():
    """List can filter by status."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second', '--body', 'B2')
        run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'done')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan', '--status', 'pending')

        assert result.returncode == 0
        assert 'requirements[1]' in result.stdout
        assert '2,Second,pending' in result.stdout
        assert '1,First' not in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: check
# =============================================================================

def test_check_marks_done():
    """Check can mark requirement as done."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'done')

        assert result.returncode == 0
        assert 'status: done' in result.stdout
    finally:
        cleanup(temp_dir)


def test_check_marks_pending():
    """Check can mark requirement as pending."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task', '--body', 'Body')
        run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'done')

        result = run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'pending')

        assert result.returncode == 0
        assert 'status: pending' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: update
# =============================================================================

def test_update_title_renames_file():
    """Updating title renames the file."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Old Title', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan', '--number', '1', '--title', 'New Title')

        assert result.returncode == 0
        assert 'renamed: True' in result.stdout
        assert 'new-title' in result.stdout

        # Verify old file gone, new file exists
        req_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'requirements'
        old_files = list(req_dir.glob('*old-title*'))
        new_files = list(req_dir.glob('*new-title*'))
        assert len(old_files) == 0
        assert len(new_files) == 1
    finally:
        cleanup(temp_dir)


def test_update_body():
    """Update body without renaming file."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Title', '--body', 'Old body')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan', '--number', '1', '--body', 'New body content')

        assert result.returncode == 0
        assert 'renamed: False' in result.stdout

        # Verify body updated
        get_result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')
        assert 'New body content' in get_result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: remove
# =============================================================================

def test_remove_deletes_file():
    """Remove deletes the requirement file."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'To Delete', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'remove', '--plan-id', 'test-plan', '--number', '1')

        assert result.returncode == 0
        assert 'status: success' in result.stdout
        assert 'total_requirements: 0' in result.stdout

        # Verify file gone
        req_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'requirements'
        files = list(req_dir.glob('REQ-*.toon'))
        assert len(files) == 0
    finally:
        cleanup(temp_dir)


def test_remove_preserves_gaps():
    """Removing a requirement preserves number gaps."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second', '--body', 'B2')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Third', '--body', 'B3')

        # Remove middle
        run_script(SCRIPT_PATH, 'remove', '--plan-id', 'test-plan', '--number', '2')

        # Next add should be 4, not 2
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Fourth', '--body', 'B4')

        assert 'REQ-004' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: findAll
# =============================================================================

def test_find_all_returns_full_content():
    """FindAll returns all requirements with body."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First', '--body', 'Body one')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second', '--body', 'Body two')

        result = run_script(SCRIPT_PATH, 'findAll', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 2' in result.stdout
        assert 'Body one' in result.stdout
        assert 'Body two' in result.stdout
        assert 'created:' in result.stdout
        assert 'updated:' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: validate (NEW OPTIMIZATION)
# =============================================================================

def create_specification(temp_dir, plan_id, number, title, requirements):
    """Helper to create a specification file."""
    spec_dir = Path(temp_dir) / '.plan' / 'plans' / plan_id / 'specifications'
    spec_dir.mkdir(parents=True, exist_ok=True)
    slug = title.lower().replace(' ', '-')[:40]
    filename = f"SPEC-{number:03d}-{slug}.toon"
    content = f"""number: {number}
title: {title}
status: pending
created: 2024-01-01T00:00:00Z
updated: 2024-01-01T00:00:00Z
requirements: {requirements}

body: |
  Test specification body
"""
    (spec_dir / filename).write_text(content, encoding='utf-8')


def test_validate_all_covered():
    """Validate shows all requirements are covered."""
    temp_dir = setup_plan_dir()
    try:
        # Create requirements
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second', '--body', 'B2')

        # Create specifications covering them
        create_specification(temp_dir, 'test-plan', 1, 'Spec One', 'REQ-1')
        create_specification(temp_dir, 'test-plan', 2, 'Spec Two', 'REQ-2')

        result = run_script(SCRIPT_PATH, 'validate', '--plan-id', 'test-plan')

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert 'status: success' in result.stdout
        assert 'total_requirements:' in result.stdout
        assert 'covered:' in result.stdout
        assert 'uncovered: 0' in result.stdout
    finally:
        cleanup(temp_dir)


def test_validate_uncovered_requirements():
    """Validate shows uncovered requirements."""
    temp_dir = setup_plan_dir()
    try:
        # Create requirements
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second', '--body', 'B2')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Third', '--body', 'B3')

        # Only cover first requirement
        create_specification(temp_dir, 'test-plan', 1, 'Spec One', 'REQ-1')

        result = run_script(SCRIPT_PATH, 'validate', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'uncovered: 2' in result.stdout
        assert 'REQ-2' in result.stdout
        assert 'REQ-3' in result.stdout
    finally:
        cleanup(temp_dir)


def test_validate_empty():
    """Validate with no requirements."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'validate', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total_requirements: 0' in result.stdout
    finally:
        cleanup(temp_dir)


def test_validate_coverage_percentage():
    """Validate includes coverage percentage."""
    temp_dir = setup_plan_dir()
    try:
        # Create 4 requirements
        for i in range(1, 5):
            run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                       '--title', f'Req {i}', '--body', f'Body {i}')

        # Cover 2 of them (50%)
        create_specification(temp_dir, 'test-plan', 1, 'Spec One', 'REQ-1, REQ-2')

        result = run_script(SCRIPT_PATH, 'validate', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'coverage_percent: 50' in result.stdout
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
                   '--title', 'Test@#$%Special!!!Characters', '--body', 'Body')

        req_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'requirements'
        files = list(req_dir.glob('REQ-001-*.toon'))
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
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', long_title, '--body', 'Body')

        req_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'requirements'
        files = list(req_dir.glob('REQ-001-*.toon'))
        assert len(files) == 1
        # Slug should be max 40 chars + REQ-001- prefix + .toon suffix
        slug_part = files[0].stem[8:]  # Remove 'REQ-001-'
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
        test_add_first_requirement,
        test_add_sequential_numbering,
        test_add_creates_slug_from_title,
        # get
        test_get_existing_requirement,
        test_get_nonexistent_returns_error,
        # list
        test_list_empty,
        test_list_with_requirements,
        test_list_filter_by_status,
        # check
        test_check_marks_done,
        test_check_marks_pending,
        # update
        test_update_title_renames_file,
        test_update_body,
        # remove
        test_remove_deletes_file,
        test_remove_preserves_gaps,
        # findAll
        test_find_all_returns_full_content,
        # validate (optimization)
        test_validate_all_covered,
        test_validate_uncovered_requirements,
        test_validate_empty,
        test_validate_coverage_percentage,
        # slug
        test_slug_special_characters,
        test_slug_truncation,
    ])
    sys.exit(runner.run())
