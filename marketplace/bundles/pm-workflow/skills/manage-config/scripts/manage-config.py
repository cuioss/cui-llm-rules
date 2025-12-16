#!/usr/bin/env python3
"""
Manage config.toon files with schema validation and field-level access.

Provides typed configuration for plan execution with enum validation.
Supports domain-based workflow skills configuration.

Usage:
    python3 manage-config.py read --plan-id my-plan
    python3 manage-config.py get --plan-id my-plan --field commit_strategy
    python3 manage-config.py get --plan-id my-plan --field workflow_skills.java.implementation
    python3 manage-config.py set --plan-id my-plan --field commit_strategy --value per_task
    python3 manage-config.py create --plan-id my-plan --domains java --workflow-skills '{"java":{...}}'
    python3 manage-config.py get-workflow-skill --plan-id my-plan --domain java --profile implementation
    python3 manage-config.py get-domains --plan-id my-plan
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Add parent paths for imports
script_dir = Path(__file__).parent
BUNDLES_DIR = script_dir.parent.parent.parent.parent  # .../bundles/
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'file-operations-base' / 'scripts'))
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'toon-usage' / 'scripts'))
sys.path.insert(0, str(BUNDLES_DIR / 'plan-marshall' / 'skills' / 'plan-marshall-config' / 'scripts'))

from file_ops import atomic_write_file, base_path
from toon_parser import parse_toon, serialize_toon
from config_core import is_initialized, load_config

# Schema validation - enum fields
SCHEMA = {
    'commit_strategy': ['per_task', 'per_plan', 'none'],
    'branch_strategy': ['feature', 'direct'],
}

# Structural validation (not enum)
REQUIRED_FIELDS = ['domains', 'workflow_skills', 'commit_strategy']
OPTIONAL_FIELDS = ['create_pr', 'verification_required', 'verification_command', 'branch_strategy']

# Fallback defaults (used when marshal.json doesn't exist)
FALLBACK_DEFAULTS = {
    'commit_strategy': 'per_task',
    'create_pr': True,
    'verification_required': True,
    'branch_strategy': 'feature',
}


def get_defaults() -> dict:
    """Get plan defaults from marshal.json, falling back to hardcoded defaults.

    Reads from .plan/marshal.json -> plan.defaults if available.
    Returns FALLBACK_DEFAULTS if marshal.json doesn't exist or lacks plan.defaults.
    """
    if not is_initialized():
        return FALLBACK_DEFAULTS.copy()

    try:
        marshal_config = load_config()
        plan_defaults = marshal_config.get('plan', {}).get('defaults', {})

        # Merge: marshal.json values override fallback defaults
        result = FALLBACK_DEFAULTS.copy()
        for key in FALLBACK_DEFAULTS:
            if key in plan_defaults:
                result[key] = plan_defaults[key]
        return result
    except Exception:
        return FALLBACK_DEFAULTS.copy()


def validate_plan_id(plan_id: str) -> bool:
    """Validate plan_id is kebab-case with no special characters."""
    return bool(re.match(r'^[a-z][a-z0-9-]*$', plan_id))


def validate_domain(domain: str) -> bool:
    """Validate domain is a simple lowercase identifier.

    Examples of valid domains: java, javascript, plugin
    """
    return bool(re.match(r'^[a-z][a-z0-9]*$', domain))


def validate_workflow_skill(skill: str) -> bool:
    """Validate workflow skill is in bundle:skill notation.

    Examples: pm-workflow:solution-outline, pm-dev-java:java-implement-agent
    """
    return bool(re.match(r'^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$', skill))


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

    For enum fields, validates against allowed values.
    For other fields, allows any value.
    """
    if field not in SCHEMA:
        return True, []  # Unknown fields are allowed
    valid_values = SCHEMA[field]
    return value in valid_values, valid_values


def get_nested_value(config: dict, field_path: str):
    """Get a nested value using dot notation.

    Args:
        config: Configuration dictionary
        field_path: Dot-separated path (e.g., 'workflow_skills.java.implementation')

    Returns:
        Value at path, or None if not found
    """
    parts = field_path.split('.')
    current = config
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


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
    """Get a specific field value.

    Supports nested field access via dot notation (e.g., workflow_skills.java.implementation).
    """
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

    # Support nested field access via dot notation
    if '.' in args.field:
        value = get_nested_value(config, args.field)
    else:
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

    # Validate value against schema for enum fields
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
    """Create config.toon with domains and workflow_skills configuration."""
    if not validate_plan_id(args.plan_id):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_plan_id',
            'message': f"Invalid plan_id format: {args.plan_id}"
        })
        sys.exit(1)

    # Parse and validate domains
    domains = [d.strip() for d in args.domains.split(',') if d.strip()]
    if not domains:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_domains',
            'message': 'At least one domain is required'
        })
        sys.exit(1)

    for domain in domains:
        if not validate_domain(domain):
            output_toon({
                'status': 'error',
                'plan_id': args.plan_id,
                'error': 'invalid_domain',
                'message': f"Invalid domain format: {domain}. Must be lowercase identifier (e.g., java, javascript, plugin)"
            })
            sys.exit(1)

    # Parse and validate workflow_skills JSON
    try:
        workflow_skills = json.loads(args.workflow_skills)
    except json.JSONDecodeError as e:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_workflow_skills',
            'message': f"Invalid workflow_skills JSON: {e}"
        })
        sys.exit(1)

    if not isinstance(workflow_skills, dict):
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'error': 'invalid_workflow_skills',
            'message': 'workflow_skills must be a JSON object'
        })
        sys.exit(1)

    # Validate workflow_skills structure matches domains
    for domain in domains:
        if domain not in workflow_skills:
            output_toon({
                'status': 'error',
                'plan_id': args.plan_id,
                'error': 'missing_domain_skills',
                'message': f"workflow_skills missing entry for domain: {domain}"
            })
            sys.exit(1)

        domain_skills = workflow_skills[domain]
        if not isinstance(domain_skills, dict):
            output_toon({
                'status': 'error',
                'plan_id': args.plan_id,
                'error': 'invalid_domain_skills',
                'message': f"workflow_skills.{domain} must be an object"
            })
            sys.exit(1)

        # Validate each skill in the domain is bundle:skill notation
        for profile, skill in domain_skills.items():
            if not validate_workflow_skill(skill):
                output_toon({
                    'status': 'error',
                    'plan_id': args.plan_id,
                    'error': 'invalid_workflow_skill',
                    'message': f"Invalid workflow skill format: {skill}. Must be bundle:skill notation"
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

    # Get defaults from marshal.json (falls back to hardcoded if not available)
    defaults = get_defaults()

    # Build config with required fields
    commit_strategy = args.commit_strategy or defaults['commit_strategy']
    is_valid, valid_values = validate_field('commit_strategy', commit_strategy)
    if not is_valid:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'field': 'commit_strategy',
            'error': 'invalid_value',
            'message': f"Invalid value '{commit_strategy}' for commit_strategy",
            'valid_values': valid_values
        })
        sys.exit(1)

    config = {
        'domains': domains,
        'workflow_skills': workflow_skills,
        'commit_strategy': commit_strategy,
    }

    # Add optional finalize settings with defaults from marshal.json
    if args.create_pr is not None:
        config['create_pr'] = args.create_pr.lower() == 'true'
    else:
        config['create_pr'] = defaults['create_pr']

    if args.verification_required is not None:
        config['verification_required'] = args.verification_required.lower() == 'true'
    else:
        config['verification_required'] = defaults['verification_required']

    if args.verification_command:
        config['verification_command'] = args.verification_command

    branch_strategy = args.branch_strategy or defaults['branch_strategy']
    is_valid, valid_values = validate_field('branch_strategy', branch_strategy)
    if not is_valid:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'field': 'branch_strategy',
            'error': 'invalid_value',
            'message': f"Invalid value '{branch_strategy}' for branch_strategy",
            'valid_values': valid_values
        })
        sys.exit(1)
    config['branch_strategy'] = branch_strategy

    write_config(args.plan_id, config)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'file': 'config.toon',
        'created': True,
        'domains_count': len(domains),
        'config': config
    })


def cmd_get_workflow_skill(args):
    """Get workflow skill for a specific domain and profile."""
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

    # Check if domain exists in config.domains
    domains = config.get('domains', [])
    if args.domain not in domains:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'domain': args.domain,
            'error': 'domain_not_found',
            'message': f"Domain '{args.domain}' not found in config.domains",
            'available_domains': domains
        })
        sys.exit(1)

    # Check if workflow_skills exists and has the domain
    workflow_skills = config.get('workflow_skills', {})
    if args.domain not in workflow_skills:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'domain': args.domain,
            'error': 'domain_not_found',
            'message': f"Domain '{args.domain}' not found in workflow_skills"
        })
        sys.exit(1)

    domain_skills = workflow_skills[args.domain]
    if args.profile not in domain_skills:
        output_toon({
            'status': 'error',
            'plan_id': args.plan_id,
            'domain': args.domain,
            'profile': args.profile,
            'error': 'profile_not_found',
            'message': f"Profile '{args.profile}' not found in workflow_skills.{args.domain}",
            'available_profiles': list(domain_skills.keys())
        })
        sys.exit(1)

    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'domain': args.domain,
        'profile': args.profile,
        'workflow_skill': domain_skills[args.profile]
    })


def cmd_get_domains(args):
    """Get the domains array from config.toon."""
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

    domains = config.get('domains', [])
    output_toon({
        'status': 'success',
        'plan_id': args.plan_id,
        'domains': domains,
        'count': len(domains)
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

    # get (supports nested field access via dot notation)
    get_parser = subparsers.add_parser('get', help='Get specific field (supports dot notation)')
    get_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    get_parser.add_argument('--field', required=True,
                            help='Field name (supports dot notation: workflow_skills.java.implementation)')
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
                                  help='Comma-separated field names (e.g., commit_strategy,branch_strategy)')
    get_multi_parser.set_defaults(func=cmd_get_multi)

    # create (new format with domains and workflow_skills)
    create_parser = subparsers.add_parser('create', help='Create config.toon')
    create_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    create_parser.add_argument('--domains', required=True,
                               help='Comma-separated list of domains (e.g., java or java,javascript)')
    create_parser.add_argument('--workflow-skills', required=True,
                               help='JSON object mapping domains to workflow skills')
    create_parser.add_argument('--commit-strategy',
                               choices=['per_task', 'per_plan', 'none'],
                               help='Commit strategy (default: per_task, none=no commits)')
    create_parser.add_argument('--create-pr',
                               help='Create PR on finalize (default: true)')
    create_parser.add_argument('--verification-required',
                               help='Require verification (default: true)')
    create_parser.add_argument('--verification-command',
                               help='Verification command to run')
    create_parser.add_argument('--branch-strategy',
                               choices=['feature', 'direct'],
                               help='Branch strategy (default: feature)')
    create_parser.add_argument('--force', action='store_true',
                               help='Overwrite existing config')
    create_parser.set_defaults(func=cmd_create)

    # get-workflow-skill
    gws_parser = subparsers.add_parser('get-workflow-skill',
                                        help='Get workflow skill for domain and profile')
    gws_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    gws_parser.add_argument('--domain', required=True,
                            help='Domain name (e.g., java, javascript, plugin)')
    gws_parser.add_argument('--profile', required=True,
                            help='Profile name (e.g., implementation, testing)')
    gws_parser.set_defaults(func=cmd_get_workflow_skill)

    # get-domains
    gd_parser = subparsers.add_parser('get-domains', help='Get domains array from config')
    gd_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    gd_parser.set_defaults(func=cmd_get_domains)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
