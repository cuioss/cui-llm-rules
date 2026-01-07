#!/usr/bin/env python3
"""Integration tests for Maven discover_modules().

Tests Maven module discovery against real projects in the local git directory.
Results are persisted to .plan/temp/test-results-maven/ for inspection.

Run with:
    python3 test/pm-dev-java/integration/discover_modules/test_maven_discover_modules.py
"""

import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "test"))
sys.path.insert(0, str(PROJECT_ROOT / "marketplace" / "bundles" / "plan-marshall" / "skills" / "extension-api" / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "marketplace" / "bundles" / "pm-dev-java" / "skills" / "plan-marshall-plugin"))

from integration_common import (
    INTEGRATION_TEST_OUTPUT_DIR,
    IntegrationTestContext,
    TestProject,
    assert_has_root_aggregator,
    assert_maven_module_structure,
    assert_no_null_values,
    assert_paths_exist,
)
from extension import Extension


# =============================================================================
# Test Projects Configuration
# =============================================================================

# Projects relative to git directory (parent of cui-llm-rules)
TEST_PROJECTS = [
    TestProject(
        name="cui-http",
        relative_path="cui-http",
        description="Single-module Maven library"
    ),
    TestProject(
        name="cui-java-tools",
        relative_path="cui-java-tools",
        description="Single-module Maven utility library"
    ),
    TestProject(
        name="nifi-extensions",
        relative_path="nifi-extensions",
        description="Multi-module Maven project with hybrid Java+npm"
    ),
    TestProject(
        name="OAuth-Sheriff",
        relative_path="OAuth-Sheriff",
        description="Multi-module Maven Quarkus project"
    ),
]

# Output directory for results
OUTPUT_DIR = INTEGRATION_TEST_OUTPUT_DIR / "discover_modules-maven"


# =============================================================================
# Integration Tests
# =============================================================================

def run_integration_tests() -> int:
    """Run all Maven discover_modules integration tests.

    Returns:
        0 if all tests pass, 1 if any fail
    """
    ext = Extension()
    all_passed = True
    test_count = 0
    pass_count = 0

    with IntegrationTestContext(OUTPUT_DIR, clean_before=True) as ctx:
        print("Maven discover_modules() Integration Tests")
        print("=" * 60)
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"Git directory: {ctx.git_dir}")
        print()

        for project in TEST_PROJECTS:
            print(f"\n--- {project.name} ---")
            print(f"Path: {project.relative_path}")
            print(f"Description: {project.description}")

            # Check if project exists
            if not ctx.validate_project(project):
                print(f"  SKIP: Project not found")
                continue

            test_count += 1
            project_path = project.absolute_path(ctx.git_dir)

            # Run discovery
            try:
                modules = ext.discover_modules(str(project_path))
                print(f"  Found: {len(modules)} module(s)")

                # Save result
                output_path = ctx.save_result(project, modules)
                print(f"  Saved: {output_path.name}")

                # Run assertions
                errors = []

                # Assert no null values (readme and description can be null)
                nulls = assert_no_null_values(
                    modules,
                    allowed_null_suffixes=[".readme", ".description"]
                )
                if nulls:
                    errors.append(f"Null values found at: {', '.join(nulls)}")

                # Assert paths exist
                missing = assert_paths_exist(modules, project_path)
                if missing:
                    errors.extend(missing)

                # Assert Maven-specific structure
                maven_errors = assert_maven_module_structure(modules)
                if maven_errors:
                    errors.extend(maven_errors)

                # Assert multi-module projects have root aggregator (if root pom.xml exists)
                root_errors = assert_has_root_aggregator(
                    modules, project_path, ["pom.xml"]
                )
                if root_errors:
                    errors.extend(root_errors)

                # Report results
                if errors:
                    print(f"  FAIL: {len(errors)} error(s)")
                    for err in errors:
                        print(f"    - {err}")
                    ctx.errors.extend([f"{project.name}: {e}" for e in errors])
                    all_passed = False
                else:
                    print(f"  PASS: All assertions passed")
                    pass_count += 1

                # Print module summary
                for mod in modules:
                    mod_name = mod.get("name", "?")
                    mod_path = mod.get("paths", {}).get("module", "?")
                    print(f"    - {mod_name} ({mod_path})")

            except Exception as e:
                print(f"  ERROR: {e}")
                ctx.errors.append(f"{project.name}: {e}")
                all_passed = False

        # Print summary
        ctx.print_summary()
        print(f"\nTests: {pass_count}/{test_count} passed")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())
