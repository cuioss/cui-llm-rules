---
name: run-config
description: Run configuration handling for persistent command configuration storage
allowed-tools: Read, Write, Edit, Bash
---

# Run Config Skill

Run configuration handling for persistent command configuration storage (via `file-operations-base` skill).

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
- Working with run configuration storage

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
python3 .plan/execute-script.py plan-marshall:run-config:run_config init
```

This creates the run configuration file with base structure if it doesn't exist.

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
test -f {run-config-file} || \
  python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file write {run-config-file} \
    --value '{"version": 1, "commands": {}, "maven": {"acceptable_warnings": {"transitive_dependency": [], "plugin_compatibility": [], "platform_specific": []}}}'
```

> **Note**: `{run-config-file}` is resolved by the `file-operations-base` skill.

---

## Workflow: Read Configuration

**Pattern**: Command Chain Execution

Read run configuration or specific command entry.

### Step 1: Ensure File Exists

First, run the **Initialize Configuration** workflow to ensure the file exists.

### Step 2: Read Using json-file-operations

```bash
# Read entire configuration
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file read {run-config-file}

# Read specific command entry
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file read-field {run-config-file} \
  --field "commands.setup-project-permissions"

# Read last execution
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file read-field {run-config-file} \
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
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file update-field {run-config-file} \
  --field "commands.<command-name>" \
  --value '{}'
```

**Note**: Skip this step if the command entry already exists.

### Step 3: Update Last Execution

```bash
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file update-field {run-config-file} \
  --field "commands.<command-name>.last_execution" \
  --value '{"date": "2025-11-25", "status": "SUCCESS", "duration_ms": 12345}'
```

### Complete Example

```bash
# Step 1: Initialize if not exists
test -f {run-config-file} || \
  python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file write {run-config-file} \
    --value '{"version": 1, "commands": {}, "maven": {"acceptable_warnings": {"transitive_dependency": [], "plugin_compatibility": [], "platform_specific": []}}}'

# Step 2: Create command entry
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file update-field {run-config-file} \
  --field "commands.verify-integration-tests" \
  --value '{}'

# Step 3: Update execution status
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file update-field {run-config-file} \
  --field "commands.verify-integration-tests.last_execution" \
  --value '{"date": "2025-11-27", "status": "SUCCESS", "duration_ms": 231584}'
```

---

## Workflow: Validate Configuration

**Pattern**: Command Chain Execution

Validate run configuration format and structure.

### Step 1: Execute Validation

```bash
python3 .plan/execute-script.py plan-marshall:run-config:run_config validate {run-config-file}
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

## Workflow: Timeout Handling for Synchronous Builds

**Pattern**: Adaptive Learning

Manage command timeouts with learned values based on execution history. Primary use case is **synchronous builds** (Maven, npm, Gradle).

**Load Reference**:
```
Read standards/timeout-handling.md
```

### Complete Build Execution Pattern

The standard pattern for builds with adaptive timeout:

```bash
# 1. Get adaptive timeout (plain number in seconds)
TIMEOUT=$(python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout get \
  --command "build:maven_verify" --default 300)

# 2. Execute with shell timeout
START=$(date +%s)
timeout ${TIMEOUT}s mvn verify
EXIT_CODE=$?
END=$(date +%s)

# 3. Record duration for adaptive learning
python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout set \
  --command "build:maven_verify" --duration $((END - START))
```

### Get Timeout

Retrieve timeout for a command with default fallback. Returns plain number (seconds).

```bash
python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout get \
  --command "build:maven_verify" \
  --default 300
```

**Output**: Plain number (e.g., `300`)

**Logic**:
- If no persisted value: returns `--default`
- If persisted: returns `persisted * 1.25` (safety margin)

### Set Timeout

Update timeout for a command with adaptive weighting.

```bash
python3 .plan/execute-script.py plan-marshall:run-config:run_config timeout set \
  --command "build:maven_verify" \
  --duration 180
```

**Output** (TOON format):
```
status           success
command          build:maven_verify
timeout_seconds  228
previous_seconds 240
source           initial|computed
```

**Logic**:
- If not set: writes directly
- If set: 80% weight to higher value (favors reliability)

### Recommended Defaults

| Command Type | Default (seconds) |
|--------------|-------------------|
| test-compile | 120 |
| test | 300 |
| verify | 300 |
| install | 300 |
| pre-commit | 600 |
| integration | 900 |

### Polling Operations (Corner Case)

For async polling (CI checks, Sonar), use `await-until --command-key` instead. It handles timeout internally with a generous external timeout as circuit breaker:

```bash
# await-until manages timeout internally via run-config
# External timeout (600s) is just a safety net
timeout 600s python3 .plan/execute-script.py plan-marshall:script-executor:await-until poll \
  --check-cmd "gh pr checks 123 --json state" \
  --success-field "state=completed" \
  --command-key "ci:pr_checks"
```

---

## Scripts

| Script | Notation |
|--------|----------|
| init | `plan-marshall:run-config:run_config init` |
| validate | `plan-marshall:run-config:run_config validate` |
| timeout get | `plan-marshall:run-config:run_config timeout get` |
| timeout set | `plan-marshall:run-config:run_config timeout set` |
| cleanup | `plan-marshall:run-config:cleanup` |

Script characteristics:
- Uses Python stdlib only (json, argparse, pathlib)
- Outputs JSON (init/validate) or TOON (timeout/cleanup) to stdout
- Exit code 0 for success, 1 for errors
- Supports `--help` flag

---

## Workflow: Cleanup Plan Directory

**Pattern**: Command Chain Execution

Clean temporary files, logs, archived plans, and memory based on retention settings.

### Step 1: Run Cleanup (Dry Run)

Preview what would be deleted:

```bash
python3 .plan/execute-script.py plan-marshall:run-config:cleanup run --dry-run
```

### Step 2: Run Cleanup

Execute cleanup with default retention (1 day logs, 5 days archived/memory):

```bash
python3 .plan/execute-script.py plan-marshall:run-config:cleanup run
```

### Step 3: Custom Retention

Override retention periods:

```bash
python3 .plan/execute-script.py plan-marshall:run-config:cleanup run \
    --logs-days 1 \
    --archived-days 5 \
    --memory-days 5
```

### Output (TOON)

```toon
status: success
operation: cleanup
dry_run: false

deleted[4]{category,count,size_bytes}:
logs	12	45678
archived_plans	3	12345
memory	5	8901
temp	28	56789
```

---

## Integration Points

### With json-file-operations Skill
- Uses generic JSON operations for field access and updates
- All CRUD operations delegate to json-file-operations

### With Scripts Library
- Validation script discovered via scripts-library.toon
- Use portable notation from Scripts table above

### With planning Bundle
- Commands record execution history to run configuration

### With lessons-learned Skill
- Lessons learned are stored separately via `plan-marshall:lessons-learned` skill
- Run configuration tracks execution state only

---

## References

- `references/run-config-format.md` - Complete schema documentation
- `standards/timeout-handling.md` - Adaptive timeout management specification
