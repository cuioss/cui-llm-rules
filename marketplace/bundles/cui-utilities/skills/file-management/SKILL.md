---
name: file-management
description: Centralized JSON file operations for .claude/ configuration and memory files
allowed-tools: Read, Write, Edit, Bash, Glob
---

# File Management Skill

Centralized file operations for `.claude/` JSON configuration files and memory layer.

## What This Skill Provides

### JSON Configuration Operations
- Read, write, and update `.claude/` JSON files
- Field-level access using JSON path notation
- Array and object manipulation
- Atomic writes with validation

### Memory Layer Operations
- CRUD operations for `.claude/memory/` files
- Category-based organization (context, decisions, interfaces, handoffs)
- Timestamp-based file naming
- Age-based cleanup and archival

### File Format Validation
- Validate JSON structure integrity
- Schema validation for known file types
- Detailed error reporting

## When to Activate This Skill

Activate this skill when:
- Reading or writing `.claude/` configuration files
- Managing session memory or context persistence
- Validating JSON file formats
- Performing structured updates to configuration

## Supported Files

| File | Format | Purpose |
|------|--------|---------|
| `.claude/run-configuration.json` | run-config | Command configurations and execution history |
| `.claude/scripts.local.json` | scripts-local | Script path registry |
| `.claude/settings.local.json` | settings-local | Project permissions |
| `.claude/memory/**/*.json` | memory | Session memory layer |

---

## Workflow: JSON File Operations

**Pattern**: Command Chain Execution

Perform read, write, and update operations on JSON configuration files.

### Parameters

- **file_path** (required): Path to JSON file (relative to project root)
- **operation** (required): One of `read`, `read-field`, `write`, `update-field`, `add-entry`, `remove-entry`
- **field** (optional): JSON path for field operations (e.g., `commands.setup-project-permissions.last_execution`)
- **value** (optional): Value for write/update operations (JSON string)

### Step 1: Execute Operation

```bash
python3 scripts/manage-json-file.py {operation} {file_path} [--field {field}] [--value '{value}']
```

### Step 2: Process Result

Parse JSON output:
- `success: true` → Return result value
- `success: false` → Report error message

### Operations Reference

| Operation | Description | Required Params |
|-----------|-------------|-----------------|
| `read` | Read entire file | file_path |
| `read-field` | Read specific field | file_path, field |
| `write` | Write entire content | file_path, value |
| `update-field` | Update specific field | file_path, field, value |
| `add-entry` | Add to array/object | file_path, field, value |
| `remove-entry` | Remove from array/object | file_path, field, value |

### Example Usage

```bash
# Read entire configuration
python3 scripts/manage-json-file.py read .claude/run-configuration.json

# Read specific field
python3 scripts/manage-json-file.py read-field .claude/run-configuration.json --field "commands.setup-project-permissions.last_execution"

# Update field
python3 scripts/manage-json-file.py update-field .claude/run-configuration.json --field "commands.setup-project-permissions.last_execution.date" --value '"2025-11-25"'

# Add to array
python3 scripts/manage-json-file.py add-entry .claude/run-configuration.json --field "commands.docs-technical-adoc-review.lessons_learned" --value '"New lesson"'
```

---

## Workflow: Memory Operations

**Pattern**: Command Chain Execution

Manage the `.claude/memory/` layer for session persistence.

### Parameters

- **operation** (required): One of `init`, `save`, `load`, `list`, `query`, `cleanup`, `archive`
- **category** (optional): One of `context`, `decisions`, `interfaces`, `handoffs`
- **identifier** (optional): File identifier or summary name
- **content** (optional): JSON content for save operations

### Step 1: Execute Operation

```bash
python3 scripts/manage-memory.py {operation} [--category {category}] [--identifier {identifier}] [--content '{content}']
```

### Step 2: Process Result

Parse JSON output and handle accordingly.

### Operations Reference

| Operation | Description | Required Params |
|-----------|-------------|-----------------|
| `init` | Create memory directory structure | None |
| `save` | Save memory file | category, identifier, content |
| `load` | Load memory file | category, identifier |
| `list` | List files in category | category (optional) |
| `query` | Find files by pattern | pattern |
| `cleanup` | Remove old files | --older-than |
| `archive` | Move to archive | category, identifier |

### Memory Categories

| Category | Purpose | Typical Lifetime |
|----------|---------|------------------|
| `context` | Session context snapshots | Short (days) |
| `decisions` | Architectural decisions | Long (permanent) |
| `interfaces` | Interface contracts | Medium (weeks) |
| `handoffs` | Pending handoff state | Short (until completed) |

### Example Usage

```bash
# Initialize memory structure
python3 scripts/manage-memory.py init

# Save context snapshot
python3 scripts/manage-memory.py save --category context --identifier "feature-auth" --content '{"decisions": ["Use JWT"]}'

# List context files
python3 scripts/manage-memory.py list --category context

# Cleanup old context files
python3 scripts/manage-memory.py cleanup --category context --older-than 7d
```

---

## Workflow: Validate File Format

**Pattern**: Command Chain Execution

Validate JSON file format and structure integrity.

### Parameters

- **file_path** (required): Path to file to validate
- **format** (optional): Expected format type (auto-detected if omitted)

### Step 1: Execute Validation

```bash
python3 scripts/validate-file-format.py {file_path} [--format {format}]
```

### Step 2: Process Result

```json
{
  "success": true,
  "valid": true,
  "checks": [
    {"check": "json_syntax", "passed": true},
    {"check": "required_fields", "passed": true}
  ]
}
```

### Format Types

| Format | File | Required Fields |
|--------|------|-----------------|
| `run-config` | run-configuration.json | version, commands |
| `scripts-local` | scripts.local.json | version, scripts, permissions |
| `settings-local` | settings.local.json | (valid JSON object) |
| `memory` | memory/**/*.json | meta, content |

### Example Usage

```bash
# Validate run configuration
python3 scripts/validate-file-format.py .claude/run-configuration.json --format run-config

# Auto-detect format
python3 scripts/validate-file-format.py .claude/scripts.local.json
```

---

## JSON Path Notation

This skill uses dot notation for JSON paths:

| Path | Description |
|------|-------------|
| `commands` | Top-level field |
| `commands.setup-project-permissions` | Nested object |
| `commands.setup-project-permissions.last_execution.date` | Deep nested field |
| `commands.docs-technical-adoc-review.lessons_learned[0]` | Array index |

### Special Characters

- Use quotes for keys with special characters: `commands."my-command".field`
- Array indices use bracket notation: `array[0]`, `array[-1]` (last element)

---

## Scripts

| Script | Purpose |
|--------|---------|
| `manage-json-file.py` | JSON file CRUD operations |
| `manage-memory.py` | Memory layer management |
| `validate-file-format.py` | File format validation |

All scripts:
- Use Python stdlib only (json, argparse, pathlib, datetime)
- Output JSON to stdout
- Exit code 0 for success, 1 for errors
- Support `--help` flag

---

## Integration Points

### With script-runner Skill
- File-management scripts are discovered via script-runner
- Use portable notation: `cui-utilities:file-management/scripts/manage-json-file.py`

### With permission-management Skill
- Provides generic JSON operations for settings.local.json
- Does not duplicate permission-specific logic

### With cui-task-workflow Bundle
- Memory operations enable task state persistence
- Cleanup operations maintain memory hygiene

---

## References

- `references/config-file-formats.md` - JSON schema specifications
- `references/memory-layer-format.md` - Memory file format documentation
