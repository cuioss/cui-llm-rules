#!/usr/bin/env python3
"""
Gradle build operations - execute, parse, find projects, search markers, check warnings.

Usage:
    gradle.py execute --tasks <tasks> [options]
    gradle.py parse --log <path> [--mode <mode>]
    gradle.py find-project --project-name <name> | --project-path <path>
    gradle.py search-markers --source-dir <dir>
    gradle.py check-warnings --warnings <json> [--acceptable-warnings <json>]
    gradle.py --help

Subcommands:
    execute         Execute Gradle build with automatic log file handling
    parse           Parse Gradle build output and categorize issues
    find-project    Find Gradle project path from project name
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
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


# ============================================================================
# EXECUTE SUBCOMMAND
# ============================================================================

def generate_log_filename() -> str:
    """Generate timestamped log filename."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"build/build-output-{timestamp}.log"


def pre_create_log_file(log_file: str) -> bool:
    """Pre-create log file and parent directory."""
    try:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return True
    except OSError:
        return False


def build_gradle_command(tasks: str, project: str, skip_tests: bool, fail_at_end: bool, gradlew: str) -> list:
    """Build Gradle command list from arguments."""
    cmd = [gradlew]
    cmd.extend(tasks.split())
    if project:
        if project.startswith(":"):
            cmd.append(project)
        else:
            cmd.extend(["-p", project])
    if skip_tests:
        cmd.extend(["-x", "test"])
    if fail_at_end:
        cmd.append("--continue")
    cmd.append("--console=plain")
    return cmd


def execute_gradle(cmd: list, timeout_ms: int, log_file: str) -> dict:
    """Execute Gradle command and return result."""
    timeout_seconds = timeout_ms / 1000.0
    start_time = time.time()

    try:
        with open(log_file, "w", encoding="utf-8") as log_fh:
            result = subprocess.run(cmd, timeout=timeout_seconds, stdout=log_fh, stderr=subprocess.STDOUT, check=False)
        duration_ms = int((time.time() - start_time) * 1000)
        return {"exit_code": result.returncode, "duration_ms": duration_ms, "timed_out": False}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "duration_ms": int((time.time() - start_time) * 1000), "timed_out": True}
    except FileNotFoundError:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": f"Gradle wrapper not found: {cmd[0]}"}
    except OSError as e:
        return {"exit_code": -1, "duration_ms": 0, "timed_out": False, "error": str(e)}


def cmd_execute(args):
    """Handle execute subcommand."""
    if not Path(args.gradlew).exists():
        print(json.dumps({"status": "error", "error": "gradlew_not_found", "message": f"Gradle wrapper not found at {args.gradlew}. Run 'gradle wrapper' to generate it."}, indent=2))
        return 1

    log_file = generate_log_filename()
    if not pre_create_log_file(log_file):
        print(json.dumps({"status": "error", "error": "log_file_creation_failed", "message": f"Failed to create log file: {log_file}"}, indent=2))
        return 1

    cmd = build_gradle_command(args.tasks, args.project, args.skip_tests, args.fail_at_end, args.gradlew)
    command_str = " ".join(cmd)
    print(f"[EXEC] {command_str}", file=sys.stderr)

    exec_result = execute_gradle(cmd, args.timeout, log_file)

    if "error" in exec_result:
        print(json.dumps({"status": "error", "error": "execution_failed", "message": exec_result["error"], "data": {"log_file": log_file, "command_executed": command_str}}, indent=2))
        return 1

    if exec_result["timed_out"]:
        print(json.dumps({"status": "error", "error": "timeout", "message": f"Build timed out after {args.timeout}ms", "data": {"log_file": log_file, "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}, indent=2))
        return 1

    result = {"status": "success", "data": {"log_file": log_file, "exit_code": exec_result["exit_code"], "duration_ms": exec_result["duration_ms"], "command_executed": command_str}}
    print(json.dumps(result, indent=2))
    return 0


# ============================================================================
# PARSE SUBCOMMAND
# ============================================================================

COMPILATION_PATTERNS = [
    r"error:\s+cannot find symbol", r"error:\s+incompatible types", r"error:\s+illegal start",
    r"error:\s+';' expected", r"error:\s+class .* is public", r"error:\s+package .* does not exist",
    r"error:\s+method .* cannot be applied", r"error:\s+unreported exception",
    r"error:\s+variable .* might not have been initialized", r"error:\s+cannot access",
    r"Execution failed for task ':.*:compileJava'", r"Execution failed for task ':.*:compileKotlin'",
]
TEST_FAILURE_PATTERNS = [r">\s+\d+ tests? completed, \d+ failed", r"FAILED", r"AssertionFailedError", r"AssertionError", r"Execution failed for task ':.*:test'"]
DEPENDENCY_PATTERNS = [r"Could not resolve", r"Could not find", r"Could not download", r"Failed to resolve", r"Cannot resolve external dependency"]
JAVADOC_PATTERNS = [r"warning:\s+no @param", r"warning:\s+no @return", r"warning:\s+missing @", r"javadoc", r"Execution failed for task ':.*:javadoc'"]
DEPRECATION_PATTERNS = [r"\[deprecation\]", r"has been deprecated", r"is deprecated"]
UNCHECKED_PATTERNS = [r"\[unchecked\]", r"unchecked conversion", r"unchecked call"]


def categorize_line(line: str) -> Optional[str]:
    """Categorize a log line by issue type."""
    for pattern in COMPILATION_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE): return "compilation_error"
    for pattern in TEST_FAILURE_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE): return "test_failure"
    for pattern in DEPENDENCY_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE): return "dependency_error"
    for pattern in JAVADOC_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE): return "javadoc_warning"
    for pattern in DEPRECATION_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE): return "deprecation_warning"
    for pattern in UNCHECKED_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE): return "unchecked_warning"
    return None


def extract_file_location(line: str) -> Tuple[str, int, int]:
    """Extract file path, line, and column from error message."""
    match = re.search(r"([^\s:]+\.(java|kt|groovy)):(\d+):?(\d+)?", line)
    if match:
        return match.group(1), int(match.group(3)), int(match.group(4)) if match.group(4) else 0
    return "", 0, 0


def parse_build_status(lines: List[str]) -> str:
    """Determine overall build status from log lines."""
    for line in reversed(lines[-50:]):
        if "BUILD SUCCESSFUL" in line: return "SUCCESS"
        if "BUILD FAILED" in line: return "FAILURE"
    return "UNKNOWN"


def parse_metrics(lines: List[str]) -> dict:
    """Extract build metrics from log."""
    metrics = {"duration_ms": 0, "tasks_executed": 0, "tests_run": 0, "tests_failed": 0}
    for line in lines:
        duration_match = re.search(r"BUILD (?:SUCCESSFUL|FAILED) in (?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s)?", line)
        if duration_match:
            hours, minutes, seconds = int(duration_match.group(1) or 0), int(duration_match.group(2) or 0), int(duration_match.group(3) or 0)
            metrics["duration_ms"] = (hours * 3600 + minutes * 60 + seconds) * 1000
        tasks_match = re.search(r"(\d+) actionable tasks?: (\d+) executed", line)
        if tasks_match: metrics["tasks_executed"] = int(tasks_match.group(2))
        test_match = re.search(r"(\d+) tests? completed(?:, (\d+) failed)?(?:, (\d+) skipped)?", line)
        if test_match:
            metrics["tests_run"] = int(test_match.group(1))
            metrics["tests_failed"] = int(test_match.group(2) or 0)
    return metrics


def cmd_parse(args):
    """Handle parse subcommand."""
    path = Path(args.log)
    if not path.exists():
        print(json.dumps({"status": "error", "error": "file_not_found", "message": f"Log file not found: {args.log}"}, indent=2))
        return 1

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    issues, seen = [], set()
    for line_num, line in enumerate(lines, 1):
        issue_type = categorize_line(line)
        if issue_type:
            file_path, file_line, file_col = extract_file_location(line)
            message = line.strip()
            dedup_key = f"{issue_type}:{file_path}:{file_line}:{message[:100]}"
            if dedup_key in seen: continue
            seen.add(dedup_key)
            severity = "ERROR" if "error" in issue_type else "WARNING"
            issues.append({"type": issue_type, "file": file_path, "line": file_line, "column": file_col, "message": message[:500], "severity": severity, "log_line": line_num})

    build_status = parse_build_status(lines)
    metrics = parse_metrics(lines)

    if args.mode == "errors":
        issues = [i for i in issues if i["severity"] == "ERROR"]

    summary = {"compilation_errors": sum(1 for i in issues if i["type"] == "compilation_error"), "test_failures": sum(1 for i in issues if i["type"] == "test_failure"), "javadoc_warnings": sum(1 for i in issues if i["type"] == "javadoc_warning"), "deprecation_warnings": sum(1 for i in issues if i["type"] == "deprecation_warning"), "unchecked_warnings": sum(1 for i in issues if i["type"] == "unchecked_warning"), "dependency_errors": sum(1 for i in issues if i["type"] == "dependency_error"), "total_issues": len(issues)}
    result = {"status": "success", "data": {"build_status": build_status, "issues": issues, "summary": summary}, "metrics": metrics}

    if args.mode == "default":
        output_lines = [f"Build Status: {build_status}", f"Duration: {metrics['duration_ms']}ms", f"Tasks: {metrics['tasks_executed']} executed", f"Tests: {metrics['tests_run']} run, {metrics['tests_failed']} failed", "", "Issues Summary:", f"  Compilation Errors: {summary['compilation_errors']}", f"  Test Failures: {summary['test_failures']}", f"  Javadoc Warnings: {summary['javadoc_warnings']}", f"  Total: {summary['total_issues']}"]
        print("\n".join(output_lines))
        return 0

    print(json.dumps(result, indent=2))
    return 0


# ============================================================================
# FIND-PROJECT SUBCOMMAND
# ============================================================================

def find_settings_file(root: Path) -> Optional[Path]:
    """Find settings.gradle or settings.gradle.kts."""
    for name in ["settings.gradle.kts", "settings.gradle"]:
        settings_path = root / name
        if settings_path.exists(): return settings_path
    return None


def parse_included_projects(settings_path: Path) -> List[str]:
    """Parse included projects from settings file."""
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()
    projects = []
    for pattern in [r'include\s*\(\s*([^)]+)\s*\)', r"include\s+(['\"][^'\"]+['\"](?:\s*,\s*['\"][^'\"]+['\"])*)"]:
        for match in re.finditer(pattern, content):
            for quoted in re.findall(r'["\']([^"\']+)["\']', match.group(1)):
                projects.append(quoted if quoted.startswith(":") else f":{quoted}")
    return list(set(projects))


def get_root_project_name(settings_path: Path) -> Optional[str]:
    """Extract rootProject.name from settings file."""
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'rootProject\.name\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else None


def find_build_files(root: Path) -> List[Path]:
    """Find all build.gradle and build.gradle.kts files."""
    build_files = []
    for pattern in ["**/build.gradle", "**/build.gradle.kts"]:
        for path in root.glob(pattern):
            if not any(part.startswith(".") or part in ("build", "target", ".gradle") for part in path.parts):
                build_files.append(path)
    return build_files


def project_path_to_gradle_notation(root: Path, project_dir: Path) -> str:
    """Convert file path to Gradle project notation."""
    try:
        resolved_root = Path(os.path.realpath(root))
        resolved_dir = Path(os.path.realpath(project_dir))
        relative = resolved_dir.relative_to(resolved_root)
        parts = relative.parts
        return ":" + ":".join(parts) if parts else ":"
    except ValueError:
        return ":"


def cmd_find_project(args):
    """Handle find-project subcommand."""
    root = Path(os.path.realpath(args.root))
    if not root.exists():
        print(json.dumps({"status": "error", "error": "root_not_found", "message": f"Root directory not found: {args.root}"}, indent=2))
        return 1

    if args.project_path:
        dir_path = args.project_path.lstrip(":").replace(":", "/") if args.project_path.startswith(":") else args.project_path
        full_path = root / dir_path
        if not full_path.exists():
            print(json.dumps({"status": "error", "error": "path_not_found", "message": f"Project path does not exist: {args.project_path}"}, indent=2))
            return 1
        build_file = None
        for ext in [".kts", ""]:
            candidate = full_path / f"build.gradle{ext}"
            if candidate.exists():
                build_file = str(Path(os.path.realpath(candidate)).relative_to(root))
                break
        if not build_file:
            print(json.dumps({"status": "error", "error": "no_build_file", "message": f"No build.gradle(.kts) found in: {args.project_path}"}, indent=2))
            return 1
        gradle_path = ":" + dir_path.replace("/", ":")
        parts = dir_path.split("/")
        parent_projects = [":" + ":".join(parts[:i]) for i in range(1, len(parts))]
        print(json.dumps({"status": "success", "data": {"project_name": full_path.name, "project_path": gradle_path, "build_file": build_file, "parent_projects": parent_projects, "gradle_p_argument": f"-p {dir_path}"}}, indent=2))
        return 0

    settings_file = find_settings_file(root)
    included_projects = parse_included_projects(settings_file) if settings_file else []
    root_project_name = get_root_project_name(settings_file) if settings_file else None

    if root_project_name and args.project_name == root_project_name:
        for ext in [".kts", ""]:
            candidate = root / f"build.gradle{ext}"
            if candidate.exists():
                print(json.dumps({"status": "success", "data": {"project_name": args.project_name, "project_path": ":", "build_file": f"build.gradle{ext}", "parent_projects": [], "gradle_p_argument": ""}}, indent=2))
                return 0

    matches = []
    for project in included_projects:
        project_last = project.split(":")[-1]
        if project_last == args.project_name or project == f":{args.project_name}":
            matches.append(project)

    for build_file in find_build_files(root):
        if build_file.parent.name == args.project_name:
            project_path = project_path_to_gradle_notation(root, build_file.parent)
            if project_path not in matches:
                matches.append(project_path)

    if not matches:
        print(json.dumps({"status": "error", "error": "project_not_found", "message": f"No project found with name '{args.project_name}'"}, indent=2))
        return 1
    if len(matches) > 1:
        print(json.dumps({"status": "error", "error": "ambiguous_project_name", "message": f"Multiple projects found for name '{args.project_name}'. Select one.", "choices": matches}, indent=2))
        return 1

    project_path = matches[0]
    dir_path = project_path.lstrip(":").replace(":", "/")
    build_file = None
    for ext in [".kts", ""]:
        candidate = root / dir_path / f"build.gradle{ext}"
        if candidate.exists():
            build_file = str(Path(os.path.realpath(candidate)).relative_to(root))
            break

    parts = project_path.lstrip(":").split(":")
    parent_projects = [":" + ":".join(parts[:i]) for i in range(1, len(parts))]
    print(json.dumps({"status": "success", "data": {"project_name": args.project_name, "project_path": project_path, "build_file": build_file, "parent_projects": parent_projects, "gradle_p_argument": f"-p {dir_path}" if dir_path else ""}}, indent=2))
    return 0


# ============================================================================
# SEARCH-MARKERS SUBCOMMAND
# ============================================================================

MARKER_PATTERN = re.compile(r'/\*~~\(TODO:\s*(.+?)\)>\*/')
AUTO_SUPPRESS_RECIPES = {
    "CuiLogRecordPatternRecipe": {"category": "logrecord", "reason": "LogRecord warning - can be auto-suppressed for debug/trace logging"},
    "InvalidExceptionUsageRecipe": {"category": "exception", "reason": "Exception handling pattern - can be auto-suppressed for framework patterns"}
}


def extract_recipe_name(message: str) -> Optional[str]:
    """Extract recipe name from marker message."""
    for recipe in AUTO_SUPPRESS_RECIPES:
        if recipe.lower() in message.lower():
            return recipe
    match = re.match(r"(\w+Recipe):", message)
    return match.group(1) if match else None


def cmd_search_markers(args):
    """Handle search-markers subcommand."""
    if not os.path.exists(args.source_dir):
        print(json.dumps({"status": "error", "error": "source_not_found", "message": f"Source directory not found: {args.source_dir}"}, indent=2))
        return 1

    extensions = [ext.strip() if ext.strip().startswith('.') else f'.{ext.strip()}' for ext in args.extensions.split(',')]
    root = Path(args.source_dir)
    markers, files_affected, recipe_summary = [], set(), defaultdict(int)
    by_category = {"auto_suppress": [], "ask_user": []}

    for ext in extensions:
        for file_path in root.rglob(f"*{ext}"):
            if any(part in ("build", "target", ".gradle", "node_modules") for part in file_path.parts):
                continue
            try:
                content = file_path.read_text(encoding='utf-8')
            except (IOError, UnicodeDecodeError):
                continue
            for line_num, line in enumerate(content.split('\n'), start=1):
                for match in MARKER_PATTERN.finditer(line):
                    message = match.group(1).strip()
                    recipe = extract_recipe_name(message)
                    if recipe and recipe in AUTO_SUPPRESS_RECIPES:
                        info = AUTO_SUPPRESS_RECIPES[recipe]
                        category_info = {"action": "auto_suppress", "suppression_comment": f"// cui-rewrite:disable {recipe}", **info}
                    else:
                        category_info = {"action": "ask_user", "category": "other", "reason": "Unknown recipe - requires user decision"}
                    marker_info = {"file": str(file_path), "line": line_num, "column": match.start() + 1, "message": message, "recipe": recipe, "raw_marker": match.group(0), **category_info}
                    markers.append(marker_info)
                    files_affected.add(str(file_path))
                    by_category[category_info["action"]].append(marker_info)
                    if recipe:
                        recipe_summary[recipe] += 1

    result = {"status": "success", "data": {"total_markers": len(markers), "files_affected": len(files_affected), "recipe_summary": dict(recipe_summary), "by_category": by_category, "auto_suppress_count": len(by_category["auto_suppress"]), "ask_user_count": len(by_category["ask_user"]), "markers": markers}}
    print(json.dumps(result, indent=2))
    return 1 if len(by_category["ask_user"]) > 0 else 0


# ============================================================================
# CHECK-WARNINGS SUBCOMMAND
# ============================================================================

ALWAYS_FIXABLE_TYPES = ["javadoc_warning", "compilation_error", "deprecation_warning", "unchecked_warning"]


def match_pattern(message: str, pattern: str) -> bool:
    """Check if message matches pattern."""
    if message == pattern: return True
    if pattern.endswith("*") and message.startswith(pattern[:-1]): return True
    if pattern.startswith("*") and pattern.endswith("*") and pattern[1:-1] in message: return True
    if pattern.startswith("*") and message.endswith(pattern[1:]): return True
    if pattern.startswith("^"):
        try:
            if re.match(pattern, message): return True
        except re.error:
            pass
    return False


def cmd_check_warnings(args):
    """Handle check-warnings subcommand."""
    warnings, acceptable_patterns = None, {}

    if args.warnings:
        try:
            warnings = json.loads(args.warnings)
        except json.JSONDecodeError as e:
            print(json.dumps({"success": False, "error": f"Invalid warnings JSON: {e}"}, indent=2))
            return 1
        if args.acceptable_warnings:
            try:
                acceptable_patterns = json.loads(args.acceptable_warnings)
            except json.JSONDecodeError:
                pass
    else:
        if sys.stdin.isatty():
            print(json.dumps({"success": False, "error": "No input provided. Use --warnings or pipe JSON to stdin."}, indent=2))
            return 1
        try:
            data = json.load(sys.stdin)
            warnings = data.get("warnings", [])
            acceptable_patterns = data.get("acceptable_warnings", {})
        except json.JSONDecodeError as e:
            print(json.dumps({"success": False, "error": f"Invalid stdin JSON: {e}"}, indent=2))
            return 1

    if warnings is None or not isinstance(warnings, list):
        print(json.dumps({"success": False, "error": "warnings must be an array"}, indent=2))
        return 1

    categorized = {"acceptable": [], "fixable": [], "unknown": []}
    for warning in warnings:
        warning_type = warning.get("type", "other")
        message = warning.get("message", "")

        if warning_type in ALWAYS_FIXABLE_TYPES:
            categorized["fixable"].append({**warning, "reason": f"Type '{warning_type}' is always fixable"})
            continue

        is_acceptable, matched_category = False, None
        for category, patterns in acceptable_patterns.items():
            for pattern in patterns:
                if match_pattern(message, pattern):
                    is_acceptable, matched_category = True, category
                    break
            if is_acceptable:
                break

        if is_acceptable:
            categorized["acceptable"].append({**warning, "reason": f"Matches acceptable pattern in '{matched_category}'"})
        else:
            categorized["unknown"].append({**warning, "reason": "No matching acceptable pattern"})

    result = {"success": True, "total": len(warnings), "acceptable": len(categorized["acceptable"]), "fixable": len(categorized["fixable"]), "unknown": len(categorized["unknown"]), "categorized": categorized}
    print(json.dumps(result, indent=2))
    return 1 if result["fixable"] > 0 or result["unknown"] > 0 else 0


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Gradle build operations", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # execute subcommand
    exec_parser = subparsers.add_parser("execute", help="Execute Gradle build with automatic log file handling")
    exec_parser.add_argument("--tasks", required=True, help="Gradle tasks to execute")
    exec_parser.add_argument("--project", help="Specific subproject (-p or :project:path)")
    exec_parser.add_argument("--skip-tests", action="store_true", help="Skip tests (-x test)")
    exec_parser.add_argument("--fail-at-end", action="store_true", help="Continue on failure (--continue)")
    exec_parser.add_argument("--timeout", type=int, default=120000, help="Build timeout in milliseconds")
    exec_parser.add_argument("--gradlew", default="./gradlew", help="Path to Gradle wrapper")
    exec_parser.set_defaults(func=cmd_execute)

    # parse subcommand
    parse_parser = subparsers.add_parser("parse", help="Parse Gradle build output and categorize issues")
    parse_parser.add_argument("--log", required=True, help="Path to Gradle build log file")
    parse_parser.add_argument("--mode", choices=["default", "errors", "structured"], default="structured", help="Output mode")
    parse_parser.set_defaults(func=cmd_parse)

    # find-project subcommand
    find_parser = subparsers.add_parser("find-project", help="Find Gradle project path from project name")
    find_group = find_parser.add_mutually_exclusive_group(required=True)
    find_group.add_argument("--project-name", help="Project name to search for")
    find_group.add_argument("--project-path", help="Explicit project path to validate")
    find_parser.add_argument("--root", default=".", help="Project root directory")
    find_parser.set_defaults(func=cmd_find_project)

    # search-markers subcommand
    markers_parser = subparsers.add_parser("search-markers", help="Search for OpenRewrite TODO markers")
    markers_parser.add_argument("--source-dir", default="src", help="Directory to search")
    markers_parser.add_argument("--extensions", default=".java,.kt", help="Comma-separated extensions")
    markers_parser.set_defaults(func=cmd_search_markers)

    # check-warnings subcommand
    warn_parser = subparsers.add_parser("check-warnings", help="Categorize build warnings")
    warn_parser.add_argument("--warnings", help="JSON array of warnings")
    warn_parser.add_argument("--acceptable-warnings", dest="acceptable_warnings", help="JSON object with acceptable patterns")
    warn_parser.set_defaults(func=cmd_check_warnings)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
