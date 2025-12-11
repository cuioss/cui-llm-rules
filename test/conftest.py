#!/usr/bin/env python3
"""
Shared test infrastructure for cui-llm-rules marketplace scripts.

This module provides base classes, fixtures, and utilities for testing
Python scripts in the marketplace bundles. Uses only Python stdlib.

Usage:
    from conftest import ScriptTestCase, run_script, create_temp_file

See test/README.md for full documentation.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional, Union
from unittest import TestCase


# =============================================================================
# Path Constants
# =============================================================================

TEST_ROOT = Path(__file__).parent
PROJECT_ROOT = TEST_ROOT.parent
MARKETPLACE_ROOT = PROJECT_ROOT / 'marketplace' / 'bundles'
TEST_FIXTURE_BASE = PROJECT_ROOT / '.plan' / 'temp' / 'test-fixture'


# =============================================================================
# Script Runner
# =============================================================================

class ScriptResult:
    """Result from running a script."""

    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    @property
    def success(self) -> bool:
        """True if script exited with code 0."""
        return self.returncode == 0

    def json(self) -> dict:
        """Parse stdout as JSON. Raises ValueError if invalid."""
        if not self.stdout.strip():
            raise ValueError(f"Empty stdout. stderr: {self.stderr}")
        return json.loads(self.stdout)

    def json_or_error(self) -> dict:
        """Parse stdout as JSON, or stderr if stdout is empty."""
        if self.stdout.strip():
            return json.loads(self.stdout)
        if self.stderr.strip():
            return json.loads(self.stderr)
        return {'error': 'No output'}

    def __repr__(self) -> str:
        return f"ScriptResult(returncode={self.returncode}, stdout={len(self.stdout)}b, stderr={len(self.stderr)}b)"


def run_script(
    script_path: Union[str, Path],
    *args: str,
    input_data: Optional[str] = None,
    cwd: Optional[Union[str, Path]] = None,
    timeout: int = 30
) -> ScriptResult:
    """
    Run a Python script and capture its output.

    Args:
        script_path: Path to the script to run
        *args: Command line arguments to pass
        input_data: Optional stdin input
        cwd: Working directory (defaults to current)
        timeout: Timeout in seconds (default 30)

    Returns:
        ScriptResult with returncode, stdout, stderr

    Example:
        result = run_script(SCRIPT_PATH, '--mode', 'structured', input_data=content)
        assert result.success
        data = result.json()
    """
    result = subprocess.run(
        [sys.executable, str(script_path)] + list(args),
        capture_output=True,
        text=True,
        input=input_data,
        cwd=cwd,
        timeout=timeout
    )
    return ScriptResult(result.returncode, result.stdout, result.stderr)


def get_script_path(bundle: str, skill: str, script: str) -> Path:
    """
    Get the path to a marketplace script.

    Args:
        bundle: Bundle name (e.g., 'pm-workflow')
        skill: Skill name (e.g., 'plan-files')
        script: Script filename (e.g., 'parse-plan.py')

    Returns:
        Absolute path to the script

    Raises:
        FileNotFoundError: If script doesn't exist
    """
    path = MARKETPLACE_ROOT / bundle / 'skills' / skill / 'scripts' / script
    if not path.exists():
        raise FileNotFoundError(f"Script not found: {path}")
    return path


# =============================================================================
# Temp File Helpers
# =============================================================================

def create_temp_file(
    content: str,
    suffix: str = '.md',
    dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    Create a temporary file with content.

    Args:
        content: File content
        suffix: File extension (default .md)
        dir: Directory to create in (default system temp)

    Returns:
        Path to created file (caller must delete)

    Example:
        temp_file = create_temp_file("# Test\\nContent")
        try:
            result = run_script(SCRIPT, str(temp_file))
        finally:
            temp_file.unlink()
    """
    fd, path = tempfile.mkstemp(suffix=suffix, dir=dir)
    try:
        os.write(fd, content.encode('utf-8'))
    finally:
        os.close(fd)
    return Path(path)


def create_temp_dir() -> Path:
    """
    Create a temporary directory.

    Returns:
        Path to created directory (caller must delete with shutil.rmtree)
    """
    return Path(tempfile.mkdtemp())


# =============================================================================
# Base Test Case
# =============================================================================

class ScriptTestCase(TestCase):
    """
    Base class for script tests with common setup/teardown.

    Provides:
        - Automatic temp directory management
        - Script path resolution
        - Common assertion helpers

    Example:
        class TestParseConfig(ScriptTestCase):
            bundle = 'pm-workflow'
            skill = 'plan-files'
            script = 'parse-config.py'

            def test_basic_config(self):
                result = self.run_script_with_file(CONFIG_CONTENT)
                self.assert_success(result)
                data = result.json()
                self.assertEqual(data['plan_type'], 'implementation')
    """

    # Override in subclass
    bundle: str = ''
    skill: str = ''
    script: str = ''

    @classmethod
    def setUpClass(cls):
        """Resolve script path once per test class."""
        if cls.bundle and cls.skill and cls.script:
            cls.script_path = get_script_path(cls.bundle, cls.skill, cls.script)
        else:
            cls.script_path = None

    def setUp(self):
        """Create temp directory for each test."""
        self.temp_dir = create_temp_dir()
        self.temp_files = []

    def tearDown(self):
        """Clean up temp files and directory."""
        for f in self.temp_files:
            try:
                f.unlink()
            except FileNotFoundError:
                pass
        try:
            shutil.rmtree(self.temp_dir)
        except FileNotFoundError:
            pass

    def create_temp_file(self, content: str, suffix: str = '.md') -> Path:
        """Create temp file tracked for cleanup."""
        path = create_temp_file(content, suffix=suffix, dir=self.temp_dir)
        self.temp_files.append(path)
        return path

    def run_script(self, *args: str, **kwargs) -> ScriptResult:
        """Run the test script with arguments."""
        if not self.script_path:
            raise ValueError("Set bundle, skill, script class attributes")
        return run_script(self.script_path, *args, **kwargs)

    def run_script_with_file(self, content: str, *extra_args: str, suffix: str = '.md') -> ScriptResult:
        """Create temp file with content and run script with it as first arg."""
        temp_file = self.create_temp_file(content, suffix=suffix)
        return self.run_script(str(temp_file), *extra_args)

    # Assertion helpers
    def assert_success(self, result: ScriptResult, msg: str = None):
        """Assert script succeeded."""
        self.assertEqual(result.returncode, 0, msg or f"Script failed: {result.stderr}")

    def assert_failure(self, result: ScriptResult, msg: str = None):
        """Assert script failed."""
        self.assertNotEqual(result.returncode, 0, msg or "Expected script to fail")

    def assert_json_field(self, result: ScriptResult, field: str, expected: Any):
        """Assert JSON output has field with expected value."""
        data = result.json()
        self.assertIn(field, data, f"Missing field: {field}")
        self.assertEqual(data[field], expected, f"Field {field} mismatch")


# =============================================================================
# Test Runner
# =============================================================================

class TestRunner:
    """
    Simple test runner for standalone test files.

    Example:
        def test_basic():
            assert 1 + 1 == 2

        def test_error():
            result = run_script(SCRIPT, 'bad-input')
            assert not result.success

        if __name__ == '__main__':
            runner = TestRunner()
            runner.add_tests([test_basic, test_error])
            sys.exit(runner.run())
    """

    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_tests(self, tests: list):
        """Add test functions."""
        self.tests.extend(tests)

    def run(self) -> int:
        """Run all tests and return exit code."""
        print(f"Running {len(self.tests)} tests...")
        print("-" * 50)

        for test in self.tests:
            try:
                test()
                print(f"  \u2713 {test.__name__}")
                self.passed += 1
            except AssertionError as e:
                print(f"  \u2717 {test.__name__}: {e}")
                self.failed += 1
                self.errors.append((test.__name__, 'FAIL', str(e)))
            except Exception as e:
                print(f"  \u2717 {test.__name__}: ERROR - {e}")
                self.failed += 1
                self.errors.append((test.__name__, 'ERROR', str(e)))

        print("-" * 50)
        print(f"Passed: {self.passed}, Failed: {self.failed}")

        if self.errors:
            print("\nFailures:")
            for name, kind, msg in self.errors:
                print(f"  {name} ({kind}): {msg}")

        return 0 if self.failed == 0 else 1


# =============================================================================
# Utilities
# =============================================================================

def assert_json_structure(data: dict, expected_keys: list, context: str = ""):
    """
    Assert JSON has expected top-level keys.

    Args:
        data: Parsed JSON dict
        expected_keys: List of required keys
        context: Optional context for error message
    """
    missing = [k for k in expected_keys if k not in data]
    if missing:
        raise AssertionError(f"Missing keys {missing} in {context or 'data'}: {list(data.keys())}")


def load_fixture(fixture_path: Union[str, Path]) -> str:
    """Load fixture file content."""
    path = Path(fixture_path)
    if not path.is_absolute():
        # Assume relative to test file's directory
        path = Path(os.getcwd()) / path
    return path.read_text()


# =============================================================================
# Plan Test Context
# =============================================================================

def get_test_fixture_dir() -> Path:
    """
    Get the test fixture directory.

    When run via test/run-tests.py, uses the TEST_FIXTURE_DIR environment variable.
    When run standalone, creates a directory in .plan/temp/test-fixture/.

    Returns:
        Path to the test fixture directory
    """
    env_dir = os.environ.get('TEST_FIXTURE_DIR')
    if env_dir:
        return Path(env_dir)

    # Fallback for standalone execution
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    fixture_dir = TEST_FIXTURE_BASE / f"standalone-{timestamp}"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    return fixture_dir


class PlanTestContext:
    """
    Context manager for tests that need PLAN_BASE_DIR.

    Uses centralized test fixture directory instead of system temp.
    When run via test/run-tests.py, the fixture directory is managed
    by the runner and cleaned up automatically after all tests.

    Usage:
        with PlanTestContext(plan_id='my-plan') as ctx:
            result = run_script(SCRIPT_PATH, 'add', '--plan-id', 'my-plan', ...)
            # ctx.fixture_dir contains the base directory
            # ctx.plan_dir contains the plan directory

    Attributes:
        fixture_dir: Base test fixture directory
        plan_id: The plan identifier
        plan_dir: Path to .../plans/{plan_id}
    """

    def __init__(self, plan_id: str = 'test-plan'):
        """
        Initialize the test context.

        Args:
            plan_id: Plan identifier (kebab-case)
        """
        self.plan_id = plan_id
        self.fixture_dir: Optional[Path] = None
        self.plan_dir: Optional[Path] = None
        self._original_plan_base_dir: Optional[str] = None
        self._is_standalone: bool = False

    def __enter__(self) -> 'PlanTestContext':
        """Set up the test context."""
        self.fixture_dir = get_test_fixture_dir()
        self._is_standalone = 'TEST_FIXTURE_DIR' not in os.environ

        # Create plan directory structure
        self.plan_dir = self.fixture_dir / 'plans' / self.plan_id
        self.plan_dir.mkdir(parents=True, exist_ok=True)

        # Set PLAN_BASE_DIR environment variable
        self._original_plan_base_dir = os.environ.get('PLAN_BASE_DIR')
        os.environ['PLAN_BASE_DIR'] = str(self.fixture_dir)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up the test context."""
        # Clean up the plan_dir to ensure test isolation
        # (when via runner, fixture_dir is shared but each test should get fresh plan_dir)
        if self.plan_dir and self.plan_dir.exists():
            shutil.rmtree(self.plan_dir, ignore_errors=True)

        # Restore original PLAN_BASE_DIR
        if self._original_plan_base_dir is None:
            os.environ.pop('PLAN_BASE_DIR', None)
        else:
            os.environ['PLAN_BASE_DIR'] = self._original_plan_base_dir

        # Only cleanup fixture_dir if running standalone (not via run-tests.py)
        if self._is_standalone and self.fixture_dir and self.fixture_dir.exists():
            shutil.rmtree(self.fixture_dir, ignore_errors=True)
