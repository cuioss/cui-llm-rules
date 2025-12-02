# Handoff Skill

Centralized skill for workflow state transfer between agents, skills, and commands using the TOON handoff protocol.

## Purpose

Provides structured handoff communication for:
- Phase transitions in task workflows
- Error propagation with alternatives
- Cross-component state transfer
- Session resumption and recovery

## Operations

### save

Save a handoff to the memory layer.

**Parameters:**
- `plan_id` (required): Plan identifier
- `step` (required): Step name (e.g., `init-complete`, `verify-error`)
- `content` (required): TOON handoff content

**Example:**
```bash
python3 scripts/handoff.py save \
  --plan_id jwt-auth \
  --step init-complete \
  --content 'from: plan-init-skill
to: plan-configure-skill
plan_id: jwt-auth
task:
  status: completed
next_action: Configure plan type'
```

### load

Load most recent handoff by plan_id and step.

**Parameters:**
- `plan_id` (required): Plan identifier
- `step` (required): Step name

**Example:**
```bash
python3 scripts/handoff.py load \
  --plan_id jwt-auth \
  --step init-complete
```

### list

List handoffs with optional filtering.

**Parameters:**
- `plan_id` (optional): Filter by plan ID
- `since` (optional): Filter by age (e.g., `7d`, `24h`, `30m`)
- `status` (optional): Filter by status (`pending`, `in_progress`, `completed`, `failed`, `blocked`)

**Example:**
```bash
python3 scripts/handoff.py list --plan_id jwt-auth --status completed
```

### get

Get a specific handoff by filename.

**Parameters:**
- `file` (required): Handoff filename

**Example:**
```bash
python3 scripts/handoff.py get --file jwt-auth-init-complete-20251202T103000Z.toon
```

### cleanup

Remove old handoffs based on age.

**Parameters:**
- `older-than` (optional): Age threshold (default: `7d`)
- `plan_id` (optional): Filter by plan ID

**Example:**
```bash
python3 scripts/handoff.py cleanup --older-than 7d
```

## Handoff Protocol

See [standards/protocol.md](standards/protocol.md) for the full handoff protocol specification.

### Required Fields

| Field | Description |
|-------|-------------|
| `from` | Source component |
| `to` | Target component |
| `plan_id` | Plan identifier |
| `task.status` | One of: `pending`, `in_progress`, `completed`, `failed`, `blocked` |

### Common Optional Fields

| Field | Description |
|-------|-------------|
| `handoff_id` | Unique identifier (auto-generated if missing) |
| `timestamp` | ISO timestamp (auto-generated if missing) |
| `task.description` | What needs to be done |
| `task.progress` | Percentage (0-100) |
| `task_id` | Specific task within phase |
| `artifacts` | Files, directories, references |
| `requirements` | REQ IDs being worked on |
| `next_action` | What to do next |
| `next_focus` | Specific focus area |
| `error` | Error details (when status=failed) |
| `alternatives` | Options for recovery |

## Templates

- [phase-transition.toon](templates/phase-transition.toon) - Standard phase transition
- [error.toon](templates/error.toon) - Error with alternatives
- [completion.toon](templates/completion.toon) - Successful completion

## Storage

Handoffs are stored in `.plan/memory/handoffs/` with filename format:
```
{plan_id}-{step}-{timestamp}.toon
```

Example: `jwt-auth-init-complete-20251202T103000Z.toon`

## Integration

### With Plan Phases

Each plan phase creates a handoff for the next phase:

| Transition | Step Name |
|------------|-----------|
| init → configure | `init-complete` |
| configure → refine | `configure-complete` |
| refine → implement | `refine-complete` |
| implement → verify | `implement-complete` |
| verify → finalize | `verify-complete` |
| finalize → done | `finalize-complete` |

### With Error Handling

Error handoffs include alternatives for user decision:

```toon
task:
  status: failed

error:
  type: build_failure
  message: Tests failed during task execution

alternatives[3]:
- Fix failing tests
- View test details
- Skip to next task
```

## Related

- [file-operations-base](../file-operations-base/) - Base file operations and TOON parser
- [manage-memories](../manage-memories/) - Session context snapshots (different lifecycle)
