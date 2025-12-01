---
name: work-log
description: Result-oriented logging for plan execution - captures actions, decisions, and outcomes during task implementation. All phase skills delegate logging here.
allowed-tools: Read, Bash
---

# Work-Log Skill

**EXECUTION MODE**: Execute requested operation immediately. Do not explain or summarize.

**Role**: Centralized logging layer for plan execution. Phase skills call this skill to record significant actions and decisions during task implementation.

## Standards (Load On-Demand)

### Format Specification
```
Read knowledge/format-spec.md
```
Contains: TOON schema, entry structure, field definitions

### Integration Guide
```
Read knowledge/integration-guide.md
```
Contains: When to log, what to log, integration patterns for phase skills

---

## Operation: log-entry

**Input**: `plan_directory`, `phase`, `task`, `action`, `result`

**Steps**:

1. **Write entry via script**:
   ```bash
   python3 scripts/write-entry.py \
     --plan-dir {plan_directory} \
     --phase {phase} \
     --task {task} \
     --action "{action}" \
     --result "{result}"
   ```

2. **Return**: JSON with success status and entry count

**Output**:
```json
{
  "success": true,
  "operation": "log-entry",
  "file": ".plan/plans/{name}/work-log.toon",
  "entry_count": 5,
  "entry": {
    "timestamp": "2025-11-29T10:30:00Z",
    "phase": "implement",
    "task": "task-1",
    "action": "Created validation logic",
    "result": "src/Validator.java"
  }
}
```

---

## Operation: read-log

**Input**: `plan_directory`, `phase` (optional), `task` (optional)

**Steps**:

1. **Read entries via script**:
   ```bash
   python3 scripts/read-log.py \
     --plan-dir {plan_directory} \
     [--phase {phase}] \
     [--task {task}]
   ```

2. **Return**: JSON with entries array and metadata

**Output**:
```json
{
  "success": true,
  "operation": "read-log",
  "file": ".plan/plans/{name}/work-log.toon",
  "total_entries": 12,
  "filtered_entries": 3,
  "entries": [
    {
      "timestamp": "2025-11-29T10:30:00Z",
      "phase": "implement",
      "task": "task-1",
      "action": "Created validation logic",
      "result": "src/Validator.java"
    }
  ]
}
```

---

## Scripts

Python scripts for deterministic operations (output JSON):

| Script | Purpose | Usage |
|--------|---------|-------|
| `write-entry.py` | Add log entry | `python3 scripts/write-entry.py --help` |
| `read-log.py` | Query log entries | `python3 scripts/read-log.py --help` |

---

## Error Handling

### File Not Found (read-log)
```json
{
  "success": true,
  "operation": "read-log",
  "file": ".plan/plans/{name}/work-log.toon",
  "total_entries": 0,
  "entries": [],
  "note": "No work-log exists yet"
}
```

### Invalid Directory
```json
{
  "success": false,
  "error": "Plan directory not found",
  "path": "{plan_directory}"
}
```

### Write Error
```json
{
  "success": false,
  "error": "Failed to write entry",
  "details": "{error_message}"
}
```

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All operations have clear input/output
- [x] Error handling for all scenarios
- [x] Python scripts for deterministic operations
- [x] Knowledge docs for format and integration
