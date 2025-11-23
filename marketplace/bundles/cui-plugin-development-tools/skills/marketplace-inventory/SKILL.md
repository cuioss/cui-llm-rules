---
name: marketplace-inventory
description: Scans and reports complete marketplace inventory (bundles, agents, commands, skills, scripts)
allowed-tools:
  - Read
  - Bash
  - Glob
---

# Marketplace Inventory Skill

Provides complete marketplace inventory scanning capabilities using the scan-marketplace-inventory.sh script.

## Purpose

This skill scans the marketplace directory structure and returns a comprehensive JSON inventory of all bundles and their resources (agents, commands, skills, scripts).

## When to Use This Skill

Activate this skill when you need to:
- Get a complete inventory of marketplace bundles
- Discover all available agents, commands, and skills
- Validate marketplace structure
- Generate reports on marketplace contents

## Workflow

When activated, this skill scans the marketplace and returns structured JSON inventory.

### Step 1: Execute Inventory Scan

Run the marketplace inventory scanner script:

```bash
bash scripts/scan-marketplace-inventory.sh --scope marketplace
```

The script will:
- Discover all bundles in marketplace/bundles/
- Enumerate agents, commands, and skills in each bundle
- Identify bundled scripts
- Return complete JSON structure

### Step 2: Parse and Return Results

The script outputs JSON in this format:

```json
{
  "scope": "marketplace",
  "base_path": "/path/to/marketplace/bundles",
  "bundles": [
    {
      "name": "bundle-name",
      "path": "marketplace/bundles/bundle-name",
      "agents": [...],
      "commands": [...],
      "skills": [...],
      "scripts": [...],
      "statistics": {...}
    }
  ],
  "statistics": {
    "total_bundles": 8,
    "total_agents": 28,
    "total_commands": 46,
    "total_skills": 30,
    "total_scripts": 7,
    "total_resources": 111
  }
}
```

Return this JSON output to the invoking command for further processing.

## Script Parameters

**--scope marketplace** (required)
- Scans the marketplace/bundles directory
- Returns complete marketplace inventory

## Error Handling

If the script fails:
- Check that the working directory is the repository root
- Verify marketplace/bundles/ directory exists
- Ensure script has execute permissions

## Non-Prompting Requirements

This skill is designed to run without user prompts. Required permissions:

**Script Execution:**
- `Bash(bash:*)` - Bash interpreter
- `Bash(scripts/scan-marketplace-inventory.sh:*)` - Inventory scanner

**Ensuring Non-Prompting:**
- Script invocation uses `scripts/` which resolves to skill's mounted path
- Script only reads marketplace directory structure (no writes)
- All output is JSON to stdout

## References

- Script location: scripts/scan-marketplace-inventory.sh
- Marketplace root: marketplace/bundles/
