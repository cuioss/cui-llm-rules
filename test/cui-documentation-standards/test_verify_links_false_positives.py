#!/usr/bin/env python3
"""Tests for verify-links-false-positives.py script.

Migrated from test-verify-links-false-positives.sh - tests link classification.
"""

import json
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('cui-documentation-standards', 'cui-documentation', 'verify-links-false-positives.py')


# =============================================================================
# Tests
# =============================================================================

def test_help_flag():
    """Test --help flag works."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.returncode == 0, "--help flag works"


def test_classify_broken_links():
    """Test classification of broken links."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        input_data = {
            "issues": [
                {"file": "standards/security.adoc", "line": 42, "link": "<<owasp-top-10>>", "type": "broken_anchor"},
                {"file": "standards/security.adoc", "line": 89, "link": "http://localhost:8080/api", "type": "broken_link"},
                {"file": "requirements/spec.adoc", "line": 120, "link": "xref:missing-file.adoc[Missing]", "type": "broken_file_link"},
                {"file": "guide.adoc", "line": 56, "link": "file:///local/path/doc.pdf", "type": "broken_link"}
            ]
        }
        json.dump(input_data, f)
        input_file = Path(f.name)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_file = Path(f.name)

    try:
        result = run_script(
            SCRIPT_PATH,
            '--input', str(input_file),
            '--output', str(output_file),
            '--pretty'
        )

        assert output_file.exists(), "Classification completed"

        content = output_file.read_text()
        # Check for expected categories
        has_categories = 'likely-false-positive' in content or 'must-verify-manual' in content
        assert has_categories, "Found expected categories in output"
    finally:
        input_file.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)


def test_stdin_stdout_processing():
    """Test stdin/stdout processing."""
    input_data = json.dumps({
        "issues": [
            {"file": "test.adoc", "line": 1, "link": "<<anchor>>", "type": "broken_anchor"}
        ]
    })

    result = run_script(SCRIPT_PATH, '--pretty', input_data=input_data)
    assert result.returncode == 0, "Stdin/stdout works"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_help_flag,
        test_classify_broken_links,
        test_stdin_stdout_processing,
    ])
    sys.exit(runner.run())
