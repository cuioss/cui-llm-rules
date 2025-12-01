#!/usr/bin/env python3
"""
Test suite for transition-phase.py phase pointer updates.

Tests that transition-phase.py updates plan.md with:
- Current Phase header on valid transitions
- Current Task pointer to first task of new phase
- No changes on invalid transitions

Usage:
    python3 test-transition-phase.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


class TestRunner:
    """Simple test runner for stdlib-only testing."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def run_test(self, name: str, test_func):
        """Run a single test function."""
        self.tests_run += 1
        try:
            test_func()
            self.tests_passed += 1
            print(f"  \u2713 {name}")
        except AssertionError as e:
            self.tests_failed += 1
            self.failures.append((name, str(e)))
            print(f"  \u2717 {name}: {e}")
        except Exception as e:
            self.tests_failed += 1
            self.failures.append((name, f"Exception: {e}"))
            print(f"  \u2717 {name}: Exception: {e}")

    def summary(self):
        """Print test summary and return exit code."""
        print("\n" + "=" * 50)
        print(f"Tests: {self.tests_run}, Passed: {self.tests_passed}, Failed: {self.tests_failed}")

        if self.failures:
            print("\nFailures:")
            for name, msg in self.failures:
                print(f"  - {name}: {msg}")

        return 0 if self.tests_failed == 0 else 1


SCRIPT_DIR = Path(__file__).parent
TRANSITION_PHASE = SCRIPT_DIR / 'transition-phase.py'


def run_script(script_path: Path, args: list[str]) -> tuple[int, str, str]:
    """Run a script and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(script_path)] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def create_plan_with_phase(plan_dir: Path, current_phase: str, plan_type: str = 'simple',
                           phase_tasks: dict = None):
    """Create a test plan with specified current phase and completed tasks.

    Args:
        plan_dir: Directory to create plan in
        current_phase: Current phase to set in header
        plan_type: Plan type (simple, plugin-development, implementation)
        phase_tasks: Dict of phase -> list of checklist items, marked [x] for complete
    """
    plan_dir.mkdir(parents=True, exist_ok=True)

    # Default phase tasks based on plan type
    if phase_tasks is None:
        phase_tasks = {}

    # Create config.toon
    config_content = f"""# Plan Configuration

plan_type: {plan_type}
branch: test-branch
issue: none

technology: none
build_system: none

compatibility: breaking
commit_strategy: fine-granular
finalizing: commit-only
"""
    (plan_dir / 'config.toon').write_text(config_content)

    # Build plan.md content
    if plan_type == 'simple':
        phases = ['init', 'execute', 'finalize']
    elif plan_type == 'plugin-development':
        phases = ['init', 'refine', 'execute', 'finalize']
    else:  # implementation
        phases = ['init', 'refine', 'implement', 'verify', 'finalize']

    # Determine current task
    current_task = 'task-1'

    # Build phase progress table
    table_rows = []
    for phase in phases:
        items = phase_tasks.get(phase, ['Task item'])
        total = len(items)
        completed = sum(1 for item in items if item.startswith('[x]'))
        if completed == 0:
            status = 'pending'
        elif completed >= total:
            status = 'completed'
        else:
            status = 'in_progress'
        table_rows.append(f"| {phase} | {status} | {total} | {completed}/{total} |")

    table = "\n".join(table_rows)

    # Build phase sections
    phase_sections = []
    for phase in phases:
        items = phase_tasks.get(phase, ['Task item'])
        completed = sum(1 for item in items if item.startswith('[x]'))
        total = len(items)
        if completed == 0:
            status = 'pending'
        elif completed >= total:
            status = 'completed'
        else:
            status = 'in_progress'

        checklist_items = []
        for item in items:
            if item.startswith('[x]'):
                checklist_items.append(f"- [x] {item[3:].strip()}")
            else:
                checklist_items.append(f"- [ ] {item}")

        phase_sections.append(f"""## Phase: {phase} ({status})

### Task 1: Test Task

**Phase**: {phase}
**Goal**: Test goal

**Checklist**:
{chr(10).join(checklist_items)}
""")

    plan_content = f"""# Task Plan: Test Plan

**Configuration**: See [config.toon](./config.toon)
**References**: See [references.toon](./references.toon)

**Current Phase**: {current_phase}
**Current Task**: {current_task}

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
{table}

---

{chr(10).join(phase_sections)}
---

## Completion Criteria

All phases must be completed.
"""

    (plan_dir / 'plan.md').write_text(plan_content)


# Test: Valid transition updates plan.md phase pointer

def test_valid_transition_updates_phase_pointer():
    """Test that valid transition updates Current Phase in plan.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        # Create plan with init phase complete, ready to transition to execute
        create_plan_with_phase(
            plan_dir,
            current_phase='init',
            plan_type='simple',
            phase_tasks={
                'init': ['[x] Setup done'],
                'execute': ['Implement feature'],
                'finalize': ['Commit changes']
            }
        )

        # Verify initial state
        content_before = (plan_dir / 'plan.md').read_text()
        assert '**Current Phase**: init' in content_before, "Initial phase should be init"

        # Run transition
        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'init'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['transition']['success'] is True
        assert result['transition']['to_phase'] == 'execute'
        assert result.get('updated') is True, "Result should indicate plan was updated"

        # Verify plan.md was updated
        content_after = (plan_dir / 'plan.md').read_text()
        assert '**Current Phase**: execute' in content_after, \
            f"Current Phase should be updated to 'execute'. Content: {content_after[:500]}"


def test_valid_transition_updates_current_task():
    """Test that valid transition updates Current Task to first task of new phase."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        create_plan_with_phase(
            plan_dir,
            current_phase='init',
            plan_type='simple',
            phase_tasks={
                'init': ['[x] Setup done'],
                'execute': ['Implement feature'],
                'finalize': ['Commit changes']
            }
        )

        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'init'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        content_after = (plan_dir / 'plan.md').read_text()
        assert '**Current Task**: task-1' in content_after, \
            "Current Task should point to first task of new phase"


# Test: Invalid transition returns error without updating

def test_invalid_transition_incomplete_phase_no_update():
    """Test that incomplete phase transition fails without updating plan.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        # Create plan with init phase NOT complete
        create_plan_with_phase(
            plan_dir,
            current_phase='init',
            plan_type='simple',
            phase_tasks={
                'init': ['Incomplete item'],  # Not [x] prefixed
                'execute': ['Implement feature'],
                'finalize': ['Commit changes']
            }
        )

        content_before = (plan_dir / 'plan.md').read_text()

        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'init'
        ])

        assert returncode != 0, "Should fail for incomplete phase"

        result = json.loads(stdout)
        assert 'error' in result
        assert result['error']['type'] == 'incomplete_phase'

        # Plan should NOT be modified
        content_after = (plan_dir / 'plan.md').read_text()
        assert content_before == content_after, "Plan should not be modified on error"


def test_invalid_transition_phase_mismatch_no_update():
    """Test that phase mismatch fails without updating plan.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        # Create plan with init as current phase
        create_plan_with_phase(
            plan_dir,
            current_phase='init',
            plan_type='simple',
            phase_tasks={
                'init': ['[x] Done'],
                'execute': ['[x] Also done'],
                'finalize': ['Not done']
            }
        )

        content_before = (plan_dir / 'plan.md').read_text()

        # Try to complete 'execute' when current is 'init'
        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'execute'
        ])

        assert returncode != 0, "Should fail for phase mismatch"

        result = json.loads(stdout)
        assert 'error' in result
        assert result['error']['type'] == 'phase_mismatch'

        # Plan should NOT be modified
        content_after = (plan_dir / 'plan.md').read_text()
        assert content_before == content_after, "Plan should not be modified on error"


# Test: Last phase (finalize) marks plan complete

def test_finalize_transition_marks_complete():
    """Test that completing finalize phase marks plan as complete."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        # Create plan with finalize as current phase, all tasks complete
        create_plan_with_phase(
            plan_dir,
            current_phase='finalize',
            plan_type='simple',
            phase_tasks={
                'init': ['[x] Done'],
                'execute': ['[x] Done'],
                'finalize': ['[x] Committed']
            }
        )

        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'finalize'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['transition']['success'] is True
        assert result['transition']['plan_complete'] is True
        assert result['transition']['to_phase'] is None


def test_finalize_transition_updates_status():
    """Test that completing finalize updates plan status indicators."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        create_plan_with_phase(
            plan_dir,
            current_phase='finalize',
            plan_type='simple',
            phase_tasks={
                'init': ['[x] Done'],
                'execute': ['[x] Done'],
                'finalize': ['[x] Committed']
            }
        )

        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'finalize'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['plan_status']['status'] == 'completed'


# Test: Plugin-development plan transitions

def test_plugin_dev_plan_transitions():
    """Test transitions for plugin-development plan type (4-phase)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        create_plan_with_phase(
            plan_dir,
            current_phase='refine',
            plan_type='plugin-development',
            phase_tasks={
                'init': ['[x] Done'],
                'refine': ['[x] Analysis complete'],
                'execute': ['Implement'],
                'finalize': ['Commit']
            }
        )

        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'refine'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['transition']['to_phase'] == 'execute'

        content_after = (plan_dir / 'plan.md').read_text()
        assert '**Current Phase**: execute' in content_after


# Test: Implementation plan transitions

def test_implementation_plan_transitions():
    """Test transitions for implementation plan type (5-phase)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plan_dir = Path(tmpdir) / 'test-plan'

        create_plan_with_phase(
            plan_dir,
            current_phase='implement',
            plan_type='implementation',
            phase_tasks={
                'init': ['[x] Done'],
                'refine': ['[x] Done'],
                'implement': ['[x] Code written'],
                'verify': ['Run tests'],
                'finalize': ['Commit']
            }
        )

        returncode, stdout, stderr = run_script(TRANSITION_PHASE, [
            str(plan_dir),
            'implement'
        ])

        assert returncode == 0, f"Script failed: {stderr}"

        result = json.loads(stdout)
        assert result['transition']['to_phase'] == 'verify'

        content_after = (plan_dir / 'plan.md').read_text()
        assert '**Current Phase**: verify' in content_after


def main():
    """Run all tests."""
    print("=" * 50)
    print("Test Suite: transition-phase.py phase pointer updates")
    print("=" * 50)
    print()

    runner = TestRunner()

    # Valid transition tests
    print("Valid transitions:")
    runner.run_test("updates phase pointer", test_valid_transition_updates_phase_pointer)
    runner.run_test("updates current task", test_valid_transition_updates_current_task)

    # Invalid transition tests
    print("\nInvalid transitions:")
    runner.run_test("incomplete phase - no update", test_invalid_transition_incomplete_phase_no_update)
    runner.run_test("phase mismatch - no update", test_invalid_transition_phase_mismatch_no_update)

    # Finalize tests
    print("\nFinalize phase:")
    runner.run_test("marks plan complete", test_finalize_transition_marks_complete)
    runner.run_test("updates status", test_finalize_transition_updates_status)

    # Plan type tests
    print("\nPlan types:")
    runner.run_test("plugin-development transitions", test_plugin_dev_plan_transitions)
    runner.run_test("implementation transitions", test_implementation_plan_transitions)

    return runner.summary()


if __name__ == '__main__':
    sys.exit(main())
