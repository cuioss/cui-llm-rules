#!/usr/bin/env python3
"""
Coverage analysis tools for JaCoCo XML reports.

Subcommands:
    analyze - Analyze JaCoCo XML reports and extract coverage metrics
    gaps    - Identify testing gaps with prioritized recommendations

Usage:
    coverage.py analyze --file <jacoco.xml> [--threshold 80]
    coverage.py gaps --report <jacoco.xml> [--priority high]
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional


EXIT_SUCCESS = 0
EXIT_ERROR = 1


# =============================================================================
# SHARED UTILITIES
# =============================================================================

def calculate_percentage(missed: int, covered: int) -> float:
    """Calculate coverage percentage."""
    total = missed + covered
    if total == 0:
        return 100.0
    return round((covered / total) * 100, 2)


def extract_counter(element: ET.Element, counter_type: str) -> tuple[int, int]:
    """Extract missed and covered counts for a counter type."""
    for counter in element.findall("counter"):
        if counter.get("type") == counter_type:
            return (
                int(counter.get("missed", 0)),
                int(counter.get("covered", 0))
            )
    return (0, 0)


def find_jacoco_xml(directory: Path) -> Optional[Path]:
    """Find jacoco.xml in directory."""
    jacoco_xml = directory / "jacoco.xml"
    if jacoco_xml.exists():
        return jacoco_xml
    for subdir in ["site/jacoco", "jacoco"]:
        jacoco_xml = directory / subdir / "jacoco.xml"
        if jacoco_xml.exists():
            return jacoco_xml
    return None


# =============================================================================
# ANALYZE SUBCOMMAND
# =============================================================================

def analyze_class(class_elem: ET.Element, package_name: str) -> Dict[str, Any]:
    """Analyze a single class element."""
    class_name = class_elem.get("name", "").replace("/", ".")

    line_missed, line_covered = extract_counter(class_elem, "LINE")
    branch_missed, branch_covered = extract_counter(class_elem, "BRANCH")
    method_missed, method_covered = extract_counter(class_elem, "METHOD")

    uncovered_methods = []
    for method in class_elem.findall("method"):
        m_missed, m_covered = extract_counter(method, "METHOD")
        if m_missed > 0 and m_covered == 0:
            method_name = method.get("name", "")
            if method_name not in ("<init>", "<clinit>"):
                uncovered_methods.append(method_name)

    return {
        "class": class_name,
        "package": package_name,
        "line_coverage": calculate_percentage(line_missed, line_covered),
        "branch_coverage": calculate_percentage(branch_missed, branch_covered),
        "method_coverage": calculate_percentage(method_missed, method_covered),
        "uncovered_methods": uncovered_methods,
        "lines": {"missed": line_missed, "covered": line_covered},
        "branches": {"missed": branch_missed, "covered": branch_covered}
    }


def analyze_package(package_elem: ET.Element) -> Dict[str, Any]:
    """Analyze a single package element."""
    package_name = package_elem.get("name", "").replace("/", ".")

    line_missed, line_covered = extract_counter(package_elem, "LINE")
    branch_missed, branch_covered = extract_counter(package_elem, "BRANCH")

    classes = []
    for class_elem in package_elem.findall("class"):
        classes.append(analyze_class(class_elem, package_name))

    return {
        "package": package_name,
        "line_coverage": calculate_percentage(line_missed, line_covered),
        "branch_coverage": calculate_percentage(branch_missed, branch_covered),
        "classes": len(classes),
        "class_details": classes
    }


def find_uncovered_lines(package_elem: ET.Element) -> List[Dict[str, Any]]:
    """Find uncovered lines from sourcefile elements."""
    uncovered = []
    for sourcefile in package_elem.findall("sourcefile"):
        filename = sourcefile.get("name", "")
        for line in sourcefile.findall("line"):
            mi = int(line.get("mi", 0))
            mb = int(line.get("mb", 0))
            if mi > 0 or mb > 0:
                uncovered.append({
                    "file": filename,
                    "line": int(line.get("nr", 0)),
                    "missed_instructions": mi,
                    "missed_branches": mb
                })
    return uncovered


def do_analyze_report(xml_path: Path, threshold: float) -> Dict[str, Any]:
    """Analyze a JaCoCo XML report."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {"status": "error", "error": f"Failed to parse XML: {e}", "file": str(xml_path)}
    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {xml_path}", "file": str(xml_path)}

    line_missed, line_covered = extract_counter(root, "LINE")
    branch_missed, branch_covered = extract_counter(root, "BRANCH")
    instruction_missed, instruction_covered = extract_counter(root, "INSTRUCTION")
    method_missed, method_covered = extract_counter(root, "METHOD")
    class_missed, class_covered = extract_counter(root, "CLASS")

    overall_coverage = {
        "line_coverage": calculate_percentage(line_missed, line_covered),
        "branch_coverage": calculate_percentage(branch_missed, branch_covered),
        "instruction_coverage": calculate_percentage(instruction_missed, instruction_covered),
        "method_coverage": calculate_percentage(method_missed, method_covered),
        "class_coverage": calculate_percentage(class_missed, class_covered)
    }

    packages = []
    low_coverage_classes = []
    all_uncovered_lines = []

    for package_elem in root.findall("package"):
        package_data = analyze_package(package_elem)
        packages.append({
            "package": package_data["package"],
            "line_coverage": package_data["line_coverage"],
            "branch_coverage": package_data["branch_coverage"],
            "classes": package_data["classes"]
        })

        for class_data in package_data["class_details"]:
            if class_data["line_coverage"] < threshold:
                low_coverage_classes.append({
                    "class": class_data["class"],
                    "line_coverage": class_data["line_coverage"],
                    "uncovered_methods": class_data["uncovered_methods"]
                })

        all_uncovered_lines.extend(find_uncovered_lines(package_elem))

    low_coverage_classes.sort(key=lambda x: x["line_coverage"])

    return {
        "status": "success",
        "data": {
            "overall_coverage": overall_coverage,
            "by_package": packages,
            "low_coverage_classes": low_coverage_classes[:10],
            "uncovered_lines": all_uncovered_lines[:50]
        },
        "metrics": {
            "file_analyzed": str(xml_path),
            "total_packages": len(packages),
            "total_classes": class_missed + class_covered,
            "total_methods": method_missed + method_covered,
            "total_lines": line_missed + line_covered,
            "threshold": threshold,
            "meets_threshold": overall_coverage["line_coverage"] >= threshold
        }
    }


def cmd_analyze(args) -> int:
    """Handle analyze subcommand."""
    if not args.file and not args.directory:
        print(json.dumps({"status": "error", "error": "Either --file or --directory must be specified"}, indent=2))
        return EXIT_ERROR

    if args.file:
        xml_path = Path(args.file)
    else:
        directory = Path(args.directory)
        xml_path = find_jacoco_xml(directory)
        if not xml_path:
            print(json.dumps({"status": "error", "error": f"No jacoco.xml found in {directory}"}, indent=2))
            return EXIT_ERROR

    result = do_analyze_report(xml_path, args.threshold)
    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS if result["status"] == "success" else EXIT_ERROR


# =============================================================================
# GAPS SUBCOMMAND
# =============================================================================

def determine_priority(class_name: str, methods: List[str], lines: List[int], branches: List[Dict]) -> str:
    """Determine priority of gap (high, medium, low)."""
    if methods:
        return 'high'
    if len(lines) > 10:
        return 'high'
    class_lower = class_name.lower()
    if any(keyword in class_lower for keyword in ['validator', 'security', 'auth']):
        return 'high'
    if branches:
        return 'medium'
    if lines:
        return 'medium'
    return 'low'


def determine_priority_reasons(class_name: str, methods: List[str], lines: List[int]) -> List[str]:
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


def parse_jacoco_for_gaps(report_path: str) -> Dict[str, Any]:
    """Parse JaCoCo XML report to extract coverage gaps."""
    try:
        tree = ET.parse(report_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {'error': f'Failed to parse XML: {e}', 'summary': {}, 'gaps': []}
    except IOError as e:
        return {'error': f'Failed to read file: {e}', 'summary': {}, 'gaps': []}

    total_line_covered = total_line_missed = 0
    total_branch_covered = total_branch_missed = 0
    total_method_covered = total_method_missed = 0
    gaps = []
    untested_public_methods = []

    for package in root.findall('.//package'):
        package_name = package.get('name', '').replace('/', '.')

        for clazz in package.findall('class'):
            class_name = clazz.get('name', '').replace('/', '.')
            source_file = clazz.get('sourcefilename', '')
            file_path = f"src/main/java/{package_name.replace('.', '/')}/{source_file}" if source_file else f"src/main/java/{class_name.replace('.', '/')}.java"

            class_line_covered = class_line_missed = 0
            class_branch_covered = class_branch_missed = 0
            uncovered_lines = []
            uncovered_branches = []
            uncovered_methods = []

            for method in clazz.findall('method'):
                method_name = method.get('name', '')
                if method_name in ['<init>', '<clinit>']:
                    continue

                method_covered = False
                for counter in method.findall('counter'):
                    counter_type = counter.get('type')
                    missed = int(counter.get('missed', 0))
                    covered = int(counter.get('covered', 0))
                    if counter_type == 'LINE':
                        class_line_covered += covered
                        class_line_missed += missed
                    elif counter_type == 'BRANCH':
                        class_branch_covered += covered
                        class_branch_missed += missed
                    elif counter_type == 'METHOD' and covered > 0:
                        method_covered = True

                if not method_covered:
                    uncovered_methods.append(method_name)
                    untested_public_methods.append({'class': class_name.split('.')[-1], 'method': method_name, 'file': file_path})

            total_line_covered += class_line_covered
            total_line_missed += class_line_missed
            total_branch_covered += class_branch_covered
            total_branch_missed += class_branch_missed

            for counter in clazz.findall('counter'):
                if counter.get('type') == 'METHOD':
                    total_method_covered += int(counter.get('covered', 0))
                    total_method_missed += int(counter.get('missed', 0))

            if uncovered_lines or uncovered_branches or uncovered_methods:
                priority = determine_priority(class_name, uncovered_methods, uncovered_lines, uncovered_branches)
                gaps.append({
                    'file': file_path,
                    'class': class_name,
                    'package': package_name,
                    'uncovered_lines': sorted(uncovered_lines),
                    'uncovered_branches': uncovered_branches,
                    'uncovered_methods': uncovered_methods,
                    'priority': priority,
                    'reasons': determine_priority_reasons(class_name, uncovered_methods, uncovered_lines)
                })

    summary = {
        'line_coverage': calculate_percentage(total_line_covered, total_line_missed),
        'branch_coverage': calculate_percentage(total_branch_covered, total_branch_missed),
        'method_coverage': calculate_percentage(total_method_covered, total_method_missed),
        'gaps_count': len(gaps)
    }

    return {'summary': summary, 'gaps': gaps, 'untested_public_methods': untested_public_methods}


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


def generate_recommendations(gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate actionable test recommendations based on gaps."""
    recommendations = []
    for gap in gaps:
        class_name = gap['class'].split('.')[-1]
        for method in gap['uncovered_methods']:
            recommendations.append({
                'priority': gap['priority'],
                'class': class_name,
                'method': method,
                'reason': 'uncovered_public_method',
                'file': gap['file'],
                'strategy': f"Add test exercising {method} method with happy path and error cases"
            })
        if gap['uncovered_branches']:
            for branch in gap['uncovered_branches'][:3]:
                recommendations.append({
                    'priority': gap['priority'],
                    'class': class_name,
                    'method': None,
                    'reason': 'uncovered_branch',
                    'file': gap['file'],
                    'lines': [branch['line']],
                    'strategy': f"Add test covering untested branch at line {branch['line']}"
                })
        if gap['uncovered_lines']:
            clusters = group_consecutive(gap['uncovered_lines'])
            for cluster in clusters[:3]:
                line_desc = f"line {cluster[0]}" if len(cluster) == 1 else f"lines {cluster[0]}-{cluster[-1]}"
                recommendations.append({
                    'priority': gap['priority'],
                    'class': class_name,
                    'method': None,
                    'reason': 'uncovered_lines',
                    'file': gap['file'],
                    'lines': cluster,
                    'strategy': f"Add test covering {line_desc}"
                })
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda r: priority_order.get(r['priority'], 3))
    return recommendations


def categorize_gaps_by_priority(gaps: List[Dict], priority_filter: Optional[str] = None) -> Dict[str, List[Dict]]:
    """Categorize gaps by priority level."""
    categorized = {'high': [], 'medium': [], 'low': []}
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


def cmd_gaps(args) -> int:
    """Handle gaps subcommand."""
    parsed = parse_jacoco_for_gaps(args.report)

    if 'error' in parsed:
        result = {'status': 'error', 'data': {'message': parsed['error']}}
        print(json.dumps(result), file=sys.stderr)
        return EXIT_ERROR

    meets_thresholds = (
        parsed['summary'].get('line_coverage', 0) >= args.threshold_line and
        parsed['summary'].get('branch_coverage', 0) >= args.threshold_branch
    )

    recommendations = generate_recommendations(parsed['gaps'])
    gaps_by_priority = categorize_gaps_by_priority(parsed['gaps'], args.priority)

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

    indent = 2 if args.pretty else None
    output_json = json.dumps(result, indent=indent)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
        except IOError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return EXIT_ERROR
    else:
        print(output_json)

    return EXIT_SUCCESS if meets_thresholds else EXIT_ERROR


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Coverage analysis tools for JaCoCo XML reports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze JaCoCo XML reports and extract coverage metrics")
    analyze_parser.add_argument("--file", "-f", help="Path to JaCoCo XML report file")
    analyze_parser.add_argument("--directory", "-d", help="Directory containing JaCoCo reports")
    analyze_parser.add_argument("--threshold", "-t", type=float, default=80.0, help="Coverage threshold (default: 80%%)")
    analyze_parser.set_defaults(func=cmd_analyze)

    # gaps subcommand
    gaps_parser = subparsers.add_parser("gaps", help="Identify testing gaps with prioritized recommendations")
    gaps_parser.add_argument("--report", type=str, required=True, help="Path to JaCoCo XML report")
    gaps_parser.add_argument("--priority", type=str, choices=['high', 'medium', 'low', 'all'], default='all', help="Filter by priority")
    gaps_parser.add_argument("--threshold-line", type=float, default=80.0, help="Line coverage threshold (default: 80)")
    gaps_parser.add_argument("--threshold-branch", type=float, default=70.0, help="Branch coverage threshold (default: 70)")
    gaps_parser.add_argument("--output", type=str, help="Output JSON file")
    gaps_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    gaps_parser.set_defaults(func=cmd_gaps)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
