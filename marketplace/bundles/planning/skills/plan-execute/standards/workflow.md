# Plan Execute Workflow

## Execution Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DUMB TASK RUNNER                                    │
│                                                                          │
│      ┌──────────────────────────────────────────────────────────┐       │
│      │                                                          │       │
│      │  1. LOCATE    →  Find current task in plan.md           │       │
│      │       │                                                  │       │
│      │       ▼                                                  │       │
│      │  2. EXECUTE   →  Run checklist items (delegate as       │       │
│      │       │           specified in item text)                │       │
│      │       ▼                                                  │       │
│      │  3. UPDATE    →  Mark items [x], call update-progress   │       │
│      │       │                                                  │       │
│      │       ▼                                                  │       │
│      │  4. NEXT      →  Move to next task or phase             │       │
│      │                                                          │       │
│      └──────────────────────────────────────────────────────────┘       │
│                                                                          │
│  NO BUSINESS LOGIC - just sequential execution of checklists.            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Phases Handled

| Phase | Typical Tasks |
|-------|---------------|
| implement | Code implementation, test creation |
| verify | Build verification, quality checks, documentation |
| finalize | Commit, PR creation, completion |
| execute | (simple plans) Combined implementation |

## Task Execution

### Reading Tasks

```
Read plan.md
Parse Phase Progress table
Find current phase (status: in_progress)
Find current task (first with unchecked items)
```

### Executing Checklist Items

For each `- [ ]` item:
1. **Parse** - Understand what action is needed
2. **Delegate** - If item specifies agent/skill/command, invoke it
3. **Execute** - Perform the action
4. **Update** - Mark item `[x]` via update-progress.py

### Progress Update

After each item completion:
```bash
python3 update-progress.py --plan-dir {dir} --phase {phase} --task-id {task} --complete-items "{item}"
```

## Phase Transition

When all tasks in phase complete:

1. **Automatic file collection** (implement/execute phases):
   - `transition-phase.py` runs `collect-modified-files.py`
   - Updates `references.toon` with changed files

2. **Auto-transition** to next phase:
   - implement → verify
   - verify → finalize
   - finalize → complete

3. **No user prompt** for transitions (continuous execution)

## Auto-Continue Rules

**Continue without prompting**:
- Task completion
- Phase transition
- Routine operations

**Stop and prompt when**:
- Error blocks progress
- Multiple valid approaches exist
- User explicitly requested confirmation

## Pre-Implemented Work

Before executing, check if deliverables already exist:
1. Verify files/components exist
2. Check acceptance criteria met
3. If pre-implemented: Still mark progress, then skip to next task
