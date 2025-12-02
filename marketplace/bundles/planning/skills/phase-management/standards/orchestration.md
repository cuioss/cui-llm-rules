# Orchestration Patterns

Standards for phase-management skill orchestration behavior.

## Core Principle

**Orchestration only** - This skill coordinates workflow execution but does NOT implement phase logic. All phase work is delegated to phase-specific skills.

## Skill Delegation Pattern

### Delegation Flow

```
phase-management (orchestrator)
        │
        ├─→ plan-files (persistence)
        │     └── read-plan, update-progress
        │
        └─→ phase skills (execution)
              ├── plan-init
              ├── plan-refine
              └── plan-execute (implement/verify/finalize/execute)
```

### Delegation Rules

1. **Read operations** → Use plan-files skill
2. **Write operations** → Use plan-files skill
3. **Phase execution** → Delegate to appropriate phase skill
4. **Never** implement phase logic directly

### Delegation Example

```markdown
# Correct: Delegate to plan-files
Skill: planning:plan-files
operation: read-plan
plan_directory: {path}

# Correct: Delegate to phase skill
Skill: planning:plan-execute
plan_directory: {path}

# Wrong: Direct file access
Read {plan_directory}/plan.md
```

## User Interaction Coordination

The phase-management skill coordinates user interaction but delegates prompts appropriately.

### Interaction Points

| Scenario | Skill Responsibility | Command Responsibility |
|----------|---------------------|------------------------|
| Multiple plans found | Return list | Ask user to select |
| Phase complete | Return next phase info | Ask to continue |
| Plan complete | Return summary | Display completion |
| Error | Return error details | Display and suggest |

### Prompt Delegation

Phase-management **returns data** for commands to prompt users:

```markdown
# phase-management returns:
plans_found[3]: {list}
recommendation: jwt-auth

# /plan-manage or /plan-execute command prompts:
"Multiple plans found. Select one to continue:
1. jwt-auth (implement phase, 3 tasks remaining) ← recommended
2. refactor-auth (verify phase, 4 tasks remaining)
3. add-logging (finalize phase, completed)

Enter selection (1-3):"
```

## Progress Tracking

### Status Aggregation

Aggregate status from multiple sources via plan-files skill:

```markdown
1. Read plan.md → current_phase, current_task, phase_progress
2. Read config.toon → plan_type, technology, build_system
3. Read references.toon → issue, adrs, interfaces

Combine into comprehensive status object.
```

### Progress Calculation

Use `get-status.py` script for deterministic progress calculation:

- Count completed tasks per phase
- Calculate overall percentage
- Determine phase completion status

## Execution Flow

### Standard Flow

```
1. Receive operation request
2. Run deterministic script (if applicable)
3. Delegate to appropriate skill
4. Collect results
5. Return structured response
```

### Operation-Specific Flows

**discover-plans**:
```
1. Run discover-plans.py
2. Return plan list with recommendation
```

**route-phase**:
```
1. Delegate read-plan to plan-files
2. Run route-phase.py with current state
3. Return routing decision
```

**transition-phase**:
```
1. Delegate read-plan to plan-files
2. Run transition-phase.py
3. If valid, delegate update-progress to plan-files
4. Return transition result
```

**get-status**:
```
1. Run get-status.py (aggregates from all files)
2. Return comprehensive status
```

## Error Propagation

### Error Handling Rules

1. **Script errors** → Wrap in structured error response
2. **Skill errors** → Propagate with context
3. **Validation errors** → Return with suggestions

### Error Response Format

```
error:
  type: {error_type}
  message: {human-readable message}
  context: {relevant state}

suggestion: {actionable next step}
```

## Quality Standards

- **No direct file I/O** - Always use plan-files skill
- **No phase logic** - Only orchestration and routing
- **Deterministic scripts** - Use Python scripts for calculations
- **Structured output** - All responses follow defined formats
- **Error context** - Include relevant state in errors
