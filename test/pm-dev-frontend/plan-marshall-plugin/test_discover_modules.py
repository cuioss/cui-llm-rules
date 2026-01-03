#!/usr/bin/env python3
"""Tests for discover_modules() in npm extension.

Tests the unified module discovery API for npm projects including
metadata extraction, dependency parsing, and stats.
"""

import json
import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    TestRunner,
    BuildTestContext
)

# Use importlib to avoid module naming conflicts with other Extension classes
import importlib.util

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
EXTENSION_BASE_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'
EXTENSION_FILE = PROJECT_ROOT / 'marketplace' / 'bundles' / 'pm-dev-frontend' / 'skills' / 'plan-marshall-plugin' / 'extension.py'

# Add extension base to path for import
sys.path.insert(0, str(EXTENSION_BASE_DIR))


def _load_npm_extension():
    """Load npm Extension class avoiding conflicts."""
    spec = importlib.util.spec_from_file_location("npm_extension", EXTENSION_FILE)
    npm_ext = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(npm_ext)
    return npm_ext.Extension


Extension = _load_npm_extension()


# =============================================================================
# Test: Basic Module Discovery
# =============================================================================

def test_discover_modules_single_module():
    """Test discover_modules with single npm project."""
    with BuildTestContext() as ctx:
        # Create a single-module npm project
        pkg = {
            "name": "my-app",
            "version": "1.0.0",
            "description": "My sample application",
            "type": "module"
        }
        (ctx.temp_dir / 'package.json').write_text(json.dumps(pkg))

        # Create source directory
        src_dir = ctx.temp_dir / 'src'
        src_dir.mkdir()
        (src_dir / 'index.js').write_text('export default function() {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        module = modules[0]

        assert module['name'] == 'my-app'
        assert module['path'] == '.'
        assert 'npm' in module['build_systems']
        assert module['metadata']['description'] == 'My sample application'
        assert module['metadata']['version'] == '1.0.0'
        assert module['metadata']['type'] == 'module'


def test_discover_modules_with_workspaces():
    """Test discover_modules with npm workspaces."""
    with BuildTestContext() as ctx:
        # Create root package.json with workspaces
        root_pkg = {
            "name": "monorepo",
            "workspaces": ["packages/*"]
        }
        (ctx.temp_dir / 'package.json').write_text(json.dumps(root_pkg))

        # Create packages directory
        packages_dir = ctx.temp_dir / 'packages'
        packages_dir.mkdir()

        # Create first workspace
        pkg_a_dir = packages_dir / 'pkg-a'
        pkg_a_dir.mkdir()
        (pkg_a_dir / 'package.json').write_text(json.dumps({
            "name": "@monorepo/pkg-a",
            "version": "1.0.0"
        }))

        # Create second workspace
        pkg_b_dir = packages_dir / 'pkg-b'
        pkg_b_dir.mkdir()
        (pkg_b_dir / 'package.json').write_text(json.dumps({
            "name": "@monorepo/pkg-b",
            "version": "2.0.0"
        }))

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 2

        # Find modules by name
        pkg_a = next(m for m in modules if 'pkg-a' in m['name'])
        pkg_b = next(m for m in modules if 'pkg-b' in m['name'])

        assert pkg_a['path'] == 'packages/pkg-a'
        assert pkg_b['path'] == 'packages/pkg-b'


def test_discover_modules_no_package_json():
    """Test discover_modules with no package.json."""
    with BuildTestContext() as ctx:
        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 0


# =============================================================================
# Test: Metadata Extraction
# =============================================================================

def test_metadata_extraction():
    """Test metadata extraction from package.json."""
    with BuildTestContext() as ctx:
        pkg = {
            "name": "test-pkg",
            "version": "3.2.1",
            "description": "A test package",
            "type": "commonjs",
            "main": "dist/index.js",
            "exports": {
                ".": "./dist/index.js"
            },
            "scripts": {
                "build": "tsc",
                "test": "jest"
            }
        }
        (ctx.temp_dir / 'package.json').write_text(json.dumps(pkg))

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        metadata = modules[0]['metadata']
        assert metadata['description'] == 'A test package'
        assert metadata['version'] == '3.2.1'
        assert metadata['type'] == 'commonjs'
        assert metadata['main'] == 'dist/index.js'
        assert metadata['exports'] is True  # exports key exists
        assert 'build' in metadata['scripts']
        assert 'test' in metadata['scripts']


# =============================================================================
# Test: Dependency Extraction
# =============================================================================

def test_extract_dependencies():
    """Test dependency extraction from package.json."""
    with BuildTestContext() as ctx:
        pkg = {
            "name": "test-pkg",
            "dependencies": {
                "lodash": "^4.17.21",
                "express": "^4.18.0"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "typescript": "^5.0.0"
            },
            "peerDependencies": {
                "react": "^18.0.0"
            }
        }
        (ctx.temp_dir / 'package.json').write_text(json.dumps(pkg))

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        deps = modules[0]['dependencies']
        assert len(deps) == 5

        # Check compile scope (dependencies)
        lodash = next(d for d in deps if d['name'] == 'lodash')
        assert lodash['scope'] == 'compile'
        assert lodash['version'] == '^4.17.21'

        # Check test scope (devDependencies)
        jest = next(d for d in deps if d['name'] == 'jest')
        assert jest['scope'] == 'test'

        # Check provided scope (peerDependencies)
        react = next(d for d in deps if d['name'] == 'react')
        assert react['scope'] == 'provided'


# =============================================================================
# Test: Source Directory Discovery
# =============================================================================

def test_discover_sources_src():
    """Test source directory discovery with src."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'package.json').write_text('{"name": "test"}')
        (ctx.temp_dir / 'src').mkdir()

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        sources = modules[0]['sources']
        assert 'src' in sources['main']


def test_discover_sources_test():
    """Test test directory discovery."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'package.json').write_text('{"name": "test"}')
        (ctx.temp_dir / 'test').mkdir()
        (ctx.temp_dir / '__tests__').mkdir()

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        sources = modules[0]['sources']
        assert 'test' in sources['test']
        assert '__tests__' in sources['test']


def test_discover_sources_resources():
    """Test resource directory discovery."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'package.json').write_text('{"name": "test"}')
        (ctx.temp_dir / 'public').mkdir()
        (ctx.temp_dir / 'static').mkdir()

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        sources = modules[0]['sources']
        assert 'public' in sources['resources']
        assert 'static' in sources['resources']


# =============================================================================
# Test: Stats
# =============================================================================

def test_stats_file_counts():
    """Test source and test file counting."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'package.json').write_text('{"name": "test"}')

        # Create source files
        src_dir = ctx.temp_dir / 'src'
        src_dir.mkdir()
        (src_dir / 'index.js').write_text('export default {}')
        (src_dir / 'utils.ts').write_text('export const x = 1')
        (src_dir / 'component.tsx').write_text('export default () => null')

        # Create test files
        test_dir = ctx.temp_dir / 'test'
        test_dir.mkdir()
        (test_dir / 'index.test.js').write_text('test("x", () => {})')
        (test_dir / 'utils.test.ts').write_text('test("y", () => {})')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        stats = modules[0]['stats']
        assert stats['source_files'] == 3
        assert stats['test_files'] == 2


def test_stats_has_readme():
    """Test README detection."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'package.json').write_text('{"name": "test"}')
        (ctx.temp_dir / 'README.md').write_text('# My Project')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['stats']['has_readme'] is True


def test_stats_no_readme():
    """Test README detection when none exists."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'package.json').write_text('{"name": "test"}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert modules[0]['stats']['has_readme'] is False


# =============================================================================
# Test: Hybrid Modules
# =============================================================================

def test_hybrid_npm_maven_module():
    """Test detection of hybrid npm + Maven module."""
    with BuildTestContext() as ctx:
        # Create npm project
        (ctx.temp_dir / 'package.json').write_text('{"name": "frontend", "version": "1.0.0"}')

        # Add pom.xml (hybrid)
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>frontend</artifactId></project>')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        # When discovered from npm extension, npm should be in build_systems
        # and maven should also be detected
        assert 'npm' in modules[0]['build_systems']
        assert 'maven' in modules[0]['build_systems']
        assert modules[0]['descriptors']['package'] == 'package.json'
        assert modules[0]['descriptors']['pom'] == 'pom.xml'


# =============================================================================
# Test: Workspaces with object format
# =============================================================================

def test_workspaces_object_format():
    """Test workspaces with object format (packages key)."""
    with BuildTestContext() as ctx:
        # Create root package.json with object workspaces
        root_pkg = {
            "name": "monorepo",
            "workspaces": {
                "packages": ["packages/*"]
            }
        }
        (ctx.temp_dir / 'package.json').write_text(json.dumps(root_pkg))

        # Create packages directory
        packages_dir = ctx.temp_dir / 'packages'
        packages_dir.mkdir()

        # Create workspace
        pkg_dir = packages_dir / 'my-pkg'
        pkg_dir.mkdir()
        (pkg_dir / 'package.json').write_text(json.dumps({
            "name": "my-pkg",
            "version": "1.0.0"
        }))

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        assert modules[0]['name'] == 'my-pkg'


# =============================================================================
# Test: Descriptors
# =============================================================================

def test_descriptors_structure():
    """Test that descriptors have correct structure."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'package.json').write_text('{"name": "test"}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        descriptors = modules[0]['descriptors']
        assert 'pom' in descriptors
        assert 'gradle' in descriptors
        assert 'package' in descriptors
        assert descriptors['package'] == 'package.json'
        assert descriptors['pom'] is None
        assert descriptors['gradle'] is None


# =============================================================================
# Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Basic module discovery
        test_discover_modules_single_module,
        test_discover_modules_with_workspaces,
        test_discover_modules_no_package_json,

        # Metadata extraction
        test_metadata_extraction,

        # Dependency extraction
        test_extract_dependencies,

        # Source directory discovery
        test_discover_sources_src,
        test_discover_sources_test,
        test_discover_sources_resources,

        # Stats
        test_stats_file_counts,
        test_stats_has_readme,
        test_stats_no_readme,

        # Hybrid modules
        test_hybrid_npm_maven_module,

        # Workspaces object format
        test_workspaces_object_format,

        # Descriptors
        test_descriptors_structure,
    ])
    sys.exit(runner.run())
