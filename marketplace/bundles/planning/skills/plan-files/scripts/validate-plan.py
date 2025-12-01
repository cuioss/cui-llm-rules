#!/usr/bin/env python3
"""
Validate plan structure and content.

Usage:
    python3 validate-plan.py <plan-directory>
    python3 validate-plan.py --help

Output: JSON with validation results including errors, warnings, and recommendations.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def validate_plan_file(plan_file: Path) -> dict:
    """Validate plan.md structure and content."""
    errors = []
    warnings = []

    if not plan_file.exists():
        return {
            'valid': False,
            'errors': [{'code': 'PLAN_NOT_FOUND', 'message': f'Plan file not found: {plan_file}'}],
            'warnings': []
        }

    content = plan_file.read_text()

    # Check for title
    if not re.search(r'^#\s+(?:Task Plan:)?\s*.+', content, re.MULTILINE):
        errors.append({'code': 'MISSING_TITLE', 'message': 'Plan missing title header'})

    # Check for current phase
    if not re.search(r'\*\*Current Phase\*\*:', content):
        errors.append({'code': 'MISSING_CURRENT_PHASE', 'message': 'Plan missing Current Phase indicator'})

    # Check for current task
    if not re.search(r'\*\*Current Task\*\*:', content):
        warnings.append({'code': 'MISSING_CURRENT_TASK', 'message': 'Plan missing Current Task indicator'})

    # Check for phase progress table
    if not re.search(r'##\s*Phase Progress', content, re.IGNORECASE):
        errors.append({'code': 'MISSING_PHASE_TABLE', 'message': 'Plan missing Phase Progress table'})

    # Validate phase progress table structure
    table_match = re.search(r'\|\s*Phase\s*\|\s*Status\s*\|\s*Tasks\s*\|\s*Completed\s*\|', content, re.IGNORECASE)
    if table_match:
        # Check for valid statuses
        status_pattern = r'\|\s*\w+\s*\|\s*(\w+)\s*\|'
        statuses = re.findall(status_pattern, content)
        valid_statuses = {'pending', 'in_progress', 'completed', 'status'}  # 'status' is header
        for status in statuses:
            if status.lower() not in valid_statuses:
                warnings.append({
                    'code': 'INVALID_STATUS',
                    'message': f"Invalid phase status: '{status}'. Use: pending, in_progress, completed"
                })
    else:
        if re.search(r'##\s*Phase Progress', content, re.IGNORECASE):
            errors.append({'code': 'INVALID_PHASE_TABLE', 'message': 'Phase Progress table has invalid structure'})

    # Check tasks structure
    task_headers = re.findall(r'### Task (\d+):', content)
    if not task_headers:
        warnings.append({'code': 'NO_TASKS', 'message': 'No tasks defined in plan'})
    else:
        # Check for sequential task numbering
        task_ids = [int(t) for t in task_headers]
        expected_ids = list(range(1, len(task_ids) + 1))
        if sorted(task_ids) != task_ids:
            warnings.append({'code': 'TASK_ORDER', 'message': 'Tasks are not in sequential order'})

    # Check task content
    task_pattern = r'### Task \d+:[^\n]*\n(.*?)(?=### Task \d+:|## Phase:|## Completion|$)'
    task_contents = re.finditer(task_pattern, content, re.DOTALL)

    for i, match in enumerate(task_contents, 1):
        task_content = match.group(1)

        if not re.search(r'\*\*Phase\*\*:', task_content):
            warnings.append({
                'code': 'TASK_MISSING_PHASE',
                'message': f'Task {i} missing Phase field'
            })

        if not re.search(r'\*\*Goal\*\*:', task_content):
            warnings.append({
                'code': 'TASK_MISSING_GOAL',
                'message': f'Task {i} missing Goal field'
            })

        if not re.search(r'\*\*Checklist\*\*:', task_content, re.IGNORECASE):
            warnings.append({
                'code': 'TASK_MISSING_CHECKLIST',
                'message': f'Task {i} missing Checklist'
            })

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_config_file(config_file: Path) -> dict:
    """Validate config.toon structure and content (TOON format)."""
    errors = []
    warnings = []

    if not config_file.exists():
        return {
            'valid': False,
            'errors': [{'code': 'CONFIG_NOT_FOUND', 'message': f'Config file not found: {config_file}'}],
            'warnings': []
        }

    content = config_file.read_text()

    # Parse TOON format - key: value pairs
    config = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            config[key.strip().lower()] = value.strip()

    # Check for plan type
    if 'plan_type' not in config:
        errors.append({'code': 'MISSING_PLAN_TYPE', 'message': 'Config missing plan_type'})
    else:
        plan_type = config['plan_type'].lower()
        if plan_type not in ['implementation', 'simple', 'plugin-development']:
            errors.append({
                'code': 'INVALID_PLAN_TYPE',
                'message': f"Invalid plan type: '{plan_type}'. Use: implementation, simple, plugin-development"
            })

    # Check for branch
    if 'branch' not in config or not config['branch']:
        errors.append({'code': 'MISSING_BRANCH', 'message': 'Config missing branch'})

    # Check for technology (optional but recommended)
    if 'technology' not in config:
        warnings.append({'code': 'MISSING_TECHNOLOGY', 'message': 'Config missing technology field'})

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_references_file(references_file: Path) -> dict:
    """Validate references.toon structure (TOON format)."""
    errors = []
    warnings = []

    if not references_file.exists():
        # References file is optional
        return {
            'valid': True,
            'errors': [],
            'warnings': [{'code': 'REFERENCES_NOT_FOUND', 'message': 'No references.toon file (optional)'}]
        }

    content = references_file.read_text()

    # Parse TOON format for basic validation
    has_branch = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('branch:'):
            value = line.split(':', 1)[1].strip()
            if value and value != '(not set)':
                has_branch = True

    if not has_branch:
        warnings.append({'code': 'MISSING_BRANCH', 'message': 'References missing branch value'})

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_plan_directory(plan_dir: Path) -> dict:
    """Validate entire plan directory structure."""
    if not plan_dir.exists():
        return {
            'error': {
                'type': 'directory_not_found',
                'message': f'Plan directory not found: {plan_dir}'
            }
        }

    if not plan_dir.is_dir():
        return {
            'error': {
                'type': 'not_a_directory',
                'message': f'Path is not a directory: {plan_dir}'
            }
        }

    # Validate individual files
    plan_result = validate_plan_file(plan_dir / 'plan.md')
    config_result = validate_config_file(plan_dir / 'config.toon')
    references_result = validate_references_file(plan_dir / 'references.toon')

    # Aggregate results
    all_errors = (
        [{'file': 'plan.md', **e} for e in plan_result['errors']] +
        [{'file': 'config.toon', **e} for e in config_result['errors']] +
        [{'file': 'references.toon', **e} for e in references_result['errors']]
    )

    all_warnings = (
        [{'file': 'plan.md', **w} for w in plan_result['warnings']] +
        [{'file': 'config.toon', **w} for w in config_result['warnings']] +
        [{'file': 'references.toon', **w} for w in references_result['warnings']]
    )

    # Check for required files
    required_files = ['plan.md', 'config.toon']
    missing_files = [f for f in required_files if not (plan_dir / f).exists()]

    overall_valid = (
        plan_result['valid'] and
        config_result['valid'] and
        references_result['valid'] and
        len(missing_files) == 0
    )

    return {
        'valid': overall_valid,
        'directory': str(plan_dir),
        'files': {
            'plan.md': {
                'exists': (plan_dir / 'plan.md').exists(),
                'valid': plan_result['valid']
            },
            'config.toon': {
                'exists': (plan_dir / 'config.toon').exists(),
                'valid': config_result['valid']
            },
            'references.toon': {
                'exists': (plan_dir / 'references.toon').exists(),
                'valid': references_result['valid']
            }
        },
        'errors': all_errors,
        'warnings': all_warnings,
        'summary': {
            'total_errors': len(all_errors),
            'total_warnings': len(all_warnings),
            'missing_required_files': missing_files
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Validate plan structure and content.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "valid": true/false,
  "directory": "/path/to/plan",
  "files": {...},
  "errors": [...],
  "warnings": [...],
  "summary": {...}
}
"""
    )
    parser.add_argument('plan_directory', help='Path to plan directory')

    args = parser.parse_args()

    plan_dir = Path(args.plan_directory)
    result = validate_plan_directory(plan_dir)

    print(json.dumps(result, indent=2))

    if 'error' in result or not result.get('valid', False):
        sys.exit(1)


if __name__ == '__main__':
    main()
