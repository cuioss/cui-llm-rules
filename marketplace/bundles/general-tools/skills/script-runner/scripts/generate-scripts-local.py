#!/usr/bin/env python3
"""
generate-scripts-local.py

Generates .claude/scripts.local.json from marketplace inventory.
This script ensures ALL scripts are captured deterministically.

Usage:
    python3 generate-scripts-local.py [--output PATH] [--marketplace-root PATH]

Options:
    --output PATH           Output path (default: .claude/scripts.local.json)
    --marketplace-root PATH Path to marketplace root (default: current directory)
    --dry-run               Print output instead of writing file

Exit codes:
    0 - Success
    1 - Error during execution
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


def generate_scripts_local(scripts: list[dict], marketplace_name: str) -> dict:
    """Generate the scripts.local.json structure."""
    # Build scripts mapping
    scripts_mapping = {}
    for script in scripts:
        notation = build_notation(
            script["bundle"],
            script["skill"],
            script["name"],
            script["type"]
        )
        scripts_mapping[notation] = {
            "absolute": script["absolute_path"],
            "type": script["type"]
        }

    # Build permissions - one per skill directory
    # Group scripts by skill to generate one permission per skill
    skill_paths = {}  # skill_path -> {has_bash, has_python}
    for script in scripts:
        skill_dir = str(Path(script["absolute_path"]).parent)
        if skill_dir not in skill_paths:
            skill_paths[skill_dir] = {"has_bash": False, "has_python": False}

        if script["type"] == "bash":
            skill_paths[skill_dir]["has_bash"] = True
        elif script["type"] == "python":
            skill_paths[skill_dir]["has_python"] = True

    permissions = []
    for skill_dir, types in sorted(skill_paths.items()):
        if types["has_bash"]:
            permissions.append(f"Bash(bash {skill_dir}:*)")
        if types["has_python"]:
            permissions.append(f"Bash(python3 {skill_dir}:*)")

    return {
        "version": 1,
        "discovered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "marketplace": marketplace_name,
        "scripts": scripts_mapping,
        "permissions": sorted(permissions)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate scripts.local.json from marketplace inventory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".claude/scripts.local.json"),
        help="Output path for scripts.local.json"
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

        # Generate the output structure
        output = generate_scripts_local(scripts, marketplace_name)

        # Output
        json_output = json.dumps(output, indent=2)

        if args.dry_run:
            print(json_output)
            print(f"\n# Would write to: {args.output}", file=sys.stderr)
            print(f"# Scripts discovered: {len(scripts)}", file=sys.stderr)
            print(f"# Permissions generated: {len(output['permissions'])}", file=sys.stderr)
        else:
            # Ensure directory exists
            args.output.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(args.output, "w") as f:
                f.write(json_output)
                f.write("\n")

            print(json.dumps({
                "success": True,
                "file": str(args.output),
                "scripts_discovered": len(scripts),
                "permissions_generated": len(output["permissions"]),
                "marketplace": marketplace_name
            }, indent=2))

        return 0

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
