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
    """Validate config.md structure and content."""
    errors = []
    warnings = []

    if not config_file.exists():
        return {
            'valid': False,
            'errors': [{'code': 'CONFIG_NOT_FOUND', 'message': f'Config file not found: {config_file}'}],
            'warnings': []
        }

    content = config_file.read_text()

    # Check for plan type
    if not re.search(r'\*\*Plan Type\*\*:', content):
        errors.append({'code': 'MISSING_PLAN_TYPE', 'message': 'Config missing Plan Type'})
    else:
        plan_type_match = re.search(r'\*\*Plan Type\*\*:\s*(\w+)', content)
        if plan_type_match:
            plan_type = plan_type_match.group(1).lower()
            if plan_type not in ['implementation', 'simple']:
                errors.append({
                    'code': 'INVALID_PLAN_TYPE',
                    'message': f"Invalid plan type: '{plan_type}'. Use: implementation, simple"
                })

    # Check for context section
    if not re.search(r'##\s*Context', content, re.IGNORECASE):
        errors.append({'code': 'MISSING_CONTEXT', 'message': 'Config missing Context section'})

    # Check for branch
    if not re.search(r'\|\s*Branch\s*\|', content, re.IGNORECASE):
        errors.append({'code': 'MISSING_BRANCH', 'message': 'Config missing Branch in Context'})

    # Check for build configuration (optional but recommended)
    if not re.search(r'##\s*Build Configuration', content, re.IGNORECASE):
        warnings.append({'code': 'MISSING_BUILD_CONFIG', 'message': 'Config missing Build Configuration section'})

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_references_file(references_file: Path) -> dict:
    """Validate references.md structure."""
    errors = []
    warnings = []

    if not references_file.exists():
        # References file is optional
        return {
            'valid': True,
            'errors': [],
            'warnings': [{'code': 'REFERENCES_NOT_FOUND', 'message': 'No references.md file (optional)'}]
        }

    content = references_file.read_text()

    # Check for broken links (basic validation)
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for name, path in links:
        if not path.startswith('http') and not path.startswith('#'):
            # Local path - check if reasonable
            if path.startswith('..') or path.startswith('./'):
                # Relative path - can't fully validate without context
                pass
            elif not Path(path).suffix:
                warnings.append({
                    'code': 'SUSPICIOUS_LINK',
                    'message': f"Link '{name}' has no file extension: {path}"
                })

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
    config_result = validate_config_file(plan_dir / 'config.md')
    references_result = validate_references_file(plan_dir / 'references.md')

    # Aggregate results
    all_errors = (
        [{'file': 'plan.md', **e} for e in plan_result['errors']] +
        [{'file': 'config.md', **e} for e in config_result['errors']] +
        [{'file': 'references.md', **e} for e in references_result['errors']]
    )

    all_warnings = (
        [{'file': 'plan.md', **w} for w in plan_result['warnings']] +
        [{'file': 'config.md', **w} for w in config_result['warnings']] +
        [{'file': 'references.md', **w} for w in references_result['warnings']]
    )

    # Check for required files
    required_files = ['plan.md', 'config.md']
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
            'config.md': {
                'exists': (plan_dir / 'config.md').exists(),
                'valid': config_result['valid']
            },
            'references.md': {
                'exists': (plan_dir / 'references.md').exists(),
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
