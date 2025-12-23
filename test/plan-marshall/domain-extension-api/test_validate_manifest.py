#!/usr/bin/env python3
"""Tests for validate_manifest.py script."""

import json
import os
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('plan-marshall', 'domain-extension-api', 'validate_manifest.py')


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

    def create_bundle_with_manifest(self, bundle_name: str, manifest: dict) -> Path:
        """Create a bundle with a custom manifest."""
        bundle_dir = self.temp_dir / bundle_name / "1.0.0"
        manifest_dir = bundle_dir / "skills" / "plan-marshall-plugin"
        manifest_dir.mkdir(parents=True)

        # Create SKILL.md
        skill_md = manifest_dir / "SKILL.md"
        skill_md.write_text("""---
name: plan-marshall-plugin
description: Test manifest
---

# Plan-Marshall Plugin
""")

        # Create plugin.json
        plugin_json = manifest_dir / "plugin.json"
        plugin_json.write_text(json.dumps(manifest, indent=2))

        return bundle_dir

    def create_bundle_with_skill(self, bundle_name: str, skill_name: str) -> Path:
        """Create a skill directory in a bundle."""
        bundle_dir = self.temp_dir / bundle_name / "1.0.0"
        skill_dir = bundle_dir / "skills" / skill_name
        skill_dir.mkdir(parents=True)

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(f"""---
name: {skill_name}
description: Test skill
---

# {skill_name}
""")

        return skill_dir


def test_validate_help():
    """Test --help flag."""
    result = run_script(SCRIPT_PATH, '--help')
    assert result.success, f"Script failed: {result.stderr}"
    assert 'validate' in result.stdout


def test_validate_bundle_not_found():
    """Test validation of non-existent bundle."""
    with MockPluginCache():
        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'nonexistent')
        assert not result.success
        assert 'Bundle not found' in result.stderr


def test_validate_no_plan_marshall_plugin():
    """Test validation when bundle has no plan-marshall-plugin skill."""
    with MockPluginCache() as cache:
        # Create bundle without plan-marshall-plugin skill
        bundle_dir = cache.temp_dir / "test-bundle" / "1.0.0"
        bundle_dir.mkdir(parents=True)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert 'No plan-marshall-plugin skill found' in result.stderr


def test_validate_valid_domain_manifest():
    """Test validation of a valid domain manifest."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-manifest-v1.json",
            "domain": {
                "key": "java",
                "name": "Java Development",
                "description": "Java patterns"
            },
            "profiles": {
                "core": {
                    "defaults": ["test-bundle:java-core"],
                    "optionals": []
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)
        cache.create_bundle_with_skill('test-bundle', 'java-core')

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'status: success' in result.stdout
        assert 'type: domain' in result.stdout
        assert 'domain: java' in result.stdout
        assert 'manifest: valid' in result.stdout


def test_validate_domain_missing_key():
    """Test validation of domain manifest without key."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-manifest-v1.json",
            "domain": {
                "name": "Java Development"
            },
            "profiles": {
                "core": {
                    "defaults": [],
                    "optionals": []
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert "Missing 'domain.key'" in result.stdout


def test_validate_domain_missing_core_profile():
    """Test validation of domain manifest without core profile."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-manifest-v1.json",
            "domain": {
                "key": "java",
                "name": "Java Development"
            },
            "profiles": {
                "implementation": {
                    "defaults": [],
                    "optionals": []
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert "Missing required profile: 'core'" in result.stdout


def test_validate_domain_invalid_profile_name():
    """Test validation of domain manifest with invalid profile name."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-manifest-v1.json",
            "domain": {
                "key": "java",
                "name": "Java Development"
            },
            "profiles": {
                "core": {
                    "defaults": [],
                    "optionals": []
                },
                "invalid-profile": {
                    "defaults": [],
                    "optionals": []
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert "Invalid profile name: 'invalid-profile'" in result.stdout


def test_validate_domain_invalid_skill_reference():
    """Test validation of domain manifest with invalid skill reference format."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-manifest-v1.json",
            "domain": {
                "key": "java",
                "name": "Java Development"
            },
            "profiles": {
                "core": {
                    "defaults": ["invalid_reference"],
                    "optionals": []
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert "Invalid skill reference format" in result.stdout


def test_validate_valid_supplement_manifest():
    """Test validation of a valid supplement manifest."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-supplements-v1.json",
            "supplements": {
                "domain": "java",
                "description": "CUI Java patterns",
                "skills": {
                    "core": {
                        "defaults": [],
                        "optionals": ["test-bundle:cui-logging"]
                    }
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)
        cache.create_bundle_with_skill('test-bundle', 'cui-logging')

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'status: success' in result.stdout
        assert 'type: supplement' in result.stdout
        assert 'target_domain: java' in result.stdout


def test_validate_supplement_missing_domain():
    """Test validation of supplement manifest without target domain."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-supplements-v1.json",
            "supplements": {
                "description": "CUI Java patterns",
                "skills": {
                    "core": {
                        "defaults": [],
                        "optionals": []
                    }
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert "Missing 'supplements.domain'" in result.stdout


def test_validate_supplement_invalid_profile():
    """Test validation of supplement manifest with invalid profile name."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-supplements-v1.json",
            "supplements": {
                "domain": "java",
                "skills": {
                    "invalid-profile": {
                        "defaults": [],
                        "optionals": []
                    }
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert "Invalid profile name: 'invalid-profile'" in result.stdout


def test_validate_domain_with_extensions():
    """Test validation of domain with extensions that exist."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-manifest-v1.json",
            "domain": {
                "key": "java",
                "name": "Java Development"
            },
            "extensions": {
                "outline": "test-bundle:java-outline-ext",
                "triage": "test-bundle:java-triage"
            },
            "profiles": {
                "core": {
                    "defaults": [],
                    "optionals": []
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)
        cache.create_bundle_with_skill('test-bundle', 'java-outline-ext')
        cache.create_bundle_with_skill('test-bundle', 'java-triage')

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert result.success, f"Script failed: {result.stderr}"
        assert 'outline: valid' in result.stdout
        assert 'triage: valid' in result.stdout


def test_validate_unsupported_schema_version():
    """Test validation of manifest with unsupported schema version."""
    with MockPluginCache() as cache:
        manifest = {
            "$schema": "https://example.com/domain-manifest-v99.json",
            "domain": {
                "key": "java",
                "name": "Java Development"
            },
            "profiles": {
                "core": {
                    "defaults": [],
                    "optionals": []
                }
            }
        }
        cache.create_bundle_with_manifest('test-bundle', manifest)

        result = run_script(SCRIPT_PATH, 'validate', '--bundle', 'test-bundle')
        assert not result.success
        assert "Unsupported schema version: v99" in result.stdout


if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        test_validate_help,
        test_validate_bundle_not_found,
        test_validate_no_plan_marshall_plugin,
        test_validate_valid_domain_manifest,
        test_validate_domain_missing_key,
        test_validate_domain_missing_core_profile,
        test_validate_domain_invalid_profile_name,
        test_validate_domain_invalid_skill_reference,
        test_validate_valid_supplement_manifest,
        test_validate_supplement_missing_domain,
        test_validate_supplement_invalid_profile,
        test_validate_domain_with_extensions,
        test_validate_unsupported_schema_version,
    ])
    sys.exit(runner.run())
