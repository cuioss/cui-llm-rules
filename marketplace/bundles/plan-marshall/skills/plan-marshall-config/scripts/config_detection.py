"""
Project detection functions for plan-marshall-config.

Auto-detects build systems, domains, and modules from project files.
"""

import copy
import xml.etree.ElementTree as ET
from pathlib import Path

from config_defaults import (
    BUILD_SYSTEM_DEFAULTS,
    DOMAIN_TEMPLATES,
    DEFAULT_PROFILES,
)


def detect_build_systems() -> list:
    """Auto-detect build systems from project files.

    Returns:
        List of build system configs with system and skill (detection reference only).
    """
    detected = []
    project_root = Path('.')

    # Maven
    if (project_root / 'pom.xml').exists():
        defaults = BUILD_SYSTEM_DEFAULTS["maven"]
        detected.append({
            "system": "maven",
            "skill": defaults["skill"]
        })

    # Gradle
    if (project_root / 'build.gradle').exists() or (project_root / 'build.gradle.kts').exists():
        defaults = BUILD_SYSTEM_DEFAULTS["gradle"]
        detected.append({
            "system": "gradle",
            "skill": defaults["skill"]
        })

    # npm
    if (project_root / 'package.json').exists():
        defaults = BUILD_SYSTEM_DEFAULTS["npm"]
        detected.append({
            "system": "npm",
            "skill": defaults["skill"]
        })

    return detected


def detect_domains() -> dict:
    """Auto-detect technical domains from project files.

    Returns:
        Dict mapping domain name to domain config (nested structure).
    """
    detected = {}
    project_root = Path('.')

    # Java detection: pom.xml or build.gradle
    if (project_root / 'pom.xml').exists() or \
       (project_root / 'build.gradle').exists() or \
       (project_root / 'build.gradle.kts').exists():
        detected['java'] = copy.deepcopy(DOMAIN_TEMPLATES['java'])

    # JavaScript detection: package.json
    if (project_root / 'package.json').exists():
        detected['javascript'] = copy.deepcopy(DOMAIN_TEMPLATES['javascript'])

    return detected


def detect_maven_modules() -> list:
    """Detect Maven modules from pom.xml.

    Returns:
        List of module info dicts with name and path.
    """
    modules = []
    pom_path = Path('pom.xml')
    if not pom_path.exists():
        return modules

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # Handle namespace
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        ns_prefix = '{http://maven.apache.org/POM/4.0.0}'

        # Try with namespace first
        modules_elem = root.find('m:modules', ns)
        if modules_elem is None:
            # Try without namespace
            modules_elem = root.find('modules')

        if modules_elem is not None:
            for module in modules_elem:
                mod_name = module.text
                if mod_name:
                    modules.append({
                        "name": mod_name,
                        "path": mod_name
                    })
    except ET.ParseError:
        pass

    return modules


def migrate_domain_to_profiles(flat_config: dict) -> dict:
    """Migrate flat domain config to profile-based structure.

    Converts a flat {defaults: [], optionals: []} structure to
    the 5-profile nested structure, preserving existing skills in core.

    Args:
        flat_config: Dict with 'defaults' and/or 'optionals' keys

    Returns:
        Dict with core + 5 profile structure
    """
    defaults = flat_config.get("defaults", [])
    optionals = flat_config.get("optionals", [])

    return {
        "core": {
            "defaults": defaults,
            "optionals": optionals
        },
        "architecture": {"defaults": [], "optionals": []},
        "planning": {"defaults": [], "optionals": []},
        "implementation": {"defaults": [], "optionals": []},
        "testing": {"defaults": [], "optionals": []},
        "quality": {"defaults": [], "optionals": []}
    }


def is_flat_domain(domain_config: dict) -> bool:
    """Check if domain config uses flat structure (not profile-based).

    A flat domain has 'defaults' or 'optionals' at top level
    without any profile keys.

    Args:
        domain_config: Domain configuration dict

    Returns:
        True if flat structure, False if nested/profile-based
    """
    has_flat_keys = 'defaults' in domain_config or 'optionals' in domain_config
    has_profile_keys = any(k in domain_config for k in ['core', 'workflow_skills', 'workflow_skill_extensions'])
    return has_flat_keys and not has_profile_keys
