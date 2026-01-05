#!/usr/bin/env python3
"""Unit tests for Maven module discovery parsing functions.

Tests the parsing functions with fixture data. These tests do NOT require Maven.

For integration tests that test full discover_modules flow against real Maven
projects, see test_discover_modules_integration.py.

Contract requirements tested:
- metadata.profiles: array with id, canonical, activation
- dependencies: string format "groupId:artifactId:scope" (not objects)
- coordinates: parsed from dependency:tree header
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Add extension directories to path for import
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
EXTENSION_BASE_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'
SCRIPTS_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'pm-dev-java' / 'skills' / 'plan-marshall-plugin' / 'scripts'
FIXTURES_DIR = Path(__file__).parent / 'fixtures'
sys.path.insert(0, str(EXTENSION_BASE_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

# Import parsing functions directly
from maven_cmd_discover import (
    _parse_coordinates_from_maven_output,
    _parse_profiles_from_maven_output,
    _parse_dependencies_from_maven_output,
    _classify_profile,
)


# =============================================================================
# Fixtures
# =============================================================================

def load_fixture(name: str) -> str:
    """Load fixture file content."""
    fixture_path = FIXTURES_DIR / name
    return fixture_path.read_text()


SAMPLE_LOG = None  # Lazy loaded


def get_sample_log() -> str:
    """Get sample Maven discovery log (lazy loaded)."""
    global SAMPLE_LOG
    if SAMPLE_LOG is None:
        SAMPLE_LOG = load_fixture('sample-maven-discovery.log')
    return SAMPLE_LOG


# =============================================================================
# Unit Tests: Coordinate Parsing
# =============================================================================

def test_parse_coordinates_extracts_group_id():
    """Test that group_id is extracted from dependency:tree header."""
    log = get_sample_log()
    coords = _parse_coordinates_from_maven_output(log)

    assert coords.get("group_id") == "com.example"


def test_parse_coordinates_extracts_artifact_id():
    """Test that artifact_id is extracted from dependency:tree header."""
    log = get_sample_log()
    coords = _parse_coordinates_from_maven_output(log)

    assert coords.get("artifact_id") == "my-app"


def test_parse_coordinates_extracts_packaging():
    """Test that packaging is extracted from dependency:tree header."""
    log = get_sample_log()
    coords = _parse_coordinates_from_maven_output(log)

    assert coords.get("packaging") == "jar"


def test_parse_coordinates_ignores_dependency_lines():
    """Test that dependency lines (with +- prefix) are not parsed as coordinates."""
    log = """[INFO] com.example:parent:pom:1.0.0
[INFO] +- com.example:child:jar:1.0.0:compile
"""
    coords = _parse_coordinates_from_maven_output(log)

    # Should get parent coords, not child
    assert coords.get("artifact_id") == "parent"
    assert coords.get("packaging") == "pom"


def test_parse_coordinates_handles_empty_log():
    """Test graceful handling of empty log."""
    coords = _parse_coordinates_from_maven_output("")
    assert coords == {}


# =============================================================================
# Unit Tests: Profile Parsing
# =============================================================================

def test_parse_profiles_extracts_all_profiles():
    """Test that all profiles are extracted from help:all-profiles output."""
    log = get_sample_log()
    profiles = _parse_profiles_from_maven_output(log)

    profile_ids = [p["id"] for p in profiles]
    assert "pre-commit" in profile_ids
    assert "coverage" in profile_ids
    assert "integration-tests" in profile_ids
    assert len(profiles) == 3


def test_parse_profiles_has_required_fields():
    """Contract: each profile must have id, canonical, activation."""
    log = get_sample_log()
    profiles = _parse_profiles_from_maven_output(log)

    for profile in profiles:
        assert "id" in profile, "profile must have 'id'"
        assert "canonical" in profile, "profile must have 'canonical'"
        assert "activation" in profile, "profile must have 'activation'"


def test_parse_profiles_classifies_canonical():
    """Test that profiles are classified to canonical names."""
    log = get_sample_log()
    profiles = _parse_profiles_from_maven_output(log)

    by_id = {p["id"]: p for p in profiles}

    assert by_id["pre-commit"]["canonical"] == "quality-gate"
    assert by_id["coverage"]["canonical"] == "coverage"
    assert by_id["integration-tests"]["canonical"] == "integration-tests"


def test_classify_profile_quality_gate():
    """Test quality-gate profile classification."""
    assert _classify_profile("pre-commit") == "quality-gate"
    assert _classify_profile("quality-check") == "quality-gate"
    assert _classify_profile("sonar") == "quality-gate"


def test_classify_profile_coverage():
    """Test coverage profile classification."""
    assert _classify_profile("coverage") == "coverage"
    assert _classify_profile("jacoco-report") == "coverage"


def test_classify_profile_integration_tests():
    """Test integration-tests profile classification."""
    assert _classify_profile("integration-tests") == "integration-tests"
    assert _classify_profile("it-tests") == "integration-tests"
    assert _classify_profile("e2e-tests") == "integration-tests"


def test_classify_profile_unknown():
    """Test that unknown profiles return None canonical."""
    assert _classify_profile("custom-profile") is None
    assert _classify_profile("release") is None


# =============================================================================
# Unit Tests: Dependency Parsing
# =============================================================================

def test_parse_dependencies_extracts_direct_deps():
    """Test that direct dependencies are extracted."""
    log = get_sample_log()
    deps = _parse_dependencies_from_maven_output(log)

    assert len(deps) == 3


def test_parse_dependencies_format():
    """Contract: dependencies must be strings in format 'groupId:artifactId:scope'."""
    log = get_sample_log()
    deps = _parse_dependencies_from_maven_output(log)

    for dep in deps:
        assert isinstance(dep, str), f"dependency must be string, got {type(dep)}"
        parts = dep.split(":")
        assert len(parts) == 3, f"dependency must be 'groupId:artifactId:scope', got '{dep}'"


def test_parse_dependencies_correct_scopes():
    """Test that dependency scopes are correctly extracted."""
    log = get_sample_log()
    deps = _parse_dependencies_from_maven_output(log)

    assert "org.junit.jupiter:junit-jupiter:test" in deps
    assert "com.google.guava:guava:compile" in deps
    assert "org.projectlombok:lombok:provided" in deps


def test_parse_dependencies_ignores_transitive():
    """Test that transitive dependencies (with |) are ignored."""
    log = """[INFO] com.example:my-app:jar:1.0.0
[INFO] +- com.example:direct:jar:1.0.0:compile
[INFO] |  \\- com.example:transitive:jar:1.0.0:compile
"""
    deps = _parse_dependencies_from_maven_output(log)

    assert len(deps) == 1
    assert "com.example:direct:compile" in deps


# =============================================================================
# Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Coordinate parsing
        test_parse_coordinates_extracts_group_id,
        test_parse_coordinates_extracts_artifact_id,
        test_parse_coordinates_extracts_packaging,
        test_parse_coordinates_ignores_dependency_lines,
        test_parse_coordinates_handles_empty_log,

        # Profile parsing
        test_parse_profiles_extracts_all_profiles,
        test_parse_profiles_has_required_fields,
        test_parse_profiles_classifies_canonical,
        test_classify_profile_quality_gate,
        test_classify_profile_coverage,
        test_classify_profile_integration_tests,
        test_classify_profile_unknown,

        # Dependency parsing
        test_parse_dependencies_extracts_direct_deps,
        test_parse_dependencies_format,
        test_parse_dependencies_correct_scopes,
        test_parse_dependencies_ignores_transitive,
    ])
    sys.exit(runner.run())
