# Handoff Skill

Centralized skill for workflow state transfer between agents, skills, and commands using the TOON handoff protocol.

## Purpose

Provides structured handoff communication for:
- Phase transitions in task workflows
- Error propagation with alternatives
- Cross-component state transfer
- Session resumption and recovery

## Storage

Handoffs are stored **plan-locally** in `.plan/plans/{plan_id}/handoffs/`. This ensures:
- All plan artifacts in one place
- Automatic cleanup when plan is deleted
- No orphaned handoffs
- Simple filename structure (no plan_id prefix)

## Operations

### save

Save a handoff to the plan's handoff directory.

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

List handoffs for a specific plan.

**Parameters:**
- `plan_id` (required): Plan identifier
- `status` (optional): Filter by status (`pending`, `in_progress`, `completed`, `failed`, `blocked`)

**Example:**
```bash
python3 scripts/handoff.py list --plan_id jwt-auth --status completed
```

### get

Get a specific handoff by filename.

**Parameters:**
- `plan_id` (required): Plan identifier
- `file` (required): Handoff filename

**Example:**
```bash
python3 scripts/handoff.py get --plan_id jwt-auth --file init-complete-20251202T103000Z.toon
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

## File Structure

Handoffs are stored in the plan's directory:
```
.plan/plans/{plan_id}/handoffs/
├── init-complete-20251202T103000Z.toon
├── configure-complete-20251202T104500Z.toon
└── verify-error-20251202T110000Z.toon
```

Filename format: `{step}-{timestamp}.toon`

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

## References

- [standards/protocol.md](standards/protocol.md) - Full handoff protocol specification
- [references/architecture.md](references/architecture.md) - Interaction patterns and use cases
- [references/context-compression.md](references/context-compression.md) - Context reduction strategies for long sessions
- [references/wave-processing.md](references/wave-processing.md) - Parallel task batching with sync points
- [references/token-budget-guidelines.md](references/token-budget-guidelines.md) - Token allocation for agent orchestration
- [references/integration-validation.md](references/integration-validation.md) - Validation patterns for parallel execution

## Related

- [phase-management](../phase-management/) - Plan phase transitions using handoffs
- [plan-execute](../plan-execute/) - Plan execution with handoff-based state transfer
