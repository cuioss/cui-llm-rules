#!/usr/bin/env python3
"""Tests for discover_modules() in Maven extension.

Tests the unified module discovery API for Maven projects against the
contract defined in build-project-structure.md.

Contract requirements:
- technology: single string (not build_systems array)
- paths: object with module, descriptor, sources, tests, readme
- metadata: snake_case fields (artifact_id, group_id)
- metadata.parent: string "groupId:artifactId" (not object)
- metadata.profiles: array with id, canonical, activation
- packages: object keyed by package name (not array)
- dependencies: string format "groupId:artifactId:scope" (not objects)
- stats: only source_files, test_files (no has_readme)
- commands: resolved canonical command strings
"""

import sys
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import (
    TestRunner,
    BuildTestContext
)

# Add extension directories to path for import
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
EXTENSION_BASE_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'
EXTENSION_DIR = PROJECT_ROOT / 'marketplace' / 'bundles' / 'pm-dev-java' / 'skills' / 'plan-marshall-plugin'
sys.path.insert(0, str(EXTENSION_BASE_DIR))
sys.path.insert(0, str(EXTENSION_DIR))

# Import Extension class directly from the file
import importlib.util
spec = importlib.util.spec_from_file_location("java_extension", EXTENSION_DIR / "extension.py")
java_extension = importlib.util.module_from_spec(spec)
spec.loader.exec_module(java_extension)
Extension = java_extension.Extension


# =============================================================================
# Test: Contract Structure Compliance
# =============================================================================

def test_module_has_technology_not_build_systems():
    """Contract: Module must have 'technology' string, not 'build_systems' array."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>test</artifactId>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        module = modules[0]

        # Contract: technology is a string
        assert 'technology' in module, "Module must have 'technology' field"
        assert isinstance(module['technology'], str), "technology must be string"
        assert module['technology'] == 'maven'

        # Contract: build_systems should NOT exist (orchestrator creates it)
        assert 'build_systems' not in module, "Module must NOT have 'build_systems' (orchestrator adds it)"


def test_module_has_paths_object():
    """Contract: Module must have 'paths' object with module, descriptor, sources, tests, readme."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>test</artifactId>
</project>''')
        (ctx.temp_dir / 'src' / 'main' / 'java').mkdir(parents=True)
        (ctx.temp_dir / 'src' / 'test' / 'java').mkdir(parents=True)
        (ctx.temp_dir / 'README.md').write_text('# Test')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        module = modules[0]

        # Contract: paths is an object
        assert 'paths' in module, "Module must have 'paths' field"
        paths = module['paths']

        # Required fields
        assert 'module' in paths, "paths must have 'module'"
        assert 'descriptor' in paths, "paths must have 'descriptor'"
        assert 'sources' in paths, "paths must have 'sources'"
        assert 'tests' in paths, "paths must have 'tests'"
        assert 'readme' in paths, "paths must have 'readme'"

        # Types
        assert isinstance(paths['module'], str), "paths.module must be string"
        assert isinstance(paths['descriptor'], str), "paths.descriptor must be string"
        assert isinstance(paths['sources'], list), "paths.sources must be array"
        assert isinstance(paths['tests'], list), "paths.tests must be array"
        assert paths['readme'] is None or isinstance(paths['readme'], str), "paths.readme must be string or null"

        # Contract: NO 'descriptors' object (that's wrong structure)
        assert 'descriptors' not in module, "Module must NOT have 'descriptors' (use paths.descriptor)"


def test_metadata_uses_snake_case():
    """Contract: Metadata fields must use snake_case (artifact_id, group_id)."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <description>Test app</description>
    <packaging>jar</packaging>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        metadata = modules[0]['metadata']

        # Contract: snake_case field names
        assert 'artifact_id' in metadata, "metadata must have 'artifact_id' (snake_case)"
        assert 'group_id' in metadata, "metadata must have 'group_id' (snake_case)"

        # Contract: NO camelCase
        assert 'artifactId' not in metadata, "metadata must NOT have 'artifactId' (use snake_case)"
        assert 'groupId' not in metadata, "metadata must NOT have 'groupId' (use snake_case)"

        # Correct values
        assert metadata['artifact_id'] == 'my-app'
        assert metadata['group_id'] == 'com.example'


def test_metadata_parent_is_string():
    """Contract: metadata.parent must be string 'groupId:artifactId', not object."""
    with BuildTestContext() as ctx:
        # Parent pom
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>parent</artifactId>
    <packaging>pom</packaging>
    <modules><module>child</module></modules>
</project>''')

        # Child with parent
        child_dir = ctx.temp_dir / 'child'
        child_dir.mkdir()
        (child_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
    </parent>
    <artifactId>child</artifactId>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        child = modules[0]

        # Contract: parent is a string
        assert 'parent' in child['metadata'], "metadata must have 'parent'"
        parent = child['metadata']['parent']
        assert isinstance(parent, str), f"parent must be string, got {type(parent)}"
        assert parent == 'com.example:parent', f"parent should be 'groupId:artifactId', got '{parent}'"


def test_metadata_has_no_type_field():
    """Contract: metadata must NOT have 'type' field (Quarkus inferred from deps)."""
    with BuildTestContext() as ctx:
        # Quarkus project
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>quarkus-app</artifactId>
    <build>
        <plugins>
            <plugin>
                <groupId>io.quarkus</groupId>
                <artifactId>quarkus-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        # Contract: NO type field
        assert 'type' not in modules[0]['metadata'], "metadata must NOT have 'type' (infer from dependencies)"


def test_metadata_has_no_modules_field():
    """Contract: metadata must NOT have 'modules' field (child modules not included)."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>parent</artifactId>
    <packaging>pom</packaging>
    <modules>
        <module>child</module>
    </modules>
</project>''')

        child_dir = ctx.temp_dir / 'child'
        child_dir.mkdir()
        (child_dir / 'pom.xml').write_text('<project><artifactId>child</artifactId></project>')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        for module in modules:
            assert 'modules' not in module['metadata'], "metadata must NOT have 'modules' field"


def test_packages_is_object_keyed_by_name():
    """Contract: packages must be object keyed by package name, not array."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        pkg_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        pkg_dir.mkdir(parents=True)
        (pkg_dir / 'Foo.java').write_text('public class Foo {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        packages = modules[0]['packages']

        # Contract: packages is a dict keyed by package name
        assert isinstance(packages, dict), f"packages must be object, got {type(packages)}"
        assert 'com.example' in packages, "packages must be keyed by package name"

        # Contract: each package has path
        pkg = packages['com.example']
        assert 'path' in pkg, "each package must have 'path'"


def test_packages_has_package_info_when_exists():
    """Contract: packages include package_info path when package-info.java exists."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        pkg_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        pkg_dir.mkdir(parents=True)
        (pkg_dir / 'Foo.java').write_text('public class Foo {}')
        (pkg_dir / 'package-info.java').write_text('/** Docs */\npackage com.example;')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        pkg = modules[0]['packages']['com.example']

        # Contract: package_info path when file exists
        assert 'package_info' in pkg, "package must have 'package_info' when file exists"
        assert pkg['package_info'].endswith('package-info.java')


def test_dependencies_are_strings():
    """Contract: dependencies must be strings in format 'groupId:artifactId:scope'."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>test</artifactId>
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
        </dependency>
    </dependencies>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        deps = modules[0]['dependencies']

        # Contract: dependencies is array of strings
        assert isinstance(deps, list), "dependencies must be array"
        assert len(deps) == 2

        for dep in deps:
            assert isinstance(dep, str), f"each dependency must be string, got {type(dep)}"
            parts = dep.split(':')
            assert len(parts) == 3, f"dependency must be 'groupId:artifactId:scope', got '{dep}'"

        # Contract: format is groupId:artifactId:scope
        assert 'org.junit.jupiter:junit-jupiter:test' in deps
        assert 'com.google.guava:guava:compile' in deps  # default scope


def test_stats_has_only_source_and_test_files():
    """Contract: stats must only have source_files and test_files (no has_readme)."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')
        (ctx.temp_dir / 'README.md').write_text('# Test')

        src_dir = ctx.temp_dir / 'src' / 'main' / 'java' / 'com'
        src_dir.mkdir(parents=True)
        (src_dir / 'Foo.java').write_text('public class Foo {}')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        stats = modules[0]['stats']

        # Contract: only these two fields
        assert 'source_files' in stats, "stats must have 'source_files'"
        assert 'test_files' in stats, "stats must have 'test_files'"

        # Contract: NO has_readme
        assert 'has_readme' not in stats, "stats must NOT have 'has_readme'"


def test_module_has_commands():
    """Contract: module must have 'commands' with resolved canonical command strings."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <artifactId>test</artifactId>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        module = modules[0]

        # Contract: commands object exists
        assert 'commands' in module, "module must have 'commands'"
        commands = module['commands']
        assert isinstance(commands, dict), "commands must be object"

        # Contract: at least module-tests and verify
        assert 'module-tests' in commands, "commands must have 'module-tests'"
        assert 'verify' in commands, "commands must have 'verify'"

        # Contract: commands are resolved strings
        for cmd_name, cmd_value in commands.items():
            assert isinstance(cmd_value, str), f"command '{cmd_name}' must be string"
            assert 'python3' in cmd_value or 'mvnw' in cmd_value, f"command must be executable"


# =============================================================================
# Test: Basic Module Discovery
# =============================================================================

def test_discover_modules_single_module():
    """Test discover_modules with single-module Maven project."""
    with BuildTestContext() as ctx:
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>
    <description>My sample application</description>
    <packaging>jar</packaging>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(pom_content)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        module = modules[0]

        assert module['name'] == 'my-app'
        assert module['paths']['module'] == '.'
        assert module['technology'] == 'maven'
        assert module['metadata']['artifact_id'] == 'my-app'
        assert module['metadata']['group_id'] == 'com.example'
        assert module['metadata']['description'] == 'My sample application'
        assert module['metadata']['packaging'] == 'jar'


def test_discover_modules_multi_module():
    """Test discover_modules with multi-module Maven project."""
    with BuildTestContext() as ctx:
        parent_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>parent</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    <modules>
        <module>core</module>
        <module>web</module>
    </modules>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(parent_pom)

        # Create core module
        core_dir = ctx.temp_dir / 'core'
        core_dir.mkdir()
        core_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
    </parent>
    <artifactId>core</artifactId>
    <description>Core library module</description>
</project>'''
        (core_dir / 'pom.xml').write_text(core_pom)

        # Create web module
        web_dir = ctx.temp_dir / 'web'
        web_dir.mkdir()
        web_pom = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
    </parent>
    <artifactId>web</artifactId>
    <packaging>war</packaging>
</project>'''
        (web_dir / 'pom.xml').write_text(web_pom)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 2

        # Find modules by name
        core_module = next(m for m in modules if m['name'] == 'core')
        web_module = next(m for m in modules if m['name'] == 'web')

        assert core_module['paths']['module'] == 'core'
        assert core_module['metadata']['description'] == 'Core library module'
        assert core_module['metadata']['parent'] == 'com.example:parent'

        assert web_module['paths']['module'] == 'web'
        assert web_module['metadata']['packaging'] == 'war'


def test_discover_modules_no_pom():
    """Test discover_modules with no pom.xml."""
    with BuildTestContext() as ctx:
        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 0


# =============================================================================
# Test: Source Directory Discovery
# =============================================================================

def test_discover_sources():
    """Test source directory discovery."""
    with BuildTestContext() as ctx:
        (ctx.temp_dir / 'pom.xml').write_text('<project><artifactId>test</artifactId></project>')

        # Create standard Maven layout
        (ctx.temp_dir / 'src' / 'main' / 'java' / 'com').mkdir(parents=True)
        (ctx.temp_dir / 'src' / 'test' / 'java' / 'com').mkdir(parents=True)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        assert len(modules) == 1
        paths = modules[0]['paths']

        assert 'src/main/java' in paths['sources']
        assert 'src/test/java' in paths['tests']


# =============================================================================
# Test: Nested Module Discovery
# =============================================================================

def test_discover_nested_modules():
    """Test discovery of nested modules (grandchildren)."""
    with BuildTestContext() as ctx:
        # Create root pom with child-parent module
        (ctx.temp_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>root</artifactId>
    <packaging>pom</packaging>
    <modules>
        <module>child-parent</module>
    </modules>
</project>''')

        # Create child-parent module
        child_parent_dir = ctx.temp_dir / 'child-parent'
        child_parent_dir.mkdir()
        (child_parent_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>root</artifactId>
    </parent>
    <artifactId>child-parent</artifactId>
    <packaging>pom</packaging>
    <modules>
        <module>grandchild-a</module>
        <module>grandchild-b</module>
    </modules>
</project>''')

        # Create grandchild-a
        grandchild_a_dir = child_parent_dir / 'grandchild-a'
        grandchild_a_dir.mkdir()
        (grandchild_a_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>child-parent</artifactId>
    </parent>
    <artifactId>grandchild-a</artifactId>
    <description>First grandchild module</description>
</project>''')

        # Create grandchild-b
        grandchild_b_dir = child_parent_dir / 'grandchild-b'
        grandchild_b_dir.mkdir()
        (grandchild_b_dir / 'pom.xml').write_text('''<?xml version="1.0"?>
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>child-parent</artifactId>
    </parent>
    <artifactId>grandchild-b</artifactId>
    <description>Second grandchild module</description>
</project>''')

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))

        module_names = [m['name'] for m in modules]
        assert 'grandchild-a' in module_names
        assert 'grandchild-b' in module_names
        assert len(modules) == 2

        grandchild_a = next(m for m in modules if m['name'] == 'grandchild-a')
        assert grandchild_a['paths']['module'] == 'child-parent/grandchild-a'


# =============================================================================
# Test: Profile Detection
# =============================================================================

def test_profiles_in_metadata():
    """Contract: metadata.profiles contains detected Maven profiles."""
    with BuildTestContext() as ctx:
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <artifactId>test</artifactId>
    <profiles>
        <profile>
            <id>pre-commit</id>
        </profile>
        <profile>
            <id>integration-tests</id>
            <activation>
                <property>
                    <name>it</name>
                </property>
            </activation>
        </profile>
    </profiles>
</project>'''
        (ctx.temp_dir / 'pom.xml').write_text(pom_content)

        ext = Extension()
        modules = ext.discover_modules(str(ctx.temp_dir))
        profiles = modules[0]['metadata'].get('profiles', [])

        # Contract: profiles is array
        assert isinstance(profiles, list), "profiles must be array"
        assert len(profiles) >= 2

        # Contract: each profile has id, canonical, activation
        for profile in profiles:
            assert 'id' in profile, "profile must have 'id'"
            assert 'canonical' in profile, "profile must have 'canonical'"
            assert 'activation' in profile, "profile must have 'activation'"


# =============================================================================
# Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Contract compliance tests (MUST pass for spec compliance)
        test_module_has_technology_not_build_systems,
        test_module_has_paths_object,
        test_metadata_uses_snake_case,
        test_metadata_parent_is_string,
        test_metadata_has_no_type_field,
        test_metadata_has_no_modules_field,
        test_packages_is_object_keyed_by_name,
        test_packages_has_package_info_when_exists,
        test_dependencies_are_strings,
        test_stats_has_only_source_and_test_files,
        test_module_has_commands,

        # Functional tests
        test_discover_modules_single_module,
        test_discover_modules_multi_module,
        test_discover_modules_no_pom,
        test_discover_sources,
        test_discover_nested_modules,
        test_profiles_in_metadata,
    ])
    sys.exit(runner.run())
