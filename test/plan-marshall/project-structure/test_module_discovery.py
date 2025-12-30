#!/usr/bin/env python3
"""Tests for module discovery in manage_project_structure.py.

Tests the discover_modules_from_filesystem() function which discovers
modules directly from the filesystem without marshal.json dependency.

Verification projects:
- OAuth-Sheriff: Pure Maven with nested modules (10 total)
- nifi-extensions: Hybrid Maven+npm modules
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import TestRunner

# Import functions under test
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'project-structure' / 'scripts'
sys.path.insert(0, str(SCRIPT_DIR))

from manage_project_structure import (
    discover_modules_from_filesystem,
    detect_build_systems,
    parse_maven_modules,
    collect_raw_project_data,
)


# ===========================================================================
# Test: detect_build_systems()
# ===========================================================================

def test_detect_build_systems_maven_only():
    """Test detection of Maven-only module."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create pom.xml
        (Path(tmpdir) / 'pom.xml').write_text('<project></project>')

        result = detect_build_systems(Path(tmpdir))

        assert result == ['maven'], f"Expected ['maven'], got {result}"


def test_detect_build_systems_npm_only():
    """Test detection of npm-only module."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create package.json
        (Path(tmpdir) / 'package.json').write_text('{}')

        result = detect_build_systems(Path(tmpdir))

        assert result == ['npm'], f"Expected ['npm'], got {result}"


def test_detect_build_systems_hybrid():
    """Test detection of hybrid Maven+npm module."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create both pom.xml and package.json
        (Path(tmpdir) / 'pom.xml').write_text('<project></project>')
        (Path(tmpdir) / 'package.json').write_text('{}')

        result = detect_build_systems(Path(tmpdir))

        assert 'maven' in result, "Expected maven in build_systems"
        assert 'npm' in result, "Expected npm in build_systems"
        assert len(result) == 2, f"Expected 2 build systems, got {len(result)}"


def test_detect_build_systems_gradle():
    """Test detection of Gradle module."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create build.gradle
        (Path(tmpdir) / 'build.gradle').write_text('plugins {}')

        result = detect_build_systems(Path(tmpdir))

        assert result == ['gradle'], f"Expected ['gradle'], got {result}"


def test_detect_build_systems_gradle_kts():
    """Test detection of Gradle Kotlin DSL module."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create build.gradle.kts
        (Path(tmpdir) / 'build.gradle.kts').write_text('plugins {}')

        result = detect_build_systems(Path(tmpdir))

        assert result == ['gradle'], f"Expected ['gradle'], got {result}"


def test_detect_build_systems_empty():
    """Test detection with no build files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = detect_build_systems(Path(tmpdir))

        assert result == [], f"Expected empty list, got {result}"


# ===========================================================================
# Test: parse_maven_modules()
# ===========================================================================

def test_parse_maven_modules_with_namespace():
    """Test parsing modules from pom.xml with Maven namespace."""
    pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modules>
        <module>module-a</module>
        <module>module-b</module>
        <module>nested/module-c</module>
    </modules>
</project>'''

    with tempfile.TemporaryDirectory() as tmpdir:
        pom_path = Path(tmpdir) / 'pom.xml'
        pom_path.write_text(pom_content)

        result = parse_maven_modules(pom_path)

        assert len(result) == 3, f"Expected 3 modules, got {len(result)}"
        assert 'module-a' in result
        assert 'module-b' in result
        assert 'nested/module-c' in result


def test_parse_maven_modules_without_namespace():
    """Test parsing modules from pom.xml without namespace."""
    pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modules>
        <module>module-x</module>
        <module>module-y</module>
    </modules>
</project>'''

    with tempfile.TemporaryDirectory() as tmpdir:
        pom_path = Path(tmpdir) / 'pom.xml'
        pom_path.write_text(pom_content)

        result = parse_maven_modules(pom_path)

        assert len(result) == 2, f"Expected 2 modules, got {len(result)}"
        assert 'module-x' in result
        assert 'module-y' in result


def test_parse_maven_modules_no_modules():
    """Test parsing pom.xml with no modules section."""
    pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <groupId>com.example</groupId>
    <artifactId>my-lib</artifactId>
</project>'''

    with tempfile.TemporaryDirectory() as tmpdir:
        pom_path = Path(tmpdir) / 'pom.xml'
        pom_path.write_text(pom_content)

        result = parse_maven_modules(pom_path)

        assert result == [], f"Expected empty list, got {result}"


def test_parse_maven_modules_file_not_found():
    """Test parsing non-existent pom.xml."""
    result = parse_maven_modules(Path('/nonexistent/pom.xml'))

    assert result == [], f"Expected empty list, got {result}"


# ===========================================================================
# Test: discover_modules_from_filesystem()
# ===========================================================================

def test_discover_modules_simple_maven():
    """Test discovery of simple Maven project with two modules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create root pom.xml with modules
        (root / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>pom</packaging>
    <modules>
        <module>module-a</module>
        <module>module-b</module>
    </modules>
</project>''')

        # Create module directories with pom.xml
        (root / 'module-a').mkdir()
        (root / 'module-a' / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>jar</packaging>
</project>''')

        (root / 'module-b').mkdir()
        (root / 'module-b' / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>war</packaging>
</project>''')

        result = discover_modules_from_filesystem(str(root))

        assert len(result) == 2, f"Expected 2 modules, got {len(result)}"

        names = [m['name'] for m in result]
        assert 'module-a' in names
        assert 'module-b' in names

        # Check packaging
        module_a = next(m for m in result if m['name'] == 'module-a')
        assert module_a['packaging'] == 'jar'
        assert module_a['build_systems'] == ['maven']


def test_discover_modules_nested():
    """Test discovery of nested Maven modules (like OAuth-Sheriff)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create root pom.xml
        (root / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>pom</packaging>
    <modules>
        <module>parent-module</module>
    </modules>
</project>''')

        # Create parent module with nested children
        parent = root / 'parent-module'
        parent.mkdir()
        (parent / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>pom</packaging>
    <modules>
        <module>child-a</module>
        <module>child-b</module>
    </modules>
</project>''')

        # Create child modules
        (parent / 'child-a').mkdir()
        (parent / 'child-a' / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>jar</packaging>
</project>''')

        (parent / 'child-b').mkdir()
        (parent / 'child-b' / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>jar</packaging>
</project>''')

        result = discover_modules_from_filesystem(str(root))

        assert len(result) == 3, f"Expected 3 modules, got {len(result)}"

        # Check parent module
        parent_mod = next(m for m in result if m['name'] == 'parent-module')
        assert parent_mod['packaging'] == 'pom'

        # Check child modules have correct paths (hierarchy via path, not parent field)
        child_a = next(m for m in result if m['name'] == 'child-a')
        assert child_a['path'] == 'parent-module/child-a'

        child_b = next(m for m in result if m['name'] == 'child-b')
        assert child_b['path'] == 'parent-module/child-b'


def test_discover_modules_hybrid():
    """Test discovery of hybrid Maven+npm modules (like nifi-extensions)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create root pom.xml
        (root / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>pom</packaging>
    <modules>
        <module>pure-maven</module>
        <module>hybrid-module</module>
    </modules>
</project>''')

        # Create pure Maven module
        (root / 'pure-maven').mkdir()
        (root / 'pure-maven' / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>jar</packaging>
</project>''')

        # Create hybrid module (Maven + npm)
        hybrid = root / 'hybrid-module'
        hybrid.mkdir()
        (hybrid / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>war</packaging>
</project>''')
        (hybrid / 'package.json').write_text('{"name": "hybrid"}')

        result = discover_modules_from_filesystem(str(root))

        assert len(result) == 2, f"Expected 2 modules, got {len(result)}"

        # Check pure Maven module
        pure_maven = next(m for m in result if m['name'] == 'pure-maven')
        assert pure_maven['build_systems'] == ['maven']

        # Check hybrid module
        hybrid_mod = next(m for m in result if m['name'] == 'hybrid-module')
        assert 'maven' in hybrid_mod['build_systems']
        assert 'npm' in hybrid_mod['build_systems']
        assert len(hybrid_mod['build_systems']) == 2


def test_discover_modules_no_pom():
    """Test discovery with no pom.xml at root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = discover_modules_from_filesystem(tmpdir)

        assert result == [], f"Expected empty list, got {result}"


def test_discover_modules_npm_only_project():
    """Test discovery of npm-only project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        root_name = root.name

        # Create package.json only
        (root / 'package.json').write_text('{"name": "my-npm-project"}')

        result = discover_modules_from_filesystem(str(root))

        assert len(result) == 1, f"Expected 1 module, got {len(result)}"
        assert result[0]['name'] == root_name
        assert result[0]['build_systems'] == ['npm']
        assert result[0]['path'] == '.'


# ===========================================================================
# Test: collect_raw_project_data()
# ===========================================================================

def test_collect_raw_project_data_structure():
    """Test that collect_raw_project_data returns correct structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create minimal Maven project
        (root / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>pom</packaging>
    <modules>
        <module>my-module</module>
    </modules>
</project>''')

        (root / 'my-module').mkdir()
        (root / 'my-module' / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>jar</packaging>
</project>''')

        # Create README
        (root / 'README.md').write_text('# My Project')

        result = collect_raw_project_data(str(root))

        # Check structure
        assert 'project' in result
        assert 'root' in result['project']
        assert 'name' in result['project']

        assert 'documentation' in result
        assert 'readme' in result['documentation']

        assert 'modules' in result
        assert isinstance(result['modules'], list)
        assert len(result['modules']) == 1

        # Unified structure - each module contains all its data
        module = result['modules'][0]
        assert 'name' in module
        assert 'path' in module


def test_collect_raw_project_data_no_marshal_dependency():
    """Test that collect_raw_project_data works without marshal.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create Maven project - NO marshal.json!
        (root / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>pom</packaging>
    <modules>
        <module>module-one</module>
    </modules>
</project>''')

        (root / 'module-one').mkdir()
        (root / 'module-one' / 'pom.xml').write_text('''<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <packaging>jar</packaging>
</project>''')

        # Verify no marshal.json exists
        assert not (root / '.plan' / 'marshal.json').exists()

        # Should work without marshal.json
        result = collect_raw_project_data(str(root))

        assert len(result['modules']) == 1
        assert result['modules'][0]['name'] == 'module-one'


# ===========================================================================
# Integration Tests: Real Projects
# ===========================================================================

def test_oauth_sheriff_discovery():
    """Integration test: OAuth-Sheriff should discover 10 modules."""
    oauth_sheriff_path = Path('/Users/oliver/git/OAuth-Sheriff')

    if not oauth_sheriff_path.exists():
        print("SKIP: OAuth-Sheriff not available")
        return

    result = discover_modules_from_filesystem(str(oauth_sheriff_path))

    # Should discover all 10 modules
    assert len(result) == 10, f"Expected 10 modules, got {len(result)}"

    # Check specific modules exist
    names = [m['name'] for m in result]
    assert 'bom' in names
    assert 'oauth-sheriff-core' in names
    assert 'oauth-sheriff-quarkus-parent' in names
    assert 'oauth-sheriff-quarkus' in names
    assert 'oauth-sheriff-quarkus-deployment' in names
    assert 'benchmarking' in names

    # Check nested module has correct path (hierarchy via path)
    quarkus_mod = next(m for m in result if m['name'] == 'oauth-sheriff-quarkus')
    assert 'oauth-sheriff-quarkus-parent' in quarkus_mod['path']


def test_nifi_extensions_discovery():
    """Integration test: nifi-extensions should discover hybrid modules."""
    nifi_path = Path('/Users/oliver/git/nifi-extensions')

    if not nifi_path.exists():
        print("SKIP: nifi-extensions not available")
        return

    result = discover_modules_from_filesystem(str(nifi_path))

    # Should discover 5 modules
    assert len(result) == 5, f"Expected 5 modules, got {len(result)}"

    # Check hybrid modules
    names = {m['name']: m for m in result}

    # nifi-cuioss-ui should be hybrid (maven + npm)
    assert 'nifi-cuioss-ui' in names
    ui_module = names['nifi-cuioss-ui']
    assert 'maven' in ui_module['build_systems'], "nifi-cuioss-ui should have maven"
    assert 'npm' in ui_module['build_systems'], "nifi-cuioss-ui should have npm"

    # e-2-e-playwright should be hybrid (maven + npm)
    assert 'e-2-e-playwright' in names
    e2e_module = names['e-2-e-playwright']
    assert 'maven' in e2e_module['build_systems'], "e-2-e-playwright should have maven"
    assert 'npm' in e2e_module['build_systems'], "e-2-e-playwright should have npm"


# ===========================================================================
# Main
# ===========================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # detect_build_systems tests
        test_detect_build_systems_maven_only,
        test_detect_build_systems_npm_only,
        test_detect_build_systems_hybrid,
        test_detect_build_systems_gradle,
        test_detect_build_systems_gradle_kts,
        test_detect_build_systems_empty,
        # parse_maven_modules tests
        test_parse_maven_modules_with_namespace,
        test_parse_maven_modules_without_namespace,
        test_parse_maven_modules_no_modules,
        test_parse_maven_modules_file_not_found,
        # discover_modules_from_filesystem tests
        test_discover_modules_simple_maven,
        test_discover_modules_nested,
        test_discover_modules_hybrid,
        test_discover_modules_no_pom,
        test_discover_modules_npm_only_project,
        # collect_raw_project_data tests
        test_collect_raw_project_data_structure,
        test_collect_raw_project_data_no_marshal_dependency,
        # Integration tests
        test_oauth_sheriff_discovery,
        test_nifi_extensions_discovery,
    ])
    sys.exit(runner.run())
