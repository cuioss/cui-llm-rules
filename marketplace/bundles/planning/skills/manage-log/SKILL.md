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

TOON format with entries table:

```toon
# Plan: my-feature
# Created: 2025-12-02T10:00:00Z

entries[5]{timestamp,type,phase,summary,detail}:
2025-12-02T10:00:00Z,progress,init,Starting init phase,
2025-12-02T10:05:00Z,decision,configure,Selected plan-type-java,Task modifies .java files in service layer
2025-12-02T11:30:00Z,artifact,configure,Created REQ-001: Implement JWT authentication,Covers token generation and validation
2025-12-02T14:00:00Z,outcome,implement,Completed implement phase: 3 tasks done,
2025-12-02T14:30:00Z,error,implement,Build failed: compilation error,Missing dependency on jwt-core module
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

Script: `planning:manage-log:manage-work-log`

### add

Add a new log entry.

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase implement \
  --summary "Implemented JWT token generation" \
  [--type decision|artifact|progress|error|outcome] \
  [--detail "Additional context or reasoning"]
```

**Parameters**:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--plan-id` | Yes | Plan identifier |
| `--phase` | Yes | Current phase (init, configure, refine, execute, finalize) |
| `--summary` | Yes | Brief description of work done |
| `--type` | No | Entry type (default: `progress`) |
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
python3 .plan/execute-script.py planning:manage-log:manage-work-log read \
  --plan-id {plan_id} \
  [--phase implement]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
total_entries: 3

entries[3]{timestamp,type,phase,summary,detail}:
2025-12-02T10:00:00Z,progress,init,Starting init phase,
2025-12-02T10:30:00Z,decision,configure,Selected plan-type-java,Task modifies .java files
2025-12-02T14:00:00Z,artifact,configure,Created REQ-001: JWT authentication,Token generation and validation
```

### list

List entries summary.

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log list \
  --plan-id {plan_id} \
  [--limit 10]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
total_entries: 15
showing: 10

entries[10]{timestamp,type,phase,summary,detail}:
...
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-log:manage-work-log` | All log operations via subcommands | `python3 .plan/execute-script.py planning:manage-log:manage-work-log {subcommand} --help` |

---

## Integration Points

### With plan-execute

Execution logs work as steps are completed.
