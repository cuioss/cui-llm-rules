#!/usr/bin/env python3
"""
Find Maven module path from artifactId.

Searches for Maven modules by artifactId and returns the module path
suitable for use with Maven's -pl argument.

Usage:
    python3 find-module-path.py --artifact-id <artifact-id>
    python3 find-module-path.py --module-path <path>  # Validate existing path
    python3 find-module-path.py --help

Output:
    JSON with module information:
    {
        "status": "success",
        "data": {
            "artifact_id": "auth-service",
            "module_path": "services/auth-service",
            "pom_file": "services/auth-service/pom.xml",
            "parent_modules": ["services"],
            "maven_pl_argument": "-pl services/auth-service"
        }
    }

    On ambiguity (multiple matches):
    {
        "status": "error",
        "error": "ambiguous_artifact_id",
        "message": "Multiple modules found for artifactId 'auth-service'. Select one.",
        "choices": ["modules/auth-service", "legacy/auth-service"]
    }
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Find Maven module path from artifactId",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Find module by artifactId
    python3 find-module-path.py --artifact-id auth-service

    # Validate an explicit module path
    python3 find-module-path.py --module-path services/auth-service

    # Search from specific root
    python3 find-module-path.py --artifact-id auth-service --root /path/to/project
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--artifact-id",
        type=str,
        help="ArtifactId to search for"
    )
    group.add_argument(
        "--module-path",
        type=str,
        help="Explicit module path to validate"
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Project root directory (default: current directory)"
    )
    return parser.parse_args()


def find_pom_files(root_dir: str) -> List[Path]:
    """Find all pom.xml files in the project."""
    root_path = Path(root_dir)
    pom_files = []

    for pom in root_path.rglob("pom.xml"):
        # Skip target directories and hidden directories
        parts = pom.parts
        if any(p.startswith('.') or p == 'target' for p in parts):
            continue
        pom_files.append(pom)

    return sorted(pom_files)


def extract_artifact_id(pom_path: Path) -> Optional[str]:
    """
    Extract artifactId from a pom.xml file.

    Only extracts the module's own artifactId, not dependencies.
    """
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # Handle Maven namespace
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

        # Try with namespace first
        artifact_elem = root.find('m:artifactId', ns)
        if artifact_elem is not None and artifact_elem.text:
            return artifact_elem.text.strip()

        # Try without namespace (some POMs don't use it)
        artifact_elem = root.find('artifactId')
        if artifact_elem is not None and artifact_elem.text:
            return artifact_elem.text.strip()

        return None
    except ET.ParseError:
        return None
    except Exception:
        return None


def get_module_path(pom_path: Path, root_dir: str) -> str:
    """Get the module path relative to root directory."""
    root_path = Path(root_dir).resolve()
    pom_parent = pom_path.parent.resolve()

    try:
        rel_path = pom_parent.relative_to(root_path)
        return str(rel_path) if str(rel_path) != '.' else '.'
    except ValueError:
        return str(pom_parent)


def get_parent_modules(module_path: str) -> List[str]:
    """Get list of parent module paths."""
    if module_path == '.' or not module_path:
        return []

    parts = Path(module_path).parts
    parents = []
    for i in range(len(parts) - 1):
        parents.append(str(Path(*parts[:i + 1])))
    return parents


def find_modules_by_artifact_id(artifact_id: str, root_dir: str) -> List[Dict[str, Any]]:
    """Find all modules matching the given artifactId."""
    pom_files = find_pom_files(root_dir)
    matches = []

    for pom_path in pom_files:
        pom_artifact_id = extract_artifact_id(pom_path)
        if pom_artifact_id == artifact_id:
            module_path = get_module_path(pom_path, root_dir)
            matches.append({
                "artifact_id": artifact_id,
                "module_path": module_path,
                "pom_file": str(pom_path.relative_to(Path(root_dir).resolve())),
                "parent_modules": get_parent_modules(module_path),
                "maven_pl_argument": f"-pl {module_path}" if module_path != '.' else ""
            })

    return matches


def validate_module_path(module_path: str, root_dir: str) -> Dict[str, Any]:
    """Validate an explicit module path and return its info."""
    root_path = Path(root_dir).resolve()
    pom_path = root_path / module_path / "pom.xml"

    if not pom_path.exists():
        return {
            "status": "error",
            "error": "module_not_found",
            "message": f"No pom.xml found at {module_path}/pom.xml"
        }

    artifact_id = extract_artifact_id(pom_path)
    if not artifact_id:
        return {
            "status": "error",
            "error": "invalid_pom",
            "message": f"Could not extract artifactId from {module_path}/pom.xml"
        }

    return {
        "status": "success",
        "data": {
            "artifact_id": artifact_id,
            "module_path": module_path,
            "pom_file": f"{module_path}/pom.xml",
            "parent_modules": get_parent_modules(module_path),
            "maven_pl_argument": f"-pl {module_path}" if module_path != '.' else ""
        }
    }


def search_by_artifact_id(artifact_id: str, root_dir: str) -> Dict[str, Any]:
    """Search for modules by artifactId."""
    # Validate root directory
    if not os.path.isdir(root_dir):
        return {
            "status": "error",
            "error": "root_not_found",
            "message": f"Root directory not found: {root_dir}"
        }

    matches = find_modules_by_artifact_id(artifact_id, root_dir)

    if not matches:
        return {
            "status": "error",
            "error": "artifact_not_found",
            "message": f"No module found with artifactId '{artifact_id}'"
        }

    if len(matches) == 1:
        return {
            "status": "success",
            "data": matches[0]
        }

    # Multiple matches - return error with choices
    return {
        "status": "error",
        "error": "ambiguous_artifact_id",
        "message": f"Multiple modules found for artifactId '{artifact_id}'. Select one.",
        "choices": [m["module_path"] for m in matches]
    }


def main():
    """Main entry point."""
    args = parse_args()

    if args.module_path:
        # Validate explicit module path
        result = validate_module_path(args.module_path, args.root)
    else:
        # Search by artifactId
        result = search_by_artifact_id(args.artifact_id, args.root)

    print(json.dumps(result, indent=2))

    # Exit code: 0 for success, 1 for any error
    if result["status"] == "error":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
