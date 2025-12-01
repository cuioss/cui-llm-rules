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
import csv
import io
import json
import sys
from pathlib import Path


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


def parse_toon_scalar(content: str, key: str) -> str:
    """Extract a scalar value from TOON content."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        if ':' in line and not line.endswith(':'):
            k, v = line.split(':', 1)
            if k.strip().lower() == key.lower():
                return v.strip()
    return ''


def parse_toon_simple_list(content: str, key: str) -> list[str]:
    """Parse a simple list like implementation_files[N]: followed by - items."""
    result = []
    in_section = False

    for line in content.splitlines():
        stripped = line.strip()

        # Check for section header like "implementation_files[0]:" or "implementation_files[3]:"
        if stripped.lower().startswith(key.lower()) and '[' in stripped:
            in_section = True
            continue

        # End section on next header or empty array declaration
        if in_section:
            if stripped.startswith('-'):
                item = stripped[1:].strip()
                if item and not item.startswith('('):  # Skip placeholders like "(populated during...)"
                    result.append(item)
            elif stripped and not stripped.startswith('#'):
                # Non-list line ends the section
                if ':' in stripped or '[' in stripped:
                    break

    return result


def parse_toon_structured_array(content: str, key: str, fields: list[str]) -> list[dict]:
    """Parse a structured array like adrs[N]{id,path,status}: followed by CSV rows."""
    result = []
    in_section = False
    section_fields = fields

    for line in content.splitlines():
        stripped = line.strip()

        # Check for section header like "adrs[0]{id,path,status}:"
        if stripped.lower().startswith(key.lower()) and '{' in stripped:
            in_section = True
            # Extract field names from header
            field_match = stripped[stripped.index('{') + 1:stripped.index('}')]
            if field_match:
                section_fields = [f.strip() for f in field_match.split(',')]
            continue

        if in_section:
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
            # End section on next header
            if ':' in stripped and (stripped.endswith(':') or '[' in stripped):
                break
            # Parse CSV row
            if stripped and not stripped.startswith('-'):
                try:
                    reader = csv.reader(io.StringIO(stripped))
                    values = next(reader)
                    if len(values) >= len(section_fields):
                        item = {}
                        for i, field in enumerate(section_fields):
                            item[field] = values[i].strip() if i < len(values) else ''
                        result.append(item)
                except (csv.Error, StopIteration):
                    pass

    return result


def parse_references_toon(content: str) -> dict:
    """Parse TOON format references and return structured data."""
    # Parse scalars
    issue = parse_toon_scalar(content, 'issue')
    issue_url = parse_toon_scalar(content, 'issue_url')
    issue_title = parse_toon_scalar(content, 'issue_title')
    branch = parse_toon_scalar(content, 'branch')
    base_branch = parse_toon_scalar(content, 'base_branch')

    # Parse simple lists
    implementation_files = parse_toon_simple_list(content, 'implementation_files')
    config_files = parse_toon_simple_list(content, 'config_files')
    test_files = parse_toon_simple_list(content, 'test_files')
    dependencies = parse_toon_simple_list(content, 'dependencies')
    related_plans = parse_toon_simple_list(content, 'related_plans')

    # Parse structured arrays
    adrs = parse_toon_structured_array(content, 'adrs', ['id', 'path', 'status'])
    interfaces = parse_toon_structured_array(content, 'interfaces', ['name', 'path'])
    external_docs = parse_toon_structured_array(content, 'external_docs', ['name', 'url'])

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
