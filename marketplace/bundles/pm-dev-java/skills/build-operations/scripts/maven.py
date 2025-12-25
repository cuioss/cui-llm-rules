#!/usr/bin/env python3
"""
Maven build operations - run, execute, parse, find modules, search markers, check warnings.

Usage:
    maven.py run --targets <targets> [options]
    maven.py execute --goals <goals> [options]
    maven.py parse --log <path> [--mode <mode>]
    maven.py find-module --artifact-id <id> | --module-path <path>
    maven.py search-markers --source-dir <dir>
    maven.py check-warnings --warnings <json> [--patterns <json>]
    maven.py --help

Subcommands:
    run             Execute build and auto-parse on failure (primary API)
    execute         Execute Maven build with automatic log file handling
    parse           Parse Maven build output and categorize issues
    find-module     Find Maven module path from artifactId
    search-markers  Search for OpenRewrite TODO markers in source files
    check-warnings  Categorize build warnings against acceptable patterns
"""

import argparse
import sys

# Import command handlers from modularized files
from maven_cmd_run import cmd_run
from maven_cmd_execute import cmd_execute
from maven_cmd_parse import cmd_parse
from maven_cmd_find_module import cmd_find_module
from maven_cmd_search_markers import cmd_search_markers
from maven_cmd_check_warnings import cmd_check_warnings


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Maven build operations", formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run subcommand (primary API)
    run_parser = subparsers.add_parser("run", help="Execute build and auto-parse on failure (primary API)")
    run_parser.add_argument("--targets", required=True, help="Build targets to execute")
    run_parser.add_argument("--module", help="Specific module to build (-pl)")
    run_parser.add_argument("--profile", help="Maven profile to activate")
    run_parser.add_argument("--timeout", type=int, default=120000, help="Build timeout in milliseconds (default: 120000 = 2 min)")
    run_parser.add_argument("--mode", choices=["actionable", "structured", "errors"], default="actionable", help="Output mode")
    run_parser.add_argument("--mvnw", default="./mvnw", help="Path to Maven wrapper")
    run_parser.set_defaults(func=cmd_run)

    # execute subcommand
    exec_parser = subparsers.add_parser("execute", help="Execute Maven build with automatic log file handling")
    exec_parser.add_argument("--goals", required=True, help="Maven goals to execute")
    exec_parser.add_argument("--profile", help="Maven profile to activate")
    exec_parser.add_argument("--module", help="Specific module to build (-pl)")
    exec_parser.add_argument("--timeout", type=int, default=120000, help="Build timeout in milliseconds (default: 120000 = 2 min)")
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
