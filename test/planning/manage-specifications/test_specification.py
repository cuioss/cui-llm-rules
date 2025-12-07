#!/usr/bin/env python3
"""Tests for specification.py script."""

import os
import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'manage-specifications', 'manage-specification.py')


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

def test_add_first_specification():
    """Add first specification creates SPEC-001."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add',
                            '--plan-id', 'test-plan',
                            '--title', 'First specification',
                            '--requirements', 'REQ-1',
                            '--body', 'This is the body')

        assert result.returncode == 0, f"Failed: {result.stderr}"
        assert 'status: success' in result.stdout
        assert 'SPEC-001' in result.stdout
        assert 'total_specifications: 1' in result.stdout

        # Verify file exists
        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        files = list(spec_dir.glob('SPEC-001-*.toon'))
        assert len(files) == 1, f"Expected 1 file, got {files}"
    finally:
        cleanup(temp_dir)


def test_add_sequential_numbering():
    """Adding multiple specifications gets sequential numbers."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1', '--body', 'Body 1')
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                            '--requirements', 'REQ-2', '--body', 'Body 2')

        assert result.returncode == 0
        assert 'SPEC-002' in result.stdout
        assert 'total_specifications: 2' in result.stdout
    finally:
        cleanup(temp_dir)


def test_add_creates_slug_from_title():
    """Slug is generated from title."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'JWT Token Format!',
                   '--requirements', 'REQ-1',
                   '--body', 'Details here')

        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        files = list(spec_dir.glob('SPEC-001-*.toon'))
        assert len(files) == 1
        assert 'jwt-token-format' in files[0].name
    finally:
        cleanup(temp_dir)


def test_add_multiple_requirements():
    """Add specification with multiple requirements."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                            '--title', 'Multi-req spec',
                            '--requirements', 'REQ-1,REQ-3,REQ-5',
                            '--body', 'Body')

        assert result.returncode == 0
        assert 'REQ-1, REQ-3, REQ-5' in result.stdout
    finally:
        cleanup(temp_dir)


def test_add_fails_without_requirements():
    """Add fails if no requirements specified."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                            '--title', 'No reqs',
                            '--requirements', '',
                            '--body', 'Body')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
        assert 'requirement' in result.stderr.lower()
    finally:
        cleanup(temp_dir)


def test_add_fails_with_invalid_requirement_format():
    """Add fails with invalid requirement format."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                            '--title', 'Bad format',
                            '--requirements', 'REQUIREMENT-1',
                            '--body', 'Body')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
        assert 'Invalid requirement format' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: get
# =============================================================================

def test_get_existing_specification():
    """Get returns full specification details."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Test specification',
                   '--requirements', 'REQ-1,REQ-2',
                   '--body', 'Test body content')

        result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')

        assert result.returncode == 0
        assert 'status: success' in result.stdout
        assert 'number: 1' in result.stdout
        assert 'Test specification' in result.stdout
        assert 'REQ-1, REQ-2' in result.stdout
        assert 'Test body content' in result.stdout
    finally:
        cleanup(temp_dir)


def test_get_nonexistent_returns_error():
    """Get nonexistent specification returns error."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '99')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
        assert 'SPEC-99' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: list
# =============================================================================

def test_list_empty():
    """List with no specifications shows zero counts."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 0' in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_with_specifications():
    """List shows all specifications in table format."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--requirements', 'REQ-2', '--body', 'B2')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 2' in result.stdout
        assert 'specifications[2]' in result.stdout
        assert '1,First,REQ-1,pending' in result.stdout
        assert '2,Second,REQ-2,pending' in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_filter_by_status():
    """List can filter by status."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--requirements', 'REQ-2', '--body', 'B2')
        run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'done')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan', '--status', 'pending')

        assert result.returncode == 0
        assert 'specifications[1]' in result.stdout
        assert '2,Second,REQ-2,pending' in result.stdout
        assert '1,First' not in result.stdout
    finally:
        cleanup(temp_dir)


def test_list_filter_by_requirement():
    """List can filter by requirement reference."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1,REQ-2', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--requirements', 'REQ-2', '--body', 'B2')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Third',
                   '--requirements', 'REQ-3', '--body', 'B3')

        result = run_script(SCRIPT_PATH, 'list', '--plan-id', 'test-plan', '--requirement', 'REQ-2')

        assert result.returncode == 0
        assert 'total: 2' in result.stdout
        assert 'First' in result.stdout
        assert 'Second' in result.stdout
        assert 'Third' not in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: check
# =============================================================================

def test_check_marks_done():
    """Check can mark specification as done."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--requirements', 'REQ-1', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'done')

        assert result.returncode == 0
        assert 'status: done' in result.stdout
    finally:
        cleanup(temp_dir)


def test_check_marks_pending():
    """Check can mark specification as pending."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Task',
                   '--requirements', 'REQ-1', '--body', 'Body')
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
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Old Title',
                   '--requirements', 'REQ-1', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan', '--number', '1', '--title', 'New Title')

        assert result.returncode == 0
        assert 'renamed: True' in result.stdout
        assert 'new-title' in result.stdout

        # Verify old file gone, new file exists
        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        old_files = list(spec_dir.glob('*old-title*'))
        new_files = list(spec_dir.glob('*new-title*'))
        assert len(old_files) == 0
        assert len(new_files) == 1
    finally:
        cleanup(temp_dir)


def test_update_body():
    """Update body without renaming file."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Title',
                   '--requirements', 'REQ-1', '--body', 'Old body')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan', '--number', '1', '--body', 'New body content')

        assert result.returncode == 0
        assert 'renamed: False' in result.stdout

        # Verify body updated
        get_result = run_script(SCRIPT_PATH, 'get', '--plan-id', 'test-plan', '--number', '1')
        assert 'New body content' in get_result.stdout
    finally:
        cleanup(temp_dir)


def test_update_requirements():
    """Update requirements."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Title',
                   '--requirements', 'REQ-1', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan', '--number', '1',
                            '--requirements', 'REQ-1,REQ-2,REQ-3')

        assert result.returncode == 0
        assert 'REQ-1, REQ-2, REQ-3' in result.stdout
    finally:
        cleanup(temp_dir)


def test_update_requirements_invalid_format_fails():
    """Update with invalid requirement format fails."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Title',
                   '--requirements', 'REQ-1', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'update', '--plan-id', 'test-plan', '--number', '1',
                            '--requirements', 'INVALID-REQ')

        assert result.returncode == 1
        assert 'error' in result.stderr.lower()
        assert 'Invalid requirement format' in result.stderr
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: remove
# =============================================================================

def test_remove_deletes_file():
    """Remove deletes the specification file."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'To Delete',
                   '--requirements', 'REQ-1', '--body', 'Body')

        result = run_script(SCRIPT_PATH, 'remove', '--plan-id', 'test-plan', '--number', '1')

        assert result.returncode == 0
        assert 'status: success' in result.stdout
        assert 'total_specifications: 0' in result.stdout

        # Verify file gone
        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        files = list(spec_dir.glob('SPEC-*.toon'))
        assert len(files) == 0
    finally:
        cleanup(temp_dir)


def test_remove_preserves_gaps():
    """Removing a specification preserves number gaps."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--requirements', 'REQ-2', '--body', 'B2')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Third',
                   '--requirements', 'REQ-3', '--body', 'B3')

        # Remove middle
        run_script(SCRIPT_PATH, 'remove', '--plan-id', 'test-plan', '--number', '2')

        # Next add should be 4, not 2
        result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Fourth',
                            '--requirements', 'REQ-4', '--body', 'B4')

        assert 'SPEC-004' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: findAll
# =============================================================================

def test_find_all_returns_full_content():
    """FindAll returns all specifications with body."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1', '--body', 'Body one')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--requirements', 'REQ-2', '--body', 'Body two')

        result = run_script(SCRIPT_PATH, 'findAll', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total: 2' in result.stdout
        assert 'Body one' in result.stdout
        assert 'Body two' in result.stdout
        assert 'created:' in result.stdout
        assert 'updated:' in result.stdout
        assert 'requirements: REQ-1' in result.stdout
        assert 'requirements: REQ-2' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: findByRequirement
# =============================================================================

def test_find_by_requirement():
    """FindByRequirement returns matching specifications."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1,REQ-2', '--body', 'B1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Second',
                   '--requirements', 'REQ-2', '--body', 'B2')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'Third',
                   '--requirements', 'REQ-3', '--body', 'B3')
        run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'done')

        result = run_script(SCRIPT_PATH, 'findByRequirement', '--plan-id', 'test-plan', '--requirement', 'REQ-2')

        assert result.returncode == 0
        assert 'requirement: REQ-2' in result.stdout
        assert 'total: 2' in result.stdout
        assert 'pending: 1' in result.stdout
        assert 'done: 1' in result.stdout
        assert 'First' in result.stdout
        assert 'Second' in result.stdout
        assert 'Third' not in result.stdout
    finally:
        cleanup(temp_dir)


def test_find_by_requirement_no_matches():
    """FindByRequirement with no matches returns empty."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan', '--title', 'First',
                   '--requirements', 'REQ-1', '--body', 'B1')

        result = run_script(SCRIPT_PATH, 'findByRequirement', '--plan-id', 'test-plan', '--requirement', 'REQ-99')

        assert result.returncode == 0
        assert 'total: 0' in result.stdout
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
                   '--requirements', 'REQ-1',
                   '--body', 'Body')

        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        files = list(spec_dir.glob('SPEC-001-*.toon'))
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
                   '--requirements', 'REQ-1',
                   '--body', 'Body')

        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        files = list(spec_dir.glob('SPEC-001-*.toon'))
        assert len(files) == 1
        # Slug should be max 40 chars + SPEC-001- prefix + .toon suffix
        slug_part = files[0].stem[9:]  # Remove 'SPEC-001-'
        assert len(slug_part) <= 40
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: get-traceability-map
# =============================================================================

def test_get_traceability_map_single_spec():
    """Get traceability map with one specification."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'First spec',
                   '--requirements', 'REQ-1',
                   '--body', 'Body 1')

        result = run_script(SCRIPT_PATH, 'get-traceability-map', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'status: success' in result.stdout
        # REQ to SPEC mapping
        assert 'REQ-1' in result.stdout
        assert 'SPEC-1' in result.stdout
    finally:
        cleanup(temp_dir)


def test_get_traceability_map_multiple_specs_multiple_reqs():
    """Get traceability map with multiple specs and requirements."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'First spec',
                   '--requirements', 'REQ-1,REQ-2',
                   '--body', 'Body 1')
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Second spec',
                   '--requirements', 'REQ-2,REQ-3',
                   '--body', 'Body 2')

        result = run_script(SCRIPT_PATH, 'get-traceability-map', '--plan-id', 'test-plan')

        assert result.returncode == 0
        # All requirements should appear
        assert 'REQ-1' in result.stdout
        assert 'REQ-2' in result.stdout
        assert 'REQ-3' in result.stdout
        # Both specs should appear
        assert 'SPEC-1' in result.stdout
        assert 'SPEC-2' in result.stdout
        # Should have totals
        assert 'total_requirements:' in result.stdout
        assert 'total_specifications:' in result.stdout
    finally:
        cleanup(temp_dir)


def test_get_traceability_map_empty():
    """Get traceability map with no specifications."""
    temp_dir = setup_plan_dir()
    try:
        result = run_script(SCRIPT_PATH, 'get-traceability-map', '--plan-id', 'test-plan')

        assert result.returncode == 0
        assert 'total_requirements: 0' in result.stdout
        assert 'total_specifications: 0' in result.stdout
    finally:
        cleanup(temp_dir)


def test_get_traceability_map_includes_coverage():
    """Get traceability map includes coverage statistics."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'First spec',
                   '--requirements', 'REQ-1',
                   '--body', 'Body 1')
        run_script(SCRIPT_PATH, 'check', '--plan-id', 'test-plan', '--number', '1', '--status', 'done')

        result = run_script(SCRIPT_PATH, 'get-traceability-map', '--plan-id', 'test-plan')

        assert result.returncode == 0
        # Should have status counts
        assert 'pending:' in result.stdout or 'done:' in result.stdout
    finally:
        cleanup(temp_dir)


# =============================================================================
# Tests: file content verification
# =============================================================================

def test_file_contains_requirements_field():
    """Created file contains requirements field."""
    temp_dir = setup_plan_dir()
    try:
        run_script(SCRIPT_PATH, 'add', '--plan-id', 'test-plan',
                   '--title', 'Test spec',
                   '--requirements', 'REQ-1,REQ-3',
                   '--body', 'Test body')

        spec_dir = Path(os.environ['PLAN_BASE_DIR']) / 'plans' / 'test-plan' / 'specifications'
        files = list(spec_dir.glob('SPEC-001-*.toon'))
        content = files[0].read_text(encoding='utf-8')

        assert 'requirements: REQ-1, REQ-3' in content
        assert 'number: 1' in content
        assert 'status: pending' in content
        assert 'body: |' in content
    finally:
        cleanup(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # add
        test_add_first_specification,
        test_add_sequential_numbering,
        test_add_creates_slug_from_title,
        test_add_multiple_requirements,
        test_add_fails_without_requirements,
        test_add_fails_with_invalid_requirement_format,
        # get
        test_get_existing_specification,
        test_get_nonexistent_returns_error,
        # list
        test_list_empty,
        test_list_with_specifications,
        test_list_filter_by_status,
        test_list_filter_by_requirement,
        # check
        test_check_marks_done,
        test_check_marks_pending,
        # update
        test_update_title_renames_file,
        test_update_body,
        test_update_requirements,
        test_update_requirements_invalid_format_fails,
        # remove
        test_remove_deletes_file,
        test_remove_preserves_gaps,
        # findAll
        test_find_all_returns_full_content,
        # findByRequirement
        test_find_by_requirement,
        test_find_by_requirement_no_matches,
        # slug
        test_slug_special_characters,
        test_slug_truncation,
        # file content
        test_file_contains_requirements_field,
        # get-traceability-map
        test_get_traceability_map_single_spec,
        test_get_traceability_map_multiple_specs_multiple_reqs,
        test_get_traceability_map_empty,
        test_get_traceability_map_includes_coverage,
    ])
    sys.exit(runner.run())
