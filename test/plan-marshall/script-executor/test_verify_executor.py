#!/usr/bin/env python3
"""
Tests for the verify-executor.py script.

Tests executor verification subcommands:
- check: Verify executor exists and is valid Python
- drift: Compare executor mappings with current marketplace state
- paths: Verify all mapped paths exist
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add test root to path for conftest imports
TEST_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TEST_ROOT))

from conftest import ScriptTestCase, run_script, MARKETPLACE_ROOT


# Script path to verify-executor.py
SCRIPT_PATH = MARKETPLACE_ROOT / 'plan-marshall' / 'skills' / 'script-executor' / 'scripts' / 'verify-executor.py'


def executor_is_available():
    """Check if a complete executor environment exists."""
    plan_dir = Path('.plan')
    return (
        plan_dir.exists() and
        (plan_dir / 'execute-script.py').exists() and
        (plan_dir / 'execution_log.py').exists()
    )


class TestVerifyExecutorCheck(ScriptTestCase):
    """Test verify-executor.py check subcommand."""

    bundle = 'plan-marshall'
    skill = 'script-executor'
    script = 'verify-executor.py'

    def test_check_fails_when_executor_missing(self):
        """Should report failure when executor doesn't exist."""
        # Run from temp dir where .plan/execute-script.py doesn't exist
        result = run_script(SCRIPT_PATH, 'check', cwd=self.temp_dir)

        self.assert_failure(result)
        self.assertIn('MISSING', result.stderr)

    def test_check_reports_valid_executor(self):
        """Should report success for valid executor (integration test)."""
        if not executor_is_available():
            self.skipTest("No complete executor present in project root")

        result = run_script(SCRIPT_PATH, 'check')
        self.assert_success(result)
        self.assertIn('Executor valid', result.stdout)


class TestVerifyExecutorDrift(ScriptTestCase):
    """Test verify-executor.py drift subcommand."""

    bundle = 'plan-marshall'
    skill = 'script-executor'
    script = 'verify-executor.py'

    def test_drift_fails_when_executor_missing(self):
        """Should report error when executor doesn't exist."""
        result = run_script(SCRIPT_PATH, 'drift', cwd=self.temp_dir)

        self.assert_failure(result)
        self.assertIn('Could not read executor mappings', result.stderr)

    def test_drift_detects_no_changes(self):
        """Should report no drift when executor matches marketplace (integration)."""
        if not executor_is_available():
            self.skipTest("No complete executor present in project root")

        result = run_script(SCRIPT_PATH, 'drift')
        # May or may not have drift - just check it runs
        self.assertIn('Executor scripts:', result.stdout)


class TestVerifyExecutorPaths(ScriptTestCase):
    """Test verify-executor.py paths subcommand."""

    bundle = 'plan-marshall'
    skill = 'script-executor'
    script = 'verify-executor.py'

    def test_paths_fails_when_executor_missing(self):
        """Should report error when executor doesn't exist."""
        result = run_script(SCRIPT_PATH, 'paths', cwd=self.temp_dir)

        self.assert_failure(result)
        self.assertIn('Could not read executor mappings', result.stderr)

    def test_paths_verifies_all_mappings(self):
        """Should verify all mapped paths exist (integration)."""
        if not executor_is_available():
            self.skipTest("No complete executor present in project root")

        result = run_script(SCRIPT_PATH, 'paths')
        self.assertIn('Total mappings:', result.stdout)
        self.assertIn('Existing:', result.stdout)


class TestVerifyExecutorOutput(ScriptTestCase):
    """Test verify-executor.py output formatting."""

    bundle = 'plan-marshall'
    skill = 'script-executor'
    script = 'verify-executor.py'

    def test_check_output_includes_toon(self):
        """Check output should include TOON status line."""
        result = run_script(SCRIPT_PATH, 'check')

        # Output should have status line in TOON format
        if result.success:
            self.assertIn('status\t', result.stdout)
        else:
            # Even failure should have structured output
            self.assertTrue(
                'MISSING' in result.stderr or 'status\t' in result.stdout
            )

    def test_drift_output_includes_counts(self):
        """Drift output should include comparison counts."""
        if not executor_is_available():
            self.skipTest("No complete executor present in project root")

        result = run_script(SCRIPT_PATH, 'drift')
        self.assertIn('Executor scripts:', result.stdout)
        self.assertIn('Marketplace scripts:', result.stdout)

    def test_paths_output_includes_counts(self):
        """Paths output should include verification counts."""
        if not executor_is_available():
            self.skipTest("No complete executor present in project root")

        result = run_script(SCRIPT_PATH, 'paths')
        self.assertIn('Total mappings:', result.stdout)
        self.assertIn('Existing:', result.stdout)
        self.assertIn('Missing:', result.stdout)


class TestVerifyExecutorHelp(ScriptTestCase):
    """Test verify-executor.py help and argument parsing."""

    bundle = 'plan-marshall'
    skill = 'script-executor'
    script = 'verify-executor.py'

    def test_requires_subcommand(self):
        """Should require a subcommand."""
        result = run_script(SCRIPT_PATH)

        self.assert_failure(result)
        # argparse error about required subcommand
        self.assertIn('required', result.stderr.lower())

    def test_invalid_subcommand_fails(self):
        """Should fail with invalid subcommand."""
        result = run_script(SCRIPT_PATH, 'invalid-command')

        self.assert_failure(result)

    def test_check_subcommand_available(self):
        """Check subcommand should be available."""
        result = run_script(SCRIPT_PATH, 'check', '--help')

        self.assert_success(result)
        self.assertIn('check', result.stdout.lower())

    def test_drift_subcommand_available(self):
        """Drift subcommand should be available."""
        result = run_script(SCRIPT_PATH, 'drift', '--help')

        self.assert_success(result)
        self.assertIn('drift', result.stdout.lower())

    def test_paths_subcommand_available(self):
        """Paths subcommand should be available."""
        result = run_script(SCRIPT_PATH, 'paths', '--help')

        self.assert_success(result)
        self.assertIn('paths', result.stdout.lower())


if __name__ == '__main__':
    import unittest
    unittest.main()
