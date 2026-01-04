#!/usr/bin/env python3
"""Maven module discovery command.

Discovers Maven modules with complete metadata using Maven commands
and file system analysis. Implements the discover_modules() contract
from build-project-structure.md.

Usage:
    python3 maven_cmd_discover.py discover --root /path/to/project [--format json]

Output:
    JSON array of module objects conforming to build-project-structure.md contract.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Add extension-api scripts to path for base library imports
EXTENSION_API_DIR = Path(__file__).parent.parent.parent.parent.parent / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'
if str(EXTENSION_API_DIR) not in sys.path:
    sys.path.insert(0, str(EXTENSION_API_DIR))

from build_discover import discover_descriptors, build_module_base, find_readme


# =============================================================================
# Constants
# =============================================================================

README_PATTERNS = ["README.md", "README.adoc", "README.txt", "README"]


# =============================================================================
# Module Discovery
# =============================================================================

def discover_maven_modules(project_root: str) -> list:
    """Discover all Maven modules with complete metadata.

    Recursively discovers modules, handling multi-module projects by
    traversing into child modules instead of including parent POMs.

    Args:
        project_root: Absolute path to project root.

    Returns:
        List of module dicts conforming to build-project-structure.md contract.
    """
    root = Path(project_root).resolve()
    return _discover_recursive(root, root, "")


def _discover_recursive(project_dir: Path, project_root: Path, base_path: str) -> list:
    """Recursively discover Maven modules.

    Args:
        project_dir: Current directory to scan for pom.xml
        project_root: Root of the project (for relative path calculation)
        base_path: Path prefix for nested modules (e.g., "parent/child")

    Returns:
        List of discovered module data dicts
    """
    modules = []
    pom_path = project_dir / "pom.xml"

    if not pom_path.exists():
        return modules

    content = pom_path.read_text()

    # Check for child modules
    child_module_names = _extract_child_modules(content, project_dir)

    if child_module_names:
        # Multi-module: recurse into each child
        for module_name in child_module_names:
            module_path = project_dir / module_name
            relative_path = f"{base_path}/{module_name}" if base_path else module_name

            nested = _discover_recursive(module_path, project_root, relative_path)
            if nested:
                modules.extend(nested)
            else:
                # Leaf module
                module_data = _extract_module_data(module_path, project_root, relative_path)
                if module_data:
                    modules.append(module_data)
    else:
        # Single-module or leaf
        module_data = _extract_module_data(project_dir, project_root, base_path)
        if module_data:
            modules.append(module_data)

    return modules


def _extract_child_modules(pom_content: str, project_dir: Path) -> list:
    """Extract child module names from pom.xml."""
    modules_match = re.search(r'<modules>(.*?)</modules>', pom_content, re.DOTALL)
    if not modules_match:
        return []

    module_names = []
    for module_name in re.findall(r'<module>([^<]+)</module>', modules_match.group(1)):
        if (project_dir / module_name).exists():
            module_names.append(module_name)
    return module_names


# =============================================================================
# Module Data Extraction
# =============================================================================

def _extract_module_data(module_path: Path, project_root: Path, relative_path: str) -> dict | None:
    """Extract complete module data conforming to contract.

    Contract (build-project-structure.md):
    - technology: single string
    - paths: {module, descriptor, sources, tests, readme}
    - metadata: snake_case (artifact_id, group_id, packaging, description, parent, profiles)
    - packages: object keyed by package name
    - dependencies: strings "groupId:artifactId:scope"
    - stats: {source_files, test_files}
    - commands: resolved canonical command strings
    """
    pom_path = module_path / "pom.xml"
    if not pom_path.exists():
        return None

    content = pom_path.read_text()

    # Extract metadata
    artifact_id = _extract_xml_value(content, "artifactId")
    group_id = _extract_xml_value(content, "groupId")
    description = _extract_xml_value(content, "description")
    packaging = _extract_xml_value(content, "packaging") or "jar"

    # Parent as string "groupId:artifactId"
    parent_group = _extract_xml_value(content, "parent/groupId")
    parent_artifact = _extract_xml_value(content, "parent/artifactId")
    parent_str = f"{parent_group}:{parent_artifact}" if parent_group and parent_artifact else None

    # Profiles
    profiles = _extract_profiles(content)

    # Source directories
    sources = _discover_sources(module_path)
    source_paths = [f"{relative_path}/{s}" if relative_path else s for s in sources["main"]]
    test_paths = [f"{relative_path}/{t}" if relative_path else t for t in sources["test"]]

    # README
    readme = find_readme(str(module_path))
    readme_path = f"{relative_path}/{readme}" if readme and relative_path else readme

    # Packages
    packages = _discover_packages(module_path, sources, relative_path)

    # Dependencies
    dependencies = _extract_dependencies(content)

    # Stats
    source_files = _count_java_files(module_path, sources["main"])
    test_files = _count_java_files(module_path, sources["test"])

    # Commands
    module_name = artifact_id or module_path.name
    commands = _build_commands(module_name, profiles)

    return {
        "name": module_name,
        "technology": "maven",
        "paths": {
            "module": relative_path if relative_path else ".",
            "descriptor": f"{relative_path}/pom.xml" if relative_path else "pom.xml",
            "sources": source_paths,
            "tests": test_paths,
            "readme": readme_path
        },
        "metadata": {
            "artifact_id": artifact_id,
            "group_id": group_id,
            "packaging": packaging,
            "description": description,
            "parent": parent_str,
            "profiles": profiles if profiles else None
        },
        "packages": packages,
        "dependencies": dependencies,
        "stats": {
            "source_files": source_files,
            "test_files": test_files
        },
        "commands": commands
    }


# =============================================================================
# XML Extraction
# =============================================================================

def _extract_xml_value(content: str, tag: str) -> str | None:
    """Extract value from XML tag.

    For top-level tags, skips values inside <parent> blocks.
    For nested paths like 'parent/artifactId', extracts from within parent block.
    """
    if "/" in tag:
        parts = tag.split("/")
        parent_match = re.search(rf'<{parts[0]}>(.*?)</{parts[0]}>', content, re.DOTALL)
        if parent_match:
            match = re.search(rf'<{parts[1]}>([^<]+)</{parts[1]}>', parent_match.group(1))
            return match.group(1).strip() if match else None
        return None

    # For top-level tags, strip out <parent> block first
    if tag in ['artifactId', 'groupId', 'version', 'description', 'packaging']:
        content_no_parent = re.sub(r'<parent>.*?</parent>', '', content, flags=re.DOTALL)
        match = re.search(rf'<{tag}>([^<]+)</{tag}>', content_no_parent)
    else:
        match = re.search(rf'<{tag}>([^<]+)</{tag}>', content)

    return match.group(1).strip() if match else None


# =============================================================================
# Profile Extraction
# =============================================================================

# Profile ID patterns mapped to canonical names
PROFILE_PATTERNS = {
    "quality-gate": ["pre-commit", "quality", "sonar"],
    "integration-tests": ["integration", "it", "e2e"],
    "coverage": ["coverage", "jacoco", "cobertura"],
}


def _extract_profiles(pom_content: str) -> list:
    """Extract Maven profiles with canonical classification."""
    profiles = []

    for match in re.finditer(r'<profile>\s*<id>([^<]+)</id>', pom_content):
        profile_id = match.group(1).strip()
        canonical = _classify_profile(profile_id)
        activation = _detect_activation(pom_content, profile_id)

        profiles.append({
            "id": profile_id,
            "canonical": canonical,
            "activation": activation
        })

    return profiles


def _classify_profile(profile_id: str) -> str | None:
    """Map profile ID to canonical name."""
    profile_lower = profile_id.lower()
    for canonical, patterns in PROFILE_PATTERNS.items():
        for pattern in patterns:
            if pattern in profile_lower:
                return canonical
    return None


def _detect_activation(pom_content: str, profile_id: str) -> dict:
    """Detect how a Maven profile is activated."""
    profile_start = pom_content.find(f'<id>{profile_id}</id>')
    if profile_start == -1:
        return {"type": "command-line"}

    profile_end = pom_content.find('</profile>', profile_start)
    block = pom_content[profile_start:profile_end] if profile_end > profile_start else ""

    # Property activation
    prop_match = re.search(r'<activation>[\s\S]*?<property>[\s\S]*?<name>([^<]+)</name>', block)
    if prop_match:
        value_match = re.search(r'<property>[\s\S]*?<value>([^<]+)</value>', block)
        return {
            "type": "property",
            "property": prop_match.group(1).strip(),
            "value": value_match.group(1).strip() if value_match else None
        }

    if '<activeByDefault>true</activeByDefault>' in block:
        return {"type": "default"}

    return {"type": "command-line"}


# =============================================================================
# Source Discovery
# =============================================================================

def _discover_sources(module_path: Path) -> dict:
    """Discover source directories."""
    sources = {"main": [], "test": []}

    if (module_path / "src" / "main" / "java").exists():
        sources["main"].append("src/main/java")
    if (module_path / "src" / "test" / "java").exists():
        sources["test"].append("src/test/java")

    return sources


def _discover_packages(module_path: Path, sources: dict, relative_path: str) -> dict:
    """Discover Java packages as dict keyed by package name."""
    packages = {}

    for source_dir in sources.get("main", []):
        source_path = module_path / source_dir
        if not source_path.exists():
            continue

        seen = set()
        for java_file in source_path.rglob("*.java"):
            pkg_dir = java_file.parent
            pkg_name = str(pkg_dir.relative_to(source_path)).replace("/", ".").replace("\\", ".")

            if pkg_name and pkg_name not in seen:
                seen.add(pkg_name)

                rel_path = str(pkg_dir.relative_to(module_path))
                if relative_path:
                    rel_path = f"{relative_path}/{rel_path}"

                pkg_info = {"path": rel_path}

                # Check for package-info.java
                info_file = pkg_dir / "package-info.java"
                if info_file.exists():
                    info_path = str(info_file.relative_to(module_path))
                    if relative_path:
                        info_path = f"{relative_path}/{info_path}"
                    pkg_info["package_info"] = info_path

                packages[pkg_name] = pkg_info

    return packages


def _count_java_files(module_path: Path, source_dirs: list) -> int:
    """Count Java files in source directories."""
    count = 0
    for src in source_dirs:
        src_path = module_path / src
        if src_path.exists():
            count += len(list(src_path.rglob("*.java")))
    return count


# =============================================================================
# Dependencies
# =============================================================================

def _extract_dependencies(pom_content: str) -> list:
    """Extract dependencies as strings 'groupId:artifactId:scope'."""
    dependencies = []

    # Find dependencies section (not dependencyManagement)
    deps_match = re.search(r'<dependencies>(.*?)</dependencies>', pom_content, re.DOTALL)
    if not deps_match:
        return dependencies

    deps_content = deps_match.group(1)

    # Skip dependencyManagement section
    if '<dependencyManagement>' in pom_content:
        mgmt_end = pom_content.find('</dependencyManagement>')
        if mgmt_end > 0:
            remaining = pom_content[mgmt_end:]
            deps_match = re.search(r'<dependencies>(.*?)</dependencies>', remaining, re.DOTALL)
            deps_content = deps_match.group(1) if deps_match else ""

    for dep_match in re.finditer(r'<dependency>(.*?)</dependency>', deps_content, re.DOTALL):
        dep = dep_match.group(1)
        group_id = _extract_xml_value(dep, "groupId")
        artifact_id = _extract_xml_value(dep, "artifactId")
        scope = _extract_xml_value(dep, "scope") or "compile"

        if group_id and artifact_id:
            dependencies.append(f"{group_id}:{artifact_id}:{scope}")

    return dependencies


# =============================================================================
# Commands
# =============================================================================

def _build_commands(module_name: str, profiles: list) -> dict:
    """Build commands object with resolved canonical command strings."""
    base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"
    commands = {}

    if module_name and module_name != ".":
        commands["module-tests"] = f'{base} --targets "clean test" --module {module_name}'
        commands["verify"] = f'{base} --targets "clean verify" --module {module_name}'
    else:
        commands["module-tests"] = f'{base} --targets "clean test"'
        commands["verify"] = f'{base} --targets "clean verify"'

    # Profile-based commands
    for profile in profiles or []:
        canonical = profile.get("canonical")
        profile_id = profile.get("id")
        activation = profile.get("activation", {})

        if canonical and profile_id:
            cmd = _generate_profile_command(profile_id, activation, module_name)
            if cmd:
                commands[canonical] = cmd

    return commands


def _generate_profile_command(profile_id: str, activation: dict, module_name: str) -> str:
    """Generate command for a profile."""
    base = "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run"

    if activation.get("type") == "property":
        prop_name = activation.get("property", "")
        prop_value = activation.get("value")
        if prop_value:
            targets = f"clean verify -D{prop_name}={prop_value}"
        else:
            targets = f"clean verify -D{prop_name}"
    else:
        targets = f"clean verify -P{profile_id}"

    cmd = f'{base} --targets "{targets}"'
    if module_name and module_name != ".":
        cmd += f" --module {module_name}"

    return cmd


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Maven module discovery")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # discover subcommand
    discover_parser = subparsers.add_parser("discover", help="Discover Maven modules")
    discover_parser.add_argument("--root", required=True, help="Project root directory")
    discover_parser.add_argument("--format", choices=["json"], default="json", help="Output format")

    args = parser.parse_args()

    if args.command == "discover":
        modules = discover_maven_modules(args.root)
        print(json.dumps(modules, indent=2))


if __name__ == "__main__":
    main()
