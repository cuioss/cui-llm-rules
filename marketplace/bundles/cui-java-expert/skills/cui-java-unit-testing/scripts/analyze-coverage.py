#!/usr/bin/env python3
"""
Analyze JaCoCo XML coverage reports and extract coverage metrics.

This script parses JaCoCo XML reports and outputs structured JSON data
for coverage analysis in CI/CD pipelines and reporting.

Usage:
    analyze-coverage.py --file <jacoco.xml>
    analyze-coverage.py --directory <target/site/jacoco>
    analyze-coverage.py --help

Output:
    JSON object with coverage metrics, low-coverage classes, and uncovered lines.
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze JaCoCo XML coverage reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    analyze-coverage.py --file target/site/jacoco/jacoco.xml
    analyze-coverage.py --directory target/site/jacoco
    analyze-coverage.py --threshold 80
        """
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to JaCoCo XML report file"
    )
    parser.add_argument(
        "--directory", "-d",
        help="Directory containing JaCoCo reports (searches for jacoco.xml)"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=80.0,
        help="Coverage threshold for low-coverage detection (default: 80%%)"
    )
    return parser.parse_args()


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


def analyze_class(class_elem: ET.Element, package_name: str) -> dict[str, Any]:
    """Analyze a single class element."""
    class_name = class_elem.get("name", "").replace("/", ".")

    line_missed, line_covered = extract_counter(class_elem, "LINE")
    branch_missed, branch_covered = extract_counter(class_elem, "BRANCH")
    method_missed, method_covered = extract_counter(class_elem, "METHOD")

    # Find uncovered methods
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


def analyze_package(package_elem: ET.Element) -> dict[str, Any]:
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


def find_uncovered_lines(package_elem: ET.Element) -> list[dict[str, Any]]:
    """Find uncovered lines from sourcefile elements."""
    uncovered = []

    for sourcefile in package_elem.findall("sourcefile"):
        filename = sourcefile.get("name", "")
        for line in sourcefile.findall("line"):
            mi = int(line.get("mi", 0))  # missed instructions
            mb = int(line.get("mb", 0))  # missed branches
            if mi > 0 or mb > 0:
                uncovered.append({
                    "file": filename,
                    "line": int(line.get("nr", 0)),
                    "missed_instructions": mi,
                    "missed_branches": mb
                })

    return uncovered


def analyze_report(xml_path: Path, threshold: float) -> dict[str, Any]:
    """Analyze a JaCoCo XML report."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return {
            "status": "error",
            "error": f"Failed to parse XML: {e}",
            "file": str(xml_path)
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "error": f"File not found: {xml_path}",
            "file": str(xml_path)
        }

    # Extract overall coverage
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

    # Analyze packages
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

        # Collect low coverage classes
        for class_data in package_data["class_details"]:
            if class_data["line_coverage"] < threshold:
                low_coverage_classes.append({
                    "class": class_data["class"],
                    "line_coverage": class_data["line_coverage"],
                    "uncovered_methods": class_data["uncovered_methods"]
                })

        # Collect uncovered lines
        all_uncovered_lines.extend(find_uncovered_lines(package_elem))

    # Sort low coverage classes by coverage (ascending)
    low_coverage_classes.sort(key=lambda x: x["line_coverage"])

    return {
        "status": "success",
        "data": {
            "overall_coverage": overall_coverage,
            "by_package": packages,
            "low_coverage_classes": low_coverage_classes[:10],  # Top 10 worst
            "uncovered_lines": all_uncovered_lines[:50]  # First 50 uncovered lines
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


def find_jacoco_xml(directory: Path) -> Path | None:
    """Find jacoco.xml in directory."""
    jacoco_xml = directory / "jacoco.xml"
    if jacoco_xml.exists():
        return jacoco_xml

    # Try common locations
    for subdir in ["site/jacoco", "jacoco"]:
        jacoco_xml = directory / subdir / "jacoco.xml"
        if jacoco_xml.exists():
            return jacoco_xml

    return None


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if not args.file and not args.directory:
        print(json.dumps({
            "status": "error",
            "error": "Either --file or --directory must be specified"
        }, indent=2))
        return 1

    if args.file:
        xml_path = Path(args.file)
    else:
        directory = Path(args.directory)
        xml_path = find_jacoco_xml(directory)
        if not xml_path:
            print(json.dumps({
                "status": "error",
                "error": f"No jacoco.xml found in {directory}"
            }, indent=2))
            return 1

    result = analyze_report(xml_path, args.threshold)
    print(json.dumps(result, indent=2))

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
