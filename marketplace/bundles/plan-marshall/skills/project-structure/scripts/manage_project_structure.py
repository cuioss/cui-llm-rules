#!/usr/bin/env python3
"""
Manage project structure knowledge in .plan/project-structure.toon.

Provides operations for reading, generating, and updating project structure
metadata including module responsibilities, placement rules, and conventions.

Also provides collect-raw-data command to gather comprehensive project data
for LLM analysis.
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

from toon_parser import parse_toon, serialize_toon, ToonParseError

EXIT_SUCCESS = 0
EXIT_ERROR = 1

# File locations
PLAN_BASE_DIR = Path(os.environ.get('PLAN_BASE_DIR', '.plan'))
STRUCTURE_PATH = PLAN_BASE_DIR / 'project-structure.toon'
MARSHAL_PATH = PLAN_BASE_DIR / 'marshal.json'


class StructureNotFoundError(Exception):
    """Raised when project-structure.toon doesn't exist."""
    pass


class MarshalNotFoundError(Exception):
    """Raised when marshal.json doesn't exist."""
    pass


def output(data: dict) -> None:
    """Output TOON result to stdout."""
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
    """Ensure value is a list. Converts empty dict to empty list.

    The TOON parser sometimes returns {} for empty arrays, so this
    normalizes to a list.
    """
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and len(value) == 0:
        return []
    if value is None:
        return []
    return [value]  # Single value to list


def normalize_module_lists(module: dict) -> dict:
    """Normalize list fields in module to ensure they are lists."""
    list_fields = ['key_packages', 'tips', 'insights', 'best_practices']
    for field in list_fields:
        if field in module:
            module[field] = ensure_list(module[field])
    return module


def load_structure() -> dict:
    """Load project-structure.toon."""
    if not STRUCTURE_PATH.exists():
        raise StructureNotFoundError(
            "project-structure.toon not found. Run 'generate' command first"
        )
    content = STRUCTURE_PATH.read_text(encoding='utf-8')
    structure = parse_toon(content)

    # Normalize list fields in modules
    modules = structure.get('modules', {})
    for module_name, module_config in modules.items():
        if isinstance(module_config, dict):
            normalize_module_lists(module_config)

    # Normalize convention lists
    conventions = structure.get('conventions', {})
    for category in conventions:
        if isinstance(conventions[category], dict) and len(conventions[category]) == 0:
            conventions[category] = []

    return structure


def save_structure(structure: dict) -> None:
    """Save project-structure.toon."""
    STRUCTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STRUCTURE_PATH.write_text(serialize_toon(structure), encoding='utf-8')


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
    parent_name: str = None,
    discovered: list = None
) -> list:
    """Recursively discover modules from filesystem.

    Parses pom.xml <modules> sections to find all Maven modules,
    including nested submodules. Also detects npm (package.json).

    Args:
        project_root: Absolute path to project root.
        current_path: Current directory being scanned.
        parent_name: Name of parent module (None for top-level).
        discovered: Accumulator list for discovered modules.

    Returns:
        List of module dicts with: name, path, parent, build_systems, packaging.
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

        # Add module
        module_entry = {
            'name': submodule_name,
            'path': rel_path,
            'parent': parent_name,
            'build_systems': build_systems,
            'packaging': packaging
        }
        discovered.append(module_entry)

        # Recurse into nested modules
        discover_modules_recursive(
            project_root,
            submodule_path,
            parent_name=submodule_name,
            discovered=discovered
        )

    return discovered


def discover_modules_from_filesystem(project_root: str = '.') -> list:
    """Discover all modules from filesystem without marshal.json dependency.

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
        return discover_modules_recursive(root_path, root_path, parent_name=None)

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
            'parent': None,
            'build_systems': ['npm'],
            'packaging': 'npm'
        }]

    return []


def infer_layer_from_module(name: str, module_type: str = None, packaging: str = None) -> str:
    """Infer architectural layer from module name, type, and packaging.

    Only returns a layer if it can be meaningfully inferred:
    - packaging=pom (parent poms, bom) -> parent
    - *-ui, *-frontend, *-web -> presentation
    - *-api -> api
    - *-service -> service
    - *-test*, integration-*, e2e-* -> testing
    - *-nar, *-assembly, *-dist -> packaging
    - Otherwise -> 'unknown' (will be omitted from output)

    Note: *-core modules are NOT auto-mapped. Determining if something is
    'library' vs 'service' requires LLM analysis.
    """
    name_lower = name.lower()

    # POM packaging = parent/aggregator modules
    if packaging == 'pom':
        return 'parent'

    if any(suffix in name_lower for suffix in ['-ui', '-frontend', '-web', 'webapp']):
        return 'presentation'
    if '-api' in name_lower:
        return 'api'
    if '-service' in name_lower:
        return 'service'
    if any(prefix in name_lower for prefix in ['test', 'integration', 'e2e', 'e-2-e']):
        return 'testing'
    if any(suffix in name_lower for suffix in ['-nar', '-assembly', '-dist', '-package']):
        return 'packaging'

    return 'unknown'


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


def select_key_packages(packages: list, max_packages: int = 4) -> list:
    """Select architecturally significant packages from a list.

    Prioritizes packages that are likely important (domain, core, api)
    and excludes utility packages (util, helper, internal).

    Args:
        packages: List of package names.
        max_packages: Maximum packages to return.

    Returns:
        Selected key packages (up to max_packages).
    """
    if not packages:
        return []

    # Skip patterns (internal implementation details)
    skip_patterns = ['util', 'helper', 'internal', 'impl', 'support']

    # Priority patterns (architecturally significant)
    priority_patterns = ['domain', 'core', 'api', 'service', 'pipeline', 'model']

    # Filter out utility packages
    filtered = [p for p in packages
                if not any(skip in p.lower().split('.')[-1] for skip in skip_patterns)]

    # If all filtered out, use original
    if not filtered:
        filtered = packages

    # Sort by priority (priority patterns first, then by length - shorter = higher level)
    def sort_key(pkg):
        parts = pkg.lower().split('.')
        last_part = parts[-1] if parts else ''
        # Priority if matches important pattern
        priority = 0 if any(p in last_part for p in priority_patterns) else 1
        # Shorter packages are usually higher-level
        return (priority, len(parts), pkg)

    sorted_packages = sorted(filtered, key=sort_key)
    return sorted_packages[:max_packages]


def detect_framework_from_dependencies(dependencies: list) -> str:
    """Detect framework from dependency list.

    Args:
        dependencies: List of dependencies in format "groupId:artifactId:scope"

    Returns:
        Detected framework name or empty string.
    """
    if not dependencies:
        return ''

    deps_str = ' '.join(str(d) for d in dependencies).lower()

    if 'io.quarkus:' in deps_str:
        return 'quarkus'
    if 'org.springframework' in deps_str:
        return 'spring'
    if 'org.apache.nifi' in deps_str:
        return 'nifi'

    return ''




def extract_module_dependencies(dependencies: list, all_module_names: set) -> list:
    """Extract inter-module dependencies from dependency list.

    Looks for dependencies that reference other modules in this project.

    Args:
        dependencies: List of dependencies in format "groupId:artifactId:scope"
        all_module_names: Set of all module names in the project

    Returns:
        List of unique module names this module depends on.
    """
    module_deps = set()  # Use set for deduplication
    for dep in dependencies:
        dep_str = str(dep).lower()
        # Extract artifactId from "groupId:artifactId:scope"
        parts = dep_str.split(':')
        if len(parts) >= 2:
            artifact_id = parts[1]
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


class RawDataNotFoundError(Exception):
    """Raised when raw-project-data.json doesn't exist or is empty."""
    pass


def generate_structure_from_marshal() -> dict:
    """Generate project-structure.toon from raw-project-data.json and marshal.json.

    Uses raw-project-data.json as the source of truth for module facts:
    - Module names, paths, build systems, packaging
    - Key packages
    - Framework detection from dependencies
    - Layer inference from packaging type
    - Inter-module dependencies

    Uses marshal.json['module_config'] only for command configuration (not module facts).

    Only outputs fields that have actual values (no empty arrays, no 'none' values).

    Raises:
        RawDataNotFoundError: If raw-project-data.json doesn't exist or has no modules.
    """
    # Load raw data as primary source for module facts
    raw_data = load_raw_data()
    raw_modules_list = raw_data.get('modules', [])  # List of module dicts
    module_details = raw_data.get('module_details', {})

    # Check if we have module data to work with
    if not raw_modules_list:
        raise RawDataNotFoundError(
            "No module data found. Run 'collect-raw-data' command first to discover modules"
        )

    # Convert modules list to dict keyed by name
    modules_config = {}
    for module in raw_modules_list:
        name = module.get('name', '')
        if name:
            modules_config[name] = {
                'path': module.get('path', name),
                'build_systems': module.get('build_systems', []),
                'packaging': module.get('packaging', ''),
                'parent': module.get('parent')
            }

    # Load raw data for enrichment (use module_details for per-module metadata)
    raw_modules = module_details

    # Get all module names for dependency extraction
    all_module_names = set(m for m in modules_config.keys() if m != 'default')

    # Build project-level section from raw data
    project_section = {
        'name': extract_project_name(raw_data.get('project_root', '')),
        'description': ''  # To be filled by LLM
    }

    # Add frameworks if detected
    frameworks = ensure_list(raw_data.get('detected_frameworks', []))
    if frameworks:
        project_section['frameworks'] = frameworks

    # Add testing frameworks if detected
    testing = ensure_list(raw_data.get('detected_testing', []))
    if testing:
        project_section['testing'] = testing

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

    for module_name, module_config in modules_config.items():
        if module_name == 'default':
            continue  # Skip default module template

        build_systems = module_config.get('build_systems', [])
        domains = infer_domains_from_build_systems(build_systems)

        # Get packaging from modules_config (extracted from modules list)
        packaging = module_config.get('packaging', '')

        # Get enrichment data from module_details
        raw_module = raw_modules.get(module_name, {})
        packages = ensure_list(raw_module.get('packages', []))
        dependencies = ensure_list(raw_module.get('dependencies', []))

        # Infer layer using packaging type (only if meaningfully inferrable)
        layer = infer_layer_from_module(module_name, module_config.get('type'), packaging)

        # Detect technology from dependencies
        framework = detect_framework_from_dependencies(dependencies)

        # Select key packages
        key_packages = select_key_packages(packages)

        # Extract inter-module dependencies
        module_deps = extract_module_dependencies(dependencies, all_module_names)
        if module_deps:
            structure['dependencies'][module_name] = module_deps

        # Build module entry with only non-empty fields
        module_entry = {}

        # Only add layer if meaningfully inferred (not default 'unknown')
        if layer and layer != 'unknown':
            module_entry['layer'] = layer

        # Only add framework if detected
        if framework:
            module_entry['framework'] = framework

        # Only add key_packages if non-empty
        if key_packages:
            module_entry['key_packages'] = key_packages

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
        README filename or empty string if not found.
    """
    mod_dir = Path(module_path)
    if not mod_dir.exists():
        return ''

    for name in ['README.adoc', 'README.md', 'README.txt', 'README']:
        if (mod_dir / name).exists():
            return name
    return ''


def scan_java_packages(module_path: str) -> list:
    """Scan Java packages in a module.

    Args:
        module_path: Relative path to module directory.

    Returns:
        List of Java package names found.
    """
    packages = set()
    mod_dir = Path(module_path)

    # Common source roots
    source_roots = [
        mod_dir / 'src' / 'main' / 'java',
        mod_dir / 'src' / 'main' / 'kotlin',
    ]

    for src_root in source_roots:
        if not src_root.exists():
            continue

        for java_file in src_root.rglob('*.java'):
            # Extract package from directory structure
            try:
                rel_path = java_file.relative_to(src_root)
                if rel_path.parent != Path('.'):
                    package = str(rel_path.parent).replace(os.sep, '.')
                    packages.add(package)
            except ValueError:
                pass

        for kotlin_file in src_root.rglob('*.kt'):
            try:
                rel_path = kotlin_file.relative_to(src_root)
                if rel_path.parent != Path('.'):
                    package = str(rel_path.parent).replace(os.sep, '.')
                    packages.add(package)
            except ValueError:
                pass

    return sorted(packages)


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
    """Parse dependencies from package.json with scope.

    Args:
        package_json_path: Path to package.json file.

    Returns:
        List of dependencies in format "package:scope".
    """
    deps = []
    if not package_json_path.exists():
        return deps

    try:
        pkg_data = json.loads(package_json_path.read_text(encoding='utf-8'))

        # Regular dependencies -> compile scope
        for name in pkg_data.get('dependencies', {}).keys():
            deps.append(f"{name}:compile")

        # Dev dependencies -> test scope
        for name in pkg_data.get('devDependencies', {}).keys():
            deps.append(f"{name}:test")

    except (json.JSONDecodeError, IOError):
        pass

    return deps


def detect_frameworks(module_path: str) -> list:
    """Detect frameworks used in a module.

    Args:
        module_path: Relative path to module directory.

    Returns:
        List of detected framework names.
    """
    frameworks = set()
    mod_dir = Path(module_path)

    # Check pom.xml for Maven dependencies
    pom_path = mod_dir / 'pom.xml'
    if pom_path.exists():
        try:
            content = pom_path.read_text(encoding='utf-8')
            if 'quarkus' in content.lower():
                frameworks.add('quarkus')
            if 'spring' in content.lower():
                frameworks.add('spring')
            if 'jakarta.ee' in content or 'javax.enterprise' in content:
                frameworks.add('cdi')
        except IOError:
            pass

    # Check package.json for npm dependencies
    pkg_path = mod_dir / 'package.json'
    if pkg_path.exists():
        try:
            pkg_data = json.loads(pkg_path.read_text(encoding='utf-8'))
            all_deps = list(pkg_data.get('dependencies', {}).keys()) + \
                       list(pkg_data.get('devDependencies', {}).keys())
            for dep in all_deps:
                if 'react' in dep.lower():
                    frameworks.add('react')
                if 'angular' in dep.lower():
                    frameworks.add('angular')
                if 'vue' in dep.lower():
                    frameworks.add('vue')
        except (json.JSONDecodeError, IOError):
            pass

    return sorted(frameworks)


def detect_testing_frameworks(module_path: str) -> list:
    """Detect testing frameworks used in a module.

    Args:
        module_path: Relative path to module directory.

    Returns:
        List of detected testing framework names.
    """
    testing = set()
    mod_dir = Path(module_path)

    # Check pom.xml
    pom_path = mod_dir / 'pom.xml'
    if pom_path.exists():
        try:
            content = pom_path.read_text(encoding='utf-8')
            if 'junit-jupiter' in content or 'junit5' in content.lower():
                testing.add('junit5')
            elif 'junit' in content.lower():
                testing.add('junit4')
            if 'mockito' in content.lower():
                testing.add('mockito')
            if 'assertj' in content.lower():
                testing.add('assertj')
            if 'arquillian' in content.lower():
                testing.add('arquillian')
        except IOError:
            pass

    # Check package.json
    pkg_path = mod_dir / 'package.json'
    if pkg_path.exists():
        try:
            pkg_data = json.loads(pkg_path.read_text(encoding='utf-8'))
            all_deps = list(pkg_data.get('devDependencies', {}).keys())
            for dep in all_deps:
                if 'jest' in dep.lower():
                    testing.add('jest')
                if 'mocha' in dep.lower():
                    testing.add('mocha')
                if 'cypress' in dep.lower():
                    testing.add('cypress')
                if 'vitest' in dep.lower():
                    testing.add('vitest')
        except (json.JSONDecodeError, IOError):
            pass

    return sorted(testing)


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


def collect_raw_project_data(project_root: str = '.') -> dict:
    """Collect comprehensive raw project data for LLM analysis.

    This function discovers modules directly from the filesystem,
    without requiring marshal.json to be populated first.

    Args:
        project_root: Path to project root directory.

    Returns:
        Dictionary with all collected project data in JSON-compatible format:
        {
            "project": {"root": "...", "name": "..."},
            "frameworks": [...],
            "documentation": {...},
            "modules": [...],  # List of module dicts
            "module_details": {...}  # Per-module metadata
        }
    """
    root_path = Path(project_root).resolve()

    # Discover modules from filesystem (no marshal.json dependency)
    modules = discover_modules_from_filesystem(str(root_path))

    # Aggregate frameworks and testing across all modules
    all_frameworks = set()
    all_testing = set()

    # Collect detailed module data
    module_details = {}
    for module in modules:
        mod_name = module['name']
        mod_path = module['path']
        full_path = root_path / mod_path

        pom_path = full_path / 'pom.xml'
        pkg_json_path = full_path / 'package.json'

        # Get dependencies
        if pom_path.exists():
            dependencies = parse_maven_dependencies(pom_path)
        elif pkg_json_path.exists():
            dependencies = parse_npm_dependencies(pkg_json_path)
        else:
            dependencies = []

        # Detect frameworks and testing
        frameworks = detect_frameworks(mod_path)
        testing = detect_testing_frameworks(mod_path)
        all_frameworks.update(frameworks)
        all_testing.update(testing)

        # Build module details entry (only if has meaningful data)
        details = {}

        packages = scan_java_packages(mod_path)
        if packages:
            details['packages'] = packages

        if dependencies:
            details['dependencies'] = dependencies

        source_count = count_source_files(mod_path)
        if source_count > 0:
            details['source_files'] = source_count

        test_count = count_test_files(mod_path)
        if test_count > 0:
            details['test_files'] = test_count

        readme = find_module_readme(mod_path)
        if readme:
            details['readme'] = readme

        # Only add to module_details if has data
        if details:
            module_details[mod_name] = details

    # Build complete data structure (JSON format)
    raw_data = {
        'project': {
            'root': str(root_path),
            'name': root_path.name
        },
        'frameworks': sorted(all_frameworks),
        'documentation': {
            'readme': find_project_readme(),
            'doc_dir': 'doc' if Path('doc').exists() else ('docs' if Path('docs').exists() else None),
            'doc_files': find_doc_files()
        },
        'modules': modules,
        'module_details': module_details
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
    except ToonParseError as e:
        return error_exit(f"Failed to parse project-structure.toon: {e}")
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
                "project-structure.toon already exists. Use --force to overwrite",
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
    - Detected frameworks

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
            'frameworks_detected': raw_data.get('frameworks', []),
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

    This is the API for build_env and other scripts that need
    module information for command generation.
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
            if not config.get('layer'):
                warnings.append(f"Module '{name}' missing layer")

        return success_exit({
            'file': str(STRUCTURE_PATH),
            'modules_count': len(modules),
            'has_placement': bool(structure.get('placement')),
            'has_conventions': bool(structure.get('conventions')),
            'warnings': warnings
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except ToonParseError as e:
        return error_exit(f"Invalid TOON format: {e}")
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
                'layer': config.get('layer', ''),
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
        if args.layer:
            module['layer'] = args.layer

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


def cmd_module_set_technology(args) -> int:
    """Set technology stack for module."""
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        module = modules[args.module]
        if 'technology' not in module:
            module['technology'] = {}

        if args.framework:
            module['technology']['framework'] = args.framework
        if args.di:
            module['technology']['di'] = args.di
        if args.testing:
            module['technology']['testing'] = args.testing

        save_structure(structure)

        return success_exit({
            'module': args.module,
            'technology': module['technology']
        })
    except StructureNotFoundError as e:
        return error_exit(str(e))
    except Exception as e:
        return error_exit(str(e))


def cmd_module_add_package(args) -> int:
    """Add key package to module."""
    try:
        structure = load_structure()
        modules = structure.get('modules', {})

        if args.module not in modules:
            return error_exit(f"Unknown module: {args.module}")

        module = modules[args.module]
        if 'key_packages' not in module:
            module['key_packages'] = []

        if args.package not in module['key_packages']:
            module['key_packages'].append(args.package)

        save_structure(structure)

        return success_exit({
            'module': args.module,
            'package_added': args.package
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
        description="Manage project structure knowledge in .plan/project-structure.toon"
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
    mod_update.add_argument('--layer', help='Architectural layer')
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

    # module set-technology
    mod_tech = module_sub.add_parser('set-technology', help='Set technology stack')
    mod_tech.add_argument('--module', required=True, help='Module name')
    mod_tech.add_argument('--framework', help='Framework name')
    mod_tech.add_argument('--di', help='DI framework (cdi, spring, none)')
    mod_tech.add_argument('--testing', help='Testing framework')
    mod_tech.set_defaults(func=cmd_module_set_technology)

    # module add-package
    mod_pkg = module_sub.add_parser('add-package', help='Add key package')
    mod_pkg.add_argument('--module', required=True, help='Module name')
    mod_pkg.add_argument('--package', required=True, help='Package to add')
    mod_pkg.set_defaults(func=cmd_module_add_package)

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
