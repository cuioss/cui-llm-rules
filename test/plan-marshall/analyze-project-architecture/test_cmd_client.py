#!/usr/bin/env python3
"""Tests for _cmd_client.py module."""

import json
import sys
import tempfile
from pathlib import Path

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / "marketplace" / "bundles" / "plan-marshall" / "skills" / "analyze-project-architecture" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from _cmd_client import (
    get_modules_list,
    get_modules_with_command,
)
from _architecture_core import (
    save_derived_data,
)


# =============================================================================
# Helper Functions
# =============================================================================

def create_test_derived_data(tmpdir: str) -> dict:
    """Create test derived-data.json and return the data."""
    test_data = {
        "project": {
            "name": "test-project",
            "root": tmpdir
        },
        "modules": {
            "module-a": {
                "name": "module-a",
                "build_systems": ["maven"],
                "paths": {"module": "module-a"},
                "commands": {
                    "module-tests": "python3 ...",
                    "verify": "python3 ...",
                    "quality-gate": "python3 ..."
                }
            },
            "module-b": {
                "name": "module-b",
                "build_systems": ["maven"],
                "paths": {"module": "module-b"},
                "commands": {
                    "module-tests": "python3 ...",
                    "verify": "python3 ..."
                }
            },
            "module-c": {
                "name": "module-c",
                "build_systems": ["npm"],
                "paths": {"module": "module-c"},
                "commands": {
                    "build": "npm run build"
                }
            }
        }
    }
    save_derived_data(test_data, tmpdir)
    return test_data


# =============================================================================
# Tests for get_modules_list
# =============================================================================

def test_get_modules_list_returns_all():
    """get_modules_list returns all module names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        create_test_derived_data(tmpdir)
        modules = get_modules_list(tmpdir)
        assert set(modules) == {"module-a", "module-b", "module-c"}


# =============================================================================
# Tests for get_modules_with_command
# =============================================================================

def test_get_modules_with_command_verify():
    """get_modules_with_command returns modules with verify command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        create_test_derived_data(tmpdir)
        modules = get_modules_with_command("verify", tmpdir)
        assert set(modules) == {"module-a", "module-b"}


def test_get_modules_with_command_module_tests():
    """get_modules_with_command returns modules with module-tests command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        create_test_derived_data(tmpdir)
        modules = get_modules_with_command("module-tests", tmpdir)
        assert set(modules) == {"module-a", "module-b"}


def test_get_modules_with_command_quality_gate():
    """get_modules_with_command returns only module-a for quality-gate."""
    with tempfile.TemporaryDirectory() as tmpdir:
        create_test_derived_data(tmpdir)
        modules = get_modules_with_command("quality-gate", tmpdir)
        assert modules == ["module-a"]


def test_get_modules_with_command_build():
    """get_modules_with_command returns only module-c for build."""
    with tempfile.TemporaryDirectory() as tmpdir:
        create_test_derived_data(tmpdir)
        modules = get_modules_with_command("build", tmpdir)
        assert modules == ["module-c"]


def test_get_modules_with_command_nonexistent():
    """get_modules_with_command returns empty list for unknown command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        create_test_derived_data(tmpdir)
        modules = get_modules_with_command("nonexistent-command", tmpdir)
        assert modules == []


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import traceback

    tests = [
        test_get_modules_list_returns_all,
        test_get_modules_with_command_verify,
        test_get_modules_with_command_module_tests,
        test_get_modules_with_command_quality_gate,
        test_get_modules_with_command_build,
        test_get_modules_with_command_nonexistent,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
            print(f"PASSED: {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAILED: {test.__name__}")
            traceback.print_exc()
            print()

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
