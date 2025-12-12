#!/usr/bin/env python3
"""
Plan-Marshall configuration management for project-level infrastructure settings.

Manages .plan/marshal.json with noun-verb subcommand pattern.

Usage:
    plan-marshall-config.py skill-domains list
    plan-marshall-config.py skill-domains get --domain java
    plan-marshall-config.py modules detect
    plan-marshall-config.py build-systems detect
    plan-marshall-config.py system retention get
    plan-marshall-config.py plan defaults list
    plan-marshall-config.py init
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add parent paths for imports
script_dir = Path(__file__).parent
BUNDLES_DIR = script_dir.parent.parent.parent.parent  # .../bundles/
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'))

from toon_parser import serialize_toon

EXIT_SUCCESS = 0
EXIT_ERROR = 1

# File location
PLAN_BASE_DIR = Path(os.environ.get('PLAN_BASE_DIR', '.plan'))
MARSHAL_PATH = PLAN_BASE_DIR / 'marshal.json'

# Template location
TEMPLATES_DIR = Path(__file__).parent.parent / 'templates'
DEFAULTS_TEMPLATE = TEMPLATES_DIR / 'marshal-defaults.json'

# Build system defaults
BUILD_SYSTEM_DEFAULTS = {
    "maven": {
        "skill": "pm-dev-builder:builder-maven-rules",
        "commands": {
            "compile": "compile",
            "test-compile": "test-compile",
            "test": "clean test",
            "verify": "clean verify",
            "install": "clean install",
            "pre-commit": "-Ppre-commit clean install",
            "coverage": "-Pcoverage clean verify",
            "integration": "-Pintegration-tests clean verify",
            "native": "clean package -Dnative"
        }
    },
    "gradle": {
        "skill": "pm-dev-builder:builder-gradle-rules",
        "commands": {
            "compile": "compileJava",
            "test-compile": "testClasses",
            "test": "clean test",
            "verify": "clean check",
            "install": "clean publishToMavenLocal",
            "pre-commit": "clean preCommit",
            "coverage": "clean test jacocoTestReport"
        }
    },
    "npm": {
        "skill": "pm-dev-builder:builder-npm-rules",
        "commands": {
            "compile": "run build",
            "test": "run test",
            "verify": "run test && run lint",
            "lint": "run lint",
            "format": "run format:check",
            "coverage": "run test:coverage",
            "e2e": "run test:e2e"
        }
    }
}


class MarshalNotInitializedError(Exception):
    """Raised when marshal.json doesn't exist and operation requires it."""
    pass


def is_initialized() -> bool:
    """Check if marshal.json exists."""
    return MARSHAL_PATH.exists()


def require_initialized() -> None:
    """Raise exception if marshal.json doesn't exist."""
    if not PLAN_BASE_DIR.exists():
        raise MarshalNotInitializedError(
            f"Directory '{PLAN_BASE_DIR}' does not exist. Run command /plan-marshall first"
        )
    if not MARSHAL_PATH.exists():
        raise MarshalNotInitializedError(
            f"marshal.json not found. Run command /plan-marshall first"
        )


def load_config() -> dict:
    """Load marshal.json."""
    return json.loads(MARSHAL_PATH.read_text(encoding='utf-8'))


def save_config(config: dict) -> None:
    """Save config to marshal.json."""
    MARSHAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARSHAL_PATH.write_text(json.dumps(config, indent=2), encoding='utf-8')


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


# =============================================================================
# skill-domains Subcommand
# =============================================================================

def cmd_skill_domains(args) -> int:
    """Handle skill-domains noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()

    if "skill_domains" not in config:
        return error_exit("skill_domains not configured. Run command /plan-marshall first")

    skill_domains = config.get('skill_domains', {})

    if args.verb == 'list':
        domains = list(skill_domains.keys())
        return success_exit({"domains": domains, "count": len(domains)})

    elif args.verb == 'get':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]
        return success_exit({
            "domain": domain,
            "defaults": domain_config.get("defaults", []),
            "optionals": domain_config.get("optionals", [])
        })

    elif args.verb == 'get-defaults':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        defaults = skill_domains[domain].get("defaults", [])
        return success_exit({"domain": domain, "defaults": defaults})

    elif args.verb == 'get-optionals':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        optionals = skill_domains[domain].get("optionals", [])
        return success_exit({"domain": domain, "optionals": optionals})

    elif args.verb == 'set':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}. Use 'add' to create new domain.")
        if args.defaults:
            skill_domains[domain]["defaults"] = args.defaults.split(',')
        if args.optionals is not None:
            skill_domains[domain]["optionals"] = args.optionals.split(',') if args.optionals else []
        config['skill_domains'] = skill_domains
        save_config(config)
        return success_exit({
            "domain": domain,
            "updated": skill_domains[domain]
        })

    elif args.verb == 'add':
        domain = args.domain
        if domain in skill_domains:
            return error_exit(f"Domain already exists: {domain}")
        defaults = args.defaults.split(',') if args.defaults else []
        optionals = args.optionals.split(',') if args.optionals else []
        skill_domains[domain] = {"defaults": defaults, "optionals": optionals}
        config['skill_domains'] = skill_domains
        save_config(config)
        return success_exit({
            "domain": domain,
            "added": skill_domains[domain]
        })

    elif args.verb == 'validate':
        domain = args.domain
        skill = args.skill
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]
        all_skills = domain_config.get("defaults", []) + domain_config.get("optionals", [])
        valid = skill in all_skills
        return success_exit({
            "domain": domain,
            "skill": skill,
            "valid": valid,
            "in_defaults": skill in domain_config.get("defaults", []),
            "in_optionals": skill in domain_config.get("optionals", [])
        })

    return EXIT_ERROR


# =============================================================================
# modules Subcommand
# =============================================================================

def detect_maven_modules() -> list:
    """Detect Maven modules from pom.xml."""
    modules = []
    pom_path = Path('pom.xml')
    if not pom_path.exists():
        return modules

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # Handle namespace
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

        # Find modules element
        modules_elem = root.find('m:modules', ns)
        if modules_elem is None:
            # Try without namespace
            modules_elem = root.find('modules')

        if modules_elem is not None:
            for module in modules_elem.findall('m:module', ns):
                if module.text:
                    modules.append(module.text)
            # Try without namespace
            for module in modules_elem.findall('module'):
                if module.text and module.text not in modules:
                    modules.append(module.text)
    except ET.ParseError:
        pass

    return modules


def infer_domains_from_module(module_path: str) -> list:
    """Infer skill domains from module content."""
    domains = []
    path = Path(module_path)

    if not path.exists():
        return domains

    # Check for Java files
    has_java = list(path.rglob('*.java'))
    has_test_java = any('test' in str(f).lower() for f in has_java)

    # Check for JavaScript files
    has_js = list(path.rglob('*.js')) + list(path.rglob('*.ts'))
    has_test_js = any('test' in str(f).lower() or 'spec' in str(f).lower() for f in has_js)

    # Determine domains
    if has_java and not has_test_java:
        domains.append('java')
    if has_test_java:
        domains.append('java-testing')
    if has_js and not has_test_js:
        domains.append('javascript')
    if has_test_js:
        domains.append('javascript-testing')

    # If path contains 'test' or 'e2e', mark as testing
    path_lower = str(path).lower()
    if 'e2e' in path_lower or 'playwright' in path_lower or 'cypress' in path_lower:
        if 'javascript-testing' not in domains:
            domains.append('javascript-testing')

    return domains if domains else ['java']  # Default to java


def infer_build_systems_from_module(module_path: str) -> list:
    """Infer build systems from module files."""
    build_systems = []
    path = Path(module_path)

    if not path.exists():
        return build_systems

    if (path / 'pom.xml').exists():
        build_systems.append('maven')
    if (path / 'build.gradle').exists() or (path / 'build.gradle.kts').exists():
        build_systems.append('gradle')
    if (path / 'package.json').exists():
        build_systems.append('npm')

    return build_systems if build_systems else ['maven']


def cmd_modules(args) -> int:
    """Handle modules noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    modules = config.get('modules', {})

    if args.verb == 'list':
        module_list = []
        for name, mod_config in modules.items():
            module_list.append({
                "name": name,
                "path": mod_config.get("path", name),
                "domains": mod_config.get("domains", []),
                "build_systems": mod_config.get("build_systems", [])
            })
        return success_exit({"modules": module_list, "count": len(module_list)})

    elif args.verb == 'get':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")
        mod_config = modules[module]
        return success_exit({
            "module": module,
            "path": mod_config.get("path", module),
            "domains": mod_config.get("domains", []),
            "build_systems": mod_config.get("build_systems", []),
            "commands": mod_config.get("commands", {})
        })

    elif args.verb == 'get-domains':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")
        domains = modules[module].get("domains", [])
        return success_exit({"module": module, "domains": domains})

    elif args.verb == 'get-build-systems':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")
        build_systems = modules[module].get("build_systems", [])
        return success_exit({"module": module, "build_systems": build_systems})

    elif args.verb == 'get-command':
        module = args.module
        system = args.system
        label = args.label

        if module not in modules:
            return error_exit(f"Unknown module: {module}")

        mod_config = modules[module]

        # Check module-specific override first
        if "commands" in mod_config and system in mod_config["commands"]:
            if label in mod_config["commands"][system]:
                return success_exit({
                    "module": module,
                    "system": system,
                    "label": label,
                    "command": mod_config["commands"][system][label],
                    "source": "module_override"
                })

        # Fall back to project-level build_systems
        build_systems = config.get("build_systems", [])
        for bs in build_systems:
            if bs.get("system") == system:
                commands = bs.get("commands", {})
                if label in commands:
                    return success_exit({
                        "module": module,
                        "system": system,
                        "label": label,
                        "command": commands[label],
                        "source": "project_level"
                    })

        return error_exit(f"Command not found: {system}.{label}")

    elif args.verb == 'add':
        module = args.module
        if module in modules:
            return error_exit(f"Module already exists: {module}")

        path = args.path if args.path else module
        domains = args.domains.split(',') if args.domains else []
        build_systems_list = args.build_systems.split(',') if args.build_systems else []

        modules[module] = {
            "path": path,
            "domains": domains,
            "build_systems": build_systems_list
        }
        config['modules'] = modules
        save_config(config)
        return success_exit({"module": module, "added": modules[module]})

    elif args.verb == 'set':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")

        if args.domains:
            modules[module]["domains"] = args.domains.split(',')
        if args.build_systems:
            modules[module]["build_systems"] = args.build_systems.split(',')

        config['modules'] = modules
        save_config(config)
        return success_exit({"module": module, "updated": modules[module]})

    elif args.verb == 'remove':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")

        removed = modules.pop(module)
        config['modules'] = modules
        save_config(config)
        return success_exit({"module": module, "removed": removed})

    elif args.verb == 'detect':
        detected = []

        # Detect Maven modules
        maven_modules = detect_maven_modules()
        for mod_path in maven_modules:
            mod_name = Path(mod_path).name
            domains = infer_domains_from_module(mod_path)
            build_systems_list = infer_build_systems_from_module(mod_path)

            if mod_name not in modules:
                modules[mod_name] = {
                    "path": mod_path,
                    "domains": domains,
                    "build_systems": build_systems_list
                }
                detected.append(mod_name)

        config['modules'] = modules
        save_config(config)
        return success_exit({
            "detected": detected,
            "count": len(detected),
            "total_modules": len(modules)
        })

    return EXIT_ERROR


# =============================================================================
# build-systems Subcommand
# =============================================================================

def detect_build_systems() -> list:
    """Auto-detect build systems from project files."""
    detected = []
    project_root = Path('.')

    # Maven
    if (project_root / 'pom.xml').exists():
        defaults = BUILD_SYSTEM_DEFAULTS["maven"]
        detected.append({
            "system": "maven",
            "skill": defaults["skill"],
            "commands": defaults["commands"].copy()
        })

    # Gradle
    if (project_root / 'build.gradle').exists() or (project_root / 'build.gradle.kts').exists():
        defaults = BUILD_SYSTEM_DEFAULTS["gradle"]
        detected.append({
            "system": "gradle",
            "skill": defaults["skill"],
            "commands": defaults["commands"].copy()
        })

    # npm
    if (project_root / 'package.json').exists():
        defaults = BUILD_SYSTEM_DEFAULTS["npm"]
        detected.append({
            "system": "npm",
            "skill": defaults["skill"],
            "commands": defaults["commands"].copy()
        })

    return detected


def cmd_build_systems(args) -> int:
    """Handle build-systems noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    build_systems = config.get('build_systems', [])

    if args.verb == 'list':
        systems = [{"system": bs.get("system"), "skill": bs.get("skill")} for bs in build_systems]
        return success_exit({"build_systems": systems, "count": len(systems)})

    elif args.verb == 'get':
        system = args.system
        for bs in build_systems:
            if bs.get("system") == system:
                return success_exit({
                    "system": system,
                    "skill": bs.get("skill"),
                    "commands": bs.get("commands", {})
                })
        return error_exit(f"Build system not found: {system}")

    elif args.verb == 'get-command':
        system = args.system
        label = args.label
        for bs in build_systems:
            if bs.get("system") == system:
                commands = bs.get("commands", {})
                if label in commands:
                    return success_exit({
                        "system": system,
                        "label": label,
                        "command": commands[label],
                        "skill": bs.get("skill")
                    })
                return error_exit(f"Command label not found: {label}")
        return error_exit(f"Build system not found: {system}")

    elif args.verb == 'add':
        system = args.system
        for bs in build_systems:
            if bs.get("system") == system:
                return error_exit(f"Build system already exists: {system}")

        if system in BUILD_SYSTEM_DEFAULTS:
            defaults = BUILD_SYSTEM_DEFAULTS[system]
            new_system = {
                "system": system,
                "skill": defaults["skill"],
                "commands": defaults["commands"].copy()
            }
        else:
            new_system = {
                "system": system,
                "skill": "",
                "commands": {}
            }

        build_systems.append(new_system)
        config['build_systems'] = build_systems
        save_config(config)
        return success_exit({"system": system, "added": new_system})

    elif args.verb == 'remove':
        system = args.system
        original_count = len(build_systems)
        build_systems = [bs for bs in build_systems if bs.get("system") != system]
        if len(build_systems) == original_count:
            return error_exit(f"Build system not found: {system}")
        config['build_systems'] = build_systems
        save_config(config)
        return success_exit({"system": system, "removed": True})

    elif args.verb == 'detect':
        detected = detect_build_systems()
        # Merge with existing (don't overwrite customizations)
        existing_systems = {bs.get("system") for bs in build_systems}
        for new_bs in detected:
            if new_bs["system"] not in existing_systems:
                build_systems.append(new_bs)
        config['build_systems'] = build_systems
        save_config(config)
        detected_names = [bs["system"] for bs in detected]
        return success_exit({
            "detected": detected_names,
            "count": len(detected_names),
            "total": len(build_systems)
        })

    return EXIT_ERROR


# =============================================================================
# system Subcommand
# =============================================================================

def cmd_system(args) -> int:
    """Handle system noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    system_config = config.get('system', {})

    if args.sub_noun == 'retention':
        retention = system_config.get('retention', {})

        if args.verb == 'get':
            return success_exit({
                "retention": retention
            })

        elif args.verb == 'set':
            field = args.field
            value = args.value

            # Type coercion
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)

            retention[field] = value
            system_config['retention'] = retention
            config['system'] = system_config
            save_config(config)
            return success_exit({
                "field": field,
                "value": value
            })

    return EXIT_ERROR


# =============================================================================
# plan Subcommand
# =============================================================================

def cmd_plan(args) -> int:
    """Handle plan noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    plan_config = config.get('plan', {})

    if args.sub_noun == 'defaults':
        defaults = plan_config.get('defaults', {})

        if args.verb == 'list':
            return success_exit({
                "defaults": defaults
            })

        elif args.verb == 'get':
            field = args.field
            if field not in defaults:
                return error_exit(f"Unknown default field: {field}")
            return success_exit({
                "field": field,
                "value": defaults[field]
            })

        elif args.verb == 'set':
            field = args.field
            value = args.value

            # Type coercion
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False

            defaults[field] = value
            plan_config['defaults'] = defaults
            config['plan'] = plan_config
            save_config(config)
            return success_exit({
                "field": field,
                "value": value
            })

    return EXIT_ERROR


# =============================================================================
# init Subcommand
# =============================================================================

def cmd_init(args) -> int:
    """Handle init command."""
    if is_initialized() and not getattr(args, 'force', False):
        return error_exit("marshal.json already exists. Use --force to overwrite.")

    # Copy from template
    if not DEFAULTS_TEMPLATE.exists():
        return error_exit(f"Template not found: {DEFAULTS_TEMPLATE}")

    config = json.loads(DEFAULTS_TEMPLATE.read_text(encoding='utf-8'))

    # Auto-detect build systems
    detected = detect_build_systems()
    if detected:
        config['build_systems'] = detected

    save_config(config)
    return success_exit({
        "created": str(MARSHAL_PATH),
        "build_systems_detected": len(detected)
    })


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Plan-Marshall configuration management',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='noun', help='Noun (resource type)')

    # --- skill-domains ---
    p_sd = subparsers.add_parser('skill-domains', help='Manage implementation skill domains')
    sd_sub = p_sd.add_subparsers(dest='verb', help='Operation')

    sd_sub.add_parser('list', help='List all domains')

    sd_get = sd_sub.add_parser('get', help='Get domain config')
    sd_get.add_argument('--domain', required=True, help='Domain name')

    sd_get_def = sd_sub.add_parser('get-defaults', help='Get domain default skills')
    sd_get_def.add_argument('--domain', required=True, help='Domain name')

    sd_get_opt = sd_sub.add_parser('get-optionals', help='Get domain optional skills')
    sd_get_opt.add_argument('--domain', required=True, help='Domain name')

    sd_set = sd_sub.add_parser('set', help='Set domain config')
    sd_set.add_argument('--domain', required=True, help='Domain name')
    sd_set.add_argument('--defaults', help='Comma-separated default skills')
    sd_set.add_argument('--optionals', help='Comma-separated optional skills')

    sd_add = sd_sub.add_parser('add', help='Add new domain')
    sd_add.add_argument('--domain', required=True, help='Domain name')
    sd_add.add_argument('--defaults', help='Comma-separated default skills')
    sd_add.add_argument('--optionals', help='Comma-separated optional skills')

    sd_val = sd_sub.add_parser('validate', help='Validate skill in domain')
    sd_val.add_argument('--domain', required=True, help='Domain name')
    sd_val.add_argument('--skill', required=True, help='Skill to validate')

    # --- modules ---
    p_mod = subparsers.add_parser('modules', help='Manage project modules')
    mod_sub = p_mod.add_subparsers(dest='verb', help='Operation')

    mod_sub.add_parser('list', help='List all modules')
    mod_sub.add_parser('detect', help='Auto-detect modules')

    mod_get = mod_sub.add_parser('get', help='Get module config')
    mod_get.add_argument('--module', required=True, help='Module name')

    mod_get_dom = mod_sub.add_parser('get-domains', help='Get module domains')
    mod_get_dom.add_argument('--module', required=True, help='Module name')

    mod_get_bs = mod_sub.add_parser('get-build-systems', help='Get module build systems')
    mod_get_bs.add_argument('--module', required=True, help='Module name')

    mod_get_cmd = mod_sub.add_parser('get-command', help='Get command with override resolution')
    mod_get_cmd.add_argument('--module', required=True, help='Module name')
    mod_get_cmd.add_argument('--system', required=True, help='Build system')
    mod_get_cmd.add_argument('--label', required=True, help='Command label')

    mod_add = mod_sub.add_parser('add', help='Add module')
    mod_add.add_argument('--module', required=True, help='Module name')
    mod_add.add_argument('--path', help='Module path')
    mod_add.add_argument('--domains', help='Comma-separated domains')
    mod_add.add_argument('--build-systems', help='Comma-separated build systems')

    mod_set = mod_sub.add_parser('set', help='Update module')
    mod_set.add_argument('--module', required=True, help='Module name')
    mod_set.add_argument('--domains', help='Comma-separated domains')
    mod_set.add_argument('--build-systems', help='Comma-separated build systems')

    mod_rem = mod_sub.add_parser('remove', help='Remove module')
    mod_rem.add_argument('--module', required=True, help='Module name')

    # --- build-systems ---
    p_bs = subparsers.add_parser('build-systems', help='Manage build system configuration')
    bs_sub = p_bs.add_subparsers(dest='verb', help='Operation')

    bs_sub.add_parser('list', help='List build systems')
    bs_sub.add_parser('detect', help='Auto-detect build systems')

    bs_get = bs_sub.add_parser('get', help='Get build system config')
    bs_get.add_argument('--system', required=True, help='Build system name')

    bs_get_cmd = bs_sub.add_parser('get-command', help='Get command for label')
    bs_get_cmd.add_argument('--system', required=True, help='Build system name')
    bs_get_cmd.add_argument('--label', required=True, help='Command label')

    bs_add = bs_sub.add_parser('add', help='Add build system')
    bs_add.add_argument('--system', required=True, help='Build system name')

    bs_rem = bs_sub.add_parser('remove', help='Remove build system')
    bs_rem.add_argument('--system', required=True, help='Build system name')

    # --- system ---
    p_sys = subparsers.add_parser('system', help='Manage system settings')
    sys_sub = p_sys.add_subparsers(dest='sub_noun', help='Sub-noun')

    p_ret = sys_sub.add_parser('retention', help='Manage retention settings')
    ret_sub = p_ret.add_subparsers(dest='verb', help='Operation')

    ret_sub.add_parser('get', help='Get retention settings')

    ret_set = ret_sub.add_parser('set', help='Set retention field')
    ret_set.add_argument('--field', required=True, help='Field name')
    ret_set.add_argument('--value', required=True, help='Field value')

    # --- plan ---
    p_plan = subparsers.add_parser('plan', help='Manage plan settings')
    plan_sub = p_plan.add_subparsers(dest='sub_noun', help='Sub-noun')

    p_def = plan_sub.add_parser('defaults', help='Manage plan defaults')
    def_sub = p_def.add_subparsers(dest='verb', help='Operation')

    def_sub.add_parser('list', help='List all plan defaults')

    def_get = def_sub.add_parser('get', help='Get default value')
    def_get.add_argument('--field', required=True, help='Field name')

    def_set = def_sub.add_parser('set', help='Set default value')
    def_set.add_argument('--field', required=True, help='Field name')
    def_set.add_argument('--value', required=True, help='Field value')

    # --- init ---
    p_init = subparsers.add_parser('init', help='Initialize marshal.json')
    p_init.add_argument('--force', action='store_true', help='Overwrite existing')

    args = parser.parse_args()

    if args.noun is None:
        parser.print_help()
        return EXIT_ERROR

    # Route to handler
    if args.noun == 'skill-domains':
        if not args.verb:
            p_sd.print_help()
            return EXIT_ERROR
        return cmd_skill_domains(args)
    elif args.noun == 'modules':
        if not args.verb:
            p_mod.print_help()
            return EXIT_ERROR
        return cmd_modules(args)
    elif args.noun == 'build-systems':
        if not args.verb:
            p_bs.print_help()
            return EXIT_ERROR
        return cmd_build_systems(args)
    elif args.noun == 'system':
        if not args.sub_noun or not args.verb:
            p_sys.print_help()
            return EXIT_ERROR
        return cmd_system(args)
    elif args.noun == 'plan':
        if not args.sub_noun or not args.verb:
            p_plan.print_help()
            return EXIT_ERROR
        return cmd_plan(args)
    elif args.noun == 'init':
        return cmd_init(args)
    else:
        parser.print_help()
        return EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())
