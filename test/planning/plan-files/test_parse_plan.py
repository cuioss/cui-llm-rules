#!/usr/bin/env python3
"""Tests for parse-plan.py script."""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_file, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'plan-files', 'parse-plan.py')


# =============================================================================
# Test Fixtures
# =============================================================================

BASIC_PLAN = """# Task Plan: JWT Authentication

**Configuration**: See [config.md](./config.md)
**References**: See [references.md](./references.md)

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

## Phase: init (completed)

### Task 1: Detect Environment

**Phase**: init
**Goal**: Gather information from command parameters

**Acceptance Criteria**:
- Build system identified
- Technology stack determined

**Checklist**:
- [x] Check current git branch
- [x] Detect build system

### Task 2: Fetch Issue Details

**Phase**: init
**Goal**: Retrieve issue information

**Acceptance Criteria**:
- Issue title available

**Checklist**:
- [x] Fetch issue title
- [x] Extract acceptance criteria

## Phase: implement (in_progress)

### Task 6: Create JwtService

**Phase**: implement
**Goal**: Implement JWT token generation service

**Acceptance Criteria**:
- Service generates valid JWT tokens
- Tokens include standard claims

**Checklist**:
- [x] Create JwtService class
- [x] Implement generateToken method
- [ ] Add token configuration
- [ ] Write unit tests

## Completion Criteria

All phases must be completed.
"""

EMPTY_PLAN = """# Task Plan: Empty

**Current Phase**: init
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | pending | 0 | 0/0 |
"""

COMPLETED_PLAN = """# Task Plan: Completed Feature

**Current Phase**: finalize
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| refine | completed | 1 | 1/1 |
| implement | completed | 2 | 2/2 |
| verify | completed | 1 | 1/1 |
| finalize | completed | 1 | 1/1 |

### Task 1: Setup

**Phase**: init
**Goal**: Initial setup

**Checklist**:
- [x] Done

### Task 2: Config

**Phase**: init
**Goal**: Configuration

**Checklist**:
- [x] Done
"""

ACCEPTANCE_CRITERIA_PLAN = """# Task Plan: Test

**Current Phase**: implement
**Current Task**: task-1

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| implement | in_progress | 1 | 0/1 |

### Task 1: Implement Feature

**Phase**: implement
**Goal**: Build the feature

**Acceptance Criteria**:
- Criterion one
- Criterion two
- Criterion three

**Checklist**:
- [ ] Step one
- [ ] Step two
"""

GROUPED_TASKS_PLAN = """# Task Plan: Grouped

**Current Phase**: implement
**Current Task**: task-3

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| implement | in_progress | 2 | 0/2 |

### Task 1: Init Task A

**Phase**: init
**Goal**: First init task

**Checklist**:
- [x] Done

### Task 2: Init Task B

**Phase**: init
**Goal**: Second init task

**Checklist**:
- [x] Done

### Task 3: Implement Task A

**Phase**: implement
**Goal**: First implement task

**Checklist**:
- [ ] Pending

### Task 4: Implement Task B

**Phase**: implement
**Goal**: Second implement task

**Checklist**:
- [ ] Pending
"""


# =============================================================================
# Tests
# =============================================================================

def test_parse_basic_plan():
    """Test parsing a basic plan with all sections."""
    temp_file = create_temp_file(BASIC_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        # Check title
        assert data['title'] == 'JWT Authentication'

        # Check plan status
        assert data['plan_status']['current_phase'] == 'implement'
        assert data['plan_status']['current_task'] == 'task-6'
        assert data['plan_status']['overall_status'] == 'in_progress'

        # Check phases
        assert len(data['phases']) == 5
        assert data['phases'][0]['name'] == 'init'
        assert data['phases'][0]['status'] == 'completed'
        assert data['phases'][0]['tasks_completed'] == 5
        assert data['phases'][2]['name'] == 'implement'
        assert data['phases'][2]['status'] == 'in_progress'

        # Check tasks
        assert len(data['tasks']) == 3
        assert data['tasks'][0]['id'] == 1
        assert data['tasks'][0]['name'] == 'Detect Environment'
        assert data['tasks'][0]['status'] == 'completed'

        # Check task 6 (in progress)
        task_6 = next(t for t in data['tasks'] if t['id'] == 6)
        assert task_6['status'] == 'in_progress'
        assert task_6['checklist_completed'] == 2
        assert task_6['checklist_total'] == 4

        # Check summary
        assert data['summary']['total_tasks'] == 3
        assert data['summary']['completed_tasks'] == 2
    finally:
        temp_file.unlink()


def test_parse_empty_plan():
    """Test parsing an empty plan."""
    temp_file = create_temp_file(EMPTY_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert data['title'] == 'Empty'
        assert data['plan_status']['current_phase'] == 'init'
        assert len(data['tasks']) == 0
        assert data['summary']['total_tasks'] == 0
    finally:
        temp_file.unlink()


def test_parse_completed_plan():
    """Test parsing a fully completed plan."""
    temp_file = create_temp_file(COMPLETED_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert data['plan_status']['overall_status'] == 'completed'
        assert all(p['status'] == 'completed' for p in data['phases'])
    finally:
        temp_file.unlink()


def test_parse_acceptance_criteria():
    """Test parsing acceptance criteria from tasks."""
    temp_file = create_temp_file(ACCEPTANCE_CRITERIA_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        task = data['tasks'][0]
        assert len(task['acceptance_criteria']) == 3
        assert task['acceptance_criteria'][0] == 'Criterion one'
        assert task['acceptance_criteria'][2] == 'Criterion three'
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


def test_tasks_by_phase():
    """Test that tasks are correctly grouped by phase."""
    temp_file = create_temp_file(GROUPED_TASKS_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_file))
        assert result.success
        data = result.json()

        assert 'init' in data['tasks_by_phase']
        assert 'implement' in data['tasks_by_phase']
        assert len(data['tasks_by_phase']['init']) == 2
        assert len(data['tasks_by_phase']['implement']) == 2
    finally:
        temp_file.unlink()


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_parse_basic_plan,
        test_parse_empty_plan,
        test_parse_completed_plan,
        test_parse_acceptance_criteria,
        test_file_not_found,
        test_tasks_by_phase,
    ])
    sys.exit(runner.run())
