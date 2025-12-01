#!/usr/bin/env python3
"""
Tests for the consolidate-build-outputs.py script.

TDD: Tests written FIRST before implementation.

Tests cover:
- Detection and consolidation of timestamped build output permissions
- Replacement with wildcard patterns
- Handling of multiple module paths
- Dry-run mode
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Add test root to path for conftest imports
TEST_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(TEST_ROOT))

from conftest import (
    ScriptTestCase, TestRunner, run_script, get_script_path,
    create_temp_dir, create_temp_file, MARKETPLACE_ROOT
)


# Script path - will fail until script is created
SCRIPT_PATH = MARKETPLACE_ROOT / 'general-tools' / 'skills' / 'permission-management' / 'scripts' / 'consolidate-build-outputs.py'


class TestDetectTimestampedPermissions(ScriptTestCase):
    """Test detection of timestamped build output permissions."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'consolidate-build-outputs.py'

    def test_detect_timestamped_build_output(self):
        """Should detect permissions with timestamp patterns."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Read(target/build-output-2025-11-20-174411.log)",
                    "Read(target/build-output-2025-11-21-093000.log)",
                    "Read(target/build-output-2025-11-22-120000.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        self.assertIn('consolidated', data)
        self.assertEqual(data['consolidated'], 3)

    def test_detect_nested_module_build_outputs(self):
        """Should detect timestamped permissions in nested module paths."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(oauth-sheriff-core/target/build-output-2025-11-20-174411.log)",
                    "Read(oauth-sheriff-api/target/build-output-2025-11-20-174411.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        self.assertEqual(data['consolidated'], 2)


class TestWildcardReplacement(ScriptTestCase):
    """Test replacement of timestamped permissions with wildcards."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'consolidate-build-outputs.py'

    def test_generates_correct_wildcard(self):
        """Should generate correct wildcard pattern."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(target/build-output-2025-11-20-174411.log)",
                    "Read(target/build-output-2025-11-21-093000.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        self.assertIn('wildcards_added', data)
        # Should consolidate to a single wildcard
        self.assertIn('Read(target/build-output-*.log)', data['wildcards_added'])

    def test_generates_nested_module_wildcard(self):
        """Should generate wildcard that covers nested modules."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(oauth-sheriff-core/target/build-output-2025-11-20-174411.log)",
                    "Read(oauth-sheriff-api/target/build-output-2025-11-20-174411.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        # Should generate a single wildcard covering all modules
        self.assertIn('wildcards_added', data)
        wildcards = data['wildcards_added']
        # Either individual wildcards or a ** pattern
        self.assertTrue(
            'Read(**/target/build-output-*.log)' in wildcards or
            len(wildcards) >= 1
        )


class TestApplyChanges(ScriptTestCase):
    """Test actual application of changes (non-dry-run)."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'consolidate-build-outputs.py'

    def test_removes_timestamped_adds_wildcard(self):
        """Should remove timestamped and add wildcard when not dry-run."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Read(target/build-output-2025-11-20-174411.log)",
                    "Read(target/build-output-2025-11-21-093000.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        # Verify the file was modified
        settings = json.loads(settings_file.read_text())
        allow_list = settings['permissions']['allow']

        # Should have removed the timestamped entries
        self.assertNotIn('Read(target/build-output-2025-11-20-174411.log)', allow_list)
        self.assertNotIn('Read(target/build-output-2025-11-21-093000.log)', allow_list)

        # Should have added the wildcard
        self.assertIn('Read(target/build-output-*.log)', allow_list)

        # Should have kept other permissions
        self.assertIn('Bash(git:*)', allow_list)


class TestDryRunMode(ScriptTestCase):
    """Test dry-run mode doesn't modify files."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'consolidate-build-outputs.py'

    def test_dry_run_does_not_modify_file(self):
        """Dry-run should not modify the settings file."""
        original_content = json.dumps({
            "permissions": {
                "allow": [
                    "Read(target/build-output-2025-11-20-174411.log)"
                ],
                "deny": [],
                "ask": []
            }
        })

        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(original_content)

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)

        # File should be unchanged
        self.assertEqual(settings_file.read_text(), original_content)


class TestNoTimestampedPermissions(ScriptTestCase):
    """Test behavior when no timestamped permissions exist."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'consolidate-build-outputs.py'

    def test_no_changes_when_no_timestamps(self):
        """Should report no changes when no timestamped permissions."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:*)",
                    "Read(target/build-output-*.log)"  # Already a wildcard
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        self.assertEqual(data['consolidated'], 0)
        self.assertEqual(len(data.get('wildcards_added', [])), 0)


class TestOutputFormat(ScriptTestCase):
    """Test the output format and structure."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'consolidate-build-outputs.py'

    def test_output_includes_removed_list(self):
        """Output should include list of removed permissions."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(target/build-output-2025-11-20-174411.log)",
                    "Read(target/build-output-2025-11-21-093000.log)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file), '--dry-run')
        self.assert_success(result)
        data = result.json()

        self.assertIn('removed', data)
        self.assertEqual(len(data['removed']), 2)


# =============================================================================
# Simple function-based tests for quick validation
# =============================================================================

def test_script_exists():
    """Verify the script exists (will fail until implemented)."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"


def test_help_works():
    """Script should respond to --help."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    import unittest

    # Check if script exists first
    if not SCRIPT_PATH.exists():
        print(f"ERROR: Script not yet implemented: {SCRIPT_PATH}")
        print("TDD: Implement the script to make these tests pass.")
        sys.exit(1)

    # Run unittest-based tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDetectTimestampedPermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestWildcardReplacement))
    suite.addTests(loader.loadTestsFromTestCase(TestApplyChanges))
    suite.addTests(loader.loadTestsFromTestCase(TestDryRunMode))
    suite.addTests(loader.loadTestsFromTestCase(TestNoTimestampedPermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormat))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Also run simple function tests
    print("\n" + "=" * 50)
    print("Running simple function tests...")
    print("=" * 50)

    simple_tests = [
        test_script_exists,
        test_help_works,
    ]

    simple_runner = TestRunner()
    simple_runner.add_tests(simple_tests)
    simple_result = simple_runner.run()

    # Exit with combined result
    sys.exit(0 if result.wasSuccessful() and simple_result == 0 else 1)
