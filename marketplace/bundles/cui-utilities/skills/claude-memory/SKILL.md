---
name: claude-memory
description: Memory layer operations for .claude/memory/ session persistence
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Claude Memory Skill

Memory layer operations for `.claude/memory/` session persistence.

## What This Skill Provides

- CRUD operations for `.claude/memory/` files
- Category-based organization (context, handoffs)
- Timestamp-based file naming for context files
- Age-based cleanup
- Memory file format validation

## When to Activate This Skill

Activate this skill when:
- Persisting session context
- Managing handoff state between sessions
- Cleaning up old memory files

---

## Memory Categories

| Category | Purpose | Typical Lifetime |
|----------|---------|------------------|
| `context` | Session context snapshots | Short (days) |
| `handoffs` | Pending handoff state | Short (until completed) |

---

## Workflow: Memory Operations

**Pattern**: Command Chain Execution

Manage the `.claude/memory/` layer for session persistence.

### Parameters

- **operation** (required): One of `save`, `load`, `list`, `query`, `cleanup`
- **category** (optional): One of `context`, `handoffs`
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
| `save` | Save memory file (creates directories on-the-fly) | category, identifier, content |
| `load` | Load memory file | category, identifier |
| `list` | List files in category | category (optional) |
| `query` | Find files by pattern | pattern |
| `cleanup` | Remove old files | --older-than |

### Example Usage

```bash
# Save context snapshot (directories created on-the-fly)
python3 scripts/manage-memory.py save --category context --identifier "feature-auth" --content '{"notes": "Working on auth feature"}'

# Load memory file
python3 scripts/manage-memory.py load --category handoffs --identifier "task-42"

# List context files from last 7 days
python3 scripts/manage-memory.py list --category context --since 7d

# Find files matching pattern
python3 scripts/manage-memory.py query --pattern "auth*" --category context

# Cleanup old context files
python3 scripts/manage-memory.py cleanup --category context --older-than 7d
```

---

## Workflow: Validate Memory File

**Pattern**: Command Chain Execution

Validate memory file format and structure.

### Parameters

- **file_path** (required): Path to memory file

### Step 1: Execute Validation

```bash
python3 scripts/validate-memory.py {file_path}
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

---

## Memory File Format

All memory files use a metadata envelope:

```json
{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "context|handoffs",
    "summary": "feature-auth",
    "session_id": "optional-session-id"
  },
  "content": {
    // Category-specific content
  }
}
```

### Required Meta Fields

| Field | Type | Description |
|-------|------|-------------|
| created | string | ISO 8601 timestamp with Z suffix |
| category | string | One of: context, handoffs |
| summary | string | Human-readable identifier |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `manage-memory.py` | Memory layer CRUD operations |
| `validate-memory.py` | Memory file format validation |

All scripts:
- Use Python stdlib only (json, argparse, pathlib, datetime)
- Output JSON to stdout
- Exit code 0 for success, 1 for errors
- Support `--help` flag

---

## Integration Points

### With json-file-operations Skill
- Uses generic JSON operations for low-level file access

### With script-runner Skill
- Memory scripts are discovered via script-runner
- Use portable notation: `cui-utilities:claude-memory/scripts/manage-memory.py`

### With cui-task-workflow Bundle
- Memory operations enable task state persistence
- Cleanup operations maintain memory hygiene

---

## References

- `references/memory-layer-format.md` - Complete memory file format documentation
