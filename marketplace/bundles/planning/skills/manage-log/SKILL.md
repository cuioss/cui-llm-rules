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

entries[3]{timestamp,phase,summary}:
2025-12-02T10:00:00Z,init,Started plan initialization
2025-12-02T11:30:00Z,init,Completed environment setup
2025-12-02T14:00:00Z,implement,Implemented JWT service
```

### Entry Fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO timestamp |
| `phase` | Phase when entry was created |
| `summary` | Brief description of work done |

---

## Operations

### add

Add a new log entry.

```bash
python3 scripts/manage-work-log.py add \
  --plan-id {plan_id} \
  --phase implement \
  --summary "Implemented JWT token generation"
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
phase: implement
timestamp: 2025-12-02T14:30:00Z
summary: Implemented JWT token generation
total_entries: 4
```

### read

Read all log entries.

```bash
python3 scripts/manage-work-log.py read \
  --plan-id {plan_id} \
  [--phase implement]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
total_entries: 3

entries[3]{timestamp,phase,summary}:
2025-12-02T10:00:00Z,init,Started plan initialization
2025-12-02T11:30:00Z,init,Completed environment setup
2025-12-02T14:00:00Z,implement,Implemented JWT service
```

### list

List entries summary.

```bash
python3 scripts/manage-work-log.py list \
  --plan-id {plan_id} \
  [--limit 10]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
total_entries: 15
showing: 10

entries[10]{timestamp,phase,summary}:
...
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `manage-work-log.py` | All log operations via subcommands | `python3 scripts/manage-work-log.py {command} --help` |

---

## Integration Points

### With plan-execute

Execution logs work as steps are completed.
