#!/usr/bin/env python3
"""Tests for transition-phase.py script."""

import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-task-workflow', 'phase-management', 'transition-phase.py')


# =============================================================================
# Test Fixtures
# =============================================================================

PLAN_INIT_COMPLETE = """# Task Plan: Test

**Current Phase**: init
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 2/2 |
| refine | pending | 3 | 0/3 |
| implement | pending | 5 | 0/5 |
| verify | pending | 2 | 0/2 |
| finalize | pending | 1 | 0/1 |

## Phase: init (in_progress)

### Task 1: Setup

**Phase**: init
**Goal**: Initial setup

**Checklist**:
- [x] Step 1
- [x] Step 2

### Task 2: Config

**Phase**: init
**Goal**: Configuration

**Checklist**:
- [x] Done
"""

PLAN_INIT_INCOMPLETE = """# Task Plan: Test

**Current Phase**: init
**Current Task**: task-1

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 1/2 |
| refine | pending | 3 | 0/3 |

## Phase: init (in_progress)

### Task 1: Setup

**Phase**: init
**Goal**: Setup

**Checklist**:
- [x] Done

### Task 2: Config

**Phase**: init
**Goal**: Config

**Checklist**:
- [ ] Pending
"""

PLAN_IMPLEMENT_COMPLETE = """# Task Plan: Test

**Current Phase**: implement
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 1 | 1/1 |
| refine | completed | 1 | 1/1 |
| implement | in_progress | 2 | 2/2 |
| verify | pending | 2 | 0/2 |
| finalize | pending | 1 | 0/1 |

## Phase: implement (in_progress)

### Task 1: Code

**Phase**: implement
**Goal**: Write code

**Checklist**:
- [x] Done

### Task 2: More Code

**Phase**: implement
**Goal**: More code

**Checklist**:
- [x] Done
"""

PLAN_FINALIZE_COMPLETE = """# Task Plan: Test

**Current Phase**: finalize
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 1 | 1/1 |
| refine | completed | 1 | 1/1 |
| implement | completed | 1 | 1/1 |
| verify | completed | 1 | 1/1 |
| finalize | in_progress | 1 | 1/1 |

## Phase: finalize (in_progress)

### Task 1: PR

**Phase**: finalize
**Goal**: Create PR

**Checklist**:
- [x] Done
"""

PLAN_REFINE_MISMATCH = """# Task Plan: Test

**Current Phase**: refine
**Current Task**: task-2

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 1 | 1/1 |
| refine | in_progress | 2 | 2/2 |

## Phase: refine (in_progress)

### Task 1: Analyze

**Phase**: refine
**Goal**: Analysis

**Checklist**:
- [x] Done

### Task 2: Plan

**Phase**: refine
**Goal**: Planning

**Checklist**:
- [x] Done
"""

# Plugin-development plan (4-phase: init -> refine -> execute -> finalize)
PLAN_PLUGIN_DEV_EXECUTE_COMPLETE = """# Task Plan: Test Plugin Dev

**Current Phase**: execute
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 1 | 1/1 |
| refine | completed | 1 | 1/1 |
| execute | in_progress | 1 | 1/1 |
| finalize | pending | 1 | 0/1 |

## Phase: execute (in_progress)

### Task 1: Implement

**Phase**: execute
**Goal**: Implementation

**Checklist**:
- [x] Done
"""

CONFIG_PLUGIN_DEV = """# Plan Configuration

plan_type: plugin-development
branch: test-branch
"""

# Simple plan (3-phase: init -> execute -> finalize)
PLAN_SIMPLE_EXECUTE_COMPLETE = """# Task Plan: Test Simple

**Current Phase**: execute
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 1 | 1/1 |
| execute | in_progress | 1 | 1/1 |
| finalize | pending | 1 | 0/1 |

## Phase: execute (in_progress)

### Task 1: Do Task

**Phase**: execute
**Goal**: Execute task

**Checklist**:
- [x] Done
"""

CONFIG_SIMPLE = """# Plan Configuration

plan_type: simple
branch: test-branch
"""


# =============================================================================
# Test Helpers
# =============================================================================

def create_plan_dir(base_dir: Path, content: str, config: str = None) -> Path:
    """Create a plan directory with plan.md and optional config.toon."""
    plan_dir = base_dir / 'test-plan'
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / 'plan.md').write_text(content)
    if config:
        (plan_dir / 'config.toon').write_text(config)
    return plan_dir


# =============================================================================
# Tests - Valid Transitions
# =============================================================================

def test_transition_init_to_refine():
    """Test valid transition from init to refine."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_INIT_COMPLETE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'init')
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        assert data['transition']['from_phase'] == 'init'
        assert data['transition']['to_phase'] == 'refine'
        assert data['transition']['success'] is True
        assert data['transition']['plan_complete'] is False
        assert data['plan_status']['current_phase'] == 'refine'
    finally:
        shutil.rmtree(temp_dir)


def test_transition_implement_to_verify():
    """Test valid transition from implement to verify."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_IMPLEMENT_COMPLETE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'implement')
        assert result.success
        data = result.json()

        assert data['transition']['from_phase'] == 'implement'
        assert data['transition']['to_phase'] == 'verify'
        assert data['transition']['success'] is True
    finally:
        shutil.rmtree(temp_dir)


def test_transition_finalize_completes_plan():
    """Test that completing finalize marks plan as complete."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_FINALIZE_COMPLETE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'finalize')
        assert result.success
        data = result.json()

        assert data['transition']['from_phase'] == 'finalize'
        assert data['transition']['to_phase'] is None
        assert data['transition']['plan_complete'] is True
        assert data['plan_status']['status'] == 'completed'
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Tests - Invalid Transitions
# =============================================================================

def test_transition_incomplete_phase():
    """Test that incomplete phase cannot transition."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_INIT_INCOMPLETE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'init')
        assert not result.success
        data = result.json()

        assert 'error' in data
        assert data['error']['type'] == 'incomplete_phase'
        assert data['error']['tasks_remaining'] > 0
    finally:
        shutil.rmtree(temp_dir)


def test_transition_phase_mismatch():
    """Test error when completed_phase doesn't match current."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_REFINE_MISMATCH)

        # Try to complete init when current is refine
        result = run_script(SCRIPT_PATH, str(plan_dir), 'init')
        assert not result.success
        data = result.json()

        assert 'error' in data
        assert data['error']['type'] == 'phase_mismatch'
    finally:
        shutil.rmtree(temp_dir)


def test_transition_invalid_phase():
    """Test error for invalid phase name."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_INIT_COMPLETE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'invalid_phase')
        assert not result.success
        data = result.json()

        assert 'error' in data
        assert data['error']['type'] == 'invalid_phase'
    finally:
        shutil.rmtree(temp_dir)


def test_transition_plan_not_found():
    """Test error when plan directory doesn't exist."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path', 'init')
    assert not result.success
    data = result.json()

    assert 'error' in data
    assert data['error']['type'] == 'plan_not_found'


# =============================================================================
# Tests - Output Structure
# =============================================================================

def test_transition_output_structure():
    """Test that output contains expected fields."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_INIT_COMPLETE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'init')
        assert result.success
        data = result.json()

        # Check required fields
        assert 'transition' in data
        assert 'plan_status' in data
        assert 'next_action' in data

        transition = data['transition']
        assert 'from_phase' in transition
        assert 'to_phase' in transition
        assert 'success' in transition
        assert 'plan_complete' in transition
    finally:
        shutil.rmtree(temp_dir)


def test_transition_help_output():
    """Test --help output."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0
    assert 'Phase order' in result.stdout
    assert 'implementation' in result.stdout
    assert 'simple' in result.stdout


# =============================================================================
# Tests - All Phase Transitions
# =============================================================================

def test_all_standard_transitions():
    """Test all standard phase transitions produce correct next phase."""
    transitions = [
        ('init', 'refine'),
        ('refine', 'implement'),
        ('implement', 'verify'),
        ('verify', 'finalize'),
    ]

    for current, expected_next in transitions:
        temp_dir = create_temp_dir()
        try:
            # Create a plan that's complete for the current phase
            plan_content = f"""# Task Plan: Test

**Current Phase**: {current}
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| {current} | in_progress | 1 | 1/1 |

## Phase: {current} (in_progress)

### Task 1: Test

**Phase**: {current}
**Goal**: Test

**Checklist**:
- [x] Done
"""
            plan_dir = create_plan_dir(temp_dir, plan_content)
            result = run_script(SCRIPT_PATH, str(plan_dir), current)

            assert result.success, f"Failed for {current} -> {expected_next}: {result.stderr}"
            data = result.json()
            assert data['transition']['to_phase'] == expected_next, f"Expected {expected_next}, got {data['transition']['to_phase']}"
        finally:
            shutil.rmtree(temp_dir)


# =============================================================================
# Tests - Plugin-Development Plan Type (4-phase)
# =============================================================================

def test_plugin_dev_execute_to_finalize():
    """Test plugin-development plan transitions from execute to finalize."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_PLUGIN_DEV_EXECUTE_COMPLETE, CONFIG_PLUGIN_DEV)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'execute')
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        assert data['transition']['from_phase'] == 'execute'
        assert data['transition']['to_phase'] == 'finalize'
        assert data['transition']['success'] is True
        assert data['plan_status']['plan_type'] == 'plugin-development'
    finally:
        shutil.rmtree(temp_dir)


def test_plugin_dev_rejects_implement_phase():
    """Test plugin-development plan rejects 'implement' as invalid phase."""
    temp_dir = create_temp_dir()
    try:
        # Create plan that claims to be in 'implement' phase but is plugin-development type
        plan_content = """# Task Plan: Test

**Current Phase**: implement
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| implement | in_progress | 1 | 1/1 |

## Phase: implement (in_progress)

### Task 1: Test

**Phase**: implement
**Goal**: Test

**Checklist**:
- [x] Done
"""
        plan_dir = create_plan_dir(temp_dir, plan_content, CONFIG_PLUGIN_DEV)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'implement')
        assert not result.success, "Expected failure for invalid phase"
        data = result.json()

        assert 'error' in data
        assert data['error']['type'] == 'invalid_phase'
        assert 'plugin-development' in str(data['error'])
    finally:
        shutil.rmtree(temp_dir)


def test_plugin_dev_rejects_verify_phase():
    """Test plugin-development plan rejects 'verify' as invalid phase."""
    temp_dir = create_temp_dir()
    try:
        plan_content = """# Task Plan: Test

**Current Phase**: verify
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| verify | in_progress | 1 | 1/1 |

## Phase: verify (in_progress)

### Task 1: Test

**Phase**: verify
**Goal**: Test

**Checklist**:
- [x] Done
"""
        plan_dir = create_plan_dir(temp_dir, plan_content, CONFIG_PLUGIN_DEV)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'verify')
        assert not result.success, "Expected failure for invalid phase"
        data = result.json()

        assert 'error' in data
        assert data['error']['type'] == 'invalid_phase'
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Tests - Simple Plan Type (3-phase)
# =============================================================================

def test_simple_execute_to_finalize():
    """Test simple plan transitions from execute to finalize."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_plan_dir(temp_dir, PLAN_SIMPLE_EXECUTE_COMPLETE, CONFIG_SIMPLE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'execute')
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        assert data['transition']['from_phase'] == 'execute'
        assert data['transition']['to_phase'] == 'finalize'
        assert data['transition']['success'] is True
        assert data['plan_status']['plan_type'] == 'simple'
    finally:
        shutil.rmtree(temp_dir)


def test_simple_rejects_refine_phase():
    """Test simple plan rejects 'refine' as invalid phase."""
    temp_dir = create_temp_dir()
    try:
        plan_content = """# Task Plan: Test

**Current Phase**: refine
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| refine | in_progress | 1 | 1/1 |

## Phase: refine (in_progress)

### Task 1: Test

**Phase**: refine
**Goal**: Test

**Checklist**:
- [x] Done
"""
        plan_dir = create_plan_dir(temp_dir, plan_content, CONFIG_SIMPLE)

        result = run_script(SCRIPT_PATH, str(plan_dir), 'refine')
        assert not result.success, "Expected failure for invalid phase"
        data = result.json()

        assert 'error' in data
        assert data['error']['type'] == 'invalid_phase'
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_transition_init_to_refine,
        test_transition_implement_to_verify,
        test_transition_finalize_completes_plan,
        test_transition_incomplete_phase,
        test_transition_phase_mismatch,
        test_transition_invalid_phase,
        test_transition_plan_not_found,
        test_transition_output_structure,
        test_transition_help_output,
        test_all_standard_transitions,
        # Plugin-development plan tests
        test_plugin_dev_execute_to_finalize,
        test_plugin_dev_rejects_implement_phase,
        test_plugin_dev_rejects_verify_phase,
        # Simple plan tests
        test_simple_execute_to_finalize,
        test_simple_rejects_refine_phase,
    ])
    sys.exit(runner.run())
