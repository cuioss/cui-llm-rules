#!/usr/bin/env python3
"""
AsciiDoc Content Quality Analyzer

Analyzes AsciiDoc files for content quality issues:
- Marketing/promotional language detection
- Unverified claims identification
- TODO/status marker detection
- Qualification pattern recognition
- Tone and style analysis

Usage:
  python3 review-content.py --file path/to/file.adoc
  python3 review-content.py --directory path/to/docs/
  python3 review-content.py --help

Output: JSON with structured analysis results
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


# Marketing/promotional language patterns
MARKETING_PATTERNS = [
    (r'\b(amazing|incredible|revolutionary|magical|awesome)\b', 'promotional_adjective'),
    (r'\b(powerful|robust|enterprise-grade|world-class|best-in-class)\b', 'qualification_buzzword'),
    (r'\b(blazing[-\s]?fast|lightning[-\s]?fast|ultra[-\s]?fast)\b', 'performance_buzzword'),
    (r'\b(seamlessly?|effortlessly?|ridiculously)\b', 'ease_buzzword'),
    (r'\b(battle[-\s]?tested|production[-\s]?proven|extensively tested)\b', 'qualification_pattern'),
    (r'\bour\s+(amazing|incredible|powerful|robust)\b', 'self_praise'),
    (r'\b(super\s+easy|incredibly\s+simple|dead\s+simple)\b', 'ease_exaggeration'),
    (r'\b(zero\s+configuration|no\s+config(uration)?\s+needed)\b', 'ease_claim'),
    (r'\bwatch\s+the\s+magic\b', 'marketing_phrase'),
    (r'\bwhy\s+choose\s+(us|this)\b', 'promotional_section', re.IGNORECASE),
]

# Unverified claim patterns
CLAIM_PATTERNS = [
    (r'\b(thousands|millions)\s+of\s+(deployments|users|installations)\b', 'adoption_claim'),
    (r'\b\d+x\s+(faster|better|more\s+efficient)\b', 'performance_claim'),
    (r'\bsub[-\s]?millisecond\b', 'performance_claim'),
    (r'\b(used\s+by|trusted\s+by)\s+(leading|major|top)\s+companies\b', 'adoption_claim'),
    (r'\bguaranteed\b', 'guarantee_claim'),
    (r'\b(100%|99\.9+%)\s+(uptime|reliability|coverage)\b', 'reliability_claim'),
    (r'\bmost\s+(robust|reliable|secure|popular)\b', 'comparative_claim'),
]

# Completeness issue patterns
COMPLETENESS_PATTERNS = [
    (r'^\s*(\*\s*)?TODO:?\s', 'todo_marker'),
    (r'^\s*(\*\s*)?FIXME:?\s', 'fixme_marker'),
    (r'^\s*(\*\s*)?WIP:?\s', 'wip_marker'),
    (r'✅\s*', 'status_marker'),
    (r'❌\s*', 'status_marker'),
    (r'⚠️\s*', 'status_marker'),
    (r'\bwork\s+in\s+progress\b', 'wip_text', re.IGNORECASE),
    (r'\bcoming\s+soon\b', 'placeholder_text', re.IGNORECASE),
    (r'\bto\s+be\s+(determined|decided|added)\b', 'placeholder_text', re.IGNORECASE),
]

# Tone patterns (negative)
TONE_PATTERNS = [
    (r'!\s*$', 'exclamation_mark'),  # Sentences ending with !
    (r'\b(you|your)\s+(will|can|should)\s+love\b', 'promotional_promise'),
    (r'\bget\s+started\s+in\s+(seconds|minutes)\b', 'time_promise'),
]


def analyze_line(line: str, line_number: int, file_path: str) -> List[Dict[str, Any]]:
    """Analyze a single line for content issues."""
    issues = []

    # Check marketing patterns
    for pattern_tuple in MARKETING_PATTERNS:
        pattern = pattern_tuple[0]
        issue_type = pattern_tuple[1]
        flags = pattern_tuple[2] if len(pattern_tuple) > 2 else 0

        matches = list(re.finditer(pattern, line, flags))
        for match in matches:
            issues.append({
                'file': file_path,
                'line': line_number,
                'column': match.start() + 1,
                'type': 'tone',
                'subtype': issue_type,
                'severity': 'critical' if issue_type in ['self_praise', 'promotional_section'] else 'high',
                'text': match.group(),
                'context': line.strip()[:100],
                'message': f"Marketing language detected: '{match.group()}'"
            })

    # Check claim patterns
    for pattern_tuple in CLAIM_PATTERNS:
        pattern = pattern_tuple[0]
        issue_type = pattern_tuple[1]
        flags = pattern_tuple[2] if len(pattern_tuple) > 2 else 0

        matches = list(re.finditer(pattern, line, flags))
        for match in matches:
            issues.append({
                'file': file_path,
                'line': line_number,
                'column': match.start() + 1,
                'type': 'correctness',
                'subtype': issue_type,
                'severity': 'critical' if issue_type in ['comparative_claim', 'guarantee_claim'] else 'high',
                'text': match.group(),
                'context': line.strip()[:100],
                'message': f"Unverified claim: '{match.group()}' - requires evidence or citation"
            })

    # Check completeness patterns
    for pattern_tuple in COMPLETENESS_PATTERNS:
        pattern = pattern_tuple[0]
        issue_type = pattern_tuple[1]
        flags = pattern_tuple[2] if len(pattern_tuple) > 2 else 0

        matches = list(re.finditer(pattern, line, flags))
        for match in matches:
            issues.append({
                'file': file_path,
                'line': line_number,
                'column': match.start() + 1,
                'type': 'completeness',
                'subtype': issue_type,
                'severity': 'high',
                'text': match.group(),
                'context': line.strip()[:100],
                'message': f"Completeness issue: {issue_type.replace('_', ' ')} found"
            })

    # Check tone patterns
    for pattern_tuple in TONE_PATTERNS:
        pattern = pattern_tuple[0]
        issue_type = pattern_tuple[1]
        flags = pattern_tuple[2] if len(pattern_tuple) > 2 else 0

        # Only flag exclamation marks in non-code content
        if issue_type == 'exclamation_mark' and not line.strip().startswith(('----', '[source', '//')):
            matches = list(re.finditer(pattern, line, flags))
            for match in matches:
                issues.append({
                    'file': file_path,
                    'line': line_number,
                    'column': match.start() + 1,
                    'type': 'tone',
                    'subtype': issue_type,
                    'severity': 'medium',
                    'text': '!',
                    'context': line.strip()[:100],
                    'message': "Exclamation mark in documentation suggests promotional tone"
                })
        elif issue_type != 'exclamation_mark':
            matches = list(re.finditer(pattern, line, flags))
            for match in matches:
                issues.append({
                    'file': file_path,
                    'line': line_number,
                    'column': match.start() + 1,
                    'type': 'tone',
                    'subtype': issue_type,
                    'severity': 'high',
                    'text': match.group(),
                    'context': line.strip()[:100],
                    'message': f"Promotional tone detected: '{match.group()}'"
                })

    return issues


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single file for content quality issues."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'file': str(file_path),
            'status': 'error',
            'error': str(e),
            'issues': []
        }

    lines = content.split('\n')
    all_issues = []

    in_code_block = False

    for line_number, line in enumerate(lines, 1):
        # Track code blocks to avoid false positives
        if line.strip().startswith('----'):
            in_code_block = not in_code_block
            continue

        # Skip code block content
        if in_code_block:
            continue

        # Skip source block markers
        if line.strip().startswith('[source'):
            continue

        issues = analyze_line(line, line_number, str(file_path))
        all_issues.extend(issues)

    # Calculate quality score
    issue_weights = {
        'critical': 10,
        'high': 5,
        'medium': 2,
        'low': 1
    }

    total_penalty = sum(issue_weights.get(i['severity'], 1) for i in all_issues)
    # Base score of 100, reduce by penalties, minimum 0
    quality_score = max(0, 100 - total_penalty)

    return {
        'file': str(file_path),
        'status': 'success',
        'quality_score': quality_score,
        'issues': all_issues,
        'issue_counts': {
            'total': len(all_issues),
            'tone': len([i for i in all_issues if i['type'] == 'tone']),
            'correctness': len([i for i in all_issues if i['type'] == 'correctness']),
            'completeness': len([i for i in all_issues if i['type'] == 'completeness'])
        },
        'severity_counts': {
            'critical': len([i for i in all_issues if i['severity'] == 'critical']),
            'high': len([i for i in all_issues if i['severity'] == 'high']),
            'medium': len([i for i in all_issues if i['severity'] == 'medium']),
            'low': len([i for i in all_issues if i['severity'] == 'low'])
        }
    }


def analyze_directory(dir_path: Path, recursive: bool = False) -> List[Dict[str, Any]]:
    """Analyze all AsciiDoc files in a directory."""
    pattern = '**/*.adoc' if recursive else '*.adoc'
    files = list(dir_path.glob(pattern))

    results = []
    for file_path in files:
        # Skip target directories
        if 'target' in file_path.parts:
            continue
        results.append(analyze_file(file_path))

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Analyze AsciiDoc files for content quality issues'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Single file to analyze'
    )
    parser.add_argument(
        '--directory', '-d',
        type=str,
        help='Directory to analyze'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Analyze subdirectories recursively'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    if not args.file and not args.directory:
        parser.print_help()
        sys.exit(1)

    results = []

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(json.dumps({
                'status': 'error',
                'error': f'File not found: {args.file}'
            }))
            sys.exit(1)
        results = [analyze_file(file_path)]

    if args.directory:
        dir_path = Path(args.directory)
        if not dir_path.exists():
            print(json.dumps({
                'status': 'error',
                'error': f'Directory not found: {args.directory}'
            }))
            sys.exit(1)
        results.extend(analyze_directory(dir_path, args.recursive))

    # Aggregate results
    all_issues = []
    total_files = len(results)
    files_with_issues = 0
    total_score = 0

    for result in results:
        if result.get('issues'):
            all_issues.extend(result['issues'])
            files_with_issues += 1
        total_score += result.get('quality_score', 0)

    avg_score = total_score / total_files if total_files > 0 else 0

    output = {
        'status': 'success',
        'data': {
            'files_analyzed': total_files,
            'files_with_issues': files_with_issues,
            'average_quality_score': round(avg_score, 1),
            'total_issues': len(all_issues),
            'issues': all_issues,
            'file_results': results
        },
        'metrics': {
            'severity_summary': {
                'critical': len([i for i in all_issues if i['severity'] == 'critical']),
                'high': len([i for i in all_issues if i['severity'] == 'high']),
                'medium': len([i for i in all_issues if i['severity'] == 'medium']),
                'low': len([i for i in all_issues if i['severity'] == 'low'])
            },
            'type_summary': {
                'tone': len([i for i in all_issues if i['type'] == 'tone']),
                'correctness': len([i for i in all_issues if i['type'] == 'correctness']),
                'completeness': len([i for i in all_issues if i['type'] == 'completeness'])
            }
        }
    }

    output_json = json.dumps(output, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Output written to: {args.output}")
    else:
        print(output_json)


if __name__ == '__main__':
    main()
