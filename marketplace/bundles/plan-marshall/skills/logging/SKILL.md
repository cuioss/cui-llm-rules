---
name: logging
description: Unified logging infrastructure for script execution and work progress tracking
allowed-tools: Read, Bash
---

# Logging Skill

Unified logging infrastructure providing script execution logging and semantic work progress tracking.

## Overview

This skill provides a single unified API for two logging concerns:

1. **Script Execution Logging**: Tracking of script executor invocations (type: `script`)
2. **Work Logging**: Semantic tracking of work progress (type: `work`)

## Log Files

### Script Execution Log

**File**: `.plan/plans/{plan-id}/script-execution.log` (plan-scoped)
**Fallback**: `.plan/logs/script-execution-YYYY-MM-DD.log` (global)

### Work Log

**File**: `.plan/plans/{plan-id}/work.log`

---

## CLI Script Usage

Script: `plan-marshall:logging:manage-log`

### Simplified API

```bash
manage-log {type} {plan_id} {level} "{message}"
```

**Arguments** (all positional, all required):

| Argument | Values | Description |
|----------|--------|-------------|
| `type` | `script`, `work` | Log type (determines output file) |
| `plan_id` | kebab-case | Plan identifier |
| `level` | `SUCCESS`, `ERROR`, `INFO`, `WARN` | Log level |
| `message` | string | Log message |

**Output**: None (exit code only)

### Examples

```bash
# Script execution logging
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  script my-plan SUCCESS "pm-workflow:manage-task:manage-task add (0.15s)"

python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  script my-plan ERROR "pm-workflow:manage-task:manage-task add failed (exit 1)"

# Work logging
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work my-plan INFO "Created deliverable: auth module"

python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work my-plan WARN "Skipped validation step"
```

---

## Log Format

### Standard Entry Structure

```
[{timestamp}] [{level}] [{type}] {message}
```

### Example Output

**script-execution.log**:
```
[2025-12-11T12:14:26Z] [SUCCESS] [SCRIPT] pm-workflow:manage-files:manage-files create (0.19s)
[2025-12-11T12:17:50Z] [ERROR] [SCRIPT] pm-workflow:manage-task:manage-task add failed (exit 1)
```

**work.log**:
```
[2025-12-11T11:14:30Z] [INFO] [WORK] Starting init phase
[2025-12-11T11:14:48Z] [INFO] [WORK] Created deliverable: auth module
[2025-12-11T11:17:50Z] [WARN] [WORK] Skipped validation step
```

### Log Levels

| Level | Description |
|-------|-------------|
| `SUCCESS` | Operation completed successfully |
| `INFO` | Progress or informational message |
| `WARN` | Warning (non-fatal issue) |
| `ERROR` | Error with details |

---

## Python API

### Unified Log Entry (Simplified)

```python
from logging import log_entry

# Log to work.log
log_entry(
    log_type='work',
    plan_id='my-plan',
    level='INFO',
    message='Created deliverable: auth module'
)

# Log to script-execution.log
log_entry(
    log_type='script',
    plan_id='my-plan',
    level='SUCCESS',
    message='pm-workflow:manage-task:manage-task add (0.15s)'
)
```

### Legacy Functions (Still Available)

```python
from logging import log_script_execution, log_work, read_work_log, list_recent_work

# Script execution with full details (used by executor)
log_script_execution(
    notation='pm-workflow:manage-files:manage-files',
    subcommand='add',
    args=['--plan-id', 'my-plan', '--file', 'test.md'],
    exit_code=0,
    duration=0.15,
    stdout='',
    stderr=''
)

# Work logging with category/phase (legacy)
result = log_work(
    plan_id='my-plan',
    category='DECISION',
    message='Selected plan-type-java',
    phase='init',
    detail='Task modifies .java files'
)

# Read/list work entries
entries = read_work_log(plan_id='my-plan', phase='init')
recent = list_recent_work(plan_id='my-plan', limit=10)
```

### Utility Functions

```python
from logging import format_timestamp, format_log_entry, get_log_path, extract_plan_id

# Get current timestamp
ts = format_timestamp()  # '2025-12-11T12:14:26Z'

# Get log file path
path = get_log_path(plan_id='my-plan', log_type='work')    # .plan/plans/my-plan/work.log
path = get_log_path(plan_id='my-plan', log_type='script')  # .plan/plans/my-plan/script-execution.log

# Extract plan-id from args
plan_id = extract_plan_id(['--plan-id', 'my-plan', '--file', 'test.md'])  # 'my-plan'
```

---

## Storage Locations

### Plan-Scoped Logs

```
.plan/plans/{plan-id}/
├── script-execution.log    # Script execution tracking
└── work.log                # Work progress tracking
```

### Global Logs

```
.plan/logs/
└── script-execution-YYYY-MM-DD.log    # Daily global script logs
```

**Scope Selection**:
- If `plan_id` is provided and plan exists: plan-scoped log
- Otherwise: global log (script execution only, work requires plan)

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PLAN_BASE_DIR` | Base directory for .plan structure | `.plan` |
| `LOG_MAX_OUTPUT` | Max chars to capture from stdout/stderr | `2000` |
| `LOG_RETENTION_DAYS` | Days to keep global logs | `7` |

---

## Integration Points

### With Script Executor

The executor automatically calls `log_script_execution()` after each script run.

### With Planning Skills

Planning skills call the simplified API:

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work my-plan INFO "Created task: implement auth module"
```

---

## Scripts

| Script | Notation | Description |
|--------|----------|-------------|
| `manage-log.py` | `plan-marshall:logging:manage-log` | CLI for all logging operations |
| `plan_logging.py` | - | Python module (imported, not executed) |
