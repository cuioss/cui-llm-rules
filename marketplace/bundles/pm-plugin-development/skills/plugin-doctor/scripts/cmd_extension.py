#!/usr/bin/env python3
"""Extension validation subcommand.

Validates extension.py files in plan-marshall-plugin skills.
Checks contract compliance and extension API consistency.

Output: JSON to stdout.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Any


# Required functions for extension.py
REQUIRED_FUNCTIONS = {
    'is_applicable': {
        'args': ['project_root'],
        'return_type': 'bool',
        'description': 'Check if bundle applies to project'
    },
    'provides_build_systems': {
        'args': [],
        'return_type': 'list',
        'description': 'Return list of build system keys'
    },
    'get_command_mappings': {
        'args': [],
        'return_type': 'dict',
        'description': 'Return command templates'
    }
}

# Domain functions - extensions must have one of these
# get_skill_domains for domain bundles, get_domain_supplements for supplement bundles
DOMAIN_FUNCTIONS = {
    'get_skill_domains': {
        'args': [],
        'return_type': 'dict',
        'description': 'Return domain metadata for skill loading'
    },
    'get_domain_supplements': {
        'args': [],
        'return_type': 'dict',
        'description': 'Return supplement metadata for target domain'
    }
}


def parse_extension_file(extension_path: Path) -> tuple[bool, list[dict], dict]:
    """Parse extension.py file and extract function info.

    Returns:
        (success, errors, functions)
    """
    errors = []
    functions = {}

    try:
        content = extension_path.read_text(encoding='utf-8')
    except (OSError, IOError) as e:
        return False, [{'type': 'read_error', 'message': str(e)}], {}

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return False, [{'type': 'syntax_error', 'message': str(e), 'line': e.lineno}], {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]

            # Try to extract return type annotation
            return_type = None
            if node.returns:
                if isinstance(node.returns, ast.Name):
                    return_type = node.returns.id
                elif isinstance(node.returns, ast.Constant):
                    return_type = str(node.returns.value)

            functions[func_name] = {
                'args': args,
                'return_type': return_type,
                'lineno': node.lineno
            }

    return True, errors, functions


def validate_extension(extension_path: Path) -> dict:
    """Validate a single extension.py file."""
    result = {
        'path': str(extension_path),
        'valid': True,
        'issues': [],
        'functions': {}
    }

    if not extension_path.exists():
        result['valid'] = False
        result['issues'].append({
            'type': 'file_missing',
            'message': f'Extension file not found: {extension_path}'
        })
        return result

    success, errors, functions = parse_extension_file(extension_path)

    if not success:
        result['valid'] = False
        result['issues'].extend(errors)
        return result

    result['functions'] = functions

    # Check required functions
    for func_name, spec in REQUIRED_FUNCTIONS.items():
        if func_name not in functions:
            result['valid'] = False
            result['issues'].append({
                'type': 'missing_function',
                'function': func_name,
                'message': f"Missing required function: {func_name}() - {spec['description']}"
            })
            continue

        func_info = functions[func_name]

        # Check arguments
        expected_args = spec['args']
        actual_args = func_info['args']
        if actual_args != expected_args:
            result['issues'].append({
                'type': 'wrong_args',
                'function': func_name,
                'expected': expected_args,
                'actual': actual_args,
                'severity': 'warning',
                'message': f"{func_name}() has args {actual_args}, expected {expected_args}"
            })

        # Check return type if annotated
        if func_info['return_type'] and func_info['return_type'] != spec['return_type']:
            result['issues'].append({
                'type': 'wrong_return_type',
                'function': func_name,
                'expected': spec['return_type'],
                'actual': func_info['return_type'],
                'severity': 'warning',
                'message': f"{func_name}() returns {func_info['return_type']}, expected {spec['return_type']}"
            })

    # Check domain functions - need at least one of get_skill_domains or get_domain_supplements
    has_domain_func = any(func_name in functions for func_name in DOMAIN_FUNCTIONS)
    if not has_domain_func:
        result['valid'] = False
        result['issues'].append({
            'type': 'missing_function',
            'function': 'get_skill_domains OR get_domain_supplements',
            'message': "Missing domain function: must have either get_skill_domains() or get_domain_supplements()"
        })

    return result


def validate_bundle_consistency(bundle_path: Path) -> dict:
    """Validate consistency between extension.py and bundle structure."""
    result = {
        'bundle': bundle_path.name,
        'valid': True,
        'issues': []
    }

    extension_path = bundle_path / 'skills' / 'plan-marshall-plugin' / 'extension.py'

    if not extension_path.exists():
        # No extension - not an error, just skip
        result['has_extension'] = False
        return result

    result['has_extension'] = True

    # Parse extension to check provides_build_systems()
    success, _, functions = parse_extension_file(extension_path)

    if not success:
        result['valid'] = False
        result['issues'].append({
            'type': 'parse_error',
            'message': 'Failed to parse extension.py'
        })
        return result

    # Check if bundle provides build systems, it should have plan-marshall-plugin skill
    if 'provides_build_systems' in functions:
        # We can't easily determine what the function returns without executing it
        # So just check if plan-marshall-plugin skill exists
        build_ops_path = bundle_path / 'skills' / 'plan-marshall-plugin'

        # Only check for bundles that might have build systems
        # (pm-dev-java, pm-dev-frontend, etc.)
        if bundle_path.name in ['pm-dev-java', 'pm-dev-frontend']:
            if not build_ops_path.is_dir():
                result['issues'].append({
                    'type': 'missing_build_operations',
                    'severity': 'warning',
                    'message': f"Bundle {bundle_path.name} may provide build systems but lacks plan-marshall-plugin skill"
                })

    return result


def scan_extensions(marketplace_root: Path) -> dict:
    """Scan all bundles for extension.py files."""
    bundles_path = marketplace_root / 'bundles'

    if not bundles_path.is_dir():
        return {'error': f'Bundles directory not found: {bundles_path}'}

    results = {
        'extensions': [],
        'summary': {
            'total_bundles': 0,
            'with_extension': 0,
            'valid': 0,
            'invalid': 0,
            'issues': 0
        }
    }

    for bundle_dir in sorted(bundles_path.iterdir()):
        if not bundle_dir.is_dir():
            continue
        if bundle_dir.name.startswith('.'):
            continue

        results['summary']['total_bundles'] += 1

        extension_path = bundle_dir / 'skills' / 'plan-marshall-plugin' / 'extension.py'

        if extension_path.exists():
            results['summary']['with_extension'] += 1
            ext_result = validate_extension(extension_path)
            ext_result['bundle'] = bundle_dir.name

            # Also check bundle consistency
            consistency = validate_bundle_consistency(bundle_dir)
            ext_result['consistency'] = consistency

            if ext_result['valid'] and consistency['valid']:
                results['summary']['valid'] += 1
            else:
                results['summary']['invalid'] += 1

            results['summary']['issues'] += len(ext_result['issues'])
            results['summary']['issues'] += len(consistency.get('issues', []))

            results['extensions'].append(ext_result)

    return results


def cmd_extension(args) -> int:
    """Validate extension.py files."""
    if args.extension_path:
        # Single extension validation
        extension_path = Path(args.extension_path)
        result = validate_extension(extension_path)
        print(json.dumps(result, indent=2))
        return 0 if result['valid'] else 1

    elif args.bundle_path:
        # Bundle consistency check
        bundle_path = Path(args.bundle_path)
        consistency = validate_bundle_consistency(bundle_path)

        if consistency.get('has_extension'):
            extension_path = bundle_path / 'skills' / 'plan-marshall-plugin' / 'extension.py'
            ext_result = validate_extension(extension_path)
            result = {
                'extension': ext_result,
                'consistency': consistency
            }
        else:
            result = consistency

        print(json.dumps(result, indent=2))
        return 0 if consistency['valid'] else 1

    elif args.marketplace_path:
        # Scan all extensions
        marketplace_path = Path(args.marketplace_path)
        result = scan_extensions(marketplace_path)
        print(json.dumps(result, indent=2))

        if 'error' in result:
            return 1
        return 0 if result['summary']['invalid'] == 0 else 1

    else:
        # Default: scan from current directory
        marketplace_path = Path.cwd() / 'marketplace'
        if not marketplace_path.exists():
            marketplace_path = Path.cwd()

        result = scan_extensions(marketplace_path)
        print(json.dumps(result, indent=2))

        if 'error' in result:
            return 1
        return 0 if result['summary']['invalid'] == 0 else 1
