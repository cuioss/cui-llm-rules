#!/usr/bin/env python3
"""Extension API for pm-dev-java bundle.

Provides build system detection, module discovery, and command mappings
for Maven and Gradle projects.
"""

import re
from pathlib import Path

from extension_base import ExtensionBase


# Build file constants
POM_XML = "pom.xml"
BUILD_GRADLE = "build.gradle"
BUILD_GRADLE_KTS = "build.gradle.kts"
SETTINGS_GRADLE = "settings.gradle"
SETTINGS_GRADLE_KTS = "settings.gradle.kts"

# Profile pattern to canonical name mapping
PROFILE_TO_CANONICAL = {
    # Integration test patterns -> "integration-tests"
    "integration-tests": "integration-tests",
    "integration-test": "integration-tests",
    "integrationTest": "integration-tests",
    "it": "integration-tests",
    "e2e": "integration-tests",
    "acceptance": "integration-tests",

    # Coverage patterns -> "coverage"
    "coverage": "coverage",
    "jacoco": "coverage",

    # Quality patterns -> "quality-gate"
    "sonar": "quality-gate",
    "pre-commit": "quality-gate",
    "precommit": "quality-gate",
    "lint": "quality-gate",
    "check": "quality-gate",
    "quality": "quality-gate",

    # Performance patterns -> "performance"
    "benchmark": "performance",
    "benchmarks": "performance",
    "jmh": "performance",
    "perf": "performance",
    "performance": "performance",
    "stress": "performance",
    "load": "performance",
}


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
        base_maven = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"
        base_gradle = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:gradle run"

        return {
            "maven": {
                "compile": f'{base_maven} --targets "compile"{{module}}',
                "test-compile": f'{base_maven} --targets "test-compile"{{module}}',
                "module-tests": f'{base_maven} --targets "clean test"{{module}}',
                "integration-tests": f'{base_maven} --targets "clean verify -Pintegration-tests"{{module}}',
                "coverage": f'{base_maven} --targets "clean verify -Pcoverage"{{module}}',
                "quality-gate": f'{base_maven} --targets "clean verify -Ppre-commit"{{module}}',
                "verify": f'{base_maven} --targets "clean verify"{{module}}',
                "install": f'{base_maven} --targets "clean install"{{module}}',
                "package": f'{base_maven} --targets "package"{{module}}',
            },
            "gradle": {
                "compile": f'{base_gradle} --targets "compileJava"{{module}}',
                "test-compile": f'{base_gradle} --targets "testClasses"{{module}}',
                "module-tests": f'{base_gradle} --targets "clean test"{{module}}',
                "integration-tests": f'{base_gradle} --targets "clean integrationTest"{{module}}',
                "coverage": f'{base_gradle} --targets "clean test jacocoTestReport"{{module}}',
                "quality-gate": f'{base_gradle} --targets "clean check"{{module}}',
                "verify": f'{base_gradle} --targets "clean build"{{module}}',
                "install": f'{base_gradle} --targets "clean publishToMavenLocal"{{module}}',
                "package": f'{base_gradle} --targets "clean assemble"{{module}}',
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
    # Maven Detection Helpers
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
            canonical = self._classify_profile(profile_id)
            activation = self._detect_profile_activation(content, profile_id)

            profiles.append({
                "id": profile_id,
                "canonical": canonical,
                "activation": activation,
            })

        return profiles

    def _classify_profile(self, profile_id: str) -> str | None:
        """Classify a profile ID to its canonical name."""
        profile_lower = profile_id.lower()

        if profile_id in PROFILE_TO_CANONICAL:
            return PROFILE_TO_CANONICAL[profile_id]

        for pattern, canonical in PROFILE_TO_CANONICAL.items():
            if pattern.lower() == profile_lower:
                return canonical

        for pattern, canonical in PROFILE_TO_CANONICAL.items():
            if pattern.lower() in profile_lower:
                return canonical

        return None

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
        """Detect Gradle profiles from settings.gradle."""
        # Gradle doesn't have Maven-style profiles
        return []
