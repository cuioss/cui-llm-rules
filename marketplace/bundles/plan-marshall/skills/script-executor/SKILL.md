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
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-document request create --plan-id my-plan --title "My Task" --source description --body "Task details"
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-document request read --plan-id my-plan

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

When `--plan-id` is provided, logs to:
```
.plan/plans/{plan-id}/script-execution.log
```

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
- Automatically cleaned by `/plan-marshall` (7 days retention)

### Log Entry Formats

**Success entries** (single-line):
```
[2025-12-08T10:30:00Z] [SUCCESS] [SCRIPT] pm-workflow:manage-files:manage-files add (0.15s)
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

Run `/plan-marshall` to generate the executor after bundle changes.

## Architecture

```
.plan/
├── execute-script.py      # Generated executor with embedded mappings
├── marshall-state.toon    # Metadata: last run, script count, hash
└── logs/                  # Global execution logs (no plan context)
    └── script-execution-YYYY-MM-DD.log

marketplace/bundles/plan-marshall/skills/logging/scripts/
└── plan_logging.py        # Unified logging module (see logging skill)
```

## Integration with Verification

The verification skill recognizes this execution pattern:

**Allowed**:
- `python3 .plan/execute-script.py {notation} ...`

**Violation**:
- `python3 {direct_script_path} ...` (after migration complete)
