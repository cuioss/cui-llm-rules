#!/usr/bin/env python3
"""
Analyze AsciiDoc content for tone issues (promotional language, missing sources, superlatives).

This script performs automated detection of:
- Promotional/marketing language patterns
- Superlatives and subjective phrases
- Missing source citations for factual claims
- Unverified performance/compatibility claims

Output: JSON with flagged sections for Claude to apply ULTRATHINK analysis.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple


# Promotional language patterns
PROMOTIONAL_PATTERNS = [
    # Superlatives
    (r'\b(best|greatest|ultimate|perfect|ideal)\b', 'superlative'),
    (r'\b(leading|top|premier|superior)\b', 'comparative_superlative'),

    # Marketing buzzwords
    (r'\b(enterprise-grade|production-ready|industry-leading|world-class)\b', 'buzzword'),
    (r'\b(cutting-edge|state-of-the-art|next-generation|revolutionary)\b', 'buzzword'),
    (r'\b(game-changing|groundbreaking|innovative|disruptive)\b', 'buzzword'),

    # Subjective adjectives
    (r'\b(powerful|robust|elegant|beautiful|amazing|awesome)\b', 'subjective'),
    (r'\b(blazing-fast|lightning-fast|super-fast|ultra-fast)\b', 'subjective_performance'),
    (r'\b(easy|simple|intuitive|seamless|effortless)\b', 'subjective_usability'),

    # Unverified claims
    (r'\b(proven|trusted|preferred|popular|widely-used)\b', 'unverified_adoption'),
    (r'\b(comprehensive|complete|full|entire)\b', 'unverified_scope'),
]

# Performance claim patterns (require verification)
PERFORMANCE_PATTERNS = [
    r'\b(faster|slower|quicker)\s+than\b',
    r'\b\d+x\s+(faster|slower|more|less)\b',
    r'\b(sub-millisecond|millisecond|nanosecond)\b',
    r'\b\d+\s*(ms|ns|μs|seconds?)\b',
    r'\b(performance|throughput|latency|response\s+time)\b.*\b(improved|better|optimized)\b',
]

# Compatibility/standards claim patterns (require citations)
STANDARDS_PATTERNS = [
    r'\b(implements?|supports?|complies?\s+with|compatible\s+with)\s+[A-Z]{2,}',  # RFC, ISO, etc
    r'\b(RFC|ISO|NIST|OWASP|IEEE)\s+\d+',
    r'\bOAuth\s+[\d.]+\b',
    r'\bOpenID\s+Connect\b',
]

# Source attribution patterns
CITATION_PATTERNS = [
    r'\bhttps?://[^\s\]]+',  # URLs
    r'\blink:https?://[^\[]+\[',  # AsciiDoc links
    r'\bxref:[^\[]+\[',  # Cross-references
]


def read_asciidoc_file(file_path: str) -> List[str]:
    """Read AsciiDoc file and return lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def detect_promotional_language(line: str, line_num: int) -> List[Dict[str, Any]]:
    """Detect promotional/marketing language in line."""
    issues = []

    for pattern, category in PROMOTIONAL_PATTERNS:
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            issues.append({
                'line': line_num,
                'column': match.start(),
                'text': match.group(0),
                'category': 'promotional',
                'subcategory': category,
                'pattern': pattern,
                'full_line': line.strip()
            })

    return issues


def detect_performance_claims(line: str, line_num: int) -> List[Dict[str, Any]]:
    """Detect performance claims that may require verification."""
    issues = []

    for pattern in PERFORMANCE_PATTERNS:
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            issues.append({
                'line': line_num,
                'column': match.start(),
                'text': match.group(0),
                'category': 'performance_claim',
                'requires': 'benchmark_data',
                'full_line': line.strip()
            })

    return issues


def detect_standards_claims(line: str, line_num: int) -> List[Dict[str, Any]]:
    """Detect standards/compatibility claims that require citations."""
    issues = []

    for pattern in STANDARDS_PATTERNS:
        matches = re.finditer(pattern, line, re.IGNORECASE)
        for match in matches:
            issues.append({
                'line': line_num,
                'column': match.start(),
                'text': match.group(0),
                'category': 'standards_claim',
                'requires': 'citation_or_reference',
                'full_line': line.strip()
            })

    return issues


def has_nearby_citation(lines: List[str], line_num: int, context_window: int = 3) -> bool:
    """Check if there's a citation within context_window lines."""
    start = max(0, line_num - context_window)
    end = min(len(lines), line_num + context_window + 1)

    context = ''.join(lines[start:end])

    for pattern in CITATION_PATTERNS:
        if re.search(pattern, context):
            return True

    return False


def detect_missing_sources(lines: List[str], line_num: int, issue: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a claim has nearby source attribution."""
    if issue['category'] in ['performance_claim', 'standards_claim']:
        if not has_nearby_citation(lines, line_num):
            issue['missing_source'] = True
            issue['verification_status'] = 'unverified'
        else:
            issue['missing_source'] = False
            issue['verification_status'] = 'citation_present'

    return issue


def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze AsciiDoc file for content tone issues."""
    lines = read_asciidoc_file(file_path)

    all_issues = []

    for line_num, line in enumerate(lines, start=1):
        # Skip code blocks, comments, and metadata
        if line.strip().startswith(('----', '....',  '//', ':', '=')):
            continue

        # Detect issues
        issues = []
        issues.extend(detect_promotional_language(line, line_num))
        issues.extend(detect_performance_claims(line, line_num))
        issues.extend(detect_standards_claims(line, line_num))

        # Check for missing sources
        for issue in issues:
            issue = detect_missing_sources(lines, line_num - 1, issue)

        all_issues.extend(issues)

    # Categorize by type
    categorized = {
        'promotional': [],
        'performance_claim': [],
        'standards_claim': [],
        'missing_sources': []
    }

    for issue in all_issues:
        category = issue['category']
        if category in categorized:
            categorized[category].append(issue)

        if issue.get('missing_source'):
            categorized['missing_sources'].append(issue)

    summary = {
        'file': file_path,
        'total_issues': len(all_issues),
        'promotional_count': len(categorized['promotional']),
        'performance_claim_count': len(categorized['performance_claim']),
        'standards_claim_count': len(categorized['standards_claim']),
        'missing_sources_count': len(categorized['missing_sources']),
        'requires_ultrathink_review': len(categorized['promotional']) > 0
    }

    return {
        'summary': summary,
        'issues_by_category': categorized,
        'all_issues': all_issues
    }


def analyze_directory(directory: str) -> Dict[str, Any]:
    """Analyze all AsciiDoc files in directory (non-recursive)."""
    dir_path = Path(directory)
    adoc_files = list(dir_path.glob('*.adoc'))

    if not adoc_files:
        print(f"No .adoc files found in {directory}", file=sys.stderr)
        sys.exit(1)

    results = []

    for file_path in adoc_files:
        # Skip target directories
        if 'target' in file_path.parts:
            continue

        file_result = analyze_file(str(file_path))
        results.append(file_result)

    # Aggregate summary
    total_issues = sum(r['summary']['total_issues'] for r in results)
    total_promotional = sum(r['summary']['promotional_count'] for r in results)
    total_performance = sum(r['summary']['performance_claim_count'] for r in results)
    total_standards = sum(r['summary']['standards_claim_count'] for r in results)
    total_missing_sources = sum(r['summary']['missing_sources_count'] for r in results)

    return {
        'directory': directory,
        'files_analyzed': len(results),
        'aggregate_summary': {
            'total_issues': total_issues,
            'promotional_count': total_promotional,
            'performance_claim_count': total_performance,
            'standards_claim_count': total_standards,
            'missing_sources_count': total_missing_sources,
            'requires_ultrathink_review': total_promotional > 0
        },
        'file_results': results
    }


def main():
    parser = argparse.ArgumentParser(
        description='Analyze AsciiDoc content for tone issues and missing sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single file
  %(prog)s --file standards/security.adoc

  # Analyze directory
  %(prog)s --directory standards/

  # Output to file
  %(prog)s --file guide.adoc --output target/analysis.json

Categories:
  - promotional: Marketing/buzzword language requiring ULTRATHINK review
  - performance_claim: Performance assertions requiring benchmark data
  - standards_claim: Standards/compatibility claims requiring citations
  - missing_sources: Claims without nearby source attribution

Output:
  JSON with flagged sections for Claude to apply ULTRATHINK analysis
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--file',
        type=str,
        help='Analyze single AsciiDoc file'
    )

    group.add_argument(
        '--directory',
        type=str,
        help='Analyze all .adoc files in directory (non-recursive)'
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

    # Analyze
    if args.file:
        result = analyze_file(args.file)
    else:
        result = analyze_directory(args.directory)

    # Output
    indent = 2 if args.pretty else None
    output_json = json.dumps(result, indent=indent)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
        except IOError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)

    sys.exit(0)


if __name__ == '__main__':
    main()
