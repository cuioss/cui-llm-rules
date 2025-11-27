#!/usr/bin/env python3
"""
Find and categorize OpenRewrite TODO markers in source files.

Searches for markers left by OpenRewrite recipes and categorizes them
as auto-suppressible or requiring user decision.
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


# OpenRewrite marker pattern: /*~~(TODO: message)>*/
MARKER_PATTERN = re.compile(r'/\*~~\(TODO:\s*([^)]+)\)>\*/')

# Recipes that can be auto-suppressed
AUTO_SUPPRESS_RECIPES = {
    "CuiLogRecordPatternRecipe": {
        "category": "logrecord",
        "reason": "LogRecord warning - can be auto-suppressed for debug/trace logging",
    },
    "InvalidExceptionUsageRecipe": {
        "category": "exception",
        "reason": "Exception handling pattern - can be auto-suppressed for framework patterns",
    },
}


def extract_recipe_name(message: str) -> str | None:
    """Extract recipe name from marker message."""
    # Pattern: "RecipeName: actual message" or just look for known recipes
    for recipe in AUTO_SUPPRESS_RECIPES:
        if recipe.lower() in message.lower():
            return recipe

    # Try to extract from format "RecipeName: message"
    match = re.match(r"(\w+Recipe):", message)
    if match:
        return match.group(1)

    return None


def categorize_marker(message: str) -> tuple[str, str | None]:
    """Categorize marker as auto_suppress or ask_user."""
    recipe = extract_recipe_name(message)
    if recipe and recipe in AUTO_SUPPRESS_RECIPES:
        return "auto_suppress", recipe
    return "ask_user", recipe


def search_markers(
    source_dir: str, extensions: list[str]
) -> dict:
    """Search for OpenRewrite markers in source files."""
    root = Path(source_dir)
    if not root.exists():
        return {
            "status": "error",
            "error": "directory_not_found",
            "message": f"Source directory not found: {source_dir}",
        }

    markers = []
    files_affected = set()
    recipe_summary = defaultdict(int)

    by_category = {
        "auto_suppress": [],
        "ask_user": [],
    }

    # Search all files with specified extensions
    for ext in extensions:
        ext_clean = ext if ext.startswith(".") else f".{ext}"
        for file_path in root.rglob(f"*{ext_clean}"):
            # Skip build directories
            if any(
                part in ("build", "target", ".gradle", "node_modules")
                for part in file_path.parts
            ):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except (OSError, UnicodeDecodeError):
                continue

            for line_num, line in enumerate(lines, 1):
                for match in MARKER_PATTERN.finditer(line):
                    message = match.group(1).strip()
                    category, recipe = categorize_marker(message)

                    marker_info = {
                        "file": str(file_path.relative_to(root.parent)
                                    if root.parent != file_path.parent
                                    else file_path),
                        "line": line_num,
                        "message": message,
                        "recipe": recipe,
                        "column": match.start(),
                    }

                    if category == "auto_suppress" and recipe:
                        marker_info["suppression_comment"] = (
                            f"// cui-rewrite:disable {recipe}"
                        )
                        marker_info["reason"] = AUTO_SUPPRESS_RECIPES[recipe]["reason"]

                    markers.append(marker_info)
                    files_affected.add(str(file_path))
                    by_category[category].append(marker_info)

                    if recipe:
                        recipe_summary[recipe] += 1

    result = {
        "status": "success",
        "data": {
            "total_markers": len(markers),
            "files_affected": len(files_affected),
            "recipe_summary": dict(recipe_summary),
            "by_category": by_category,
            "auto_suppress_count": len(by_category["auto_suppress"]),
            "ask_user_count": len(by_category["ask_user"]),
            "markers": markers,
        },
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Search for OpenRewrite markers in source files"
    )
    parser.add_argument(
        "--source-dir",
        default="src",
        help="Directory to search (default: src)",
    )
    parser.add_argument(
        "--extensions",
        default=".java,.kt",
        help="File extensions to search, comma-separated (default: .java,.kt)",
    )

    args = parser.parse_args()

    extensions = [e.strip() for e in args.extensions.split(",")]
    result = search_markers(args.source_dir, extensions)

    print(json.dumps(result, indent=2))

    # Exit code based on whether user action is needed
    if result["status"] == "success":
        if result["data"]["ask_user_count"] > 0:
            exit(1)
    exit(0)


if __name__ == "__main__":
    main()
