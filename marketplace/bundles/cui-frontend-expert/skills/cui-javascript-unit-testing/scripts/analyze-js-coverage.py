#!/usr/bin/env python3
"""
Analyze JavaScript test coverage reports (Jest/Istanbul JSON or LCOV format).

Returns structured JSON with coverage metrics, low-coverage files, and uncovered lines.
Stdlib-only - no external dependencies required.

Usage:
    python3 analyze-js-coverage.py --report coverage/coverage-summary.json
    python3 analyze-js-coverage.py --report coverage/lcov.info --format lcov
    python3 analyze-js-coverage.py --report coverage/coverage-summary.json --threshold 80

Output:
    JSON object with status, overall_coverage, by_file, low_coverage_files, and summary
"""

import argparse
import json
import os
import re
import sys
from typing import Any


def parse_json_coverage(report_path: str) -> dict[str, Any]:
    """Parse Jest/Istanbul JSON coverage-summary.json format."""
    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    overall = {}
    by_file = []

    # Extract total coverage if present
    if 'total' in data:
        total = data['total']
        overall = {
            'line_coverage': total.get('lines', {}).get('pct', 0),
            'statement_coverage': total.get('statements', {}).get('pct', 0),
            'function_coverage': total.get('functions', {}).get('pct', 0),
            'branch_coverage': total.get('branches', {}).get('pct', 0)
        }

    # Extract per-file coverage
    for file_path, coverage in data.items():
        if file_path == 'total':
            continue

        # Calculate uncovered lines (not available in summary format)
        lines_data = coverage.get('lines', {})
        uncovered_count = lines_data.get('total', 0) - lines_data.get('covered', 0)

        by_file.append({
            'file': file_path,
            'line_coverage': lines_data.get('pct', 0),
            'statement_coverage': coverage.get('statements', {}).get('pct', 0),
            'function_coverage': coverage.get('functions', {}).get('pct', 0),
            'branch_coverage': coverage.get('branches', {}).get('pct', 0),
            'uncovered_lines_count': uncovered_count,
            'uncovered_lines': []  # Detailed info not in summary format
        })

    return {'overall': overall, 'by_file': by_file}


def parse_lcov_coverage(report_path: str) -> dict[str, Any]:
    """Parse LCOV format coverage report."""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    files_data = []
    current_file = None
    current_data = {}

    for line in content.split('\n'):
        line = line.strip()

        if line.startswith('SF:'):
            # Source file
            current_file = line[3:]
            current_data = {
                'file': current_file,
                'lines_found': 0,
                'lines_hit': 0,
                'functions_found': 0,
                'functions_hit': 0,
                'branches_found': 0,
                'branches_hit': 0,
                'uncovered_lines': []
            }
        elif line.startswith('LF:'):
            current_data['lines_found'] = int(line[3:])
        elif line.startswith('LH:'):
            current_data['lines_hit'] = int(line[3:])
        elif line.startswith('FNF:'):
            current_data['functions_found'] = int(line[4:])
        elif line.startswith('FNH:'):
            current_data['functions_hit'] = int(line[4:])
        elif line.startswith('BRF:'):
            current_data['branches_found'] = int(line[4:])
        elif line.startswith('BRH:'):
            current_data['branches_hit'] = int(line[4:])
        elif line.startswith('DA:'):
            # Line data: DA:line_number,hit_count
            parts = line[3:].split(',')
            if len(parts) >= 2 and parts[1] == '0':
                current_data['uncovered_lines'].append(int(parts[0]))
        elif line == 'end_of_record' and current_file:
            files_data.append(current_data)
            current_file = None

    # Calculate overall coverage
    total_lines_found = sum(f['lines_found'] for f in files_data)
    total_lines_hit = sum(f['lines_hit'] for f in files_data)
    total_funcs_found = sum(f['functions_found'] for f in files_data)
    total_funcs_hit = sum(f['functions_hit'] for f in files_data)
    total_branches_found = sum(f['branches_found'] for f in files_data)
    total_branches_hit = sum(f['branches_hit'] for f in files_data)

    overall = {
        'line_coverage': (total_lines_hit / total_lines_found * 100) if total_lines_found > 0 else 0,
        'function_coverage': (total_funcs_hit / total_funcs_found * 100) if total_funcs_found > 0 else 0,
        'branch_coverage': (total_branches_hit / total_branches_found * 100) if total_branches_found > 0 else 0,
        'statement_coverage': (total_lines_hit / total_lines_found * 100) if total_lines_found > 0 else 0
    }

    by_file = []
    for f in files_data:
        line_cov = (f['lines_hit'] / f['lines_found'] * 100) if f['lines_found'] > 0 else 0
        func_cov = (f['functions_hit'] / f['functions_found'] * 100) if f['functions_found'] > 0 else 0
        branch_cov = (f['branches_hit'] / f['branches_found'] * 100) if f['branches_found'] > 0 else 0

        by_file.append({
            'file': f['file'],
            'line_coverage': round(line_cov, 2),
            'function_coverage': round(func_cov, 2),
            'branch_coverage': round(branch_cov, 2),
            'statement_coverage': round(line_cov, 2),
            'uncovered_lines_count': len(f['uncovered_lines']),
            'uncovered_lines': f['uncovered_lines']
        })

    return {'overall': overall, 'by_file': by_file}


def classify_coverage(coverage: float, threshold: float) -> str:
    """Classify coverage level by severity."""
    if coverage < 50:
        return 'CRITICAL'
    elif coverage < threshold:
        return 'WARNING'
    return 'OK'


def analyze_coverage(report_path: str, report_format: str, threshold: float) -> dict[str, Any]:
    """Main analysis function."""
    if not os.path.exists(report_path):
        return {
            'status': 'error',
            'error': 'REPORT_NOT_FOUND',
            'message': f'Coverage report not found: {report_path}',
            'searched_path': report_path
        }

    try:
        if report_format == 'json':
            data = parse_json_coverage(report_path)
        elif report_format == 'lcov':
            data = parse_lcov_coverage(report_path)
        else:
            return {
                'status': 'error',
                'error': 'UNSUPPORTED_FORMAT',
                'message': f'Unsupported report format: {report_format}'
            }
    except json.JSONDecodeError as e:
        return {
            'status': 'error',
            'error': 'PARSE_ERROR',
            'message': f'Failed to parse JSON: {e}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': 'PARSE_ERROR',
            'message': f'Failed to parse report: {e}'
        }

    # Identify low coverage files
    low_coverage_files = []
    files_with_good_coverage = 0
    files_with_critical = 0

    for file_data in data['by_file']:
        coverage = file_data.get('line_coverage', 0)
        severity = classify_coverage(coverage, threshold)

        if severity == 'OK':
            files_with_good_coverage += 1
        elif severity == 'CRITICAL':
            files_with_critical += 1
            low_coverage_files.append({
                'file': file_data['file'],
                'coverage': coverage,
                'severity': severity,
                'uncovered_lines': file_data.get('uncovered_lines', [])
            })
        else:  # WARNING
            low_coverage_files.append({
                'file': file_data['file'],
                'coverage': coverage,
                'severity': severity,
                'uncovered_lines': file_data.get('uncovered_lines', [])
            })

    # Sort low coverage files by coverage (lowest first)
    low_coverage_files.sort(key=lambda x: x['coverage'])

    # Round overall coverage values
    overall = {k: round(v, 2) for k, v in data['overall'].items()}

    return {
        'status': 'success',
        'data': {
            'report_format': report_format.upper(),
            'report_path': report_path,
            'overall_coverage': overall,
            'by_file': data['by_file'],
            'low_coverage_files': low_coverage_files
        },
        'metrics': {
            'total_files': len(data['by_file']),
            'files_with_good_coverage': files_with_good_coverage,
            'files_with_low_coverage': len(low_coverage_files),
            'files_with_critical_coverage': files_with_critical,
            'threshold': threshold
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Analyze JavaScript test coverage reports (Jest/Istanbul JSON or LCOV)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --report coverage/coverage-summary.json
  %(prog)s --report coverage/lcov.info --format lcov
  %(prog)s --report coverage/coverage-summary.json --threshold 80

Output format:
  JSON object with status, data (coverage metrics), and metrics (summary counts)
        '''
    )

    parser.add_argument(
        '--report',
        required=True,
        help='Path to coverage report file (coverage-summary.json or lcov.info)'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'lcov'],
        default='json',
        help='Report format: json (default) or lcov'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=80.0,
        help='Coverage threshold percentage (default: 80)'
    )

    args = parser.parse_args()

    # Auto-detect format from filename if not specified
    report_format = args.format
    if report_format == 'json' and args.report.endswith('.info'):
        report_format = 'lcov'

    result = analyze_coverage(args.report, report_format, args.threshold)
    print(json.dumps(result, indent=2))

    # Exit with error code if analysis failed
    if result.get('status') == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
