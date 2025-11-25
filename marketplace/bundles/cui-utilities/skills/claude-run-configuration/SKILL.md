---
name: claude-run-configuration
description: Run configuration handling for .claude/run-configuration.json
allowed-tools: Read, Write, Edit, Bash
---

# Claude Run Configuration Skill

Run configuration handling for `.claude/run-configuration.json` command configurations and execution history.

## What This Skill Provides

- Read and update run configuration entries
- Track command execution history
- Manage lessons learned and acceptable warnings
- Validate run configuration format
- Schema documentation for configuration structure

## When to Activate This Skill

Activate this skill when:
- Recording command execution results
- Updating lessons learned from command runs
- Managing acceptable warnings lists
- Validating run configuration structure
- Working with `.claude/run-configuration.json`

---

## Run Configuration Structure

```json
{
  "version": 1,
  "commands": {
    "<command-name>": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS|FAILURE",
        "run_number": 1
      },
      "lessons_learned": ["Array of lessons"],
      "acceptable_warnings": []
    }
  },
  "maven": {
    "<maven-command>": {
      "last_execution": { ... },
      "acceptable_warnings": [ ... ]
    }
  },
  "agent_decisions": {
    "<agent-name>": {
      "status": "keep-monolithic|refactored",
      "decision_date": "2025-10-30",
      "rationale": "Why this decision was made"
    }
  }
}
```

---

## Workflow: Read Configuration

**Pattern**: Command Chain Execution

Read run configuration or specific command entry.

### Using json-file-operations

```bash
# Read entire configuration
python3 json-file-operations/scripts/manage-json-file.py read .claude/run-configuration.json

# Read specific command entry
python3 json-file-operations/scripts/manage-json-file.py read-field .claude/run-configuration.json \
  --field "commands.setup-project-permissions"

# Read last execution
python3 json-file-operations/scripts/manage-json-file.py read-field .claude/run-configuration.json \
  --field "commands.setup-project-permissions.last_execution"
```

---

## Workflow: Update Execution Status

**Pattern**: Command Chain Execution

Record command execution results.

### Step 1: Update Last Execution

```bash
python3 json-file-operations/scripts/manage-json-file.py update-field .claude/run-configuration.json \
  --field "commands.<command-name>.last_execution" \
  --value '{"date": "2025-11-25", "status": "SUCCESS", "run_number": 1}'
```

### Step 2: Add Lesson Learned (optional)

```bash
python3 json-file-operations/scripts/manage-json-file.py add-entry .claude/run-configuration.json \
  --field "commands.<command-name>.lessons_learned" \
  --value '"New lesson from this execution"'
```

---

## Workflow: Validate Configuration

**Pattern**: Command Chain Execution

Validate run configuration format and structure.

### Step 1: Execute Validation

```bash
python3 scripts/validate-run-config.py .claude/run-configuration.json
```

### Step 2: Process Result

```json
{
  "success": true,
  "valid": true,
  "checks": [
    {"check": "json_syntax", "passed": true},
    {"check": "required_fields", "passed": true, "fields": ["version", "commands"]},
    {"check": "version_type", "passed": true},
    {"check": "commands_object", "passed": true}
  ]
}
```

---

## Configuration Sections

### commands

Per-command configuration and history.

| Field | Type | Description |
|-------|------|-------------|
| last_execution | object | Most recent execution details |
| lessons_learned | array | Accumulated lessons from executions |
| acceptable_warnings | array | Warnings to ignore |
| skipped_files | array | Files to skip in processing |
| skipped_directories | array | Directories to skip |

### maven

Maven-specific build configurations.

| Field | Type | Description |
|-------|------|-------------|
| last_execution | object | Build timing information |
| acceptable_warnings | array | Warning patterns to accept |

### agent_decisions

Agent architecture decisions.

| Field | Type | Description |
|-------|------|-------------|
| status | string | Current state (keep-monolithic, refactored) |
| decision_date | string | When decision was made |
| rationale | string | Reasoning for decision |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `validate-run-config.py` | Run configuration format validation |

Script characteristics:
- Uses Python stdlib only (json, argparse, pathlib)
- Outputs JSON to stdout
- Exit code 0 for success, 1 for errors
- Supports `--help` flag

---

## Integration Points

### With json-file-operations Skill
- Uses generic JSON operations for field access and updates
- All CRUD operations delegate to json-file-operations

### With script-runner Skill
- Validation script discovered via script-runner
- Use portable notation: `cui-utilities:claude-run-configuration/scripts/validate-run-config.py`

### With cui-task-workflow Bundle
- Commands record execution history to run configuration
- Lessons learned accumulate across executions

---

## References

- `references/run-config-format.md` - Complete schema documentation
