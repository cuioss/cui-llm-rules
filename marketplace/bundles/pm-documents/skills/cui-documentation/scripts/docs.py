#!/usr/bin/env python3
"""
AsciiDoc documentation operations - stats, validation, formatting, and analysis.

Usage:
    docs.py stats [OPTIONS] [directory]
    docs.py validate [OPTIONS] [path]
    docs.py format [OPTIONS] [path]
    docs.py verify-links [OPTIONS]
    docs.py classify-links [OPTIONS]
    docs.py review [OPTIONS]
    docs.py analyze-tone [OPTIONS]
    docs.py --help

Subcommands:
    stats           Generate documentation statistics and metrics
    validate        Validate AsciiDoc files for compliance
    format          Auto-fix common AsciiDoc formatting issues
    verify-links    Verify all links in AsciiDoc files
    classify-links  Classify broken links to reduce false positives
    review          Analyze content for quality issues
    analyze-tone    Detect promotional language and missing sources
"""

import argparse
import fnmatch
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Exit codes
EXIT_SUCCESS = 0
EXIT_NON_COMPLIANT = 1
EXIT_ERROR = 2

# Color codes for output
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color


# ============================================================================
# STATS SUBCOMMAND
# ============================================================================

def format_size(size: int) -> str:
    """Format file size in human-readable format."""
    if size > 1048576:
        return f"{size // 1048576} MB"
    elif size > 1024:
        return f"{size // 1024} KB"
    else:
        return f"{size} B"


def analyze_file_stats(file_path: Path) -> dict:
    """Analyze a single AsciiDoc file and return statistics."""
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

    section_pattern = re.compile(r'^(=+) ')
    for line in lines:
        match = section_pattern.match(line)
        if match:
            stats['sections'] += 1
            depth = len(match.group(1))
            if depth > stats['max_depth']:
                stats['max_depth'] = depth

    stats['xrefs'] = len(re.findall(r'xref:', content))
    stats['images'] = len(re.findall(r'image::', content))
    stats['code_blocks'] = len(re.findall(r'^\[source', content, re.MULTILINE))
    stats['tables'] = len(re.findall(r'^\|===', content, re.MULTILINE))
    stats['lists'] = len(re.findall(r'^[[:space:]]*(\*|[0-9]+\.|.*::)', content, re.MULTILINE))

    return stats


def cmd_stats(args):
    """Handle stats subcommand."""
    target_dir = Path(args.directory)

    if not target_dir.is_dir():
        print(f"Error: Directory '{target_dir}' does not exist")
        return EXIT_ERROR

    file_stats = []
    dir_stats = {}
    totals = {'lines': 0, 'words': 0, 'sections': 0, 'xrefs': 0, 'images': 0, 'code_blocks': 0, 'tables': 0, 'lists': 0}

    for file_path in sorted(target_dir.rglob('*.adoc')):
        stats = analyze_file_stats(file_path)
        file_stats.append(stats)

        for key in totals:
            totals[key] += stats.get(key, 0)

        dir_name = str(file_path.parent)
        if dir_name not in dir_stats:
            dir_stats[dir_name] = {'files': 0, 'lines': 0, 'words': 0, 'size': 0}
        dir_stats[dir_name]['files'] += 1
        dir_stats[dir_name]['lines'] += stats['lines']
        dir_stats[dir_name]['words'] += stats['words']
        dir_stats[dir_name]['size'] += stats['size']

    total_files = len(file_stats)

    if args.format == 'json':
        output = {
            'metadata': {'directory': str(target_dir), 'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'total_files': total_files},
            'summary': {**totals, 'averages': {'lines_per_file': totals['lines'] // total_files if total_files else 0, 'words_per_file': totals['words'] // total_files if total_files else 0}},
            'directories': dir_stats,
        }
        if args.details:
            output['files'] = {s['file']: {k: v for k, v in s.items() if k != 'file'} for s in file_stats}
        print(json.dumps(output, indent=2))
    else:
        print(f"{BLUE}Documentation Statistics{NC}")
        print("=" * 30)
        print(f"Directory: {target_dir}")
        print(f"Total files: {total_files}")
        print(f"Total lines: {totals['lines']:,}")
        print(f"Total words: {totals['words']:,}")

    return EXIT_SUCCESS


# ============================================================================
# VALIDATE SUBCOMMAND
# ============================================================================

REQUIRED_ATTRS = ['= ', ':toc: left', ':toclevels: 3', ':toc-title: Table of Contents', ':sectnums:', ':source-highlighter: highlight.js']


def check_list_formatting(content: str) -> list:
    """Check for list formatting issues."""
    lines = content.split('\n')
    issues = []
    in_code_block = False
    prev_was_blank = True
    in_list = False
    prev_line = ""

    for i, line in enumerate(lines, start=1):
        if line == '----':
            in_code_block = not in_code_block
        current_is_blank = len(line.strip()) == 0

        starts_new_list = False
        list_type = ""
        if not in_code_block:
            if re.match(r'^[\*\-\+] ', line):
                starts_new_list, list_type = True, "unordered"
            elif re.match(r'^[0-9]+\. ', line):
                starts_new_list, list_type = True, "ordered"
            elif re.match(r'^[^:]+::', line):
                starts_new_list, list_type = True, "definition"
            elif re.match(r'^\. ', line) and not in_list:
                starts_new_list, list_type = True, "numbered"

        continuing_list = False
        if not in_code_block and in_list:
            if re.match(r'^[\*\-\+] ', line) or re.match(r'^\*\* ', line) or re.match(r'^[0-9]+\. ', line) or re.match(r'^\. ', line) or current_is_blank:
                continuing_list = True

        if starts_new_list and not prev_was_blank and i > 1 and not in_list:
            issues.append((i, list_type, prev_line[:50]))

        if starts_new_list:
            in_list = True
        elif not continuing_list and not current_is_blank:
            in_list = False

        prev_line = line
        prev_was_blank = current_is_blank

    return issues


def check_file_compliance(file_path: Path) -> dict:
    """Check a single AsciiDoc file for compliance."""
    content = file_path.read_text(encoding='utf-8')
    result = {'file': str(file_path), 'compliant': True, 'errors': 0, 'warnings': 0, 'issues': [], 'missing_attrs': [], 'list_issues': [], 'xref_count': 0}

    for attr in REQUIRED_ATTRS:
        if attr not in content:
            result['missing_attrs'].append(attr)
            result['issues'].append({'type': 'missing_header', 'severity': 'error', 'attribute': attr})
            result['errors'] += 1
            result['compliant'] = False

    list_issues = check_list_formatting(content)
    if list_issues:
        result['list_issues'] = list_issues
        for line_num, list_type, context in list_issues:
            result['issues'].append({'type': 'list_formatting', 'severity': 'warning', 'line': line_num, 'list_type': list_type, 'context': context})
        result['warnings'] += len(list_issues)
        result['compliant'] = False

    xref_count = len(re.findall(r'<<.*\.adoc.*>>', content))
    if xref_count > 0:
        result['xref_count'] = xref_count
        result['issues'].append({'type': 'deprecated_xref', 'severity': 'warning', 'count': xref_count})
        result['warnings'] += xref_count
        result['compliant'] = False

    return result


def cmd_validate(args):
    """Handle validate subcommand."""
    check_path = Path(args.path)

    if not check_path.exists():
        if args.format == 'json':
            print(json.dumps({'error': 'Path not found', 'path': str(check_path)}))
        else:
            print(f"Error: Path '{check_path}' does not exist.")
        return EXIT_ERROR

    results = []
    if check_path.is_file():
        adoc_files = [check_path] if check_path.suffix == '.adoc' else []
    else:
        adoc_files = sorted(check_path.rglob('*.adoc'))

    ignore_patterns = args.ignore_patterns or ['asciidoc-standards.adoc']
    for file_path in adoc_files:
        if any(fnmatch.fnmatch(file_path.name, p) for p in ignore_patterns):
            continue
        results.append(check_file_compliance(file_path))

    summary = {
        'total_files': len(results),
        'non_compliant_files': sum(1 for r in results if not r['compliant']),
        'compliant_files': sum(1 for r in results if r['compliant']),
        'total_errors': sum(r['errors'] for r in results),
        'total_warnings': sum(r['warnings'] for r in results),
    }

    if args.format == 'json':
        output = {'directory': str(check_path), 'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'summary': summary, 'files': [r for r in results if not r['compliant']]}
        print(json.dumps(output, indent=2))
    else:
        print(f"Summary: {summary['total_files']} files, {summary['non_compliant_files']} non-compliant, {summary['total_errors']} errors, {summary['total_warnings']} warnings")

    return EXIT_NON_COMPLIANT if summary['total_errors'] > 0 or summary['total_warnings'] > 0 else EXIT_SUCCESS


# ============================================================================
# FORMAT SUBCOMMAND
# ============================================================================

def fix_lists(content: str) -> Tuple[str, int]:
    """Fix list formatting by adding blank lines before lists."""
    lines = content.split('\n')
    result = []
    fixed_count = 0
    in_code_block = False
    prev_was_blank = True
    in_list = False

    for i, line in enumerate(lines):
        if line == '----':
            in_code_block = not in_code_block
        current_is_blank = len(line.strip()) == 0

        starts_new_list = False
        if not in_code_block:
            if re.match(r'^[\*\-\+] ', line) or re.match(r'^[0-9]+\. ', line) or re.match(r'^[^:]+::', line) or (re.match(r'^\. ', line) and not in_list):
                starts_new_list = True

        continuing_list = False
        if not in_code_block and in_list:
            if re.match(r'^[\*\-\+] ', line) or re.match(r'^\*\* ', line) or re.match(r'^[0-9]+\. ', line) or current_is_blank:
                continuing_list = True

        if starts_new_list and not prev_was_blank and i > 0 and not in_list:
            result.append('')
            fixed_count += 1

        result.append(line)

        if starts_new_list:
            in_list = True
        elif not continuing_list and not current_is_blank:
            in_list = False

        prev_was_blank = current_is_blank

    return '\n'.join(result), fixed_count


def fix_xrefs(content: str) -> Tuple[str, int]:
    """Fix cross-references by converting <<>> syntax to xref:."""
    pattern = r'<<([^,>]*),([^>]*)>>'
    fixed_content, count = re.subn(pattern, r'xref:\1[\2]', content)
    return fixed_content, count


def fix_whitespace(content: str) -> Tuple[str, int]:
    """Fix whitespace issues."""
    original = content
    lines = [line.rstrip() for line in content.split('\n')]
    content = '\n'.join(lines)
    if not content.endswith('\n'):
        content += '\n'
    return content, 1 if content != original else 0


def cmd_format(args):
    """Handle format subcommand."""
    target_path = Path(args.path)

    if not target_path.exists():
        print(f"Error: Path '{target_path}' does not exist")
        return EXIT_ERROR

    files_processed = 0
    files_modified = 0
    issues_fixed = 0
    fix_types = args.fix_types if args.fix_types else ['all']

    def process_file(file_path: Path):
        nonlocal files_processed, files_modified, issues_fixed
        files_processed += 1
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        file_issues = 0

        if 'all' in fix_types or 'lists' in fix_types:
            content, count = fix_lists(content)
            file_issues += count
        if 'all' in fix_types or 'xref' in fix_types:
            content, count = fix_xrefs(content)
            file_issues += count
        if 'all' in fix_types or 'whitespace' in fix_types:
            content, count = fix_whitespace(content)
            file_issues += count

        if content != original_content:
            files_modified += 1
            issues_fixed += file_issues
            if not args.no_backup:
                shutil.copy2(file_path, file_path.with_suffix(file_path.suffix + '.bak'))
            file_path.write_text(content, encoding='utf-8')
            print(f"{GREEN}Fixed: {file_path}{NC}")

    if target_path.is_file():
        if target_path.suffix == '.adoc':
            process_file(target_path)
    else:
        for file_path in sorted(target_path.rglob('*.adoc')):
            process_file(file_path)

    print(f"\nSummary: {files_processed} processed, {files_modified} modified, {issues_fixed} issues fixed")
    return EXIT_SUCCESS


# ============================================================================
# VERIFY-LINKS SUBCOMMAND
# ============================================================================

@dataclass
class Link:
    file: str
    line_num: int
    link_text: str
    link_type: str
    target: str = ""
    anchor: str = ""
    label: str = ""


@dataclass
class Issue:
    file: str
    line_num: int
    link_text: str
    issue_type: str
    description: str
    context: str
    suggested_fix: str = ""


def extract_anchors_from_file(filepath: str) -> Set[str]:
    """Extract all valid anchors from an AsciiDoc file."""
    anchors = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        anchors.update(re.findall(r'\[\[([^\]]+)\]\]', line))
        anchors.update(re.findall(r'\[#([^\]]+)\]', line))
        section_match = re.match(r'^(={1,6})\s+(.+)$', line.strip())
        if section_match:
            title = section_match.group(2)
            title = re.sub(r'\{[^\}]+\}', '', title)
            title = re.sub(r'link:https?://[^\[]+\[[^\]]+\]', '', title)
            anchor = title.strip().lower()
            anchor = re.sub(r'[^\w\s-]', '', anchor)
            anchor = re.sub(r'\s+', '-', anchor)
            anchor = re.sub(r'-+', '-', anchor).strip('-')
            if anchor:
                anchors.add(anchor)
    return anchors


def extract_links_from_file(filepath: str) -> List[Link]:
    """Extract all links from an AsciiDoc file."""
    links = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('----') or line.strip().startswith('....'):
            in_code_block = not in_code_block
            continue

        for match in re.finditer(r'<<([^,>]+)(?:,([^>]+))?>>', line):
            links.append(Link(file=filepath, line_num=line_num, link_text=match.group(0), link_type='cross-ref', anchor=match.group(1).strip(), label=match.group(2).strip() if match.group(2) else ""))

        for match in re.finditer(r'xref:([^\[]+)\[([^\]]*)\]', line):
            target_full = match.group(1).strip()
            target, anchor = (target_full.split('#', 1) + [""])[:2] if '#' in target_full else (target_full, "")
            links.append(Link(file=filepath, line_num=line_num, link_text=match.group(0), link_type='xref', target=target, anchor=anchor, label=match.group(2).strip()))

        for match in re.finditer(r'<<([^>]*\.adoc[^>]*)>>', line):
            links.append(Link(file=filepath, line_num=line_num, link_text=match.group(0), link_type='deprecated', target=match.group(1)))

    return links


def verify_links(files: List[str]) -> Tuple[List[Link], List[Issue]]:
    """Verify all links in all files."""
    all_links = []
    issues = []
    anchor_cache = {f: extract_anchors_from_file(f) for f in files}

    for filepath in files:
        links = extract_links_from_file(filepath)
        all_links.extend(links)

        for link in links:
            if link.link_type == 'cross-ref' and link.anchor not in anchor_cache[filepath]:
                issues.append(Issue(file=filepath, line_num=link.line_num, link_text=link.link_text, issue_type='broken', description=f"Anchor '{link.anchor}' not found"))
            elif link.link_type == 'xref':
                target_path = os.path.normpath(os.path.join(os.path.dirname(filepath), link.target)) if link.target else filepath
                if not os.path.exists(target_path):
                    issues.append(Issue(file=filepath, line_num=link.line_num, link_text=link.link_text, issue_type='broken', description=f"Target file '{target_path}' not found"))
                elif link.anchor:
                    if target_path not in anchor_cache:
                        anchor_cache[target_path] = extract_anchors_from_file(target_path)
                    if link.anchor not in anchor_cache[target_path]:
                        issues.append(Issue(file=filepath, line_num=link.line_num, link_text=link.link_text, issue_type='broken', description=f"Anchor '{link.anchor}' not found in '{target_path}'"))
            elif link.link_type == 'deprecated':
                issues.append(Issue(file=filepath, line_num=link.line_num, link_text=link.link_text, issue_type='format_violation', description="Deprecated syntax - use xref:", suggested_fix=f"xref:{link.target.rstrip('#,')}[Label]"))

    return all_links, issues


def cmd_verify_links(args):
    """Handle verify-links subcommand."""
    # Check mutual exclusivity
    if args.file and args.directory:
        print("Error: Cannot specify both --file and --directory", file=sys.stderr)
        return EXIT_ERROR

    target_path = args.file if args.file else (args.directory if args.directory else '.')
    recursive = args.recursive if args.directory else (not args.file)

    path = Path(target_path)
    if not path.exists():
        print(f"Error: Path '{target_path}' not found", file=sys.stderr)
        return EXIT_ERROR

    files = []
    if path.is_file():
        files = [str(path)]
    elif recursive:
        files = [str(f) for f in path.rglob('*.adoc') if 'target' not in f.parts]
    else:
        files = [str(f) for f in path.glob('*.adoc')]

    if not files:
        print(f"No AsciiDoc files found in {target_path}", file=sys.stderr)
        return EXIT_ERROR

    all_links, issues = verify_links(files)
    broken = [i for i in issues if i.issue_type == 'broken']
    violations = [i for i in issues if i.issue_type == 'format_violation']

    output = {
        'status': 'success' if not issues else 'failure',
        'data': {'files_processed': len(files), 'total_links': len(all_links), 'broken_links': len(broken), 'format_violations': len(violations), 'issues': [{'file': i.file, 'line': i.line_num, 'link': i.link_text, 'type': i.issue_type, 'description': i.description} for i in issues]},
        'metrics': {'valid_links': len(all_links) - len(issues)}
    }
    print(json.dumps(output, indent=2))

    if args.report:
        Path(args.report).write_text(json.dumps(output, indent=2))

    return EXIT_SUCCESS if not issues else EXIT_NON_COMPLIANT


# ============================================================================
# CLASSIFY-LINKS SUBCOMMAND
# ============================================================================

def categorize_broken_link(issue: Dict[str, Any]) -> str:
    """Categorize a broken link issue."""
    link = issue.get('link', '')
    if link.startswith('<<') or '#' in link:
        return 'likely-false-positive'
    if any(p in link.lower() for p in ['localhost', '127.0.0.1', '0.0.0.0']):
        return 'likely-false-positive'
    if link.startswith('file://'):
        return 'likely-false-positive'
    if any(g in link for g in ['target/', 'build/', 'dist/']):
        return 'likely-false-positive'
    if link.startswith('http://') or link.startswith('https://'):
        return 'must-verify-manual'
    return 'must-verify-manual'


def cmd_classify_links(args):
    """Handle classify-links subcommand."""
    try:
        if args.input:
            with open(args.input, 'r') as f:
                input_data = json.load(f)
        else:
            input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_ERROR

    issues = input_data.get('issues', input_data.get('data', {}).get('issues', []))
    categorized = {'likely-false-positive': [], 'must-verify-manual': [], 'definitely-broken': []}

    for issue in issues:
        category = categorize_broken_link(issue)
        issue['category'] = category
        categorized[category].append(issue)

    result = {
        'summary': {'total_issues': len(issues), 'likely_false_positive_count': len(categorized['likely-false-positive']), 'must_verify_manual_count': len(categorized['must-verify-manual']), 'definitely_broken_count': len(categorized['definitely-broken'])},
        'categorized_issues': categorized
    }

    output_json = json.dumps(result, indent=2 if args.pretty else None)
    if args.output:
        Path(args.output).write_text(output_json)
    else:
        print(output_json)

    return EXIT_SUCCESS


# ============================================================================
# REVIEW SUBCOMMAND
# ============================================================================

MARKETING_PATTERNS = [
    (r'\b(amazing|incredible|revolutionary|magical|awesome)\b', 'promotional_adjective'),
    (r'\b(powerful|robust|enterprise-grade|world-class|best-in-class)\b', 'qualification_buzzword'),
    (r'\b(blazing[-\s]?fast|lightning[-\s]?fast|ultra[-\s]?fast)\b', 'performance_buzzword'),
]

COMPLETENESS_PATTERNS = [
    (r'^\s*(\*\s*)?TODO:?\s', 'todo_marker'),
    (r'^\s*(\*\s*)?FIXME:?\s', 'fixme_marker'),
    (r'\bwork\s+in\s+progress\b', 'wip_text'),
    (r'\bcoming\s+soon\b', 'placeholder_text'),
]


def analyze_content_line(line: str, line_number: int, file_path: str) -> List[Dict[str, Any]]:
    """Analyze a single line for content issues."""
    issues = []

    for pattern, issue_type in MARKETING_PATTERNS:
        for match in re.finditer(pattern, line, re.IGNORECASE):
            issues.append({'file': file_path, 'line': line_number, 'type': 'tone', 'subtype': issue_type, 'severity': 'high', 'text': match.group(), 'message': f"Marketing language: '{match.group()}'"})

    for pattern, issue_type in COMPLETENESS_PATTERNS:
        for match in re.finditer(pattern, line, re.IGNORECASE):
            issues.append({'file': file_path, 'line': line_number, 'type': 'completeness', 'subtype': issue_type, 'severity': 'high', 'text': match.group(), 'message': f"Completeness issue: {issue_type}"})

    return issues


def cmd_review(args):
    """Handle review subcommand."""
    if not args.file and not args.directory:
        print("Error: --file or --directory required", file=sys.stderr)
        return EXIT_ERROR

    results = []
    paths = [Path(args.file)] if args.file else list(Path(args.directory).glob('**/*.adoc' if args.recursive else '*.adoc'))

    for file_path in paths:
        if 'target' in file_path.parts or not file_path.exists():
            continue

        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        all_issues = []
        in_code_block = False

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('----'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            all_issues.extend(analyze_content_line(line, line_num, str(file_path)))

        results.append({'file': str(file_path), 'issues': all_issues, 'issue_count': len(all_issues)})

    all_issues = [i for r in results for i in r['issues']]
    output = {
        'status': 'success',
        'data': {'files_analyzed': len(results), 'total_issues': len(all_issues), 'issues': all_issues},
        'metrics': {'tone_issues': len([i for i in all_issues if i['type'] == 'tone']), 'completeness_issues': len([i for i in all_issues if i['type'] == 'completeness'])}
    }

    output_json = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).write_text(output_json)
    else:
        print(output_json)

    return EXIT_SUCCESS


# ============================================================================
# ANALYZE-TONE SUBCOMMAND
# ============================================================================

PROMOTIONAL_PATTERNS = [
    (r'\b(best|greatest|ultimate|perfect|ideal)\b', 'superlative'),
    (r'\b(leading|top|premier|superior)\b', 'comparative_superlative'),
    (r'\b(enterprise-grade|production-ready|industry-leading|world-class)\b', 'buzzword'),
    (r'\b(powerful|robust|elegant|beautiful|amazing|awesome)\b', 'subjective'),
]

PERFORMANCE_PATTERNS = [r'\b(faster|slower|quicker)\s+than\b', r'\b\d+x\s+(faster|slower|more|less)\b', r'\b(sub-millisecond|millisecond|nanosecond)\b']


def cmd_analyze_tone(args):
    """Handle analyze-tone subcommand."""
    if not args.file and not args.directory:
        print("Error: --file or --directory required", file=sys.stderr)
        return EXIT_ERROR

    all_issues = []

    def analyze_file(file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith(('----', '....', '//', ':', '=')):
                continue

            for pattern, category in PROMOTIONAL_PATTERNS:
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    all_issues.append({'file': file_path, 'line': line_num, 'text': match.group(0), 'category': 'promotional', 'subcategory': category})

            for pattern in PERFORMANCE_PATTERNS:
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    all_issues.append({'file': file_path, 'line': line_num, 'text': match.group(0), 'category': 'performance_claim'})

    if args.file:
        analyze_file(args.file)
    else:
        for f in Path(args.directory).glob('*.adoc'):
            if 'target' not in f.parts:
                analyze_file(str(f))

    result = {
        'summary': {'total_issues': len(all_issues), 'promotional_count': len([i for i in all_issues if i['category'] == 'promotional']), 'performance_claim_count': len([i for i in all_issues if i['category'] == 'performance_claim'])},
        'all_issues': all_issues
    }

    output_json = json.dumps(result, indent=2 if args.pretty else None)
    if args.output:
        Path(args.output).write_text(output_json)
    else:
        print(output_json)

    return EXIT_SUCCESS


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AsciiDoc documentation operations", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # stats subcommand
    stats_parser = subparsers.add_parser("stats", help="Generate documentation statistics")
    stats_parser.add_argument('directory', nargs='?', default='.', help='Directory to analyze')
    stats_parser.add_argument('-f', '--format', dest='format', default='console', choices=['console', 'json'], help='Output format')
    stats_parser.add_argument('-d', '--details', action='store_true', help='Include detailed per-file statistics')
    stats_parser.set_defaults(func=cmd_stats)

    # validate subcommand
    validate_parser = subparsers.add_parser("validate", help="Validate AsciiDoc files for compliance")
    validate_parser.add_argument('path', nargs='?', default='standards', help='File or directory to check')
    validate_parser.add_argument('-f', '--format', dest='format', default='console', choices=['console', 'json'], help='Output format')
    validate_parser.add_argument('-i', '--ignore', action='append', dest='ignore_patterns', help='Ignore pattern')
    validate_parser.set_defaults(func=cmd_validate)

    # format subcommand
    format_parser = subparsers.add_parser("format", help="Auto-fix AsciiDoc formatting issues")
    format_parser.add_argument('path', nargs='?', default='.', help='File or directory to format')
    format_parser.add_argument('-t', '--type', action='append', dest='fix_types', choices=['all', 'lists', 'xref', 'whitespace'], help='Fix types')
    format_parser.add_argument('-b', '--no-backup', action='store_true', help="Don't create backup files")
    format_parser.set_defaults(func=cmd_format)

    # verify-links subcommand
    links_parser = subparsers.add_parser("verify-links", help="Verify links in AsciiDoc files")
    links_parser.add_argument('--file', type=str, help='Single file to verify')
    links_parser.add_argument('--directory', type=str, help='Directory to verify')
    links_parser.add_argument('--recursive', action='store_true', help='Scan subdirectories')
    links_parser.add_argument('--report', type=str, help='Output report file')
    links_parser.set_defaults(func=cmd_verify_links)

    # classify-links subcommand
    classify_parser = subparsers.add_parser("classify-links", help="Classify broken links to reduce false positives")
    classify_parser.add_argument('--input', type=str, help='Input JSON file')
    classify_parser.add_argument('--output', type=str, help='Output JSON file')
    classify_parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    classify_parser.set_defaults(func=cmd_classify_links)

    # review subcommand
    review_parser = subparsers.add_parser("review", help="Analyze content for quality issues")
    review_parser.add_argument('--file', '-f', type=str, help='Single file to analyze')
    review_parser.add_argument('--directory', '-d', type=str, help='Directory to analyze')
    review_parser.add_argument('--recursive', '-r', action='store_true', help='Analyze subdirectories')
    review_parser.add_argument('--output', '-o', type=str, help='Output file')
    review_parser.set_defaults(func=cmd_review)

    # analyze-tone subcommand
    tone_parser = subparsers.add_parser("analyze-tone", help="Detect promotional language and missing sources")
    tone_parser.add_argument('--file', type=str, help='Single file to analyze')
    tone_parser.add_argument('--directory', type=str, help='Directory to analyze')
    tone_parser.add_argument('--output', type=str, help='Output JSON file')
    tone_parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    tone_parser.set_defaults(func=cmd_analyze_tone)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
