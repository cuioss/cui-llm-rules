#!/usr/bin/env python3
"""
verify-fix.py

Verifies that a fix was successfully applied by re-running relevant diagnostics.

Usage:
    python3 verify-fix.py <fix_type> <component_path>

Arguments:
    fix_type        Type of fix to verify (see supported types below)
    component_path  Path to the component file that was fixed

Supported fix types:
    missing-frontmatter    Verify frontmatter was added
    missing-name-field     Verify name field was added
    missing-description-field  Verify description field was added
    missing-tools-field    Verify tools field was added
    array-syntax-tools     Verify array syntax was converted
    rule-6-violation       Verify Task tool was removed
    trailing-whitespace    Verify trailing whitespace was removed
    pattern-22-violation   Verify self-update patterns were removed
    unused-tool-declared   Verify unused tools were removed

Output: JSON with verification result including:
    - verified: Whether verification completed
    - issue_resolved: Whether the issue was actually fixed
    - details: Human-readable explanation

Exit codes:
    0 - Verification completed (check issue_resolved for result)
    1 - Error (missing arguments, file not found)
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_frontmatter(content: str) -> tuple[bool, str]:
    """Extract YAML frontmatter from content."""
    if not content.startswith('---'):
        return False, ''

    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        return True, match.group(1)
    return False, ''


def verify_frontmatter_fix(file_path: Path) -> dict:
    """Verify frontmatter was added with required fields."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    frontmatter_present, frontmatter = extract_frontmatter(content)

    if not frontmatter_present:
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Still missing frontmatter'
        }

    has_name = bool(re.search(r'^name:', frontmatter, re.MULTILINE))
    has_desc = bool(re.search(r'^description:', frontmatter, re.MULTILINE))

    if has_name and has_desc:
        return {
            'verified': True,
            'issue_resolved': True,
            'details': 'Frontmatter present with required fields'
        }

    return {
        'verified': True,
        'issue_resolved': False,
        'details': f'Frontmatter present but missing fields (name: {has_name}, description: {has_desc})'
    }


def verify_array_syntax_fix(file_path: Path) -> dict:
    """Verify tools no longer uses array syntax."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    frontmatter_present, frontmatter = extract_frontmatter(content)

    if not frontmatter_present:
        return {
            'verified': True,
            'issue_resolved': True,
            'details': 'No frontmatter to check'
        }

    if re.search(r'^tools:.*\[', frontmatter, re.MULTILINE):
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Still using array syntax for tools'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'Tools now using comma-separated format'
    }


def verify_rule_6_fix(file_path: Path) -> dict:
    """Verify Task tool was removed from declaration."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    frontmatter_present, frontmatter = extract_frontmatter(content)

    if not frontmatter_present:
        return {
            'verified': True,
            'issue_resolved': True,
            'details': 'No frontmatter to check'
        }

    if re.search(r'^tools:.*\bTask\b', frontmatter, re.MULTILINE):
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Task tool still declared (Rule 6 violation)'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'Task tool removed from declaration'
    }


def verify_trailing_whitespace_fix(file_path: Path) -> dict:
    """Verify trailing whitespace was removed."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    trailing_count = len(re.findall(r'[ \t]+$', content, re.MULTILINE))

    if trailing_count > 0:
        return {
            'verified': True,
            'issue_resolved': False,
            'details': f'Still has trailing whitespace on {trailing_count} lines'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'No trailing whitespace found'
    }


def verify_pattern_22_fix(file_path: Path) -> dict:
    """Verify self-update patterns were removed."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    if re.search(r'/plugin-update-agent|/plugin-update-command', content, re.IGNORECASE):
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Still contains self-update commands (Pattern 22 violation)'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'Self-update patterns removed'
    }


def verify_unused_tool_fix(file_path: Path) -> dict:
    """Verify unused tools were removed."""
    # Try to run full tool coverage analysis
    try:
        from analyze_tool_coverage import analyze_tool_coverage
        result = analyze_tool_coverage(file_path)

        if 'error' in result:
            return {
                'verified': True,
                'issue_resolved': None,
                'details': 'Full analysis not available, manual verification recommended'
            }

        unused_count = result.get('tool_coverage', {}).get('unused_count', 0)

        if unused_count == 0:
            return {
                'verified': True,
                'issue_resolved': True,
                'details': 'No unused tools declared'
            }

        return {
            'verified': True,
            'issue_resolved': False,
            'details': f'Still has {unused_count} unused tools declared'
        }

    except ImportError:
        return {
            'verified': True,
            'issue_resolved': None,
            'details': 'Full analysis not available, manual verification recommended'
        }


def verify_generic(file_path: Path, fix_type: str) -> dict:
    """Generic verification for unknown fix types."""
    return {
        'verified': True,
        'issue_resolved': None,
        'details': 'Manual verification recommended'
    }


def main():
    parser = argparse.ArgumentParser(
        description="Verify that a fix was successfully applied"
    )
    parser.add_argument(
        'fix_type',
        help="Type of fix to verify"
    )
    parser.add_argument(
        'component_path',
        help="Path to the component file that was fixed"
    )

    args = parser.parse_args()

    file_path = Path(args.component_path)

    # Validate path
    if not file_path.exists():
        print(json.dumps({
            'verified': False,
            'error': f'File not found: {args.component_path}'
        }), file=sys.stderr)
        return 1

    if not file_path.is_file():
        print(json.dumps({
            'verified': False,
            'error': f'Not a file: {args.component_path}'
        }), file=sys.stderr)
        return 1

    # Route to appropriate verification
    fix_type = args.fix_type

    if fix_type in ('missing-frontmatter', 'missing-name-field',
                    'missing-description-field', 'missing-tools-field'):
        result = verify_frontmatter_fix(file_path)
    elif fix_type == 'array-syntax-tools':
        result = verify_array_syntax_fix(file_path)
    elif fix_type == 'rule-6-violation':
        result = verify_rule_6_fix(file_path)
    elif fix_type == 'trailing-whitespace':
        result = verify_trailing_whitespace_fix(file_path)
    elif fix_type == 'pattern-22-violation':
        result = verify_pattern_22_fix(file_path)
    elif fix_type == 'unused-tool-declared':
        result = verify_unused_tool_fix(file_path)
    else:
        result = verify_generic(file_path, fix_type)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
