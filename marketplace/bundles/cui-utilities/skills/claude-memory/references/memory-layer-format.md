# Memory Layer Format

File format specifications for `.claude/memory/` session persistence.

## Directory Structure

```
.claude/memory/
├── context/         # Session context snapshots
└── handoffs/        # Pending handoff state
```

## Memory File Envelope

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

### Optional Meta Fields

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Claude Code session identifier |

---

## Categories

### context

Session context snapshots. Short-lived, typically cleaned up after days.

**File naming**: `{date}-{summary}.json`

**Example**: `2025-11-25-feature-auth.json`

**Content structure**:
```json
{
  "meta": { ... },
  "content": {
    "pending": ["Implement token refresh"],
    "notes": "Working on authentication feature"
  }
}
```

### handoffs

Pending handoff state. Short-lived, deleted when completed.

**File naming**: `{task-id}.json`

**Example**: `task-42.json`

**Content structure**:
```json
{
  "meta": { ... },
  "content": {
    "task": "Implement user authentication",
    "progress": "70%",
    "completed": ["Login form", "Token generation"],
    "pending": ["Logout", "Session refresh"],
    "blockers": [],
    "next_steps": ["Implement logout endpoint"],
    "context_references": ["2025-11-25-feature-auth"]
  }
}
```

---

## Operations

### Save

Creates or updates a memory file. Directories are created on-the-fly.

```bash
python3 scripts/manage-memory.py save \
  --category context \
  --identifier "feature-auth" \
  --content '{"decisions": ["Use JWT"]}'
```

For `context` category, date prefix is auto-added.

### Load

Retrieves memory file content.

```bash
python3 scripts/manage-memory.py load \
  --category handoffs \
  --identifier "task-42"
```

### List

Lists files in category.

```bash
python3 scripts/manage-memory.py list \
  --category context \
  --since 7d
```

### Query

Finds files by pattern.

```bash
python3 scripts/manage-memory.py query \
  --pattern "auth*" \
  --category context
```

### Cleanup

Removes old files.

```bash
python3 scripts/manage-memory.py cleanup \
  --category context \
  --older-than 7d
```

---

## Lifecycle Recommendations

| Category | Typical Lifetime | Cleanup Strategy |
|----------|-----------------|------------------|
| context | Days | Auto-cleanup after 7d |
| handoffs | Until completed | Delete on completion |
