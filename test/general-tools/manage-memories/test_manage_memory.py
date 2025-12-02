#!/usr/bin/env python3
"""Tests for manage-memory.py script.

Migrated from test-manage-memory.sh - tests memory layer CRUD operations
including save, load, list, query, and cleanup.
"""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Script under test
SCRIPT_PATH = get_script_path('general-tools', 'manage-memories', 'manage-memory.py')


# =============================================================================
# Test Helpers
# =============================================================================

class TempDirContext:
    """Context manager for tests that need a fresh temp directory."""

    def __init__(self):
        self.temp_dir = None
        self.old_cwd = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)


def run_memory_script(*args):
    """Run the memory script with arguments."""
    proc = subprocess.run(
        ['python3', str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True
    )
    return proc


def parse_json(output):
    """Parse JSON from output."""
    import json
    return json.loads(output)


# =============================================================================
# Tests
# =============================================================================

def test_save_creates_dirs():
    """Test save creates directories on-the-fly."""
    with TempDirContext() as temp_dir:
        result = run_memory_script(
            'save', '--category', 'context',
            '--identifier', 'test-feature',
            '--content', '{"notes": "Testing"}'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        assert 'context' in data.get('path', ''), "Path should contain context"

        # Verify directory was created (uses .plan/memory, not .claude/memory)
        assert (temp_dir / '.plan' / 'memory' / 'context').is_dir(), \
            "Context directory should be created"


def test_save_context():
    """Test save to context category."""
    with TempDirContext():
        result = run_memory_script(
            'save', '--category', 'context',
            '--identifier', 'test-feature',
            '--content', '{"decisions": ["Use JWT"]}'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        assert 'context' in data.get('path', ''), "Path should contain context"


def test_save_handoffs():
    """Test save to handoffs category."""
    with TempDirContext():
        result = run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'task-42',
            '--content', '{"task": "Auth feature", "progress": "50%"}'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        assert 'handoffs' in data.get('path', ''), "Path should contain handoffs"


def test_load():
    """Test load memory file."""
    with TempDirContext():
        # First save
        run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'load-test',
            '--content', '{"value": 123}'
        )

        result = run_memory_script(
            'load', '--category', 'handoffs',
            '--identifier', 'load-test'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        assert data.get('content', {}).get('value') == 123, "Content value should be 123"


def test_load_has_meta():
    """Test load includes meta envelope."""
    with TempDirContext():
        run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'meta-test',
            '--content', '{"test": true}'
        )

        result = run_memory_script(
            'load', '--category', 'handoffs',
            '--identifier', 'meta-test'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        meta = data.get('meta', {})
        assert 'created' in meta, "Meta should have created"
        assert meta.get('category') == 'handoffs', "Meta category should be handoffs"


def test_list_category():
    """Test list files in category."""
    with TempDirContext():
        # Save a few files
        run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'list-test-1',
            '--content', '{}'
        )
        run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'list-test-2',
            '--content', '{}'
        )

        result = run_memory_script('list', '--category', 'handoffs')
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        assert data.get('count', 0) >= 2, "Should find at least 2 files"


def test_list_all():
    """Test list all categories."""
    with TempDirContext():
        # Create at least one file
        run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'list-all-test',
            '--content', '{}'
        )

        result = run_memory_script('list')
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"


def test_query_pattern():
    """Test query by pattern."""
    with TempDirContext():
        run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'query-auth-test',
            '--content', '{}'
        )
        run_memory_script(
            'save', '--category', 'handoffs',
            '--identifier', 'query-data-test',
            '--content', '{}'
        )

        result = run_memory_script(
            'query', '--pattern', 'query-auth*',
            '--category', 'handoffs'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        assert data.get('count', 0) >= 1, "Should find at least 1 match"


def test_cleanup():
    """Test cleanup old files."""
    with TempDirContext() as temp_dir:
        # Create a file with an old created timestamp directly in the JSON
        # Uses .plan/memory, not .claude/memory
        memory_dir = temp_dir / '.plan' / 'memory' / 'context'
        memory_dir.mkdir(parents=True)
        (memory_dir / 'old-cleanup-test.json').write_text('''{
  "meta": {
    "created": "2020-01-01T00:00:00Z",
    "category": "context",
    "summary": "cleanup-test"
  },
  "content": {}
}''')

        result = run_memory_script(
            'cleanup', '--category', 'context',
            '--older-than', '1d'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        assert data.get('removed_count', 0) >= 1, "Should remove at least 1 file"


def test_load_not_found():
    """Test load non-existent file returns error."""
    with TempDirContext():
        result = run_memory_script(
            'load', '--category', 'handoffs',
            '--identifier', 'nonexistent'
        )
        # Script may output to stderr for errors
        output = result.stdout if result.stdout.strip() else result.stderr
        data = parse_json(output)

        assert data.get('success') is False, "Should fail for non-existent file"


def test_invalid_category():
    """Test invalid category returns error."""
    with TempDirContext():
        result = run_memory_script(
            'save', '--category', 'invalid',
            '--identifier', 'test',
            '--content', '{}'
        )

        combined = result.stdout.lower() + result.stderr.lower()
        assert 'invalid choice' in combined, "Should show invalid choice error"


def test_context_date_prefix():
    """Test context files get date prefix."""
    with TempDirContext():
        import re
        result = run_memory_script(
            'save', '--category', 'context',
            '--identifier', 'date-prefix-test',
            '--content', '{}'
        )
        data = parse_json(result.stdout)

        assert data.get('success') is True, "Should succeed"
        identifier = data.get('identifier', '')
        assert re.search(r'\d{4}-\d{2}-\d{2}', identifier), \
            "Identifier should have date prefix"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_save_creates_dirs,
        test_save_context,
        test_save_handoffs,
        test_load,
        test_load_has_meta,
        test_list_category,
        test_list_all,
        test_query_pattern,
        test_cleanup,
        test_load_not_found,
        test_invalid_category,
        test_context_date_prefix,
    ])
    sys.exit(runner.run())
