---
name: script-executor
description: Universal script execution pattern via execute-script.py proxy
allowed-tools: Read, Bash
---

# Script Executor Skill

## Overview

All marketplace scripts are executed through `.plan/execute-script.py`:

```bash
python3 .plan/execute-script.py {notation} {subcommand} {args...}
```

## Notation Format

Simplified notation: `{bundle}:{skill}`

| Example |
|---------|
| `pm-workflow:manage-files` |
| `pm-dev-builder:builder-maven-rules` |

## Examples

```bash
# Document operations (typed documents)
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-documents request create --plan-id my-plan --title "My Task" --source description --body "Task details"
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-documents request read --plan-id my-plan

# File operations (generic files)
python3 .plan/execute-script.py pm-workflow:manage-files:manage-files write --plan-id my-plan --file notes.md --content "..."

# Build operations
python3 .plan/execute-script.py pm-dev-builder:builder-maven-rules:maven execute --goals clean,verify

# Config operations
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set --plan-id my-plan --key foo --value bar
```

## Error Handling

The executor standardizes error output:

```
SCRIPT_ERROR    {notation}    {exit_code}    {summary}
```

## Execution Logging

The executor provides two-tier logging:

### Plan-Scoped Logging

When a plan ID is provided, logs to:
```
.plan/plans/{plan-id}/script-execution.log
```

**Two ways to enable plan-scoped logging:**

| Parameter | Use Case | Behavior |
|-----------|----------|----------|
| `--plan-id` | Scripts that accept it (manage-* scripts) | Script uses value + logging picks it up |
| `--trace-plan-id` | Scripts without `--plan-id` (scan-*, analyze-*) | Stripped before passing to script, logging only |

**Example with --plan-id** (script uses it):
```bash
python3 .plan/execute-script.py pm-workflow:manage-files:manage-files add \
  --plan-id my-plan --file task.md
```

**Example with --trace-plan-id** (logging only, stripped):
```bash
python3 .plan/execute-script.py plan-marshall:marketplace-inventory:scan-marketplace-inventory \
  --trace-plan-id my-plan --include-descriptions
```

The `--trace-plan-id` parameter is removed before the script executes, so the script never sees it. This enables plan-scoped logging for scripts that don't have their own `--plan-id` parameter.

**Benefits**:
- Tied to plan lifecycle (deleted when plan archived/deleted)
- Enables per-plan audit trail

### Global Logging

Fallback when no plan context:
```
.plan/logs/script-execution-YYYY-MM-DD.log
```

**Benefits**:
- Session-based daily logs
- Automatically cleaned by `/plan-marshall-hq` (7 days retention)

### Log Entry Formats

**Success entries** (single-line):
```
[2025-12-08T10:30:00Z] [INFO] [SCRIPT] pm-workflow:manage-files:manage-files add (0.15s)
```

**Error entries** (multi-line with fields):
```
[2025-12-08T10:31:00Z] [ERROR] [SCRIPT] pm-workflow:manage-files:manage-files add (0.23s)
  exit_code: 1
  args: --plan-id my-plan --file missing.md
  stderr: FileNotFoundError: missing.md not found
```

See `plan-marshall:logging` skill for full log format specification.

## Setup

Run `/plan-marshall-hq` to generate the executor after bundle changes.

## Architecture

```
.plan/
├── execute-script.py      # Generated executor with embedded mappings
├── marshall-state.toon    # Plugin root path + metadata
└── logs/                  # Global execution logs (no plan context)
    └── script-execution-YYYY-MM-DD.log

~/.claude/plugins/cache/plan-marshall/
└── {bundle}/              # Installed plugin bundles
    └── {version}/         # Versioned bundle contents
        └── skills/...     # Skills with scripts
```

## Bootstrap Pattern (Before Executor Exists)

When `.plan/execute-script.py` doesn't exist yet (first run), use the bootstrap pattern:

### Step 1: Get Plugin Root

Check `.plan/marshall-state.toon` for cached `plugin_root`, or detect it:

```bash
python3 ~/.claude/plugins/cache/*/plan-marshall/*/skills/plan-marshall/scripts/bootstrap-plugin.py get-root
```

Output:
```
plugin_root	/Users/.../.claude/plugins/cache/plan-marshall
source	detected|cached
```

### Step 2: Execute Scripts Directly

Use the plugin root with glob pattern for version:

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/*/skills/{skill}/scripts/{script}.py {args}
```

### State File Format

`.plan/marshall-state.toon`:
```
plugin_root	/Users/oliver/.claude/plugins/cache/plan-marshall
detected_at	2025-12-12T10:30:00+00:00
```

This pattern enables:
- Plugin scripts to work in any project (not just the marketplace repo)
- Caching for fast subsequent lookups
- Version-agnostic paths via glob

## Integration with Verification

The verification skill recognizes this execution pattern:

**Allowed**:
- `python3 .plan/execute-script.py {notation} ...`

**Violation**:
- `python3 {direct_script_path} ...` (after migration complete)
