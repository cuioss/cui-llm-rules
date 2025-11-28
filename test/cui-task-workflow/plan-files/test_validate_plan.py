#!/usr/bin/env python3
"""Tests for validate-plan.py script."""

import shutil
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, create_temp_dir, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-task-workflow', 'plan-files', 'validate-plan.py')


# =============================================================================
# Test Fixtures
# =============================================================================

VALID_PLAN = """# Task Plan: JWT Authentication

**Current Phase**: implement
**Current Task**: task-1

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| implement | in_progress | 3 | 0/3 |

### Task 1: Setup

**Phase**: init
**Goal**: Initial setup

**Checklist**:
- [x] Done
"""

VALID_CONFIG = """# Task Configuration

**Plan Type**: Implementation

## Build Configuration

| Property | Value |
|----------|-------|
| Technology | Java |

## Context

| Property | Value |
|----------|-------|
| Branch | feature/jwt |
"""

MINIMAL_PLAN = """# Task Plan: Test

**Current Phase**: init
**Current Task**: task-1

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | pending | 1 | 0/1 |
"""

MINIMAL_CONFIG = """# Task Configuration

**Plan Type**: Implementation

## Context

| Property | Value |
|----------|-------|
| Branch | main |
"""

INVALID_PLAN = """# Task Plan: Test

Some content without required fields
"""

INVALID_CONFIG = """# Task Configuration

Some content without required fields
"""

INVALID_PLAN_TYPE_CONFIG = """# Task Configuration

**Plan Type**: InvalidType

## Context

| Property | Value |
|----------|-------|
| Branch | main |
"""

PLAN_WITHOUT_TASK = """# Task Plan: Test

**Current Phase**: init

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | pending | 1 | 0/1 |
"""

VALID_REFERENCES = """# Task References

## Standards

- [Java Core](../../standards/java/core.adoc)

## Related ADRs

- [ADR-001](../adr/ADR-001.md)
"""


# =============================================================================
# Helpers
# =============================================================================

def create_plan_directory(plan_content=None, config_content=None, references_content=None):
    """Create a temporary plan directory with specified files."""
    temp_dir = create_temp_dir()

    if plan_content:
        (temp_dir / 'plan.md').write_text(plan_content)

    if config_content:
        (temp_dir / 'config.md').write_text(config_content)

    if references_content:
        (temp_dir / 'references.md').write_text(references_content)

    return temp_dir


def cleanup_dir(temp_dir):
    """Clean up temporary directory."""
    shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# Tests
# =============================================================================

def test_validate_valid_plan():
    """Test validation of a valid plan directory."""
    temp_dir = create_plan_directory(VALID_PLAN, VALID_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        assert result.success, f"Script failed: {result.stderr}"
        data = result.json()

        assert data['valid'] is True
        assert data['files']['plan.md']['valid'] is True
        assert data['files']['config.md']['valid'] is True
        assert data['summary']['total_errors'] == 0
    finally:
        cleanup_dir(temp_dir)


def test_validate_missing_plan():
    """Test validation when plan.md is missing."""
    temp_dir = create_plan_directory(config_content=MINIMAL_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        data = result.json()

        assert data['valid'] is False
        assert data['files']['plan.md']['exists'] is False
        assert 'plan.md' in data['summary']['missing_required_files']
    finally:
        cleanup_dir(temp_dir)


def test_validate_missing_config():
    """Test validation when config.md is missing."""
    temp_dir = create_plan_directory(plan_content=MINIMAL_PLAN)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        data = result.json()

        assert data['valid'] is False
        assert data['files']['config.md']['exists'] is False
        assert 'config.md' in data['summary']['missing_required_files']
    finally:
        cleanup_dir(temp_dir)


def test_validate_plan_errors():
    """Test validation detects plan errors."""
    temp_dir = create_plan_directory(INVALID_PLAN, MINIMAL_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        data = result.json()

        assert data['valid'] is False
        assert data['files']['plan.md']['valid'] is False

        # Check for expected errors
        error_codes = [e['code'] for e in data['errors'] if e['file'] == 'plan.md']
        assert 'MISSING_CURRENT_PHASE' in error_codes
        assert 'MISSING_PHASE_TABLE' in error_codes
    finally:
        cleanup_dir(temp_dir)


def test_validate_config_errors():
    """Test validation detects config errors."""
    temp_dir = create_plan_directory(MINIMAL_PLAN, INVALID_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        data = result.json()

        assert data['valid'] is False
        assert data['files']['config.md']['valid'] is False

        error_codes = [e['code'] for e in data['errors'] if e['file'] == 'config.md']
        assert 'MISSING_PLAN_TYPE' in error_codes
        assert 'MISSING_CONTEXT' in error_codes
        assert 'MISSING_BRANCH' in error_codes
    finally:
        cleanup_dir(temp_dir)


def test_validate_invalid_plan_type():
    """Test validation detects invalid plan type."""
    temp_dir = create_plan_directory(MINIMAL_PLAN, INVALID_PLAN_TYPE_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        data = result.json()

        assert data['valid'] is False
        error_codes = [e['code'] for e in data['errors']]
        assert 'INVALID_PLAN_TYPE' in error_codes
    finally:
        cleanup_dir(temp_dir)


def test_validate_warnings():
    """Test validation generates appropriate warnings."""
    temp_dir = create_plan_directory(PLAN_WITHOUT_TASK, MINIMAL_CONFIG)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        data = result.json()

        # Plan is valid but has warnings
        assert data['files']['plan.md']['valid'] is True

        warning_codes = [w['code'] for w in data['warnings']]
        # Missing current task is a warning, not error
        assert 'MISSING_CURRENT_TASK' in warning_codes
        # No tasks defined is a warning
        assert 'NO_TASKS' in warning_codes
    finally:
        cleanup_dir(temp_dir)


def test_validate_directory_not_found():
    """Test error handling for missing directory."""
    result = run_script(SCRIPT_PATH, '/nonexistent/path/plan')
    assert not result.success
    assert result.returncode == 1

    data = result.json()
    assert 'error' in data
    assert data['error']['type'] == 'directory_not_found'


def test_validate_with_references():
    """Test validation includes references.md."""
    temp_dir = create_plan_directory(VALID_PLAN, VALID_CONFIG, VALID_REFERENCES)
    try:
        result = run_script(SCRIPT_PATH, str(temp_dir))
        data = result.json()

        assert data['files']['references.md']['exists'] is True
        assert data['files']['references.md']['valid'] is True
    finally:
        cleanup_dir(temp_dir)


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_validate_valid_plan,
        test_validate_missing_plan,
        test_validate_missing_config,
        test_validate_plan_errors,
        test_validate_config_errors,
        test_validate_invalid_plan_type,
        test_validate_warnings,
        test_validate_directory_not_found,
        test_validate_with_references,
    ])
    sys.exit(runner.run())
