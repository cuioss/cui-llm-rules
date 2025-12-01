#!/usr/bin/env python3
"""Tests for calculate-progress.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_file, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'plan-files', 'calculate-progress.py')


# =============================================================================
# Test Fixtures
# =============================================================================

BASIC_PROGRESS_PLAN = """# Task Plan: JWT Authentication

**Current Phase**: implement
**Current Task**: task-6

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 5 | 5/5 |
| refine | completed | 3 | 3/3 |
| implement | in_progress | 5 | 2/5 |
| verify | pending | 4 | 0/4 |
| finalize | pending | 3 | 0/3 |

---

### Task 1: Setup

**Phase**: init
**Goal**: Initial setup

**Checklist**:
- [x] Step 1
- [x] Step 2

### Task 6: Create JwtService

**Phase**: implement
**Goal**: Implement JWT

**Checklist**:
- [x] Create class
- [x] Add method
- [ ] Add config
- [ ] Write tests
"""

CHECKLIST_PLAN = """# Task Plan: Test

**Current Phase**: implement

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| implement | in_progress | 2 | 0/2 |

### Task 1: Task A

**Phase**: implement
**Goal**: First task

**Checklist**:
- [x] Item 1
- [x] Item 2
- [ ] Item 3

### Task 2: Task B

**Phase**: implement
**Goal**: Second task

**Checklist**:
- [ ] Item 1
- [ ] Item 2
"""

BY_PHASE_PLAN = """# Task Plan: Test

**Current Phase**: implement

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| implement | in_progress | 2 | 0/2 |

### Task 1: Init A

**Phase**: init

**Checklist**:
- [x] Done

### Task 2: Init B

**Phase**: init

**Checklist**:
- [x] Done

### Task 3: Implement A

**Phase**: implement

**Checklist**:
- [ ] Pending
- [ ] Pending

### Task 4: Implement B

**Phase**: implement

**Checklist**:
- [ ] Pending
"""

COMPLETED_PLAN = """# Task Plan: Completed

**Current Phase**: finalize

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| refine | completed | 1 | 1/1 |
| implement | completed | 2 | 2/2 |
| verify | completed | 1 | 1/1 |
| finalize | completed | 1 | 1/1 |

### Task 1: Done

**Phase**: init

**Checklist**:
- [x] Done
"""

EMPTY_PLAN = """# Task Plan: Empty

**Current Phase**: init

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | pending | 0 | 0/0 |
"""

CURRENT_PHASE_PLAN = """# Task Plan: Test

**Current Phase**: verify

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| implement | completed | 3 | 3/3 |
| verify | in_progress | 2 | 1/2 |
| finalize | pending | 1 | 0/1 |
"""


# =============================================================================
# Tests
# =============================================================================

def test_calculate_basic_progress():
    """Test calculating progress from a basic plan."""
    temp_file = create_temp_file(BASIC_PROGRESS_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        # Check overall progress
        assert data['overall']['total_tasks'] == 20  # 5+3+5+4+3
        assert data['overall']['completed_tasks'] == 10  # 5+3+2
        assert data['overall']['remaining_tasks'] == 10
        assert data['overall']['percentage'] == 50.0
        assert data['overall']['current_phase'] == 'implement'

        # Check phases
        assert len(data['phases']) == 5
        assert data['phases'][0]['phase'] == 'init'
        assert data['phases'][0]['percentage'] == 100.0
        assert data['phases'][2]['phase'] == 'implement'
        assert data['phases'][2]['percentage'] == 40.0

        # Check status
        assert data['status']['is_started'] is True
        assert data['status']['is_completed'] is False
        assert data['status']['phases_completed'] == 2
    finally:
        temp_file.unlink()


def test_calculate_checklist_progress():
    """Test calculating checklist-level progress."""
    temp_file = create_temp_file(CHECKLIST_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        # Check checklist progress
        assert data['checklist']['total_items'] == 5
        assert data['checklist']['completed_items'] == 2
        assert data['checklist']['remaining_items'] == 3
        assert data['checklist']['percentage'] == 40.0

        # Check task details
        assert len(data['tasks']) == 2
        assert data['tasks'][0]['checklist_completed'] == 2
        assert data['tasks'][0]['checklist_total'] == 3
        assert data['tasks'][1]['checklist_completed'] == 0
        assert data['tasks'][1]['checklist_total'] == 2
    finally:
        temp_file.unlink()


def test_calculate_progress_by_phase():
    """Test progress grouped by phase."""
    temp_file = create_temp_file(BY_PHASE_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        # Check by_phase grouping
        assert 'init' in data['by_phase']
        assert 'implement' in data['by_phase']

        assert data['by_phase']['init']['tasks'] == 2
        assert data['by_phase']['init']['checklist_completed'] == 2
        assert data['by_phase']['init']['checklist_total'] == 2

        assert data['by_phase']['implement']['tasks'] == 2
        assert data['by_phase']['implement']['checklist_completed'] == 0
        assert data['by_phase']['implement']['checklist_total'] == 3
    finally:
        temp_file.unlink()


def test_calculate_completed_plan():
    """Test progress for a fully completed plan."""
    temp_file = create_temp_file(COMPLETED_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert data['overall']['percentage'] == 100.0
        assert data['overall']['remaining_tasks'] == 0
        assert data['status']['is_completed'] is True
        assert data['status']['phases_completed'] == 5
        assert data['status']['phases_total'] == 5
    finally:
        temp_file.unlink()


def test_calculate_empty_plan():
    """Test progress for an empty/new plan."""
    temp_file = create_temp_file(EMPTY_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert data['overall']['total_tasks'] == 0
        assert data['overall']['percentage'] == 0
        assert data['checklist']['total_items'] == 0
        assert data['status']['is_started'] is False
        assert data['status']['is_completed'] is False
    finally:
        temp_file.unlink()


def test_file_not_found():
    """Test error handling for missing file."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path/plan.md')
    assert not result.success
    assert result.returncode == 1

    data = result.json()
    assert 'error' in data
    assert data['error']['type'] == 'file_not_found'


def test_calculate_current_phase_detection():
    """Test that current phase is correctly detected."""
    temp_file = create_temp_file(CURRENT_PHASE_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert data['overall']['current_phase'] == 'verify'
    finally:
        temp_file.unlink()


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_calculate_basic_progress,
        test_calculate_checklist_progress,
        test_calculate_progress_by_phase,
        test_calculate_completed_plan,
        test_calculate_empty_plan,
        test_file_not_found,
        test_calculate_current_phase_detection,
    ])
    sys.exit(runner.run())
