#!/usr/bin/env python3
"""
Manage project structure knowledge in .plan/project-structure.json.

Provides operations for reading, generating, and updating project structure
metadata including module responsibilities, placement rules, and conventions.

Also provides collect-raw-data command to gather comprehensive project data
for LLM analysis.

Storage: JSON (reliable, standard tooling)
Output: TOON (LLM-friendly format)
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add script directory for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
BUNDLES_DIR = script_dir.parent.parent.parent.parent  # .../bundles/
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'))
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'extension-api' / 'scripts'))

from toon_parser import serialize_toon
from extension import discover_project_modules

EXIT_SUCCESS = 0
EXIT_ERROR = 1

# File locations
PLAN_BASE_DIR = Path(os.environ.get('PLAN_BASE_DIR', '.plan'))
STRUCTURE_PATH = PLAN_BASE_DIR / 'project-structure.json'
MARSHAL_PATH = PLAN_BASE_DIR / 'marshal.json'


class StructureNotFoundError(Exception):
    """Raised when project-structure.json doesn't exist."""
    pass


class MarshalNotFoundError(Exception):
    """Raised when marshal.json doesn't exist."""
    pass


def output(data: dict) -> None:
    """Output TOON result to stdout (LLM-friendly format)."""
    print(serialize_toon(data))


def error_exit(message: str, **extra) -> int:
    """Output error and return error exit code."""
    output({"status": "error", "error": message, **extra})
    return EXIT_ERROR


def success_exit(data: dict) -> int:
    """Output success and return success exit code."""
    output({"status": "success", **data})
    return EXIT_SUCCESS


def ensure_list(value) -> list:
    """Ensure value is a list.

    Handles edge cases from raw-project-data.json parsing:
    - Empty dict {} -> empty list []
    - None -> empty list []
    - Single value -> list with that value
    """
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and len(value) == 0:
        return []
    if value is None:
        return []
    return [value]


def load_structure() -> dict:
    """Load project-structure.json."""
    if not STRUCTURE_PATH.exists():
        raise StructureNotFoundError(
            "project-structure.json not found. Run 'generate' command first"
        )
    return json.loads(STRUCTURE_PATH.read_text(encoding='utf-8'))


def save_structure(structure: dict) -> None:
    """Save project-structure.json."""
    STRUCTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STRUCTURE_PATH.write_text(json.dumps(structure, indent=2), encoding='utf-8')


def load_marshal() -> dict:
    """Load marshal.json."""
    if not MARSHAL_PATH.exists():
        raise MarshalNotFoundError(
            "marshal.json not found. Run command /marshall-steward first"
        )
    return json.loads(MARSHAL_PATH.read_text(encoding='utf-8'))


def infer_domains_from_build_systems(build_systems: list) -> list:
    """Infer skill domains from build systems.

    Mapping:
    - maven, gradle -> java
    - npm -> javascript
    """
    domains = []
    for bs in build_systems:
        if bs in ('maven', 'gradle') and 'java' not in domains:
            domains.append('java')
        elif bs == 'npm' and 'javascript' not in domains:
            domains.append('javascript')
    return domains


# ===========================================================================
# Module Discovery (No marshal.json dependency)
# ===========================================================================

def detect_build_systems(module_path: Path) -> list:
    """Detect all build systems in a module directory.

    Args:
        module_path: Path to module directory.

    Returns:
        List of build systems found (maven, gradle, npm).
    """
    build_systems = []

    if (module_path / 'pom.xml').exists():
        build_systems.append('maven')
    if (module_path / 'build.gradle').exists() or (module_path / 'build.gradle.kts').exists():
        build_systems.append('gradle')
    if (module_path / 'package.json').exists():
        build_systems.append('npm')

    return build_systems


def parse_maven_modules(pom_path: Path) -> list:
    """Parse <modules> section from pom.xml.

    Args:
        pom_path: Path to pom.xml file.

    Returns:
        List of module directory names.
    """
    if not pom_path.exists():
        return []

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

        # Try with namespace first
        modules_elem = root.find('m:modules', ns)
        if modules_elem is None:
            modules_elem = root.find('modules')

        if modules_elem is None:
            return []

        modules = []
        for module in modules_elem:
            # Try with namespace
            module_name = module.text
            if module_name:
                modules.append(module_name.strip())

        return modules

    except ET.ParseError:
        return []


def discover_modules_recursive(
    project_root: Path,
    current_path: Path,
    discovered: list = None
) -> list:
    """Recursively discover modules from filesystem.

    Parses pom.xml <modules> sections to find all Maven modules,
    including nested submodules. Also detects npm (package.json).

    Args:
        project_root: Absolute path to project root.
        current_path: Current directory being scanned.
        discovered: Accumulator list for discovered modules.

    Returns:
        List of module dicts with: name, path, build_systems, packaging.
    """
    if discovered is None:
        discovered = []

    pom_path = current_path / 'pom.xml'
    if not pom_path.exists():
        return discovered

    # Get submodules from pom.xml
    submodules = parse_maven_modules(pom_path)

    for submodule_name in submodules:
        submodule_path = current_path / submodule_name

        if not submodule_path.exists() or not submodule_path.is_dir():
            continue

        # Calculate relative path from project root
        try:
            rel_path = str(submodule_path.relative_to(project_root))
        except ValueError:
            rel_path = submodule_name

        # Detect build systems and packaging
        build_systems = detect_build_systems(submodule_path)
        submodule_pom = submodule_path / 'pom.xml'
        packaging = get_maven_packaging(submodule_pom) if submodule_pom.exists() else ''

        # Find README
        readme_path = None
        for readme_name in ['README.md', 'README.adoc', 'README.txt', 'readme.md']:
            if (submodule_path / readme_name).exists():
                readme_path = f"{rel_path}/{readme_name}" if rel_path != "." else readme_name
                break

        # Count source and test files
        source_files = 0
        test_files = 0
        main_java = submodule_path / 'src' / 'main' / 'java'
        test_java = submodule_path / 'src' / 'test' / 'java'
        if main_java.exists():
            source_files = len(list(main_java.rglob('*.java')))
        if test_java.exists():
            test_files = len(list(test_java.rglob('*.java')))

        # Discover packages
        packages = {}
        if main_java.exists():
            for java_file in main_java.rglob('*.java'):
                pkg_path = java_file.parent.relative_to(main_java)
                pkg_name = str(pkg_path).replace('/', '.').replace('\\', '.')
                if pkg_name and pkg_name != '.':
                    if pkg_name not in packages:
                        packages[pkg_name] = {'path': str(pkg_path)}

        # Add module
        module_entry = {
            'name': submodule_name,
            'path': rel_path,
            'build_systems': build_systems,
            'packaging': packaging,
            'source_files': source_files,
            'test_files': test_files,
        }
        if readme_path:
            module_entry['readme'] = readme_path
        if packages:
            module_entry['packages'] = packages

        discovered.append(module_entry)

        # Recurse into nested modules
        discover_modules_recursive(
            project_root,
            submodule_path,
            discovered=discovered
        )

    return discovered


def discover_modules_from_filesystem(project_root: str = '.') -> list:
    """Discover all modules from filesystem without marshal.json dependency.

    DEPRECATED: Use discover_modules_from_extensions() instead.
    This function is kept for backward compatibility.

    This is the primary entry point for module discovery. It scans the project
    filesystem to find all modules, supporting:
    - Recursive Maven module detection (pom.xml <modules> parsing)
    - npm detection (package.json presence)
    - Hybrid modules (both Maven and npm)
    - Nested submodules with parent relationships

    Args:
        project_root: Path to project root directory.

    Returns:
        List of module dicts with structure:
        [
            {
                "name": "module-name",
                "path": "relative/path/to/module",
                "parent": "parent-module-name" or null,
                "build_systems": ["maven", "npm"],
                "packaging": "jar" or "pom" or "war" etc.
            }
        ]
    """
    root_path = Path(project_root).resolve()

    # Check for Maven project
    if (root_path / 'pom.xml').exists():
        return discover_modules_recursive(root_path, root_path)

    # Check for Gradle project
    if (root_path / 'build.gradle').exists() or (root_path / 'build.gradle.kts').exists():
        # For now, return empty list - Gradle multi-module support can be added later
        # Gradle modules would require parsing settings.gradle
        return []

    # Check for npm project (single module)
    if (root_path / 'package.json').exists():
        return [{
            'name': root_path.name,
            'path': '.',
            'build_systems': ['npm'],
            'packaging': 'npm'
        }]

    return []


# ===========================================================================
# Extension-based Module Discovery (New API)
# ===========================================================================

def discover_modules_from_extensions(project_root: str = '.') -> list:
    """Discover all modules using extension discover_project_modules() API.

    This is the preferred entry point for module discovery. It delegates to
    the extension-api which handles:
    - Extension discovery (which bundles apply to this project)
    - Module discovery per extension (via discover_modules())
    - Hybrid module merging (same path from multiple extensions)
    - Command merging (nest by build system for conflicts)

    Features:
    - Complete metadata extraction (name, path, build_systems, descriptors)
    - Package discovery with descriptions from package-info.java
    - Dependency extraction (Maven pom.xml, npm package.json, Gradle build.gradle)
    - Source/test file statistics
    - Automatic hybrid module merging (e.g., Maven + npm in same directory)

    Args:
        project_root: Path to project root directory.

    Returns:
        List of module dicts with comprehensive structure from extensions.
        See extension_base.py discover_modules() for full schema.
    """
    root_path = Path(project_root).resolve()

    # Use discover_project_modules() which handles extension discovery,
    # module discovery, and hybrid module merging
    result = discover_project_modules(root_path)

    modules_dict = result.get('modules', {})

    # If no modules discovered from extensions, fall back to filesystem discovery
    if not modules_dict:
        return discover_modules_from_filesystem(str(root_path))

    return list(modules_dict.values())




def load_raw_data() -> dict:
    """Load raw-project-data.json if it exists.

    Returns:
        Parsed raw data dict, or empty dict if not found.
    """
    raw_path = PLAN_BASE_DIR / 'raw-project-data.json'
    if not raw_path.exists():
        return {}
    try:
        content = raw_path.read_text(encoding='utf-8')
        return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return {}


def select_key_packages(packages: dict | list, max_packages: int = 4) -> dict:
    """Select architecturally significant packages from raw data.

    Prioritizes packages that are likely important (domain, core, api)
    and excludes utility packages (util, helper, internal).

    Args:
        packages: One of:
                  - dict of package name -> {path, package_info} (old format)
                  - list of package dicts with 'name', 'path', 'description' (extension format)
                  - list of package names (legacy format)
        max_packages: Maximum packages to return.

    Returns:
        Dict of package name -> {path, package_info, description}.
        - path: project-relative path to package directory
        - package_info: project-relative path to package-info.java (only if exists in raw data)
        - description: empty string (to be enriched by LLM)
    """
    if not packages:
        return {}

    # Handle different input formats
    if isinstance(packages, list):
        if packages and isinstance(packages[0], dict):
            # Extension format: list of dicts with 'name', 'path', etc.
            package_names = [p.get('name', '') for p in packages if p.get('name')]
            package_data = {
                p.get('name'): {
                    'path': p.get('path', ''),
                    'description': p.get('description', ''),
                    'package_info': p.get('package_info', '')
                }
                for p in packages if p.get('name')
            }
        else:
            # Legacy list format - list of package name strings
            package_names = packages
            package_data = {name: {'path': ''} for name in packages}
    else:
        # Dict format: {package_name: {path, package_info}}
        package_names = list(packages.keys())
        package_data = packages

    # Skip patterns (internal implementation details)
    skip_patterns = ['util', 'helper', 'internal', 'impl', 'support']

    # Priority patterns (architecturally significant)
    priority_patterns = ['domain', 'core', 'api', 'service', 'pipeline', 'model']

    # Filter out utility packages
    filtered = [p for p in package_names
                if not any(skip in p.lower().split('.')[-1] for skip in skip_patterns)]

    # If all filtered out, use original
    if not filtered:
        filtered = package_names

    # Sort by priority (priority patterns first, then by length - shorter = higher level)
    def sort_key(pkg):
        parts = pkg.lower().split('.')
        last_part = parts[-1] if parts else ''
        # Priority if matches important pattern
        priority = 0 if any(p in last_part for p in priority_patterns) else 1
        # Shorter packages are usually higher-level
        return (priority, len(parts), pkg)

    sorted_packages = sorted(filtered, key=sort_key)
    selected = sorted_packages[:max_packages]

    # Build result from raw data (paths already computed)
    result = {}
    for pkg_name in selected:
        raw_entry = package_data.get(pkg_name, {})

        # Build package entry with description field for LLM enrichment
        pkg_entry = {
            'path': raw_entry.get('path', ''),
            'description': ''
        }

        # Preserve package_info if present in raw data
        if 'package_info' in raw_entry:
            pkg_entry['package_info'] = raw_entry['package_info']

        result[pkg_name] = pkg_entry

    return result


def extract_module_dependencies(dependencies: list, all_module_names: set) -> list:
    """Extract inter-module dependencies from dependency list.

    Looks for dependencies that reference other modules in this project.

    Args:
        dependencies: List of dependencies, either:
                     - dicts with 'groupId', 'artifactId', 'scope' (extension format)
                     - strings in format "groupId:artifactId:scope" (legacy format)
        all_module_names: Set of all module names in the project

    Returns:
        List of unique module names this module depends on.
    """
    module_deps = set()  # Use set for deduplication
    for dep in dependencies:
        # Extract artifactId based on format
        if isinstance(dep, dict):
            # Extension format: dict with groupId, artifactId, scope
            artifact_id = dep.get('artifactId', '').lower()
        else:
            # Legacy format: "groupId:artifactId:scope" string
            dep_str = str(dep).lower()
            parts = dep_str.split(':')
            artifact_id = parts[1] if len(parts) >= 2 else ''

        if artifact_id:
            # Check if this artifact matches any module name
            for module_name in all_module_names:
                if module_name.lower() == artifact_id:
                    module_deps.add(module_name)
                    break
    return sorted(module_deps)  # Return sorted list for consistent output


def extract_project_name(project_root: str) -> str:
    """Extract project name from project root path."""
    if not project_root:
        return ''
    return Path(project_root).name


def extract_project_description(project_root: str, readme_filename: str = '') -> str:
    """Extract project description from README file.

    Looks for common description patterns in README files:
    - AsciiDoc: '== What is it?' section or first paragraph after title
    - Markdown: '## Description' section or first paragraph after title
    - Falls back to first substantive paragraph

    Args:
        project_root: Path to project root directory
        readme_filename: Optional specific README filename

    Returns:
        Extracted description (1-2 sentences) or empty string if not found
    """
    if not project_root:
        return ''

    root_path = Path(project_root)

    # Find README file
    readme_path = None
    if readme_filename:
        readme_path = root_path / readme_filename
        if not readme_path.exists():
            readme_path = None

    if not readme_path:
        # Try common README names
        for name in ['README.adoc', 'README.md', 'README.txt', 'README', 'readme.md']:
            candidate = root_path / name
            if candidate.exists():
                readme_path = candidate
                break

    if not readme_path or not readme_path.exists():
        return ''

    try:
        content = readme_path.read_text(encoding='utf-8')
    except (IOError, UnicodeDecodeError):
        return ''

    # Determine format
    is_asciidoc = readme_path.suffix.lower() == '.adoc'

    description = ''

    if is_asciidoc:
        # Look for "What is it?" section (common pattern)
        what_is_match = re.search(
            r'==\s*What is it\?\s*\n+(.+?)(?=\n==|\n\[|\ntoc::|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if what_is_match:
            description = what_is_match.group(1).strip()
        else:
            # Look for first paragraph after title and badges
            # Skip lines starting with image:, link:, :attr:, [, =
            lines = content.split('\n')
            in_content = False
            para_lines = []
            for line in lines:
                stripped = line.strip()
                # Skip empty, attributes, images, badges, title markers
                if not stripped:
                    if para_lines:
                        break  # End of paragraph
                    continue
                if stripped.startswith(('image:', 'link:', ':', '[', '=')):
                    continue
                if stripped.startswith('toc::'):
                    continue
                # Found content line
                para_lines.append(stripped)
                if len(para_lines) >= 3:  # Enough for description
                    break
            if para_lines:
                description = ' '.join(para_lines)
    else:
        # Markdown: look for ## Description or first paragraph
        desc_match = re.search(
            r'##\s*Description\s*\n+(.+?)(?=\n##|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            # First paragraph after title (skip badges)
            lines = content.split('\n')
            para_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if para_lines:
                        break
                    continue
                # Skip title, badges, links
                if stripped.startswith(('#', '!', '[', '<')):
                    continue
                para_lines.append(stripped)
                if len(para_lines) >= 3:
                    break
            if para_lines:
                description = ' '.join(para_lines)

    # Clean up description
    if description:
        # Remove AsciiDoc/Markdown formatting
        description = re.sub(r'\*\*([^*]+)\*\*', r'\1', description)  # **bold**
        description = re.sub(r'\*([^*]+)\*', r'\1', description)      # *italic*
        description = re.sub(r'`([^`]+)`', r'\1', description)        # `code`
        description = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', description)  # [text](url)
        description = re.sub(r'https?://\S+', '', description)        # URLs
        description = re.sub(r'\s+', ' ', description).strip()        # Normalize whitespace

        # Limit to ~2 sentences (first ~250 chars ending at sentence boundary)
        if len(description) > 250:
            # Find sentence end
            end_match = re.search(r'^.{100,250}[.!?]', description)
            if end_match:
                description = end_match.group(0)
            else:
                description = description[:250].rsplit(' ', 1)[0] + '...'

    return description


class RawDataNotFoundError(Exception):
    """Raised when raw-project-data.json doesn't exist or is empty."""
    pass


def generate_structure_from_marshal() -> dict:
    """Generate project-structure.json from raw-project-data.json.

    Uses raw-project-data.json as the source of truth for module facts:
    - Module names, paths, build systems, packaging
    - Key packages
    - Framework detection from dependencies
    - External dependencies per module (for LLM context)
    - Inter-module dependencies (computed and stored at top level)

    Uses marshal.json['module_config'] only for command configuration (not module facts).

    Only outputs fields that have actual values (no empty arrays, no 'none' values).

    Raises:
        RawDataNotFoundError: If raw-project-data.json doesn't exist or has no modules.
    """
    # Load raw data as primary source for module facts
    raw_data = load_raw_data()
    modules_list = raw_data.get('modules', [])  # List of module dicts (unified structure)

    # Check if we have module data to work with
    if not modules_list:
        raise RawDataNotFoundError(
            "No module data found. Run 'collect-raw-data' command first to discover modules"
        )

    # Convert modules list to dict keyed by name (each module contains all its data)
    modules_by_name = {}
    for module in modules_list:
        name = module.get('name', '')
        if name:
            modules_by_name[name] = module

    # Get all module names for dependency extraction
    all_module_names = set(m for m in modules_by_name.keys() if m != 'default')

    # Build project-level section from raw data
    # Project info is nested under 'project' key in raw-project-data.json
    project_info = raw_data.get('project', {})
    project_root = project_info.get('root', '')
    project_name = project_info.get('name', '')
    if not project_name:
        # Fallback: extract from root path
        project_name = extract_project_name(project_root)

    # Extract description from README
    doc_info = raw_data.get('documentation', {})
    readme_file = doc_info.get('project_readme', '')
    project_description = extract_project_description(project_root, readme_file)

    project_section = {
        'name': project_name,
        'description': project_description
    }

    # Add documentation info if available
    doc_info = raw_data.get('documentation', {})
    if doc_info:
        docs = {}
        if doc_info.get('project_readme'):
            docs['readme'] = doc_info['project_readme']
        doc_files = ensure_list(doc_info.get('doc_files', []))
        if doc_files:
            docs['doc_files'] = doc_files
        if docs:
            project_section['documentation'] = docs

    structure = {
        'project': project_section,
        'modules': {},
        'dependencies': {}
    }

    for module_name, module in modules_by_name.items():
        if module_name == 'default':
            continue  # Skip default module template

        # Extract data from unified module dict
        packages = module.get('packages', {})  # dict (new) or list (legacy)
        dependencies = ensure_list(module.get('dependencies', []))

        # Select key packages (uses pre-computed paths from raw data)
        key_packages = select_key_packages(packages)

        # Extract descriptions from package-info.java for each key package
        # Falls back to class-level JavaDoc if no package-info.java exists
        for pkg_name, pkg_info in key_packages.items():
            if not pkg_info.get('description'):
                description = ''
                package_info_path = pkg_info.get('package_info', '')

                # Try package-info.java first
                if package_info_path:
                    abs_path = Path(project_root) / package_info_path if project_root else package_info_path
                    description = extract_javadoc_description(str(abs_path))

                # Fallback: extract from main class JavaDoc if no package-info.java
                if not description:
                    package_path = pkg_info.get('path', '')
                    if package_path:
                        abs_pkg_path = Path(project_root) / package_path if project_root else package_path
                        description = extract_class_javadoc_fallback(str(abs_pkg_path))

                if description:
                    pkg_info['description'] = description

        # Extract inter-module dependencies
        module_deps = extract_module_dependencies(dependencies, all_module_names)
        if module_deps:
            structure['dependencies'][module_name] = module_deps

        # Build module entry with only non-empty fields
        module_entry = {}

        # Extract responsibility from README if available
        readme = module.get('readme', '')
        if readme:
            # Resolve relative path against project root
            abs_readme = Path(project_root) / readme if project_root else readme
            responsibility = extract_readme_first_paragraph(str(abs_readme))
            if responsibility:
                module_entry['responsibility'] = responsibility
            module_entry['readme'] = readme

        # Only add key_packages if non-empty
        if key_packages:
            module_entry['key_packages'] = key_packages

        # Add external dependencies for LLM context
        if dependencies:
            module_entry['dependencies'] = dependencies

        # Add hybrid module fields if present (from raw data)
        package_json = module.get('package_json', '')
        if package_json:
            module_entry['package_json'] = package_json

        ui_path = module.get('ui_path', '')
        if ui_path:
            module_entry['ui_path'] = ui_path

        structure['modules'][module_name] = module_entry

    # Add documentation module if doc/ directory exists
    doc_data = collect_doc_module_data()
    if doc_data:
        doc_module = {
            'path': doc_data['path']
        }
        if doc_data.get('content_types'):
            doc_module['content_types'] = doc_data['content_types']
        if doc_data.get('sections'):
            doc_module['sections'] = doc_data['sections']
        if doc_data.get('top_files'):
            doc_module['key_files'] = doc_data['top_files']
        structure['modules']['doc'] = doc_module

    return structure


# ===========================================================================
# Data Collection Functions (for collect-raw-data command)
# ===========================================================================

def extract_javadoc_description(package_info_path: str) -> str:
    """Extract first sentence/paragraph from package-info.java JavaDoc.

    Args:
        package_info_path: Project-relative path to package-info.java.

    Returns:
        Extracted description or empty string if not found.
    """
    path = Path(package_info_path)
    if not path.exists():
        return ''

    try:
        content = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return ''

    # Find JavaDoc comment /** ... */
    match = re.search(r'/\*\*(.*?)\*/', content, re.DOTALL)
    if not match:
        return ''

    javadoc = match.group(1)

    # Clean up JavaDoc: remove leading asterisks and whitespace
    lines = []
    for line in javadoc.split('\n'):
        # Remove leading whitespace, asterisk, and more whitespace
        cleaned = re.sub(r'^\s*\*?\s?', '', line)
        # Skip @tags
        if cleaned.startswith('@'):
            break
        if cleaned:
            lines.append(cleaned)

    if not lines:
        return ''

    # Join lines and get first sentence (up to first period followed by space or end)
    text = ' '.join(lines)
    # Get first 1-2 sentences (up to ~200 chars)
    match = re.match(r'^(.{1,200}?[.!?])(?:\s|$)', text)
    if match:
        return match.group(1).strip()

    # If no sentence boundary found, return first ~150 chars
    return text[:150].strip() + ('...' if len(text) > 150 else '')


def extract_class_javadoc_fallback(package_path: str) -> str:
    """Extract description from main class JavaDoc as fallback when no package-info.java.

    Finds the first Java class in the package directory and extracts its class-level
    JavaDoc comment. This provides a fallback for packages without package-info.java.

    Args:
        package_path: Project-relative path to package directory.

    Returns:
        Extracted description or empty string if not found.
    """
    pkg_dir = Path(package_path)
    if not pkg_dir.exists() or not pkg_dir.is_dir():
        return ''

    # Find Java files in the package (not recursively)
    java_files = list(pkg_dir.glob('*.java'))
    if not java_files:
        return ''

    # Sort to get consistent results, prefer files that look like main classes
    # (interfaces, main classes typically come first alphabetically or by convention)
    java_files.sort(key=lambda f: (
        # Deprioritize test files and impl classes
        'Test' in f.stem,
        'Impl' in f.stem,
        f.stem.lower()
    ))

    # Try each file until we find a class-level JavaDoc
    for java_file in java_files[:5]:  # Limit to first 5 files
        try:
            content = java_file.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue

        # Find JavaDoc comment before class/interface/enum declaration
        # Pattern: /** ... */ followed by optional annotations, then class/interface/enum
        match = re.search(
            r'/\*\*(.*?)\*/\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(?:class|interface|enum)\s+\w+',
            content,
            re.DOTALL
        )
        if not match:
            continue

        javadoc = match.group(1)

        # Clean up JavaDoc: remove leading asterisks and whitespace
        lines = []
        for line in javadoc.split('\n'):
            cleaned = re.sub(r'^\s*\*?\s?', '', line)
            # Skip @tags
            if cleaned.startswith('@'):
                break
            if cleaned:
                lines.append(cleaned)

        if not lines:
            continue

        # Join and get first sentence
        text = ' '.join(lines)
        sentence_match = re.match(r'^(.{1,200}?[.!?])(?:\s|$)', text)
        if sentence_match:
            return sentence_match.group(1).strip()

        # Return truncated if no sentence boundary
        if len(text) > 20:  # Only return if meaningful
            return text[:150].strip() + ('...' if len(text) > 150 else '')

    return ''


def extract_readme_first_paragraph(readme_path: str) -> str:
    """Extract first meaningful paragraph from README file.

    Supports both Markdown (.md) and AsciiDoc (.adoc) formats.

    Args:
        readme_path: Project-relative path to README file.

    Returns:
        First paragraph content or empty string if not found.
    """
    path = Path(readme_path)
    if not path.exists():
        return ''

    try:
        content = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return ''

    lines = content.split('\n')
    paragraph_lines = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        # Skip title lines (# Title or = Title)
        if stripped.startswith('#') or stripped.startswith('='):
            # If we already collected paragraph, we're done
            if paragraph_lines:
                break
            continue

        # Skip empty lines at start, but end paragraph on empty line
        if not stripped:
            if paragraph_lines:
                break
            continue

        # Skip AsciiDoc attributes like :toc:
        if stripped.startswith(':') and ':' in stripped[1:]:
            continue

        # Skip list items, code blocks, etc.
        if stripped.startswith('*') or stripped.startswith('-') or stripped.startswith('```'):
            if paragraph_lines:
                break
            continue

        # Collect paragraph text
        paragraph_lines.append(stripped)
        in_paragraph = True

    if not paragraph_lines:
        return ''

    # Join and limit length
    text = ' '.join(paragraph_lines)
    # Get first 1-2 sentences (up to ~250 chars)
    match = re.match(r'^(.{1,250}?[.!?])(?:\s|$)', text)
    if match:
        return match.group(1).strip()

    # If no sentence boundary, return first ~200 chars
    return text[:200].strip() + ('...' if len(text) > 200 else '')


def find_project_readme() -> str:
    """Find project-level README file.

    Returns:
        Path to README file or empty string if not found.
    """
    for name in ['README.adoc', 'README.md', 'README.txt', 'README']:
        if Path(name).exists():
            return name
    return ''


def find_doc_files() -> list:
    """Find documentation files in doc/ directory.

    Returns:
        List of doc file paths (*.adoc, *.md).
    """
    doc_files = []
    doc_dir = Path('doc')
    if not doc_dir.exists():
        # Try 'docs' as alternative
        doc_dir = Path('docs')
    if not doc_dir.exists():
        return doc_files

    for ext in ['*.adoc', '*.md']:
        doc_files.extend(str(f) for f in doc_dir.glob(ext))

    return sorted(doc_files)


def find_doc_directories() -> list:
    """Find documentation subdirectories in doc/ directory.

    Returns:
        List of doc directory paths.
    """
    doc_dirs = []
    doc_dir = Path('doc')
    if not doc_dir.exists():
        doc_dir = Path('docs')
    if not doc_dir.exists():
        return doc_dirs

    for item in doc_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            doc_dirs.append(str(item))

    return sorted(doc_dirs)


def collect_doc_module_data() -> dict:
    """Collect documentation module data if doc/ directory exists.

    Returns:
        Dict with doc module info, or empty dict if no doc directory.
    """
    doc_dir = Path('doc')
    if not doc_dir.exists():
        doc_dir = Path('docs')
    if not doc_dir.exists():
        return {}

    # Count files by type
    adoc_files = list(doc_dir.rglob('*.adoc'))
    md_files = list(doc_dir.rglob('*.md'))
    puml_files = list(doc_dir.rglob('*.puml'))
    png_files = list(doc_dir.rglob('*.png'))

    # Get top-level sections (directories)
    sections = []
    for item in sorted(doc_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            sections.append(item.name)

    # Get top-level doc files
    top_files = []
    for item in sorted(doc_dir.iterdir()):
        if item.is_file() and item.suffix in ['.adoc', '.md']:
            top_files.append(item.name)

    # Detect content types
    content_types = []
    if adoc_files:
        content_types.append('asciidoc')
    if md_files:
        content_types.append('markdown')
    if puml_files:
        content_types.append('plantuml')

    return {
        'path': str(doc_dir),
        'content_types': content_types,
        'sections': sections,
        'top_files': top_files,
        'file_counts': {
            'asciidoc': len(adoc_files),
            'markdown': len(md_files),
            'plantuml': len(puml_files),
            'images': len(png_files)
        }
    }


def find_module_readme(module_path: str) -> str:
    """Find README file in a module directory.

    Args:
        module_path: Relative path to module directory.

    Returns:
        Project-relative path to README (e.g., 'my-core/README.md') or empty string if not found.
    """
    mod_dir = Path(module_path)
    if not mod_dir.exists():
        return ''

    for name in ['README.adoc', 'README.md', 'README.txt', 'README']:
        if (mod_dir / name).exists():
            return f"{module_path}/{name}"
    return ''


def find_ui_components_path(module_path: str) -> str:
    """Find UI components directory in a module.

    Detects common UI component locations for hybrid Java/JS modules:
    - Quarkus Dev UI: src/main/resources/dev-ui/components
    - Standard web resources: src/main/resources/META-INF/resources
    - Web components: src/main/webapp/components

    Args:
        module_path: Relative path to module directory.

    Returns:
        Project-relative path to UI components dir or empty string if not found.
    """
    mod_dir = Path(module_path)
    if not mod_dir.exists():
        return ''

    # Common UI component locations (priority order)
    ui_paths = [
        'src/main/resources/dev-ui/components',  # Quarkus Dev UI
        'src/main/resources/dev-ui',              # Quarkus Dev UI root
        'src/main/webapp/components',             # Traditional webapp
        'src/main/resources/META-INF/resources',  # JAX-RS static resources
    ]

    for ui_path in ui_paths:
        full_path = mod_dir / ui_path
        if full_path.exists() and full_path.is_dir():
            # Check if directory has JS/TS files
            has_js = any(full_path.rglob('*.js')) or any(full_path.rglob('*.ts'))
            if has_js:
                return f"{module_path}/{ui_path}"

    return ''


def scan_java_packages(module_path: str) -> dict:
    """Scan Java packages in a module with structured metadata.

    Args:
        module_path: Relative path to module directory.

    Returns:
        Dict of package name -> {path, package_info (if exists)}.
        - path: project-relative path to package directory
        - package_info: project-relative path to package-info.java (only if file exists)
    """
    packages = {}
    mod_dir = Path(module_path)

    # Common source roots with their project-relative prefixes
    source_configs = [
        (mod_dir / 'src' / 'main' / 'java', f"{module_path}/src/main/java"),
        (mod_dir / 'src' / 'main' / 'kotlin', f"{module_path}/src/main/kotlin"),
    ]

    for src_root, path_prefix in source_configs:
        if not src_root.exists():
            continue

        # Collect all package directories
        package_dirs = set()

        for java_file in src_root.rglob('*.java'):
            try:
                rel_path = java_file.relative_to(src_root)
                if rel_path.parent != Path('.'):
                    package_dirs.add(rel_path.parent)
            except ValueError:
                pass

        for kotlin_file in src_root.rglob('*.kt'):
            try:
                rel_path = kotlin_file.relative_to(src_root)
                if rel_path.parent != Path('.'):
                    package_dirs.add(rel_path.parent)
            except ValueError:
                pass

        # Build structured data for each package
        for pkg_dir in package_dirs:
            pkg_name = str(pkg_dir).replace(os.sep, '.')
            pkg_rel_path = f"{path_prefix}/{pkg_dir}"

            # Build package entry
            pkg_entry = {'path': pkg_rel_path}

            # Check for package-info.java - only add if exists
            pkg_info_file = src_root / pkg_dir / 'package-info.java'
            if pkg_info_file.exists():
                pkg_entry['package_info'] = f"{pkg_rel_path}/package-info.java"

            packages[pkg_name] = pkg_entry

    return packages


def count_source_files(module_path: str) -> int:
    """Count source files in a module.

    Args:
        module_path: Relative path to module directory.

    Returns:
        Number of source files (*.java, *.kt, *.js, *.ts).
    """
    mod_dir = Path(module_path)
    count = 0

    # Java/Kotlin sources
    src_main = mod_dir / 'src' / 'main'
    if src_main.exists():
        for ext in ['*.java', '*.kt']:
            count += len(list(src_main.rglob(ext)))

    # JavaScript/TypeScript sources
    src_dir = mod_dir / 'src'
    if src_dir.exists():
        for ext in ['*.js', '*.ts', '*.jsx', '*.tsx']:
            # Exclude test files and node_modules
            for f in src_dir.rglob(ext):
                if 'node_modules' not in str(f) and '.test.' not in str(f) and '.spec.' not in str(f):
                    count += 1

    return count


def count_test_files(module_path: str) -> int:
    """Count test files in a module.

    Args:
        module_path: Relative path to module directory.

    Returns:
        Number of test files.
    """
    mod_dir = Path(module_path)
    count = 0

    # Java/Kotlin tests
    src_test = mod_dir / 'src' / 'test'
    if src_test.exists():
        for ext in ['*.java', '*.kt']:
            count += len(list(src_test.rglob(ext)))

    # JavaScript/TypeScript tests
    for pattern in ['*.test.js', '*.test.ts', '*.spec.js', '*.spec.ts',
                    '*.test.jsx', '*.test.tsx', '*.spec.jsx', '*.spec.tsx']:
        count += len(list(mod_dir.rglob(pattern)))

    return count


def parse_maven_dependencies(pom_path: Path) -> list:
    """Parse dependencies from pom.xml with scope.

    Args:
        pom_path: Path to pom.xml file.

    Returns:
        List of dependencies in format "groupId:artifactId:scope".
    """
    deps = []
    if not pom_path.exists():
        return deps

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # Handle namespace
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

        # Try with namespace first
        deps_elem = root.find('m:dependencies', ns)
        if deps_elem is None:
            deps_elem = root.find('dependencies')

        if deps_elem is None:
            return deps

        for dep in deps_elem:
            # Get groupId
            group_id = dep.find('m:groupId', ns)
            if group_id is None:
                group_id = dep.find('groupId')

            # Get artifactId
            artifact_id = dep.find('m:artifactId', ns)
            if artifact_id is None:
                artifact_id = dep.find('artifactId')

            # Get scope (default to compile)
            scope_elem = dep.find('m:scope', ns)
            if scope_elem is None:
                scope_elem = dep.find('scope')
            scope = scope_elem.text if scope_elem is not None else 'compile'

            if group_id is not None and artifact_id is not None:
                deps.append(f"{group_id.text}:{artifact_id.text}:{scope}")

    except ET.ParseError:
        pass

    return deps


def parse_npm_dependencies(package_json_path: Path) -> list:
    """Parse dependencies from package.json with npm: prefix and scope.

    Args:
        package_json_path: Path to package.json file.

    Returns:
        List of dependencies in format "npm:package:scope".
        The npm: prefix distinguishes from maven dependencies in hybrid modules.
    """
    deps = []
    if not package_json_path.exists():
        return deps

    try:
        pkg_data = json.loads(package_json_path.read_text(encoding='utf-8'))

        # Regular dependencies -> compile scope
        for name in pkg_data.get('dependencies', {}).keys():
            deps.append(f"npm:{name}:compile")

        # Dev dependencies -> test scope
        for name in pkg_data.get('devDependencies', {}).keys():
            deps.append(f"npm:{name}:test")

    except (json.JSONDecodeError, IOError):
        pass

    return deps


def get_maven_packaging(pom_path: Path) -> str:
    """Get packaging type from pom.xml.

    Args:
        pom_path: Path to pom.xml file.

    Returns:
        Packaging type (jar, war, pom, etc.) or empty string.
    """
    if not pom_path.exists():
        return ''

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

        packaging = root.find('m:packaging', ns)
        if packaging is None:
            packaging = root.find('packaging')

        return packaging.text if packaging is not None else 'jar'

    except ET.ParseError:
        return ''


def transform_extension_module(ext_module: dict, root_path: Path) -> dict:
    """Transform extension module data to collect_raw_project_data format.

    Extensions return module data in the discover_modules contract format:
    - build_systems: array (e.g., ["maven"], ["gradle"], ["npm"])
    - paths: { module, descriptor, sources, tests, readme }
    - metadata: { artifact_id, group_id, packaging, ... }
    - packages: dict keyed by package name
    - dependencies: list of strings "groupId:artifactId:scope"
    - stats: { source_files, test_files }
    - commands: dict of canonical command strings

    This transforms to the flat format expected by raw-project-data.json consumers.

    Args:
        ext_module: Module dict from extension.discover_modules()
        root_path: Project root path for computing additional paths

    Returns:
        Module dict in collect_raw_project_data format.
    """
    paths = ext_module.get('paths', {})
    mod_path = paths.get('module', ext_module.get('path', '.'))

    # Get build_systems array (always present in spec-compliant modules)
    build_systems = ext_module.get('build_systems', [])

    # Start with basic fields
    module = {
        'name': ext_module.get('name', ''),
        'path': mod_path,
        'build_systems': build_systems,
    }

    # Extract packaging from metadata or top-level (filesystem format)
    metadata = ext_module.get('metadata', {})
    if metadata.get('packaging'):
        module['packaging'] = metadata['packaging']
    elif metadata.get('type'):
        module['packaging'] = metadata['type']
    elif ext_module.get('packaging'):
        module['packaging'] = ext_module['packaging']

    # Copy packages - convert dict to list if needed
    packages = ext_module.get('packages', {})
    if packages:
        if isinstance(packages, dict):
            module['packages'] = list(packages.keys())
        else:
            module['packages'] = packages

    # Copy dependencies directly (list of strings from extensions)
    dependencies = ext_module.get('dependencies', [])
    if dependencies:
        module['dependencies'] = dependencies

    # Flatten stats to top-level (check both nested stats and top-level for filesystem format)
    stats = ext_module.get('stats', {})
    source_files = stats.get('source_files', 0) or ext_module.get('source_files', 0)
    test_files = stats.get('test_files', 0) or ext_module.get('test_files', 0)
    if source_files > 0:
        module['source_files'] = source_files
    if test_files > 0:
        module['test_files'] = test_files

    # Get readme from paths (new contract), top-level (filesystem format), or fallback to stats.has_readme
    readme_path = paths.get('readme') or ext_module.get('readme')
    if readme_path:
        module['readme'] = readme_path
    elif stats.get('has_readme'):
        readme = find_module_readme(mod_path)
        if readme:
            module['readme'] = readme

    # Check for package.json descriptor (npm modules)
    descriptor = paths.get('descriptor', '')
    if 'package.json' in descriptor:
        module['package_json'] = descriptor

    # Detect UI components path for hybrid modules
    ui_path = find_ui_components_path(mod_path)
    if ui_path:
        module['ui_path'] = ui_path

    return module


def collect_raw_project_data(project_root: str = '.') -> dict:
    """Collect comprehensive raw project data for LLM analysis.

    Uses extension-based module discovery for comprehensive metadata
    extraction. Falls back to legacy filesystem detection if no
    extensions are available.

    Args:
        project_root: Path to project root directory.

    Returns:
        Dictionary with all collected project data in JSON-compatible format:
        {
            "project": {"root": "...", "name": "..."},
            "documentation": {...},
            "modules": [...]  # Unified module dicts with all metadata
        }

    Each module dict contains: name, path, build_systems, packaging,
    plus enrichment data: packages, dependencies, source_files, test_files, readme.

    For hybrid modules (Java + JavaScript):
    - dependencies: Combined list from all build systems
    - package_json: Path to package.json (for npm modules)
    - ui_path: Path to UI components directory (e.g., dev-ui/components)
    """
    root_path = Path(project_root).resolve()

    # Discover modules using extension API (preferred) or filesystem (fallback)
    ext_modules = discover_modules_from_extensions(str(root_path))

    # Transform extension format to expected output format
    modules = [transform_extension_module(m, root_path) for m in ext_modules]

    # Build complete data structure (JSON format)
    raw_data = {
        'project': {
            'root': str(root_path),
            'name': root_path.name
        },
        'documentation': {
            'readme': find_project_readme(),
            'doc_dir': 'doc' if Path('doc').exists() else ('docs' if Path('docs').exists() else None),
            'doc_files': find_doc_files()
        },
        'modules': modules
    }

    # Clean up None values in documentation
    raw_data['documentation'] = {k: v for k, v in raw_data['documentation'].items() if v is not None}

    return raw_data


# ===========================================================================
# Command: read
# ===========================================================================

def cmd_read(args) -> int:
    """Read project structure (generates if missing)."""
    try:
        try:
            structure = load_structure()
        except StructureNotFoundError:
            # Auto-generate if missing
            try:
                structure = generate_structure_from_marshal()
                save_structure(structure)
            except (MarshalNotFoundError, RawDataNotFoundError) as e:
                return error_exit(str(e))

        return success_exit({
            'file': str(STRUCTURE_PATH),
            **structure
        })
    except json.JSONDecodeError as e:
        return error_exit(f"Failed to parse project-structure.json: {e}")
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: generate
# ===========================================================================

def cmd_generate(args) -> int:
    """Generate project structure from codebase."""
    try:
        if STRUCTURE_PATH.exists() and not args.force:
            return error_exit(
                "project-structure.json already exists. Use --force to overwrite",
                file=str(STRUCTURE_PATH)
            )

        structure = generate_structure_from_marshal()
        save_structure(structure)

        modules_count = len(structure.get('modules', {}))
        return success_exit({
            'file': str(STRUCTURE_PATH),
            'modules_generated': modules_count,
            'message': f"Generated structure with {modules_count} modules"
        })
    except (MarshalNotFoundError, RawDataNotFoundError) as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: collect-raw-data
# ===========================================================================

RAW_DATA_PATH = PLAN_BASE_DIR / 'raw-project-data.json'


def cmd_collect_raw_data(args) -> int:
    """Collect comprehensive raw project data for LLM analysis.

    Scans the project filesystem to gather:
    - Module information (names, paths, build systems, packaging)
    - Per-module details (packages, dependencies, source/test counts)
    - Documentation (project README, doc files)

    This command discovers modules directly from the filesystem,
    without requiring marshal.json to be populated first.

    Output is written to .plan/raw-project-data.json in JSON format.
    """
    try:
        raw_data = collect_raw_project_data()

        # Write to file as JSON
        RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAW_DATA_PATH.write_text(json.dumps(raw_data, indent=2), encoding='utf-8')

        modules_count = len(raw_data.get('modules', []))
        doc_files_count = len(raw_data.get('documentation', {}).get('doc_files', []))

        return success_exit({
            'file': str(RAW_DATA_PATH),
            'modules_discovered': modules_count,
            'doc_files_found': doc_files_count,
            'message': f"Discovered {modules_count} modules from filesystem"
        })
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: raw-data-as-toon
# ===========================================================================

def cmd_raw_data_as_toon(args) -> int:
    """Output raw project data as TOON for LLM consumption.

    Reads .plan/raw-project-data.json and outputs it in TOON format,
    which is more token-efficient for LLM processing.

    If the file doesn't exist, returns error suggesting to run
    collect-raw-data first.
    """
    try:
        if not RAW_DATA_PATH.exists():
            return error_exit(
                f"{RAW_DATA_PATH} not found. Run 'collect-raw-data' command first."
            )

        raw_data = json.loads(RAW_DATA_PATH.read_text(encoding='utf-8'))

        # Convert to TOON format
        toon_output = serialize_toon(raw_data)
        print(toon_output)
        return 0
    except json.JSONDecodeError as e:
        return error_exit(f"Invalid JSON in {RAW_DATA_PATH}: {e}")
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: modules-for-commands
# ===========================================================================

def cmd_modules_for_commands(args) -> int:
    """Output module data needed for command generation.

    Reads raw-project-data.json and outputs a focused TOON format
    with just the fields needed for build command configuration:
    - name, path, build_systems, packaging

    This is the API for scripts that need module information
    for command generation.
    """
    try:
        if not RAW_DATA_PATH.exists():
            return error_exit(
                f"{RAW_DATA_PATH} not found. Run 'collect-raw-data' command first."
            )

        raw_data = json.loads(RAW_DATA_PATH.read_text(encoding='utf-8'))
        modules = raw_data.get('modules', [])

        # Apply module filter if specified
        module_filter = getattr(args, 'module', None)
        if module_filter:
            modules = [m for m in modules if m.get('name') == module_filter]
            if not modules:
                return error_exit(f"Module not found: {module_filter}")

        # Output as TOON uniform array
        fields = ['name', 'path', 'build_systems', 'packaging']
        print(f"modules[{len(modules)}]{{name,path,build_systems,packaging}}:")
        for mod in modules:
            name = mod.get('name', '')
            path = mod.get('path', '')
            # Join build_systems with + for TOON (avoid comma conflict)
            build_systems = '+'.join(mod.get('build_systems', []))
            packaging = mod.get('packaging', '')
            print(f"{name},{path},{build_systems},{packaging}")

        return 0
    except json.JSONDecodeError as e:
        return error_exit(f"Invalid JSON in {RAW_DATA_PATH}: {e}")
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: validate
# ===========================================================================

def cmd_validate(args) -> int:
    """Validate project structure format."""
    try:
        structure = load_structure()

        warnings = []

        # Check required sections
        if 'modules' not in structure:
            warnings.append("Missing 'modules' section")

        # Check module structure
        modules = structure.get('modules', {})
        for name, config in modules.items():
            if not config.get('responsibility'):
                warnings.append(f"Module '{name}' missing responsibility")

        return success_exit({
            'file': str(STRUCTURE_PATH),
            'modules_count': len(modules),
            'has_placement': bool(structure.get('placement')),
            'has_conventions': bool(structure.get('conventions')),
            'warnings': warnings
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except json.JSONDecodeError as e:
        return error_exit(f"Invalid JSON format: {e}")
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: project
# ===========================================================================

def cmd_project_update(args) -> int:
    """Update project-level metadata."""
    try:
        structure = load_structure()
        project = structure.get('project', {})

        if args.description:
            project['description'] = args.description
        if args.name:
            project['name'] = args.name

        structure['project'] = project
        save_structure(structure)

        return success_exit({
            'project': project.get('name', ''),
            'updated': True
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: module
# ===========================================================================

def cmd_module_get(args) -> int:
    """Get specific module metadata."""
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        return success_exit({
            'module': args.module,
            **modules[args.module]
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_module_list(args) -> int:
    """List all modules."""
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        module_list = []
        for name, config in modules.items():
            module_list.append({
                'name': name,
                'responsibility': config.get('responsibility', '')[:50]
            })

        return success_exit({
            'count': len(module_list),
            'modules': module_list
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_module_update(args) -> int:
    """Update module metadata."""
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        module = modules[args.module]

        if args.responsibility:
            module['responsibility'] = args.responsibility

        save_structure(structure)

        return success_exit({
            'module': args.module,
            'updated': True
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_module_add_tip(args) -> int:
    """Add implementation tip to module."""
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        module = modules[args.module]
        if 'tips' not in module:
            module['tips'] = []

        if args.tip not in module['tips']:
            module['tips'].append(args.tip)

        save_structure(structure)

        return success_exit({
            'module': args.module,
            'tip_added': args.tip
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_module_add_insight(args) -> int:
    """Add learned insight to module."""
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        module = modules[args.module]
        if 'insights' not in module:
            module['insights'] = []

        if args.insight not in module['insights']:
            module['insights'].append(args.insight)

        save_structure(structure)

        return success_exit({
            'module': args.module,
            'insight_added': args.insight
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))



def cmd_module_add_package(args) -> int:
    """Add key package to module with path, package_info, and optional description.

    Package structure:
    - path: project-relative path to package directory
    - package_info: project-relative path to package-info.java if exists
    - description: package description (1-2 sentences)
    """
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        module = modules[args.module]
        if 'key_packages' not in module:
            module['key_packages'] = {}

        # Get or create package entry
        existing = module['key_packages'].get(args.package, {})
        if isinstance(existing, str):
            # Migrate from old format (string description)
            existing = {'path': '', 'package_info': '', 'description': existing}

        # Update with provided values
        pkg_entry = {
            'path': args.path or existing.get('path', ''),
            'package_info': args.package_info or existing.get('package_info', ''),
            'description': args.description or existing.get('description', '')
        }
        module['key_packages'][args.package] = pkg_entry

        save_structure(structure)

        return success_exit({
            'module': args.module,
            'package_added': args.package,
            'path': pkg_entry['path'],
            'package_info': pkg_entry['package_info'],
            'description': pkg_entry['description']
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_module_set_package_description(args) -> int:
    """Set description for a key package.

    Updates the description field within the package's structured entry.
    """
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        module = modules[args.module]
        key_packages = module.get('key_packages', {})

        if args.package not in key_packages:
            return error_exit(f"Package not found: {args.package}. Add it first with add-package")

        # Get existing package entry
        pkg_entry = key_packages[args.package]
        if isinstance(pkg_entry, str):
            # Migrate from old format (string description)
            pkg_entry = {'path': '', 'package_info': '', 'description': pkg_entry}

        # Update description
        pkg_entry['description'] = args.description
        key_packages[args.package] = pkg_entry

        save_structure(structure)

        return success_exit({
            'module': args.module,
            'package': args.package,
            'description': args.description
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: placement
# ===========================================================================

def cmd_placement_query(args) -> int:
    """Query placement rule for component type."""
    try:
        structure = load_structure()
        placement = structure.get('placement', {})

        if args.component_type not in placement:
            return error_exit(f"Unknown component type: {args.component_type}")

        rule = placement[args.component_type]
        return success_exit({
            'component_type': args.component_type,
            **rule
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_placement_list(args) -> int:
    """List all placement rules."""
    try:
        structure = load_structure()
        placement = structure.get('placement', {})

        rules = []
        for comp_type, rule in placement.items():
            rules.append({
                'type': comp_type,
                'module': rule.get('module', ''),
                'pattern': rule.get('pattern', '')
            })

        return success_exit({
            'count': len(rules),
            'rules': rules
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_placement_set(args) -> int:
    """Set placement rule for component type."""
    try:
        structure = load_structure()

        if 'placement' not in structure:
            structure['placement'] = {}

        structure['placement'][args.component_type] = {
            'module': args.module,
            'package': args.package,
            'pattern': args.pattern
        }

        if args.test_pattern:
            structure['placement'][args.component_type]['test_pattern'] = args.test_pattern
        if args.example:
            structure['placement'][args.component_type]['example'] = args.example

        save_structure(structure)

        return success_exit({
            'component_type': args.component_type,
            'rule_set': True
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: convention
# ===========================================================================

def cmd_convention_list(args) -> int:
    """List all conventions."""
    try:
        structure = load_structure()
        conventions = structure.get('conventions', {})

        return success_exit({
            'naming': conventions.get('naming', []),
            'packages': conventions.get('packages', []),
            'testing': conventions.get('testing', []),
            'documentation': conventions.get('documentation', [])
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_convention_add(args) -> int:
    """Add a convention."""
    try:
        structure = load_structure()

        if 'conventions' not in structure:
            structure['conventions'] = {}

        category = args.category
        if category not in structure['conventions']:
            structure['conventions'][category] = []

        if args.convention not in structure['conventions'][category]:
            structure['conventions'][category].append(args.convention)

        save_structure(structure)

        return success_exit({
            'category': category,
            'convention_added': args.convention
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Command: dependency
# ===========================================================================

def cmd_dependency_list(args) -> int:
    """List module dependencies."""
    try:
        structure = load_structure()
        deps = structure.get('dependencies', {})

        return success_exit({
            'module_deps': deps.get('module_deps', {}),
            'layer_rules': deps.get('layer_rules', {})
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_dependency_add(args) -> int:
    """Add module dependency."""
    try:
        structure = load_structure()

        if 'dependencies' not in structure:
            structure['dependencies'] = {'module_deps': {}, 'layer_rules': {}}

        module_deps = structure['dependencies'].get('module_deps', {})

        if args.from_module not in module_deps:
            module_deps[args.from_module] = []

        if args.to_module not in module_deps[args.from_module]:
            module_deps[args.from_module].append(args.to_module)

        structure['dependencies']['module_deps'] = module_deps
        save_structure(structure)

        return success_exit({
            'from_module': args.from_module,
            'to_module': args.to_module,
            'added': True
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


# ===========================================================================
# Main entry point
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Manage project structure knowledge in .plan/project-structure.json"
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # read command
    read_parser = subparsers.add_parser('read', help='Read project structure')
    read_parser.set_defaults(func=cmd_read)

    # generate command
    generate_parser = subparsers.add_parser('generate', help='Generate structure from codebase')
    generate_parser.add_argument('--force', action='store_true', help='Overwrite existing')
    generate_parser.set_defaults(func=cmd_generate)

    # collect-raw-data command
    collect_parser = subparsers.add_parser('collect-raw-data', help='Collect raw project data for LLM analysis')
    collect_parser.set_defaults(func=cmd_collect_raw_data)

    # raw-data-as-toon command
    raw_toon_parser = subparsers.add_parser('raw-data-as-toon', help='Output raw project data as TOON')
    raw_toon_parser.set_defaults(func=cmd_raw_data_as_toon)

    # modules-for-commands command
    mod_cmd_parser = subparsers.add_parser('modules-for-commands', help='Output module data for command generation')
    mod_cmd_parser.add_argument('--module', help='Filter to specific module')
    mod_cmd_parser.set_defaults(func=cmd_modules_for_commands)

    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate structure format')
    validate_parser.set_defaults(func=cmd_validate)

    # project subcommand
    project_parser = subparsers.add_parser('project', help='Project-level operations')
    project_sub = project_parser.add_subparsers(dest='project_cmd', required=True)

    # project update
    proj_update = project_sub.add_parser('update', help='Update project metadata')
    proj_update.add_argument('--description', help='Project description (one sentence)')
    proj_update.add_argument('--name', help='Project name')
    proj_update.set_defaults(func=cmd_project_update)

    # module subcommand
    module_parser = subparsers.add_parser('module', help='Module operations')
    module_sub = module_parser.add_subparsers(dest='module_cmd', required=True)

    # module get
    mod_get = module_sub.add_parser('get', help='Get module metadata')
    mod_get.add_argument('--module', required=True, help='Module name')
    mod_get.set_defaults(func=cmd_module_get)

    # module list
    mod_list = module_sub.add_parser('list', help='List all modules')
    mod_list.set_defaults(func=cmd_module_list)

    # module update
    mod_update = module_sub.add_parser('update', help='Update module metadata')
    mod_update.add_argument('--module', required=True, help='Module name')
    mod_update.add_argument('--responsibility', help='Module responsibility')
    mod_update.set_defaults(func=cmd_module_update)

    # module add-tip
    mod_tip = module_sub.add_parser('add-tip', help='Add implementation tip')
    mod_tip.add_argument('--module', required=True, help='Module name')
    mod_tip.add_argument('--tip', required=True, help='Tip to add')
    mod_tip.set_defaults(func=cmd_module_add_tip)

    # module add-insight
    mod_insight = module_sub.add_parser('add-insight', help='Add learned insight')
    mod_insight.add_argument('--module', required=True, help='Module name')
    mod_insight.add_argument('--insight', required=True, help='Insight to add')
    mod_insight.set_defaults(func=cmd_module_add_insight)

    # module add-package
    mod_pkg = module_sub.add_parser('add-package', help='Add key package')
    mod_pkg.add_argument('--module', required=True, help='Module name')
    mod_pkg.add_argument('--package', required=True, help='Package to add (dot-notation)')
    mod_pkg.add_argument('--path', help='Project-relative path to package directory')
    mod_pkg.add_argument('--package-info', dest='package_info',
                        help='Project-relative path to package-info.java')
    mod_pkg.add_argument('--description', help='Package description (1-2 sentences)')
    mod_pkg.set_defaults(func=cmd_module_add_package)

    # module set-package-description
    mod_pkg_desc = module_sub.add_parser('set-package-description', help='Set package description')
    mod_pkg_desc.add_argument('--module', required=True, help='Module name')
    mod_pkg_desc.add_argument('--package', required=True, help='Package name')
    mod_pkg_desc.add_argument('--description', required=True, help='Package description (1-2 sentences)')
    mod_pkg_desc.set_defaults(func=cmd_module_set_package_description)

    # placement subcommand
    placement_parser = subparsers.add_parser('placement', help='Placement rule operations')
    placement_sub = placement_parser.add_subparsers(dest='placement_cmd', required=True)

    # placement query
    place_query = placement_sub.add_parser('query', help='Query placement rule')
    place_query.add_argument('--component-type', required=True, help='Component type')
    place_query.set_defaults(func=cmd_placement_query)

    # placement list
    place_list = placement_sub.add_parser('list', help='List all placement rules')
    place_list.set_defaults(func=cmd_placement_list)

    # placement set
    place_set = placement_sub.add_parser('set', help='Set placement rule')
    place_set.add_argument('--component-type', required=True, help='Component type')
    place_set.add_argument('--module', required=True, help='Target module')
    place_set.add_argument('--package', required=True, help='Package pattern')
    place_set.add_argument('--pattern', required=True, help='File pattern')
    place_set.add_argument('--test-pattern', help='Test file pattern')
    place_set.add_argument('--example', help='Example file name')
    place_set.set_defaults(func=cmd_placement_set)

    # convention subcommand
    conv_parser = subparsers.add_parser('convention', help='Convention operations')
    conv_sub = conv_parser.add_subparsers(dest='conv_cmd', required=True)

    # convention list
    conv_list = conv_sub.add_parser('list', help='List conventions')
    conv_list.set_defaults(func=cmd_convention_list)

    # convention add
    conv_add = conv_sub.add_parser('add', help='Add convention')
    conv_add.add_argument('--category', required=True,
                         choices=['naming', 'packages', 'testing', 'documentation'],
                         help='Convention category')
    conv_add.add_argument('--convention', required=True, help='Convention text')
    conv_add.set_defaults(func=cmd_convention_add)

    # dependency subcommand
    dep_parser = subparsers.add_parser('dependency', help='Dependency operations')
    dep_sub = dep_parser.add_subparsers(dest='dep_cmd', required=True)

    # dependency list
    dep_list = dep_sub.add_parser('list', help='List dependencies')
    dep_list.set_defaults(func=cmd_dependency_list)

    # dependency add
    dep_add = dep_sub.add_parser('add', help='Add module dependency')
    dep_add.add_argument('--from-module', required=True, help='Dependent module')
    dep_add.add_argument('--to-module', required=True, help='Dependency target')
    dep_add.set_defaults(func=cmd_dependency_add)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
