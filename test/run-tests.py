#!/usr/bin/env python3
"""
Central test runner for cui-llm-rules.

Usage:
    python3 test/run-tests.py                    # Run all tests
    python3 test/run-tests.py test/pm-workflow/     # Run tests in directory
    python3 test/run-tests.py test/pm-workflow/plan-files/test_parse_plan.py  # Run single test
"""

import subprocess
import sys
from pathlib import Path

TEST_ROOT = Path(__file__).parent


def find_test_files(path: Path) -> list[Path]:
    """Find all test files in a path."""
    if path.is_file():
        return [path] if path.name.startswith('test_') and path.suffix == '.py' else []
    return sorted(path.rglob('test_*.py'))


def run_test(test_file: Path) -> tuple[bool, str]:
    """Run a single test file. Returns (success, output)."""
    result = subprocess.run(
        [sys.executable, str(test_file)],
        capture_output=True,
        text=True,
        cwd=TEST_ROOT.parent
    )
    output = result.stdout + result.stderr
    return result.returncode == 0, output


def main():
    # Determine test path
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if not target.is_absolute():
            target = TEST_ROOT.parent / target
    else:
        target = TEST_ROOT

    if not target.exists():
        print(f"Error: Path not found: {target}")
        sys.exit(1)

    # Find test files
    test_files = find_test_files(target)
    if not test_files:
        print(f"No test files found in: {target}")
        sys.exit(1)

    print(f"Running {len(test_files)} test file(s)...")
    print("=" * 60)

    passed = 0
    failed = 0
    failed_tests = []

    for test_file in test_files:
        relative_path = test_file.relative_to(TEST_ROOT.parent)
        success, output = run_test(test_file)

        if success:
            passed += 1
            print(f"  \u2713 {relative_path}")
        else:
            failed += 1
            failed_tests.append((relative_path, output))
            print(f"  \u2717 {relative_path}")

    print("=" * 60)
    print(f"Passed: {passed}, Failed: {failed}")

    # Show failure details
    if failed_tests:
        print("\nFailure details:")
        for path, output in failed_tests:
            print(f"\n--- {path} ---")
            print(output)

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
