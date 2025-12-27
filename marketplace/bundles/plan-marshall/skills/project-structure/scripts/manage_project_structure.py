#!/usr/bin/env python3
"""
Manage project structure knowledge in .plan/project-structure.toon.

Provides operations for reading, generating, and updating project structure
metadata including module responsibilities, placement rules, and conventions.
"""

import argparse
import json
import os
import sys
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


def infer_layer_from_module(name: str, module_type: str = None) -> str:
    """Infer architectural layer from module name and type.

    Heuristics:
    - *-ui, *-frontend, *-web -> presentation
    - *-api -> api
    - *-service, *-core -> service
    - *-test*, integration-*, e2e-* -> testing
    - *-nar, *-assembly, *-dist -> packaging
    - Otherwise -> extension
    """
    name_lower = name.lower()

    if any(suffix in name_lower for suffix in ['-ui', '-frontend', '-web', 'webapp']):
        return 'presentation'
    if '-api' in name_lower:
        return 'api'
    if any(suffix in name_lower for suffix in ['-service', '-core']):
        return 'service'
    if any(prefix in name_lower for prefix in ['test', 'integration', 'e2e', 'e-2-e']):
        return 'testing'
    if any(suffix in name_lower for suffix in ['-nar', '-assembly', '-dist', '-package']):
        return 'packaging'

    return 'extension'


def generate_structure_from_marshal() -> dict:
    """Generate project-structure.toon from marshal.json modules."""
    marshal = load_marshal()
    modules_config = marshal.get('modules', {})

    structure = {
        'modules': {},
        'dependencies': {
            'module_deps': {},
            'layer_rules': {
                'presentation': {'allowed': ['extension', 'service', 'api'], 'forbidden': ['testing', 'packaging']},
                'extension': {'allowed': ['api', 'service'], 'forbidden': ['presentation', 'testing']},
                'service': {'allowed': ['api'], 'forbidden': ['presentation', 'testing', 'packaging']},
                'api': {'allowed': [], 'forbidden': ['presentation', 'testing', 'packaging', 'service']},
                'packaging': {'allowed': ['extension', 'presentation', 'service'], 'forbidden': ['testing']},
                'testing': {'allowed': ['packaging', 'extension', 'presentation', 'service', 'api'], 'forbidden': []}
            }
        },
        'placement': {},
        'conventions': {
            'naming': [],
            'packages': [],
            'testing': [],
            'documentation': []
        }
    }

    for module_name, module_config in modules_config.items():
        if module_name == 'default':
            continue  # Skip default module template

        build_systems = module_config.get('build_systems', [])
        domains = infer_domains_from_build_systems(build_systems)
        layer = infer_layer_from_module(module_name, module_config.get('type'))

        structure['modules'][module_name] = {
            'responsibility': '',  # To be filled by user
            'layer': layer,
            'technology': {
                'framework': '',
                'di': 'none',
                'testing': 'junit5' if 'java' in domains else 'jest' if 'javascript' in domains else ''
            },
            'key_packages': [],
            'tips': [],
            'insights': [],
            'best_practices': []
        }

    return structure


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
            except MarshalNotFoundError as e:
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
    except MarshalNotFoundError as e:
        return error_exit(str(e))
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
