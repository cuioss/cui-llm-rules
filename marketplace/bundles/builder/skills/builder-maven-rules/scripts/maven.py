#!/usr/bin/env python3
"""
Maven build operations - execute, parse, find modules, search markers, check warnings.

Usage:
    maven.py execute --goals <goals> [options]
    maven.py parse --log <path> [--mode <mode>]
    maven.py find-module --artifact-id <id> | --module-path <path>
    maven.py search-markers --source-dir <dir>
    maven.py check-warnings --warnings <json> [--patterns <json>]
    maven.py --help

Subcommands:
    execute         Execute Maven build with automatic log file handling
    parse           Parse Maven build output and categorize issues
    find-module     Find Maven module path from artifactId
    search-markers  Search for OpenRewrite TODO markers in source files
    check-warnings  Categorize build warnings against acceptable patterns
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


# ============================================================================
# EXECUTE SUBCOMMAND
# ============================================================================

def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"target/build-output-{timestamp}.log"


def pre_create_log_file(log_file: str) -> bool:
    """Pre-create log file and parent directory."""
    try:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return True
    except OSError:
        return False


def build_maven_command(goals: str, profile: str, module: str, mvnw: str, log_file: str) -> list:
    """Build Maven command list from arguments."""
    cmd = [mvnw, "-l", log_file]
    if profile:
        cmd.append(f"-P{profile}")
    cmd.extend(goals.split())
    if module:
        cmd.extend(["-pl", module])
    return cmd


def execute_maven(cmd: list, timeout_ms: int) -> dict:
    """Execute Maven command and return result."""
    timeout_seconds = timeout_ms / 1000.0
    start_time = time.time()

    try:
        result = subprocess.run(cmd, timeout=timeout_seconds, capture_output=False, check=False)
        duration_ms = int((time.time() - start_time) * 1000)
        return {"exit_code": result.returncode, "duration_ms": duration_ms, "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "duration_ms": int((time.time() - start_time) * 1000), "timed_out": True}
    except FileNotFoundError:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": f"Maven wrapper not found: {cmd[0]}"}
    except OSError as e:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": str(e)}


def cmd_execute(args):
    """Handle execute subcommand."""
    log_file = generate_log_filename()
    if not pre_create_log_file(log_file):
        print(json.dumps({"status": "error", "error": "log_file_creation_failed", "message": f"Failed to create log file: {log_file}"}, indent=2))
        return 1

    cmd = build_maven_command(args.goals, args.profile, args.module, args.mvnw, log_file)
    command_str = " ".join(cmd)
    print(f"[EXEC] {command_str}", file=sys.stderr)

    exec_result = execute_maven(cmd, args.timeout)

    if "error" in exec_result:
        print(json.dumps({"status": "error", "error": "execution_failed", "message": exec_result["error"], "data": {"log_file": log_file, "command_executed": command_str}}, indent=2))
        return 1

    if exec_result["timed_out"]:
        print(json.dumps({"status": "error", "error": "timeout", "message": f"Build timed out after {args.timeout}ms", "data": {"log_file": log_file, "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}, indent=2))
        return 1

    result = {"status": "success" if exec_result["exit_code"] == 0 else "error", "data": {"log_file": log_file, "exit_code": exec_result["exit_code"], "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}
    if exec_result["exit_code"] != 0:
        result["error"] = "build_failed"
        result["message"] = f"Maven build failed with exit code {exec_result['exit_code']}"
    print(json.dumps(result, indent=2))
    return 0 if exec_result["exit_code"] == 0 else 1


# ============================================================================
# PARSE SUBCOMMAND
# ============================================================================

def detect_build_status(content: str) -> str:
    """Detect overall build status from log content."""
    if "BUILD SUCCESS" in content:
        return "SUCCESS"
    if "BUILD FAILURE" in content:
        return "FAILURE"
    if re.search(r"^\[ERROR\]", content, re.MULTILINE):
        return "FAILURE"
    return "SUCCESS"


def extract_duration(content: str) -> Optional[int]:
    """Extract total build time in milliseconds."""
    match = re.search(r"Total time:\s+([\d.]+)\s+s", content)
    if match:
        return int(float(match.group(1)) * 1000)
    match = re.search(r"Total time:\s+(\d+):(\d+)\s+min", content)
    if match:
        return (int(match.group(1)) * 60 + int(match.group(2))) * 1000
    return None


def extract_test_summary(content: str) -> dict:
    """Extract test execution summary."""
    pattern = r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)"
    matches = list(re.finditer(pattern, content))
    if matches:
        m = matches[-1]
        return {"tests_run": int(m.group(1)), "failures": int(m.group(2)), "errors": int(m.group(3)), "skipped": int(m.group(4))}
    return {"tests_run": 0, "failures": 0, "errors": 0, "skipped": 0}


def categorize_issue(message: str) -> str:
    """Categorize an issue based on its message content."""
    lower_msg = message.lower()
    if any(p in lower_msg for p in ["cannot find symbol", "incompatible types", "illegal start", "class, interface, or enum expected", "unreported exception", "method does not override", "not a statement", "package does not exist", "cannot be applied"]):
        return "compilation_error"
    if any(p in lower_msg for p in ["tests run:", "failure!", "test failure", "assertionfailed", "expected:"]):
        return "test_failure"
    if any(p in lower_msg for p in ["could not resolve dependencies", "could not find artifact", "missing, no dependency", "artifact not found", "non-resolvable"]):
        return "dependency_error"
    if any(p in lower_msg for p in ["javadoc", "no @param", "no @return", "@param name", "missing @"]):
        return "javadoc_warning"
    if "[deprecation]" in lower_msg or "has been deprecated" in lower_msg:
        return "deprecation_warning"
    if "[unchecked]" in lower_msg or "unchecked conversion" in lower_msg:
        return "unchecked_warning"
    if any(p in lower_msg for p in ["org.openrewrite", "rewrite-maven-plugin", "rewrite:"]):
        return "openrewrite_info"
    return "other"


def parse_file_location(line: str) -> dict:
    """Extract file, line, and column from a Maven error/warning line."""
    result = {"file": None, "line": None, "column": None}
    match = re.search(r"([^\s\[\]]+\.java):\[(\d+),(\d+)\]", line)
    if match:
        return {"file": match.group(1), "line": int(match.group(2)), "column": int(match.group(3))}
    match = re.search(r"([^\s\[\]]+\.java):(\d+):", line)
    if match:
        return {"file": match.group(1), "line": int(match.group(2)), "column": None}
    match = re.search(r"(\w+Test)\.(\w+):(\d+)", line)
    if match:
        return {"file": f"{match.group(1)}.java", "line": int(match.group(3)), "column": None, "method": match.group(2)}
    return result


def extract_issues(content: str, include_warnings: bool = True) -> list:
    """Extract all issues from Maven output."""
    issues = []
    for line_num, line in enumerate(content.split("\n"), 1):
        severity = None
        if "[ERROR]" in line:
            severity = "ERROR"
        elif include_warnings and "[WARNING]" in line:
            severity = "WARNING"
        if severity:
            message = re.sub(r"^\[(INFO|ERROR|WARNING)\]\s*", "", line.strip())
            if not message or message.startswith("->") or message.startswith("at "):
                continue
            location = parse_file_location(line)
            issues.append({"type": categorize_issue(message), "file": location.get("file"), "line": location.get("line"), "column": location.get("column"), "message": message[:500], "severity": severity, "log_line": line_num})
    return issues


def generate_summary(issues: list) -> dict:
    """Generate issue summary by category."""
    summary = {"compilation_errors": 0, "test_failures": 0, "javadoc_warnings": 0, "deprecation_warnings": 0, "unchecked_warnings": 0, "dependency_errors": 0, "openrewrite_info": 0, "other_warnings": 0, "other_errors": 0, "total_issues": len(issues)}
    for issue in issues:
        t, s = issue["type"], issue["severity"]
        if t == "compilation_error": summary["compilation_errors"] += 1
        elif t == "test_failure": summary["test_failures"] += 1
        elif t == "javadoc_warning": summary["javadoc_warnings"] += 1
        elif t == "deprecation_warning": summary["deprecation_warnings"] += 1
        elif t == "unchecked_warning": summary["unchecked_warnings"] += 1
        elif t == "dependency_error": summary["dependency_errors"] += 1
        elif t == "openrewrite_info": summary["openrewrite_info"] += 1
        elif s == "ERROR": summary["other_errors"] += 1
        else: summary["other_warnings"] += 1
    return summary


def cmd_parse(args):
    """Handle parse subcommand."""
    path = Path(args.log)
    if not path.exists():
        print(json.dumps({"status": "error", "error": f"Log file not found: {args.log}"}, indent=2))
        return 1
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(json.dumps({"status": "error", "error": f"Failed to read log file: {str(e)}"}, indent=2))
        return 1

    build_status = detect_build_status(content)
    duration = extract_duration(content)
    test_summary = extract_test_summary(content)
    issues = extract_issues(content, args.mode not in ["errors"])
    if args.mode == "no-openrewrite":
        issues = [i for i in issues if i["type"] != "openrewrite_info"]
    summary = generate_summary(issues)

    result = {"status": "success" if build_status == "SUCCESS" else "error", "data": {"build_status": build_status, "issues": issues, "summary": summary}, "metrics": {"duration_ms": duration, "tests_run": test_summary["tests_run"], "tests_failed": test_summary["failures"] + test_summary["errors"]}}
    print(json.dumps(result, indent=2))
    return 0


# ============================================================================
# FIND-MODULE SUBCOMMAND
# ============================================================================

def find_pom_files(root_dir: str) -> List[Path]:
    """Find all pom.xml files in the project."""
    pom_files = []
    for pom in Path(root_dir).rglob("pom.xml"):
        if not any(p.startswith('.') or p == 'target' for p in pom.parts):
            pom_files.append(pom)
    return sorted(pom_files)


def extract_artifact_id(pom_path: Path) -> Optional[str]:
    """Extract artifactId from a pom.xml file."""
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        elem = root.find('m:artifactId', ns) or root.find('artifactId')
        return elem.text.strip() if elem is not None and elem.text else None
    except Exception:
        return None


def get_module_path(pom_path: Path, root_dir: str) -> str:
    """Get the module path relative to root directory."""
    try:
        # Resolve symlinks for consistent comparison (macOS: /var -> /private/var)
        resolved_pom = Path(os.path.realpath(pom_path.parent))
        resolved_root = Path(os.path.realpath(root_dir))
        rel_path = resolved_pom.relative_to(resolved_root)
        return str(rel_path) if str(rel_path) != '.' else '.'
    except ValueError:
        return str(pom_path.parent)


def cmd_find_module(args):
    """Handle find-module subcommand."""
    if args.module_path:
        pom_path = Path(args.root) / args.module_path / "pom.xml"
        if not pom_path.exists():
            print(json.dumps({"status": "error", "error": "module_not_found", "message": f"No pom.xml found at {args.module_path}/pom.xml"}, indent=2))
            return 1
        artifact_id = extract_artifact_id(pom_path)
        if not artifact_id:
            print(json.dumps({"status": "error", "error": "invalid_pom", "message": f"Could not extract artifactId from {args.module_path}/pom.xml"}, indent=2))
            return 1
        print(json.dumps({"status": "success", "data": {"artifact_id": artifact_id, "module_path": args.module_path, "pom_file": f"{args.module_path}/pom.xml", "maven_pl_argument": f"-pl {args.module_path}" if args.module_path != '.' else ""}}, indent=2))
        return 0

    if not os.path.isdir(args.root):
        print(json.dumps({"status": "error", "error": "root_not_found", "message": f"Root directory not found: {args.root}"}, indent=2))
        return 1

    matches = []
    resolved_root = Path(os.path.realpath(args.root))
    for pom_path in find_pom_files(args.root):
        if extract_artifact_id(pom_path) == args.artifact_id:
            module_path = get_module_path(pom_path, args.root)
            # Use realpath for consistent comparison on macOS
            pom_file = str(Path(os.path.realpath(pom_path)).relative_to(resolved_root))
            matches.append({"artifact_id": args.artifact_id, "module_path": module_path, "pom_file": pom_file, "maven_pl_argument": f"-pl {module_path}" if module_path != '.' else ""})

    if not matches:
        print(json.dumps({"status": "error", "error": "artifact_not_found", "message": f"No module found with artifactId '{args.artifact_id}'"}, indent=2))
        return 1
    if len(matches) == 1:
        print(json.dumps({"status": "success", "data": matches[0]}, indent=2))
        return 0
    print(json.dumps({"status": "error", "error": "ambiguous_artifact_id", "message": f"Multiple modules found for artifactId '{args.artifact_id}'. Select one.", "choices": [m["module_path"] for m in matches]}, indent=2))
    return 1


# ============================================================================
# SEARCH-MARKERS SUBCOMMAND
# ============================================================================

MARKER_PATTERN = re.compile(r'/\*~~\(TODO:\s*(.+?)\)>\*/')
AUTO_SUPPRESS_RECIPES = {
    "CuiLogRecordPatternRecipe": {"category": "logrecord", "reason": "LogRecord warning - can be auto-suppressed for debug/trace logging"},
    "InvalidExceptionUsageRecipe": {"category": "exception", "reason": "Exception handling pattern - can be auto-suppressed for framework patterns"}
}


def extract_recipe_name(message: str) -> str:
    """Extract recipe name from marker message."""
    match = re.match(r'^(\w+(?:Recipe|Pattern))', message)
    if match:
        return match.group(1)
    parts = message.split()
    return parts[0].rstrip(' -:') if parts else "UnknownRecipe"


def cmd_search_markers(args):
    """Handle search-markers subcommand."""
    if not os.path.exists(args.source_dir):
        print(json.dumps({"status": "error", "error": "source_not_found", "message": f"Source directory not found: {args.source_dir}"}, indent=2))
        return 1

    extensions = [ext.strip() if ext.strip().startswith('.') else f'.{ext.strip()}' for ext in args.extensions.split(',')]
    files = []
    for ext in extensions:
        files.extend(Path(args.source_dir).rglob(f"*{ext}"))

    all_markers = []
    files_with_markers = set()

    for file_path in sorted(files):
        try:
            content = file_path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError):
            continue
        for line_num, line in enumerate(content.split('\n'), start=1):
            for match in MARKER_PATTERN.finditer(line):
                message = match.group(1).strip()
                recipe = extract_recipe_name(message)
                if recipe in AUTO_SUPPRESS_RECIPES:
                    info = AUTO_SUPPRESS_RECIPES[recipe]
                    category_info = {"action": "auto_suppress", "suppression_comment": f"// cui-rewrite:disable {recipe}", **info}
                else:
                    category_info = {"action": "ask_user", "category": "other", "reason": "Unknown recipe - requires user decision"}
                all_markers.append({"file": str(file_path), "line": line_num, "column": match.start() + 1, "message": message, "recipe": recipe, "raw_marker": match.group(0), **category_info})
                files_with_markers.add(str(file_path))

    auto_suppress = [m for m in all_markers if m["action"] == "auto_suppress"]
    ask_user = [m for m in all_markers if m["action"] == "ask_user"]

    result = {"status": "success", "data": {"total_markers": len(all_markers), "files_affected": len(files_with_markers), "by_category": {"auto_suppress": auto_suppress, "ask_user": ask_user}, "auto_suppress_count": len(auto_suppress), "ask_user_count": len(ask_user), "markers": all_markers}}
    print(json.dumps(result, indent=2))
    return 1 if len(ask_user) > 0 else 0


# ============================================================================
# CHECK-WARNINGS SUBCOMMAND
# ============================================================================

ALWAYS_FIXABLE_TYPES = ["javadoc_warning", "compilation_error", "deprecation_warning", "unchecked_warning"]


def is_acceptable(warning_message: str, patterns: List[str]) -> bool:
    """Check if a warning matches any acceptable pattern."""
    for pattern in patterns:
        clean_pattern = pattern[9:].strip() if pattern.startswith('[WARNING]') else pattern
        if clean_pattern in warning_message:
            return True
        try:
            if re.search(clean_pattern, warning_message, re.IGNORECASE):
                return True
        except re.error:
            pass
    return False


def flatten_patterns(acceptable_warnings: dict) -> List[str]:
    """Flatten acceptable_warnings object into a list of patterns."""
    patterns = []
    if isinstance(acceptable_warnings, dict):
        for value in acceptable_warnings.values():
            if isinstance(value, list):
                patterns.extend(str(p) for p in value if p)
    elif isinstance(acceptable_warnings, list):
        patterns.extend(str(p) for p in acceptable_warnings if p)
    return patterns


def cmd_check_warnings(args):
    """Handle check-warnings subcommand."""
    warnings = None
    patterns = []

    if args.warnings:
        try:
            warnings = json.loads(args.warnings)
        except json.JSONDecodeError as e:
            print(json.dumps({"success": False, "error": f"Invalid JSON in --warnings: {e}"}, indent=2))
            return 1
        if args.patterns:
            try:
                patterns = json.loads(args.patterns)
            except json.JSONDecodeError as e:
                print(json.dumps({"success": False, "error": f"Invalid JSON in --patterns: {e}"}, indent=2))
                return 1
        elif args.acceptable_warnings:
            try:
                patterns = flatten_patterns(json.loads(args.acceptable_warnings))
            except json.JSONDecodeError as e:
                print(json.dumps({"success": False, "error": f"Invalid JSON in --acceptable-warnings: {e}"}, indent=2))
                return 1
    else:
        if sys.stdin.isatty():
            print(json.dumps({"success": False, "error": "No input provided. Use --warnings/--patterns or pipe JSON to stdin."}, indent=2))
            return 1
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({"success": False, "error": f"Invalid JSON from stdin: {e}"}, indent=2))
            return 1
        warnings = input_data.get("warnings", [])
        patterns = input_data.get("patterns", []) or flatten_patterns(input_data.get("acceptable_warnings", {}))

    if warnings is None or not isinstance(warnings, list):
        print(json.dumps({"success": False, "error": "warnings must be an array"}, indent=2))
        return 1

    warning_items = [w for w in warnings if w.get("severity") == "WARNING"]
    acceptable, fixable, unknown = [], [], []

    for w in warning_items:
        wtype = w.get("type", "other")
        if wtype in ALWAYS_FIXABLE_TYPES:
            fixable.append(w)
        elif is_acceptable(w.get("message", ""), patterns):
            acceptable.append(w)
        elif wtype in ["compilation_error", "test_failure", "dependency_error"]:
            fixable.append(w)
        elif wtype == "openrewrite_info":
            acceptable.append(w)
        elif wtype in ["other", "other_warnings"]:
            unknown.append({**w, "requires_classification": True})
        else:
            fixable.append(w)

    result = {"success": True, "total": len(warning_items), "acceptable": len(acceptable), "fixable": len(fixable), "unknown": len(unknown), "categorized": {"acceptable": acceptable, "fixable": fixable, "unknown": unknown}}
    print(json.dumps(result, indent=2))
    return 1 if len(fixable) > 0 or len(unknown) > 0 else 0


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Maven build operations", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # execute subcommand
    exec_parser = subparsers.add_parser("execute", help="Execute Maven build with automatic log file handling")
    exec_parser.add_argument("--goals", required=True, help="Maven goals to execute")
    exec_parser.add_argument("--profile", help="Maven profile to activate")
    exec_parser.add_argument("--module", help="Specific module to build (-pl)")
    exec_parser.add_argument("--timeout", type=int, default=120000, help="Build timeout in milliseconds")
    exec_parser.add_argument("--mvnw", default="./mvnw", help="Path to Maven wrapper")
    exec_parser.set_defaults(func=cmd_execute)

    # parse subcommand
    parse_parser = subparsers.add_parser("parse", help="Parse Maven build output and categorize issues")
    parse_parser.add_argument("--log", required=True, help="Path to Maven build log file")
    parse_parser.add_argument("--mode", choices=["default", "errors", "structured", "no-openrewrite"], default="structured", help="Output mode")
    parse_parser.set_defaults(func=cmd_parse)

    # find-module subcommand
    find_parser = subparsers.add_parser("find-module", help="Find Maven module path from artifactId")
    find_group = find_parser.add_mutually_exclusive_group(required=True)
    find_group.add_argument("--artifact-id", help="ArtifactId to search for")
    find_group.add_argument("--module-path", help="Explicit module path to validate")
    find_parser.add_argument("--root", default=".", help="Project root directory")
    find_parser.set_defaults(func=cmd_find_module)

    # search-markers subcommand
    markers_parser = subparsers.add_parser("search-markers", help="Search for OpenRewrite TODO markers")
    markers_parser.add_argument("--source-dir", default="src", help="Directory to search")
    markers_parser.add_argument("--extensions", default=".java", help="Comma-separated extensions")
    markers_parser.set_defaults(func=cmd_search_markers)

    # check-warnings subcommand
    warn_parser = subparsers.add_parser("check-warnings", help="Categorize build warnings")
    warn_parser.add_argument("--warnings", help="JSON array of warning objects")
    warn_parser.add_argument("--patterns", help="JSON array of acceptable patterns")
    warn_parser.add_argument("--acceptable-warnings", dest="acceptable_warnings", help="JSON object with categorized patterns")
    warn_parser.set_defaults(func=cmd_check_warnings)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
