#!/usr/bin/env python3
"""Tests for extension_base.py module."""

import sys
from pathlib import Path

# Add extension-api scripts to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / "marketplace" / "bundles" / "plan-marshall" / "skills" / "extension-api" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from extension_base import (
    CMD_COMPILE,
    CMD_TEST_COMPILE,
    CMD_MODULE_TESTS,
    CMD_INTEGRATION_TESTS,
    CMD_COVERAGE,
    CMD_PERFORMANCE,
    CMD_QUALITY_GATE,
    CMD_VERIFY,
    CMD_INSTALL,
    CMD_PACKAGE,
    ALL_CANONICAL_COMMANDS,
    CANONICAL_COMMANDS,
    PROFILE_PATTERNS,
    ExtensionBase,
)


# =============================================================================
# Tests for CMD_* Constants
# =============================================================================

def test_cmd_constants_values():
    """CMD_* constants have expected string values."""
    assert CMD_COMPILE == "compile"
    assert CMD_TEST_COMPILE == "test-compile"
    assert CMD_MODULE_TESTS == "module-tests"
    assert CMD_INTEGRATION_TESTS == "integration-tests"
    assert CMD_COVERAGE == "coverage"
    assert CMD_PERFORMANCE == "performance"
    assert CMD_QUALITY_GATE == "quality-gate"
    assert CMD_VERIFY == "verify"
    assert CMD_INSTALL == "install"
    assert CMD_PACKAGE == "package"


def test_all_canonical_commands_contains_all():
    """ALL_CANONICAL_COMMANDS contains all CMD_* constants."""
    expected = [
        CMD_COMPILE, CMD_TEST_COMPILE, CMD_MODULE_TESTS, CMD_INTEGRATION_TESTS,
        CMD_COVERAGE, CMD_PERFORMANCE, CMD_QUALITY_GATE, CMD_VERIFY,
        CMD_INSTALL, CMD_PACKAGE
    ]
    assert ALL_CANONICAL_COMMANDS == expected


# =============================================================================
# Tests for CANONICAL_COMMANDS Metadata
# =============================================================================

def test_canonical_commands_structure():
    """CANONICAL_COMMANDS has expected structure for each command."""
    for cmd_name, meta in CANONICAL_COMMANDS.items():
        assert "phase" in meta, f"{cmd_name} missing 'phase'"
        assert "description" in meta, f"{cmd_name} missing 'description'"
        assert "required" in meta, f"{cmd_name} missing 'required'"
        assert "applicable_to" in meta, f"{cmd_name} missing 'applicable_to'"
        assert isinstance(meta["required"], bool), f"{cmd_name} 'required' should be bool"
        assert isinstance(meta["applicable_to"], list), f"{cmd_name} 'applicable_to' should be list"


def test_canonical_commands_required():
    """Required commands are marked correctly."""
    required_commands = [CMD_MODULE_TESTS, CMD_QUALITY_GATE, CMD_VERIFY]
    for cmd in required_commands:
        assert CANONICAL_COMMANDS[cmd]["required"], f"{cmd} should be required"


def test_canonical_commands_phases():
    """Commands are assigned to expected phases."""
    phase_mapping = {
        "build": [CMD_COMPILE, CMD_TEST_COMPILE],
        "test": [CMD_MODULE_TESTS, CMD_INTEGRATION_TESTS, CMD_COVERAGE, CMD_PERFORMANCE],
        "quality": [CMD_QUALITY_GATE],
        "verify": [CMD_VERIFY],
        "deploy": [CMD_INSTALL, CMD_PACKAGE],
    }
    for phase, commands in phase_mapping.items():
        for cmd in commands:
            assert CANONICAL_COMMANDS[cmd]["phase"] == phase, f"{cmd} should be in {phase} phase"


# =============================================================================
# Tests for PROFILE_PATTERNS
# =============================================================================

def test_profile_patterns_integration_tests():
    """Integration test aliases map to CMD_INTEGRATION_TESTS."""
    aliases = ["integration-tests", "integration-test", "it", "e2e", "acceptance"]
    for alias in aliases:
        assert alias in PROFILE_PATTERNS, f"'{alias}' should be in PROFILE_PATTERNS"
        assert PROFILE_PATTERNS[alias] == CMD_INTEGRATION_TESTS


def test_profile_patterns_quality_gate():
    """Quality gate aliases map to CMD_QUALITY_GATE."""
    aliases = ["pre-commit", "precommit", "sonar", "lint", "check", "quality"]
    for alias in aliases:
        assert alias in PROFILE_PATTERNS, f"'{alias}' should be in PROFILE_PATTERNS"
        assert PROFILE_PATTERNS[alias] == CMD_QUALITY_GATE


def test_profile_patterns_coverage():
    """Coverage aliases map to CMD_COVERAGE."""
    aliases = ["coverage", "jacoco"]
    for alias in aliases:
        assert alias in PROFILE_PATTERNS, f"'{alias}' should be in PROFILE_PATTERNS"
        assert PROFILE_PATTERNS[alias] == CMD_COVERAGE


def test_profile_patterns_performance():
    """Performance aliases map to CMD_PERFORMANCE."""
    aliases = ["benchmark", "jmh", "perf", "performance", "stress", "load"]
    for alias in aliases:
        assert alias in PROFILE_PATTERNS, f"'{alias}' should be in PROFILE_PATTERNS"
        assert PROFILE_PATTERNS[alias] == CMD_PERFORMANCE


# =============================================================================
# Tests for ExtensionBase Class
# =============================================================================

class ConcreteExtension(ExtensionBase):
    """Concrete implementation for testing."""

    def get_skill_domains(self) -> dict:
        return {"domain": {"key": "test"}, "profiles": {}}


def test_extension_base_abstract_methods():
    """ExtensionBase requires get_skill_domains."""
    ext = ConcreteExtension()
    assert ext.get_skill_domains()["domain"]["key"] == "test"


def test_extension_base_default_build_systems():
    """Default provides_build_systems returns empty list."""
    ext = ConcreteExtension()
    assert ext.provides_build_systems() == []


def test_extension_base_default_applicable_build_systems():
    """Default get_applicable_build_systems returns empty list."""
    ext = ConcreteExtension()
    assert ext.get_applicable_build_systems("/some/path") == []


def test_extension_base_default_discover_modules():
    """Default discover_modules returns empty list."""
    ext = ConcreteExtension()
    assert ext.discover_modules("/some/path") == []


def test_extension_base_default_profiles():
    """Default get_profiles returns empty list."""
    ext = ConcreteExtension()
    assert ext.get_profiles("/some/path") == []


def test_extension_base_default_triage():
    """Default provides_triage returns None."""
    ext = ConcreteExtension()
    assert ext.provides_triage() is None


def test_extension_base_default_outline():
    """Default provides_outline returns None."""
    ext = ConcreteExtension()
    assert ext.provides_outline() is None


def test_extension_base_default_generate_profile_command():
    """Default generate_profile_command returns None."""
    ext = ConcreteExtension()
    assert ext.generate_profile_command("maven", "integration-tests", "it", {}) is None


# =============================================================================
# Tests for classify_profile()
# =============================================================================

def test_classify_profile_exact_match():
    """classify_profile matches exact pattern."""
    ext = ConcreteExtension()
    assert ext.classify_profile("pre-commit") == CMD_QUALITY_GATE
    assert ext.classify_profile("integration-tests") == CMD_INTEGRATION_TESTS


def test_classify_profile_case_insensitive():
    """classify_profile is case-insensitive."""
    ext = ConcreteExtension()
    assert ext.classify_profile("PRE-COMMIT") == CMD_QUALITY_GATE
    assert ext.classify_profile("PreCommit") == CMD_QUALITY_GATE


def test_classify_profile_substring():
    """classify_profile matches substring patterns."""
    ext = ConcreteExtension()
    # "my-integration-tests" contains "integration-tests"
    assert ext.classify_profile("my-integration-tests") == CMD_INTEGRATION_TESTS
    # "run-sonar-analysis" contains "sonar"
    assert ext.classify_profile("run-sonar-analysis") == CMD_QUALITY_GATE


def test_classify_profile_unknown():
    """classify_profile returns None for unknown patterns."""
    ext = ConcreteExtension()
    assert ext.classify_profile("unknown-profile") is None
    assert ext.classify_profile("my-custom-thing") is None


def test_classify_profile_empty():
    """classify_profile handles empty string."""
    ext = ConcreteExtension()
    assert ext.classify_profile("") is None


if __name__ == "__main__":
    import traceback

    tests = [
        test_cmd_constants_values,
        test_all_canonical_commands_contains_all,
        test_canonical_commands_structure,
        test_canonical_commands_required,
        test_canonical_commands_phases,
        test_profile_patterns_integration_tests,
        test_profile_patterns_quality_gate,
        test_profile_patterns_coverage,
        test_profile_patterns_performance,
        test_extension_base_abstract_methods,
        test_extension_base_default_build_systems,
        test_extension_base_default_applicable_build_systems,
        test_extension_base_default_discover_modules,
        test_extension_base_default_profiles,
        test_extension_base_default_triage,
        test_extension_base_default_outline,
        test_extension_base_default_generate_profile_command,
        test_classify_profile_exact_match,
        test_classify_profile_case_insensitive,
        test_classify_profile_substring,
        test_classify_profile_unknown,
        test_classify_profile_empty,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"FAILED: {test.__name__}")
            traceback.print_exc()
            print()

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
