---
name: planning-inventory
description: Scans and reports all planning-related components across marketplace bundles
allowed-tools:
  - Read
  - Bash
---

# Planning Inventory Skill

Provides a unified view of all planning-related components across the marketplace, including core planning infrastructure and derived components in domain bundles.

## Purpose

Planning-related components are distributed across multiple bundles:

| Bundle | Component Types |
|--------|-----------------|
| `planning` | Core infrastructure (plan-*, manage-*, *-workflow) |
| `cui-java-expert` | java-plan, java-specify (skills + agents) |
| `cui-frontend-expert` | js-plan, js-specify (skills + agents) |
| `cui-plugin-development-tools` | plugin-plan, plugin-specify (skills + agents) |

This skill provides a single command to discover all these components.

## When to Use This Skill

Activate this skill when you need to:

- Get a complete inventory of planning-related components
- Understand the planning component ecosystem
- Validate planning system integrity
- Generate reports on planning capabilities

## Workflow

### Step 1: Execute Planning Inventory Scan

Run the planning inventory scanner script:

**Script**: `planning:planning-inventory/scripts/scan-planning-inventory.py`

```bash
python3 {script_path}
```

**Direct execution from marketplace checkout:**
```bash
python3 marketplace/bundles/planning/skills/planning-inventory/scripts/scan-planning-inventory.py
```

### Step 2: Parse and Return Results

The script outputs JSON organized into core and derived categories.

## Script Parameters

### --format (optional)

Output format. Default: `full`

| Value | Description |
|-------|-------------|
| `full` | Complete inventory with paths and all details |
| `summary` | Compact summary with component names only |

**Examples**:
```bash
python3 {script_path} --format full
python3 {script_path} --format summary
```

### --include-descriptions (optional flag)

When specified, includes description fields from YAML frontmatter.

```bash
python3 {script_path} --include-descriptions
```

## Output Format

### Full Format

```json
{
  "patterns": ["plan-*", "manage-*", "*-workflow", "*-plan", "*-specify", "*-plan-*", "*-specify-*"],
  "bundles_scanned": ["planning", "cui-java-expert", "cui-frontend-expert", "cui-plugin-development-tools"],
  "core": {
    "bundle": "planning",
    "agents": [...],
    "commands": [...],
    "skills": [...],
    "scripts": [...]
  },
  "derived": [
    {
      "bundle": "cui-java-expert",
      "agents": [{"name": "java-plan-agent", ...}, {"name": "java-specify-agent", ...}],
      "skills": [{"name": "java-plan", ...}, {"name": "java-specify", ...}],
      ...
    },
    ...
  ],
  "statistics": {
    "core": {"agents": 3, "commands": 4, "skills": 22, "scripts": 12, "total": 41},
    "derived": {"bundles": 3, "agents": 6, "skills": 6, "total": 12},
    "total_components": 53
  }
}
```

### Summary Format

```json
{
  "core_bundle": "planning",
  "core_components": [
    {"type": "skills", "names": ["plan-init", "plan-configure", ...]},
    {"type": "agents", "names": ["plan-init-agent", ...]},
    {"type": "commands", "names": ["task-implement", ...]}
  ],
  "derived_bundles": [
    {"bundle": "cui-java-expert", "agents": ["java-plan-agent", ...], "skills": ["java-plan", ...]},
    ...
  ],
  "statistics": {...}
}
```

## Component Categories

### Core Components (planning bundle)

| Pattern | Examples |
|---------|----------|
| `plan-*` | plan-init, plan-configure, plan-refine, plan-execute, plan-finalize |
| `manage-*` | manage-tasks, manage-specifications, manage-requirements, manage-config |
| `*-workflow` | pr-workflow, git-workflow, sonar-workflow |
| `task-*` | task-implement |
| `pr-*` | pr-doctor |
| `plan-type-*` | plan-type-java, plan-type-javascript, plan-type-plugin |

### Derived Components (domain bundles)

| Bundle | Agents | Skills |
|--------|--------|--------|
| cui-java-expert | java-plan-agent, java-specify-agent | java-plan, java-specify |
| cui-frontend-expert | js-plan-agent, js-specify-agent | js-plan, js-specify |
| cui-plugin-development-tools | plugin-plan-agent, plugin-specify-agent | plugin-plan, plugin-specify |

## Dependencies

This skill uses `cui-plugin-development-tools:marketplace-inventory` internally with:

- `--bundles`: Filtered to planning-related bundles
- `--name-pattern`: Filtered to planning-related patterns

## Non-Prompting Requirements

This skill is designed to run without user prompts. Required permissions:

**Script Execution:**
- `Bash(bash:*)` - Bash interpreter
- Script permissions synced via `/tools-setup-project-permissions`

**Script only reads marketplace directory structure (no writes).**
