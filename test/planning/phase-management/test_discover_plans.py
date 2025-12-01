#!/usr/bin/env python3
"""Tests for discover-plans.py script."""

import os
import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('planning', 'phase-management', 'discover-plans.py')


# =============================================================================
# Test Fixtures
# =============================================================================

PLAN_INIT = """# Task Plan: Init Only

**Current Phase**: init
**Current Task**: task-1

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 0/2 |
| refine | pending | 0 | 0/0 |
"""

PLAN_IMPLEMENT = """# Task Plan: JWT Authentication

**Current Phase**: implement
**Current Task**: task-6

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| refine | completed | 3 | 3/3 |
| implement | in_progress | 5 | 2/5 |
| verify | pending | 4 | 0/4 |
| finalize | pending | 3 | 0/3 |
"""

PLAN_COMPLETED = """# Task Plan: Completed Feature

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
"""

# Simple plan type (3-phase: init → execute → finalize)
PLAN_EXECUTE = """# Task Plan: Simple Documentation Update

**Current Phase**: execute
**Current Task**: task-1

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| execute | in_progress | 3 | 1/3 |
| finalize | pending | 2 | 0/2 |
"""


# =============================================================================
# Test Helpers
# =============================================================================

def create_plans_structure(base_dir: Path, plans: dict) -> Path:
    """Create a .claude/plans/ structure with specified plans."""
    plans_dir = base_dir / '.claude' / 'plans'
    plans_dir.mkdir(parents=True, exist_ok=True)

    for name, content in plans.items():
        plan_dir = plans_dir / name
        plan_dir.mkdir(exist_ok=True)
        (plan_dir / 'plan.md').write_text(content)

    return plans_dir


# =============================================================================
# Tests
# =============================================================================

def test_discover_single_plan():
    """Test discovering a single plan."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = create_plans_structure(temp_dir, {
            'jwt-auth': PLAN_IMPLEMENT
        })

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        assert data['count'] == 1
        assert len(data['plans']) == 1
        assert data['plans'][0]['name'] == 'jwt-auth'
        assert data['plans'][0]['phase'] == 'implement'
        assert data['plans'][0]['status'] == 'in_progress'
        assert data['recommendation'] == 'jwt-auth'
    finally:
        shutil.rmtree(temp_dir)


def test_discover_multiple_plans():
    """Test discovering multiple plans."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = create_plans_structure(temp_dir, {
            'plan-a': PLAN_INIT,
            'plan-b': PLAN_IMPLEMENT,
            'plan-c': PLAN_COMPLETED
        })

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success
        data = result.json()

        assert data['count'] == 3
        assert len(data['plans']) == 3

        # Check all plans found
        names = [p['name'] for p in data['plans']]
        assert 'plan-a' in names
        assert 'plan-b' in names
        assert 'plan-c' in names

        # Recommendation should be an in-progress plan
        assert data['recommendation'] in ['plan-a', 'plan-b']
    finally:
        shutil.rmtree(temp_dir)


def test_discover_empty_directory():
    """Test discovering plans in empty directory."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = temp_dir / '.claude' / 'plans'
        plans_dir.mkdir(parents=True)

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success  # Empty is not an error
        data = result.json()

        assert data['count'] == 0
        assert data['plans'] == []
        assert data['recommendation'] is None
    finally:
        shutil.rmtree(temp_dir)


def test_discover_nonexistent_directory():
    """Test handling of nonexistent directory."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path/plans/')
    assert result.success  # Nonexistent is not an error, just empty
    data = result.json()

    assert data['count'] == 0
    assert 'does not exist' in data.get('message', '')


def test_discover_default_path():
    """Test default search path (.claude/plans/)."""
    # Just verify help works since we can't easily test default path
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0
    assert '.claude/plans/' in result.stdout


def test_discover_plan_metadata():
    """Test that plan metadata is correctly extracted."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = create_plans_structure(temp_dir, {
            'jwt-auth': PLAN_IMPLEMENT
        })

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success
        data = result.json()

        plan = data['plans'][0]
        assert plan['name'] == 'jwt-auth'
        assert plan['title'] == 'JWT Authentication'
        assert plan['phase'] == 'implement'
        assert plan['task'] == 'task-6'
        assert plan['status'] == 'in_progress'
        assert 'path' in plan
    finally:
        shutil.rmtree(temp_dir)


def test_discover_completed_plan_status():
    """Test that completed plans have correct status."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = create_plans_structure(temp_dir, {
            'completed-task': PLAN_COMPLETED
        })

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success
        data = result.json()

        plan = data['plans'][0]
        assert plan['status'] == 'completed'
    finally:
        shutil.rmtree(temp_dir)


def test_discover_prefers_in_progress():
    """Test that recommendation prefers in-progress plans."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = create_plans_structure(temp_dir, {
            'completed-plan': PLAN_COMPLETED,
            'active-plan': PLAN_IMPLEMENT
        })

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success
        data = result.json()

        # Should recommend the in-progress plan
        assert data['recommendation'] == 'active-plan'
    finally:
        shutil.rmtree(temp_dir)


def test_discover_simple_plan_execute_phase():
    """Test discovering a Simple plan type with execute phase."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = create_plans_structure(temp_dir, {
            'simple-task': PLAN_EXECUTE
        })

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        assert data['count'] == 1
        assert len(data['plans']) == 1
        plan = data['plans'][0]
        assert plan['name'] == 'simple-task'
        assert plan['phase'] == 'execute'
        assert plan['status'] == 'in_progress'
        assert plan['title'] == 'Simple Documentation Update'
    finally:
        shutil.rmtree(temp_dir)


def test_discover_mixed_plan_types():
    """Test discovering both Implementation and Simple plan types."""
    temp_dir = create_temp_dir()
    try:
        plans_dir = create_plans_structure(temp_dir, {
            'impl-plan': PLAN_IMPLEMENT,
            'simple-plan': PLAN_EXECUTE
        })

        result = run_script(SCRIPT_PATH, str(plans_dir))
        assert result.success
        data = result.json()

        assert data['count'] == 2
        phases = {p['name']: p['phase'] for p in data['plans']}
        assert phases['impl-plan'] == 'implement'
        assert phases['simple-plan'] == 'execute'
    finally:
        shutil.rmtree(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_discover_single_plan,
        test_discover_multiple_plans,
        test_discover_empty_directory,
        test_discover_nonexistent_directory,
        test_discover_default_path,
        test_discover_plan_metadata,
        test_discover_completed_plan_status,
        test_discover_prefers_in_progress,
        test_discover_simple_plan_execute_phase,
        test_discover_mixed_plan_types,
    ])
    sys.exit(runner.run())
