#!/usr/bin/env python3
"""
AsciiDoc Formatter - Auto-fix common AsciiDoc formatting issues.

Companion tool to asciidoc-validator.sh/py.

Usage:
    python3 asciidoc-formatter.py [OPTIONS] [file_or_directory]

Options:
    -t, --type TYPE     Fix types: all, lists, xref, headers, whitespace
    -i, --interactive   Ask before applying each fix
    -b, --no-backup     Don't create backup files
    -v, --verbose       Show detailed progress
    -h, --help          Show this help message

Fix Types:
    lists      - Add blank lines before lists
    xref       - Convert <<>> syntax to xref:
    headers    - Add missing header attributes
    whitespace - Fix trailing whitespace and ensure final newline
    all        - Apply all fixes (default)
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Statistics
files_processed = 0
files_modified = 0
issues_fixed = 0


def fix_lists(content: str) -> tuple[str, int]:
    """
    Fix list formatting by adding blank lines before lists.

    Returns:
        Tuple of (fixed_content, count_of_fixes)
    """
    lines = content.split('\n')
    result = []
    fixed_count = 0

    in_code_block = False
    prev_was_blank = True  # Start as if previous was blank
    in_list = False

    for i, line in enumerate(lines):
        # Track if we are inside a code block
        if line == '----':
            in_code_block = not in_code_block

        current_is_blank = len(line.strip()) == 0

        # Detect if current line starts a new list (only outside code blocks)
        starts_new_list = False
        if not in_code_block:
            # Check for list starters
            if (re.match(r'^[\*\-\+] ', line) or           # Unordered list
                re.match(r'^[0-9]+\. ', line) or           # Ordered list
                re.match(r'^[^:]+::', line) or             # Definition list
                (re.match(r'^\. ', line) and not in_list)): # Numbered list with dot
                starts_new_list = True

        # Detect if we are continuing a list
        continuing_list = False
        if not in_code_block and in_list:
            if (re.match(r'^[\*\-\+] ', line) or     # Another unordered item
                re.match(r'^\*\* ', line) or         # Nested unordered
                re.match(r'^[0-9]+\. ', line) or     # Another ordered item
                current_is_blank):                    # Blank line within list
                continuing_list = True

        # If this starts a new list and previous line was not blank
        # and we are not at the beginning of the file
        if starts_new_list and not prev_was_blank and i > 0 and not in_list:
            result.append('')  # Add blank line
            fixed_count += 1

        # Add current line
        result.append(line)

        # Update list state
        if starts_new_list:
            in_list = True
        elif not continuing_list and not current_is_blank:
            in_list = False

        # Update state for next iteration
        prev_was_blank = current_is_blank

    return '\n'.join(result), fixed_count


def fix_xrefs(content: str) -> tuple[str, int]:
    """
    Fix cross-references by converting <<>> syntax to xref:.

    Returns:
        Tuple of (fixed_content, count_of_fixes)
    """
    # Pattern: <<file.adoc#anchor,text>> -> xref:file.adoc#anchor[text]
    pattern = r'<<([^,>]*),([^>]*)>>'
    replacement = r'xref:\1[\2]'

    fixed_content, count = re.subn(pattern, replacement, content)
    return fixed_content, count


def fix_headers(content: str) -> tuple[str, int]:
    """
    Fix headers by adding missing header attributes after title.

    Returns:
        Tuple of (fixed_content, count_of_fixes)
    """
    lines = content.split('\n')

    # Check if file has a title
    title_line_idx = None
    for i, line in enumerate(lines):
        if line.startswith('= '):
            title_line_idx = i
            break

    if title_line_idx is None:
        return content, 0

    # Required headers
    required_headers = [
        ':toc: left',
        ':toclevels: 3',
        ':toc-title: Table of Contents',
        ':sectnums:',
        ':source-highlighter: highlight.js',
    ]

    # Find which headers are missing
    missing_headers = []
    for header in required_headers:
        if header not in content:
            missing_headers.append(header)

    if not missing_headers:
        return content, 0

    # Insert missing headers after the title line
    result = lines[:title_line_idx + 1]
    result.extend(missing_headers)
    result.extend(lines[title_line_idx + 1:])

    return '\n'.join(result), len(missing_headers)


def fix_whitespace(content: str) -> tuple[str, int]:
    """
    Fix whitespace issues: remove trailing whitespace and ensure final newline.

    Returns:
        Tuple of (fixed_content, count_of_fixes)
    """
    original = content

    # Remove trailing whitespace from each line
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]

    # Ensure final newline (but not multiple)
    content = '\n'.join(lines)
    if not content.endswith('\n'):
        content += '\n'

    # Count as 1 fix if anything changed
    changed = 1 if content != original else 0
    return content, changed


def create_backup(file_path: Path) -> None:
    """Create a backup of the file."""
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
    shutil.copy2(file_path, backup_path)


def show_diff(original: str, modified: str, file_path: Path) -> None:
    """Show a diff of changes (simplified version)."""
    import difflib
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=str(file_path),
        tofile=str(file_path) + ' (modified)',
        lineterm=''
    )
    print(''.join(list(diff)[:40]))  # Show first 40 lines of diff


def process_file(file_path: Path, fix_types: list, backup: bool, interactive: bool, verbose: bool) -> bool:
    """
    Process a single AsciiDoc file.

    Returns:
        True if file was modified, False otherwise
    """
    global files_processed, files_modified, issues_fixed

    files_processed += 1

    if verbose:
        print(f"{BLUE}Processing: {file_path}{NC}")

    # Read file content
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    file_issues_fixed = 0

    # Apply fixes in sequence
    if 'all' in fix_types or 'lists' in fix_types:
        content, count = fix_lists(content)
        if count > 0:
            print(f"{YELLOW}  Fixed {count} list formatting issues{NC}")
            file_issues_fixed += count

    if 'all' in fix_types or 'xref' in fix_types:
        content, count = fix_xrefs(content)
        if count > 0:
            print(f"{YELLOW}  Fixed {count} cross-reference(s){NC}")
            file_issues_fixed += count

    if 'all' in fix_types or 'headers' in fix_types:
        content, count = fix_headers(content)
        if count > 0:
            print(f"{YELLOW}  Added missing header attributes{NC}")
            file_issues_fixed += count

    if 'all' in fix_types or 'whitespace' in fix_types:
        content, count = fix_whitespace(content)
        if count > 0:
            print(f"{YELLOW}  Fixed whitespace issues{NC}")
            file_issues_fixed += count

    # Check if anything changed
    if content != original_content:
        files_modified += 1
        issues_fixed += file_issues_fixed

        if interactive:
            print(f"\n{YELLOW}Proposed changes for {file_path}:{NC}")
            show_diff(original_content, content, file_path)
            response = input("Apply these changes? [y/N] ").strip().lower()

            if response == 'y':
                if backup:
                    create_backup(file_path)
                file_path.write_text(content, encoding='utf-8')
                print(f"{GREEN}✓ Applied fixes to {file_path}{NC}")
            else:
                print("Skipped")
                return False
        else:
            if backup:
                create_backup(file_path)
            file_path.write_text(content, encoding='utf-8')
            print(f"{GREEN}✓ Fixed: {file_path}{NC}")

        return True
    else:
        if verbose:
            print("  No issues found")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Auto-format AsciiDoc files to fix common formatting issues.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Fix Types:
  lists      - Add blank lines before lists
  xref       - Convert <<>> syntax to xref:
  headers    - Add missing header attributes
  whitespace - Fix trailing whitespace and ensure final newline
  all        - Apply all fixes (default)

Examples:
  %(prog)s                                    # Format all .adoc files in current directory
  %(prog)s docs/                             # Format all files in docs directory
  %(prog)s -t lists -t xref file.adoc       # Fix only lists and xrefs in specific file
  %(prog)s -i --no-backup                   # Interactive mode without backups
'''
    )

    parser.add_argument('path', nargs='?', default='.',
                        help='File or directory to format (default: current directory)')
    parser.add_argument('-t', '--type', action='append', dest='fix_types',
                        choices=['all', 'lists', 'xref', 'headers', 'whitespace'],
                        help='Fix types (can be specified multiple times)')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Ask before applying each fix')
    parser.add_argument('-b', '--no-backup', action='store_true',
                        help="Don't create backup files")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed progress')

    args = parser.parse_args()

    # Set defaults
    fix_types = args.fix_types if args.fix_types else ['all']
    backup = not args.no_backup
    target_path = Path(args.path)

    # Check if target exists
    if not target_path.exists():
        print(f"Error: Path '{target_path}' does not exist")
        sys.exit(EXIT_ERROR)

    print(f"{BLUE}AsciiDoc Formatter{NC}")
    print("==================")
    print()

    # Find and process files
    if target_path.is_file():
        if target_path.suffix == '.adoc':
            process_file(target_path, fix_types, backup, args.interactive, args.verbose)
        else:
            print("Error: File must have .adoc extension")
            sys.exit(EXIT_ERROR)
    else:
        # Directory - find all .adoc files
        adoc_files = sorted(target_path.rglob('*.adoc'))
        for file_path in adoc_files:
            process_file(file_path, fix_types, backup, args.interactive, args.verbose)

    # Summary
    print()
    print("Summary:")
    print("--------")
    print(f"Files processed: {files_processed}")
    print(f"Files modified: {files_modified}")
    print(f"Issues fixed: {issues_fixed}")

    sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    main()
