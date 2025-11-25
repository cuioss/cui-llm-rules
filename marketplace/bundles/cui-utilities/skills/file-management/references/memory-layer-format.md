# Memory Layer Format

File format specifications for `.claude/memory/` session persistence.

## Directory Structure

```
.claude/memory/
├── context/         # Session context snapshots
├── decisions/       # Architectural decisions
├── interfaces/      # Interface contracts
├── handoffs/        # Pending handoff state
└── archive/         # Archived files
    ├── context/
    ├── decisions/
    ├── interfaces/
    └── handoffs/
```

## Memory File Envelope

All memory files use a metadata envelope:

```json
{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "context|decisions|interfaces|handoffs",
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
| category | string | One of: context, decisions, interfaces, handoffs |
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
    "decisions": ["Use JWT for auth", "Store sessions in Redis"],
    "interfaces": {
      "AuthService": {"methods": ["login", "logout"]}
    },
    "pending": ["Implement token refresh"],
    "notes": "Working on authentication feature"
  }
}
```

### decisions

Architectural decisions. Long-lived, typically permanent.

**File naming**: `{summary}.json`

**Example**: `auth-implementation.json`

**Content structure**:
```json
{
  "meta": { ... },
  "content": {
    "decision": "Use JWT tokens for authentication",
    "rationale": "Stateless, scalable, standard",
    "alternatives_considered": ["Session cookies", "OAuth only"],
    "constraints": ["Must work offline", "Mobile support"],
    "status": "accepted|superseded|deprecated"
  }
}
```

### interfaces

Interface contracts. Medium-lived, updated as interfaces evolve.

**File naming**: `{module-name}.json`

**Example**: `auth-module.json`

**Content structure**:
```json
{
  "meta": { ... },
  "content": {
    "module": "auth",
    "types": {
      "User": {"id": "string", "email": "string"},
      "AuthResult": {"success": "boolean", "token": "string?"}
    },
    "functions": {
      "login": {"params": ["email", "password"], "returns": "AuthResult"},
      "logout": {"params": ["token"], "returns": "void"}
    },
    "events": ["user.logged_in", "user.logged_out"]
  }
}
```

### handoffs

Pending handoff state. Short-lived, archived when completed.

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

Creates or updates a memory file.

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
  --category decisions \
  --identifier "auth-implementation"
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
  --category decisions
```

### Cleanup

Removes old files.

```bash
python3 scripts/manage-memory.py cleanup \
  --category context \
  --older-than 7d
```

### Archive

Moves file to archive.

```bash
python3 scripts/manage-memory.py archive \
  --category handoffs \
  --identifier "task-42"
```

---

## Lifecycle Recommendations

| Category | Typical Lifetime | Cleanup Strategy |
|----------|-----------------|------------------|
| context | Days | Auto-cleanup after 7d |
| decisions | Permanent | Manual archive when superseded |
| interfaces | Weeks/Months | Update in place |
| handoffs | Until completed | Archive on completion |

## .gitignore

The memory directory should be gitignored:

```
.claude/memory/
```

Context and handoffs are session-specific. Decisions and interfaces may be shared but are typically regenerated.
