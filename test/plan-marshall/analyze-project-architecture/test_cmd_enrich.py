#!/usr/bin/env python3
"""Tests for _cmd_enrich.py module."""

import json
import sys
import tempfile
from pathlib import Path

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / "marketplace" / "bundles" / "plan-marshall" / "skills" / "analyze-project-architecture" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from _cmd_enrich import (
    enrich_project,
    enrich_module,
    enrich_package,
    enrich_skills,
    enrich_dependencies,
    enrich_tip,
    enrich_insight,
    enrich_best_practice,
)
from _architecture_core import (
    DataNotFoundError,
    ModuleNotFoundError,
    save_derived_data,
    save_llm_enriched,
    load_llm_enriched,
)


# =============================================================================
# Helper Functions
# =============================================================================

def setup_test_project(tmpdir: str) -> None:
    """Create test derived-data.json and llm-enriched.json."""
    derived_data = {
        "project": {"name": "test-project", "root": tmpdir},
        "modules": {
            "module-a": {
                "name": "module-a",
                "build_systems": ["maven"],
                "paths": {"module": "module-a"},
                "metadata": {},
                "packages": {},
                "dependencies": [],
                "commands": {}
            }
        }
    }
    save_derived_data(derived_data, tmpdir)

    enriched_data = {
        "project": {"description": ""},
        "modules": {
            "module-a": {
                "responsibility": "",
                "purpose": "",
                "key_packages": {},
                "proposed_skill_domains": [],
                "key_dependencies": [],
                "internal_dependencies": [],
                "tips": [],
                "insights": [],
                "best_practices": []
            }
        }
    }
    save_llm_enriched(enriched_data, tmpdir)


# =============================================================================
# Tests for enrich_project
# =============================================================================

def test_enrich_project_updates_description():
    """enrich_project updates project description."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_project("Test project description", tmpdir)

        assert result["status"] == "success"
        assert result["updated"] == "project.description"

        # Verify file updated
        enriched = load_llm_enriched(tmpdir)
        assert enriched["project"]["description"] == "Test project description"


def test_enrich_project_missing_file_raises():
    """enrich_project raises DataNotFoundError when file missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Only create derived, not enriched
        save_derived_data({"project": {}, "modules": {}}, tmpdir)

        try:
            enrich_project("desc", tmpdir)
            assert False, "Should have raised DataNotFoundError"
        except DataNotFoundError:
            pass


# =============================================================================
# Tests for enrich_module
# =============================================================================

def test_enrich_module_updates_responsibility():
    """enrich_module updates module responsibility."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_module("module-a", "Core validation logic", None, tmpdir)

        assert result["status"] == "success"
        assert result["module"] == "module-a"
        assert "responsibility" in result["updated"]

        enriched = load_llm_enriched(tmpdir)
        assert enriched["modules"]["module-a"]["responsibility"] == "Core validation logic"


def test_enrich_module_updates_purpose():
    """enrich_module updates module purpose when provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_module("module-a", "Core logic", "library", tmpdir)

        assert "purpose" in result["updated"]

        enriched = load_llm_enriched(tmpdir)
        assert enriched["modules"]["module-a"]["purpose"] == "library"


def test_enrich_module_not_found_raises():
    """enrich_module raises ModuleNotFoundError for invalid module."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        try:
            enrich_module("nonexistent", "desc", None, tmpdir)
            assert False, "Should have raised ModuleNotFoundError"
        except ModuleNotFoundError:
            pass


# =============================================================================
# Tests for enrich_package
# =============================================================================

def test_enrich_package_adds_new():
    """enrich_package adds new key package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_package("module-a", "com.example.core", "Core package", tmpdir)

        assert result["status"] == "success"
        assert result["action"] == "added"

        enriched = load_llm_enriched(tmpdir)
        assert "com.example.core" in enriched["modules"]["module-a"]["key_packages"]
        assert enriched["modules"]["module-a"]["key_packages"]["com.example.core"]["description"] == "Core package"


def test_enrich_package_updates_existing():
    """enrich_package updates existing key package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        # Add first
        enrich_package("module-a", "com.example.core", "Original", tmpdir)

        # Update
        result = enrich_package("module-a", "com.example.core", "Updated", tmpdir)

        assert result["action"] == "updated"

        enriched = load_llm_enriched(tmpdir)
        assert enriched["modules"]["module-a"]["key_packages"]["com.example.core"]["description"] == "Updated"


# =============================================================================
# Tests for enrich_skills
# =============================================================================

def test_enrich_skills_sets_domains():
    """enrich_skills sets proposed skill domains."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        domains = ["pm-dev-java:java-core", "pm-dev-java:junit-core"]
        result = enrich_skills("module-a", domains, tmpdir)

        assert result["status"] == "success"
        assert result["proposed_skill_domains"] == domains

        enriched = load_llm_enriched(tmpdir)
        assert enriched["modules"]["module-a"]["proposed_skill_domains"] == domains


# =============================================================================
# Tests for enrich_dependencies
# =============================================================================

def test_enrich_dependencies_sets_key():
    """enrich_dependencies sets key dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        key_deps = ["org.example:dep1", "org.example:dep2"]
        result = enrich_dependencies("module-a", key_deps, None, tmpdir)

        assert result["status"] == "success"
        assert result["key_dependencies"] == key_deps

        enriched = load_llm_enriched(tmpdir)
        assert enriched["modules"]["module-a"]["key_dependencies"] == key_deps


def test_enrich_dependencies_sets_internal():
    """enrich_dependencies sets internal dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        internal_deps = ["module-b", "module-c"]
        result = enrich_dependencies("module-a", None, internal_deps, tmpdir)

        assert result["status"] == "success"
        assert result["internal_dependencies"] == internal_deps


def test_enrich_dependencies_sets_both():
    """enrich_dependencies can set both key and internal."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_dependencies("module-a", ["dep1"], ["mod-b"], tmpdir)

        assert "key_dependencies" in result
        assert "internal_dependencies" in result


# =============================================================================
# Tests for Array Append Commands
# =============================================================================

def test_enrich_tip_appends():
    """enrich_tip appends to tips array."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_tip("module-a", "Tip 1", tmpdir)
        assert result["tips"] == ["Tip 1"]

        result = enrich_tip("module-a", "Tip 2", tmpdir)
        assert result["tips"] == ["Tip 1", "Tip 2"]


def test_enrich_tip_no_duplicates():
    """enrich_tip does not add duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        enrich_tip("module-a", "Same tip", tmpdir)
        result = enrich_tip("module-a", "Same tip", tmpdir)

        assert result["tips"] == ["Same tip"]


def test_enrich_insight_appends():
    """enrich_insight appends to insights array."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_insight("module-a", "Insight 1", tmpdir)
        assert result["insights"] == ["Insight 1"]


def test_enrich_best_practice_appends():
    """enrich_best_practice appends to best_practices array."""
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_test_project(tmpdir)

        result = enrich_best_practice("module-a", "Practice 1", tmpdir)
        assert result["best_practices"] == ["Practice 1"]


if __name__ == "__main__":
    import traceback

    tests = [
        test_enrich_project_updates_description,
        test_enrich_project_missing_file_raises,
        test_enrich_module_updates_responsibility,
        test_enrich_module_updates_purpose,
        test_enrich_module_not_found_raises,
        test_enrich_package_adds_new,
        test_enrich_package_updates_existing,
        test_enrich_skills_sets_domains,
        test_enrich_dependencies_sets_key,
        test_enrich_dependencies_sets_internal,
        test_enrich_dependencies_sets_both,
        test_enrich_tip_appends,
        test_enrich_tip_no_duplicates,
        test_enrich_insight_appends,
        test_enrich_best_practice_appends,
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
