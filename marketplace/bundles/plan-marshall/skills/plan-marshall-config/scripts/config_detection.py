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


