#!/usr/bin/env python3
"""
Documentation Statistics Generator.

Analyzes AsciiDoc documentation and generates metrics reports.

Usage:
    python3 documentation-stats.py [OPTIONS] [directory]

Options:
    -f, --format FORMAT    Output format: console, json, csv, markdown (default: console)
    -d, --details          Include detailed per-file statistics
    -h, --help             Show this help message

Metrics Collected:
    - File count and sizes
    - Line and word counts
    - Section structure depth
    - Cross-references (xref)
    - Images and media
    - Code blocks
    - Tables
    - Lists
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1

# Color codes
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def format_size(size: int) -> str:
    """Format file size in human-readable format."""
    if size > 1048576:
        return f"{size // 1048576} MB"
    elif size > 1024:
        return f"{size // 1024} KB"
    else:
        return f"{size} B"


def analyze_file(file_path: Path) -> dict:
    """
    Analyze a single AsciiDoc file and return statistics.

    Returns:
        Dict with file statistics
    """
    content = file_path.read_text(encoding='utf-8', errors='replace')
    lines = content.split('\n')

    stats = {
        'file': str(file_path),
        'lines': len(lines),
        'words': len(content.split()),
        'size': file_path.stat().st_size,
        'sections': 0,
        'max_depth': 0,
        'xrefs': 0,
        'images': 0,
        'code_blocks': 0,
        'tables': 0,
        'lists': 0,
    }

    # Count sections and track max depth
    section_pattern = re.compile(r'^(=+) ')
    for line in lines:
        match = section_pattern.match(line)
        if match:
            stats['sections'] += 1
            depth = len(match.group(1))
            if depth > stats['max_depth']:
                stats['max_depth'] = depth

    # Count elements
    stats['xrefs'] = len(re.findall(r'xref:', content))
    stats['images'] = len(re.findall(r'image::', content))
    stats['code_blocks'] = len(re.findall(r'^\[source', content, re.MULTILINE))
    stats['tables'] = len(re.findall(r'^\|===', content, re.MULTILINE))
    stats['lists'] = len(re.findall(r'^[[:space:]]*(\*|[0-9]+\.|.*::)', content, re.MULTILINE))

    return stats


def analyze_directory(target_dir: Path) -> tuple[list, dict, dict]:
    """
    Analyze all AsciiDoc files in a directory.

    Returns:
        Tuple of (file_stats_list, totals_dict, directory_stats_dict)
    """
    file_stats = []
    dir_stats = {}

    totals = {
        'lines': 0,
        'words': 0,
        'sections': 0,
        'xrefs': 0,
        'images': 0,
        'code_blocks': 0,
        'tables': 0,
        'lists': 0,
    }

    # Find and analyze all .adoc files
    adoc_files = sorted(target_dir.rglob('*.adoc'))

    for file_path in adoc_files:
        stats = analyze_file(file_path)
        file_stats.append(stats)

        # Update totals
        totals['lines'] += stats['lines']
        totals['words'] += stats['words']
        totals['sections'] += stats['sections']
        totals['xrefs'] += stats['xrefs']
        totals['images'] += stats['images']
        totals['code_blocks'] += stats['code_blocks']
        totals['tables'] += stats['tables']
        totals['lists'] += stats['lists']

        # Update directory stats
        dir_name = str(file_path.parent)
        if dir_name not in dir_stats:
            dir_stats[dir_name] = {
                'files': 0,
                'lines': 0,
                'words': 0,
                'size': 0,
            }
        dir_stats[dir_name]['files'] += 1
        dir_stats[dir_name]['lines'] += stats['lines']
        dir_stats[dir_name]['words'] += stats['words']
        dir_stats[dir_name]['size'] += stats['size']

    return file_stats, totals, dir_stats


def output_console(file_stats: list, totals: dict, dir_stats: dict,
                   target_dir: str, include_details: bool) -> None:
    """Output results in console format."""
    total_files = len(file_stats)

    print(f"{BLUE}Documentation Statistics{NC}")
    print("=" * 30)
    print(f"Directory: {target_dir}")
    print(f"Generated: {datetime.now()}")
    print()

    # Overall statistics
    print(f"{CYAN}Overall Statistics:{NC}")
    print(f"  Total files: {total_files}")
    print(f"  Total lines: {totals['lines']:,}")
    print(f"  Total words: {totals['words']:,}")

    if total_files > 0:
        print(f"  Average lines/file: {totals['lines'] // total_files}")
        print(f"  Average words/file: {totals['words'] // total_files}")
    print()

    print(f"{CYAN}Content Elements:{NC}")
    print(f"  Sections: {totals['sections']}")
    print(f"  Cross-references: {totals['xrefs']}")
    print(f"  Images: {totals['images']}")
    print(f"  Code blocks: {totals['code_blocks']}")
    print(f"  Tables: {totals['tables']}")
    print(f"  Lists: {totals['lists']}")
    print()

    # Directory breakdown
    print(f"{CYAN}By Directory:{NC}")
    print(f"{'Directory':<35} {'Files':>5} {'Lines':>8} {'Words':>9} {'Size':>10}")
    print("-" * 72)

    for dir_name in sorted(dir_stats.keys()):
        stats = dir_stats[dir_name]
        print(f"{dir_name:<35} {stats['files']:>5} {stats['lines']:>8} "
              f"{stats['words']:>9} {format_size(stats['size']):>10}")

    # Detailed file statistics
    if include_details:
        print()
        print(f"{CYAN}File Details:{NC}")
        print(f"{'File':<35} {'Lines':>5} {'Words':>6} {'Sections':>8} {'XRefs':>6} {'Images':>7} {'Code':>5}")
        print("-" * 80)

        for stats in sorted(file_stats, key=lambda x: x['file']):
            filename = Path(stats['file']).name
            print(f"{filename:<35} {stats['lines']:>5} {stats['words']:>6} "
                  f"{stats['sections']:>8} {stats['xrefs']:>6} {stats['images']:>7} {stats['code_blocks']:>5}")


def output_json(file_stats: list, totals: dict, dir_stats: dict,
                target_dir: str, include_details: bool) -> None:
    """Output results in JSON format."""
    total_files = len(file_stats)

    output = {
        'metadata': {
            'directory': target_dir,
            'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'total_files': total_files,
        },
        'summary': {
            'lines': totals['lines'],
            'words': totals['words'],
            'sections': totals['sections'],
            'cross_references': totals['xrefs'],
            'images': totals['images'],
            'code_blocks': totals['code_blocks'],
            'tables': totals['tables'],
            'lists': totals['lists'],
            'averages': {
                'lines_per_file': totals['lines'] // total_files if total_files > 0 else 0,
                'words_per_file': totals['words'] // total_files if total_files > 0 else 0,
                'sections_per_file': totals['sections'] // total_files if total_files > 0 else 0,
            }
        },
        'directories': dir_stats,
    }

    if include_details:
        output['files'] = {
            stats['file']: {
                'lines': stats['lines'],
                'words': stats['words'],
                'size': stats['size'],
                'sections': stats['sections'],
                'max_depth': stats['max_depth'],
                'xrefs': stats['xrefs'],
                'images': stats['images'],
                'code_blocks': stats['code_blocks'],
                'tables': stats['tables'],
                'lists': stats['lists'],
            }
            for stats in file_stats
        }

    print(json.dumps(output, indent=2))


def output_csv(file_stats: list, totals: dict, dir_stats: dict,
               target_dir: str, include_details: bool) -> None:
    """Output results in CSV format."""
    if include_details:
        print("File,Lines,Words,Size,Sections,MaxDepth,XRefs,Images,CodeBlocks,Tables,Lists")
        for stats in file_stats:
            print(f'"{stats["file"]}",{stats["lines"]},{stats["words"]},{stats["size"]},'
                  f'{stats["sections"]},{stats["max_depth"]},{stats["xrefs"]},{stats["images"]},'
                  f'{stats["code_blocks"]},{stats["tables"]},{stats["lists"]}')
    else:
        print("Directory,Files,Lines,Words,Size")
        for dir_name in sorted(dir_stats.keys()):
            stats = dir_stats[dir_name]
            print(f'"{dir_name}",{stats["files"]},{stats["lines"]},{stats["words"]},{stats["size"]}')


def output_markdown(file_stats: list, totals: dict, dir_stats: dict,
                    target_dir: str, include_details: bool) -> None:
    """Output results in Markdown format."""
    total_files = len(file_stats)

    print("# Documentation Statistics Report")
    print()
    print(f"**Directory:** {target_dir}  ")
    print(f"**Generated:** {datetime.now()}  ")
    print()

    print("## Summary")
    print()
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Total Files | {total_files} |")
    print(f"| Total Lines | {totals['lines']:,} |")
    print(f"| Total Words | {totals['words']:,} |")

    if total_files > 0:
        print(f"| Average Lines/File | {totals['lines'] // total_files} |")
        print(f"| Average Words/File | {totals['words'] // total_files} |")
    print()

    print("## Content Elements")
    print()
    print("| Element | Count |")
    print("|---------|-------|")
    print(f"| Sections | {totals['sections']} |")
    print(f"| Cross-references | {totals['xrefs']} |")
    print(f"| Images | {totals['images']} |")
    print(f"| Code Blocks | {totals['code_blocks']} |")
    print(f"| Tables | {totals['tables']} |")
    print(f"| Lists | {totals['lists']} |")
    print()

    print("## By Directory")
    print()
    print("| Directory | Files | Lines | Words | Size |")
    print("|-----------|-------|-------|-------|------|")

    for dir_name in sorted(dir_stats.keys()):
        stats = dir_stats[dir_name]
        print(f"| {dir_name} | {stats['files']} | {stats['lines']} | "
              f"{stats['words']} | {format_size(stats['size'])} |")


def main():
    parser = argparse.ArgumentParser(
        description='Generate statistics and metrics for AsciiDoc documentation.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Metrics Collected:
  - File count and sizes
  - Line and word counts
  - Section structure depth
  - Cross-references (xref)
  - Images and media
  - Code blocks
  - Tables
  - Lists

Examples:
  %(prog)s                                    # Basic stats for current directory
  %(prog)s -f json -d docs/                  # Detailed JSON report for docs
  %(prog)s -f markdown standards/            # Markdown report for standards
'''
    )

    parser.add_argument('directory', nargs='?', default='.',
                        help='Directory to analyze (default: current directory)')
    parser.add_argument('-f', '--format', dest='output_format', default='console',
                        choices=['console', 'json', 'csv', 'markdown'],
                        help='Output format: console, json, csv, markdown (default: console)')
    parser.add_argument('-d', '--details', action='store_true',
                        help='Include detailed per-file statistics')

    args = parser.parse_args()

    target_dir = Path(args.directory)

    # Validate directory
    if not target_dir.is_dir():
        print(f"Error: Directory '{target_dir}' does not exist")
        sys.exit(EXIT_ERROR)

    if args.output_format == 'console':
        print(f"{BLUE}Analyzing documentation...{NC}", file=sys.stderr)

    # Analyze directory
    file_stats, totals, dir_stats = analyze_directory(target_dir)

    # Output results
    output_funcs = {
        'console': output_console,
        'json': output_json,
        'csv': output_csv,
        'markdown': output_markdown,
    }

    output_func = output_funcs[args.output_format]
    output_func(file_stats, totals, dir_stats, str(target_dir), args.details)

    sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    main()
