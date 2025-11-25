#!/usr/bin/env python3
"""
Analyze JaCoCo coverage reports to identify testing gaps.

Parses JaCoCo XML reports to extract uncovered lines, branches, and methods,
prioritizes gaps by importance, and generates actionable recommendations.

Output: JSON with gap analysis for Claude to process.
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional


def parse_jacoco_report(report_path: str) -> Dict[str, Any]:
    """Parse JaCoCo XML report to extract coverage data."""
    try:
        tree = ET.parse(report_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {
            'error': f'Failed to parse XML: {e}',
            'summary': {},
            'gaps': []
        }
    except IOError as e:
        return {
            'error': f'Failed to read file: {e}',
            'summary': {},
            'gaps': []
        }

    # Aggregate coverage data
    total_line_covered = 0
    total_line_missed = 0
    total_branch_covered = 0
    total_branch_missed = 0
    total_method_covered = 0
    total_method_missed = 0

    gaps = []
    untested_public_methods = []

    # Process each package
    for package in root.findall('.//package'):
        package_name = package.get('name', '').replace('/', '.')

        # Process each class in package
        for clazz in package.findall('class'):
            class_name = clazz.get('name', '').replace('/', '.')
            source_file = clazz.get('sourcefilename', '')

            # Build source path
            if source_file:
                file_path = f"src/main/java/{package_name.replace('.', '/')}/{source_file}"
            else:
                file_path = f"src/main/java/{class_name.replace('.', '/')}.java"

            # Aggregate class-level counters
            class_line_covered = 0
            class_line_missed = 0
            class_branch_covered = 0
            class_branch_missed = 0
            uncovered_lines = []
            uncovered_branches = []
            uncovered_methods = []

            # Process methods
            for method in clazz.findall('method'):
                method_name = method.get('name', '')
                method_desc = method.get('desc', '')

                # Skip constructors and synthetic methods
                if method_name in ['<init>', '<clinit>']:
                    continue

                method_line_covered = 0
                method_line_missed = 0
                method_branch_covered = 0
                method_branch_missed = 0
                method_covered = False

                # Process method counters
                for counter in method.findall('counter'):
                    counter_type = counter.get('type')
                    missed = int(counter.get('missed', 0))
                    covered = int(counter.get('covered', 0))

                    if counter_type == 'LINE':
                        method_line_covered += covered
                        method_line_missed += missed
                    elif counter_type == 'BRANCH':
                        method_branch_covered += covered
                        method_branch_missed += missed
                    elif counter_type == 'METHOD':
                        if covered > 0:
                            method_covered = True

                # If method not covered at all
                if not method_covered:
                    uncovered_methods.append(method_name)
                    # Track untested public methods
                    untested_public_methods.append({
                        'class': class_name.split('.')[-1],
                        'method': method_name,
                        'file': file_path
                    })

                # Aggregate to class level
                class_line_covered += method_line_covered
                class_line_missed += method_line_missed
                class_branch_covered += method_branch_covered
                class_branch_missed += method_branch_missed

            # Extract line-level coverage from sourcefile
            for line in clazz.findall('counter[@type="LINE"]/../line'):
                line_num = int(line.get('nr', 0))
                mi = int(line.get('mi', 0))  # missed instructions
                ci = int(line.get('ci', 0))  # covered instructions
                mb = int(line.get('mb', 0))  # missed branches
                cb = int(line.get('cb', 0))  # covered branches

                # If line has no coverage
                if ci == 0 and mi > 0:
                    uncovered_lines.append(line_num)

                # If line has partial branch coverage
                if mb > 0 and cb > 0:
                    branch_coverage = (cb / (cb + mb)) * 100
                    uncovered_branches.append({
                        'line': line_num,
                        'missed': mb,
                        'covered': cb,
                        'coverage': round(branch_coverage, 1)
                    })

            # Aggregate to totals
            total_line_covered += class_line_covered
            total_line_missed += class_line_missed
            total_branch_covered += class_branch_covered
            total_branch_missed += class_branch_missed

            # Count methods from class-level counter
            for counter in clazz.findall('counter'):
                if counter.get('type') == 'METHOD':
                    total_method_covered += int(counter.get('covered', 0))
                    total_method_missed += int(counter.get('missed', 0))

            # Create gap entry if there are gaps
            if uncovered_lines or uncovered_branches or uncovered_methods:
                priority = determine_priority(
                    class_name,
                    uncovered_methods,
                    uncovered_lines,
                    uncovered_branches
                )

                gap = {
                    'file': file_path,
                    'class': class_name,
                    'package': package_name,
                    'uncovered_lines': sorted(uncovered_lines),
                    'uncovered_branches': uncovered_branches,
                    'uncovered_methods': uncovered_methods,
                    'priority': priority,
                    'reasons': determine_priority_reasons(
                        class_name,
                        uncovered_methods,
                        uncovered_lines
                    )
                }
                gaps.append(gap)

    # Calculate summary
    line_coverage = calculate_coverage(total_line_covered, total_line_missed)
    branch_coverage = calculate_coverage(total_branch_covered, total_branch_missed)
    method_coverage = calculate_coverage(total_method_covered, total_method_missed)

    summary = {
        'line_coverage': line_coverage,
        'branch_coverage': branch_coverage,
        'method_coverage': method_coverage,
        'gaps_count': len(gaps)
    }

    return {
        'summary': summary,
        'gaps': gaps,
        'untested_public_methods': untested_public_methods
    }


def calculate_coverage(covered: int, missed: int) -> float:
    """Calculate coverage percentage."""
    total = covered + missed
    if total == 0:
        return 100.0
    return round((covered / total) * 100, 1)


def determine_priority(class_name: str, methods: List[str],
                      lines: List[int], branches: List[Dict]) -> str:
    """Determine priority of gap (high, medium, low)."""
    # High priority: public methods uncovered
    if methods:
        return 'high'

    # High priority: many uncovered lines
    if len(lines) > 10:
        return 'high'

    # High priority: error handling patterns
    class_lower = class_name.lower()
    if any(keyword in class_lower for keyword in ['validator', 'security', 'auth']):
        return 'high'

    # Medium priority: some branches uncovered
    if branches:
        return 'medium'

    # Medium priority: some lines uncovered
    if lines:
        return 'medium'

    return 'low'


def determine_priority_reasons(class_name: str, methods: List[str],
                               lines: List[int]) -> List[str]:
    """Determine reasons for priority classification."""
    reasons = []

    if methods:
        reasons.append(f'{len(methods)} method(s) uncovered')

    if len(lines) > 10:
        reasons.append('many uncovered lines')

    class_lower = class_name.lower()
    if 'validator' in class_lower:
        reasons.append('validation logic')
    if 'security' in class_lower or 'auth' in class_lower:
        reasons.append('security-critical code')
    if 'service' in class_lower:
        reasons.append('service layer')

    return reasons


def categorize_gaps_by_priority(gaps: List[Dict], priority_filter: Optional[str] = None) -> Dict[str, List[Dict]]:
    """Categorize gaps by priority level."""
    categorized = {
        'high': [],
        'medium': [],
        'low': []
    }

    for gap in gaps:
        priority = gap.get('priority', 'low')
        if priority in categorized:
            gap_entry = {
                'class': gap['class'].split('.')[-1],
                'method': gap['uncovered_methods'][0] if gap['uncovered_methods'] else None,
                'file': gap['file'],
                'lines': gap['uncovered_lines'][:5] if gap['uncovered_lines'] else [],
                'reason': gap['reasons'][0] if gap['reasons'] else 'uncovered code'
            }
            categorized[priority].append(gap_entry)

    # Apply filter if specified
    if priority_filter and priority_filter != 'all':
        filtered = {'high': [], 'medium': [], 'low': []}
        if priority_filter == 'high':
            filtered['high'] = categorized['high']
        elif priority_filter == 'medium':
            filtered['high'] = categorized['high']
            filtered['medium'] = categorized['medium']
        elif priority_filter == 'low':
            filtered['low'] = categorized['low']
        return filtered

    return categorized


def generate_recommendations(gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate actionable test recommendations based on gaps."""
    recommendations = []

    for gap in gaps:
        class_name = gap['class'].split('.')[-1]  # Simple name

        # Recommendations for uncovered methods
        for method in gap['uncovered_methods']:
            recommendations.append({
                'priority': gap['priority'],
                'class': class_name,
                'method': method,
                'reason': 'uncovered_public_method',
                'file': gap['file'],
                'strategy': f"Add test exercising {method} method with happy path and error cases"
            })

        # Recommendations for uncovered branches
        if gap['uncovered_branches']:
            for branch in gap['uncovered_branches'][:3]:  # Top 3
                recommendations.append({
                    'priority': gap['priority'],
                    'class': class_name,
                    'method': None,
                    'reason': 'uncovered_branch',
                    'file': gap['file'],
                    'lines': [branch['line']],
                    'strategy': f"Add test covering untested branch at line {branch['line']}"
                })

        # Recommendations for uncovered line clusters
        if gap['uncovered_lines']:
            # Group consecutive lines
            clusters = group_consecutive(gap['uncovered_lines'])
            for cluster in clusters[:3]:  # Top 3 clusters
                if len(cluster) == 1:
                    line_desc = f"line {cluster[0]}"
                else:
                    line_desc = f"lines {cluster[0]}-{cluster[-1]}"

                recommendations.append({
                    'priority': gap['priority'],
                    'class': class_name,
                    'method': None,
                    'reason': 'uncovered_lines',
                    'file': gap['file'],
                    'lines': cluster,
                    'strategy': f"Add test covering {line_desc}"
                })

    # Sort by priority (high first)
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda r: priority_order.get(r['priority'], 3))

    return recommendations


def group_consecutive(numbers: List[int]) -> List[List[int]]:
    """Group consecutive numbers into clusters."""
    if not numbers:
        return []

    sorted_nums = sorted(numbers)
    clusters = []
    current_cluster = [sorted_nums[0]]

    for i in range(1, len(sorted_nums)):
        if sorted_nums[i] == current_cluster[-1] + 1:
            current_cluster.append(sorted_nums[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [sorted_nums[i]]

    clusters.append(current_cluster)
    return clusters


def check_thresholds(summary: Dict[str, Any],
                     threshold_line: float,
                     threshold_branch: float) -> bool:
    """Check if coverage meets thresholds."""
    line_ok = summary.get('line_coverage', 0) >= threshold_line
    branch_ok = summary.get('branch_coverage', 0) >= threshold_branch
    return line_ok and branch_ok


def main():
    parser = argparse.ArgumentParser(
        description='Analyze JaCoCo coverage report to identify testing gaps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze coverage report
  %(prog)s --report target/site/jacoco/jacoco.xml

  # Filter by priority
  %(prog)s --report target/site/jacoco/jacoco.xml --priority high

  # With custom thresholds
  %(prog)s --report target/site/jacoco/jacoco.xml --threshold-line 85 --threshold-branch 75

Output:
  {
    "status": "success",
    "data": {
      "overall_coverage": {"line": 75.5, "branch": 68.2, "method": 82.3},
      "gaps_by_priority": {"high": [...], "medium": [...], "low": [...]},
      "untested_public_methods": [...],
      "recommendations": [...]
    }
  }

Priority Levels:
  high: Public methods uncovered, security/validation code, many gaps
  medium: Some branches/lines uncovered, service layer
  low: Minor gaps, edge cases
        """
    )

    parser.add_argument(
        '--report',
        type=str,
        required=True,
        help='Path to JaCoCo XML report (jacoco.xml)'
    )

    parser.add_argument(
        '--priority',
        type=str,
        choices=['high', 'medium', 'low', 'all'],
        default='all',
        help='Filter gaps by priority level (default: all)'
    )

    parser.add_argument(
        '--threshold-line',
        type=float,
        default=80.0,
        help='Line coverage threshold percentage (default: 80)'
    )

    parser.add_argument(
        '--threshold-branch',
        type=float,
        default=70.0,
        help='Branch coverage threshold percentage (default: 70)'
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

    # Parse report
    parsed = parse_jacoco_report(args.report)

    # Check for parse errors
    if 'error' in parsed:
        result = {
            'status': 'error',
            'data': {'message': parsed['error']}
        }
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)

    # Check thresholds
    meets_thresholds = check_thresholds(
        parsed['summary'],
        args.threshold_line,
        args.threshold_branch
    )

    # Generate recommendations
    recommendations = generate_recommendations(parsed['gaps'])

    # Categorize gaps by priority
    gaps_by_priority = categorize_gaps_by_priority(parsed['gaps'], args.priority)

    # Build result in expected format
    result = {
        'status': 'success',
        'data': {
            'overall_coverage': {
                'line': parsed['summary']['line_coverage'],
                'branch': parsed['summary']['branch_coverage'],
                'method': parsed['summary']['method_coverage']
            },
            'gaps_by_priority': gaps_by_priority,
            'untested_public_methods': parsed.get('untested_public_methods', []),
            'recommendations': recommendations,
            'meets_thresholds': meets_thresholds,
            'gaps_count': parsed['summary']['gaps_count']
        }
    }

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

    # Exit with status based on thresholds
    # 0: Meets thresholds
    # 1: Does not meet thresholds
    sys.exit(0 if meets_thresholds else 1)


if __name__ == '__main__':
    main()
