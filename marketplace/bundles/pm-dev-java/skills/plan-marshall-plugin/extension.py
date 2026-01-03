#!/usr/bin/env python3
"""Extension API for pm-dev-java bundle.

Provides build system detection, module discovery, and command mappings
for Maven and Gradle projects.
"""

import re
from pathlib import Path

from extension_base import (
    ExtensionBase,
    CMD_COMPILE,
    CMD_TEST_COMPILE,
    CMD_MODULE_TESTS,
    CMD_VERIFY,
    CMD_INSTALL,
    CMD_PACKAGE,
)


# Build file constants
POM_XML = "pom.xml"
BUILD_GRADLE = "build.gradle"
BUILD_GRADLE_KTS = "build.gradle.kts"
SETTINGS_GRADLE = "settings.gradle"
SETTINGS_GRADLE_KTS = "settings.gradle.kts"


class Extension(ExtensionBase):
    """Java/Maven/Gradle extension for pm-dev-java bundle."""

    def is_applicable(self, project_root: str) -> bool:
        """Check if Java bundle applies to the project."""
        root = Path(project_root)
        return (
            (root / POM_XML).exists() or
            (root / BUILD_GRADLE).exists() or
            (root / BUILD_GRADLE_KTS).exists() or
            (root / SETTINGS_GRADLE).exists() or
            (root / SETTINGS_GRADLE_KTS).exists()
        )

    def provides_build_systems(self) -> list:
        """Build system keys this bundle handles."""
        return ["maven", "gradle"]

    def get_applicable_build_systems(self, project_root: str) -> list:
        """Return build systems actually present in the project."""
        root = Path(project_root)
        systems = []

        if (root / POM_XML).exists():
            systems.append("maven")

        if any((root / f).exists() for f in [BUILD_GRADLE, BUILD_GRADLE_KTS, SETTINGS_GRADLE, SETTINGS_GRADLE_KTS]):
            systems.append("gradle")

        return systems

    def get_command_mappings(self) -> dict:
        """Return canonical -> script invocation template."""
        # Use inherited build_command_template helper for consistency
        def maven(targets: str) -> str:
            return self.build_command_template("pm-dev-java", "maven", targets)

        def gradle(targets: str) -> str:
            return self.build_command_template("pm-dev-java", "gradle", targets)

        # NOTE: Profile-dependent commands (integration-tests, coverage, quality-gate)
        # are NOT included here. They are dynamically generated from detected profiles
        # via get_profiles() + generate_profile_command(). This ensures portability
        # across projects with different profile naming conventions.
        return {
            "maven": {
                CMD_COMPILE: maven("compile"),
                CMD_TEST_COMPILE: maven("test-compile"),
                CMD_MODULE_TESTS: maven("clean test"),
                CMD_VERIFY: maven("clean verify"),
                CMD_INSTALL: maven("clean install"),
                CMD_PACKAGE: maven("package"),
            },
            "gradle": {
                CMD_COMPILE: gradle("compileJava"),
                CMD_TEST_COMPILE: gradle("testClasses"),
                CMD_MODULE_TESTS: gradle("clean test"),
                CMD_VERIFY: gradle("clean build"),
                CMD_INSTALL: gradle("clean publishToMavenLocal"),
                CMD_PACKAGE: gradle("clean assemble"),
            }
        }

    def get_skill_domains(self) -> dict:
        """Domain metadata for skill loading."""
        return {
            "domain": {
                "key": "java",
                "name": "Java Development",
                "description": "Java code patterns, CDI, JUnit testing, Maven/Gradle builds"
            },
            "profiles": {
                "core": {
                    "defaults": ["pm-dev-java:java-core"],
                    "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok"]
                },
                "implementation": {
                    "defaults": [],
                    "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
                },
                "testing": {
                    "defaults": ["pm-dev-java:junit-core"],
                    "optionals": ["pm-dev-java:junit-integration"]
                },
                "quality": {
                    "defaults": ["pm-dev-java:javadoc"],
                    "optionals": []
                }
            }
        }

    def provides_triage(self) -> str | None:
        """Return triage skill reference."""
        return "pm-dev-java:java-triage"

    def get_modules(self, project_root: str) -> list:
        """Return project modules detected by Maven or Gradle."""
        modules = []
        root = Path(project_root)

        modules.extend(self._detect_maven_modules(root))
        modules.extend(self._detect_gradle_modules(root))

        return modules

    def get_module_type(self, module_path: str) -> str:
        """Return the module type for a given module path."""
        path = Path(module_path)

        pom_path = path / POM_XML
        if pom_path.exists():
            return self._detect_maven_module_type(pom_path)

        for build_file in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
            gradle_path = path / build_file
            if gradle_path.exists():
                return self._detect_gradle_module_type(gradle_path)

        return "jar"

    def get_profiles(self, module_path: str) -> list:
        """Return build profiles for a module."""
        path = Path(module_path)
        profiles = []

        pom_path = path / POM_XML
        if pom_path.exists():
            profiles.extend(self._detect_maven_profiles(pom_path))

        for settings_file in [SETTINGS_GRADLE_KTS, SETTINGS_GRADLE]:
            settings_path = path / settings_file
            if settings_path.exists():
                profiles.extend(self._detect_gradle_profiles(settings_path))
                break

        return profiles

    def generate_profile_command(
        self,
        build_system: str,
        canonical: str,
        profile_id: str,
        activation: dict,
        module_name: str = None
    ) -> str | None:
        """Generate a command string for a profile-based canonical command."""
        if build_system == "maven":
            if activation.get("type") == "property":
                prop_name = activation.get("property", "")
                prop_value = activation.get("value")
                if prop_value:
                    targets = f"clean verify -D{prop_name}={prop_value}"
                else:
                    targets = f"clean verify -D{prop_name}"
            else:
                targets = f"clean verify -P{profile_id}"

            cmd = f'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets "{targets}"'

        elif build_system == "gradle":
            cmd = f'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run --targets "clean {profile_id}"'

        else:
            return None

        if module_name and module_name != "default":
            cmd += f" --module {module_name}"

        return cmd

    # =========================================================================
    # discover_modules() Implementation
    # =========================================================================

    def discover_modules(self, project_root: str) -> list:
        """Discover all modules with complete metadata.

        Implements the unified discover_modules() API for Maven and Gradle projects.
        Returns comprehensive module information including metadata, dependencies,
        packages, and stats.
        """
        modules = []
        root = Path(project_root)

        # Discover Maven modules first (takes priority)
        maven_modules = self._discover_maven_modules(root)
        modules.extend(maven_modules)

        # Discover Gradle modules (only if no Maven found at same path)
        maven_paths = {m['path'] for m in maven_modules}
        for gradle_module in self._discover_gradle_full_modules(root):
            if gradle_module['path'] not in maven_paths:
                modules.append(gradle_module)

        return modules

    def _discover_maven_modules(self, project_dir: Path, project_root: Path = None, base_path: str = "") -> list:
        """Discover Maven modules with complete metadata.

        Recursively discovers nested modules. When a module has <modules>,
        it recurses into those children instead of including the parent POM.

        Args:
            project_dir: Current directory to scan for pom.xml
            project_root: Root of the project (for relative path calculation)
            base_path: Path prefix for nested modules (e.g., "parent/child")

        Returns:
            List of discovered module data dicts
        """
        modules = []
        pom_path = project_dir / POM_XML

        if not pom_path.exists():
            return modules

        # Initialize project_root on first call
        if project_root is None:
            project_root = project_dir

        # Parse pom.xml for module list
        content = pom_path.read_text()
        child_module_names = []

        modules_match = re.search(r'<modules>(.*?)</modules>', content, re.DOTALL)
        if modules_match:
            module_content = modules_match.group(1)
            for module_name in re.findall(r'<module>([^<]+)</module>', module_content):
                module_path = project_dir / module_name
                if module_path.exists():
                    child_module_names.append(module_name)

        # If multi-module project, recurse into each child module
        if child_module_names:
            for module_name in child_module_names:
                module_path = project_dir / module_name
                # Calculate the relative path from project root
                relative_path = f"{base_path}/{module_name}" if base_path else module_name

                # Recursively discover nested modules
                nested_modules = self._discover_maven_modules(module_path, project_root, relative_path)
                if nested_modules:
                    # Module has nested children - use those instead
                    modules.extend(nested_modules)
                else:
                    # Leaf module - extract its data
                    module_data = self._extract_maven_module_data(module_path, project_root, relative_path)
                    if module_data:
                        modules.append(module_data)
        else:
            # Single-module project or leaf module - discover it
            module_data = self._extract_maven_module_data(project_dir, project_root, base_path)
            if module_data:
                modules.append(module_data)

        return modules

    def _extract_maven_module_data(self, module_path: Path, project_root: Path, relative_path: str) -> dict | None:
        """Extract complete module data from a Maven module."""
        pom_path = module_path / POM_XML
        if not pom_path.exists():
            return None

        content = pom_path.read_text()

        # Extract basic metadata from pom.xml
        artifact_id = self._extract_xml_value(content, "artifactId")
        group_id = self._extract_xml_value(content, "groupId")
        description = self._extract_xml_value(content, "description")
        packaging = self._extract_xml_value(content, "packaging") or "jar"

        # Detect module type
        module_type = self._detect_maven_module_type(pom_path)

        # Detect parent
        parent_artifact = self._extract_xml_value(content, "parent/artifactId")
        parent_info = None
        if parent_artifact:
            parent_info = {
                "name": parent_artifact,
                "path": ".."  # Relative to module
            }

        # Detect child modules
        child_modules = []
        modules_match = re.search(r'<modules>(.*?)</modules>', content, re.DOTALL)
        if modules_match:
            module_content = modules_match.group(1)
            child_modules = re.findall(r'<module>([^<]+)</module>', module_content)

        # Discover source directories
        sources = self._discover_maven_sources(module_path)

        # Discover packages
        packages = self._discover_maven_packages(module_path, sources)

        # Calculate stats
        source_files = self._count_java_files(module_path, sources["main"])
        test_files = self._count_java_files(module_path, sources["test"])
        has_readme = self._check_readme(module_path)

        # Determine build systems (could be maven+npm for hybrid)
        build_systems = ["maven"]
        package_json = module_path / "package.json"
        if package_json.exists():
            build_systems.append("npm")

        # Build descriptors
        descriptors = {
            "pom": str(Path(relative_path) / POM_XML) if relative_path else POM_XML,
            "gradle": None,
            "package": str(Path(relative_path) / "package.json") if package_json.exists() else None
        }

        # Extract dependencies (simplified - from pom.xml only)
        dependencies = self._extract_maven_dependencies(content)

        return {
            "name": artifact_id or module_path.name,
            "path": relative_path if relative_path else ".",
            "build_systems": build_systems,
            "descriptors": descriptors,
            "metadata": {
                "description": description,
                "groupId": group_id,
                "artifactId": artifact_id,
                "packaging": packaging,
                "type": module_type,
                "parent": parent_info,
                "modules": child_modules
            },
            "sources": sources,
            "packages": packages,
            "dependencies": dependencies,
            "stats": {
                "source_files": source_files,
                "test_files": test_files,
                "has_readme": has_readme
            }
        }

    def _extract_xml_value(self, content: str, tag: str) -> str | None:
        """Extract value from XML tag (simple, non-nested).

        For top-level tags like 'artifactId', this skips values inside <parent> blocks.
        For nested paths like 'parent/artifactId', it extracts from within the parent block.
        """
        # Handle nested paths like "parent/artifactId"
        if "/" in tag:
            parts = tag.split("/")
            parent_tag = parts[0]
            child_tag = parts[1]
            # Find parent block first
            parent_match = re.search(rf'<{parent_tag}>(.*?)</{parent_tag}>', content, re.DOTALL)
            if parent_match:
                parent_content = parent_match.group(1)
                match = re.search(rf'<{child_tag}>([^<]+)</{child_tag}>', parent_content)
                return match.group(1).strip() if match else None
            return None

        # For top-level tags, strip out the <parent> block first to avoid false matches
        if tag in ['artifactId', 'groupId', 'version', 'description', 'packaging']:
            content_no_parent = re.sub(r'<parent>.*?</parent>', '', content, flags=re.DOTALL)
            match = re.search(rf'<{tag}>([^<]+)</{tag}>', content_no_parent)
        else:
            match = re.search(rf'<{tag}>([^<]+)</{tag}>', content)

        return match.group(1).strip() if match else None

    def _discover_maven_sources(self, module_path: Path) -> dict:
        """Discover source directories for a Maven module."""
        sources = {
            "main": [],
            "test": [],
            "resources": []
        }

        # Standard Maven layout
        main_java = module_path / "src" / "main" / "java"
        if main_java.exists():
            sources["main"].append("src/main/java")

        test_java = module_path / "src" / "test" / "java"
        if test_java.exists():
            sources["test"].append("src/test/java")

        main_resources = module_path / "src" / "main" / "resources"
        if main_resources.exists():
            sources["resources"].append("src/main/resources")

        test_resources = module_path / "src" / "test" / "resources"
        if test_resources.exists():
            sources["resources"].append("src/test/resources")

        return sources

    def _discover_maven_packages(self, module_path: Path, sources: dict) -> list:
        """Discover Java packages in a Maven module."""
        packages = []

        for source_dir in sources.get("main", []):
            source_path = module_path / source_dir
            if not source_path.exists():
                continue

            # Find all directories that contain .java files or package-info.java
            for java_dir in source_path.rglob("*.java"):
                package_dir = java_dir.parent
                package_name = str(package_dir.relative_to(source_path)).replace("/", ".").replace("\\", ".")

                if package_name and package_name not in [p["name"] for p in packages]:
                    # Check for package-info.java
                    package_info = package_dir / "package-info.java"
                    description = None
                    if package_info.exists():
                        description = self._extract_package_description(package_info)

                    # Count files in this package (non-recursive)
                    source_files = len(list(package_dir.glob("*.java")))

                    # Check for corresponding test package
                    test_dir = module_path / "src" / "test" / "java" / str(package_dir.relative_to(source_path))
                    test_files = len(list(test_dir.glob("*.java"))) if test_dir.exists() else 0

                    packages.append({
                        "name": package_name,
                        "path": str(package_dir.relative_to(module_path)),
                        "description": description,
                        "source_files": source_files,
                        "test_files": test_files
                    })

        return packages

    def _extract_package_description(self, package_info: Path) -> str | None:
        """Extract package description from package-info.java JavaDoc."""
        try:
            content = package_info.read_text()
            # Extract first line of JavaDoc comment
            javadoc_match = re.search(r'/\*\*\s*\n?\s*\*?\s*([^\n*]+)', content)
            if javadoc_match:
                description = javadoc_match.group(1).strip()
                # Clean up common prefixes
                description = re.sub(r'^Provides\s+', '', description)
                description = re.sub(r'^Contains\s+', '', description)
                return description if description else None
        except Exception:
            pass
        return None

    def _count_java_files(self, module_path: Path, source_dirs: list) -> int:
        """Count Java files in source directories."""
        count = 0
        for source_dir in source_dirs:
            source_path = module_path / source_dir
            if source_path.exists():
                count += len(list(source_path.rglob("*.java")))
        return count

    def _check_readme(self, module_path: Path) -> bool:
        """Check if module has a README file."""
        readme_patterns = ["README.md", "README.adoc", "README.txt", "README"]
        return any((module_path / f).exists() for f in readme_patterns)

    def _extract_maven_dependencies(self, pom_content: str) -> list:
        """Extract dependencies from pom.xml content."""
        dependencies = []

        # Find dependencies section (not dependencyManagement)
        deps_match = re.search(r'<dependencies>(.*?)</dependencies>', pom_content, re.DOTALL)
        if not deps_match:
            return dependencies

        deps_content = deps_match.group(1)

        # Skip if this looks like dependencyManagement
        if '<dependencyManagement>' in pom_content:
            # Find the actual dependencies section after dependencyManagement
            mgmt_end = pom_content.find('</dependencyManagement>')
            if mgmt_end > 0:
                remaining = pom_content[mgmt_end:]
                deps_match = re.search(r'<dependencies>(.*?)</dependencies>', remaining, re.DOTALL)
                if deps_match:
                    deps_content = deps_match.group(1)
                else:
                    deps_content = ""

        # Parse each dependency
        for dep_match in re.finditer(r'<dependency>(.*?)</dependency>', deps_content, re.DOTALL):
            dep_content = dep_match.group(1)

            group_id = self._extract_xml_value(dep_content, "groupId")
            artifact_id = self._extract_xml_value(dep_content, "artifactId")
            scope = self._extract_xml_value(dep_content, "scope") or "compile"

            if group_id and artifact_id:
                dependencies.append({
                    "groupId": group_id,
                    "artifactId": artifact_id,
                    "scope": scope
                })

        return dependencies

    # =========================================================================
    # Maven Detection Helpers (Legacy - kept for backward compatibility)
    # =========================================================================

    def _detect_maven_modules(self, project_dir: Path) -> list:
        """Detect Maven modules from pom.xml."""
        modules = []
        pom_path = project_dir / POM_XML

        if not pom_path.exists():
            return modules

        content = pom_path.read_text()

        modules_match = re.search(r'<modules>(.*?)</modules>', content, re.DOTALL)
        if modules_match:
            module_content = modules_match.group(1)
            for module in re.findall(r'<module>([^<]+)</module>', module_content):
                module_path = project_dir / module
                if module_path.exists():
                    modules.append({
                        "name": module,
                        "path": module,
                        "build_system": "maven"
                    })

        return modules

    def _detect_maven_module_type(self, pom_path: Path) -> str:
        """Detect module type from Maven pom.xml."""
        if not pom_path.exists():
            return "jar"

        content = pom_path.read_text()

        packaging_match = re.search(r'<packaging>([^<]+)</packaging>', content)
        if packaging_match:
            packaging = packaging_match.group(1).strip().lower()
            if packaging == "pom":
                return "pom"
            if packaging == "war":
                return "war"

        if "quarkus-maven-plugin" in content:
            return "quarkus"

        return "jar"

    def _detect_maven_profiles(self, pom_path: Path) -> list:
        """Detect Maven profiles from pom.xml."""
        if not pom_path.exists():
            return []

        content = pom_path.read_text()
        profiles = []

        profile_pattern = re.compile(r'<profile>\s*<id>([^<]+)</id>', re.MULTILINE)
        matches = profile_pattern.findall(content)

        for profile_id in matches:
            profile_id = profile_id.strip()
            canonical = self.classify_profile(profile_id)  # Use inherited helper
            activation = self._detect_profile_activation(content, profile_id)

            profiles.append({
                "id": profile_id,
                "canonical": canonical,
                "activation": activation,
            })

        return profiles

    def _detect_profile_activation(self, pom_content: str, profile_id: str) -> dict:
        """Detect how a Maven profile is activated."""
        profile_start = pom_content.find(f'<id>{profile_id}</id>')
        if profile_start == -1:
            return {"type": "command-line"}

        profile_end = pom_content.find('</profile>', profile_start)
        if profile_end == -1:
            profile_end = len(pom_content)

        profile_block = pom_content[profile_start:profile_end]

        prop_match = re.search(r'<activation>[\s\S]*?<property>[\s\S]*?<name>([^<]+)</name>', profile_block)
        if prop_match:
            prop_name = prop_match.group(1).strip()
            value_match = re.search(r'<property>[\s\S]*?<value>([^<]+)</value>', profile_block)
            value = value_match.group(1).strip() if value_match else None
            return {
                "type": "property",
                "property": prop_name,
                "value": value,
            }

        if '<activeByDefault>true</activeByDefault>' in profile_block:
            return {"type": "default"}

        jdk_match = re.search(r'<activation>\s*<jdk>([^<]+)</jdk>', profile_block)
        if jdk_match:
            return {"type": "jdk", "version": jdk_match.group(1).strip()}

        if '<os>' in profile_block:
            return {"type": "os"}

        return {"type": "command-line"}

    # =========================================================================
    # Gradle Detection Helpers
    # =========================================================================

    def _detect_gradle_modules(self, project_dir: Path) -> list:
        """Detect Gradle modules from settings.gradle."""
        modules = []

        for settings_file in [SETTINGS_GRADLE_KTS, SETTINGS_GRADLE]:
            settings_path = project_dir / settings_file
            if settings_path.exists():
                content = settings_path.read_text()

                for match in re.finditer(r'include\s*[(\'"]+:?([^)\'\"]+)[)\'"]+', content):
                    module_name = match.group(1).replace(':', '/')
                    module_path = project_dir / module_name
                    if module_path.exists():
                        modules.append({
                            "name": module_name.replace('/', '-'),
                            "path": module_name,
                            "build_system": "gradle"
                        })
                break

        return modules

    def _detect_gradle_module_type(self, build_file: Path) -> str:
        """Detect module type from Gradle build file."""
        if not build_file.exists():
            return "jar"

        content = build_file.read_text()

        if "war" in content and ("apply plugin:" in content or "plugins {" in content):
            if "'war'" in content or '"war"' in content:
                return "war"

        if "quarkus" in content.lower():
            return "quarkus"

        return "jar"

    def _detect_gradle_profiles(self, _settings_path: Path) -> list:
        """Detect Gradle profiles from settings.gradle.

        Returns empty list because Gradle uses a different model than Maven profiles.
        Gradle equivalents (custom tasks, build variants) are handled through
        get_command_mappings() which provides the standard canonical commands.
        Profile-based command generation is Maven-specific.
        """
        return []

    # =========================================================================
    # Gradle discover_modules() Implementation
    # =========================================================================

    def _discover_gradle_full_modules(self, project_dir: Path) -> list:
        """Discover Gradle modules with complete metadata."""
        modules = []

        # Check for settings.gradle (multi-module) or build.gradle (single module)
        settings_path = None
        for settings_file in [SETTINGS_GRADLE_KTS, SETTINGS_GRADLE]:
            if (project_dir / settings_file).exists():
                settings_path = project_dir / settings_file
                break

        if settings_path:
            # Multi-module Gradle project
            content = settings_path.read_text()
            child_modules = []

            for match in re.finditer(r'include\s*[(\'"]+:?([^)\'\"]+)[)\'"]+', content):
                module_name = match.group(1).replace(':', '/')
                module_path = project_dir / module_name
                if module_path.exists():
                    child_modules.append(module_name)

            for module_name in child_modules:
                module_path = project_dir / module_name
                module_data = self._extract_gradle_module_data(module_path, project_dir, module_name)
                if module_data:
                    modules.append(module_data)
        else:
            # Check for single-module project
            for build_file in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
                if (project_dir / build_file).exists():
                    module_data = self._extract_gradle_module_data(project_dir, project_dir, "")
                    if module_data:
                        modules.append(module_data)
                    break

        return modules

    def _extract_gradle_module_data(self, module_path: Path, project_root: Path, relative_path: str) -> dict | None:
        """Extract complete module data from a Gradle module."""
        # Find build file
        build_file = None
        for bf in [BUILD_GRADLE_KTS, BUILD_GRADLE]:
            if (module_path / bf).exists():
                build_file = module_path / bf
                break

        if not build_file:
            return None

        content = build_file.read_text()

        # Extract metadata from build.gradle
        name = self._extract_gradle_property(content, "archivesBaseName") or \
               self._extract_gradle_property(content, "rootProject.name") or \
               module_path.name

        description = self._extract_gradle_property(content, "description")
        group = self._extract_gradle_property(content, "group")
        version = self._extract_gradle_property(content, "version")

        # Detect module type
        module_type = self._detect_gradle_module_type(build_file)

        # Detect parent (root project)
        parent_info = None
        if relative_path:
            parent_info = {
                "name": project_root.name,
                "path": ".."
            }

        # Discover source directories (same as Maven layout)
        sources = self._discover_maven_sources(module_path)

        # Discover packages
        packages = self._discover_maven_packages(module_path, sources)

        # Calculate stats
        source_files = self._count_java_files(module_path, sources["main"])
        test_files = self._count_java_files(module_path, sources["test"])
        has_readme = self._check_readme(module_path)

        # Check for hybrid (Gradle + npm)
        build_systems = ["gradle"]
        package_json = module_path / "package.json"
        if package_json.exists():
            build_systems.append("npm")

        # Build descriptors
        descriptors = {
            "pom": None,
            "gradle": str(Path(relative_path) / build_file.name) if relative_path else build_file.name,
            "package": str(Path(relative_path) / "package.json") if package_json.exists() else None
        }

        return {
            "name": name,
            "path": relative_path if relative_path else ".",
            "build_systems": build_systems,
            "descriptors": descriptors,
            "metadata": {
                "description": description,
                "group": group,
                "version": version,
                "type": module_type,
                "parent": parent_info,
                "modules": []  # Child modules not tracked here
            },
            "sources": sources,
            "packages": packages,
            "dependencies": [],  # Dependencies require gradle execution (deferred)
            "stats": {
                "source_files": source_files,
                "test_files": test_files,
                "has_readme": has_readme
            }
        }

    def _extract_gradle_property(self, content: str, prop_name: str) -> str | None:
        """Extract property value from Gradle build file."""
        # Handle both Groovy and Kotlin DSL
        patterns = [
            rf'{prop_name}\s*=\s*[\'"]([^\'"]+)[\'"]',  # property = "value"
            rf'{prop_name}\s*\(\s*[\'"]([^\'"]+)[\'"]',  # property("value")
            rf'set{prop_name.capitalize()}\s*\(\s*[\'"]([^\'"]+)[\'"]',  # setProperty("value")
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()

        return None
