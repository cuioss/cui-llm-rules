#!/usr/bin/env python3
"""
Parse Gradle build output and categorize issues.

Extracts errors, warnings, and test results from Gradle build logs.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Issue:
    """Represents a build issue."""

    type: str
    file: str = ""
    line: int = 0
    column: int = 0
    message: str = ""
    severity: str = "ERROR"
    suggestions: list[str] = field(default_factory=list)
    log_line: int = 0


@dataclass
class BuildMetrics:
    """Build execution metrics."""

    duration_ms: int = 0
    tasks_executed: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    tests_run: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0


# Issue type patterns for Gradle output
COMPILATION_PATTERNS = [
    r"error:\s+cannot find symbol",
    r"error:\s+incompatible types",
    r"error:\s+illegal start",
    r"error:\s+';' expected",
    r"error:\s+class .* is public",
    r"error:\s+package .* does not exist",
    r"error:\s+method .* cannot be applied",
    r"error:\s+unreported exception",
    r"error:\s+variable .* might not have been initialized",
    r"error:\s+cannot access",
    r"error:\s+duplicate class",
    r"error:\s+no suitable method found",
    r"Execution failed for task ':.*:compileJava'",
    r"Execution failed for task ':.*:compileKotlin'",
]

TEST_FAILURE_PATTERNS = [
    r">\s+\d+ tests? completed, \d+ failed",
    r"FAILED",
    r"AssertionFailedError",
    r"AssertionError",
    r"Execution failed for task ':.*:test'",
    r"Test run finished .* failures",
]

DEPENDENCY_PATTERNS = [
    r"Could not resolve",
    r"Could not find",
    r"Could not download",
    r"Failed to resolve",
    r"Cannot resolve external dependency",
    r"Dependency resolution failed",
    r"A module conflict was detected",
]

JAVADOC_PATTERNS = [
    r"warning:\s+no @param",
    r"warning:\s+no @return",
    r"warning:\s+missing @",
    r"javadoc",
    r"Execution failed for task ':.*:javadoc'",
]

DEPRECATION_PATTERNS = [
    r"\[deprecation\]",
    r"has been deprecated",
    r"is deprecated",
    r"deprecated API",
]

UNCHECKED_PATTERNS = [
    r"\[unchecked\]",
    r"unchecked conversion",
    r"unchecked call",
    r"uses unchecked",
]


def categorize_line(line: str) -> str | None:
    """Categorize a log line by issue type."""
    line_lower = line.lower()

    for pattern in COMPILATION_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return "compilation_error"

    for pattern in TEST_FAILURE_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return "test_failure"

    for pattern in DEPENDENCY_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return "dependency_error"

    for pattern in JAVADOC_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return "javadoc_warning"

    for pattern in DEPRECATION_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return "deprecation_warning"

    for pattern in UNCHECKED_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return "unchecked_warning"

    return None


def extract_file_location(line: str) -> tuple[str, int, int]:
    """Extract file path, line, and column from error message."""
    # Pattern: /path/to/File.java:45:20: error message
    # Or: /path/to/File.kt:45:20 error message
    match = re.search(r"([^\s:]+\.(java|kt|groovy)):(\d+):?(\d+)?", line)
    if match:
        file_path = match.group(1)
        line_num = int(match.group(3))
        col_num = int(match.group(4)) if match.group(4) else 0
        return file_path, line_num, col_num
    return "", 0, 0


def generate_suggestions(issue_type: str, message: str) -> list[str]:
    """Generate fix suggestions based on issue type."""
    suggestions = []

    if issue_type == "compilation_error":
        if "cannot find symbol" in message.lower():
            suggestions.append("Check if the class/method exists and is imported")
            suggestions.append("Verify spelling and case sensitivity")
        elif "incompatible types" in message.lower():
            suggestions.append("Check type compatibility")
            suggestions.append("Consider using type conversion or casting")
        elif "package" in message.lower() and "does not exist" in message.lower():
            suggestions.append("Add missing dependency to build.gradle")
            suggestions.append("Check if package name is correct")

    elif issue_type == "test_failure":
        suggestions.append("Review test assertions and expected values")
        suggestions.append("Check if test dependencies are up to date")
        suggestions.append("Run test in isolation to verify")

    elif issue_type == "dependency_error":
        suggestions.append("Check dependency coordinates (group:name:version)")
        suggestions.append("Verify repository configuration")
        suggestions.append("Check network connectivity")

    elif issue_type == "javadoc_warning":
        suggestions.append("Add missing Javadoc tags (@param, @return, etc.)")
        suggestions.append("Review Javadoc completeness")

    elif issue_type == "deprecation_warning":
        suggestions.append("Replace deprecated API with recommended alternative")
        suggestions.append("Check migration guides for deprecated features")

    elif issue_type == "unchecked_warning":
        suggestions.append("Add proper generic type parameters")
        suggestions.append("Use @SuppressWarnings(\"unchecked\") if intentional")

    return suggestions


def parse_build_status(lines: list[str]) -> str:
    """Determine overall build status from log lines."""
    for line in reversed(lines[-50:]):  # Check last 50 lines
        if "BUILD SUCCESSFUL" in line:
            return "SUCCESS"
        if "BUILD FAILED" in line:
            return "FAILURE"
    return "UNKNOWN"


def parse_metrics(lines: list[str]) -> BuildMetrics:
    """Extract build metrics from log."""
    metrics = BuildMetrics()

    for line in lines:
        # Duration pattern: BUILD SUCCESSFUL in 2m 30s
        duration_match = re.search(
            r"BUILD (?:SUCCESSFUL|FAILED) in (?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s)?",
            line,
        )
        if duration_match:
            hours = int(duration_match.group(1) or 0)
            minutes = int(duration_match.group(2) or 0)
            seconds = int(duration_match.group(3) or 0)
            metrics.duration_ms = (hours * 3600 + minutes * 60 + seconds) * 1000

        # Tasks pattern: 45 actionable tasks: 43 executed, 2 up-to-date
        tasks_match = re.search(
            r"(\d+) actionable tasks?: (\d+) executed", line
        )
        if tasks_match:
            metrics.tasks_executed = int(tasks_match.group(2))

        # Test results pattern: 150 tests completed, 2 failed, 3 skipped
        test_match = re.search(
            r"(\d+) tests? completed(?:, (\d+) failed)?(?:, (\d+) skipped)?",
            line,
        )
        if test_match:
            metrics.tests_run = int(test_match.group(1))
            metrics.tests_failed = int(test_match.group(2) or 0)
            metrics.tests_skipped = int(test_match.group(3) or 0)

    return metrics


def parse_log(log_path: str, mode: str = "default") -> dict:
    """Parse Gradle build log and extract issues."""
    path = Path(log_path)
    if not path.exists():
        result = {
            "status": "error",
            "error": "file_not_found",
            "message": f"Log file not found: {log_path}",
        }
        print(json.dumps(result, indent=2))
        return result

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    issues: list[Issue] = []
    seen_messages: set[str] = set()  # Deduplicate issues

    for line_num, line in enumerate(lines, 1):
        issue_type = categorize_line(line)
        if issue_type:
            file_path, file_line, file_col = extract_file_location(line)
            message = line.strip()

            # Deduplicate
            dedup_key = f"{issue_type}:{file_path}:{file_line}:{message[:100]}"
            if dedup_key in seen_messages:
                continue
            seen_messages.add(dedup_key)

            severity = "ERROR" if "error" in issue_type else "WARNING"
            suggestions = generate_suggestions(issue_type, message)

            issues.append(
                Issue(
                    type=issue_type,
                    file=file_path,
                    line=file_line,
                    column=file_col,
                    message=message,
                    severity=severity,
                    suggestions=suggestions,
                    log_line=line_num,
                )
            )

    build_status = parse_build_status(lines)
    metrics = parse_metrics(lines)

    # Build summary
    summary = {
        "compilation_errors": sum(
            1 for i in issues if i.type == "compilation_error"
        ),
        "test_failures": sum(1 for i in issues if i.type == "test_failure"),
        "javadoc_warnings": sum(
            1 for i in issues if i.type == "javadoc_warning"
        ),
        "deprecation_warnings": sum(
            1 for i in issues if i.type == "deprecation_warning"
        ),
        "unchecked_warnings": sum(
            1 for i in issues if i.type == "unchecked_warning"
        ),
        "dependency_errors": sum(
            1 for i in issues if i.type == "dependency_error"
        ),
        "other_warnings": sum(
            1
            for i in issues
            if i.type == "other" and i.severity == "WARNING"
        ),
        "other_errors": sum(
            1 for i in issues if i.type == "other" and i.severity == "ERROR"
        ),
        "total_issues": len(issues),
    }

    # Format output based on mode
    if mode == "errors":
        issues = [i for i in issues if i.severity == "ERROR"]

    result = {
        "status": "success",
        "data": {
            "build_status": build_status,
            "issues": [
                {
                    "type": i.type,
                    "file": i.file,
                    "line": i.line,
                    "column": i.column,
                    "message": i.message,
                    "severity": i.severity,
                    "suggestions": i.suggestions,
                    "log_line": i.log_line,
                }
                for i in issues
            ],
            "summary": summary,
        },
        "metrics": {
            "duration_ms": metrics.duration_ms,
            "tasks_executed": metrics.tasks_executed,
            "tasks_failed": metrics.tasks_failed,
            "tests_run": metrics.tests_run,
            "tests_failed": metrics.tests_failed,
        },
    }

    if mode == "default":
        # Human-readable output
        output_lines = [
            f"Build Status: {build_status}",
            f"Duration: {metrics.duration_ms}ms",
            f"Tasks: {metrics.tasks_executed} executed",
            f"Tests: {metrics.tests_run} run, {metrics.tests_failed} failed",
            "",
            f"Issues Summary:",
            f"  Compilation Errors: {summary['compilation_errors']}",
            f"  Test Failures: {summary['test_failures']}",
            f"  Javadoc Warnings: {summary['javadoc_warnings']}",
            f"  Dependency Errors: {summary['dependency_errors']}",
            f"  Total: {summary['total_issues']}",
        ]

        if issues:
            output_lines.append("")
            output_lines.append("Issues:")
            for issue in issues[:20]:  # Limit to first 20
                output_lines.append(
                    f"  [{issue.severity}] {issue.type}: {issue.message[:100]}"
                )
                if issue.file:
                    output_lines.append(f"    at {issue.file}:{issue.line}")

        print("\n".join(output_lines))
        return result

    # structured or errors mode
    print(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Parse Gradle build output and categorize issues"
    )
    parser.add_argument(
        "--log",
        required=True,
        help="Path to Gradle build log file",
    )
    parser.add_argument(
        "--mode",
        choices=["default", "errors", "structured"],
        default="default",
        help="Output mode (default: default)",
    )

    args = parser.parse_args()
    parse_log(args.log, args.mode)


if __name__ == "__main__":
    main()
