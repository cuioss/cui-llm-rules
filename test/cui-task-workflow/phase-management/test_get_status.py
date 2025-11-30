#!/usr/bin/env python3
"""Tests for get-status.py script."""

import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-task-workflow', 'phase-management', 'get-status.py')


# =============================================================================
# Test Fixtures
# =============================================================================

PLAN_MD_FULL = """# Task Plan: JWT Authentication

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
| implement | in_progress | 7 | 4/7 |
| verify | pending | 4 | 0/4 |
| finalize | pending | 3 | 0/3 |

---

## Phase: init (completed)

### Task 1: Setup

**Phase**: init
**Goal**: Initial setup

**Checklist**:
- [x] Done

## Phase: implement (in_progress)

### Task 6: Create JwtService

**Phase**: implement
**Goal**: Implement JWT token generation service

**Checklist**:
- [x] Create class
- [x] Add methods
- [ ] Add tests
- [ ] Document
"""

CONFIG_TOON = """# Configuration

plan_type: implementation
technology: java
build_system: maven
compatibility: deprecations
commit_strategy: fine-granular
finalizing: pr-workflow
"""

REFERENCES_TOON = """# References

issue: 123
issue_url: https://github.com/org/repo/issues/123
issue_title: Add JWT Authentication
branch: feature/jwt-auth
base_branch: main

adrs[]:
- ADR-001: Token Format Selection
- ADR-002: Security Considerations

interfaces[]:
- IF-AUTH-001: AuthenticationService
"""

PLAN_COMPLETED = """# Task Plan: Completed

**Current Phase**: finalize
**Current Task**: none

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| refine | completed | 1 | 1/1 |
| implement | completed | 3 | 3/3 |
| verify | completed | 2 | 2/2 |
| finalize | completed | 1 | 1/1 |
"""

PLAN_MINIMAL = """# Task Plan: Minimal

**Current Phase**: init
**Current Task**: task-1

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 1 | 0/1 |
"""


# =============================================================================
# Test Helpers
# =============================================================================

def create_full_plan_dir(base_dir: Path) -> Path:
    """Create a full plan directory with all files."""
    plan_dir = base_dir / 'jwt-auth'
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / 'plan.md').write_text(PLAN_MD_FULL)
    (plan_dir / 'config.toon').write_text(CONFIG_TOON)
    (plan_dir / 'references.toon').write_text(REFERENCES_TOON)
    return plan_dir


def create_minimal_plan_dir(base_dir: Path) -> Path:
    """Create a minimal plan directory with only plan.md."""
    plan_dir = base_dir / 'minimal'
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / 'plan.md').write_text(PLAN_MINIMAL)
    return plan_dir


# =============================================================================
# Tests - Complete Status Aggregation
# =============================================================================

def test_full_status_aggregation():
    """Test complete status aggregation from all files."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_full_plan_dir(temp_dir)

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        # Check plan_status
        assert data['plan_status']['name'] == 'jwt-auth'
        assert data['plan_status']['title'] == 'JWT Authentication'
        assert data['plan_status']['plan_type'] == 'implementation'
        assert data['plan_status']['overall_status'] == 'in_progress'
        assert data['plan_status']['overall_progress'] > 0

        # Check phase_progress
        assert len(data['phase_progress']) == 5
        init_phase = next(p for p in data['phase_progress'] if p['phase'] == 'init')
        assert init_phase['status'] == 'completed'

        # Check current_focus
        assert data['current_focus']['phase'] == 'implement'
        assert data['current_focus']['task'] == 'task-6'
        assert 'JwtService' in data['current_focus']['task_name']

        # Check configuration
        assert data['configuration']['technology'] == 'java'
        assert data['configuration']['build_system'] == 'maven'

        # Check references
        assert data['references']['issue'] is not None
        assert 'ADR-001' in data['references']['adrs']
        assert 'IF-AUTH-001' in data['references']['interfaces']
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Tests - Progress Calculation
# =============================================================================

def test_progress_calculation():
    """Test overall progress percentage calculation."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_full_plan_dir(temp_dir)

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        # Total tasks: 5+3+7+4+3 = 22
        # Completed: 5+3+4+0+0 = 12
        # Progress: 12/22 = 54.5%
        progress = data['plan_status']['overall_progress']
        assert 50 <= progress <= 60, f"Expected ~54.5%, got {progress}%"
    finally:
        shutil.rmtree(temp_dir)


def test_completed_plan_progress():
    """Test progress is 100% for completed plans."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / 'completed'
        plan_dir.mkdir()
        (plan_dir / 'plan.md').write_text(PLAN_COMPLETED)

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        assert data['plan_status']['overall_status'] == 'completed'
        assert data['plan_status']['overall_progress'] == 100.0
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Tests - Missing Files Handling
# =============================================================================

def test_missing_config_file():
    """Test handling when config.md is missing."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_minimal_plan_dir(temp_dir)

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        # Should still work with defaults
        assert data['plan_status']['plan_type'] == 'implementation'
        assert data['configuration']['technology'] == ''
    finally:
        shutil.rmtree(temp_dir)


def test_missing_references_file():
    """Test handling when references.md is missing."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_minimal_plan_dir(temp_dir)

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        # Should have empty references
        assert data['references']['issue'] is None
        assert data['references']['adrs'] == []
    finally:
        shutil.rmtree(temp_dir)


def test_missing_plan_directory():
    """Test error when plan directory doesn't exist."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path')
    assert not result.success
    data = result.json()

    assert 'error' in data
    assert data['error']['type'] == 'directory_not_found'


def test_missing_plan_file():
    """Test error when plan.md doesn't exist."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / 'empty-plan'
        plan_dir.mkdir()

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert not result.success
        data = result.json()

        assert 'error' in data
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Tests - Output Structure
# =============================================================================

def test_output_structure():
    """Test that output contains all expected top-level fields."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_full_plan_dir(temp_dir)

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        # Check all top-level fields
        assert 'plan_status' in data
        assert 'phase_progress' in data
        assert 'current_focus' in data
        assert 'configuration' in data
        assert 'references' in data
        assert 'plan_directory' in data
    finally:
        shutil.rmtree(temp_dir)


def test_phase_progress_structure():
    """Test phase progress array structure."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = create_full_plan_dir(temp_dir)

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        for phase in data['phase_progress']:
            assert 'phase' in phase
            assert 'status' in phase
            assert 'tasks' in phase
            assert 'completed' in phase
    finally:
        shutil.rmtree(temp_dir)


def test_help_output():
    """Test --help output."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0
    assert 'plan_status' in result.stdout
    assert 'phase_progress' in result.stdout


# =============================================================================
# Tests - Partial Plan Data
# =============================================================================

def test_partial_config_data():
    """Test handling of partial config data."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / 'partial'
        plan_dir.mkdir()
        (plan_dir / 'plan.md').write_text(PLAN_MINIMAL)
        (plan_dir / 'config.toon').write_text("""# Configuration

plan_type: simple
""")

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        assert data['plan_status']['plan_type'] == 'simple'
        # Other config fields should be empty or default
        assert data['configuration']['technology'] == ''
    finally:
        shutil.rmtree(temp_dir)


def test_partial_references_data():
    """Test handling of partial references data."""
    temp_dir = create_temp_dir()
    try:
        plan_dir = temp_dir / 'partial'
        plan_dir.mkdir()
        (plan_dir / 'plan.md').write_text(PLAN_MINIMAL)
        (plan_dir / 'references.toon').write_text("""# References

branch: feature/test
""")

        result = run_script(SCRIPT_PATH, str(plan_dir))
        assert result.success
        data = result.json()

        assert data['references']['issue'] is None
        assert data['configuration']['branch'] == 'feature/test'
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_full_status_aggregation,
        test_progress_calculation,
        test_completed_plan_progress,
        test_missing_config_file,
        test_missing_references_file,
        test_missing_plan_directory,
        test_missing_plan_file,
        test_output_structure,
        test_phase_progress_structure,
        test_help_output,
        test_partial_config_data,
        test_partial_references_data,
    ])
    sys.exit(runner.run())
