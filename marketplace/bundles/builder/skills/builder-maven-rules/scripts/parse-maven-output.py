#!/usr/bin/env python3
"""
Parse Maven build output and categorize issues.

Parses Maven build log files and extracts errors, warnings, and test failures
with structured categorization for command orchestration.

Usage:
    python3 parse-maven-output.py --log <path> [--mode <mode>]
    python3 parse-maven-output.py --help

Output Modes:
    default    - Summary with all errors and warnings (human-readable)
    errors     - Only errors (no warnings)
    structured - Full JSON output for machine processing
    no-openrewrite - Errors/warnings excluding OpenRewrite messages

Returns JSON with structure:
{
    "status": "success|error",
    "data": {
        "build_status": "SUCCESS|FAILURE",
        "issues": [...],
        "summary": {...}
    }
}
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Parse Maven build output and categorize issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Parse build log with default mode
    python3 parse-maven-output.py --log target/build-output.log

    # Get structured JSON output
    python3 parse-maven-output.py --log target/build-output.log --mode structured

    # Get errors only
    python3 parse-maven-output.py --log target/build-output.log --mode errors
        """,
    )
    parser.add_argument(
        "--log", type=str, required=True, help="Path to Maven build log file"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["default", "errors", "structured", "no-openrewrite"],
        default="default",
        help="Output mode (default: default)",
    )
    return parser.parse_args()


def detect_build_status(content: str) -> str:
    """Detect overall build status from log content."""
    if "BUILD SUCCESS" in content:
        return "SUCCESS"
    if "BUILD FAILURE" in content:
        return "FAILURE"
    # Check for [ERROR] lines as fallback
    if re.search(r"^\[ERROR\]", content, re.MULTILINE):
        return "FAILURE"
    return "SUCCESS"


def extract_duration(content: str) -> Optional[int]:
    """Extract total build time in milliseconds."""
    # Match "Total time: 21.635 s" or "Total time: 2:35 min"
    match = re.search(r"Total time:\s+([\d.]+)\s+s", content)
    if match:
        return int(float(match.group(1)) * 1000)

    match = re.search(r"Total time:\s+(\d+):(\d+)\s+min", content)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return (minutes * 60 + seconds) * 1000

    return None


def extract_test_summary(content: str) -> dict:
    """Extract test execution summary."""
    # Match final test summary: "Tests run: 13, Failures: 0, Errors: 0, Skipped: 0"
    summary_pattern = r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)"
    matches = list(re.finditer(summary_pattern, content))

    if matches:
        # Use last match (final summary)
        last_match = matches[-1]
        return {
            "tests_run": int(last_match.group(1)),
            "failures": int(last_match.group(2)),
            "errors": int(last_match.group(3)),
            "skipped": int(last_match.group(4)),
        }

    return {"tests_run": 0, "failures": 0, "errors": 0, "skipped": 0}


def categorize_issue(message: str) -> str:
    """Categorize an issue based on its message content."""
    lower_msg = message.lower()

    # Compilation errors
    if any(
        pattern in lower_msg
        for pattern in [
            "cannot find symbol",
            "incompatible types",
            "illegal start",
            "class, interface, or enum expected",
            "unreported exception",
            "method does not override",
            "not a statement",
            "package does not exist",
            "cannot be applied",
        ]
    ):
        return "compilation_error"

    # Test failures
    if any(
        pattern in lower_msg
        for pattern in [
            "tests run:",
            "failure!",
            "test failure",
            "assertionfailed",
            "expected:",
        ]
    ):
        return "test_failure"

    # Dependency errors
    if any(
        pattern in lower_msg
        for pattern in [
            "could not resolve dependencies",
            "could not find artifact",
            "missing, no dependency",
            "artifact not found",
            "non-resolvable",
        ]
    ):
        return "dependency_error"

    # Javadoc warnings
    if any(
        pattern in lower_msg
        for pattern in [
            "javadoc",
            "no @param",
            "no @return",
            "@param name",
            "missing @",
        ]
    ):
        return "javadoc_warning"

    # Deprecation warnings
    if "[deprecation]" in lower_msg or "has been deprecated" in lower_msg:
        return "deprecation_warning"

    # Unchecked warnings
    if "[unchecked]" in lower_msg or "unchecked conversion" in lower_msg:
        return "unchecked_warning"

    # OpenRewrite messages
    if any(
        pattern in lower_msg
        for pattern in ["org.openrewrite", "rewrite-maven-plugin", "rewrite:"]
    ):
        return "openrewrite_info"

    return "other"


def parse_file_location(line: str) -> dict:
    """Extract file, line, and column from a Maven error/warning line."""
    result = {"file": None, "line": None, "column": None}

    # Pattern: /path/to/File.java:[45,20] message
    match = re.search(r"([^\s\[\]]+\.java):\[(\d+),(\d+)\]", line)
    if match:
        result["file"] = match.group(1)
        result["line"] = int(match.group(2))
        result["column"] = int(match.group(3))
        return result

    # Pattern: /path/to/File.java:45: message
    match = re.search(r"([^\s\[\]]+\.java):(\d+):", line)
    if match:
        result["file"] = match.group(1)
        result["line"] = int(match.group(2))
        return result

    # Pattern for test failures: TestClass.methodName:34
    match = re.search(r"(\w+Test)\.(\w+):(\d+)", line)
    if match:
        result["file"] = f"{match.group(1)}.java"
        result["line"] = int(match.group(3))
        result["method"] = match.group(2)
        return result

    return result


def extract_issues(content: str, include_warnings: bool = True) -> list:
    """Extract all issues from Maven output."""
    issues = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        severity = None
        if "[ERROR]" in line:
            severity = "ERROR"
        elif include_warnings and "[WARNING]" in line:
            severity = "WARNING"

        if severity:
            # Clean up the message
            message = line.strip()
            message = re.sub(r"^\[INFO\]\s*", "", message)
            message = re.sub(r"^\[ERROR\]\s*", "", message)
            message = re.sub(r"^\[WARNING\]\s*", "", message)

            # Skip empty messages or continuation lines
            if not message or message.startswith("->") or message.startswith("at "):
                continue

            location = parse_file_location(line)
            category = categorize_issue(message)

            issue = {
                "type": category,
                "file": location.get("file"),
                "line": location.get("line"),
                "column": location.get("column"),
                "message": message[:500],  # Truncate very long messages
                "severity": severity,
                "log_line": line_num,
            }

            # Add method for test failures
            if "method" in location:
                issue["method"] = location["method"]

            issues.append(issue)

    return issues


def filter_openrewrite(issues: list) -> list:
    """Filter out OpenRewrite-related issues."""
    return [i for i in issues if i["type"] != "openrewrite_info"]


def generate_summary(issues: list) -> dict:
    """Generate issue summary by category."""
    summary = {
        "compilation_errors": 0,
        "test_failures": 0,
        "javadoc_warnings": 0,
        "deprecation_warnings": 0,
        "unchecked_warnings": 0,
        "dependency_errors": 0,
        "openrewrite_info": 0,
        "other_warnings": 0,
        "other_errors": 0,
        "total_issues": len(issues),
    }

    for issue in issues:
        issue_type = issue["type"]
        severity = issue["severity"]

        if issue_type == "compilation_error":
            summary["compilation_errors"] += 1
        elif issue_type == "test_failure":
            summary["test_failures"] += 1
        elif issue_type == "javadoc_warning":
            summary["javadoc_warnings"] += 1
        elif issue_type == "deprecation_warning":
            summary["deprecation_warnings"] += 1
        elif issue_type == "unchecked_warning":
            summary["unchecked_warnings"] += 1
        elif issue_type == "dependency_error":
            summary["dependency_errors"] += 1
        elif issue_type == "openrewrite_info":
            summary["openrewrite_info"] += 1
        elif severity == "ERROR":
            summary["other_errors"] += 1
        else:
            summary["other_warnings"] += 1

    return summary


def get_suggestions(issue_type: str, message: str) -> list:
    """Get fix suggestions based on issue type and message."""
    suggestions_map = {
        "compilation_error": {
            "cannot find symbol": [
                "Check if the class/method exists and is properly imported",
                "Verify the spelling of the symbol name",
                "Ensure the dependency containing this class is declared in pom.xml",
            ],
            "incompatible types": [
                "Add explicit type cast if conversion is safe",
                "Use appropriate conversion methods (Integer.parseInt(), String.valueOf())",
                "Check method return types and variable declarations",
            ],
            "illegal start": [
                "Check for missing semicolons or braces",
                "Verify proper syntax for the statement",
                "Look for misplaced keywords or operators",
            ],
            "class, interface, or enum expected": [
                "Check for extra closing braces",
                "Verify import statements are at the top of the file",
                "Ensure code is within a class definition",
            ],
        },
        "dependency_error": {
            "could not resolve": [
                "Run 'mvn dependency:resolve' to see detailed errors",
                "Check if the artifact exists in Maven Central",
                "Verify the version number is correct",
            ],
            "could not find artifact": [
                "Verify the groupId, artifactId, and version are correct",
                "Check if the artifact requires a specific repository",
                "Try running 'mvn -U clean install' to force update",
            ],
        },
        "test_failure": {
            "default": [
                "Check the surefire-reports directory for detailed failure information",
                "Run 'mvn test -Dtest=ClassName' to run specific test class",
                "Use 'mvn test -X' for debug output",
            ]
        },
        "javadoc_warning": {
            "no @param": [
                "Add @param tag for the specified parameter",
                "Verify parameter name matches the method signature",
            ],
            "no @return": [
                "Add @return tag describing the return value",
                "Check if method signature actually returns a value",
            ],
        },
    }

    if issue_type in suggestions_map:
        type_suggestions = suggestions_map[issue_type]
        for pattern, suggestions in type_suggestions.items():
            if pattern.lower() in message.lower():
                return suggestions
        # Return default if available
        if "default" in type_suggestions:
            return type_suggestions["default"]

    return []


def format_default_output(
    build_status: str, issues: list, summary: dict, duration: Optional[int]
) -> str:
    """Format output for default mode (human-readable)."""
    lines = [f"Status: {build_status}", ""]

    if duration:
        lines.append(f"Duration: {duration}ms")
        lines.append("")

    # Group issues by severity
    errors = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]

    if errors:
        lines.append("Errors:")
        for issue in errors:
            loc = ""
            if issue["file"]:
                loc = f"{issue['file']}"
                if issue["line"]:
                    loc += f":{issue['line']}"
            lines.append(f"  [{issue['type']}] {loc}: {issue['message'][:100]}")
        lines.append("")

    if warnings:
        lines.append("Warnings:")
        for issue in warnings:
            loc = ""
            if issue["file"]:
                loc = f"{issue['file']}"
                if issue["line"]:
                    loc += f":{issue['line']}"
            lines.append(f"  [{issue['type']}] {loc}: {issue['message'][:100]}")
        lines.append("")

    if not errors and not warnings:
        lines.append("No errors or warnings found")
        lines.append("")

    lines.append("Summary:")
    lines.append(f"  Compilation errors: {summary['compilation_errors']}")
    lines.append(f"  Test failures: {summary['test_failures']}")
    lines.append(f"  Javadoc warnings: {summary['javadoc_warnings']}")
    lines.append(f"  Dependency errors: {summary['dependency_errors']}")
    lines.append(f"  Total issues: {summary['total_issues']}")

    return "\n".join(lines)


def format_errors_output(build_status: str, issues: list) -> str:
    """Format output for errors mode (errors only)."""
    lines = [f"Status: {build_status}", ""]

    errors = [i for i in issues if i["severity"] == "ERROR"]

    if errors:
        lines.append("Errors:")
        for issue in errors:
            loc = ""
            if issue["file"]:
                loc = f"{issue['file']}"
                if issue["line"]:
                    loc += f":{issue['line']}"
            lines.append(f"  {issue['log_line']}: [{issue['type']}] {loc}")
            lines.append(f"    {issue['message'][:150]}")
        lines.append("")
    else:
        lines.append("No errors found")

    return "\n".join(lines)


def analyze_log(log_path: str, mode: str) -> dict:
    """Main analysis function."""
    path = Path(log_path)

    if not path.exists():
        return {
            "status": "error",
            "error": f"Log file not found: {log_path}",
        }

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to read log file: {str(e)}",
        }

    build_status = detect_build_status(content)
    duration = extract_duration(content)
    test_summary = extract_test_summary(content)

    # Extract issues based on mode
    include_warnings = mode not in ["errors"]
    issues = extract_issues(content, include_warnings)

    # Filter OpenRewrite for no-openrewrite mode
    if mode == "no-openrewrite":
        issues = filter_openrewrite(issues)

    summary = generate_summary(issues)

    # Add suggestions for structured mode
    if mode == "structured":
        for issue in issues:
            issue["suggestions"] = get_suggestions(issue["type"], issue["message"])

    result = {
        "status": "success" if build_status == "SUCCESS" else "error",
        "data": {
            "build_status": build_status,
            "issues": issues,
            "summary": summary,
        },
        "metrics": {
            "duration_ms": duration,
            "tests_run": test_summary["tests_run"],
            "tests_failed": test_summary["failures"] + test_summary["errors"],
        },
    }

    return result


def main():
    """Main entry point."""
    args = parse_args()

    result = analyze_log(args.log, args.mode)

    if args.mode in ["default", "errors", "no-openrewrite"]:
        if result["status"] == "error" and "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        if args.mode == "errors":
            print(
                format_errors_output(
                    result["data"]["build_status"], result["data"]["issues"]
                )
            )
        else:
            print(
                format_default_output(
                    result["data"]["build_status"],
                    result["data"]["issues"],
                    result["data"]["summary"],
                    result["metrics"]["duration_ms"],
                )
            )
    else:
        # structured mode - JSON output
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
