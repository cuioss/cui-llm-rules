#!/usr/bin/env python3
"""Discover domain and supplement bundles in the plugin cache."""

import argparse
import json
import os
import sys
from pathlib import Path


# Default plugin cache location
DEFAULT_PLUGIN_CACHE = Path.home() / ".claude" / "plugins" / "cache" / "plan-marshall"


def get_plugin_cache_path() -> Path:
    """Get the plugin cache path, allowing override via environment variable."""
    env_path = os.environ.get("PLUGIN_CACHE_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_PLUGIN_CACHE


def detect_manifest_type(manifest: dict) -> str:
    """Detect if manifest is a domain or supplement type.

    Args:
        manifest: Parsed plugin.json content

    Returns:
        'domain' if manifest has 'domain' field,
        'supplement' if manifest has 'supplements' field,
        'unknown' otherwise
    """
    if "domain" in manifest:
        return "domain"
    if "supplements" in manifest:
        return "supplement"
    return "unknown"


def extract_schema_version(schema_url: str) -> str:
    """Extract version from schema URL.

    Args:
        schema_url: URL like '.../domain-manifest-v1.json'

    Returns:
        Version string like 'v1'
    """
    if not schema_url:
        return "unknown"
    # Extract version from filename pattern: *-v{N}.json
    filename = schema_url.split("/")[-1]
    if "-v" in filename:
        version_part = filename.split("-v")[-1]
        version = "v" + version_part.replace(".json", "")
        return version
    return "unknown"


def scan_bundle_for_manifest(bundle_path: Path) -> dict | None:
    """Scan a bundle for plan-marshall-plugin manifest.

    Args:
        bundle_path: Path to bundle directory

    Returns:
        Manifest dict with metadata, or None if not found
    """
    # Look for the fixed skill name
    manifest_path = bundle_path / "skills" / "plan-marshall-plugin" / "plugin.json"
    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    manifest_type = detect_manifest_type(manifest)
    if manifest_type == "unknown":
        return None

    # bundle_path is {cache}/{bundle}/{version}/, so parent.name is the bundle name
    return {
        "bundle": bundle_path.parent.name,
        "manifest_path": str(manifest_path),
        "type": manifest_type,
        "manifest": manifest,
    }


def extract_domain_info(bundle_info: dict) -> dict:
    """Extract domain information from manifest.

    Args:
        bundle_info: Bundle info dict from scan_bundle_for_manifest

    Returns:
        Domain info dict with key, name, bundle, extensions
    """
    manifest = bundle_info["manifest"]
    domain = manifest.get("domain", {})
    extensions = manifest.get("extensions", {})

    return {
        "key": domain.get("key", ""),
        "name": domain.get("name", ""),
        "description": domain.get("description", ""),
        "bundle": bundle_info["bundle"],
        "has_outline": bool(extensions.get("outline")),
        "has_triage": bool(extensions.get("triage")),
    }


def extract_supplement_info(bundle_info: dict) -> dict:
    """Extract supplement information from manifest.

    Args:
        bundle_info: Bundle info dict from scan_bundle_for_manifest

    Returns:
        Supplement info dict with domain, bundle, description
    """
    manifest = bundle_info["manifest"]
    supplements = manifest.get("supplements", {})

    return {
        "domain": supplements.get("domain", ""),
        "bundle": bundle_info["bundle"],
        "description": supplements.get("description", ""),
    }


def cmd_discover(args):
    """Handle 'discover' subcommand."""
    plugin_cache = get_plugin_cache_path()

    if not plugin_cache.exists():
        print("status: success")
        print("domains_found: 0")
        print("supplements_found: 0")
        print()
        print("domains[0]{key,name,bundle,has_outline,has_triage}:")
        print()
        print("supplements[0]{domain,bundle,description}:")
        sys.exit(0)

    domains = []
    supplements = []

    # Scan all bundles in the cache
    for bundle_dir in plugin_cache.iterdir():
        if not bundle_dir.is_dir():
            continue

        # Handle versioned structure: {bundle}/{version}/
        for version_dir in bundle_dir.iterdir():
            if not version_dir.is_dir():
                continue

            bundle_info = scan_bundle_for_manifest(version_dir)
            if bundle_info is None:
                continue

            if bundle_info["type"] == "domain":
                domains.append(extract_domain_info(bundle_info))
            elif bundle_info["type"] == "supplement":
                supplements.append(extract_supplement_info(bundle_info))

    # Sort results
    domains.sort(key=lambda d: d["key"])
    supplements.sort(key=lambda s: (s["domain"], s["bundle"]))

    # Output in TOON format
    print("status: success")
    print(f"domains_found: {len(domains)}")
    print(f"supplements_found: {len(supplements)}")
    print()

    # Domains table
    print(f"domains[{len(domains)}]{{key,name,bundle,has_outline,has_triage}}:")
    for d in domains:
        has_outline = "true" if d["has_outline"] else "false"
        has_triage = "true" if d["has_triage"] else "false"
        print(f"{d['key']}\t{d['name']}\t{d['bundle']}\t{has_outline}\t{has_triage}")
    print()

    # Supplements table
    print(f"supplements[{len(supplements)}]{{domain,bundle,description}}:")
    for s in supplements:
        print(f"{s['domain']}\t{s['bundle']}\t{s['description']}")

    sys.exit(0)


def cmd_list_bundles(args):
    """Handle 'list-bundles' subcommand - list all bundles with plan-marshall-plugin."""
    plugin_cache = get_plugin_cache_path()

    if not plugin_cache.exists():
        print("status: success")
        print("bundles_found: 0")
        print()
        print("bundles[0]{name,type,path}:")
        sys.exit(0)

    bundles = []

    for bundle_dir in plugin_cache.iterdir():
        if not bundle_dir.is_dir():
            continue

        for version_dir in bundle_dir.iterdir():
            if not version_dir.is_dir():
                continue

            bundle_info = scan_bundle_for_manifest(version_dir)
            if bundle_info is not None:
                bundles.append({
                    "name": bundle_info["bundle"],
                    "type": bundle_info["type"],
                    "path": bundle_info["manifest_path"],
                })

    bundles.sort(key=lambda b: b["name"])

    print("status: success")
    print(f"bundles_found: {len(bundles)}")
    print()

    print(f"bundles[{len(bundles)}]{{name,type,path}}:")
    for b in bundles:
        print(f"{b['name']}\t{b['type']}\t{b['path']}")

    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Discover domain and supplement bundles in the plugin cache"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # discover subcommand
    discover_parser = subparsers.add_parser(
        "discover",
        help="Discover all domains and supplements"
    )
    discover_parser.set_defaults(func=cmd_discover)

    # list-bundles subcommand
    list_parser = subparsers.add_parser(
        "list-bundles",
        help="List all bundles with plan-marshall-plugin skill"
    )
    list_parser.set_defaults(func=cmd_list_bundles)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
