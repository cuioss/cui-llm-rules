#!/usr/bin/env python3
"""
Tests for the detect-suspicious-permissions.py script.

TDD: Tests written FIRST before implementation.

Tests cover:
- Detection of system temp directory permissions
- Detection of root/home directory write access
- Detection of dangerous command patterns
- User-approved permission exclusion
- Severity classification
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
SCRIPT_PATH = MARKETPLACE_ROOT / 'general-tools' / 'skills' / 'permission-management' / 'scripts' / 'detect-suspicious-permissions.py'


class TestDetectSystemTempPermissions(ScriptTestCase):
    """Test detection of system temp directory permissions."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-suspicious-permissions.py'

    def test_detect_tmp_write_permission(self):
        """Should flag Write(/tmp/**) as suspicious."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Write(/tmp/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        self.assertIn('suspicious', data)
        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Write(/tmp/**)', suspicious_perms)

    def test_detect_var_tmp_permission(self):
        """Should flag Write(/var/tmp/**) as suspicious."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Write(/var/tmp/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Write(/var/tmp/**)', suspicious_perms)


class TestDetectRootAccessPermissions(ScriptTestCase):
    """Test detection of overly broad root/home access."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-suspicious-permissions.py'

    def test_detect_root_write_access(self):
        """Should flag Write(/**)  as highly suspicious."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Write(/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Write(/**)', suspicious_perms)

        # Should be high severity
        for item in data['suspicious']:
            if item['permission'] == 'Write(/**)':
                self.assertEqual(item['severity'], 'high')

    def test_detect_etc_access(self):
        """Should flag Write(/etc/**) as suspicious."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Write(/etc/**)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Write(/etc/**)', suspicious_perms)


class TestDetectDangerousCommands(ScriptTestCase):
    """Test detection of dangerous command patterns."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-suspicious-permissions.py'

    def test_detect_rm_rf_permission(self):
        """Should flag Bash(rm:-rf *) as dangerous."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(rm:-rf *)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Bash(rm:-rf *)', suspicious_perms)

    def test_detect_sudo_permission(self):
        """Should flag Bash(sudo:*) as suspicious."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(sudo:*)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Bash(sudo:*)', suspicious_perms)

    def test_detect_curl_pipe_bash(self):
        """Should flag patterns that could be curl | bash."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Bash(curl:* | bash)"],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertIn('Bash(curl:* | bash)', suspicious_perms)


class TestUserApprovedExclusion(ScriptTestCase):
    """Test exclusion of user-approved permissions."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-suspicious-permissions.py'

    def test_exclude_user_approved_permissions(self):
        """Should not flag permissions that user has explicitly approved."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": ["Write(/tmp/**)", "Bash(sudo:*)"],
                "deny": [],
                "ask": []
            }
        }))

        # Create run-configuration with approved list
        approved_file = self.temp_dir / 'run-configuration.json'
        approved_file.write_text(json.dumps({
            "commands": {
                "setup-project-permissions": {
                    "user_approved_permissions": ["Write(/tmp/**)"]
                }
            }
        }))

        result = run_script(
            SCRIPT_PATH,
            '--settings', str(settings_file),
            '--approved-file', str(approved_file)
        )
        self.assert_success(result)
        data = result.json()

        # tmp should be in already_approved, not suspicious
        suspicious_perms = [s['permission'] for s in data['suspicious']]
        self.assertNotIn('Write(/tmp/**)', suspicious_perms)
        self.assertIn('Write(/tmp/**)', data.get('already_approved', []))

        # sudo should still be flagged
        self.assertIn('Bash(sudo:*)', suspicious_perms)


class TestSeverityClassification(ScriptTestCase):
    """Test severity classification of suspicious permissions."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-suspicious-permissions.py'

    def test_severity_levels(self):
        """Should classify permissions into high/medium/low severity."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Write(/**)",          # high - root write
                    "Write(/tmp/**)",      # medium - temp dir
                    "Bash(curl:*)"         # low - network access
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        severities = {s['permission']: s['severity'] for s in data['suspicious']}

        self.assertEqual(severities.get('Write(/**)'), 'high')
        # Note: exact severity levels may vary based on implementation


class TestSafePermissions(ScriptTestCase):
    """Test that safe permissions are not flagged."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-suspicious-permissions.py'

    def test_safe_project_permissions(self):
        """Should not flag normal project permissions."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {
                "allow": [
                    "Edit(.plan/**)",
                    "Read(//~/git/my-project/**)",
                    "Write(//~/git/my-project/**)",
                    "Bash(git:*)",
                    "Bash(npm:*)",
                    "Skill(builder:*)"
                ],
                "deny": [],
                "ask": []
            }
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        # None of these should be flagged
        self.assertEqual(len(data['suspicious']), 0)


class TestOutputFormat(ScriptTestCase):
    """Test the output format and structure."""

    bundle = 'general-tools'
    skill = 'permission-management'
    script = 'detect-suspicious-permissions.py'

    def test_output_includes_reason(self):
        """Each suspicious permission should include a reason."""
        settings_file = self.temp_dir / 'settings.json'
        settings_file.write_text(json.dumps({
            "permissions": {"allow": ["Write(/tmp/**)"], "deny": [], "ask": []}
        }))

        result = run_script(SCRIPT_PATH, '--settings', str(settings_file))
        self.assert_success(result)
        data = result.json()

        self.assertTrue(len(data['suspicious']) > 0)
        for item in data['suspicious']:
            self.assertIn('permission', item)
            self.assertIn('reason', item)
            self.assertIn('severity', item)


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

    suite.addTests(loader.loadTestsFromTestCase(TestDetectSystemTempPermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectRootAccessPermissions))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectDangerousCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestUserApprovedExclusion))
    suite.addTests(loader.loadTestsFromTestCase(TestSeverityClassification))
    suite.addTests(loader.loadTestsFromTestCase(TestSafePermissions))
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
