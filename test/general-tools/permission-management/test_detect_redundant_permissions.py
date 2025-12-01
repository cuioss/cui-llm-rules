#!/usr/bin/env python3
"""
Tests for the detect-redundant-permissions.py script.

TDD: Tests written FIRST before implementation.

Tests cover:
- Detection of permissions in local that duplicate global
- Detection of marketplace permissions in local (should be global)
- Detection of permissions covered by broader wildcards
- Path normalization edge cases
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
SCRIPT_PATH = MARKETPLACE_ROOT / 'general-tools' / 'skills' / 'permission-management' / 'scripts' / 'detect-redundant-permissions.py'


class TestDetectExactDuplicates(ScriptTestCase):
    """Test detection of exact duplicate permissions between global and local."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-redundant-permissions.py'

    def test_detect_exact_duplicate(self):
        """Should detect when same permission exists in both global and local."""
        # Create mock global settings
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Bash(npm:*)", "Read(//~/git/**)"],
                "deny": [],
                "ask": []
            }
        }))

        # Create mock local settings with duplicate
        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)", "Edit(.plan/**)"],  # git:* is duplicate
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('redundant', data)
        redundant_perms = [r['permission'] for r in data['redundant']]
        self.assertIn('Bash(git:*)', redundant_perms)
        self.assertNotIn('Edit(.plan/**)', redundant_perms)

    def test_no_duplicates_reports_empty(self):
        """Should report empty redundant list when no duplicates exist."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {"allow": ["Edit(.plan/**)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertEqual(len(data['redundant']), 0)


class TestDetectMarketplaceInLocal(ScriptTestCase):
    """Test detection of marketplace permissions that should be in global."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-redundant-permissions.py'

    def test_detect_skill_permission_in_local(self):
        """Should flag Skill() permissions in local as belonging in global."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {"allow": ["Skill(builder:*)"], "deny": [], "ask": []}
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Skill(cui-java-expert:*)",  # Should be in global
                    "Edit(.plan/**)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('marketplace_in_local', data)
        marketplace_perms = [m['permission'] for m in data['marketplace_in_local']]
        self.assertIn('Skill(cui-java-expert:*)', marketplace_perms)

    def test_detect_slashcommand_permission_in_local(self):
        """Should flag SlashCommand() permissions in local as belonging in global."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "SlashCommand(/builder:*)",  # Should be in global
                    "SlashCommand(/java-create:*)"  # Should be in global
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        marketplace_perms = [m['permission'] for m in data['marketplace_in_local']]
        self.assertIn('SlashCommand(/builder:*)', marketplace_perms)
        self.assertIn('SlashCommand(/java-create:*)', marketplace_perms)


class TestDetectWildcardCovered(ScriptTestCase):
    """Test detection of specific permissions covered by broader wildcards."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-redundant-permissions.py'

    def test_detect_specific_covered_by_wildcard(self):
        """Should detect when specific permission is covered by global wildcard."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Read(//~/git/**)"],  # Broad wildcard
                "deny": [],
                "ask": []
            }
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Read(//~/git/my-project/**)"  # Covered by global wildcard
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        # Should identify the specific permission as redundant
        redundant_perms = [r['permission'] for r in data['redundant']]
        self.assertIn('Read(//~/git/my-project/**)', redundant_perms)

    def test_bash_command_wildcard_coverage(self):
        """Should detect when Bash(cmd:specific) is covered by Bash(cmd:*)."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(git:*)"],  # Broad wildcard
                "deny": [],
                "ask": []
            }
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Bash(git:status)",  # Covered by git:*
                    "Bash(git:commit)"   # Covered by git:*
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        redundant_perms = [r['permission'] for r in data['redundant']]
        self.assertIn('Bash(git:status)', redundant_perms)
        self.assertIn('Bash(git:commit)', redundant_perms)


class TestOutputFormat(ScriptTestCase):
    """Test the output format and structure."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-redundant-permissions.py'

    def test_output_includes_reason(self):
        """Each redundant permission should include a reason."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertTrue(len(data['redundant']) > 0)
        for item in data['redundant']:
            self.assertIn('permission', item)
            self.assertIn('reason', item)

    def test_output_summary_counts(self):
        """Output should include summary counts."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"], "deny": [], "ask": []}
        }))

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)", "Skill(builder:*)"], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        self.assert_success(result)
        data = result.json()

        self.assertIn('summary', data)
        self.assertIn('redundant_count', data['summary'])
        self.assertIn('marketplace_in_local_count', data['summary'])


class TestErrorHandling(ScriptTestCase):
    """Test error handling for invalid inputs."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-redundant-permissions.py'

    def test_missing_global_file(self):
        """Should handle missing global settings file gracefully."""
        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', '/nonexistent/path/settings.json',
            '--local-settings', str(local_file)
        )
        # Should succeed but report global not found
        data = result.json()
        # Either returns error or handles gracefully with warning
        self.assertTrue('error' in data or 'warning' in data or data.get('global_exists') is False)

    def test_invalid_json_in_settings(self):
        """Should handle invalid JSON gracefully."""
        global_file = self.temp_dir / 'global.json'
        global_file.write_text("{ invalid json }")

        local_file = self.temp_dir / 'local.json'
        local_file.write_text(json.dumps({
            "permissions": {"allow": [], "deny": [], "ask": []}
        }))

        result = run_script(
            SCRIPT_PATH,
            '--global-settings', str(global_file),
            '--local-settings', str(local_file)
        )
        data = result.json()
        self.assertIn('error', data)


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

    suite.addTests(loader.loadTestsFromTestCase(TestDetectExactDuplicates))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectMarketplaceInLocal))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectWildcardCovered))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

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
