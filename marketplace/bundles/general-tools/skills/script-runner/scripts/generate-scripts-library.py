#!/usr/bin/env python3
"""
generate-scripts-library.py

Generates .plan/scripts-library.toon from marketplace inventory.
This script ensures ALL scripts are captured deterministically in TOON format.

Usage:
    python3 generate-scripts-library.py [--output PATH] [--marketplace-root PATH]

Options:
    --output PATH           Output path (default: .plan/scripts-library.toon)
    --marketplace-root PATH Path to marketplace root (default: current directory)
    --dry-run               Print output instead of writing file

Exit codes:
    0 - Success
    1 - Error during execution

Output format (TOON):
    version: 2
    generated: 2025-12-07T10:30:00Z
    marketplace: cui-development-standards
    script_count: 79

    scripts[79]{notation,absolute,type}:
    bundle:skill/scripts/name.py,/absolute/path/name.py,python
    ...
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def discover_marketplace_scripts(marketplace_root: Path) -> tuple[list[dict], str]:
    """
    Run scan-marketplace-inventory.py and return all discovered scripts.

    Returns:
        (scripts_list, marketplace_name)
    """
    script_path = (
        marketplace_root /
        "marketplace/bundles/cui-plugin-development-tools/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py"
    )

    if not script_path.exists():
        raise FileNotFoundError(f"Inventory script not found: {script_path}")

    result = subprocess.run(
        ["python3", str(script_path), "--resource-types", "scripts"],
        cwd=str(marketplace_root),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Inventory script failed: {result.stderr}")

    inventory = json.loads(result.stdout)

    # Detect marketplace name from plugin paths
    marketplace_name = "unknown"
    base_path = inventory.get("base_path", "")
    if "marketplace/bundles" in base_path:
        # Try to find marketplace name from mcp.json or .claude-plugin
        mcp_path = marketplace_root / ".claude" / "mcp.json"
        if mcp_path.exists():
            with open(mcp_path) as f:
                mcp = json.load(f)
                for key in mcp.get("mcpServers", {}):
                    if "@" in key:
                        marketplace_name = key.split("@")[-1]
                        break

    # Collect all scripts from all bundles
    all_scripts = []
    for bundle in inventory.get("bundles", []):
        bundle_name = bundle["name"]
        for script in bundle.get("scripts", []):
            all_scripts.append({
                "bundle": bundle_name,
                "skill": script["skill"],
                "name": script["name"],
                "type": script["type"],
                "absolute_path": script["path_formats"]["absolute"]
            })

    return all_scripts, marketplace_name


def build_notation(bundle: str, skill: str, script_name: str, script_type: str) -> str:
    """Build the portable notation for a script."""
    ext = ".py" if script_type == "python" else ".sh"
    return f"{bundle}:{skill}/scripts/{script_name}{ext}"


def generate_scripts_library_toon(scripts: list[dict], marketplace_name: str) -> str:
    """Generate the scripts-library.toon content."""
    lines = []

    # Header
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    lines.append(f"version: 2")
    lines.append(f"generated: {timestamp}")
    lines.append(f"marketplace: {marketplace_name}")
    lines.append(f"script_count: {len(scripts)}")
    lines.append("")

    # Build sorted list of (notation, absolute, type)
    script_entries = []
    for script in scripts:
        notation = build_notation(
            script["bundle"],
            script["skill"],
            script["name"],
            script["type"]
        )
        script_entries.append((notation, script["absolute_path"], script["type"]))

    # Sort by notation for consistent output
    script_entries.sort(key=lambda x: x[0])

    # Scripts table
    lines.append(f"scripts[{len(script_entries)}]{{notation,absolute,type}}:")
    for notation, absolute, script_type in script_entries:
        lines.append(f"{notation},{absolute},{script_type}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate scripts-library.toon from marketplace inventory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".plan/scripts-library.toon"),
        help="Output path for scripts-library.toon"
    )
    parser.add_argument(
        "--marketplace-root",
        type=Path,
        default=Path.cwd(),
        help="Path to marketplace root directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output instead of writing file"
    )

    args = parser.parse_args()

    # Resolve paths
    if not args.output.is_absolute():
        args.output = args.marketplace_root / args.output

    try:
        # Discover all scripts
        scripts, marketplace_name = discover_marketplace_scripts(args.marketplace_root)

        # Generate TOON content
        toon_content = generate_scripts_library_toon(scripts, marketplace_name)

        if args.dry_run:
            print(toon_content)
            print(f"\n# Would write to: {args.output}", file=sys.stderr)
            print(f"# Scripts discovered: {len(scripts)}", file=sys.stderr)
        else:
            # Ensure directory exists
            args.output.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(args.output, "w") as f:
                f.write(toon_content)
                f.write("\n")

            # Output success in TOON format
            print(f"status: success")
            print(f"scripts_discovered: {len(scripts)}")
            print(f"output_file: {args.output}")
            print(f"marketplace: {marketplace_name}")

        return 0

    except Exception as e:
        # Output error in TOON format
        print(f"status: error", file=sys.stderr)
        print(f"message: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
