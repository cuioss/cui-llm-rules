#!/usr/bin/env python3
"""
Analyze LOGGER usage violations in Java files based on CUI logging standards.

CUI Logging Rules:
- INFO/WARN/ERROR/FATAL MUST use LogRecord
- DEBUG/TRACE must NOT use LogRecord (direct string only)

Usage:
    analyze-logging-violations.py --file <file.java>
    analyze-logging-violations.py --directory <src/main/java>
    analyze-logging-violations.py --help

Output:
    JSON object with violations list and summary statistics.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze LOGGER usage violations in Java files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    analyze-logging-violations.py --file src/main/java/MyClass.java
    analyze-logging-violations.py --directory src/main/java
        """
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to Java file to analyze"
    )
    parser.add_argument(
        "--directory", "-d",
        help="Directory to search for Java files"
    )
    return parser.parse_args()


# Levels that MUST use LogRecord
LOGRECORD_REQUIRED_LEVELS = {"info", "warn", "error", "fatal"}

# Levels that must NOT use LogRecord
DIRECT_STRING_LEVELS = {"debug", "trace"}

# Pattern to match LOGGER statements
LOGGER_PATTERN = re.compile(
    r'LOGGER\.(info|debug|trace|warn|error|fatal)\s*\(',
    re.IGNORECASE
)

# Pattern to detect LogRecord usage (references INFO, WARN, ERROR, FATAL nested classes)
LOGRECORD_USAGE_PATTERN = re.compile(
    r'LOGGER\.\w+\s*\(\s*(?:(?:\w+\s*,\s*)?)?(INFO|WARN|ERROR|FATAL)\.\w+',
    re.IGNORECASE
)

# Pattern to detect direct string usage
DIRECT_STRING_PATTERN = re.compile(
    r'LOGGER\.\w+\s*\(\s*(?:\w+\s*,\s*)?"[^"]*"'
)


def analyze_line(line: str, line_number: int, file_path: str) -> list[dict[str, Any]]:
    """Analyze a single line for LOGGER violations."""
    violations = []

    # Find all LOGGER calls in the line
    for match in LOGGER_PATTERN.finditer(line):
        level = match.group(1).lower()

        # Extract the code snippet for this LOGGER call
        start = match.start()
        # Find the end of the statement (closing paren with semicolon)
        snippet_end = line.find(";", start)
        if snippet_end == -1:
            snippet_end = len(line)
        snippet = line[start:snippet_end + 1].strip()

        # Check if LogRecord is used
        uses_logrecord = bool(LOGRECORD_USAGE_PATTERN.search(line))
        uses_direct_string = bool(DIRECT_STRING_PATTERN.search(line))

        # Determine violation type
        if level in LOGRECORD_REQUIRED_LEVELS:
            if not uses_logrecord and uses_direct_string:
                violations.append({
                    "file": file_path,
                    "line": line_number,
                    "level": level.upper(),
                    "violation_type": "MISSING_LOG_RECORD",
                    "current_usage": "direct_string",
                    "expected_usage": "log_record",
                    "code_snippet": snippet
                })
        elif level in DIRECT_STRING_LEVELS:
            if uses_logrecord:
                violations.append({
                    "file": file_path,
                    "line": line_number,
                    "level": level.upper(),
                    "violation_type": "INCORRECT_LOG_RECORD_USAGE",
                    "current_usage": "log_record",
                    "expected_usage": "direct_string",
                    "code_snippet": snippet
                })

    return violations


def analyze_file(file_path: Path) -> dict[str, Any]:
    """Analyze a single Java file for LOGGER violations."""
    violations = []
    total_statements = 0
    compliant = 0

    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "violations": [],
            "total_statements": 0
        }

    for line_number, line in enumerate(content.split("\n"), 1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue

        # Count LOGGER statements
        matches = LOGGER_PATTERN.findall(line)
        total_statements += len(matches)

        # Analyze for violations
        line_violations = analyze_line(line, line_number, str(file_path))
        violations.extend(line_violations)

        # Count compliant statements
        compliant += len(matches) - len(line_violations)

    return {
        "file": str(file_path),
        "violations": violations,
        "total_statements": total_statements,
        "compliant": compliant
    }


def find_java_files(directory: Path) -> list[Path]:
    """Find all Java files in directory recursively."""
    return list(directory.rglob("*.java"))


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if not args.file and not args.directory:
        print(json.dumps({
            "status": "error",
            "error": "Either --file or --directory must be specified"
        }, indent=2))
        return 1

    files_to_analyze = []

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(json.dumps({
                "status": "error",
                "error": f"File not found: {args.file}"
            }, indent=2))
            return 1
        files_to_analyze = [file_path]
    else:
        directory = Path(args.directory)
        if not directory.exists():
            print(json.dumps({
                "status": "error",
                "error": f"Directory not found: {args.directory}"
            }, indent=2))
            return 1
        files_to_analyze = find_java_files(directory)

    # Aggregate results
    all_violations = []
    total_statements = 0
    total_compliant = 0
    missing_logrecord = 0
    incorrect_logrecord = 0

    for file_path in files_to_analyze:
        result = analyze_file(file_path)
        all_violations.extend(result["violations"])
        total_statements += result["total_statements"]
        total_compliant += result.get("compliant", 0)

        for v in result["violations"]:
            if v["violation_type"] == "MISSING_LOG_RECORD":
                missing_logrecord += 1
            elif v["violation_type"] == "INCORRECT_LOG_RECORD_USAGE":
                incorrect_logrecord += 1

    output = {
        "status": "success",
        "data": {
            "total_statements": total_statements,
            "violations": all_violations,
            "summary": {
                "missing_log_record": missing_logrecord,
                "incorrect_log_record": incorrect_logrecord,
                "compliant": total_compliant
            }
        },
        "metrics": {
            "files_analyzed": len(files_to_analyze),
            "total_violations": len(all_violations),
            "compliance_rate": round(
                (total_compliant / total_statements * 100) if total_statements > 0 else 100,
                2
            )
        }
    }

    print(json.dumps(output, indent=2))
    return 0 if len(all_violations) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
