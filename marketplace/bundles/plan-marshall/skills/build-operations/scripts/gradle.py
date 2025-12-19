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
import sys

# Import command handlers from modularized files
from gradle_cmd_execute import cmd_execute
from gradle_cmd_parse import cmd_parse
from gradle_cmd_find_project import cmd_find_project
from gradle_cmd_search_markers import cmd_search_markers
from gradle_cmd_check_warnings import cmd_check_warnings


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
    exec_parser.add_argument("--timeout", type=int, default=120000, help="Build timeout in milliseconds (default: 120000 = 2 min)")
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
