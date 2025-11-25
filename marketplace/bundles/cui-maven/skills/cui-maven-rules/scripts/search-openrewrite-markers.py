#!/usr/bin/env python3
"""
Search for OpenRewrite TODO markers in source files.

Finds and categorizes OpenRewrite markers that indicate code patterns
requiring manual review or suppression.

Usage:
    python3 search-openrewrite-markers.py --source-dir <dir>
    python3 search-openrewrite-markers.py --help

Output:
    JSON with categorized markers:
    {
        "status": "success",
        "data": {
            "total_markers": 5,
            "files_affected": 3,
            "by_category": {
                "auto_suppress": [...],
                "ask_user": [...]
            },
            "markers": [...]
        }
    }
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


# Marker pattern: /*~~(TODO: message)>*/
MARKER_PATTERN = re.compile(r'/\*~~\(TODO:\s*(.+?)\)>\*/')

# Recipes that can be auto-suppressed (from standards)
AUTO_SUPPRESS_RECIPES = {
    "CuiLogRecordPatternRecipe": {
        "category": "logrecord",
        "reason": "LogRecord warning - can be auto-suppressed for debug/trace logging"
    },
    "InvalidExceptionUsageRecipe": {
        "category": "exception",
        "reason": "Exception handling pattern - can be auto-suppressed for framework patterns"
    }
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Search for OpenRewrite TODO markers in source files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Search default src directory
    python3 search-openrewrite-markers.py

    # Search specific directory
    python3 search-openrewrite-markers.py --source-dir src/main/java

    # Search multiple modules
    python3 search-openrewrite-markers.py --source-dir .
        """,
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default="src",
        help="Directory to search for markers (default: src)"
    )
    parser.add_argument(
        "--extensions",
        type=str,
        default=".java",
        help="Comma-separated file extensions to search (default: .java)"
    )
    return parser.parse_args()


def find_java_files(source_dir: str, extensions: List[str]) -> List[Path]:
    """Find all files with specified extensions in directory."""
    files = []
    source_path = Path(source_dir)

    if not source_path.exists():
        return []

    for ext in extensions:
        files.extend(source_path.rglob(f"*{ext}"))

    return sorted(files)


def extract_recipe_name(message: str) -> str:
    """Extract recipe name from marker message."""
    # Common patterns:
    # "CuiLogRecordPatternRecipe - LOGGER call does not use LogRecord"
    # "InvalidExceptionUsageRecipe - catch block does not..."

    # Try to extract recipe name (ends with Recipe or Pattern)
    match = re.match(r'^(\w+(?:Recipe|Pattern))', message)
    if match:
        return match.group(1)

    # Fallback: first word
    parts = message.split()
    if parts:
        return parts[0].rstrip(' -:')

    return "UnknownRecipe"


def categorize_marker(recipe_name: str) -> Dict[str, Any]:
    """Categorize a marker based on its recipe."""
    if recipe_name in AUTO_SUPPRESS_RECIPES:
        info = AUTO_SUPPRESS_RECIPES[recipe_name]
        return {
            "action": "auto_suppress",
            "suppression_comment": f"// cui-rewrite:disable {recipe_name}",
            **info
        }

    return {
        "action": "ask_user",
        "category": "other",
        "reason": "Unknown recipe - requires user decision"
    }


def search_file(file_path: Path) -> List[Dict[str, Any]]:
    """Search a single file for markers."""
    markers = []

    try:
        content = file_path.read_text(encoding='utf-8')
    except (IOError, UnicodeDecodeError):
        return []

    lines = content.split('\n')

    for line_num, line in enumerate(lines, start=1):
        for match in MARKER_PATTERN.finditer(line):
            message = match.group(1).strip()
            recipe_name = extract_recipe_name(message)
            category_info = categorize_marker(recipe_name)

            markers.append({
                "file": str(file_path),
                "line": line_num,
                "column": match.start() + 1,
                "message": message,
                "recipe": recipe_name,
                "raw_marker": match.group(0),
                **category_info
            })

    return markers


def search_markers(source_dir: str, extensions: List[str]) -> Dict[str, Any]:
    """Search all files for markers and return categorized results."""
    files = find_java_files(source_dir, extensions)

    if not files:
        return {
            "status": "success",
            "data": {
                "total_markers": 0,
                "files_affected": 0,
                "by_category": {
                    "auto_suppress": [],
                    "ask_user": []
                },
                "markers": []
            }
        }

    all_markers = []
    files_with_markers = set()

    for file_path in files:
        file_markers = search_file(file_path)
        if file_markers:
            files_with_markers.add(str(file_path))
            all_markers.extend(file_markers)

    # Categorize markers
    auto_suppress = [m for m in all_markers if m["action"] == "auto_suppress"]
    ask_user = [m for m in all_markers if m["action"] == "ask_user"]

    # Group by recipe for summary
    recipe_counts = {}
    for marker in all_markers:
        recipe = marker["recipe"]
        recipe_counts[recipe] = recipe_counts.get(recipe, 0) + 1

    return {
        "status": "success",
        "data": {
            "total_markers": len(all_markers),
            "files_affected": len(files_with_markers),
            "recipe_summary": recipe_counts,
            "by_category": {
                "auto_suppress": auto_suppress,
                "ask_user": ask_user
            },
            "auto_suppress_count": len(auto_suppress),
            "ask_user_count": len(ask_user),
            "markers": all_markers
        }
    }


def main():
    """Main entry point."""
    args = parse_args()

    # Parse extensions
    extensions = [ext.strip() for ext in args.extensions.split(',')]
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    # Check source directory exists
    if not os.path.exists(args.source_dir):
        result = {
            "status": "error",
            "error": "source_not_found",
            "message": f"Source directory not found: {args.source_dir}"
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Search for markers
    result = search_markers(args.source_dir, extensions)

    print(json.dumps(result, indent=2))

    # Exit 0 if no markers or all auto-suppressible
    # Exit 1 if there are markers requiring user action
    if result["data"]["ask_user_count"] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
