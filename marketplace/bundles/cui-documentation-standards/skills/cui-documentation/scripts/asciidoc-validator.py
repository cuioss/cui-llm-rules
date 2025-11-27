#!/usr/bin/env python3
"""
AsciiDoc Validator - Comprehensive validation tool for AsciiDoc documents.

Usage:
    python3 asciidoc-validator.py [OPTIONS] [directory]

Options:
    -f, --format FORMAT    Output format: console, json (default: console)
    -v, --verbose          Show detailed output for all files
    -q, --quiet            Show only errors (no success messages)
    -i, --ignore PATTERN   Add ignore pattern (can be used multiple times)
    -s, --severity LEVEL   Minimum severity: error, warning, all (default: all)
    -h, --help             Show this help message

Exit codes:
    0 - All files compliant
    1 - Non-compliant files found
    2 - Error occurred
"""

import argparse
import fnmatch
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Exit codes
EXIT_SUCCESS = 0
EXIT_NON_COMPLIANT = 1
EXIT_ERROR = 2

# Color codes for output
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Required header attributes
REQUIRED_ATTRS = [
    '= ',
    ':toc: left',
    ':toclevels: 3',
    ':toc-title: Table of Contents',
    ':sectnums:',
    ':source-highlighter: highlight.js',
]


def check_list_formatting(content: str) -> list:
    """
    Check for list formatting issues (missing blank line before lists).

    Returns:
        List of tuples (line_number, list_type, context)
    """
    lines = content.split('\n')
    issues = []

    in_code_block = False
    prev_was_blank = True  # Start as if previous was blank
    in_list = False
    prev_line = ""

    for i, line in enumerate(lines, start=1):
        # Track if we are inside a code block
        if line == '----':
            in_code_block = not in_code_block

        current_is_blank = len(line.strip()) == 0

        # Detect if current line starts a new list (only outside code blocks)
        starts_new_list = False
        list_type = ""
        if not in_code_block:
            if re.match(r'^[\*\-\+] ', line):          # Unordered list
                starts_new_list = True
                list_type = "unordered"
            elif re.match(r'^[0-9]+\. ', line):        # Ordered list
                starts_new_list = True
                list_type = "ordered"
            elif re.match(r'^[^:]+::', line):          # Definition list
                starts_new_list = True
                list_type = "definition"
            elif re.match(r'^\. ', line) and not in_list:  # Numbered list with dot
                starts_new_list = True
                list_type = "numbered"

        # Detect if we are continuing a list
        continuing_list = False
        if not in_code_block and in_list:
            if (re.match(r'^[\*\-\+] ', line) or     # Another unordered item
                re.match(r'^\*\* ', line) or         # Nested unordered
                re.match(r'^[0-9]+\. ', line) or     # Another ordered item
                re.match(r'^\. ', line) or           # Another numbered item (dot syntax)
                current_is_blank):                   # Blank line within list
                continuing_list = True

        # If this starts a new list and previous line was not blank
        # and we are not at the beginning of the file and not already in list
        if starts_new_list and not prev_was_blank and i > 1 and not in_list:
            issues.append((i, list_type, prev_line[:50]))

        # Update list state
        if starts_new_list:
            in_list = True
        elif not continuing_list and not current_is_blank:
            in_list = False

        # Update state for next iteration
        prev_line = line
        prev_was_blank = current_is_blank

    return issues


def check_xref_syntax(content: str) -> int:
    """
    Check for deprecated cross-reference syntax (<<file.adoc>>).

    Returns:
        Count of deprecated xref instances
    """
    pattern = r'<<.*\.adoc.*>>'
    matches = re.findall(pattern, content)
    return len(matches)


def check_file(file_path: Path) -> dict:
    """
    Check a single AsciiDoc file for compliance.

    Returns:
        Dict with file info and issues found
    """
    content = file_path.read_text(encoding='utf-8')

    result = {
        'file': str(file_path),
        'compliant': True,
        'errors': 0,
        'warnings': 0,
        'issues': [],
        'missing_attrs': [],
        'list_issues': [],
        'xref_count': 0,
    }

    # Check for required header attributes
    for attr in REQUIRED_ATTRS:
        if attr not in content:
            result['missing_attrs'].append(attr)
            result['issues'].append({
                'type': 'missing_header',
                'severity': 'error',
                'attribute': attr
            })
            result['errors'] += 1
            result['compliant'] = False

    # Check for list formatting issues
    list_issues = check_list_formatting(content)
    if list_issues:
        result['list_issues'] = list_issues
        for line_num, list_type, context in list_issues:
            result['issues'].append({
                'type': 'list_formatting',
                'severity': 'warning',
                'line': line_num,
                'list_type': list_type,
                'context': context
            })
        result['warnings'] += len(list_issues)
        result['compliant'] = False

    # Check for deprecated cross-reference syntax
    xref_count = check_xref_syntax(content)
    if xref_count > 0:
        result['xref_count'] = xref_count
        result['issues'].append({
            'type': 'deprecated_xref',
            'severity': 'warning',
            'count': xref_count
        })
        result['warnings'] += xref_count
        result['compliant'] = False

    return result


def should_ignore_file(file_path: Path, ignore_patterns: list) -> bool:
    """Check if file should be ignored based on patterns."""
    file_name = file_path.name
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    return False


def output_console(results: list, summary: dict, verbose: bool, quiet: bool) -> None:
    """Output results in console format."""
    for result in results:
        if result['errors'] > 0 or result['warnings'] > 0 or verbose:
            print(f"Checking {result['file']}...")

            if result['errors'] == 0 and result['warnings'] == 0:
                print("  ✅ Compliant with all standards")
            else:
                # Show missing attributes
                if result['missing_attrs']:
                    print("  ❌ Missing required header attributes:")
                    for attr in result['missing_attrs']:
                        print(f"     - {attr}")

                # Show list issues
                if result['list_issues']:
                    print("  ⚠️  List formatting issues: missing blank line before lists")
                    for line_num, list_type, context in result['list_issues']:
                        print(f"      Line {line_num}: {list_type} list after: {context}")

                # Show xref issues
                if result['xref_count'] > 0:
                    print(f"  ⚠️  Deprecated cross-reference syntax: found {result['xref_count']} instance(s) using <<>> instead of xref:")

            print()

    # Summary
    if not quiet:
        print("Summary:")
        print("-------")
        print(f"Total files checked: {summary['total_files']}")
        print(f"Non-compliant files: {summary['non_compliant_files']}")
        print(f"Total errors: {summary['total_errors']}")
        print(f"Total warnings: {summary['total_warnings']}")
        print()

        if summary['non_compliant_files'] == 0:
            print("All files comply with the AsciiDoc standards! 🎉")
        else:
            print("Some files need to be updated to comply with the AsciiDoc standards.")


def output_json(results: list, summary: dict, check_dir: str) -> None:
    """Output results in JSON format."""
    output = {
        'directory': check_dir,
        'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'summary': summary,
        'files': []
    }

    for result in results:
        if not result['compliant']:
            file_output = {
                'file': result['file'],
                'compliant': False,
                'errors': result['errors'],
                'warnings': result['warnings'],
                'issues': result['issues']
            }
            output['files'].append(file_output)

    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Validate AsciiDoc files for compliance with project standards.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Checks performed:
  - Required header attributes
  - List formatting (blank lines)
  - Cross-reference syntax

Exit codes:
  0 - All files compliant
  1 - Non-compliant files found
  2 - Error occurred

Examples:
  %(prog)s                                    # Check standards directory
  %(prog)s -f json docs                       # JSON output for docs directory
  %(prog)s -q -i 'temp*.adoc' standards       # Quiet mode, ignore temp files
'''
    )

    parser.add_argument('path', nargs='?', default='standards',
                        help='File or directory to check (default: standards)')
    parser.add_argument('-f', '--format', dest='output_format', default='console',
                        choices=['console', 'json'],
                        help='Output format: console, json (default: console)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed output for all files')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Show only errors (no success messages)')
    parser.add_argument('-i', '--ignore', action='append', dest='ignore_patterns',
                        default=['asciidoc-standards.adoc'],
                        help='Add ignore pattern (can be used multiple times)')
    parser.add_argument('-s', '--severity', default='all',
                        choices=['error', 'warning', 'all'],
                        help='Minimum severity: error, warning, all (default: all)')

    args = parser.parse_args()

    check_path = Path(args.path)

    # Validate that the path exists
    if not check_path.exists():
        if args.output_format == 'json':
            print(json.dumps({'error': 'Path not found', 'path': str(check_path)}))
        else:
            print(f"Error: Path '{check_path}' does not exist.")
        sys.exit(EXIT_ERROR)

    if args.output_format == 'console' and not args.quiet:
        if check_path.is_file():
            print(f"Checking '{check_path}' for compliance with AsciiDoc standards...")
        else:
            print(f"Checking .adoc files in '{check_path}' for compliance with AsciiDoc standards...")
        print()

    # Find and process files
    results = []
    if check_path.is_file():
        adoc_files = [check_path] if check_path.suffix == '.adoc' else []
    else:
        adoc_files = sorted(check_path.rglob('*.adoc'))

    for file_path in adoc_files:
        if should_ignore_file(file_path, args.ignore_patterns):
            continue

        result = check_file(file_path)
        results.append(result)

    # Calculate summary
    summary = {
        'total_files': len(results),
        'non_compliant_files': sum(1 for r in results if not r['compliant']),
        'compliant_files': sum(1 for r in results if r['compliant']),
        'total_errors': sum(r['errors'] for r in results),
        'total_warnings': sum(r['warnings'] for r in results),
    }

    # Output results
    if args.output_format == 'json':
        output_json(results, summary, str(check_path))
    else:
        output_console(results, summary, args.verbose, args.quiet)

    # Exit with appropriate code
    if summary['total_errors'] > 0:
        sys.exit(EXIT_NON_COMPLIANT)
    elif summary['total_warnings'] > 0 and args.severity != 'error':
        sys.exit(EXIT_NON_COMPLIANT)
    else:
        sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    main()
