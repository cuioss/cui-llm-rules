#!/usr/bin/env python3
"""
Parse references.toon and extract structured reference data.

Usage:
    python3 parse-references.py <plan-directory>
    python3 parse-references.py <references-file>
    python3 parse-references.py --help

Output: JSON with reference structure including ADRs, interfaces, files, and external docs.

TOON format only - no markdown support.
"""

import argparse
import json
import sys
from pathlib import Path

# Import shared TOON parser
SCRIPT_DIR = Path(__file__).parent
TOON_DIR = SCRIPT_DIR.parent.parent.parent.parent / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(TOON_DIR))

from toon_parser import parse_toon


def find_references_file(path: Path) -> Path:
    """Find references.toon file from path or directory."""
    if path.is_file():
        return path

    # If directory, look for references.toon
    if path.is_dir():
        toon_file = path / 'references.toon'
        if toon_file.exists():
            return toon_file

    return path  # Return original for error handling


def parse_references_toon(content: str) -> dict:
    """Parse TOON format references and return structured data."""
    # Use shared TOON parser
    data = parse_toon(content)

    # Helper to get scalar with default
    def get_scalar(key: str, default: str = '') -> str:
        val = data.get(key)
        if val is None or val == '(not set)':
            return default
        return str(val) if not isinstance(val, str) else val

    # Helper to get list with default
    def get_list(key: str) -> list:
        val = data.get(key)
        if val is None:
            return []
        if isinstance(val, list):
            # Filter out placeholders like "(populated during...)"
            return [item for item in val if isinstance(item, str) and not item.startswith('(')]
        return []

    # Helper to get structured array
    def get_structured_array(key: str) -> list[dict]:
        val = data.get(key)
        if val is None:
            return []
        if isinstance(val, list):
            return [item for item in val if isinstance(item, dict)]
        return []

    # Extract scalars
    issue = get_scalar('issue')
    issue_url = get_scalar('issue_url')
    issue_title = get_scalar('issue_title')
    branch = get_scalar('branch')
    base_branch = get_scalar('base_branch')

    # Extract simple lists
    implementation_files = get_list('implementation_files')
    config_files = get_list('config_files')
    test_files = get_list('test_files')
    dependencies = get_list('dependencies')
    related_plans = get_list('related_plans')

    # Extract structured arrays
    adrs = get_structured_array('adrs')
    interfaces = get_structured_array('interfaces')
    external_docs = get_structured_array('external_docs')

    # Build related_files structure (combine all file types)
    related_files = []
    for f in implementation_files:
        related_files.append({'path': f, 'type': 'implementation'})
    for f in config_files:
        related_files.append({'path': f, 'type': 'config'})
    for f in test_files:
        related_files.append({'path': f, 'type': 'test'})

    # Build external_links from external_docs
    external_links = [{'name': d.get('name', ''), 'url': d.get('url', ''), 'type': 'external'} for d in external_docs]

    # Add type field to adrs and interfaces for consistency
    for adr in adrs:
        adr['type'] = 'adr'
    for iface in interfaces:
        iface['type'] = 'interface'

    # Combine all references
    all_references = related_files + adrs + interfaces + external_links

    return {
        'issue': {
            'id': issue if issue and issue != '(not set)' else '',
            'url': issue_url if issue_url and issue_url != '(not set)' else '',
            'title': issue_title if issue_title and issue_title != '(not set)' else ''
        },
        'branch': branch,
        'base_branch': base_branch or 'main',
        'implementation_files': implementation_files,
        'config_files': config_files,
        'test_files': test_files,
        'adrs': adrs,
        'interfaces': interfaces,
        'external_links': external_links,
        'dependencies': dependencies,
        'related_plans': related_plans,
        'related_files': related_files,
        'all_references': all_references,
        'summary': {
            'total_references': len(all_references),
            'implementation_files_count': len(implementation_files),
            'config_files_count': len(config_files),
            'test_files_count': len(test_files),
            'adrs_count': len(adrs),
            'interfaces_count': len(interfaces),
            'external_links_count': len(external_links),
            'dependencies_count': len(dependencies),
            'related_plans_count': len(related_plans)
        },
        'validation': {
            'has_issue': bool(issue and issue != '(not set)'),
            'has_branch': bool(branch),
            'has_implementation_files': len(implementation_files) > 0,
            'has_test_files': len(test_files) > 0,
            'has_adrs': len(adrs) > 0,
            'has_interfaces': len(interfaces) > 0,
            'has_external_links': len(external_links) > 0
        },
        'format': 'toon'
    }


def parse_references(path: Path) -> dict:
    """Parse references file and return structured data."""
    references_file = find_references_file(path)

    if not references_file.exists():
        return {
            'error': {
                'type': 'file_not_found',
                'message': f'References file not found: {path}'
            }
        }

    content = references_file.read_text()
    return parse_references_toon(content)


def main():
    parser = argparse.ArgumentParser(
        description='Parse references.toon and extract structured reference data.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
TOON format only - accepts plan directory or references.toon file path.

Output JSON structure:
{
  "issue": {"id": "...", "url": "...", "title": "..."},
  "branch": "...",
  "base_branch": "main",
  "implementation_files": [...],
  "config_files": [...],
  "test_files": [...],
  "adrs": [{"id": "...", "path": "...", "status": "..."}],
  "interfaces": [{"name": "...", "path": "..."}],
  "external_links": [{"name": "...", "url": "..."}],
  "dependencies": [...],
  "related_plans": [...],
  "related_files": [...],
  "all_references": [...],
  "summary": {...},
  "validation": {...},
  "format": "toon"
}
"""
    )
    parser.add_argument('path', help='Path to plan directory or references.toon file')

    args = parser.parse_args()

    path = Path(args.path)
    result = parse_references(path)

    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
