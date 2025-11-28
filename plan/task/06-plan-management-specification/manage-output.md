# User-Facing Output for Plan Management

This document defines output standards for plan management commands, focusing on what users see during plan orchestration.

## Core Principle

Users need progress visibility without implementation detail overload. Show status, not internal operations.

---

## Status Output Format

Display progress as structured summaries:

```
plan_status:
  current_phase: execute
  current_task: task-1
  init_completed: true

next_action: Execute analysis tasks (Task 1: Analyze task-implement.md)
```

---

## Phase Transition Messaging

When transitioning between phases, output should include:

1. **Completion Summary**: What was accomplished
2. **Artifacts Created**: Files/outputs produced
3. **Current State**: Where in the workflow
4. **Next Action**: Clear direction for continuation

Example:
```
Plan created successfully:

plan_type: simple
artifacts:
  plan_directory: .claude/plans/<plan-name>/
  plan_file: .claude/plans/<plan-name>/plan.md
  config_file: .claude/plans/<plan-name>/config.md
  references_file: .claude/plans/<plan-name>/references.md
plan_status:
  current_phase: init
  current_task: task-1
next_action: Complete init phase, then start execute phase
```

---

## Configuration Display

Show configuration summaries for user confirmation:

```
## Detected Configuration

**Plan Type**: simple (3-phase: init->execute->finalize)
**Branch**: <branch-name>
**Issue**: <issue-ref or none>
**Build System**: <detected or none>
**Technology**: <detected or none>

**Defaults Applied**:
- Compatibility: breaking
- Commit Strategy: fine-granular
- Finalizing: commit-only

Proceed with this configuration? (yes/no)
```

---

## Progress Table Format

Use tables for phase overview:

```markdown
| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| execute | in_progress | 5 | 1/5 |
| finalize | pending | 2 | 0/2 |
```

---

## Issue Detection Output

When problems occur, structure output clearly:

```
ISSUES DETECTED:
1. Interface mismatch in Operation type
   - Frontend: {userId: string, op: Transform}
   - Backend: {user_id: number, operation: Delta}
   FIX: Standardizing to {userId: string, operation: Transform}

2. Race condition in applyOperation()
   - Missing mutex on document.operations array
   FIX: Added operation queue with atomic processing
```

---

## Final Metrics Display

On completion, show measurable outcomes:

```
Final metrics:
- Latency: 47ms average (requirement: <100ms) OK
- Concurrent users: 100+ tested (requirement: 50+) OK
- Test coverage: 92% with 147 test cases OK
- Zero architectural drift from original spec OK
```

---

## Output by Phase Skill

| Skill | Output Focus |
|-------|--------------|
| plan-init | Configuration summary + plan artifacts location |
| plan-refine | Decomposition details + dependency graph |
| plan-implement | Progress updates + artifact references |
| plan-verify | Verification results + pass/fail status |
| plan-finalize | Completion summary + deliverables list |

---

## Key Principles

1. **Show status, not process** - Users care about progress, not internal operations
2. **Structured formats** - Consistent output enables scanning and tooling
3. **Clear next actions** - Always tell the user what happens next
4. **Measurable outcomes** - Final output should show quantifiable results
5. **Problem/fix pairing** - When issues occur, always pair with resolution
