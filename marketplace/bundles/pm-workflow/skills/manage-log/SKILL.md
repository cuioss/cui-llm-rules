---
name: manage-log
description: Manage work-log.toon files with timestamped entries
allowed-tools: Read, Glob, Bash
---

# Manage Log Skill

Manage work-log.toon files with timestamped entries. Tracks work progress across phases.

## What This Skill Provides

- Add timestamped log entries
- Read log entries with filtering
- List entries by phase or date

## When to Activate This Skill

Activate this skill when:
- Recording work progress
- Reviewing what was done in a phase
- Tracking activity history

---

## Storage Location

Work logs are stored in the plan directory:

```
.plan/plans/{plan_id}/work-log.toon
```

---

## File Format

TOON format with entries list:

```toon
# Plan: my-feature
# Updated: 2025-12-02T14:30:00Z

entries:
  - timestamp: 2025-12-02T10:00:00Z
    type: progress
    phase: init
    summary: Starting init phase
  - timestamp: 2025-12-02T10:05:00Z
    type: decision
    phase: refine
    summary: Selected plan-type-java
    detail: Task modifies .java files in service layer
  - timestamp: 2025-12-02T11:30:00Z
    type: artifact
    phase: execute
    summary: Created REQ-001: Implement JWT authentication
    detail: Covers token generation and validation
  - timestamp: 2025-12-02T14:00:00Z
    type: outcome
    phase: execute
    summary: Completed execute phase: 3 tasks done
  - timestamp: 2025-12-02T14:30:00Z
    type: error
    phase: execute
    summary: Build failed: compilation error
    detail: Missing dependency on jwt-core module
```

### Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `timestamp` | Yes | ISO timestamp (UTC) |
| `type` | Yes | Entry type: `decision`, `artifact`, `progress`, `error`, `outcome` |
| `phase` | Yes | Phase when entry was created |
| `summary` | Yes | Brief description of work done |
| `detail` | No | Additional context, reasoning, or error details |

### Entry Types

| Type | Purpose | Example Summary |
|------|---------|-----------------|
| `decision` | Log choices with reasoning | "Selected plan-type-java" |
| `artifact` | Log created items with titles | "Created REQ-001: Implement JWT auth" |
| `progress` | Log phase transitions or steps | "Starting refine phase" |
| `error` | Log failures with context | "Skill load failed: plan-type-plugin not found" |
| `outcome` | Log phase completion summaries | "Completed refine: 6 specs, 12 tasks" |

---

## Operations

Script: `pm-workflow:manage-log:manage-work-log`

### add

Add a new log entry.

```bash
python3 .plan/execute-script.py pm-workflow:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase implement \
  --summary "Implemented JWT token generation" \
  [--type decision|artifact|progress|error|outcome] \
  [--detail "Additional context or reasoning"]
```

**Parameters**:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--plan-id` | Yes | Plan identifier (kebab-case) |
| `--phase` | Yes | Current phase (init, refine, execute, finalize) |
| `--summary` | Yes | Brief description of work done |
| `--type` | No | Entry type: `decision`, `artifact`, `progress`, `error`, `outcome` (default: `progress`) |
| `--detail` | No | Additional context, reasoning, or error details |

**Output** (TOON):
```toon
status: success
plan_id: my-feature
type: artifact
phase: configure
timestamp: 2025-12-02T14:30:00Z
summary: Created REQ-001: Implement JWT authentication
detail: Covers token generation and validation for API endpoints
total_entries: 4
```

### read

Read all log entries.

```bash
python3 .plan/execute-script.py pm-workflow:manage-log:manage-work-log read \
  --plan-id {plan_id} \
  [--phase execute]
```

**Parameters**:
- `--plan-id` (required): Plan identifier
- `--phase`: Filter entries by phase

**Output** (TOON):
```toon
status: success
plan_id: my-feature
total_entries: 3
entries:
  - timestamp: 2025-12-02T10:00:00Z
    type: progress
    phase: init
    summary: Starting init phase
  - timestamp: 2025-12-02T10:30:00Z
    type: decision
    phase: refine
    summary: Selected plan-type-java
    detail: Task modifies .java files
  - timestamp: 2025-12-02T14:00:00Z
    type: artifact
    phase: execute
    summary: Created REQ-001: JWT authentication
    detail: Token generation and validation
```

### list

List entries summary (most recent entries).

```bash
python3 .plan/execute-script.py pm-workflow:manage-log:manage-work-log list \
  --plan-id {plan_id} \
  [--limit 10]
```

**Parameters**:
- `--plan-id` (required): Plan identifier
- `--limit`: Maximum number of entries to return (most recent)

**Output** (TOON):
```toon
status: success
plan_id: my-feature
total_entries: 15
showing: 10
entries:
  - timestamp: 2025-12-02T14:00:00Z
    type: progress
    phase: execute
    summary: Completed task TASK-001
  - timestamp: 2025-12-02T14:30:00Z
    type: error
    phase: execute
    summary: Build failed
    detail: Missing dependency on jwt-core module
```

---

## Scripts

**Script**: `pm-workflow:manage-log:manage-work-log`

| Command | Parameters | Description |
|---------|------------|-------------|
| `add` | `--plan-id --phase --summary [--type] [--detail]` | Add new log entry |
| `read` | `--plan-id [--phase]` | Read all entries (with optional phase filter) |
| `list` | `--plan-id [--limit]` | List most recent entries |

---

## Integration Points

### With plan-execute

Execution logs work as steps are completed.
