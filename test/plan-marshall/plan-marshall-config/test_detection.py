#!/usr/bin/env python3
"""Tests for project detection in plan-marshall-config.

Tests auto-detection of build systems, domains, and modules from project files,
including complex nested structures like multi-module Maven projects with nested npm.
"""

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, PlanTestContext
from test_helpers import SCRIPT_PATH


# =============================================================================
# Test Cleanup - Ensure Isolation Between Tests
# =============================================================================

def cleanup_project_files(fixture_dir: Path) -> None:
    """Remove all project files from fixture directory to ensure test isolation.

    When tests run via run-tests.py, they share a fixture directory.
    This function ensures clean state before each test.
    """
    # Remove root build files
    for filename in ['pom.xml', 'package.json', 'build.gradle', 'build.gradle.kts']:
        filepath = fixture_dir / filename
        if filepath.exists():
            filepath.unlink()

    # Remove module directories
    for module_name in ['core', 'api', 'web', 'ui', 'e2e']:
        module_dir = fixture_dir / module_name
        if module_dir.exists():
            shutil.rmtree(module_dir)


# =============================================================================
# Test Fixtures - Project Structure Creators
# =============================================================================

def create_simple_maven_project(fixture_dir: Path) -> None:
    """Create a simple single-module Maven project."""
    pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>simple-app</artifactId>
    <version>1.0.0</version>
</project>'''
    (fixture_dir / 'pom.xml').write_text(pom_content)


def create_simple_npm_project(fixture_dir: Path) -> None:
    """Create a simple npm project."""
    package_content = json.dumps({
        "name": "simple-app",
        "version": "1.0.0"
    }, indent=2)
    (fixture_dir / 'package.json').write_text(package_content)


def create_multi_module_maven_project(fixture_dir: Path) -> None:
    """Create a multi-module Maven project (Java only)."""
    root_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>multi-module-app</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    <modules>
        <module>core</module>
        <module>api</module>
        <module>web</module>
    </modules>
</project>'''
    (fixture_dir / 'pom.xml').write_text(root_pom)

    # Create module directories with pom.xml
    for module in ['core', 'api', 'web']:
        module_dir = fixture_dir / module
        module_dir.mkdir(parents=True, exist_ok=True)
        module_pom = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>multi-module-app</artifactId>
        <version>1.0.0</version>
    </parent>
    <artifactId>{module}</artifactId>
</project>'''
        (module_dir / 'pom.xml').write_text(module_pom)


def create_mixed_multi_module_project(fixture_dir: Path) -> None:
    """Create a multi-module Maven project with nested npm modules.

    Structure like nifi-extensions:
    - Root pom.xml (maven parent)
    - core/ (Java only)
    - api/ (Java only)
    - ui/ (Java + JavaScript - has package.json)
    - e2e/ (Java + JavaScript - has package.json for playwright)
    """
    root_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>mixed-multi-module</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    <modules>
        <module>core</module>
        <module>api</module>
        <module>ui</module>
        <module>e2e</module>
    </modules>
</project>'''
    (fixture_dir / 'pom.xml').write_text(root_pom)

    # Java-only modules
    for module in ['core', 'api']:
        module_dir = fixture_dir / module
        module_dir.mkdir(parents=True, exist_ok=True)
        module_pom = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>mixed-multi-module</artifactId>
        <version>1.0.0</version>
    </parent>
    <artifactId>{module}</artifactId>
</project>'''
        (module_dir / 'pom.xml').write_text(module_pom)

    # Java + JavaScript modules (have both pom.xml and package.json)
    for module in ['ui', 'e2e']:
        module_dir = fixture_dir / module
        module_dir.mkdir(parents=True, exist_ok=True)

        # Maven pom.xml
        module_pom = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>mixed-multi-module</artifactId>
        <version>1.0.0</version>
    </parent>
    <artifactId>{module}</artifactId>
</project>'''
        (module_dir / 'pom.xml').write_text(module_pom)

        # npm package.json
        package_content = json.dumps({
            "name": f"@example/{module}",
            "version": "1.0.0"
        }, indent=2)
        (module_dir / 'package.json').write_text(package_content)


def create_minimal_marshal_json(fixture_dir: Path) -> Path:
    """Create minimal marshal.json for detection tests."""
    config = {
        "skill_domains": {
            "system": {
                "defaults": ["plan-marshall:general-development-rules"],
                "optionals": []
            }
        },
        "modules": {},
        "build_systems": [],
        "system": {"retention": {"logs_days": 1}},
        "plan": {"defaults": {}}
    }
    marshal_path = fixture_dir / 'marshal.json'
    marshal_path.write_text(json.dumps(config, indent=2))
    return marshal_path


# =============================================================================
# Build Systems Detection Tests
# =============================================================================

def test_detect_build_systems_maven_only():
    """Test detecting Maven as build system."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_simple_maven_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'detect', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()
        assert 'npm' not in result.stdout.lower()


def test_detect_build_systems_npm_only():
    """Test detecting npm as build system."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_simple_npm_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'detect', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'npm' in result.stdout.lower()
        assert 'maven' not in result.stdout.lower()


def test_detect_build_systems_multi_module_maven_no_npm():
    """Test that multi-module Maven project with nested package.json does NOT detect npm at root."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_mixed_multi_module_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'build-systems', 'detect', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        # Should detect maven (root pom.xml)
        assert 'maven' in result.stdout.lower()
        # Should NOT detect npm (no root package.json, only nested in modules)
        assert 'npm' not in result.stdout.lower(), \
            "Should not detect npm - package.json is nested in modules, not at root"


# =============================================================================
# Modules Detection Tests
# =============================================================================

def test_detect_modules_multi_module_maven():
    """Test detecting Maven modules."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_multi_module_maven_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'modules', 'detect', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'core' in result.stdout
        assert 'api' in result.stdout
        assert 'web' in result.stdout


def test_detect_modules_infers_java_domain():
    """Test that detected Maven modules have java domain."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_multi_module_maven_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        # Detect modules
        run_script(SCRIPT_PATH, 'modules', 'detect', cwd=ctx.fixture_dir)

        # Verify module has java domain
        result = run_script(SCRIPT_PATH, 'modules', 'get-domains', '--module', 'core', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout.lower()


def test_detect_modules_mixed_infers_javascript_for_nested_npm():
    """Test that modules with nested package.json have javascript domain."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_mixed_multi_module_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        # Detect modules
        run_script(SCRIPT_PATH, 'modules', 'detect', cwd=ctx.fixture_dir)

        # Verify ui module has javascript domain (it has package.json)
        result = run_script(SCRIPT_PATH, 'modules', 'get-domains', '--module', 'ui', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'javascript' in result.stdout.lower(), \
            "Module with package.json should have javascript domain"


def test_detect_modules_mixed_java_only_module():
    """Test that Java-only modules don't have javascript domain."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_mixed_multi_module_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        # Detect modules
        run_script(SCRIPT_PATH, 'modules', 'detect', cwd=ctx.fixture_dir)

        # Verify core module only has java domain (no package.json)
        result = run_script(SCRIPT_PATH, 'modules', 'get-domains', '--module', 'core', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'java' in result.stdout.lower()
        # Should NOT have javascript
        assert 'javascript' not in result.stdout.lower(), \
            "Module without package.json should not have javascript domain"


def test_detect_modules_mixed_build_systems():
    """Test that modules with nested package.json have npm build system."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_mixed_multi_module_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        # Detect modules
        run_script(SCRIPT_PATH, 'modules', 'detect', cwd=ctx.fixture_dir)

        # Verify ui module has npm build system
        result = run_script(SCRIPT_PATH, 'modules', 'get-build-systems', '--module', 'ui', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()
        assert 'npm' in result.stdout.lower(), \
            "Module with package.json should have npm build system"


def test_detect_modules_java_only_build_systems():
    """Test that Java-only modules only have maven build system."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_mixed_multi_module_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        # Detect modules
        run_script(SCRIPT_PATH, 'modules', 'detect', cwd=ctx.fixture_dir)

        # Verify core module only has maven build system
        result = run_script(SCRIPT_PATH, 'modules', 'get-build-systems', '--module', 'core', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"
        assert 'maven' in result.stdout.lower()
        assert 'npm' not in result.stdout.lower(), \
            "Module without package.json should not have npm build system"


# =============================================================================
# Domain Detection Tests
# =============================================================================

def test_detect_domains_maven_project():
    """Test detecting java domain from Maven project."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_simple_maven_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'detect', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify java domain was added
        verify = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'java', cwd=ctx.fixture_dir)
        assert verify.success, "Java domain should exist"


def test_detect_domains_npm_project():
    """Test detecting javascript domain from npm project."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_simple_npm_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'detect', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify javascript domain was added
        verify = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'javascript', cwd=ctx.fixture_dir)
        assert verify.success, "JavaScript domain should exist"


def test_detect_domains_multi_module_maven_no_javascript():
    """Test that multi-module Maven with nested npm doesn't add javascript at root."""
    with PlanTestContext() as ctx:
        cleanup_project_files(ctx.fixture_dir)
        create_mixed_multi_module_project(ctx.fixture_dir)
        create_minimal_marshal_json(ctx.fixture_dir)

        result = run_script(SCRIPT_PATH, 'skill-domains', 'detect', cwd=ctx.fixture_dir)

        assert result.success, f"Should succeed: {result.stderr}"

        # Verify java domain exists
        verify_java = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'java', cwd=ctx.fixture_dir)
        assert verify_java.success, "Java domain should exist"

        # Verify javascript domain does NOT exist at root level
        verify_js = run_script(SCRIPT_PATH, 'skill-domains', 'get', '--domain', 'javascript', cwd=ctx.fixture_dir)
        assert 'error' in verify_js.stdout.lower(), \
            "JavaScript should not be detected as root domain when only nested in modules"


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Build systems detection
        test_detect_build_systems_maven_only,
        test_detect_build_systems_npm_only,
        test_detect_build_systems_multi_module_maven_no_npm,
        # Modules detection
        test_detect_modules_multi_module_maven,
        test_detect_modules_infers_java_domain,
        test_detect_modules_mixed_infers_javascript_for_nested_npm,
        test_detect_modules_mixed_java_only_module,
        test_detect_modules_mixed_build_systems,
        test_detect_modules_java_only_build_systems,
        # Domain detection
        test_detect_domains_maven_project,
        test_detect_domains_npm_project,
        test_detect_domains_multi_module_maven_no_javascript,
    ])
    sys.exit(runner.run())
