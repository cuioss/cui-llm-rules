#!/usr/bin/env python3
"""Abstract base class for extension.py implementations.

Provides default implementations for optional functions while requiring
implementation of essential functions via abstract methods.

Usage:
    from extension_base import ExtensionBase

    class Extension(ExtensionBase):
        def get_skill_domains(self) -> dict:
            return {"domain": {...}, "profiles": {...}}

        def discover_modules(self, project_root: str) -> list:
            # Delegate to script
            from maven_cmd_discover import discover_maven_modules
            return discover_maven_modules(project_root)
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
        "aliases": [
            "integration-tests", "integration-test", "integrationTest",
            "it", "e2e", "acceptance",
        ],
    },
    CMD_COVERAGE: {
        "phase": "test",
        "description": "Test execution with coverage measurement",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
        "aliases": ["coverage", "jacoco"],
    },
    CMD_PERFORMANCE: {
        "phase": "test",
        "description": "Performance/benchmark tests (JMH, k6, wrk)",
        "required": False,
        "applicable_to": ["jar", "quarkus", "npm"],
        "aliases": [
            "benchmark", "benchmarks", "jmh",
            "perf", "performance", "stress", "load",
        ],
    },

    # Quality phase
    CMD_QUALITY_GATE: {
        "phase": "quality",
        "description": "Static analysis, linting, formatting checks",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "pom", "npm"],
        "aliases": [
            "pre-commit", "precommit", "sonar",
            "lint", "check", "quality",
        ],
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


# =============================================================================
# Profile Classification Patterns (derived from CANONICAL_COMMANDS aliases)
# =============================================================================

def _build_profile_patterns() -> dict:
    """Build PROFILE_PATTERNS from CANONICAL_COMMANDS aliases."""
    patterns = {}
    for cmd, meta in CANONICAL_COMMANDS.items():
        for alias in meta.get("aliases", []):
            patterns[alias] = cmd
    return patterns


PROFILE_PATTERNS = _build_profile_patterns()


class ExtensionBase(ABC):
    """Abstract base class for domain bundle extensions.

    Subclasses must implement:
        - get_skill_domains: Domain metadata and skill profiles

    All other methods have sensible defaults.
    Build bundles should override discover_modules() for module discovery.
    """

    # =========================================================================
    # Required Methods (must be implemented)
    # =========================================================================

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
    # Module Discovery Methods (override for build bundles)
    # =========================================================================

    def discover_modules(self, project_root: str) -> list:
        """Discover all modules with complete metadata.

        This is the primary API for module discovery. Returns comprehensive
        module information including metadata, dependencies, packages, and stats.

        Args:
            project_root: Absolute path to project root.

        Returns:
            List of module dicts. See build-project-structure.md for complete
            contract including:
            - name, technology (string)
            - paths: {module, descriptor, sources, tests, readme}
            - metadata: snake_case fields (artifact_id, group_id, parent as string)
            - packages: object keyed by package name
            - dependencies: strings "groupId:artifactId:scope"
            - stats: {source_files, test_files}
            - commands: resolved canonical command strings

        Notes:
            - Override in build bundles to provide technology-specific discovery
            - Default implementation returns empty list
            - Delegate to scripts in scripts/ directory for implementation
        """
        return []

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
    # Configuration Callback (override to set project defaults)
    # =========================================================================

    def config_defaults(self, project_root: str) -> None:
        """Configure project-specific defaults in run-configuration.json.

        Called by marshall-steward during initialization, after extension loading
        but before workflow logic accesses configuration. This is the hook for
        extensions to set domain-specific defaults.

        Args:
            project_root: Absolute path to project root directory.

        Returns:
            None (void method)

        Contract:
            - MUST only write values if they don't already exist
            - MUST NOT override user-defined configuration
            - SHOULD use direct import from run_config module
            - MAY skip silently if no defaults are needed

        Example:
            def config_defaults(self, project_root: str) -> None:
                from run_config import ext_defaults_set_default
                # set_default returns True if set, False if key already existed
                ext_defaults_set_default("my_bundle.skip_profiles", ["itest", "native"], project_root)

        See standards/config-callback.md for complete documentation.
        """
        pass  # Default no-op implementation

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
