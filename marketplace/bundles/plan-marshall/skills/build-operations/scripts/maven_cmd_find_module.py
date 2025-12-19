#!/usr/bin/env python3
"""Find-module subcommand for Maven module discovery."""

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional


def find_pom_files(root_dir: str) -> List[Path]:
    """Find all pom.xml files in the project."""
    pom_files = []
    for pom in Path(root_dir).rglob("pom.xml"):
        if not any(p.startswith('.') or p == 'target' for p in pom.parts):
            pom_files.append(pom)
    return sorted(pom_files)


def extract_artifact_id(pom_path: Path) -> Optional[str]:
    """Extract artifactId from a pom.xml file.

    Handles both namespaced and non-namespaced POM files.
    - Namespaced: <project xmlns="http://maven.apache.org/POM/4.0.0">
    - Non-namespaced: <project>
    """
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # Check for Maven namespace in root element
        # ElementTree represents default namespace as {namespace}tagname
        maven_ns = 'http://maven.apache.org/POM/4.0.0'
        if root.tag == f'{{{maven_ns}}}project':
            # Namespaced POM - use {namespace}elementname syntax
            elem = root.find(f'{{{maven_ns}}}artifactId')
        else:
            # Non-namespaced POM - direct element lookup
            elem = root.find('artifactId')

        if elem is not None and elem.text:
            return elem.text.strip()
        return None
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
