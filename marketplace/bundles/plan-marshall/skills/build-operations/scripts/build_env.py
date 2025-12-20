#!/usr/bin/env python3
"""
Build environment detection and command generation.

Usage:
    build-env.py detect --project-dir <dir> [--format <format>]
    build-env.py detect-modules --project-dir <dir>
    build-env.py detect-module-type --module <module> [--build-system <bs>]
    build-env.py detect-profiles --module <module> [--build-system <bs>]
    build-env.py persist --project-dir <dir> [--dry-run]
    build-env.py lookup --canonical <name> --module <module>
    build-env.py get-available-commands --module <module>
    build-env.py validate-required --module <module>
    build-env.py --help

Subcommands:
    detect               Detect available build systems in a project
    detect-modules       Detect project modules (Maven, Gradle, npm workspaces)
    detect-module-type   Detect module type (pom, jar, war, quarkus)
    detect-profiles      Detect Maven/Gradle profiles and classify them
    persist              Generate and persist module commands to marshal.json
    lookup               Look up canonical command for a module
    get-available-commands  List available canonical commands for a module
    validate-required    Validate required commands are configured
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Build system detection configuration
BUILD_SYSTEMS = {
    "maven": {
        "files": ["pom.xml"],
        "priority": 1,
        "technology": "java"
    },
    "gradle": {
        "files": ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"],
        "priority": 2,
        "technology": "java"
    },
    "npm": {
        "files": ["package.json"],
        "priority": 3,
        "technology": "javascript"
    }
}


# Standard command labels and their goal mappings per build system (LEGACY)
# Kept for backward compatibility - use CANONICAL_COMMANDS for new code
COMMAND_MAPPINGS = {
    "maven": {
        "test-compile": "test-compile",
        "test": "clean test",
        "verify": "clean verify",
        "install": "clean install",
        "pre-commit": "clean install",
        "coverage": "clean verify -Pcoverage"
    },
    "gradle": {
        "test-compile": "testClasses",
        "test": "clean test",
        "verify": "clean build",
        "install": "clean build publishToMavenLocal",
        "pre-commit": "clean build",
        "coverage": "clean test jacocoTestReport"
    },
    "npm": {
        "test": "run test",
        "build": "run build",
        "lint": "run lint",
        "verify": "run test && npm run lint",
        "pre-commit": "run test"
    }
}


# =============================================================================
# Canonical Command Vocabulary
# =============================================================================

# Canonical command definitions with phase, description, required flag, applicable_to
CANONICAL_COMMANDS = {
    # Build phase
    "compile": {
        "phase": "build",
        "description": "Compile production sources only",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus"],
    },
    "test-compile": {
        "phase": "build",
        "description": "Compile production and test sources",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus"],
    },

    # Test phase
    "module-tests": {
        "phase": "test",
        "description": "Unit tests for the module (JUnit, Jest, pytest)",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    "integration-tests": {
        "phase": "test",
        "description": "Integration tests (containers, external services)",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    "coverage": {
        "phase": "test",
        "description": "Test execution with coverage measurement",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
    "performance": {
        "phase": "test",
        "description": "Performance/benchmark tests (JMH, k6, wrk)",
        "required": False,
        "applicable_to": ["jar", "quarkus", "npm"],
    },

    # Quality phase
    "quality-gate": {
        "phase": "quality",
        "description": "Static analysis, linting, formatting checks",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "pom", "npm"],
    },

    # Verify phase
    "verify": {
        "phase": "verify",
        "description": "Full verification (compile + test + quality)",
        "required": True,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },

    # Deploy phase
    "install": {
        "phase": "deploy",
        "description": "Install artifact to local repository",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "pom"],
    },
    "package": {
        "phase": "deploy",
        "description": "Create deployable artifact (jar, war, native)",
        "required": False,
        "applicable_to": ["jar", "war", "quarkus", "npm"],
    },
}


# Build system mappings: canonical name -> build-system-specific goals
BUILD_SYSTEM_MAPPINGS = {
    "maven": {
        "compile": "compile",
        "test-compile": "test-compile",
        "module-tests": "clean test",
        "integration-tests": "clean verify -Pintegration-tests",
        "coverage": "clean verify -Pcoverage",
        "performance": "clean verify -Pbenchmark",
        "quality-gate": "clean verify -Ppre-commit",
        "verify": "clean verify",
        "install": "clean install",
        "package": "package",
    },
    "gradle": {
        "compile": "compileJava",
        "test-compile": "testClasses",
        "module-tests": "clean test",
        "integration-tests": "clean integrationTest",
        "coverage": "clean test jacocoTestReport",
        "performance": "clean jmh",
        "quality-gate": "clean check",
        "verify": "clean build",
        "install": "clean publishToMavenLocal",
        "package": "clean assemble",
    },
    "npm": {
        "compile": None,
        "test-compile": None,
        "module-tests": "run test",
        "integration-tests": "run test:e2e",
        "coverage": "run test:coverage",
        "performance": "run test:perf",
        "quality-gate": "run lint && npm run format:check",
        "verify": "run test && npm run lint",
        "install": None,
        "package": "run build",
    },
}


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


# Profile modifiers that append suffixes to base canonical names
PROFILE_MODIFIERS = {
    "quick": {"suffix": "-quick", "description": "Fast execution mode"},
    "stress": {"suffix": "-stress", "description": "Stress testing mode"},
    "max": {"suffix": "-max", "description": "Maximum load mode"},
}


# Old label to canonical name migration mapping
OLD_TO_CANONICAL = {
    "test": "module-tests",
    "pre-commit": "quality-gate",
    "lint": "quality-gate",
}


def detect_build_systems(project_dir: Path) -> dict:
    """Detect all available build systems in the project directory."""
    detected = []

    for system, config in BUILD_SYSTEMS.items():
        for build_file in config["files"]:
            file_path = project_dir / build_file
            if file_path.exists():
                detected.append({
                    "name": system,
                    "priority": config["priority"],
                    "technology": config["technology"],
                    "detected_by": str(build_file)
                })
                break

    if not detected:
        return {
            "available_systems": "",
            "default_system": "",
            "detected": [],
            "message": "No build systems detected"
        }

    detected.sort(key=lambda x: x["priority"])
    available = ",".join(d["name"] for d in detected)
    default = detected[0]["name"]

    return {
        "available_systems": available,
        "default_system": default,
        "detected": detected,
        "message": f"Detected {len(detected)} build system(s)"
    }


def cmd_detect(args):
    """Handle detect subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({"status": "error", "message": f"Directory not found: {project_dir}"}, indent=2))
        return 1

    result = detect_build_systems(project_dir)
    result["status"] = "success"
    result["project_dir"] = str(project_dir)

    if args.format == "simple":
        print(f"available_systems={result['available_systems']}")
        print(f"default_system={result['default_system']}")
    else:
        print(json.dumps(result, indent=2))

    return 0


# =============================================================================
# Module Detection
# =============================================================================

def detect_maven_modules(project_dir: Path) -> list:
    """Detect Maven modules from pom.xml."""
    modules = []
    pom_path = project_dir / "pom.xml"

    if not pom_path.exists():
        return modules

    content = pom_path.read_text()

    # Extract <modules> section
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


def detect_gradle_modules(project_dir: Path) -> list:
    """Detect Gradle modules from settings.gradle or settings.gradle.kts."""
    modules = []

    for settings_file in ["settings.gradle.kts", "settings.gradle"]:
        settings_path = project_dir / settings_file
        if settings_path.exists():
            content = settings_path.read_text()

            # Match include("module") or include ':module' patterns
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


def detect_npm_workspaces(project_dir: Path) -> list:
    """Detect npm workspaces from package.json."""
    modules = []
    package_path = project_dir / "package.json"

    if not package_path.exists():
        return modules

    try:
        data = json.loads(package_path.read_text())
        workspaces = data.get("workspaces", [])

        if isinstance(workspaces, dict):
            workspaces = workspaces.get("packages", [])

        for workspace in workspaces:
            # Handle glob patterns like "packages/*"
            if "*" in workspace:
                base_path = project_dir / workspace.replace("/*", "").replace("/**", "")
                if base_path.exists() and base_path.is_dir():
                    for child in base_path.iterdir():
                        if child.is_dir() and (child / "package.json").exists():
                            modules.append({
                                "name": child.name,
                                "path": str(child.relative_to(project_dir)),
                                "build_system": "npm"
                            })
            else:
                workspace_path = project_dir / workspace
                if workspace_path.exists():
                    modules.append({
                        "name": Path(workspace).name,
                        "path": workspace,
                        "build_system": "npm"
                    })
    except (json.JSONDecodeError, KeyError):
        pass

    return modules


def detect_all_modules(project_dir: Path) -> list:
    """Detect all modules from all build systems."""
    modules = []
    modules.extend(detect_maven_modules(project_dir))
    modules.extend(detect_gradle_modules(project_dir))
    modules.extend(detect_npm_workspaces(project_dir))
    return modules


# =============================================================================
# Module Type Detection
# =============================================================================

def detect_module_type(pom_path: Path) -> str:
    """Detect module type from pom.xml packaging element.

    Args:
        pom_path: Path to pom.xml file

    Returns:
        Module type: "pom", "jar", "war", or "quarkus"
    """
    if not pom_path.exists():
        return "jar"  # Default

    content = pom_path.read_text()

    # Check <packaging> element
    packaging_match = re.search(r'<packaging>([^<]+)</packaging>', content)
    if packaging_match:
        packaging = packaging_match.group(1).strip().lower()
        if packaging == "pom":
            return "pom"
        if packaging == "war":
            return "war"

    # Check for Quarkus (quarkus-maven-plugin presence)
    if "quarkus-maven-plugin" in content:
        return "quarkus"

    return "jar"


def detect_gradle_module_type(build_file: Path) -> str:
    """Detect module type from build.gradle or build.gradle.kts.

    Args:
        build_file: Path to build.gradle or build.gradle.kts file

    Returns:
        Module type: "jar", "war", or "quarkus"
    """
    if not build_file.exists():
        return "jar"  # Default

    content = build_file.read_text()

    # Check for war plugin
    if "war" in content.lower() and ("plugin" in content.lower() or "plugins" in content.lower()):
        if re.search(r'[\'"]war[\'"]', content) or "id 'war'" in content or 'id("war")' in content:
            return "war"

    # Check for Quarkus plugin
    if "quarkus" in content.lower():
        return "quarkus"

    return "jar"


def detect_npm_module_type(package_path: Path) -> str:
    """Detect module type from package.json.

    Args:
        package_path: Path to package.json file

    Returns:
        Module type: always "npm" for npm projects
    """
    return "npm"


def detect_module_type_for_path(module_path: Path, build_system: str) -> str:
    """Detect module type for a given module path and build system.

    Args:
        module_path: Path to module directory
        build_system: Build system (maven, gradle, npm)

    Returns:
        Module type string
    """
    if build_system == "maven":
        pom_path = module_path / "pom.xml"
        return detect_module_type(pom_path)
    elif build_system == "gradle":
        for build_file in ["build.gradle.kts", "build.gradle"]:
            build_path = module_path / build_file
            if build_path.exists():
                return detect_gradle_module_type(build_path)
        return "jar"
    elif build_system == "npm":
        return detect_npm_module_type(module_path / "package.json")
    else:
        return "jar"


def cmd_detect_module_type(args):
    """Handle detect-module-type subcommand."""
    project_dir = Path(args.project_dir).resolve()
    module_path = project_dir

    if args.module and args.module != "default":
        module_path = project_dir / args.module

    if not module_path.exists():
        print(f"error: Module path not found: {module_path}", file=sys.stderr)
        return 1

    # Detect build system if not specified
    build_system = args.build_system
    if not build_system:
        # Auto-detect from available files
        if (module_path / "pom.xml").exists():
            build_system = "maven"
        elif (module_path / "build.gradle.kts").exists() or (module_path / "build.gradle").exists():
            build_system = "gradle"
        elif (module_path / "package.json").exists():
            build_system = "npm"
        else:
            print("error: Could not detect build system", file=sys.stderr)
            return 1

    module_type = detect_module_type_for_path(module_path, build_system)

    # Output in TOON format
    print("status: success")
    print(f"module: {args.module or 'default'}")
    print(f"build_system: {build_system}")
    print(f"type: {module_type}")

    return 0


def cmd_detect_modules(args):
    """Handle detect-modules subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({"status": "error", "message": f"Directory not found: {project_dir}"}, indent=2))
        return 1

    modules = detect_all_modules(project_dir)

    result = {
        "status": "success",
        "project_dir": str(project_dir),
        "modules": modules,
        "count": len(modules)
    }

    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Hybrid Module Detection
# =============================================================================

def detect_hybrid_build_systems(module_path: Path) -> list:
    """Detect all build systems present in a module directory.

    A hybrid module has multiple build systems (e.g., Maven + npm).

    Args:
        module_path: Path to module directory

    Returns:
        List of detected build systems (e.g., ["maven", "npm"])
    """
    systems = []

    # Check for Maven
    if (module_path / "pom.xml").exists():
        systems.append("maven")

    # Check for Gradle
    if (module_path / "build.gradle").exists() or (module_path / "build.gradle.kts").exists():
        systems.append("gradle")

    # Check for npm
    if (module_path / "package.json").exists():
        systems.append("npm")

    return systems


def is_hybrid_module(module_path: Path) -> bool:
    """Check if a module has multiple build systems.

    Args:
        module_path: Path to module directory

    Returns:
        True if module has more than one build system
    """
    return len(detect_hybrid_build_systems(module_path)) > 1


def generate_hybrid_commands(module_path: Path, module_name: str = None) -> dict:
    """Generate commands for a hybrid module with all its build systems.

    For hybrid modules, commands are nested by build system:
    {
        "module-tests": {
            "maven": "...",
            "npm": "..."
        }
    }

    Args:
        module_path: Path to module directory
        module_name: Module name (None or "default" for root module)

    Returns:
        Dict of canonical_name -> {build_system: command} for each build system
    """
    build_systems = detect_hybrid_build_systems(module_path)
    if len(build_systems) <= 1:
        return {}  # Not hybrid, use regular command generation

    commands = {}

    for build_system in build_systems:
        # Detect module type for this build system
        mod_type = detect_module_type_for_path(module_path, build_system)

        # Generate commands for this build system
        for canonical, spec in CANONICAL_COMMANDS.items():
            # Filter by applicable_to
            if mod_type not in spec["applicable_to"]:
                continue

            goals = BUILD_SYSTEM_MAPPINGS.get(build_system, {}).get(canonical)
            if goals is None:
                continue

            # Generate full command string
            if build_system == "npm":
                cmd = f'python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "{goals}"'
            else:
                cmd = f'python3 .plan/execute-script.py plan-marshall:build-operations:{build_system} execute --goals "{goals}"'

            # Add module flag for non-default modules
            if module_name and module_name != "default":
                cmd += f" --module {module_name}"

            # Initialize nested dict if needed
            if canonical not in commands:
                commands[canonical] = {}

            commands[canonical][build_system] = cmd

    return commands


# =============================================================================
# Command Generation and Persistence
# =============================================================================

def generate_command(build_system: str, label: str, module_name: str = None) -> str:
    """Generate a full executable command string.

    Args:
        build_system: maven, gradle, or npm
        label: Command label (test, verify, etc.)
        module_name: Module name (None or "default" for root module)

    Returns:
        Full command string for execution
    """
    if build_system not in COMMAND_MAPPINGS:
        return None

    if label not in COMMAND_MAPPINGS[build_system]:
        return None

    goals = COMMAND_MAPPINGS[build_system][label]

    if build_system == "npm":
        base = f'python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "{goals}"'
    else:
        base = f'python3 .plan/execute-script.py plan-marshall:build-operations:{build_system} execute --goals "{goals}"'

    # Add module flag for non-default modules
    if module_name and module_name != "default":
        base += f" --module {module_name}"

    # Add profile for pre-commit
    if label == "pre-commit":
        base += " --profile pre-commit"

    return base


def generate_module_commands(build_system: str, module_name: str = None) -> dict:
    """Generate all standard commands for a module.

    Args:
        build_system: maven, gradle, or npm
        module_name: Module name (None or "default" for root module)

    Returns:
        Dict of label -> command string
    """
    commands = {}

    if build_system not in COMMAND_MAPPINGS:
        return commands

    for label in COMMAND_MAPPINGS[build_system]:
        cmd = generate_command(build_system, label, module_name)
        if cmd:
            commands[label] = cmd

    return commands


def load_marshal_json(project_dir: Path) -> dict:
    """Load marshal.json from .plan directory."""
    marshal_path = project_dir / ".plan" / "marshal.json"
    if marshal_path.exists():
        return json.loads(marshal_path.read_text())
    return {}


def save_marshal_json(project_dir: Path, config: dict) -> None:
    """Save marshal.json to .plan directory."""
    marshal_path = project_dir / ".plan" / "marshal.json"
    marshal_path.parent.mkdir(parents=True, exist_ok=True)
    marshal_path.write_text(json.dumps(config, indent=2))


def generate_canonical_commands_for_type(build_system: str, module_type: str, module_name: str = None, minimal: bool = False) -> dict:
    """Generate canonical commands filtered by module type.

    Args:
        build_system: maven, gradle, or npm
        module_type: Module type (pom, jar, war, quarkus, npm)
        module_name: Module name (None or "default" for root module)
        minimal: If True, only generate required commands (module-tests, quality-gate, verify)

    Returns:
        Dict of canonical_name -> command string
    """
    commands = {}

    if build_system not in BUILD_SYSTEM_MAPPINGS:
        return commands

    for canonical, spec in CANONICAL_COMMANDS.items():
        # Filter by applicable_to
        if module_type not in spec["applicable_to"]:
            continue

        # In minimal mode, only generate required commands
        if minimal and not spec.get("required", False):
            continue

        goals = BUILD_SYSTEM_MAPPINGS[build_system].get(canonical)
        if goals is None:
            continue

        # Generate full command string
        if build_system == "npm":
            cmd = f'python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "{goals}"'
        else:
            cmd = f'python3 .plan/execute-script.py plan-marshall:build-operations:{build_system} execute --goals "{goals}"'

        # Add module flag for non-default modules
        if module_name and module_name != "default":
            cmd += f" --module {module_name}"

        commands[canonical] = cmd

    return commands


def generate_profile_command(build_system: str, canonical: str, profile_id: str, activation: dict, module_name: str = None) -> str:
    """Generate a command string for a profile-based canonical command.

    Args:
        build_system: maven or gradle
        canonical: Canonical command name (integration-tests, coverage, performance)
        profile_id: Profile ID to activate
        activation: Activation info from profile detection
        module_name: Module name (None or "default" for root module)

    Returns:
        Full command string for execution
    """
    if build_system == "maven":
        # Determine activation method
        if activation.get("type") == "property":
            prop_name = activation.get("property", "")
            prop_value = activation.get("value")
            if prop_value:
                goals = f"clean verify -D{prop_name}={prop_value}"
            else:
                goals = f"clean verify -D{prop_name}"
        else:
            # Default to -P activation
            goals = f"clean verify -P{profile_id}"

        cmd = f'python3 .plan/execute-script.py plan-marshall:build-operations:maven execute --goals "{goals}"'
    elif build_system == "gradle":
        # Gradle typically uses tasks
        cmd = f'python3 .plan/execute-script.py plan-marshall:build-operations:gradle execute --tasks "clean {profile_id}"'
    else:
        return None

    # Add module flag for non-default modules
    if module_name and module_name != "default":
        cmd += f" --module {module_name}"

    return cmd


def cmd_persist(args):
    """Handle persist subcommand - detect and persist module commands."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(json.dumps({"status": "error", "message": f"Directory not found: {project_dir}"}, indent=2))
        return 1

    # Parse include_profiles if provided (format: "module:profile-id,module:profile-id")
    include_profiles_set = set()
    if args.include_profiles:
        for pair in args.include_profiles.split(","):
            pair = pair.strip()
            if ":" in pair:
                include_profiles_set.add(pair)

    # In minimal mode, skip all profile-based commands unless explicitly included
    minimal = getattr(args, 'minimal', False)

    # Detect build systems
    build_result = detect_build_systems(project_dir)
    if not build_result["available_systems"]:
        print("status: error")
        print("message: No build systems detected")
        return 1

    available_systems = build_result["available_systems"].split(",")
    default_system = build_result["default_system"]

    # Detect modules
    modules = detect_all_modules(project_dir)

    # Load existing config
    config = load_marshal_json(project_dir)

    if "modules" not in config:
        config["modules"] = {}

    # Check if default module is hybrid
    default_is_hybrid = is_hybrid_module(project_dir)
    default_build_systems = detect_hybrid_build_systems(project_dir) if default_is_hybrid else [default_system]

    # Detect module type for default module
    default_type = detect_module_type_for_path(project_dir, default_system)

    # Detect profiles for default module
    default_profiles = detect_profiles_for_module(project_dir, default_system)

    # Ensure default module exists
    if "default" not in config["modules"]:
        config["modules"]["default"] = {
            "path": ".",
            "domains": [],
            "build_systems": default_build_systems
        }
    else:
        config["modules"]["default"]["build_systems"] = default_build_systems

    # Set module type for default
    config["modules"]["default"]["type"] = default_type

    # Store detected profiles
    if default_profiles:
        config["modules"]["default"]["detected_profiles"] = [
            {"id": p["id"], "canonical": p.get("canonical")} for p in default_profiles
        ]

    # Generate commands for default module
    if default_is_hybrid:
        # Hybrid module: generate nested commands for each build system
        default_commands = generate_hybrid_commands(project_dir, None)
    else:
        # Single build system: generate flat commands
        default_commands = generate_canonical_commands_for_type(default_system, default_type, minimal=minimal)

        # Add profile-based commands (may override type-based if profile has specific activation)
        for profile in default_profiles:
            if profile.get("canonical"):
                canonical = profile["canonical"]
                profile_id = profile["id"]

                # Check if profile should be included
                # In minimal mode: only include if explicitly listed in --include-profiles
                # In normal mode: include all detected profiles
                profile_key = f"default:{profile_id}"
                if minimal and profile_key not in include_profiles_set:
                    continue  # Skip this profile in minimal mode unless explicitly included

                # Check if we have an include_profiles filter and this profile is not in it
                if include_profiles_set and profile_key not in include_profiles_set:
                    continue  # Skip profiles not in the explicit include list

                activation = profile.get("activation", {})
                activation_type = activation.get("type", "command-line")

                # Profile-based commands with specific activation (property, jdk, os, default)
                # should REPLACE type-based commands because they're more accurate
                should_use_profile = (
                    canonical not in default_commands or
                    activation_type in ("property", "jdk", "os", "default")
                )

                if should_use_profile:
                    cmd = generate_profile_command(
                        default_system, canonical, profile_id,
                        activation, None
                    )
                    if cmd:
                        default_commands[canonical] = cmd

    config["modules"]["default"]["commands"] = default_commands

    # Generate commands for detected modules
    modules_updated = 1  # default
    commands_generated = len(default_commands)

    for module in modules:
        mod_name = module["name"]
        mod_system = module["build_system"]
        mod_path = project_dir / module["path"]

        # Check if this module is hybrid
        mod_is_hybrid = is_hybrid_module(mod_path)
        mod_build_systems = detect_hybrid_build_systems(mod_path) if mod_is_hybrid else [mod_system]

        # Detect module type
        mod_type = detect_module_type_for_path(mod_path, mod_system)

        # Detect profiles for this module
        mod_profiles = detect_profiles_for_module(mod_path, mod_system)

        if mod_name not in config["modules"]:
            config["modules"][mod_name] = {
                "path": module["path"],
                "domains": [],
                "build_systems": mod_build_systems
            }
        else:
            config["modules"][mod_name]["build_systems"] = mod_build_systems

        # Set module type
        config["modules"][mod_name]["type"] = mod_type

        # Store detected profiles
        if mod_profiles:
            config["modules"][mod_name]["detected_profiles"] = [
                {"id": p["id"], "canonical": p.get("canonical")} for p in mod_profiles
            ]

        # Generate commands
        if mod_is_hybrid:
            # Hybrid module: generate nested commands for each build system
            mod_commands = generate_hybrid_commands(mod_path, mod_name)
        else:
            # Single build system: generate flat commands
            mod_commands = generate_canonical_commands_for_type(mod_system, mod_type, mod_name, minimal=minimal)

            # Add profile-based commands (may override type-based if profile has specific activation)
            for profile in mod_profiles:
                if profile.get("canonical"):
                    canonical = profile["canonical"]
                    profile_id = profile["id"]

                    # Check if profile should be included
                    # In minimal mode: only include if explicitly listed in --include-profiles
                    # In normal mode: include all detected profiles (unless filtered)
                    profile_key = f"{mod_name}:{profile_id}"
                    if minimal and profile_key not in include_profiles_set:
                        continue  # Skip this profile in minimal mode unless explicitly included

                    # Check if we have an include_profiles filter and this profile is not in it
                    if include_profiles_set and profile_key not in include_profiles_set:
                        continue  # Skip profiles not in the explicit include list

                    activation = profile.get("activation", {})
                    activation_type = activation.get("type", "command-line")

                    # Profile-based commands with specific activation should REPLACE type-based
                    should_use_profile = (
                        canonical not in mod_commands or
                        activation_type in ("property", "jdk", "os", "default")
                    )

                    if should_use_profile:
                        cmd = generate_profile_command(
                            mod_system, canonical, profile["id"],
                            activation, mod_name
                        )
                        if cmd:
                            mod_commands[canonical] = cmd

        config["modules"][mod_name]["commands"] = mod_commands
        modules_updated += 1
        commands_generated += len(mod_commands)

    # Update build_systems section if not present
    if "build_systems" not in config or not config["build_systems"]:
        config["build_systems"] = [
            {"system": system, "skill": "plan-marshall:build-operations"}
            for system in available_systems
        ]

    # Save unless dry run
    if not args.dry_run:
        save_marshal_json(project_dir, config)

    # Output in TOON format
    print(f"status: success")
    print(f"build_systems: {build_result['available_systems']}")
    print(f"modules_updated: {modules_updated}")
    print(f"commands_generated: {commands_generated}")
    print()
    print(f"modules[{modules_updated}]" + "{name,path,type,commands_count}:")
    for mod_name, mod_config in config["modules"].items():
        cmd_count = len(mod_config.get("commands", {}))
        mod_type = mod_config.get("type", "jar")
        print(f"{mod_name}\t{mod_config.get('path', mod_name)}\t{mod_type}\t{cmd_count}")

    return 0


# =============================================================================
# Canonical Lookup API
# =============================================================================

def generate_canonical_command(build_system: str, canonical: str, module_name: str = None) -> str:
    """Generate a full executable command string for a canonical command name.

    Args:
        build_system: maven, gradle, or npm
        canonical: Canonical command name (module-tests, verify, etc.)
        module_name: Module name (None or "default" for root module)

    Returns:
        Full command string for execution, or None if not applicable
    """
    if build_system not in BUILD_SYSTEM_MAPPINGS:
        return None

    goals = BUILD_SYSTEM_MAPPINGS[build_system].get(canonical)
    if goals is None:
        return None

    if build_system == "npm":
        base = f'python3 .plan/execute-script.py plan-marshall:build-operations:npm execute --command "{goals}"'
    else:
        base = f'python3 .plan/execute-script.py plan-marshall:build-operations:{build_system} execute --goals "{goals}"'

    # Add module flag for non-default modules
    if module_name and module_name != "default":
        base += f" --module {module_name}"

    return base


def lookup_command(canonical: str, module: str, config: dict, build_system: str = None) -> str | dict | None:
    """Look up the executable command for a canonical name and module.

    Only returns commands that are explicitly configured in marshal.json.
    Does NOT fall back to generating commands from BUILD_SYSTEM_MAPPINGS.

    Args:
        canonical: One of the canonical command names (e.g., "module-tests")
        module: Module name (e.g., "oauth-sheriff-core") or "default" for root
        config: Loaded marshal.json configuration
        build_system: Optional build system filter (for hybrid modules)

    Returns:
        - Command string if single build system or filter specified
        - Dict of {build_system: command} for hybrid modules without filter
        - None if not available
    """
    modules = config.get("modules", {})
    module_config = modules.get(module)

    if not module_config:
        return None

    commands = module_config.get("commands", {})
    command_entry = commands.get(canonical)

    if command_entry is None:
        return None

    # Handle existing command entry
    if isinstance(command_entry, dict):
        # New format: {command, source} or {maven: {...}, npm: {...}}
        if "command" in command_entry:
            return command_entry["command"]

        # Hybrid format with per-build-system commands
        if build_system:
            bs_entry = command_entry.get(build_system)
            if bs_entry and isinstance(bs_entry, dict):
                return bs_entry.get("command")
            return bs_entry

        # Check if this is a hybrid command (has build system keys)
        build_systems = module_config.get("build_systems", [])
        if build_systems and any(bs in command_entry for bs in build_systems):
            # Return dict for hybrid without filter
            return command_entry

        return None

    # Simple string format
    return command_entry


def cmd_lookup(args):
    """Handle lookup subcommand - look up canonical command for a module."""
    project_dir = Path(args.project_dir).resolve()
    config = load_marshal_json(project_dir)

    if not config:
        print(f"error: marshal.json not found in {project_dir}/.plan/", file=sys.stderr)
        print("hint: Run '/marshall-steward' to initialize configuration", file=sys.stderr)
        return 1

    result = lookup_command(args.canonical, args.module, config, args.build_system)

    if result is None:
        print(f"error: Command '{args.canonical}' not found for module '{args.module}'", file=sys.stderr)

        # Show available commands
        module_config = config.get("modules", {}).get(args.module)
        if module_config:
            available = list(module_config.get("commands", {}).keys())
            if available:
                print(f"available: {', '.join(available)}", file=sys.stderr)
        else:
            available_modules = list(config.get("modules", {}).keys())
            print(f"available modules: {', '.join(available_modules)}", file=sys.stderr)

        print("hint: Run '/marshall-steward' to reconfigure", file=sys.stderr)
        return 1

    if isinstance(result, dict):
        # Hybrid module - output in TOON format
        print(f"status: ambiguous")
        print(f"message: Module '{args.module}' has multiple build systems. Specify --build-system.")
        print()
        print("commands{build_system,command}:")
        for bs, cmd in result.items():
            print(f"{bs}\t{cmd}")
        return 1

    # Output plain text for shell capture
    print(result)
    return 0


def get_available_commands(module: str, config: dict) -> list:
    """Get list of available canonical command names for a module.

    Args:
        module: Module name
        config: Loaded marshal.json configuration

    Returns:
        List of canonical names that have commands configured
    """
    modules = config.get("modules", {})
    module_config = modules.get(module)

    if not module_config:
        return []

    commands = module_config.get("commands", {})
    return list(commands.keys())


def cmd_get_available_commands(args):
    """Handle get-available-commands subcommand."""
    project_dir = Path(args.project_dir).resolve()
    config = load_marshal_json(project_dir)

    if not config:
        print(f"error: marshal.json not found in {project_dir}/.plan/", file=sys.stderr)
        print("hint: Run '/marshall-steward' to initialize configuration", file=sys.stderr)
        return 1

    module_config = config.get("modules", {}).get(args.module)
    if not module_config:
        print(f"error: Module '{args.module}' not found", file=sys.stderr)
        available_modules = list(config.get("modules", {}).keys())
        print(f"available modules: {', '.join(available_modules)}", file=sys.stderr)
        return 1

    available = get_available_commands(args.module, config)

    # Output in TOON format
    print("status: success")
    print(f"module: {args.module}")
    print(f"count: {len(available)}")
    print()
    print(f"commands[{len(available)}]" + "{name}:")
    for cmd in available:
        print(cmd)

    return 0


def validate_required_commands(module: str, config: dict) -> list:
    """Validate that required commands are configured for a module.

    Args:
        module: Module name
        config: Loaded marshal.json configuration

    Returns:
        List of missing required commands (empty if all present)

    Raises:
        ValueError: If module does not exist in configuration
    """
    modules = config.get("modules", {})
    module_config = modules.get(module)

    if not module_config:
        raise ValueError(f"Module '{module}' not found in configuration")

    # Get module type, default to "jar" if not specified
    module_type = module_config.get("type", "jar")
    commands = module_config.get("commands", {})

    missing = []
    for canonical, spec in CANONICAL_COMMANDS.items():
        if spec["required"] and module_type in spec["applicable_to"]:
            if canonical not in commands:
                missing.append(canonical)

    return missing


def cmd_validate_required(args):
    """Handle validate-required subcommand."""
    project_dir = Path(args.project_dir).resolve()
    config = load_marshal_json(project_dir)

    if not config:
        print(f"error: marshal.json not found in {project_dir}/.plan/", file=sys.stderr)
        print("hint: Run '/marshall-steward' to initialize configuration", file=sys.stderr)
        return 1

    module_config = config.get("modules", {}).get(args.module)
    if not module_config:
        print(f"error: Module '{args.module}' not found", file=sys.stderr)
        available_modules = list(config.get("modules", {}).keys())
        print(f"available modules: {', '.join(available_modules)}", file=sys.stderr)
        return 1

    try:
        missing = validate_required_commands(args.module, config)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    module_type = module_config.get("type", "jar")

    # Output in TOON format
    if missing:
        print("status: incomplete")
        print(f"module: {args.module}")
        print(f"module_type: {module_type}")
        print(f"missing_count: {len(missing)}")
        print()
        print(f"missing[{len(missing)}]" + "{name,description}:")
        for cmd in missing:
            desc = CANONICAL_COMMANDS.get(cmd, {}).get("description", "")
            print(f"{cmd}\t{desc}")
        return 1
    else:
        print("status: success")
        print(f"module: {args.module}")
        print(f"module_type: {module_type}")
        print("message: All required commands are configured")
        return 0


# =============================================================================
# Module Type Detection
# =============================================================================

def detect_module_type(pom_path: Path) -> str:
    """Detect module type from Maven pom.xml packaging element.

    Args:
        pom_path: Path to pom.xml file

    Returns:
        Module type: "pom", "jar", "war", or "quarkus"
    """
    if not pom_path.exists():
        return "jar"  # Default type

    content = pom_path.read_text()

    # Check packaging element
    packaging_match = re.search(r'<packaging>([^<]+)</packaging>', content)
    if packaging_match:
        packaging = packaging_match.group(1).strip().lower()
        if packaging == "pom":
            return "pom"
        if packaging == "war":
            return "war"

    # Detect Quarkus from quarkus-maven-plugin
    if "quarkus-maven-plugin" in content:
        return "quarkus"

    return "jar"


def detect_gradle_module_type(build_file: Path) -> str:
    """Detect module type from Gradle build file.

    Args:
        build_file: Path to build.gradle or build.gradle.kts

    Returns:
        Module type: "jar", "war", or "quarkus"
    """
    if not build_file.exists():
        return "jar"

    content = build_file.read_text()

    # Check for war plugin
    if "war" in content and ("apply plugin:" in content or "plugins {" in content):
        if "'war'" in content or '"war"' in content:
            return "war"

    # Check for Quarkus
    if "quarkus" in content.lower():
        return "quarkus"

    return "jar"


def detect_npm_module_type(package_json: Path) -> str:
    """Detect module type from npm package.json.

    Args:
        package_json: Path to package.json

    Returns:
        Module type: always "npm" for npm projects
    """
    # npm projects don't have module types in the same sense
    # Return a generic type
    return "npm"


def detect_module_type_for_path(module_path: Path, build_system: str = None) -> str:
    """Detect module type for a given path, optionally filtering by build system.

    Args:
        module_path: Path to the module directory
        build_system: Optional build system filter (maven, gradle, npm)

    Returns:
        Module type string
    """
    if build_system == "maven" or (build_system is None and (module_path / "pom.xml").exists()):
        return detect_module_type(module_path / "pom.xml")

    if build_system == "gradle" or (build_system is None and (module_path / "build.gradle").exists()):
        return detect_gradle_module_type(module_path / "build.gradle")

    if build_system == "gradle" or (build_system is None and (module_path / "build.gradle.kts").exists()):
        return detect_gradle_module_type(module_path / "build.gradle.kts")

    if build_system == "npm" or (build_system is None and (module_path / "package.json").exists()):
        return detect_npm_module_type(module_path / "package.json")

    return "jar"  # Default


def cmd_detect_module_type(args):
    """Handle detect-module-type subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"error: Directory not found: {project_dir}", file=sys.stderr)
        return 1

    # Determine module path
    if args.module and args.module != "default":
        module_path = project_dir / args.module
        if not module_path.exists():
            # Try to find it in marshal.json
            config = load_marshal_json(project_dir)
            module_config = config.get("modules", {}).get(args.module)
            if module_config:
                module_path = project_dir / module_config.get("path", args.module)
            else:
                print(f"error: Module path not found: {module_path}", file=sys.stderr)
                return 1
    else:
        module_path = project_dir

    # Detect type
    module_type = detect_module_type_for_path(module_path, args.build_system)

    # Output in TOON format
    print("status: success")
    print(f"module: {args.module or 'default'}")
    print(f"path: {module_path}")
    print(f"type: {module_type}")

    return 0


# =============================================================================
# Profile Detection
# =============================================================================

def detect_maven_profiles(pom_path: Path) -> list:
    """Detect Maven profiles from pom.xml.

    Args:
        pom_path: Path to pom.xml file

    Returns:
        List of dicts with profile info: {id, canonical, activation}
    """
    if not pom_path.exists():
        return []

    content = pom_path.read_text()
    profiles = []

    # Find all <profile><id>...</id> patterns
    profile_pattern = re.compile(r'<profile>\s*<id>([^<]+)</id>', re.MULTILINE)
    matches = profile_pattern.findall(content)

    for profile_id in matches:
        profile_id = profile_id.strip()
        canonical = classify_profile(profile_id)
        activation = detect_profile_activation(content, profile_id)

        profiles.append({
            "id": profile_id,
            "canonical": canonical,
            "activation": activation,
        })

    return profiles


def detect_gradle_profiles(settings_path: Path) -> list:
    """Detect Gradle profiles from settings.gradle.

    Note: Gradle doesn't have native profiles like Maven.
    Looks for custom profile-like patterns or tasks.

    Args:
        settings_path: Path to settings.gradle or settings.gradle.kts

    Returns:
        List of dicts with profile info
    """
    if not settings_path.exists():
        return []

    content = settings_path.read_text()
    profiles = []

    # Look for ext.profiles or similar patterns
    # This is a simple heuristic - Gradle profiles are typically custom
    profile_pattern = re.compile(r"['\"]([a-zA-Z]+-?test[s]?)['\"]|['\"]([a-zA-Z]*benchmark[s]?)['\"]", re.IGNORECASE)
    matches = profile_pattern.findall(content)

    for match in matches:
        profile_id = match[0] or match[1]
        if profile_id:
            canonical = classify_profile(profile_id)
            profiles.append({
                "id": profile_id,
                "canonical": canonical,
                "activation": {"type": "task"},
            })

    return profiles


def classify_profile(profile_id: str) -> str | None:
    """Classify a profile ID to its canonical name.

    Args:
        profile_id: Profile identifier

    Returns:
        Canonical name or None if no match
    """
    profile_lower = profile_id.lower()

    # Direct match
    if profile_id in PROFILE_TO_CANONICAL:
        return PROFILE_TO_CANONICAL[profile_id]

    # Case-insensitive match
    for pattern, canonical in PROFILE_TO_CANONICAL.items():
        if pattern.lower() == profile_lower:
            return canonical

    # Partial match (profile contains pattern)
    for pattern, canonical in PROFILE_TO_CANONICAL.items():
        if pattern.lower() in profile_lower:
            return canonical

    return None


def detect_profile_activation(pom_content: str, profile_id: str) -> dict:
    """Detect how a Maven profile is activated.

    Args:
        pom_content: Content of pom.xml
        profile_id: Profile ID to look for

    Returns:
        Dict with activation info: {type, property, value}
    """
    # Find the profile block
    profile_start = pom_content.find(f'<id>{profile_id}</id>')
    if profile_start == -1:
        return {"type": "command-line"}

    # Find the activation block within this profile
    # Look for <activation> after <id>profile_id</id> but before next </profile>
    profile_end = pom_content.find('</profile>', profile_start)
    if profile_end == -1:
        profile_end = len(pom_content)

    profile_block = pom_content[profile_start:profile_end]

    # Check for property activation (handle multiline with whitespace)
    prop_match = re.search(r'<activation>[\s\S]*?<property>[\s\S]*?<name>([^<]+)</name>', profile_block)
    if prop_match:
        prop_name = prop_match.group(1).strip()
        # Check for value within the same activation block
        value_match = re.search(r'<property>[\s\S]*?<value>([^<]+)</value>', profile_block)
        value = value_match.group(1).strip() if value_match else None
        return {
            "type": "property",
            "property": prop_name,
            "value": value,
        }

    # Check for activeByDefault
    if '<activeByDefault>true</activeByDefault>' in profile_block:
        return {"type": "default"}

    # Check for JDK activation
    jdk_match = re.search(r'<activation>\s*<jdk>([^<]+)</jdk>', profile_block)
    if jdk_match:
        return {"type": "jdk", "version": jdk_match.group(1).strip()}

    # Check for OS activation
    if '<os>' in profile_block:
        return {"type": "os"}

    # Default: command-line activation via -P
    return {"type": "command-line"}


def detect_profiles_for_module(module_path: Path, build_system: str = None) -> list:
    """Detect profiles for a module.

    Args:
        module_path: Path to the module directory
        build_system: Optional build system filter

    Returns:
        List of profile dicts
    """
    profiles = []

    if build_system == "maven" or (build_system is None and (module_path / "pom.xml").exists()):
        profiles.extend(detect_maven_profiles(module_path / "pom.xml"))

    if build_system == "gradle" or build_system is None:
        for settings_file in ["settings.gradle", "settings.gradle.kts"]:
            if (module_path / settings_file).exists():
                profiles.extend(detect_gradle_profiles(module_path / settings_file))
                break

    return profiles


def cmd_detect_profiles(args):
    """Handle detect-profiles subcommand."""
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"error: Directory not found: {project_dir}", file=sys.stderr)
        return 1

    # Determine module path
    if args.module and args.module != "default":
        module_path = project_dir / args.module
        if not module_path.exists():
            config = load_marshal_json(project_dir)
            module_config = config.get("modules", {}).get(args.module)
            if module_config:
                module_path = project_dir / module_config.get("path", args.module)
            else:
                print(f"error: Module path not found: {module_path}", file=sys.stderr)
                return 1
    else:
        module_path = project_dir

    # Detect profiles
    profiles = detect_profiles_for_module(module_path, args.build_system)

    # Output in TOON format
    print("status: success")
    print(f"module: {args.module or 'default'}")
    print(f"path: {module_path}")
    print(f"count: {len(profiles)}")
    print()
    print(f"profiles[{len(profiles)}]" + "{id,canonical,activation_type}:")
    for profile in profiles:
        canonical = profile.get("canonical") or "-"
        activation_type = profile.get("activation", {}).get("type", "command-line")
        print(f"{profile['id']}\t{canonical}\t{activation_type}")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build environment detection and command generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # detect subcommand
    detect_parser = subparsers.add_parser("detect", help="Detect available build systems in a project")
    detect_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory to scan")
    detect_parser.add_argument("--format", choices=["json", "simple"], default="json", help="Output format")
    detect_parser.set_defaults(func=cmd_detect)

    # detect-modules subcommand
    modules_parser = subparsers.add_parser("detect-modules", help="Detect project modules (Maven, Gradle, npm workspaces)")
    modules_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory to scan")
    modules_parser.set_defaults(func=cmd_detect_modules)

    # persist subcommand
    persist_parser = subparsers.add_parser("persist", help="Generate and persist module commands to marshal.json")
    persist_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    persist_parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Show what would be done without saving")
    persist_parser.add_argument("--minimal", dest="minimal", action="store_true",
                               help="Only generate required commands (module-tests, quality-gate, verify)")
    persist_parser.add_argument("--include-profiles", dest="include_profiles", default=None,
                               help="Comma-separated list of module:profile-id pairs to include (e.g., 'core:coverage,core:integration-tests')")
    persist_parser.set_defaults(func=cmd_persist)

    # lookup subcommand
    lookup_parser = subparsers.add_parser("lookup", help="Look up canonical command for a module")
    lookup_parser.add_argument("--canonical", required=True, help="Canonical command name (module-tests, verify, etc.)")
    lookup_parser.add_argument("--module", required=True, help="Module name (use 'default' for root module)")
    lookup_parser.add_argument("--build-system", dest="build_system", help="Build system filter (for hybrid modules)")
    lookup_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    lookup_parser.set_defaults(func=cmd_lookup)

    # get-available-commands subcommand
    available_parser = subparsers.add_parser("get-available-commands", help="List available canonical commands for a module")
    available_parser.add_argument("--module", required=True, help="Module name (use 'default' for root module)")
    available_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    available_parser.set_defaults(func=cmd_get_available_commands)

    # validate-required subcommand
    validate_parser = subparsers.add_parser("validate-required", help="Validate required commands are configured for a module")
    validate_parser.add_argument("--module", required=True, help="Module name (use 'default' for root module)")
    validate_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    validate_parser.set_defaults(func=cmd_validate_required)

    # detect-module-type subcommand
    type_parser = subparsers.add_parser("detect-module-type", help="Detect module type (pom, jar, war, quarkus)")
    type_parser.add_argument("--module", help="Module name (default: root module)")
    type_parser.add_argument("--build-system", dest="build_system", help="Build system (maven, gradle, npm)")
    type_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    type_parser.set_defaults(func=cmd_detect_module_type)

    # detect-profiles subcommand
    profiles_parser = subparsers.add_parser("detect-profiles", help="Detect Maven/Gradle profiles and classify them")
    profiles_parser.add_argument("--module", help="Module name (default: root module)")
    profiles_parser.add_argument("--build-system", dest="build_system", help="Build system (maven, gradle)")
    profiles_parser.add_argument("--project-dir", dest="project_dir", default=".", help="Project directory")
    profiles_parser.set_defaults(func=cmd_detect_profiles)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
