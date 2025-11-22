#!/usr/bin/env python3
"""
Generate AsciiDoc documentation for LogRecord classes following CUI standards.

Analyzes Java LogMessages holder classes and generates or updates AsciiDoc
documentation with standardized table format.

Usage:
    document-logrecord.py --holder <ClassName.java> --output <LogMessages.adoc>
    document-logrecord.py --help

Output:
    JSON object with generation status and documentation metadata.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate AsciiDoc documentation for LogRecord classes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    document-logrecord.py --holder src/main/java/MyLogMessages.java --output doc/LogMessages.adoc
    document-logrecord.py --holder MyLogMessages.java --analyze-only
        """
    )
    parser.add_argument(
        "--holder",
        required=True,
        help="Path to LogMessages holder Java class"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to output AsciiDoc file (if not specified, prints to stdout)"
    )
    parser.add_argument(
        "--analyze-only", "-a",
        action="store_true",
        help="Only analyze, don't generate documentation"
    )
    return parser.parse_args()


@dataclass
class LogRecordInfo:
    """Information about a single LogRecord constant."""
    constant_name: str
    template: str
    prefix: str
    identifier: int
    level: str
    description: str


# Pattern to extract PREFIX constant
PREFIX_PATTERN = re.compile(
    r'public\s+static\s+final\s+String\s+PREFIX\s*=\s*"([^"]+)"'
)

# Pattern to detect nested class (INFO, WARN, ERROR, FATAL)
NESTED_CLASS_PATTERN = re.compile(
    r'public\s+static\s+final\s+class\s+(INFO|WARN|ERROR|FATAL)\s*\{'
)

# Pattern to extract LogRecord constant
LOGRECORD_PATTERN = re.compile(
    r'public\s+static\s+final\s+LogRecord\s+(\w+)\s*=\s*LogRecordModel\.builder\(\)'
)

# Pattern to extract template
TEMPLATE_PATTERN = re.compile(r'\.template\s*\(\s*"([^"]+)"\s*\)')

# Pattern to extract identifier
IDENTIFIER_PATTERN = re.compile(r'\.identifier\s*\(\s*(\d+)\s*\)')

# Pattern to extract Javadoc description
JAVADOC_PATTERN = re.compile(r'/\*\*\s*([^*]+)\s*\*/')


def extract_prefix(content: str) -> str:
    """Extract the PREFIX constant value."""
    match = PREFIX_PATTERN.search(content)
    return match.group(1) if match else "UNKNOWN"


def find_nested_classes(content: str) -> list[tuple[str, int, int]]:
    """Find nested class boundaries (INFO, WARN, ERROR, FATAL)."""
    classes = []

    for match in NESTED_CLASS_PATTERN.finditer(content):
        level = match.group(1)
        start = match.start()

        # Find the closing brace by counting
        brace_count = 0
        end = start
        for i, char in enumerate(content[start:], start):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    end = i
                    break

        classes.append((level, start, end))

    return classes


def extract_logrecords(content: str, level: str, start: int, end: int, prefix: str) -> list[LogRecordInfo]:
    """Extract LogRecord constants from a nested class section."""
    section = content[start:end]
    records = []

    # Find all LogRecord constants in this section
    for match in LOGRECORD_PATTERN.finditer(section):
        constant_name = match.group(1)
        builder_start = match.start()

        # Find the end of the builder chain (.build())
        builder_end = section.find(".build()", builder_start)
        if builder_end == -1:
            continue

        builder_section = section[builder_start:builder_end + 8]

        # Extract template
        template_match = TEMPLATE_PATTERN.search(builder_section)
        template = template_match.group(1) if template_match else ""

        # Extract identifier
        id_match = IDENTIFIER_PATTERN.search(builder_section)
        identifier = int(id_match.group(1)) if id_match else 0

        # Try to find Javadoc description before the constant
        javadoc_search_start = max(0, builder_start - 200)
        javadoc_section = section[javadoc_search_start:builder_start]
        javadoc_match = JAVADOC_PATTERN.search(javadoc_section)

        if javadoc_match:
            description = javadoc_match.group(1).strip()
        else:
            # Generate description from constant name
            description = generate_description(constant_name)

        records.append(LogRecordInfo(
            constant_name=constant_name,
            template=template,
            prefix=prefix,
            identifier=identifier,
            level=level,
            description=description
        ))

    # Sort by identifier
    records.sort(key=lambda r: r.identifier)
    return records


def generate_description(constant_name: str) -> str:
    """Generate a description from constant name."""
    # Convert SNAKE_CASE to words
    words = constant_name.lower().replace("_", " ")
    return f"Logged when {words} occurs"


def format_identifier(prefix: str, identifier: int) -> str:
    """Format identifier with leading zeros."""
    return f"{prefix}-{identifier:03d}"


def generate_level_table(records: list[LogRecordInfo], level: str) -> str:
    """Generate AsciiDoc table for a log level."""
    level_ranges = {
        "INFO": "001-099",
        "WARN": "100-199",
        "ERROR": "200-299",
        "FATAL": "300-399"
    }

    lines = [
        f"== {level} Level ({level_ranges.get(level, '???')})",
        "",
        '[cols="1,1,2,2", options="header"]',
        "|===",
        "|ID |Component |Message |Description",
        ""
    ]

    for record in records:
        formatted_id = format_identifier(record.prefix, record.identifier)
        lines.append(
            f"|{formatted_id} |{record.prefix} |{record.template} |{record.description}"
        )

    lines.append("|===")
    lines.append("")

    return "\n".join(lines)


def generate_documentation(records_by_level: dict[str, list[LogRecordInfo]],
                          class_name: str) -> str:
    """Generate complete AsciiDoc documentation."""
    lines = [
        f"= {class_name} Log Messages",
        ":toc: left",
        ":toclevels: 2",
        ":sectnums:",
        "",
        f"This document describes all log messages for the {class_name} module.",
        ""
    ]

    # Generate tables in order: INFO, WARN, ERROR, FATAL
    for level in ["INFO", "WARN", "ERROR", "FATAL"]:
        if level in records_by_level and records_by_level[level]:
            lines.append(generate_level_table(records_by_level[level], level))

    return "\n".join(lines)


def analyze_holder(file_path: Path) -> dict[str, Any]:
    """Analyze a LogMessages holder class."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        return {
            "status": "error",
            "error": f"Failed to read file: {e}"
        }

    # Extract class name from file path
    class_name = file_path.stem

    # Extract PREFIX
    prefix = extract_prefix(content)

    # Find nested classes
    nested_classes = find_nested_classes(content)

    # Extract LogRecords from each level
    records_by_level: dict[str, list[LogRecordInfo]] = {}
    total_records = 0

    for level, start, end in nested_classes:
        records = extract_logrecords(content, level, start, end, prefix)
        if records:
            records_by_level[level] = records
            total_records += len(records)

    return {
        "status": "success",
        "class_name": class_name,
        "prefix": prefix,
        "records_by_level": records_by_level,
        "total_records": total_records,
        "levels_found": list(records_by_level.keys())
    }


def main() -> int:
    """Main entry point."""
    args = parse_args()

    holder_path = Path(args.holder)
    if not holder_path.exists():
        print(json.dumps({
            "status": "error",
            "error": f"Holder class not found: {args.holder}"
        }, indent=2))
        return 1

    # Analyze the holder class
    analysis = analyze_holder(holder_path)

    if analysis["status"] == "error":
        print(json.dumps(analysis, indent=2))
        return 1

    if args.analyze_only:
        # Return analysis results as JSON
        output = {
            "status": "success",
            "data": {
                "holder_class": str(holder_path),
                "prefix": analysis["prefix"],
                "info_messages": len(analysis["records_by_level"].get("INFO", [])),
                "warn_messages": len(analysis["records_by_level"].get("WARN", [])),
                "error_messages": len(analysis["records_by_level"].get("ERROR", [])),
                "fatal_messages": len(analysis["records_by_level"].get("FATAL", [])),
                "total_messages": analysis["total_records"]
            },
            "metrics": {
                "levels_found": analysis["levels_found"]
            }
        }
        print(json.dumps(output, indent=2))
        return 0

    # Generate documentation
    # Convert LogRecordInfo objects to the format expected by generate_documentation
    records_by_level_converted = {}
    for level, records in analysis["records_by_level"].items():
        records_by_level_converted[level] = records

    documentation = generate_documentation(
        records_by_level_converted,
        analysis["class_name"]
    )

    # Output documentation
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(documentation, encoding="utf-8")

        output = {
            "status": "success",
            "data": {
                "generated_files": [str(output_path)],
                "documentation": {
                    "holder_class": str(holder_path),
                    "prefix": analysis["prefix"],
                    "info_messages": len(analysis["records_by_level"].get("INFO", [])),
                    "warn_messages": len(analysis["records_by_level"].get("WARN", [])),
                    "error_messages": len(analysis["records_by_level"].get("ERROR", [])),
                    "fatal_messages": len(analysis["records_by_level"].get("FATAL", [])),
                    "total_messages": analysis["total_records"]
                },
                "tables_generated": len(analysis["levels_found"]),
                "rows_updated": analysis["total_records"]
            },
            "errors": []
        }
        print(json.dumps(output, indent=2))
    else:
        # Print documentation to stdout
        print(documentation)

    return 0


if __name__ == "__main__":
    sys.exit(main())
