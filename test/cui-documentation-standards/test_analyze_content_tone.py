#!/usr/bin/env python3
"""Tests for analyze-content-tone.py script.

Migrated from test-analyze-content-tone.sh - tests tone analysis of documentation.
"""

import json
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-documentation-standards', 'cui-documentation', 'analyze-content-tone.py')


# =============================================================================
# Tests
# =============================================================================

def test_help_flag():
    """Test --help flag works."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0, "--help flag works"


def test_analyze_sample_file():
    """Test analyzing sample AsciiDoc file with tone issues."""
    sample_content = """= Sample Documentation

== Introduction

Our powerful JWT library provides the best-in-class performance for token validation.
It's blazing-fast and enterprise-grade, making it the perfect solution for your needs.

== Features

The library is easy to use and implements OAuth 2.0.
It provides sub-millisecond validation with comprehensive security features.

Used by thousands of companies worldwide, this robust solution is production-ready
and supports all major frameworks.

== Performance

Faster than competitors with proven scalability.
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        f.write(sample_content)
        sample_file = Path(f.name)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_file = Path(f.name)

    try:
        result = run_script(
            SCRIPT_PATH,
            '--file', str(sample_file),
            '--output', str(output_file),
            '--pretty'
        )

        assert output_file.exists(), "Analysis completed"

        content = output_file.read_text()
        # Check for expected detection categories
        has_promotional = 'promotional' in content
        has_summary = 'total_issues' in content

        assert has_promotional or has_summary, "Detected promotional language or generated summary"
    finally:
        sample_file.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)


def test_directory_analysis():
    """Test directory analysis."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create sample files
        (temp_path / 'sample.adoc').write_text("""= Sample
== Section
This is factual content without promotional language.
The implementation follows RFC 6749.
""")
        (temp_path / 'another.adoc').write_text("""= Another Document
== Section
Technical documentation content.
""")

        result = run_script(
            SCRIPT_PATH,
            '--directory', str(temp_path),
            '--pretty'
        )

        assert result.returncode == 0, "Directory analysis works"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_help_flag,
        test_analyze_sample_file,
        test_directory_analysis,
    ])
    sys.exit(runner.run())
