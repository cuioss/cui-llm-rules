#!/usr/bin/env python3
"""
Java core analysis tools.

Subcommands:
    analyze-logging   - Analyze LOGGER usage violations in Java files
    document-logrecord - Generate AsciiDoc documentation for LogRecord classes
    verify-params     - Verify implementation parameters for ambiguity

Usage:
    java-core.py analyze-logging --file <file.java>
    java-core.py document-logrecord --holder <LogMessages.java>
    java-core.py verify-params --description "..."
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


EXIT_SUCCESS = 0
EXIT_ERROR = 1


# =============================================================================
# ANALYZE-LOGGING SUBCOMMAND
# =============================================================================

LOGRECORD_REQUIRED_LEVELS = {"info", "warn", "error", "fatal"}
DIRECT_STRING_LEVELS = {"debug", "trace"}
LOGGER_PATTERN = re.compile(r'LOGGER\.(info|debug|trace|warn|error|fatal)\s*\(', re.IGNORECASE)
LOGRECORD_USAGE_PATTERN = re.compile(r'LOGGER\.\w+\s*\(\s*(?:(?:\w+\s*,\s*)?)?(INFO|WARN|ERROR|FATAL)\.\w+', re.IGNORECASE)
DIRECT_STRING_PATTERN = re.compile(r'LOGGER\.\w+\s*\(\s*(?:\w+\s*,\s*)?"[^"]*"')


def analyze_logging_line(line: str, line_number: int, file_path: str) -> List[Dict[str, Any]]:
    """Analyze a single line for LOGGER violations."""
    violations = []
    for match in LOGGER_PATTERN.finditer(line):
        level = match.group(1).lower()
        start = match.start()
        snippet_end = line.find(";", start)
        if snippet_end == -1:
            snippet_end = len(line)
        snippet = line[start:snippet_end + 1].strip()

        uses_logrecord = bool(LOGRECORD_USAGE_PATTERN.search(line))
        uses_direct_string = bool(DIRECT_STRING_PATTERN.search(line))

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


def analyze_logging_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single Java file for LOGGER violations."""
    violations = []
    total_statements = 0
    compliant = 0

    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        return {"file": str(file_path), "error": str(e), "violations": [], "total_statements": 0}

    for line_number, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue

        matches = LOGGER_PATTERN.findall(line)
        total_statements += len(matches)
        line_violations = analyze_logging_line(line, line_number, str(file_path))
        violations.extend(line_violations)
        compliant += len(matches) - len(line_violations)

    return {"file": str(file_path), "violations": violations, "total_statements": total_statements, "compliant": compliant}


def cmd_analyze_logging(args) -> int:
    """Handle analyze-logging subcommand."""
    if not args.file and not args.directory:
        print(json.dumps({"status": "error", "error": "Either --file or --directory must be specified"}, indent=2))
        return EXIT_ERROR

    files_to_analyze = []
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(json.dumps({"status": "error", "error": f"File not found: {args.file}"}, indent=2))
            return EXIT_ERROR
        files_to_analyze = [file_path]
    else:
        directory = Path(args.directory)
        if not directory.exists():
            print(json.dumps({"status": "error", "error": f"Directory not found: {args.directory}"}, indent=2))
            return EXIT_ERROR
        files_to_analyze = list(directory.rglob("*.java"))

    all_violations = []
    total_statements = total_compliant = missing_logrecord = incorrect_logrecord = 0

    for file_path in files_to_analyze:
        result = analyze_logging_file(file_path)
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
            "summary": {"missing_log_record": missing_logrecord, "incorrect_log_record": incorrect_logrecord, "compliant": total_compliant}
        },
        "metrics": {
            "files_analyzed": len(files_to_analyze),
            "total_violations": len(all_violations),
            "compliance_rate": round((total_compliant / total_statements * 100) if total_statements > 0 else 100, 2)
        }
    }

    print(json.dumps(output, indent=2))
    return EXIT_SUCCESS if len(all_violations) == 0 else EXIT_ERROR


# =============================================================================
# DOCUMENT-LOGRECORD SUBCOMMAND
# =============================================================================

@dataclass
class LogRecordInfo:
    """Information about a single LogRecord constant."""
    constant_name: str
    template: str
    prefix: str
    identifier: int
    level: str
    description: str


PREFIX_PATTERN = re.compile(r'public\s+static\s+final\s+String\s+PREFIX\s*=\s*"([^"]+)"')
NESTED_CLASS_PATTERN = re.compile(r'public\s+static\s+final\s+class\s+(INFO|WARN|ERROR|FATAL)\s*\{')
LOGRECORD_PATTERN = re.compile(r'public\s+static\s+final\s+LogRecord\s+(\w+)\s*=\s*LogRecordModel\.builder\(\)')
TEMPLATE_PATTERN = re.compile(r'\.template\s*\(\s*"([^"]+)"\s*\)')
IDENTIFIER_PATTERN = re.compile(r'\.identifier\s*\(\s*(\d+)\s*\)')
JAVADOC_PATTERN = re.compile(r'/\*\*\s*([^*]+)\s*\*/')


def extract_prefix(content: str) -> str:
    """Extract the PREFIX constant value."""
    match = PREFIX_PATTERN.search(content)
    return match.group(1) if match else "UNKNOWN"


def find_nested_classes(content: str) -> List[tuple]:
    """Find nested class boundaries (INFO, WARN, ERROR, FATAL)."""
    classes = []
    for match in NESTED_CLASS_PATTERN.finditer(content):
        level = match.group(1)
        start = match.start()
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


def generate_description_from_name(constant_name: str) -> str:
    """Generate a description from constant name."""
    words = constant_name.lower().replace("_", " ")
    return f"Logged when {words} occurs"


def extract_logrecords(content: str, level: str, start: int, end: int, prefix: str) -> List[LogRecordInfo]:
    """Extract LogRecord constants from a nested class section."""
    section = content[start:end]
    records = []

    for match in LOGRECORD_PATTERN.finditer(section):
        constant_name = match.group(1)
        builder_start = match.start()
        builder_end = section.find(".build()", builder_start)
        if builder_end == -1:
            continue

        builder_section = section[builder_start:builder_end + 8]
        template_match = TEMPLATE_PATTERN.search(builder_section)
        template = template_match.group(1) if template_match else ""
        id_match = IDENTIFIER_PATTERN.search(builder_section)
        identifier = int(id_match.group(1)) if id_match else 0

        javadoc_search_start = max(0, builder_start - 200)
        javadoc_section = section[javadoc_search_start:builder_start]
        javadoc_match = JAVADOC_PATTERN.search(javadoc_section)
        description = javadoc_match.group(1).strip() if javadoc_match else generate_description_from_name(constant_name)

        records.append(LogRecordInfo(
            constant_name=constant_name, template=template, prefix=prefix,
            identifier=identifier, level=level, description=description
        ))

    records.sort(key=lambda r: r.identifier)
    return records


def generate_level_table(records: List[LogRecordInfo], level: str) -> str:
    """Generate AsciiDoc table for a log level."""
    level_ranges = {"INFO": "001-099", "WARN": "100-199", "ERROR": "200-299", "FATAL": "300-399"}
    lines = [
        f"== {level} Level ({level_ranges.get(level, '???')})", "",
        '[cols="1,1,2,2", options="header"]', "|===", "|ID |Component |Message |Description", ""
    ]
    for record in records:
        formatted_id = f"{record.prefix}-{record.identifier:03d}"
        lines.append(f"|{formatted_id} |{record.prefix} |{record.template} |{record.description}")
    lines.extend(["|===", ""])
    return "\n".join(lines)


def generate_documentation(records_by_level: Dict[str, List[LogRecordInfo]], class_name: str) -> str:
    """Generate complete AsciiDoc documentation."""
    lines = [f"= {class_name} Log Messages", ":toc: left", ":toclevels: 2", ":sectnums:", "",
             f"This document describes all log messages for the {class_name} module.", ""]
    for level in ["INFO", "WARN", "ERROR", "FATAL"]:
        if level in records_by_level and records_by_level[level]:
            lines.append(generate_level_table(records_by_level[level], level))
    return "\n".join(lines)


def cmd_document_logrecord(args) -> int:
    """Handle document-logrecord subcommand."""
    holder_path = Path(args.holder)
    if not holder_path.exists():
        print(json.dumps({"status": "error", "error": f"Holder class not found: {args.holder}"}, indent=2))
        return EXIT_ERROR

    try:
        content = holder_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        print(json.dumps({"status": "error", "error": f"Failed to read file: {e}"}, indent=2))
        return EXIT_ERROR

    class_name = holder_path.stem
    prefix = extract_prefix(content)
    nested_classes = find_nested_classes(content)

    records_by_level: Dict[str, List[LogRecordInfo]] = {}
    total_records = 0
    for level, start, end in nested_classes:
        records = extract_logrecords(content, level, start, end, prefix)
        if records:
            records_by_level[level] = records
            total_records += len(records)

    if args.analyze_only:
        output = {
            "status": "success",
            "data": {
                "holder_class": str(holder_path), "prefix": prefix,
                "info_messages": len(records_by_level.get("INFO", [])),
                "warn_messages": len(records_by_level.get("WARN", [])),
                "error_messages": len(records_by_level.get("ERROR", [])),
                "fatal_messages": len(records_by_level.get("FATAL", [])),
                "total_messages": total_records
            },
            "metrics": {"levels_found": list(records_by_level.keys())}
        }
        print(json.dumps(output, indent=2))
        return EXIT_SUCCESS

    documentation = generate_documentation(records_by_level, class_name)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(documentation, encoding="utf-8")
        output = {
            "status": "success",
            "data": {
                "generated_files": [str(output_path)],
                "documentation": {
                    "holder_class": str(holder_path), "prefix": prefix,
                    "info_messages": len(records_by_level.get("INFO", [])),
                    "warn_messages": len(records_by_level.get("WARN", [])),
                    "error_messages": len(records_by_level.get("ERROR", [])),
                    "fatal_messages": len(records_by_level.get("FATAL", [])),
                    "total_messages": total_records
                },
                "tables_generated": len(records_by_level), "rows_updated": total_records
            },
            "errors": []
        }
        print(json.dumps(output, indent=2))
    else:
        print(documentation)

    return EXIT_SUCCESS


# =============================================================================
# VERIFY-PARAMS SUBCOMMAND
# =============================================================================

AMBIGUOUS_PATTERNS = [
    (r'\b(should|could|might|may)\s+(probably|possibly|optionally|perhaps)\b', 'uncertain_requirement'),
    (r'\bshould\s+probably\b', 'uncertain_requirement'),
    (r'\bcould\s+(?:maybe|possibly)\b', 'uncertain_requirement'),
    (r'\b(some|several|a few|many|various)\s+\w+', 'vague_quantity'),
    (r'\bif\s+needed\b', 'conditional_requirement'),
    (r'\bas\s+appropriate\b', 'conditional_requirement'),
    (r'\bwhen\s+necessary\b', 'conditional_requirement'),
    (r'\bas\s+required\b', 'conditional_requirement'),
    (r'\bmaybe\s+\w+', 'uncertain_action'),
    (r'\bperhaps\s+\w+', 'uncertain_action'),
]


def get_issue_description(category: str) -> str:
    """Get human-readable issue description for category."""
    descriptions = {
        'uncertain_requirement': 'Uncertain requirement - needs definitive specification',
        'vague_quantity': 'Vague quantity - needs specific count or list',
        'conditional_requirement': 'Conditional requirement - needs clear condition',
        'uncertain_action': 'Uncertain action - needs confirmation'
    }
    return descriptions.get(category, 'Ambiguous phrasing detected')


def detect_ambiguities(description: str) -> List[Dict[str, Any]]:
    """Detect ambiguous language patterns in description."""
    ambiguities = []
    for pattern, category in AMBIGUOUS_PATTERNS:
        matches = list(re.finditer(pattern, description, re.IGNORECASE))
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(description), match.end() + 50)
            context = description[start:end].strip()
            ambiguities.append({
                'pattern': match.group(0), 'category': category, 'context': context,
                'position': match.start(), 'issue': get_issue_description(category)
            })
    return ambiguities


def check_missing_information(description: str) -> List[Dict[str, Any]]:
    """Check for missing required information."""
    missing = []
    if re.search(r'\b(validate|validation|check|verify)\b', description, re.IGNORECASE):
        if not re.search(r'\b(throw|return|log)\b.*\b(exception|false|error)\b', description, re.IGNORECASE):
            missing.append({'category': 'error_handling', 'issue': 'Validation mentioned but failure behavior not specified',
                           'question': 'What should happen when validation fails?'})

    if re.search(r'\b(IOException|SQLException|Exception)\b', description):
        if not re.search(r'\b(wrap|catch|propagate|handle|throw)\b', description, re.IGNORECASE):
            missing.append({'category': 'error_handling', 'issue': 'Checked exception mentioned but handling strategy not specified',
                           'question': 'How should checked exceptions be handled?'})

    if re.search(r'\b(log|logging|logger)\b', description, re.IGNORECASE):
        if not re.search(r'\b(DEBUG|INFO|WARN|ERROR|TRACE)\b', description):
            missing.append({'category': 'logging', 'issue': 'Logging mentioned but level not specified',
                           'question': 'What logging level should be used?'})

    if re.search(r'\breturn\b', description, re.IGNORECASE):
        if not re.search(r'\b(void|Optional|null|empty)\b', description, re.IGNORECASE):
            missing.append({'category': 'return_value', 'issue': 'Return mentioned but null/empty behavior not specified',
                           'question': 'Should method return Optional<T>, allow null, or guarantee non-null?'})
    return missing


def detect_vague_scope(description: str) -> List[Dict[str, Any]]:
    """Detect vague scope or boundaries."""
    vague_scope = []
    vague_targets = [
        (r'\badd\s+(?:to|in)\s+\w+\s+(?:class|method|interface)\b', 'Vague modification target'),
        (r'\bupdate\s+\w+\b(?!\s+(?:class|method|field))', 'Vague update target'),
        (r'\bmodify\s+(?:the|existing)\b', 'Vague modification scope')
    ]
    for pattern, issue in vague_targets:
        matches = list(re.finditer(pattern, description, re.IGNORECASE))
        for match in matches:
            context = description[max(0, match.start()-30):min(len(description), match.end()+30)].strip()
            vague_scope.append({'pattern': match.group(0), 'issue': issue, 'context': context,
                               'question': 'Specify exact class/method/field names'})
    return vague_scope


def generate_suggestions(ambiguities: List, missing_info: List, vague_scope: List) -> List[str]:
    """Generate actionable suggestions based on detected issues."""
    suggestions = []
    if ambiguities:
        suggestions.append('Replace uncertain language with definitive requirements')
    if any(item['category'] == 'error_handling' for item in missing_info):
        suggestions.append('Specify exception handling strategy')
    if any(item['category'] == 'logging' for item in missing_info):
        suggestions.append('Specify logging level')
    if any(item['category'] == 'return_value' for item in missing_info):
        suggestions.append('Clarify null/empty return behavior')
    if vague_scope:
        suggestions.append('Specify exact targets')
    return suggestions


def calculate_clarity_score(description: str, ambiguities: List, missing_info: List, vague_scope: List) -> int:
    """Calculate clarity score (0-100)."""
    score = 100
    score -= len(ambiguities) * 10
    score -= len(missing_info) * 15
    score -= len(vague_scope) * 10
    if re.search(r'\bthrow\s+\w+Exception\b', description):
        score += 5
    if re.search(r'\b(DEBUG|INFO|WARN|ERROR)\s+level\b', description):
        score += 5
    if re.search(r'\bOptional<\w+>\b', description):
        score += 5
    return max(0, min(100, score))


def verify_parameters(description: str) -> Dict[str, Any]:
    """Main verification function."""
    ambiguities = detect_ambiguities(description)
    missing_info = check_missing_information(description)
    vague_scope = detect_vague_scope(description)
    suggestions = generate_suggestions(ambiguities, missing_info, vague_scope)
    clarity_score = calculate_clarity_score(description, ambiguities, missing_info, vague_scope)

    has_vague_scope = len(vague_scope) > 0 or len(description.split()) < 5

    return {
        'status': 'success',
        'data': {
            'clarity_score': clarity_score,
            'verification_passed': clarity_score >= 60 and not has_vague_scope,
            'total_issues': len(ambiguities) + len(missing_info) + len(vague_scope),
            'ambiguities': ambiguities, 'missing_information': missing_info,
            'vague_scope': has_vague_scope, 'suggestions': suggestions,
            'description_length': len(description), 'description_word_count': len(description.split())
        }
    }


def cmd_verify_params(args) -> int:
    """Handle verify-params subcommand."""
    if args.description:
        description = args.description
    else:
        description = sys.stdin.read().strip()

    if not description:
        print("Error: No description provided", file=sys.stderr)
        return EXIT_ERROR

    result = verify_parameters(description)
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

    return EXIT_SUCCESS if result['data']['verification_passed'] else EXIT_ERROR


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Java core analysis tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze-logging subcommand
    logging_parser = subparsers.add_parser("analyze-logging", help="Analyze LOGGER usage violations in Java files")
    logging_parser.add_argument("--file", "-f", help="Path to Java file to analyze")
    logging_parser.add_argument("--directory", "-d", help="Directory to search for Java files")
    logging_parser.set_defaults(func=cmd_analyze_logging)

    # document-logrecord subcommand
    doc_parser = subparsers.add_parser("document-logrecord", help="Generate AsciiDoc documentation for LogRecord classes")
    doc_parser.add_argument("--holder", required=True, help="Path to LogMessages holder Java class")
    doc_parser.add_argument("--output", "-o", help="Path to output AsciiDoc file")
    doc_parser.add_argument("--analyze-only", "-a", action="store_true", help="Only analyze, don't generate documentation")
    doc_parser.set_defaults(func=cmd_document_logrecord)

    # verify-params subcommand
    verify_parser = subparsers.add_parser("verify-params", help="Verify implementation parameters for ambiguity")
    verify_parser.add_argument("--description", type=str, help="Implementation description text to verify")
    verify_parser.add_argument("--output", type=str, help="Output JSON file")
    verify_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    verify_parser.set_defaults(func=cmd_verify_params)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
