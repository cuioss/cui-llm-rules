#!/usr/bin/env python3
"""
Marshal configuration management for project-level planning settings.

Manages .plan/marshal.json with noun-verb subcommand pattern.

Usage:
    marshal-config.py domain-agents get --plan-type pm-workflow:plan-type-java
    marshal-config.py domain-agents set --plan-type pm-workflow:plan-type-java --solution-outline-agent ...
    marshal-config.py defaults get --field verification_required
    marshal-config.py defaults set --field create_pr --value true
    marshal-config.py rules match --file src/main/java/Foo.java
    marshal-config.py init
"""

import argparse
import fnmatch
import json
import os
import re
import sys
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


class MarshalNotInitializedError(Exception):
    """Raised when marshal.json doesn't exist and operation requires it."""
    pass


def is_initialized() -> bool:
    """Check if marshal.json exists (exception-free for init use case)."""
    return MARSHAL_PATH.exists()


def require_initialized() -> None:
    """Raise exception if marshal.json doesn't exist."""
    if not PLAN_BASE_DIR.exists():
        raise MarshalNotInitializedError(
            f"Directory '{PLAN_BASE_DIR}' does not exist. Run /plan-marshall first."
        )
    if not MARSHAL_PATH.exists():
        raise MarshalNotInitializedError(
            f"File '{MARSHAL_PATH}' does not exist. Run /plan-marshall first."
        )


# Hardcoded defaults when marshal.json is missing
DEFAULTS = {
    "plan_type_rules": [
        {"pattern": "*", "plan_type": "pm-workflow:plan-type-generic", "description": "Default"}
    ],
    "domain_agents": {
        "pm-workflow:plan-type-generic": {"solution_outline_agent": None, "task_plan_agent": None}
    },
    "defaults": {
        "create_pr": False,
        "verification_required": True,
        "branch_strategy": "direct"
    },
    "plan_type_defaults": {},
    "custom_plan_types": [],
    "detection_keywords": {},
    "build_systems": [],
    "state": {}
}


# =============================================================================
# Core Functions
# =============================================================================

def load_config() -> dict:
    """Load marshal.json. Assumes require_initialized() was called first."""
    if MARSHAL_PATH.exists():
        try:
            return json.loads(MARSHAL_PATH.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            return DEFAULTS.copy()
    # For init command which doesn't call require_initialized
    return DEFAULTS.copy()


def save_config(config: dict) -> None:
    """Save config to marshal.json."""
    MARSHAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARSHAL_PATH.write_text(json.dumps(config, indent=2), encoding='utf-8')


def output(data: dict) -> None:
    """Output TOON result to stdout for token efficiency."""
    print(serialize_toon(data))


def error_response(message: str, **extra) -> dict:
    """Create error response."""
    return {"status": "error", "error": message, **extra}


def success_response(data: dict) -> dict:
    """Create success response."""
    return {"status": "success", "data": data}


# =============================================================================
# domain-agents Subcommand
# =============================================================================

def cmd_domain_agents(args) -> int:
    """Handle domain-agents noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    domain_agents = config.get('domain_agents', {})

    if args.verb == 'get':
        plan_type = args.plan_type
        if plan_type not in domain_agents:
            output(error_response(f"Unknown plan-type: {plan_type}"))
            return EXIT_ERROR
        output(success_response(domain_agents[plan_type]))
        return EXIT_SUCCESS

    elif args.verb == 'set':
        plan_type = args.plan_type
        if plan_type not in domain_agents:
            domain_agents[plan_type] = {"solution_outline_agent": None, "task_plan_agent": None}

        if args.solution_outline_agent:
            domain_agents[plan_type]["solution_outline_agent"] = args.solution_outline_agent if args.solution_outline_agent != 'null' else None
        if args.task_plan_agent:
            domain_agents[plan_type]["task_plan_agent"] = args.task_plan_agent if args.task_plan_agent != 'null' else None

        config['domain_agents'] = domain_agents
        save_config(config)
        output(success_response({"plan_type": plan_type, "updated": domain_agents[plan_type]}))
        return EXIT_SUCCESS

    elif args.verb == 'list':
        output(success_response(domain_agents))
        return EXIT_SUCCESS

    return EXIT_ERROR


# =============================================================================
# defaults Subcommand
# =============================================================================

def cmd_defaults(args) -> int:
    """Handle defaults noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    defaults = config.get('defaults', DEFAULTS['defaults'].copy())

    if args.verb == 'get':
        field = args.field
        if field not in defaults:
            output(error_response(f"Unknown field: {field}"))
            return EXIT_ERROR
        output(success_response({field: defaults[field]}))
        return EXIT_SUCCESS

    elif args.verb == 'set':
        field = args.field
        value = args.value
        # Type coercion for boolean
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        defaults[field] = value
        config['defaults'] = defaults
        save_config(config)
        output(success_response({field: value}))
        return EXIT_SUCCESS

    elif args.verb == 'list':
        output(success_response(defaults))
        return EXIT_SUCCESS

    return EXIT_ERROR


# =============================================================================
# plan-type-defaults Subcommand
# =============================================================================

def cmd_plan_type_defaults(args) -> int:
    """Handle plan-type-defaults noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    pt_defaults = config.get('plan_type_defaults', {})

    if args.verb == 'get':
        plan_type = args.plan_type
        if plan_type not in pt_defaults:
            output(success_response({}))  # Empty defaults is valid
            return EXIT_SUCCESS
        output(success_response(pt_defaults[plan_type]))
        return EXIT_SUCCESS

    elif args.verb == 'set':
        plan_type = args.plan_type
        if plan_type not in pt_defaults:
            pt_defaults[plan_type] = {}
        if args.verification_command:
            pt_defaults[plan_type]['verification_command'] = args.verification_command
        if args.pr_workflow is not None:
            pt_defaults[plan_type]['pr_workflow'] = args.pr_workflow.lower() == 'true'
        config['plan_type_defaults'] = pt_defaults
        save_config(config)
        output(success_response({"plan_type": plan_type, "updated": pt_defaults[plan_type]}))
        return EXIT_SUCCESS

    return EXIT_ERROR


# =============================================================================
# rules Subcommand
# =============================================================================

def match_pattern(pattern: str, filepath: str) -> bool:
    """Match file against glob pattern. Supports | for OR."""
    patterns = pattern.split('|')
    for p in patterns:
        p = p.strip()
        if fnmatch.fnmatch(filepath, p):
            return True
        # Also check basename for simple patterns
        if fnmatch.fnmatch(Path(filepath).name, p):
            return True
    return False


def cmd_rules(args) -> int:
    """Handle rules noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    rules = config.get('plan_type_rules', DEFAULTS['plan_type_rules'].copy())

    if args.verb == 'match':
        filepath = args.file
        for rule in rules:
            if match_pattern(rule['pattern'], filepath):
                output(success_response({
                    "plan_type": rule['plan_type'],
                    "pattern": rule['pattern'],
                    "description": rule.get('description', '')
                }))
                return EXIT_SUCCESS
        output(success_response({"plan_type": "pm-workflow:plan-type-generic", "pattern": "*", "description": "Default"}))
        return EXIT_SUCCESS

    elif args.verb == 'list':
        output(success_response(rules))
        return EXIT_SUCCESS

    elif args.verb == 'add':
        new_rule = {
            "pattern": args.pattern,
            "plan_type": args.plan_type,
            "description": args.description or ""
        }
        # Insert before fallback if exists
        if rules and rules[-1]['pattern'] == '*':
            rules.insert(-1, new_rule)
        else:
            rules.append(new_rule)
        config['plan_type_rules'] = rules
        save_config(config)
        output(success_response({"added": new_rule}))
        return EXIT_SUCCESS

    elif args.verb == 'remove':
        pattern = args.pattern
        original_count = len(rules)
        rules = [r for r in rules if r['pattern'] != pattern]
        if len(rules) == original_count:
            output(error_response(f"Pattern not found: {pattern}"))
            return EXIT_ERROR
        config['plan_type_rules'] = rules
        save_config(config)
        output(success_response({"removed": pattern}))
        return EXIT_SUCCESS

    return EXIT_ERROR


# =============================================================================
# keywords Subcommand
# =============================================================================

def cmd_keywords(args) -> int:
    """Handle keywords noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    keywords = config.get('detection_keywords', {})

    if args.verb == 'match':
        text = args.text.lower()
        words = set(re.findall(r'\b\w+\b', text))
        for plan_type, kw_list in keywords.items():
            matched = [kw for kw in kw_list if kw.lower() in words]
            if matched:
                output(success_response({"plan_type": plan_type, "matched": matched}))
                return EXIT_SUCCESS
        output(success_response({"plan_type": None, "matched": []}))
        return EXIT_SUCCESS

    elif args.verb == 'list':
        if args.plan_type:
            kws = keywords.get(args.plan_type, [])
            output(success_response(kws))
        else:
            output(success_response(keywords))
        return EXIT_SUCCESS

    elif args.verb == 'add':
        plan_type = args.plan_type
        keyword = args.keyword
        if plan_type not in keywords:
            keywords[plan_type] = []
        if keyword not in keywords[plan_type]:
            keywords[plan_type].append(keyword)
        config['detection_keywords'] = keywords
        save_config(config)
        output(success_response({"plan_type": plan_type, "added": keyword}))
        return EXIT_SUCCESS

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
        detected.append({
            "detected": "maven",
            "skill": "pm-dev-builder:builder-maven-rules",
            "active": True
        })

    # Gradle
    if (project_root / 'build.gradle').exists() or (project_root / 'build.gradle.kts').exists():
        detected.append({
            "detected": "gradle",
            "skill": "pm-dev-builder:builder-gradle-rules",
            "active": True
        })

    # npm
    if (project_root / 'package.json').exists():
        detected.append({
            "detected": "npm",
            "skill": "pm-dev-builder:builder-npm-rules",
            "active": True
        })

    return detected


def cmd_build_systems(args) -> int:
    """Handle build-systems noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    build_systems = config.get('build_systems', [])

    if args.verb == 'list':
        output(success_response(build_systems))
        return EXIT_SUCCESS

    elif args.verb == 'set':
        system = args.system
        active = args.active.lower() == 'true'
        found = False
        for bs in build_systems:
            if bs['detected'] == system:
                bs['active'] = active
                found = True
                break
        if not found:
            output(error_response(f"Build system not found: {system}"))
            return EXIT_ERROR
        config['build_systems'] = build_systems
        save_config(config)
        output(success_response({"system": system, "active": active}))
        return EXIT_SUCCESS

    elif args.verb == 'detect':
        detected = detect_build_systems()
        config['build_systems'] = detected
        save_config(config)
        output(success_response({"detected": detected}))
        return EXIT_SUCCESS

    return EXIT_ERROR


# =============================================================================
# custom-types Subcommand
# =============================================================================

def cmd_custom_types(args) -> int:
    """Handle custom-types noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    custom_types = config.get('custom_plan_types', [])

    if args.verb == 'list':
        output(success_response(custom_types))
        return EXIT_SUCCESS

    elif args.verb == 'add':
        new_type = {
            "name": args.name,
            "skill_path": args.skill_path,
            "solution_outline_agent": args.solution_outline_agent if args.solution_outline_agent != 'null' else None,
            "task_plan_agent": args.task_plan_agent if args.task_plan_agent != 'null' else None
        }
        # Check for duplicates
        for ct in custom_types:
            if ct['name'] == args.name:
                output(error_response(f"Custom type already exists: {args.name}"))
                return EXIT_ERROR
        custom_types.append(new_type)
        config['custom_plan_types'] = custom_types
        save_config(config)
        output(success_response({"added": new_type}))
        return EXIT_SUCCESS

    elif args.verb == 'remove':
        name = args.name
        original_count = len(custom_types)
        custom_types = [ct for ct in custom_types if ct['name'] != name]
        if len(custom_types) == original_count:
            output(error_response(f"Custom type not found: {name}"))
            return EXIT_ERROR
        config['custom_plan_types'] = custom_types
        save_config(config)
        output(success_response({"removed": name}))
        return EXIT_SUCCESS

    return EXIT_ERROR


# =============================================================================
# state Subcommand
# =============================================================================

def cmd_state(args) -> int:
    """Handle state noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        output(error_response(str(e)))
        return EXIT_ERROR

    config = load_config()
    state = config.get('state', {})

    if args.verb == 'get':
        output(success_response(state))
        return EXIT_SUCCESS

    elif args.verb == 'set':
        field = args.field
        value = args.value
        # Type coercion for numbers
        if value.isdigit():
            value = int(value)
        state[field] = value
        config['state'] = state
        save_config(config)
        output(success_response({field: value}))
        return EXIT_SUCCESS

    elif args.verb == 'update-checksum':
        # Calculate checksum of config (excluding state)
        import hashlib
        config_copy = {k: v for k, v in config.items() if k != 'state'}
        checksum = hashlib.md5(json.dumps(config_copy, sort_keys=True).encode()).hexdigest()[:8]
        state['checksum'] = checksum
        config['state'] = state
        save_config(config)
        output(success_response({"checksum": checksum}))
        return EXIT_SUCCESS

    return EXIT_ERROR


# =============================================================================
# init Subcommand
# =============================================================================

def cmd_init(args) -> int:
    """Handle init command. Does NOT require_initialized() - this creates the file."""
    if is_initialized() and not getattr(args, 'force', False):
        output(error_response("marshal.json already exists. Use --force to overwrite."))
        return EXIT_ERROR

    # Start with defaults
    config = DEFAULTS.copy()

    # If template specified, load it
    if hasattr(args, 'template') and args.template:
        template_path = Path(__file__).parent.parent.parent.parent.parent / 'pm-workflow' / 'skills' / 'plan-marshall' / 'templates' / f'{args.template}.json'
        if template_path.exists():
            try:
                template = json.loads(template_path.read_text(encoding='utf-8'))
                config.update(template)
            except json.JSONDecodeError:
                pass

    # Auto-detect build systems
    detected = detect_build_systems()
    if detected:
        config['build_systems'] = detected

    save_config(config)
    output(success_response({
        "created": str(MARSHAL_PATH),
        "build_systems_detected": len(detected)
    }))
    return EXIT_SUCCESS


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Marshal configuration management',
        epilog='''
Examples:
  marshal-config.py domain-agents get --plan-type pm-workflow:plan-type-java
  marshal-config.py defaults set --field create_pr --value true
  marshal-config.py rules match --file src/main/java/Foo.java
  marshal-config.py init
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='noun', help='Noun (resource type)')

    # --- domain-agents ---
    p_da = subparsers.add_parser('domain-agents', help='Manage domain agent mappings')
    da_sub = p_da.add_subparsers(dest='verb', help='Operation')

    da_get = da_sub.add_parser('get', help='Get agents for plan-type')
    da_get.add_argument('--plan-type', required=True, help='Plan type (bundle:skill)')

    da_set = da_sub.add_parser('set', help='Set agents for plan-type')
    da_set.add_argument('--plan-type', required=True, help='Plan type (bundle:skill)')
    da_set.add_argument('--solution-outline-agent', help='Solution Outline agent (bundle:agent or null)')
    da_set.add_argument('--task-plan-agent', help='Task Plan agent (bundle:agent or null)')

    da_sub.add_parser('list', help='List all domain agent mappings')

    # --- defaults ---
    p_def = subparsers.add_parser('defaults', help='Manage default settings')
    def_sub = p_def.add_subparsers(dest='verb', help='Operation')

    def_get = def_sub.add_parser('get', help='Get default value')
    def_get.add_argument('--field', required=True, help='Field name')

    def_set = def_sub.add_parser('set', help='Set default value')
    def_set.add_argument('--field', required=True, help='Field name')
    def_set.add_argument('--value', required=True, help='Field value')

    def_sub.add_parser('list', help='List all defaults')

    # --- plan-type-defaults ---
    p_ptd = subparsers.add_parser('plan-type-defaults', help='Manage per-plan-type defaults')
    ptd_sub = p_ptd.add_subparsers(dest='verb', help='Operation')

    ptd_get = ptd_sub.add_parser('get', help='Get plan-type defaults')
    ptd_get.add_argument('--plan-type', required=True, help='Plan type')

    ptd_set = ptd_sub.add_parser('set', help='Set plan-type defaults')
    ptd_set.add_argument('--plan-type', required=True, help='Plan type')
    ptd_set.add_argument('--verification-command', help='Verification command')
    ptd_set.add_argument('--pr-workflow', help='PR workflow (true/false)')

    # --- rules ---
    p_rules = subparsers.add_parser('rules', help='Manage plan-type routing rules')
    rules_sub = p_rules.add_subparsers(dest='verb', help='Operation')

    rules_match = rules_sub.add_parser('match', help='Match file to plan-type')
    rules_match.add_argument('--file', required=True, help='File path to match')

    rules_sub.add_parser('list', help='List all rules')

    rules_add = rules_sub.add_parser('add', help='Add a rule')
    rules_add.add_argument('--pattern', required=True, help='Glob pattern')
    rules_add.add_argument('--plan-type', required=True, help='Plan type')
    rules_add.add_argument('--description', help='Description')

    rules_remove = rules_sub.add_parser('remove', help='Remove a rule')
    rules_remove.add_argument('--pattern', required=True, help='Pattern to remove')

    # --- keywords ---
    p_kw = subparsers.add_parser('keywords', help='Manage detection keywords')
    kw_sub = p_kw.add_subparsers(dest='verb', help='Operation')

    kw_match = kw_sub.add_parser('match', help='Match text to plan-type')
    kw_match.add_argument('--text', required=True, help='Text to analyze')

    kw_list = kw_sub.add_parser('list', help='List keywords')
    kw_list.add_argument('--plan-type', help='Filter by plan-type')

    kw_add = kw_sub.add_parser('add', help='Add a keyword')
    kw_add.add_argument('--plan-type', required=True, help='Plan type')
    kw_add.add_argument('--keyword', required=True, help='Keyword to add')

    # --- build-systems ---
    p_bs = subparsers.add_parser('build-systems', help='Manage build system configuration')
    bs_sub = p_bs.add_subparsers(dest='verb', help='Operation')

    bs_sub.add_parser('list', help='List build systems')

    bs_set = bs_sub.add_parser('set', help='Set build system status')
    bs_set.add_argument('--system', required=True, help='Build system name')
    bs_set.add_argument('--active', required=True, help='Active status (true/false)')

    bs_sub.add_parser('detect', help='Auto-detect build systems')

    # --- custom-types ---
    p_ct = subparsers.add_parser('custom-types', help='Manage custom plan types')
    ct_sub = p_ct.add_subparsers(dest='verb', help='Operation')

    ct_sub.add_parser('list', help='List custom types')

    ct_add = ct_sub.add_parser('add', help='Add custom type')
    ct_add.add_argument('--name', required=True, help='Type name')
    ct_add.add_argument('--skill-path', required=True, help='Path to SKILL.md')
    ct_add.add_argument('--solution-outline-agent', help='Solution Outline agent (or null)')
    ct_add.add_argument('--task-plan-agent', help='Task Plan agent (or null)')

    ct_remove = ct_sub.add_parser('remove', help='Remove custom type')
    ct_remove.add_argument('--name', required=True, help='Type name')

    # --- state ---
    p_state = subparsers.add_parser('state', help='Manage generation state')
    state_sub = p_state.add_subparsers(dest='verb', help='Operation')

    state_sub.add_parser('get', help='Get state')

    state_set = state_sub.add_parser('set', help='Set state field')
    state_set.add_argument('--field', required=True, help='Field name')
    state_set.add_argument('--value', required=True, help='Field value')

    state_sub.add_parser('update-checksum', help='Recalculate checksum')

    # --- init ---
    p_init = subparsers.add_parser('init', help='Initialize marshal.json')
    p_init.add_argument('--template', help='Template name (e.g., java-project)')
    p_init.add_argument('--force', action='store_true', help='Overwrite existing')

    args = parser.parse_args()

    if args.noun is None:
        parser.print_help()
        return EXIT_ERROR

    # Route to handler
    if args.noun == 'domain-agents':
        return cmd_domain_agents(args)
    elif args.noun == 'defaults':
        return cmd_defaults(args)
    elif args.noun == 'plan-type-defaults':
        return cmd_plan_type_defaults(args)
    elif args.noun == 'rules':
        return cmd_rules(args)
    elif args.noun == 'keywords':
        return cmd_keywords(args)
    elif args.noun == 'build-systems':
        return cmd_build_systems(args)
    elif args.noun == 'custom-types':
        return cmd_custom_types(args)
    elif args.noun == 'state':
        return cmd_state(args)
    elif args.noun == 'init':
        return cmd_init(args)
    else:
        parser.print_help()
        return EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())
