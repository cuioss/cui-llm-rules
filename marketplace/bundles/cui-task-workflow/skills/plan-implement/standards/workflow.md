# Plan Implement Workflow

## Phase Overview

The implement phase executes tasks and produces working code:

```
Plan from Refine Phase
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ IMPLEMENT PHASE                                     │
│                                                     │
│   1. Read context (plan, config, requirements)      │
│   2. Identify target task (respect dependencies)    │
│   3. Load task references                           │
│   4. Execute checklist items                        │
│   5. Delegate to language agents                    │
│   6. Verify acceptance criteria                     │
│   7. Update progress, commit per strategy           │
│   8. Transition to verify phase                     │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Verify Phase
```

## Operations Summary

| Operation | Description | Output |
|-----------|-------------|--------|
| **execute-tasks** | Execute tasks from plan | Updated plan with completed tasks |
| **delegate** | Route task to language agent | Agent completion report |
| **track-progress** | Update task/phase progress | Progress status |

## Task Execution Patterns

### Pattern 1: Sequential Chain

```
Task 1 (foundation)
    ↓
Task 2 (depends on 1)
    ↓
Task 3 (depends on 2)
```

Execute 1→2→3 in strict order.

### Pattern 2: Parallel Independent

```
Task 1 (foundation)
    ↓
    ├── Task 2 (independent)
    ├── Task 3 (independent)
    └── Task 4 (independent)
    ↓
Task 5 (depends on 2,3,4)
```

Task 1, then 2/3/4 in any order, then Task 5.

### Pattern 3: Iterative Refinement

```
Task 1 (initial implementation)
    ↓
Task 2 (add error handling)
    ↓
Task 3 (add edge cases)
```

Each task refines previous work.

## Language Agent Delegation

### Java Implementation

**Agent**: `cui-java-expert:java-implement-agent`

**Standard Checklist**:
```markdown
- [ ] Follow CUI Java coding standards
- [ ] Add JavaDoc to public methods
- [ ] Implement unit tests (JUnit 5)
- [ ] Verify build via maven-builder agent
- [ ] Check coverage ≥80%
```

### JavaScript Implementation

**Agent**: `builder:npm-builder`

**Standard Checklist**:
```markdown
- [ ] Follow CUI JavaScript standards
- [ ] Add JSDoc to exported functions
- [ ] Implement unit tests (Jest)
- [ ] Verify build via npm-builder agent
- [ ] Check coverage ≥80%
```

### Mixed Implementation

For tasks with both Java and JavaScript:
1. Identify components by technology
2. Delegate Java parts first
3. Delegate JavaScript parts
4. Coordinate integration
5. Verify both builds

## Progress Tracking

### Task Status

| Status | Indicator | Description |
|--------|-----------|-------------|
| Pending | `[ ]` | Not started |
| In Progress | `[ ]` with some `[x]` | Partially complete |
| Completed | `[x]` | All items done |
| Blocked | `[!]` | Cannot proceed |

### Checklist Item Types

| Type | Action | Tool |
|------|--------|------|
| `implement` | Write/Edit code | Edit, Write |
| `test` | Write/Edit tests | Edit, Write + Bash |
| `document` | Write/Edit docs | Edit, Write |
| `verify` | Run build/tests | Delegate to agent |
| `commit` | Git operations | Bash |

## Commit Strategy

| Strategy | When to Commit |
|----------|----------------|
| `fine-granular` | After each task |
| `phase-specific` | After implement phase |
| `complete` | Skip (commit in finalize) |
