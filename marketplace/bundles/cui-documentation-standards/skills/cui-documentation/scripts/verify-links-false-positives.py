#!/usr/bin/env python3
"""
Classify broken link candidates from verify-adoc-links.py to reduce false positives.

This script categorizes broken links into:
- likely-false-positive: Links that appear broken but are likely valid (anchors, localhost, file://)
- must-verify-manual: Links requiring manual verification with Read tool
- definitely-broken: Links that are confirmed broken by the script

Output: JSON with categorized issues for Claude to process.
"""

import argparse
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any


def is_internal_anchor(link: str) -> bool:
    """Check if link is an internal anchor reference."""
    # Format: <<anchor-id>> or file.adoc#anchor
    return link.startswith('<<') or '#' in link


def is_localhost_url(link: str) -> bool:
    """Check if link is a localhost URL."""
    localhost_patterns = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '[::1]'  # IPv6 localhost
    ]
    return any(pattern in link.lower() for pattern in localhost_patterns)


def is_file_protocol(link: str) -> bool:
    """Check if link uses file:// protocol."""
    return link.startswith('file://')


def is_generated_path(link: str) -> bool:
    """Check if link points to generated documentation."""
    generated_paths = [
        'target/',
        'build/',
        'dist/',
        'out/',
        '.gradle/',
        'node_modules/'
    ]
    return any(gen in link for gen in generated_paths)


def is_external_url(link: str) -> bool:
    """Check if link is an external HTTP/HTTPS URL."""
    return link.startswith('http://') or link.startswith('https://')


def categorize_broken_link(issue: Dict[str, Any]) -> str:
    """
    Categorize a broken link issue.

    Returns:
        - 'likely-false-positive': Link appears broken but is likely valid
        - 'must-verify-manual': Requires manual verification with Read tool
        - 'definitely-broken': Confirmed broken by script
    """
    link = issue.get('link', '')
    issue_type = issue.get('type', '')

    # Internal anchors - likely false positive (may be dynamically generated)
    if is_internal_anchor(link):
        return 'likely-false-positive'

    # Localhost URLs - intentional local references
    if is_localhost_url(link):
        return 'likely-false-positive'

    # File protocol - may be valid on user's machine
    if is_file_protocol(link):
        return 'likely-false-positive'

    # Generated paths - may be created during build
    if is_generated_path(link):
        return 'likely-false-positive'

    # External URLs - need network check (manual verification recommended)
    if is_external_url(link):
        return 'must-verify-manual'

    # File links - require Read tool verification
    if issue_type in ['broken_file_link', 'file_not_found']:
        return 'must-verify-manual'

    # Default to manual verification for safety
    return 'must-verify-manual'


def add_verification_hint(issue: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Add verification hints based on category."""
    issue_copy = issue.copy()
    issue_copy['category'] = category

    if category == 'likely-false-positive':
        reasons = []
        link = issue.get('link', '')

        if is_internal_anchor(link):
            reasons.append('Internal anchor reference (may be dynamically generated)')
        if is_localhost_url(link):
            reasons.append('Localhost URL (intentional development reference)')
        if is_file_protocol(link):
            reasons.append('File protocol (may be valid on local filesystem)')
        if is_generated_path(link):
            reasons.append('Generated documentation path (created during build)')

        issue_copy['false_positive_reasons'] = reasons
        issue_copy['action'] = 'keep'

    elif category == 'must-verify-manual':
        link = issue.get('link', '')
        file_path = issue.get('file', '')

        hints = []

        if is_external_url(link):
            hints.append('External URL - verify accessibility (may require network)')
            issue_copy['verification_method'] = 'network_check'
        else:
            hints.append('File link - verify existence with Read tool')
            hints.append(f'Resolve path relative to: {Path(file_path).parent}')
            issue_copy['verification_method'] = 'read_tool'

        issue_copy['verification_hints'] = hints
        issue_copy['action'] = 'verify_then_decide'

    elif category == 'definitely-broken':
        issue_copy['action'] = 'ask_user_before_removal'

    return issue_copy


def process_broken_links(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process broken links and categorize them.

    Args:
        input_data: JSON from verify-adoc-links.py

    Returns:
        Categorized issues with verification hints
    """
    issues = input_data.get('issues', [])

    categorized = {
        'likely-false-positive': [],
        'must-verify-manual': [],
        'definitely-broken': []
    }

    for issue in issues:
        category = categorize_broken_link(issue)
        enhanced_issue = add_verification_hint(issue, category)
        categorized[category].append(enhanced_issue)

    summary = {
        'total_issues': len(issues),
        'likely_false_positive_count': len(categorized['likely-false-positive']),
        'must_verify_manual_count': len(categorized['must-verify-manual']),
        'definitely_broken_count': len(categorized['definitely-broken']),
        'recommendation': generate_recommendation(categorized)
    }

    return {
        'summary': summary,
        'categorized_issues': categorized
    }


def generate_recommendation(categorized: Dict[str, List]) -> str:
    """Generate action recommendation based on categorization."""
    false_positives = len(categorized['likely-false-positive'])
    must_verify = len(categorized['must-verify-manual'])
    definitely_broken = len(categorized['definitely-broken'])

    if must_verify == 0 and definitely_broken == 0:
        return 'All broken links are likely false positives. Review before taking action.'
    elif must_verify > 0:
        return f'Manual verification required for {must_verify} links using Read tool.'
    else:
        return f'{definitely_broken} links confirmed broken. Ask user before removal.'


def main():
    parser = argparse.ArgumentParser(
        description='Classify broken link candidates to reduce false positives',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify broken links from verify-adoc-links.py output
  %(prog)s --input target/links.json --output target/classified.json

  # Read from stdin, write to stdout
  cat target/links.json | %(prog)s

Output Format:
  {
    "summary": {
      "total_issues": 10,
      "likely_false_positive_count": 4,
      "must_verify_manual_count": 5,
      "definitely_broken_count": 1,
      "recommendation": "Manual verification required for 5 links using Read tool."
    },
    "categorized_issues": {
      "likely-false-positive": [...],
      "must-verify-manual": [...],
      "definitely-broken": [...]
    }
  }
        """
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Input JSON file from verify-adoc-links.py (default: stdin)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file (default: stdout)'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    # Read input
    try:
        if args.input:
            with open(args.input, 'r') as f:
                input_data = json.load(f)
        else:
            input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Process
    result = process_broken_links(input_data)

    # Write output
    indent = 2 if args.pretty else None
    output_json = json.dumps(result, indent=indent)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
        except IOError as e:
            print(f"Error: Cannot write to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)

    # Exit with status based on results
    # 0: Success (issues categorized)
    # 1: Error
    sys.exit(0)


if __name__ == '__main__':
    main()
