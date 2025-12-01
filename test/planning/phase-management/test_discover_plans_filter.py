#!/usr/bin/env python3
"""
Tests for discover-plans.py --filter functionality.

Run with:
    python3 -m pytest test/planning/phase-management/test_discover_plans_filter.py -v
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the script directory to path for imports
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'planning' / 'skills' / 'phase-management' / 'scripts'
sys.path.insert(0, str(SCRIPT_DIR))

from importlib import import_module

# Import the module (handle the hyphen in filename)
import importlib.util
spec = importlib.util.spec_from_file_location("discover_plans", SCRIPT_DIR / "discover-plans.py")
discover_plans_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discover_plans_module)

# Get functions from module
parse_filter = discover_plans_module.parse_filter
matches_filter = discover_plans_module.matches_filter
discover_plans = discover_plans_module.discover_plans
VALID_PHASES = discover_plans_module.VALID_PHASES
VALID_STATUSES = discover_plans_module.VALID_STATUSES


class TestParseFilter(unittest.TestCase):
    """Tests for parse_filter function."""

    def test_empty_filter_returns_empty_sets(self):
        """Empty filter string returns empty sets."""
        phase_filters, status_filters = parse_filter(None)
        self.assertEqual(phase_filters, set())
        self.assertEqual(status_filters, set())

        phase_filters, status_filters = parse_filter('')
        self.assertEqual(phase_filters, set())
        self.assertEqual(status_filters, set())

    def test_single_phase_filter(self):
        """Single phase filter is parsed correctly."""
        phase_filters, status_filters = parse_filter('init')
        self.assertEqual(phase_filters, {'init'})
        self.assertEqual(status_filters, set())

    def test_multiple_phase_filters(self):
        """Multiple phase filters are parsed correctly."""
        phase_filters, status_filters = parse_filter('implement,verify,finalize')
        self.assertEqual(phase_filters, {'implement', 'verify', 'finalize'})
        self.assertEqual(status_filters, set())

    def test_execute_phase_filter(self):
        """Execute phase (Simple plan type) is parsed correctly."""
        phase_filters, status_filters = parse_filter('execute')
        self.assertEqual(phase_filters, {'execute'})
        self.assertEqual(status_filters, set())

    def test_all_executable_phases_filter(self):
        """All executable phases (implement, execute, verify, finalize) are parsed."""
        phase_filters, status_filters = parse_filter('implement,execute,verify,finalize')
        self.assertEqual(phase_filters, {'implement', 'execute', 'verify', 'finalize'})
        self.assertEqual(status_filters, set())

    def test_single_status_filter(self):
        """Single status filter is parsed correctly."""
        phase_filters, status_filters = parse_filter('completed')
        self.assertEqual(phase_filters, set())
        self.assertEqual(status_filters, {'completed'})

    def test_mixed_filters(self):
        """Mixed phase and status filters are parsed correctly."""
        phase_filters, status_filters = parse_filter('init,completed')
        self.assertEqual(phase_filters, {'init'})
        self.assertEqual(status_filters, {'completed'})

    def test_invalid_filter_ignored(self):
        """Invalid filter values are silently ignored."""
        phase_filters, status_filters = parse_filter('init,invalid,refine')
        self.assertEqual(phase_filters, {'init', 'refine'})
        self.assertEqual(status_filters, set())

    def test_case_insensitive(self):
        """Filter parsing is case-insensitive."""
        phase_filters, status_filters = parse_filter('INIT,Completed')
        self.assertEqual(phase_filters, {'init'})
        self.assertEqual(status_filters, {'completed'})

    def test_whitespace_trimmed(self):
        """Whitespace around filter values is trimmed."""
        phase_filters, status_filters = parse_filter('init , refine , completed')
        self.assertEqual(phase_filters, {'init', 'refine'})
        self.assertEqual(status_filters, {'completed'})


class TestMatchesFilter(unittest.TestCase):
    """Tests for matches_filter function."""

    def test_no_filters_matches_all(self):
        """No filters matches all plans."""
        plan = {'phase': 'implement', 'status': 'in_progress'}
        self.assertTrue(matches_filter(plan, set(), set()))

    def test_phase_filter_match(self):
        """Phase filter matches correct phase."""
        plan = {'phase': 'implement', 'status': 'in_progress'}
        self.assertTrue(matches_filter(plan, {'implement'}, set()))
        self.assertFalse(matches_filter(plan, {'verify'}, set()))

    def test_multiple_phase_filters_match_any(self):
        """Multiple phase filters match if plan matches any."""
        plan = {'phase': 'implement', 'status': 'in_progress'}
        self.assertTrue(matches_filter(plan, {'implement', 'verify', 'finalize'}, set()))

    def test_execute_phase_filter_match(self):
        """Execute phase filter matches Simple plan type."""
        plan = {'phase': 'execute', 'status': 'in_progress'}
        self.assertTrue(matches_filter(plan, {'execute'}, set()))
        self.assertFalse(matches_filter(plan, {'implement'}, set()))

    def test_all_executable_phases_filter_match(self):
        """All executable phases filter matches both plan types."""
        impl_plan = {'phase': 'implement', 'status': 'in_progress'}
        simple_plan = {'phase': 'execute', 'status': 'in_progress'}
        executable_phases = {'implement', 'execute', 'verify', 'finalize'}

        self.assertTrue(matches_filter(impl_plan, executable_phases, set()))
        self.assertTrue(matches_filter(simple_plan, executable_phases, set()))

    def test_status_filter_match(self):
        """Status filter matches correct status."""
        plan = {'phase': 'implement', 'status': 'completed'}
        self.assertTrue(matches_filter(plan, set(), {'completed'}))
        self.assertFalse(matches_filter(plan, set(), {'in_progress'}))

    def test_combined_filters_require_both(self):
        """Combined phase and status filters require both to match."""
        plan = {'phase': 'implement', 'status': 'in_progress'}

        # Both match
        self.assertTrue(matches_filter(plan, {'implement'}, {'in_progress'}))

        # Phase matches, status doesn't
        self.assertFalse(matches_filter(plan, {'implement'}, {'completed'}))

        # Status matches, phase doesn't
        self.assertFalse(matches_filter(plan, {'verify'}, {'in_progress'}))

    def test_empty_phase_in_plan(self):
        """Plan with empty phase doesn't match phase filters."""
        plan = {'phase': '', 'status': 'pending'}
        self.assertFalse(matches_filter(plan, {'init'}, set()))
        self.assertTrue(matches_filter(plan, set(), {'pending'}))


class TestDiscoverPlansFilter(unittest.TestCase):
    """Integration tests for discover_plans with filter."""

    def setUp(self):
        """Create temporary directory with test plans."""
        self.temp_dir = tempfile.mkdtemp()
        self.plans_dir = Path(self.temp_dir) / 'plans'
        self.plans_dir.mkdir()

        # Create test plans with different phases and statuses
        # Implementation plan type (5-phase): init → refine → implement → verify → finalize
        self._create_plan('plan-init', 'init', 'pending')
        self._create_plan('plan-refine', 'refine', 'in_progress')
        self._create_plan('plan-implement', 'implement', 'in_progress')
        self._create_plan('plan-verify', 'verify', 'in_progress')
        self._create_plan('plan-finalize', 'finalize', 'in_progress')
        self._create_plan('plan-completed', 'finalize', 'completed')
        # Simple plan type (3-phase): init → execute → finalize
        self._create_plan('plan-execute', 'execute', 'in_progress')

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_plan(self, name: str, phase: str, status: str):
        """Create a test plan directory with plan.md."""
        plan_dir = self.plans_dir / name
        plan_dir.mkdir()

        # Determine status from phase for plan.md content
        phase_status = 'completed' if status == 'completed' else 'in_progress'

        content = f"""# Task Plan: {name}

**Status**: {status}
**Current Phase**: {phase}
**Current Task**: task-1

## Phase Progress Table

| Phase | Status |
|-------|--------|
| init | completed |
| refine | completed |
| implement | {'completed' if phase in ['verify', 'finalize'] else phase_status} |
| verify | {'completed' if phase == 'finalize' else 'pending'} |
| finalize | {phase_status if phase == 'finalize' else 'pending'} |
"""
        (plan_dir / 'plan.md').write_text(content)

    def test_filter_by_single_phase(self):
        """Filter by single phase returns only matching plans."""
        result = discover_plans(str(self.plans_dir), 'init')

        self.assertEqual(result['filter_applied'], 'init')
        self.assertEqual(result['filtered_count'], 1)
        self.assertEqual(len(result['plans']), 1)
        self.assertEqual(result['plans'][0]['name'], 'plan-init')

    def test_filter_by_multiple_phases(self):
        """Filter by multiple phases returns all matching plans."""
        result = discover_plans(str(self.plans_dir), 'implement,verify,finalize')

        self.assertEqual(result['filter_applied'], 'implement,verify,finalize')
        # Should match: plan-implement, plan-verify, plan-finalize, plan-completed
        self.assertEqual(result['filtered_count'], 4)

        plan_names = {p['name'] for p in result['plans']}
        self.assertIn('plan-implement', plan_names)
        self.assertIn('plan-verify', plan_names)
        self.assertIn('plan-finalize', plan_names)
        self.assertIn('plan-completed', plan_names)

    def test_filter_by_execute_phase(self):
        """Filter by execute phase (Simple plan type) returns matching plans."""
        result = discover_plans(str(self.plans_dir), 'execute')

        self.assertEqual(result['filter_applied'], 'execute')
        self.assertEqual(result['filtered_count'], 1)
        self.assertEqual(result['plans'][0]['name'], 'plan-execute')
        self.assertEqual(result['plans'][0]['phase'], 'execute')

    def test_filter_all_executable_phases(self):
        """Filter by all executable phases (implement, execute, verify, finalize)."""
        result = discover_plans(str(self.plans_dir), 'implement,execute,verify,finalize')

        self.assertEqual(result['filter_applied'], 'implement,execute,verify,finalize')
        # Should match: plan-implement, plan-execute, plan-verify, plan-finalize, plan-completed
        self.assertEqual(result['filtered_count'], 5)

        plan_names = {p['name'] for p in result['plans']}
        self.assertIn('plan-implement', plan_names)
        self.assertIn('plan-execute', plan_names)
        self.assertIn('plan-verify', plan_names)
        self.assertIn('plan-finalize', plan_names)
        self.assertIn('plan-completed', plan_names)
        # Should NOT include init or refine
        self.assertNotIn('plan-init', plan_names)
        self.assertNotIn('plan-refine', plan_names)

    def test_filter_by_status_completed(self):
        """Filter by completed status returns only completed plans."""
        result = discover_plans(str(self.plans_dir), 'completed')

        self.assertEqual(result['filter_applied'], 'completed')
        self.assertEqual(result['filtered_count'], 1)
        self.assertEqual(result['plans'][0]['name'], 'plan-completed')

    def test_filter_no_matches_returns_empty(self):
        """Filter with no matches returns empty list."""
        # Filter for a phase that doesn't exist in combination with completed status
        # Our init plan has phase='init' but status='in_progress' (because it has a phase)
        # So filtering for init phase AND completed status should return 0
        result = discover_plans(str(self.plans_dir), 'init,completed')

        # This should only match plans that are in init phase AND completed
        # Since our init plan is in_progress, it won't match
        # Note: plan-completed is in finalize phase, so it doesn't match init filter
        self.assertEqual(result['filtered_count'], 0)

    def test_filter_preserves_recommendation_logic(self):
        """Filter preserves recommendation logic (prefers in_progress)."""
        result = discover_plans(str(self.plans_dir), 'implement,verify')

        # Recommendation should be from filtered results, preferring in_progress
        self.assertIsNotNone(result['recommendation'])
        # Both plan-implement and plan-verify are in_progress
        self.assertIn(result['recommendation'], ['plan-implement', 'plan-verify'])

    def test_no_filter_returns_all(self):
        """No filter returns all plans."""
        result = discover_plans(str(self.plans_dir))

        self.assertNotIn('filter_applied', result)
        self.assertNotIn('filtered_count', result)
        self.assertEqual(len(result['plans']), 7)  # All test plans (6 impl + 1 simple)

    def test_count_vs_filtered_count(self):
        """Count shows total, filtered_count shows filtered."""
        result = discover_plans(str(self.plans_dir), 'init')

        self.assertEqual(result['count'], 7)  # Total plans (6 impl + 1 simple)
        self.assertEqual(result['filtered_count'], 1)  # Filtered plans


class TestDiscoverPlansNoDirectory(unittest.TestCase):
    """Tests for discover_plans with non-existent directory."""

    def test_nonexistent_directory_with_filter(self):
        """Non-existent directory returns empty with filter info."""
        result = discover_plans('/nonexistent/path', 'init')

        self.assertEqual(result['plans'], [])
        self.assertEqual(result['count'], 0)
        self.assertEqual(result['filter_applied'], 'init')
        self.assertEqual(result['filtered_count'], 0)
        self.assertIn('message', result)


if __name__ == '__main__':
    unittest.main()
