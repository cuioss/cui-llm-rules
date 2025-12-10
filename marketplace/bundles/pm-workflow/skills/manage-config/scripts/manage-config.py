#!/usr/bin/env python3
"""
Manage config.toon files with schema validation and field-level access.

Provides typed configuration for plan execution with enum validation.

Usage:
    python3 manage-config.py read --plan-id my-plan
    python3 manage-config.py get --plan-id my-plan --field plan_type
    python3 manage-config.py set --plan-id my-plan --field plan_type --value pm-workflow:plan-type-java
    python3 manage-config.py create --plan-id my-plan --plan-type pm-workflow:plan-type-java
"""

import argparse
import re
import sys
from pathlib import Path

# Add parent paths for imports
script_dir = Path(__file__).parent
BUNDLES_DIR = script_dir.parent.parent.parent.parent  # .../bundles/
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'file-operations-base' / 'scripts'))
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'))

from file_ops import atomic_write_file, base_path
from toon_parser import parse_toon, serialize_toon

# Schema validation - simplified to 2 enum fields
# plan_type uses bundle:skill notation and is validated separately
SCHEMA = {
    'compatibility': ['deprecations', 'breaking'],
    'commit_strategy': ['fine-granular', 'phase-specific', 'complete'],
}

DEFAULTS = {
    'compatibility': 'deprecations',
    'commit_strategy': 'phase-specific',
}


def validate_plan_id(plan_id: str) -> bool:
    """Validate plan_id is kebab-case with no special characters."""
    return bool(re.match(r'^[a-z][a-z0-9-]*$', plan_id))


def validate_plan_type(plan_type: str) -> bool:
    """Validate plan_type is in bundle:skill notation.

    Examples of valid plan types:
    - pm-workflow:plan-type-java
    - pm-workflow:plan-type-javascript
    - pm-workflow:plan-type-generic
    - pm-workflow:plan-type-plugin
    """
    # Pattern: bundle-name:skill-name (both kebab-case)
    return bool(re.match(r'^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$', plan_type))


def validate_plan_type_exists(plan_type: str) -> tuple[bool, str | None]:
    """Validate that the plan_type skill actually exists.

    Args:
        plan_type: Plan type in bundle:skill notation (e.g., pm-workflow:plan-type-java)

    Returns:
        Tuple of (exists, skill_path). If exists is False, skill_path is None.
    """
    if not validate_plan_type(plan_type):
        return False, None

    bundle, skill = plan_type.split(':')
    skill_path = BUNDLES_DIR / bundle / 'skills' / skill / 'SKILL.md'
    if skill_path.exists():
        return True, str(skill_path)
    return False, None


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
    """Validate a field value against schema.

    For plan_type, validates bundle:skill notation.
    For other fields, validates against enum values.
    """
    if field == 'plan_type':
        # plan_type uses bundle:skill notation
        return validate_plan_type(value), []
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
        error_data = {
            'status': 'error',
            'plan_id': args.plan_id,
            'field': args.field,
            'error': 'invalid_value',
        }
        if args.field == 'plan_type':
            error_data['message'] = f"Invalid plan_type format: {args.value}. Must be bundle:skill notation (e.g., pm-workflow:plan-type-java)"
        else:
            error_data['message'] = f"Invalid value '{args.value}' for field '{args.field}'"
            error_data['valid_values'] = valid_values
        output_toon(error_data)
        sys.exit(1)

    # For plan_type, also validate skill exists
    if args.field == 'plan_type':
        exists, _ = validate_plan_type_exists(args.value)
        if not exists:
            output_toon({
                'status': 'error',
                'plan_id': args.plan_id,
                'field': args.field,
                'error': 'skill_not_found',
                'message': f"Skill not found for plan_type: {args.value}. Expected SKILL.md at bundles/{args.value.replace(':', '/skills/')}/SKILL.md"
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


def cmd_get_multi(args):
    """Get multiple fields in one call."""
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

    # Parse requested fields
    fields = [f.strip() for f in args.fields.split(',') if f.strip()]

    result = {
        'status': 'success',
        'plan_id': args.plan_id
    }

    # Add requested fields to result (only if they exist)
    for field in fields:
        if field in config:
            result[field] = config[field]

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

    # Validate plan_type format (bundle:skill notation)
    if not validate_plan_type(args.plan_type):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_type',
            'message': f"Invalid plan_type format: {args.plan_type}. Must be bundle:skill notation (e.g., pm-workflow:plan-type-java)"
        })
        sys.exit(1)

    # Validate plan_type skill exists
    exists, _ = validate_plan_type_exists(args.plan_type)
    if not exists:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'skill_not_found',
            'message': f"Skill not found for plan_type: {args.plan_type}. Expected SKILL.md at bundles/{args.plan_type.replace(':', '/skills/')}/SKILL.md"
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

    # Build config from args (simplified to 3 fields)
    config = {
        'plan_type': args.plan_type,
        'compatibility': args.compatibility or DEFAULTS['compatibility'],
        'commit_strategy': args.commit_strategy or DEFAULTS['commit_strategy'],
    }

    # Validate enum fields (plan_type already validated above)
    for field in ['compatibility', 'commit_strategy']:
        value = config[field]
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

    # get-multi
    get_multi_parser = subparsers.add_parser('get-multi', help='Get multiple fields in one call')
    get_multi_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    get_multi_parser.add_argument('--fields', required=True,
                                  help='Comma-separated field names (e.g., plan_type,compatibility)')
    get_multi_parser.set_defaults(func=cmd_get_multi)

    # create (simplified to 3 fields)
    create_parser = subparsers.add_parser('create', help='Create config.toon')
    create_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    create_parser.add_argument('--plan-type', required=True,
                               help='Plan type in bundle:skill notation (e.g., pm-workflow:plan-type-java)')
    create_parser.add_argument('--compatibility',
                               choices=['deprecations', 'breaking'],
                               help='Compatibility strategy (default: deprecations)')
    create_parser.add_argument('--commit-strategy',
                               choices=['fine-granular', 'phase-specific', 'complete'],
                               help='Commit strategy (default: phase-specific)')
    create_parser.add_argument('--force', action='store_true',
                               help='Overwrite existing config')
    create_parser.set_defaults(func=cmd_create)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
