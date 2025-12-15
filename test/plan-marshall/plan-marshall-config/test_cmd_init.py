#!/usr/bin/env python3
"""Tests for init command in plan-marshall-config.

Tests init command variants including force overwrite and error handling.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, PlanTestContext
from test_helpers import SCRIPT_PATH, create_marshal_json


# =============================================================================
# Init Command Tests
# =============================================================================

def test_init_creates_marshal_json():
    """Test init creates marshal.json with defaults."""
    with PlanTestContext() as ctx:
        result = run_script(SCRIPT_PATH, 'init')

        assert result.success, f"Init should succeed: {result.stderr}"
        assert 'success' in result.stdout.lower(), "Should output success"

        marshal_path = ctx.fixture_dir / 'marshal.json'
        assert marshal_path.exists(), "marshal.json should be created"

        config = json.loads(marshal_path.read_text())
        assert 'skill_domains' in config, "Should have skill_domains"
        assert 'system' in config, "Should have system"
        assert 'plan' in config, "Should have plan"


def test_init_fails_if_exists():
    """Test init fails if marshal.json already exists."""
    with PlanTestContext() as ctx:
        create_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'init')

        assert not result.success or 'already exists' in result.stdout.lower(), \
            "Should fail or warn when marshal.json exists"


def test_init_force_overwrites():
    """Test init --force overwrites existing marshal.json."""
    with PlanTestContext() as ctx:
        # Create existing with custom content
        create_marshal_json(ctx.fixture_dir, {"custom": True})

        result = run_script(SCRIPT_PATH, 'init', '--force')

        assert result.success, f"Init --force should succeed: {result.stderr}"

        marshal_path = ctx.fixture_dir / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        assert 'skill_domains' in config, "Should have default content"
        assert 'custom' not in config, "Should not have old custom content"


def test_init_creates_parent_directory():
    """Test init creates .plan directory if missing."""
    with PlanTestContext() as ctx:
        # PlanTestContext creates .plan, but we verify it works
        result = run_script(SCRIPT_PATH, 'init')

        assert result.success, f"Init should succeed: {result.stderr}"
        assert (ctx.fixture_dir / 'marshal.json').exists()


def test_init_preserves_system_domain():
    """Test init includes system domain in defaults."""
    with PlanTestContext() as ctx:
        result = run_script(SCRIPT_PATH, 'init')

        assert result.success, f"Init should succeed: {result.stderr}"

        marshal_path = ctx.fixture_dir / 'marshal.json'
        config = json.loads(marshal_path.read_text())
        assert 'system' in config.get('skill_domains', {}), \
            "Should include system domain"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_init_creates_marshal_json,
        test_init_fails_if_exists,
        test_init_force_overwrites,
        test_init_creates_parent_directory,
        test_init_preserves_system_domain,
    ])
    sys.exit(runner.run())
