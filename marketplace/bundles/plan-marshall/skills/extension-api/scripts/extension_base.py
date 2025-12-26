#!/usr/bin/env python3
"""Abstract base class for extension.py implementations.

Provides default implementations for optional functions while requiring
implementation of essential functions via abstract methods.

Usage:
    from extension_base import ExtensionBase

    class Extension(ExtensionBase):
        def is_applicable(self, project_root: str) -> bool:
            return (Path(project_root) / "pom.xml").exists()

        def get_skill_domains(self) -> dict:
            return {"domain": {...}, "profiles": {...}}

        # Override other methods as needed
"""

from abc import ABC, abstractmethod
from pathlib import Path


# =============================================================================
# Canonical Command Constants
# =============================================================================

CMD_COMPILE = "compile"
CMD_TEST_COMPILE = "test-compile"
CMD_MODULE_TESTS = "module-tests"
CMD_INTEGRATION_TESTS = "integration-tests"
CMD_COVERAGE = "coverage"
CMD_PERFORMANCE = "performance"
CMD_QUALITY_GATE = "quality-gate"
CMD_VERIFY = "verify"
CMD_INSTALL = "install"
CMD_PACKAGE = "package"

ALL_CANONICAL_COMMANDS = [
    CMD_COMPILE,
    CMD_TEST_COMPILE,
    CMD_MODULE_TESTS,
    CMD_INTEGRATION_TESTS,
    CMD_COVERAGE,
    CMD_PERFORMANCE,
    CMD_QUALITY_GATE,
    CMD_VERIFY,
    CMD_INSTALL,
    CMD_PACKAGE,
]


# =============================================================================
# Profile Classification Patterns
# =============================================================================

PROFILE_PATTERNS = {
    # Integration test patterns -> CMD_INTEGRATION_TESTS
    "integration-tests": CMD_INTEGRATION_TESTS,
    "integration-test": CMD_INTEGRATION_TESTS,
    "integrationTest": CMD_INTEGRATION_TESTS,
    "it": CMD_INTEGRATION_TESTS,
    "e2e": CMD_INTEGRATION_TESTS,
    "acceptance": CMD_INTEGRATION_TESTS,

    # Coverage patterns -> CMD_COVERAGE
    "coverage": CMD_COVERAGE,
    "jacoco": CMD_COVERAGE,

    # Quality patterns -> CMD_QUALITY_GATE
    "sonar": CMD_QUALITY_GATE,
    "pre-commit": CMD_QUALITY_GATE,
    "precommit": CMD_QUALITY_GATE,
    "lint": CMD_QUALITY_GATE,
    "check": CMD_QUALITY_GATE,
    "quality": CMD_QUALITY_GATE,

    # Performance patterns -> CMD_PERFORMANCE
    "benchmark": CMD_PERFORMANCE,
    "benchmarks": CMD_PERFORMANCE,
    "jmh": CMD_PERFORMANCE,
    "perf": CMD_PERFORMANCE,
    "performance": CMD_PERFORMANCE,
    "stress": CMD_PERFORMANCE,
    "load": CMD_PERFORMANCE,
}


# =============================================================================
# Canonical Command Metadata
# =============================================================================

CANONICAL_COMMANDS = {
    # Build phase
    CMD_COMPILE: {
        "phase": "build",
        "description": "Compile production sources only",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus"],
    },
    CMD_TEST_COMPILE: {
        "phase": "build",
        "description": "Compile production and test sources",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus"],
    },

    # Test phase
    CMD_MODULE_TESTS: {
        "phase": "test",
        "description": "Unit tests for the module (JUnit, Jest, pytest)",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    CMD_INTEGRATION_TESTS: {
        "phase": "test",
        "description": "Integration tests (containers, external services)",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    CMD_COVERAGE: {
        "phase": "test",
        "description": "Test execution with coverage measurement",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    CMD_PERFORMANCE: {
        "phase": "test",
        "description": "Performance/benchmark tests (JMH, k6, wrk)",
        "required": False,
        "applicable_to": ["jar", "quarkus", "npm"],
    },

    # Quality phase
    CMD_QUALITY_GATE: {
        "phase": "quality",
        "description": "Static analysis, linting, formatting checks",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "pom", "npm"],
    },

    # Verify phase
    CMD_VERIFY: {
        "phase": "verify",
        "description": "Full verification (compile + test + quality)",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },

    # Deploy phase
    CMD_INSTALL: {
        "phase": "deploy",
        "description": "Install artifact to local repository",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "pom"],
    },
    CMD_PACKAGE: {
        "phase": "deploy",
        "description": "Create deployable artifact (jar, war, native)",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
}


class ExtensionBase(ABC):
    """Abstract base class for domain bundle extensions.

    Subclasses must implement:
        - is_applicable: Project detection logic
        - get_skill_domains: Domain metadata and skill profiles

    All other methods have sensible defaults for non-build bundles.
    Build bundles should override build-related methods.
    """

    # =========================================================================
    # Required Methods (must be implemented)
    # =========================================================================

    @abstractmethod
    def is_applicable(self, project_root: str) -> bool:
        """Check if this bundle applies to the project.

        Args:
            project_root: Absolute path to the project root directory.

        Returns:
            True if this bundle should be activated for the project.

        Examples:
            - Check for pom.xml/build.gradle for Java bundles
            - Check for package.json for JavaScript bundles
            - Check for doc/ directory for documentation bundles
        """
        pass

    @abstractmethod
    def get_skill_domains(self) -> dict:
        """Return domain metadata for skill loading.

        Returns:
            Dict with domain identity and profile-based skill organization:
            {
                "domain": {
                    "key": str,          # Unique domain identifier
                    "name": str,         # Human-readable name
                    "description": str   # Domain description
                },
                "profiles": {
                    "core": {"defaults": [...], "optionals": [...]},
                    "implementation": {"defaults": [...], "optionals": [...]},
                    "testing": {"defaults": [...], "optionals": [...]},
                    "quality": {"defaults": [...], "optionals": [...]}
                }
            }
        """
        pass

    # =========================================================================
    # Build System Methods (override for build bundles)
    # =========================================================================

    def provides_build_systems(self) -> list:
        """Return build system keys this bundle handles (static declaration).

        Returns:
            List of build system keys (e.g., ["maven", "gradle"]).
            Empty list if bundle doesn't provide build systems.

        Valid Keys:
            - "maven" - Maven build system
            - "gradle" - Gradle build system
            - "npm" - npm/Node.js build system
        """
        return []

    def get_applicable_build_systems(self, project_root: str) -> list:
        """Return build systems actually present in the project.

        Args:
            project_root: Absolute path to project root.

        Returns:
            List of build system keys present (e.g., ["maven"]).
            Empty list if no applicable build systems found.

        Notes:
            Override this for build bundles to check for actual build files.
            Default implementation returns empty list.
        """
        return []

    def get_command_mappings(self) -> dict:
        """Return canonical command name to script invocation mappings.

        Returns:
            Nested dict: {build_system: {canonical_name: command_template}}
            Empty dict if bundle doesn't provide build commands.

        Template Placeholders:
            {module} - Replaced with ' --module <name>' or '' by persist

        Canonical Names:
            compile, test-compile, module-tests, integration-tests,
            coverage, performance, quality-gate, verify, install, package
        """
        return {}

    # =========================================================================
    # Module Detection Methods (override for build bundles)
    # =========================================================================

    def get_modules(self, project_root: str) -> list:
        """Return project modules detected by this build system.

        Args:
            project_root: Absolute path to project root.

        Returns:
            List of module dicts:
            [{"name": str, "path": str, "build_system": str}]

        Examples:
            - Maven: Parse pom.xml <modules> section
            - Gradle: Parse settings.gradle include() statements
            - npm: Parse package.json workspaces
        """
        return []

    def get_module_type(self, module_path: str) -> str:
        """Return the module type for a given module path.

        Args:
            module_path: Absolute path to module directory.

        Returns:
            Module type string:
            - "unknown" - Default for non-build bundles
            - "pom" - Parent/BOM module (Maven)
            - "jar" - Library module (Java)
            - "war" - Web application
            - "quarkus" - Quarkus application
            - "npm" - npm project
        """
        return "unknown"

    def get_profiles(self, module_path: str) -> list:
        """Return build profiles for a module.

        Args:
            module_path: Absolute path to module directory.

        Returns:
            List of profile dicts:
            [{
                "id": str,
                "canonical": str | None,
                "activation": {"type": str, ...}
            }]

        Notes:
            Use classify_profile() helper to map profile IDs to canonical names.
            See PROFILE_PATTERNS for the mapping vocabulary.
        """
        return []

    def classify_profile(self, profile_id: str) -> str | None:
        """Classify a profile ID to its canonical command name.

        Args:
            profile_id: The profile identifier (e.g., "integration-tests", "jacoco")

        Returns:
            Canonical command name (e.g., CMD_INTEGRATION_TESTS) or None if not recognized.

        Notes:
            Uses PROFILE_PATTERNS vocabulary for classification.
            Matching is case-insensitive and supports partial matches.
        """
        profile_lower = profile_id.lower()

        # Exact match first
        if profile_id in PROFILE_PATTERNS:
            return PROFILE_PATTERNS[profile_id]

        # Case-insensitive exact match
        for pattern, canonical in PROFILE_PATTERNS.items():
            if pattern.lower() == profile_lower:
                return canonical

        # Substring match (e.g., "my-integration-tests" matches "integration-tests")
        for pattern, canonical in PROFILE_PATTERNS.items():
            if pattern.lower() in profile_lower:
                return canonical

        return None

    def generate_profile_command(
        self,
        build_system: str,
        canonical: str,
        profile_id: str,
        activation: dict,
        module_name: str = None
    ) -> str | None:
        """Generate a command string for a profile-based canonical command.

        Args:
            build_system: "maven", "gradle", or "npm"
            canonical: The canonical command name (e.g., "integration-tests")
            profile_id: The profile ID to activate
            activation: Dict with activation info (type, property, value)
            module_name: Optional module name for multi-module projects

        Returns:
            Command string or None if not supported
        """
        return None

    # =========================================================================
    # Command Template Helpers
    # =========================================================================

    def build_command_template(
        self,
        bundle: str,
        script: str,
        targets: str,
        include_module_placeholder: bool = True
    ) -> str:
        """Build a standardized command template for get_command_mappings().

        Provides consistent command template generation across all build bundles.

        Args:
            bundle: Bundle name (e.g., "pm-dev-java", "pm-dev-frontend")
            script: Script name within plan-marshall-plugin (e.g., "maven", "npm")
            targets: Build targets/goals (e.g., "clean test", "run build")
            include_module_placeholder: Whether to append {module} placeholder

        Returns:
            Command template string like:
            'python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets "clean test"{module}'

        Example:
            # In pm-dev-java extension:
            def get_command_mappings(self):
                return {
                    "maven": {
                        CMD_COMPILE: self.build_command_template(
                            "pm-dev-java", "maven", "compile"
                        ),
                    }
                }
        """
        base = f'python3 .plan/execute-script.py {bundle}:plan-marshall-plugin:{script} run --targets "{targets}"'
        if include_module_placeholder:
            base += "{module}"
        return base

    # =========================================================================
    # Workflow Extension Methods (override if providing capabilities)
    # =========================================================================

    def provides_triage(self) -> str | None:
        """Return triage skill reference if available.

        Returns:
            Skill reference as 'bundle:skill' (e.g., 'pm-dev-java:java-triage')
            or None if no triage capability.

        Purpose:
            Triage skills categorize and prioritize findings during
            the plan-finalize phase.
        """
        return None

    def provides_outline(self) -> str | None:
        """Return outline skill reference if available.

        Returns:
            Skill reference as 'bundle:skill'
            or None if no outline capability.

        Purpose:
            Outline skills guide solution design during the
            plan-init phase for domain-specific deliverables.
        """
        return None
