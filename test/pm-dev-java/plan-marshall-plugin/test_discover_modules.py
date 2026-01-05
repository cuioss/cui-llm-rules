#!/usr/bin/env python3
"""Unit tests for Maven module discovery parsing functions.

Tests the parsing functions with fixture data. These tests do NOT require Maven.

For integration tests that test full discover_modules flow against real Maven
projects, see test_discover_modules_integration.py.

Contract requirements tested:
- Only command-line activated profiles are included (Active: false)
- Profiles have id and canonical fields only (no activation field)
- Skip list filters out specified profiles
- Explicit mapping takes precedence over alias matching
- Alias matching uses CANONICAL_COMMANDS from extension_base.py
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
    _filter_command_line_profiles,
    _filter_skip_profiles,
    _map_canonical_profiles,
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
# Unit Tests: Raw Profile Parsing
# =============================================================================

def test_parse_profiles_extracts_all_raw_profiles():
    """Test that all profiles are extracted from help:all-profiles output."""
    log = get_sample_log()
    profiles = _parse_profiles_from_maven_output(log)

    profile_ids = [p["id"] for p in profiles]
    # Should include ALL profiles, even default-activated ones
    assert "pre-commit" in profile_ids
    assert "coverage" in profile_ids
    assert "integration-tests" in profile_ids
    assert "jdk17" in profile_ids  # default-activated
    assert "release" in profile_ids
    assert "native" in profile_ids
    assert len(profiles) == 6


def test_parse_profiles_includes_activation_status():
    """Test that raw profiles include is_active status."""
    log = get_sample_log()
    profiles = _parse_profiles_from_maven_output(log)

    by_id = {p["id"]: p for p in profiles}

    # Command-line activated (Active: false)
    assert by_id["pre-commit"]["is_active"] is False
    assert by_id["coverage"]["is_active"] is False
    # Default activated (Active: true)
    assert by_id["jdk17"]["is_active"] is True


# =============================================================================
# Unit Tests: Command-Line Activation Filter
# =============================================================================

def test_filter_command_line_excludes_default_activated():
    """Test that profiles with Active: true are filtered out."""
    raw_profiles = [
        {"id": "pre-commit", "is_active": False},
        {"id": "jdk17", "is_active": True},  # Should be excluded
        {"id": "coverage", "is_active": False},
    ]

    filtered = _filter_command_line_profiles(raw_profiles)

    profile_ids = [p["id"] for p in filtered]
    assert "pre-commit" in profile_ids
    assert "coverage" in profile_ids
    assert "jdk17" not in profile_ids  # Excluded
    assert len(filtered) == 2


def test_filter_command_line_removes_is_active_field():
    """Test that is_active field is removed after filtering."""
    raw_profiles = [
        {"id": "pre-commit", "is_active": False},
    ]

    filtered = _filter_command_line_profiles(raw_profiles)

    assert "is_active" not in filtered[0]


# =============================================================================
# Unit Tests: Skip List Filtering
# =============================================================================

def test_filter_skip_removes_listed_profiles():
    """Test that profiles in skip list are removed."""
    profiles = [
        {"id": "pre-commit"},
        {"id": "release"},
        {"id": "coverage"},
        {"id": "native"},
    ]
    skip_list = ["release", "native"]

    filtered = _filter_skip_profiles(profiles, skip_list)

    profile_ids = [p["id"] for p in filtered]
    assert "pre-commit" in profile_ids
    assert "coverage" in profile_ids
    assert "release" not in profile_ids
    assert "native" not in profile_ids
    assert len(filtered) == 2


def test_filter_skip_handles_empty_skip_list():
    """Test that empty skip list keeps all profiles."""
    profiles = [
        {"id": "pre-commit"},
        {"id": "release"},
    ]

    filtered = _filter_skip_profiles(profiles, [])

    assert len(filtered) == 2


def test_filter_skip_handles_none_skip_list():
    """Test that None skip list keeps all profiles."""
    profiles = [
        {"id": "pre-commit"},
        {"id": "release"},
    ]

    filtered = _filter_skip_profiles(profiles, None)

    assert len(filtered) == 2


def test_filter_skip_trims_whitespace():
    """Test that skip list entries are trimmed."""
    profiles = [
        {"id": "release"},
        {"id": "native"},
    ]
    skip_list = [" release ", "native"]

    filtered = _filter_skip_profiles(profiles, skip_list)

    assert len(filtered) == 0


# =============================================================================
# Unit Tests: Canonical Mapping
# =============================================================================

def test_map_canonical_uses_explicit_mapping_first():
    """Test that explicit mapping takes precedence over aliases."""
    profiles = [
        {"id": "pre-commit"},
        {"id": "javadoc"},  # Not in CANONICAL_COMMANDS aliases
    ]
    explicit_mapping = {
        "pre-commit": "quality-gate",
        "javadoc": "javadoc",  # CUI-specific, not in aliases
    }

    mapped = _map_canonical_profiles(profiles, explicit_mapping)

    by_id = {p["id"]: p for p in mapped}
    assert by_id["pre-commit"]["canonical"] == "quality-gate"
    assert by_id["javadoc"]["canonical"] == "javadoc"


def test_map_canonical_falls_back_to_aliases():
    """Test that alias matching is used when no explicit mapping."""
    profiles = [
        {"id": "coverage"},  # matches alias
        {"id": "integration-tests"},  # matches alias
    ]

    mapped = _map_canonical_profiles(profiles, {})

    by_id = {p["id"]: p for p in mapped}
    assert by_id["coverage"]["canonical"] == "coverage"
    assert by_id["integration-tests"]["canonical"] == "integration-tests"


def test_map_canonical_sets_none_for_unknown():
    """Test that unknown profiles get canonical=None."""
    profiles = [
        {"id": "custom-profile"},
        {"id": "release"},
    ]

    mapped = _map_canonical_profiles(profiles, {})

    by_id = {p["id"]: p for p in mapped}
    assert by_id["custom-profile"]["canonical"] is None
    assert by_id["release"]["canonical"] is None


def test_map_canonical_handles_empty_mapping():
    """Test that None mapping uses only aliases."""
    profiles = [
        {"id": "pre-commit"},
    ]

    mapped = _map_canonical_profiles(profiles, None)

    assert mapped[0]["canonical"] == "quality-gate"


# =============================================================================
# Unit Tests: Profile Classification (Alias Matching)
# =============================================================================

def test_classify_profile_quality_gate_aliases():
    """Test quality-gate profile classification via aliases."""
    # These are defined in CANONICAL_COMMANDS["quality-gate"]["aliases"]
    assert _classify_profile("pre-commit") == "quality-gate"
    assert _classify_profile("precommit") == "quality-gate"
    assert _classify_profile("sonar") == "quality-gate"
    assert _classify_profile("lint") == "quality-gate"
    assert _classify_profile("quality") == "quality-gate"


def test_classify_profile_coverage_aliases():
    """Test coverage profile classification via aliases."""
    # These are defined in CANONICAL_COMMANDS["coverage"]["aliases"]
    assert _classify_profile("coverage") == "coverage"
    assert _classify_profile("jacoco") == "coverage"


def test_classify_profile_integration_tests_aliases():
    """Test integration-tests profile classification via aliases."""
    # These are defined in CANONICAL_COMMANDS["integration-tests"]["aliases"]
    assert _classify_profile("integration-tests") == "integration-tests"
    assert _classify_profile("integration-test") == "integration-tests"
    assert _classify_profile("it") == "integration-tests"
    assert _classify_profile("e2e") == "integration-tests"


def test_classify_profile_performance_aliases():
    """Test performance profile classification via aliases."""
    # These are defined in CANONICAL_COMMANDS["performance"]["aliases"]
    assert _classify_profile("benchmark") == "performance"
    assert _classify_profile("jmh") == "performance"
    assert _classify_profile("perf") == "performance"


def test_classify_profile_unknown():
    """Test that unknown profiles return None canonical."""
    assert _classify_profile("custom-profile") is None
    assert _classify_profile("release") is None
    assert _classify_profile("native") is None
    assert _classify_profile("javadoc") is None  # Not in aliases


def test_classify_profile_no_substring_matching():
    """Test that partial/substring matching does NOT work.

    Only exact alias matches should work, not substring contains.
    """
    # "quality-check" should NOT match "quality" substring
    assert _classify_profile("quality-check") is None
    # "jacoco-report" should NOT match "jacoco" substring
    assert _classify_profile("jacoco-report") is None
    # "it-tests" should NOT match "it" substring
    assert _classify_profile("it-tests") is None


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
# Integration Tests: Full Profile Pipeline
# =============================================================================

def test_full_profile_pipeline():
    """Test the complete profile extraction -> filter -> skip -> map pipeline."""
    log = get_sample_log()

    # 1. Parse raw profiles
    raw_profiles = _parse_profiles_from_maven_output(log)
    assert len(raw_profiles) == 6

    # 2. Filter to command-line only
    cmd_line = _filter_command_line_profiles(raw_profiles)
    profile_ids = [p["id"] for p in cmd_line]
    assert "jdk17" not in profile_ids  # default-activated excluded
    assert len(cmd_line) == 5

    # 3. Apply skip list
    skip_list = ["release", "native"]
    filtered = _filter_skip_profiles(cmd_line, skip_list)
    assert len(filtered) == 3

    # 4. Map to canonical
    mapping = {"pre-commit": "quality-gate"}
    mapped = _map_canonical_profiles(filtered, mapping)

    by_id = {p["id"]: p for p in mapped}
    assert by_id["pre-commit"]["canonical"] == "quality-gate"
    assert by_id["coverage"]["canonical"] == "coverage"
    assert by_id["integration-tests"]["canonical"] == "integration-tests"

    # 5. Verify no activation field
    for profile in mapped:
        assert "activation" not in profile
        assert "is_active" not in profile


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

        # Raw profile parsing
        test_parse_profiles_extracts_all_raw_profiles,
        test_parse_profiles_includes_activation_status,

        # Command-line filter
        test_filter_command_line_excludes_default_activated,
        test_filter_command_line_removes_is_active_field,

        # Skip list filter
        test_filter_skip_removes_listed_profiles,
        test_filter_skip_handles_empty_skip_list,
        test_filter_skip_handles_none_skip_list,
        test_filter_skip_trims_whitespace,

        # Canonical mapping
        test_map_canonical_uses_explicit_mapping_first,
        test_map_canonical_falls_back_to_aliases,
        test_map_canonical_sets_none_for_unknown,
        test_map_canonical_handles_empty_mapping,

        # Profile classification (aliases)
        test_classify_profile_quality_gate_aliases,
        test_classify_profile_coverage_aliases,
        test_classify_profile_integration_tests_aliases,
        test_classify_profile_performance_aliases,
        test_classify_profile_unknown,
        test_classify_profile_no_substring_matching,

        # Dependency parsing
        test_parse_dependencies_extracts_direct_deps,
        test_parse_dependencies_format,
        test_parse_dependencies_correct_scopes,
        test_parse_dependencies_ignores_transitive,

        # Full pipeline
        test_full_profile_pipeline,
    ])
    sys.exit(runner.run())
