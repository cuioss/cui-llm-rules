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
| `pm-java` | java-task-plan, java-solution-outline (skills + agents) |
| `pm-frontend` | js-task-plan, js-solution-outline (skills + agents) |
| `pm-plugin-development` | plugin-task-plan, plugin-solution-outline (skills + agents) |

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

**Script**: `pm-workflow:planning-inventory`

```bash
python3 .plan/execute-script.py pm-workflow:planning-inventory:scan-planning-inventory scan
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
python3 .plan/execute-script.py pm-workflow:planning-inventory:scan-planning-inventory scan --format full
python3 .plan/execute-script.py pm-workflow:planning-inventory:scan-planning-inventory scan --format summary
```

### --include-descriptions (optional flag)

When specified, includes description fields from YAML frontmatter.

```bash
python3 .plan/execute-script.py pm-workflow:planning-inventory:scan-planning-inventory scan --include-descriptions
```

## Output Format

### Full Format

```json
{
  "patterns": ["plan-*", "manage-*", "*-workflow", "*-plan", "*-goals", "*-plan-*", "*-goals-*"],
  "bundles_scanned": ["planning", "pm-java", "pm-frontend", "pm-plugin-development"],
  "core": {
    "bundle": "planning",
    "agents": [...],
    "commands": [...],
    "skills": [...],
    "scripts": [...]
  },
  "derived": [
    {
      "bundle": "pm-java",
      "agents": [{"name": "java-task-plan-agent", ...}, {"name": "java-solution-outline-agent", ...}],
      "skills": [{"name": "java-task-plan", ...}, {"name": "java-solution-outline", ...}],
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
    {"type": "skills", "names": ["plan-init", "plan-refine", "plan-execute", ...]},
    {"type": "agents", "names": ["plan-init-agent", "plan-refine-agent", ...]},
    {"type": "commands", "names": ["task-implement", ...]}
  ],
  "derived_bundles": [
    {"bundle": "pm-java", "agents": ["java-task-plan-agent", ...], "skills": ["java-task-plan", ...]},
    ...
  ],
  "statistics": {...}
}
```

## Component Categories

### Core Components (planning bundle)

| Pattern | Examples |
|---------|----------|
| `plan-*` | plan-init, plan-refine, plan-execute, plan-finalize |
| `manage-*` | manage-tasks, manage-plan-documents, manage-config, manage-lifecycle |
| `*-workflow` | pr-workflow, git-workflow, sonar-workflow |
| `task-*` | task-implement |
| `pr-*` | pr-doctor |
| `plan-type-*` | plan-type-java, plan-type-javascript, plan-type-plugin |

### Derived Components (domain bundles)

| Bundle | Agents | Skills |
|--------|--------|--------|
| pm-java | java-task-plan-agent, java-solution-outline-agent | java-task-plan, java-solution-outline |
| pm-frontend | js-task-plan-agent, js-solution-outline-agent | js-task-plan, js-solution-outline |
| pm-plugin-development | plugin-task-plan-agent, plugin-solution-outline-agent | plugin-task-plan, plugin-solution-outline |

## Dependencies

This skill uses `pm-core:marketplace-inventory` internally with:

- `--bundles`: Filtered to planning-related bundles
- `--name-pattern`: Filtered to planning-related patterns

## Non-Prompting Requirements

This skill is designed to run without user prompts. Required permissions:

**Script Execution:**
- `Bash(bash:*)` - Bash interpreter
- Script permissions synced via `/tools-setup-project-permissions`

**Script only reads marketplace directory structure (no writes).**
