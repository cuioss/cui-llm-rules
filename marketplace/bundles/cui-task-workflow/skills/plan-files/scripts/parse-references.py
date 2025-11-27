#!/usr/bin/env python3
"""
Parse references.md and extract structured reference data.

Usage:
    python3 parse-references.py <references-file>
    python3 parse-references.py --help

Output: JSON with reference structure including standards, ADRs, interfaces, and related files.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_standards_section(content: str) -> list[dict]:
    """Extract standards from the Standards section."""
    standards = []

    # Find the Standards section
    section_pattern = r'##\s*(?:Loaded\s+)?Standards\s*\n(.*?)(?=\n##|\n---|\Z)'
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    if not section_match:
        return standards

    section_content = section_match.group(1)

    # Parse list items: - [Name](path) or - Name: path
    item_pattern = r'-\s*(?:\[([^\]]+)\]\(([^)]+)\)|([^:\n]+):\s*([^\n]+))'
    matches = re.finditer(item_pattern, section_content)

    for match in matches:
        if match.group(1):  # Markdown link format
            name = match.group(1).strip()
            path = match.group(2).strip()
        else:  # Name: path format
            name = match.group(3).strip()
            path = match.group(4).strip()

        standards.append({
            'name': name,
            'path': path,
            'type': 'standard'
        })

    return standards


def parse_adr_section(content: str) -> list[dict]:
    """Extract ADRs from the ADR section."""
    adrs = []

    # Find ADR section
    section_pattern = r'##\s*(?:Related\s+)?ADRs?\s*\n(.*?)(?=\n##|\n---|\Z)'
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    if not section_match:
        return adrs

    section_content = section_match.group(1)

    # Parse list items with optional status
    # Format: - [ADR-001](path) or - [ADR-001](path) - Status: proposed
    item_pattern = r'-\s*\[([^\]]+)\]\(([^)]+)\)(?:\s*-\s*Status:\s*(\w+))?'
    matches = re.finditer(item_pattern, section_content)

    for match in matches:
        adr_id = match.group(1).strip()
        path = match.group(2).strip()
        status = match.group(3).strip().lower() if match.group(3) else 'unknown'

        adrs.append({
            'id': adr_id,
            'path': path,
            'status': status,
            'type': 'adr'
        })

    return adrs


def parse_interface_section(content: str) -> list[dict]:
    """Extract interfaces from the Interface section."""
    interfaces = []

    # Find Interface section
    section_pattern = r'##\s*(?:Related\s+)?Interfaces?\s*\n(.*?)(?=\n##|\n---|\Z)'
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    if not section_match:
        return interfaces

    section_content = section_match.group(1)

    # Parse list items
    item_pattern = r'-\s*\[([^\]]+)\]\(([^)]+)\)'
    matches = re.finditer(item_pattern, section_content)

    for match in matches:
        name = match.group(1).strip()
        path = match.group(2).strip()

        interfaces.append({
            'name': name,
            'path': path,
            'type': 'interface'
        })

    return interfaces


def parse_related_files_section(content: str) -> list[dict]:
    """Extract related files from the Related Files section."""
    files = []

    # Find Related Files section
    section_pattern = r'##\s*Related\s+Files?\s*\n(.*?)(?=\n##|\n---|\Z)'
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    if not section_match:
        return files

    section_content = section_match.group(1)

    # Parse list items with optional description
    # Format: - [file.java](path) - Description
    item_pattern = r'-\s*\[([^\]]+)\]\(([^)]+)\)(?:\s*-\s*(.+))?'
    matches = re.finditer(item_pattern, section_content)

    for match in matches:
        name = match.group(1).strip()
        path = match.group(2).strip()
        description = match.group(3).strip() if match.group(3) else ''

        files.append({
            'name': name,
            'path': path,
            'description': description,
            'type': 'file'
        })

    return files


def parse_external_links_section(content: str) -> list[dict]:
    """Extract external links from the External Links section."""
    links = []

    # Find External Links section
    section_pattern = r'##\s*External\s+(?:Links?|References?)\s*\n(.*?)(?=\n##|\n---|\Z)'
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    if not section_match:
        return links

    section_content = section_match.group(1)

    # Parse list items
    item_pattern = r'-\s*\[([^\]]+)\]\(([^)]+)\)'
    matches = re.finditer(item_pattern, section_content)

    for match in matches:
        name = match.group(1).strip()
        url = match.group(2).strip()

        links.append({
            'name': name,
            'url': url,
            'type': 'external'
        })

    return links


def parse_references(references_file: Path) -> dict:
    """Parse references.md and return structured data."""
    if not references_file.exists():
        return {
            'error': {
                'type': 'file_not_found',
                'message': f'References file not found: {references_file}'
            }
        }

    content = references_file.read_text()

    standards = parse_standards_section(content)
    adrs = parse_adr_section(content)
    interfaces = parse_interface_section(content)
    related_files = parse_related_files_section(content)
    external_links = parse_external_links_section(content)

    # Combine all references
    all_references = standards + adrs + interfaces + related_files + external_links

    return {
        'standards': standards,
        'adrs': adrs,
        'interfaces': interfaces,
        'related_files': related_files,
        'external_links': external_links,
        'all_references': all_references,
        'summary': {
            'total_references': len(all_references),
            'standards_count': len(standards),
            'adrs_count': len(adrs),
            'interfaces_count': len(interfaces),
            'related_files_count': len(related_files),
            'external_links_count': len(external_links)
        },
        'validation': {
            'has_standards': len(standards) > 0,
            'has_adrs': len(adrs) > 0,
            'has_interfaces': len(interfaces) > 0,
            'has_related_files': len(related_files) > 0,
            'has_external_links': len(external_links) > 0
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Parse references.md and extract structured reference data.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "standards": [...],
  "adrs": [...],
  "interfaces": [...],
  "related_files": [...],
  "external_links": [...],
  "all_references": [...],
  "summary": {...},
  "validation": {...}
}
"""
    )
    parser.add_argument('references_file', help='Path to references.md file')

    args = parser.parse_args()

    references_file = Path(args.references_file)
    result = parse_references(references_file)

    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
