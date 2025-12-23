#!/usr/bin/env python3
"""Tests for discover_domains.py script."""

import json
import os
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('plan-marshall', 'domain-extension-api', 'discover_domains.py')


class MockPluginCache:
    """Context manager for creating mock plugin cache with test manifests."""

    def __init__(self):
        self.temp_dir = None
        self.original_env = None

    def __enter__(self):
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp(prefix='test-plugin-cache-'))
        self.original_env = os.environ.get('PLUGIN_CACHE_PATH')
        os.environ['PLUGIN_CACHE_PATH'] = str(self.temp_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_env is not None:
            os.environ['PLUGIN_CACHE_PATH'] = self.original_env
        else:
            os.environ.pop('PLUGIN_CACHE_PATH', None)

        # Cleanup temp directory
        import shutil
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_domain_bundle(self, bundle_name: str, domain_key: str, domain_name: str,
                            has_outline: bool = False, has_triage: bool = False) -> Path:
        """Create a mock domain bundle with plan-marshall-plugin skill."""
        bundle_dir = self.temp_dir / bundle_name / "1.0.0"
        manifest_dir = bundle_dir / "skills" / "plan-marshall-plugin"
        manifest_dir.mkdir(parents=True)

        # Create SKILL.md
        skill_md = manifest_dir / "SKILL.md"
        skill_md.write_text(f"""---
name: plan-marshall-plugin
description: Domain manifest for {domain_name}
---

# Plan-Marshall Plugin

Domain manifest for {domain_name}.
""")

        # Create plugin.json
        manifest = {
            "$schema": "https://example.com/domain-manifest-v1.json",
            "domain": {
                "key": domain_key,
                "name": domain_name,
                "description": f"Test domain: {domain_name}"
            },
            "profiles": {
                "core": {
                    "defaults": [f"{bundle_name}:test-skill"],
                    "optionals": []
                }
            }
        }

        if has_outline or has_triage:
            manifest["extensions"] = {}
            if has_outline:
                manifest["extensions"]["outline"] = f"{bundle_name}:outline-ext"
            if has_triage:
                manifest["extensions"]["triage"] = f"{bundle_name}:triage-ext"

        plugin_json = manifest_dir / "plugin.json"
        plugin_json.write_text(json.dumps(manifest, indent=2))

        return bundle_dir

    def create_supplement_bundle(self, bundle_name: str, target_domain: str,
                                 description: str) -> Path:
        """Create a mock supplement bundle with plan-marshall-plugin skill."""
        bundle_dir = self.temp_dir / bundle_name / "1.0.0"
        manifest_dir = bundle_dir / "skills" / "plan-marshall-plugin"
        manifest_dir.mkdir(parents=True)

        # Create SKILL.md
        skill_md = manifest_dir / "SKILL.md"
        skill_md.write_text(f"""---
name: plan-marshall-plugin
description: Supplement for {target_domain}
---

# Plan-Marshall Plugin

Supplement for {target_domain}.
""")

        # Create plugin.json
        manifest = {
            "$schema": "https://example.com/domain-supplements-v1.json",
            "supplements": {
                "domain": target_domain,
                "description": description,
                "skills": {
                    "core": {
                        "defaults": [],
                        "optionals": [f"{bundle_name}:test-skill"]
                    }
                }
            }
        }

        plugin_json = manifest_dir / "plugin.json"
        plugin_json.write_text(json.dumps(manifest, indent=2))

        return bundle_dir


def test_discover_help():
    """Test --help flag."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.success, f"Script failed: {result.stderr}"
    assert 'discover' in result.stdout
    assert 'list-bundles' in result.stdout


def test_discover_empty_cache():
    """Test discovery with empty/non-existent cache."""
    with MockPluginCache() as cache:
        result = run_script(SCRIPT_PATH, 'discover')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'status: success' in result.stdout
        assert 'domains_found: 0' in result.stdout
        assert 'supplements_found: 0' in result.stdout


def test_discover_single_domain():
    """Test discovery with one domain bundle."""
    with MockPluginCache() as cache:
        cache.create_domain_bundle('test-bundle', 'test', 'Test Domain')

        result = run_script(SCRIPT_PATH, 'discover')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'domains_found: 1' in result.stdout
        assert 'test\tTest Domain\ttest-bundle' in result.stdout


def test_discover_domain_with_extensions():
    """Test discovery of domain with outline and triage extensions."""
    with MockPluginCache() as cache:
        cache.create_domain_bundle(
            'java-bundle', 'java', 'Java Development',
            has_outline=True, has_triage=True
        )

        result = run_script(SCRIPT_PATH, 'discover')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'java\tJava Development\tjava-bundle\ttrue\ttrue' in result.stdout


def test_discover_supplement():
    """Test discovery of supplement bundle."""
    with MockPluginCache() as cache:
        cache.create_supplement_bundle(
            'test-supplement', 'java', 'Test supplement for Java'
        )

        result = run_script(SCRIPT_PATH, 'discover')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'supplements_found: 1' in result.stdout
        assert 'java\ttest-supplement\tTest supplement for Java' in result.stdout


def test_discover_multiple_bundles():
    """Test discovery of multiple domains and supplements."""
    with MockPluginCache() as cache:
        cache.create_domain_bundle('java-bundle', 'java', 'Java Development', True, True)
        cache.create_domain_bundle('js-bundle', 'javascript', 'JavaScript Development')
        cache.create_supplement_bundle('java-cui', 'java', 'CUI Java patterns')

        result = run_script(SCRIPT_PATH, 'discover')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'domains_found: 2' in result.stdout
        assert 'supplements_found: 1' in result.stdout


def test_list_bundles():
    """Test list-bundles subcommand."""
    with MockPluginCache() as cache:
        cache.create_domain_bundle('test-domain', 'test', 'Test Domain')
        cache.create_supplement_bundle('test-supplement', 'test', 'Test Supplement')

        result = run_script(SCRIPT_PATH, 'list-bundles')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'bundles_found: 2' in result.stdout
        assert 'test-domain\tdomain' in result.stdout
        assert 'test-supplement\tsupplement' in result.stdout


if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_discover_help,
        test_discover_empty_cache,
        test_discover_single_domain,
        test_discover_domain_with_extensions,
        test_discover_supplement,
        test_discover_multiple_bundles,
        test_list_bundles,
    ])
    sys.exit(runner.run())
