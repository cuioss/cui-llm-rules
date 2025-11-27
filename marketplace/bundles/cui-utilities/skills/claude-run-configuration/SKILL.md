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
- Manage acceptable warnings and skip lists
- Validate run configuration format
- Schema documentation for configuration structure

## When to Activate This Skill

Activate this skill when:
- Recording command execution results
- Managing acceptable warnings lists
- Managing skipped files/directories
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
        "status": "SUCCESS|FAILURE"
      },
      "acceptable_warnings": [],
      "skipped_files": [],
      "skipped_directories": []
    }
  },
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": [],
      "plugin_compatibility": [],
      "platform_specific": []
    }
  }
}
```

---

## Workflow: Initialize Configuration

**Pattern**: Command Chain Execution

**CRITICAL**: Always ensure the file exists before reading or updating. Use the init script to create it with proper base structure.

### Step 1: Initialize Configuration File

```bash
python3 scripts/init-run-config.py
```

This creates `.claude/run-configuration.json` with base structure if it doesn't exist.

**Options:**
- `--project-dir /path/to/project` - Initialize in specific directory
- `--force` - Overwrite existing file

**Base Structure Created:**
```json
{
  "version": 1,
  "commands": {},
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": [],
      "plugin_compatibility": [],
      "platform_specific": []
    }
  }
}
```

### Alternative: Manual Initialization

If the script is not available, create manually:

```bash
test -f .claude/run-configuration.json || \
  python3 json-file-operations/scripts/manage-json-file.py write .claude/run-configuration.json \
    --value '{"version": 1, "commands": {}, "maven": {"acceptable_warnings": {"transitive_dependency": [], "plugin_compatibility": [], "platform_specific": []}}}'
```

---

## Workflow: Read Configuration

**Pattern**: Command Chain Execution

Read run configuration or specific command entry.

### Step 1: Ensure File Exists

First, run the **Initialize Configuration** workflow to ensure the file exists.

### Step 2: Read Using json-file-operations

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

### Step 1: Ensure File Exists

First, run the **Initialize Configuration** workflow to ensure the file exists with base structure.

### Step 2: Ensure Command Entry Exists

Before updating nested fields, ensure the command entry exists:

```bash
# Create command entry if it doesn't exist (update-field auto-creates intermediate objects)
python3 json-file-operations/scripts/manage-json-file.py update-field .claude/run-configuration.json \
  --field "commands.<command-name>" \
  --value '{}'
```

**Note**: Skip this step if the command entry already exists.

### Step 3: Update Last Execution

```bash
python3 json-file-operations/scripts/manage-json-file.py update-field .claude/run-configuration.json \
  --field "commands.<command-name>.last_execution" \
  --value '{"date": "2025-11-25", "status": "SUCCESS", "duration_ms": 12345}'
```

### Complete Example

```bash
# Step 1: Initialize if not exists
test -f .claude/run-configuration.json || \
  python3 json-file-operations/scripts/manage-json-file.py write .claude/run-configuration.json \
    --value '{"version": 1, "commands": {}, "maven": {"acceptable_warnings": {"transitive_dependency": [], "plugin_compatibility": [], "platform_specific": []}}}'

# Step 2: Create command entry
python3 json-file-operations/scripts/manage-json-file.py update-field .claude/run-configuration.json \
  --field "commands.verify-integration-tests" \
  --value '{}'

# Step 3: Update execution status
python3 json-file-operations/scripts/manage-json-file.py update-field .claude/run-configuration.json \
  --field "commands.verify-integration-tests.last_execution" \
  --value '{"date": "2025-11-27", "status": "SUCCESS", "duration_ms": 231584}'
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
| acceptable_warnings | array | Warnings to ignore |
| skipped_files | array | Files to skip in processing |
| skipped_directories | array | Directories to skip |
| user_approved_permissions | array | Permissions approved by user |

### maven

Maven build configurations.

| Field | Type | Description |
|-------|------|-------------|
| acceptable_warnings | object | Warning patterns by category |

Categories: `transitive_dependency`, `plugin_compatibility`, `platform_specific`

---

## Scripts

| Script | Purpose |
|--------|---------|
| `init-run-config.py` | Initialize run configuration with base structure |
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

### With claude-lessons-learned Skill
- Lessons learned are stored separately in `.claude/lessons-learned/`
- Run configuration tracks execution state only

---

## References

- `references/run-config-format.md` - Complete schema documentation
