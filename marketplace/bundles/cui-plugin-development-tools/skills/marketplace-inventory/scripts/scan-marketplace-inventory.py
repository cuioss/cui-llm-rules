#!/usr/bin/env python3
"""
scan-marketplace-inventory.py

Scans marketplace directories and returns structured inventory of bundles,
agents, commands, skills, and scripts.

Usage:
    python3 scan-marketplace-inventory.py [options]

Options:
    --scope <value>          Directory scope: marketplace, global, project (default: marketplace)
    --resource-types <types> Resource types: agents, commands, skills, scripts, or comma-separated (default: all)
    --include-descriptions   Extract descriptions from YAML frontmatter

Exit codes:
    0 - Success (JSON output)
    1 - Error (invalid parameters, missing directory)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


def find_bundles(base_path: Path) -> list[Path]:
    """Find all bundle directories by locating plugin.json files."""
    bundles = []
    for plugin_json in base_path.rglob(".claude-plugin/plugin.json"):
        # Bundle is two levels up from plugin.json
        bundle_dir = plugin_json.parent.parent
        if bundle_dir not in bundles:
            bundles.append(bundle_dir)
    return sorted(bundles)


def extract_description(file_path: Path) -> Optional[str]:
    """Extract description from YAML frontmatter."""
    if not file_path.exists():
        return None

    try:
        content = file_path.read_text()
    except (OSError, UnicodeDecodeError):
        return None

    # Check for YAML frontmatter
    if not content.startswith("---"):
        return None

    # Extract frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)

    # Extract description field
    for line in frontmatter.split('\n'):
        if line.startswith('description:'):
            desc = line[len('description:'):].strip()
            return desc if desc else None

    return None


def discover_agents(bundle_dir: Path, include_descriptions: bool) -> list[dict]:
    """Discover agent .md files in bundle/agents/."""
    agents_dir = bundle_dir / "agents"
    if not agents_dir.is_dir():
        return []

    agents = []
    for agent_file in sorted(agents_dir.glob("*.md")):
        if agent_file.is_file():
            agent = {
                "name": agent_file.stem,
                "path": str(agent_file.relative_to(Path.cwd()))
            }
            if include_descriptions:
                agent["description"] = extract_description(agent_file)
            agents.append(agent)
    return agents


def discover_commands(bundle_dir: Path, include_descriptions: bool) -> list[dict]:
    """Discover command .md files in bundle/commands/."""
    commands_dir = bundle_dir / "commands"
    if not commands_dir.is_dir():
        return []

    commands = []
    for command_file in sorted(commands_dir.glob("*.md")):
        if command_file.is_file():
            command = {
                "name": command_file.stem,
                "path": str(command_file.relative_to(Path.cwd()))
            }
            if include_descriptions:
                command["description"] = extract_description(command_file)
            commands.append(command)
    return commands


def discover_skills(bundle_dir: Path, include_descriptions: bool) -> list[dict]:
    """Discover skill directories containing SKILL.md."""
    skills_dir = bundle_dir / "skills"
    if not skills_dir.is_dir():
        return []

    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        skill_dir = skill_md.parent
        skill = {
            "name": skill_dir.name,
            "path": str(skill_dir.relative_to(Path.cwd()))
        }
        if include_descriptions:
            skill["description"] = extract_description(skill_md)
        skills.append(skill)
    return skills


def discover_scripts(bundle_dir: Path) -> list[dict]:
    """Discover script files (.sh, .py) in skill/scripts/ directories."""
    skills_dir = bundle_dir / "skills"
    if not skills_dir.is_dir():
        return []

    scripts = []
    # Find all .sh and .py files in scripts/ subdirectories
    for script_file in sorted(skills_dir.rglob("scripts/*.sh")) + sorted(skills_dir.rglob("scripts/*.py")):
        if script_file.is_file():
            skill_dir = script_file.parent.parent
            skill_name = skill_dir.name

            # Determine script type
            script_type = "python" if script_file.suffix == ".py" else "bash"

            # Generate path formats
            relative_path = str(script_file.relative_to(Path.cwd()))
            runtime_mount = f"./.claude/skills/{skill_name}/scripts/{script_file.name}"

            scripts.append({
                "name": script_file.stem,
                "skill": skill_name,
                "type": script_type,
                "path_formats": {
                    "runtime": runtime_mount,
                    "relative": relative_path,
                    "absolute": str(script_file.resolve())
                }
            })

    return scripts


def get_base_path(scope: str) -> Path:
    """Determine base path based on scope."""
    if scope == "marketplace":
        # Try current directory first, then parent
        if (Path.cwd() / "marketplace/bundles").is_dir():
            return Path.cwd() / "marketplace/bundles"
        elif (Path.cwd().parent / "marketplace/bundles").is_dir():
            return Path.cwd().parent / "marketplace/bundles"
        else:
            raise FileNotFoundError("marketplace/bundles directory not found")
    elif scope == "global":
        return Path.home() / ".claude"
    elif scope == "project":
        return Path.cwd() / ".claude"
    else:
        raise ValueError(f"Invalid scope: {scope}")


def main():
    parser = argparse.ArgumentParser(
        description="Scan marketplace directories and return structured inventory"
    )
    parser.add_argument(
        "--scope",
        choices=["marketplace", "global", "project"],
        default="marketplace",
        help="Directory scope to scan"
    )
    parser.add_argument(
        "--resource-types",
        default="all",
        help="Resource types: agents, commands, skills, scripts, or comma-separated"
    )
    parser.add_argument(
        "--include-descriptions",
        action="store_true",
        help="Extract descriptions from YAML frontmatter"
    )

    args = parser.parse_args()

    # Parse resource types
    include_agents = False
    include_commands = False
    include_skills = False
    include_scripts = False

    if args.resource_types == "all":
        include_agents = include_commands = include_skills = include_scripts = True
    else:
        for rtype in args.resource_types.split(","):
            rtype = rtype.strip()
            if rtype == "agents":
                include_agents = True
            elif rtype == "commands":
                include_commands = True
            elif rtype == "skills":
                include_skills = True
            elif rtype == "scripts":
                include_scripts = True
            else:
                print(f"ERROR: Invalid resource type: {rtype}", file=sys.stderr)
                print("Valid values: agents, commands, skills, scripts", file=sys.stderr)
                return 1

    # Get base path
    try:
        base_path = get_base_path(args.scope)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not base_path.is_dir():
        print(f"ERROR: Base path not found: {base_path}", file=sys.stderr)
        return 1

    # Find bundles
    bundle_dirs = find_bundles(base_path)

    # Build inventory
    bundles_data = []
    total_agents = total_commands = total_skills = total_scripts = 0

    for bundle_dir in bundle_dirs:
        bundle_name = bundle_dir.name

        bundle = {
            "name": bundle_name,
            "path": str(bundle_dir.relative_to(Path.cwd()))
        }

        # Discover resources
        agents = discover_agents(bundle_dir, args.include_descriptions) if include_agents else []
        commands = discover_commands(bundle_dir, args.include_descriptions) if include_commands else []
        skills = discover_skills(bundle_dir, args.include_descriptions) if include_skills else []
        scripts = discover_scripts(bundle_dir) if include_scripts else []

        bundle["agents"] = agents
        bundle["commands"] = commands
        bundle["skills"] = skills
        bundle["scripts"] = scripts

        # Bundle statistics
        bundle["statistics"] = {
            "agents": len(agents),
            "commands": len(commands),
            "skills": len(skills),
            "scripts": len(scripts),
            "total_resources": len(agents) + len(commands) + len(skills) + len(scripts)
        }

        bundles_data.append(bundle)

        # Update totals
        total_agents += len(agents)
        total_commands += len(commands)
        total_skills += len(skills)
        total_scripts += len(scripts)

    # Output
    output = {
        "scope": args.scope,
        "base_path": str(base_path),
        "bundles": bundles_data,
        "statistics": {
            "total_bundles": len(bundles_data),
            "total_agents": total_agents,
            "total_commands": total_commands,
            "total_skills": total_skills,
            "total_scripts": total_scripts,
            "total_resources": total_agents + total_commands + total_skills + total_scripts
        }
    }

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
