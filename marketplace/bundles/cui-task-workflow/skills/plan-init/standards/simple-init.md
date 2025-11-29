# Simple Init Standards

**Output**: 3-phase plan (init→execute→finalize)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

## Phase Structure Template

When creating a simple plan, generate this structure:

```markdown
# Task Plan: {task_title}

**Configuration**: See [config.toon](./config.toon)
**References**: See [references.toon](./references.toon)

**Current Phase**: init
**Current Task**: task-1

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 0/2 |
| execute | pending | 0 | 0/0 |
| finalize | pending | 2 | 0/2 |

---

## Phase: init (in_progress)

### Task 1: Detect Environment

**Phase**: init
**Goal**: Gather basic information

**Acceptance Criteria**:
- Current branch identified
- Task scope understood

**Checklist**:
- [ ] Check current git branch
- [ ] Understand task scope
- [ ] Identify files to modify

### Task 2: Confirm Configuration

**Phase**: init
**Goal**: Quick confirmation of defaults

**Acceptance Criteria**:
- User has confirmed settings

**Checklist**:
- [ ] Display quick summary
- [ ] Confirm or edit settings
- [ ] Transition to execute phase

---

## Phase: execute (pending)

{Tasks generated from task description}

---

## Phase: finalize (pending)

### Task 1: Commit Changes

**Phase**: finalize
**Goal**: Commit all changes

**Acceptance Criteria**:
- All changes committed
- Commit message follows conventions

**Checklist**:
- [ ] Stage all changes
- [ ] Create commit with descriptive message
- [ ] Push to branch (if remote)

### Task 2: Verify Completion

**Phase**: finalize
**Goal**: Ensure task is complete

**Acceptance Criteria**:
- All acceptance criteria met

**Checklist**:
- [ ] Verify all changes applied
- [ ] Check no issues remaining
- [ ] Mark plan complete

---

## Completion Criteria

All phases must be completed and all tasks marked with `[x]` before plan is complete.
```

## Config Format (TOON)

```toon
# Plan Configuration

plan_type: simple
branch: {branch-name}
issue: none

technology: none
build_system: none

compatibility: breaking
commit_strategy: fine-granular
finalizing: commit-only
```

## References Template

```markdown
# References

## Context

**Branch**: `{branch}`

## Related Files

**Files to Modify**:
- (populated during execute phase)

## Notes

(add any relevant notes)
```

## Key Differences from Implementation

| Aspect | Implementation | Simple |
|--------|----------------|--------|
| Phases | 5 | 3 |
| Branch | Feature branch required | Any branch OK |
| Issue | Recommended | Not used |
| Build System | Auto-detected | None |
| PR Workflow | Yes | No |
| User Interaction | Full confirmation | Minimal |
| Total Tasks | ~18+ | ~6 |
