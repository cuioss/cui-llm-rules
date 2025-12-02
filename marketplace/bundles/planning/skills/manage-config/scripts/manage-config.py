#!/usr/bin/env python3
"""
Manage config.toon files with schema validation and field-level access.

Provides typed configuration for plan execution with enum validation.

Usage:
    python3 manage-config.py read --plan-id my-plan
    python3 manage-config.py get --plan-id my-plan --field plan_type
    python3 manage-config.py set --plan-id my-plan --field plan_type --value java
    python3 manage-config.py create --plan-id my-plan --plan-type implementation --technology java
"""

import argparse
import re
import sys
from pathlib import Path

# Add parent paths for imports
script_dir = Path(__file__).parent
BUNDLES_DIR = script_dir.parent.parent.parent.parent  # .../bundles/
sys.path.insert(0, str(BUNDLES_DIR / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'))
sys.path.insert(0, str(BUNDLES_DIR / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'))

from file_ops import atomic_write_file, base_path
from toon_parser import parse_toon, serialize_toon

# Schema validation
SCHEMA = {
    'plan_type': ['implementation', 'plugin-development', 'simple'],
    'technology': ['java', 'javascript', 'plugin', 'mixed'],
    'build_system': ['maven', 'gradle', 'npm', 'none'],
    'compatibility': ['deprecations', 'breaking'],
    'commit_strategy': ['fine-granular', 'phase-specific', 'complete'],
    'finalizing': ['pr-workflow', 'commit-only'],
}

DEFAULTS = {
    'compatibility': 'deprecations',
    'commit_strategy': 'phase-specific',
    'finalizing': 'pr-workflow',
}


def validate_plan_id(plan_id: str) -> bool:
    """Validate plan_id is kebab-case with no special characters."""
    return bool(re.match(r'^[a-z][a-z0-9-]*$', plan_id))


def get_config_path(plan_id: str) -> Path:
    """Get the config.toon file path."""
    return base_path('plans', plan_id, 'config.toon')


def read_config(plan_id: str) -> dict:
    """Read config.toon for a plan."""
    path = get_config_path(plan_id)
    if not path.exists():
        return {}
    return parse_toon(path.read_text(encoding='utf-8'))


def write_config(plan_id: str, config: dict):
    """Write config.toon for a plan."""
    path = get_config_path(plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "# Plan Configuration\n\n" + serialize_toon(config)
    atomic_write_file(path, content)


def validate_field(field: str, value: str) -> tuple[bool, list]:
    """Validate a field value against schema."""
    if field not in SCHEMA:
        return True, []  # Unknown fields are allowed
    valid_values = SCHEMA[field]
    return value in valid_values, valid_values


def output_toon(data: dict):
    """Output TOON format to stdout."""
    print(serialize_toon(data))


def cmd_read(args):
    """Read entire config.toon."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    config = read_config(args.plan_id)
    if not config:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'file_not_found',
            'message': 'config.toon not found'
        })
        sys.exit(1)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'config': config
    })


def cmd_get(args):
    """Get a specific field value."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    config = read_config(args.plan_id)
    if not config:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'file_not_found',
            'message': 'config.toon not found'
        })
        sys.exit(1)

    value = config.get(args.field)
    if value is None:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'field': args.field,
            'error': 'field_not_found',
            'message': f"Field '{args.field}' not found in config"
        })
        sys.exit(1)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'field': args.field,
        'value': value
    })


def cmd_set(args):
    """Set a specific field value."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    # Validate value against schema
    is_valid, valid_values = validate_field(args.field, args.value)
    if not is_valid:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'field': args.field,
            'error': 'invalid_value',
            'message': f"Invalid value '{args.value}' for field '{args.field}'",
            'valid_values': valid_values
        })
        sys.exit(1)

    config = read_config(args.plan_id)
    previous = config.get(args.field)
    config[args.field] = args.value
    write_config(args.plan_id, config)

    result = {
        'status': 'success',
        'plan_id': args.plan_id,
        'field': args.field,
        'value': args.value
    }
    if previous is not None:
        result['previous'] = previous
    output_toon(result)


def cmd_create(args):
    """Create config.toon with initial values."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    # Check if already exists
    path = get_config_path(args.plan_id)
    if path.exists() and not args.force:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'file_exists',
            'message': 'config.toon already exists. Use --force to overwrite.'
        })
        sys.exit(1)

    # Build config from args
    config = {
        'plan_type': args.plan_type,
        'technology': args.technology,
        'build_system': args.build_system,
        'compatibility': args.compatibility or DEFAULTS['compatibility'],
        'commit_strategy': args.commit_strategy or DEFAULTS['commit_strategy'],
        'finalizing': args.finalizing or DEFAULTS['finalizing'],
    }

    # Validate all fields
    for field, value in config.items():
        is_valid, valid_values = validate_field(field, value)
        if not is_valid:
            output_toon({
                'status': 'error',
                'plan_id': args.plan_id,
                'field': field,
                'error': 'invalid_value',
                'message': f"Invalid value '{value}' for field '{field}'",
                'valid_values': valid_values
            })
            sys.exit(1)

    write_config(args.plan_id, config)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': 'config.toon',
        'created': True,
        'config': config
    })


def main():
    parser = argparse.ArgumentParser(
        description='Manage config.toon files with schema validation'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # read
    read_parser = subparsers.add_parser('read', help='Read entire config')
    read_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    read_parser.set_defaults(func=cmd_read)

    # get
    get_parser = subparsers.add_parser('get', help='Get specific field')
    get_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    get_parser.add_argument('--field', required=True, help='Field name')
    get_parser.set_defaults(func=cmd_get)

    # set
    set_parser = subparsers.add_parser('set', help='Set specific field')
    set_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    set_parser.add_argument('--field', required=True, help='Field name')
    set_parser.add_argument('--value', required=True, help='Field value')
    set_parser.set_defaults(func=cmd_set)

    # create
    create_parser = subparsers.add_parser('create', help='Create config.toon')
    create_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    create_parser.add_argument('--plan-type', required=True,
                               choices=['implementation', 'plugin-development', 'simple'],
                               help='Plan type')
    create_parser.add_argument('--technology', required=True,
                               choices=['java', 'javascript', 'plugin', 'mixed'],
                               help='Primary technology')
    create_parser.add_argument('--build-system', required=True,
                               choices=['maven', 'gradle', 'npm', 'none'],
                               help='Build system')
    create_parser.add_argument('--compatibility',
                               choices=['deprecations', 'breaking'],
                               help='Compatibility strategy')
    create_parser.add_argument('--commit-strategy',
                               choices=['fine-granular', 'phase-specific', 'complete'],
                               help='Commit strategy')
    create_parser.add_argument('--finalizing',
                               choices=['pr-workflow', 'commit-only'],
                               help='Finalization method')
    create_parser.add_argument('--force', action='store_true',
                               help='Overwrite existing config')
    create_parser.set_defaults(func=cmd_create)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
