# Task Execute Command Specification

## Overview

Refactored command for plan execution. Handles implementation, verification, and finalization phases only.

```
---
name: plan-execute
description: Execute task plans - implement, verify, and finalize phases
---
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `plan` | optional | Plan name (e.g., `jwt-auth`, not path) |
| `phase` | optional | Force specific phase: `implement`, `verify`, `finalize` |

**Note**: The `plan` parameter accepts the plan **name** only, not the full path. Paths are implementation details shown in displays for user reference but never used as parameters.

## Behavior

### Default (no parameters)

When called without parameters, presents executable plans for user selection.

**Workflow**:

1. **Discover executable plans** (phases: implement, verify, finalize):
   ```bash
   python3 scripts/discover-plans.py .claude/plans/ --filter=implement,verify,finalize
   ```

2. **Display numbered list** (AskUserQuestion):
   ```
   Executable Plans:

   1. jwt-authentication [implement] - Task 3/12: "Add token validation"
      Path: .claude/plans/jwt-authentication/
   2. user-profile-api [verify] - Build verification pending
      Path: .claude/plans/user-profile-api/
   3. database-migration [finalize] - Ready for commit and PR
      Path: .claude/plans/database-migration/

   0. Exit (use /plan-manage to create or refine plans)

   Select plan to continue:
   ```

3. **On selection**:
   - Load selected plan
   - Execute appropriate phase skill
   - Continue workflow (see Phase Execution)

### With plan parameter

Directly execute the specified plan from its current phase.

**Workflow**:

1. **Validate plan**:
   - Verify plan exists
   - Read current phase
   - Verify phase is executable (implement, verify, or finalize)

2. **If phase is init or refine**:
   ```
   Plan 'jwt-auth' is in '{phase}' phase.

   This command handles execution phases only (implement, verify, finalize).
   Use /plan-manage to complete init/refine phases first.
   ```

3. **If phase is executable**:
   - Execute phase skill (see Phase Execution)

### With phase override

Force execution of a specific phase (with validation).

**Workflow**:

1. **Validate override**:
   - Phase must be implement, verify, or finalize
   - Phase must be reachable from current state

2. **If invalid override**:
   ```
   Cannot execute '{requested}' phase.

   Current phase: {current}
   Valid targets: {list of valid phases}

   Select valid phase or continue with current.
   ```

---

## Phase Execution

### Implement Phase

**Entry**: Plan is in `implement` phase with tasks defined.

**Workflow**:

1. **Get current task**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-plan
   ```

2. **Display task context**:
   ```
   Implementing: jwt-authentication
   Current Task: task-3 - "Add token validation"

   Progress: 2/12 tasks complete
   ```

3. **Execute**:
   ```
   Skill: cui-task-workflow:plan-implement
   plan_directory: {path}
   ```

4. **Handle completion**:
   - If task complete → Update progress, get next task
   - If all tasks complete → Transition to verify phase
   - Prompt: "Continue with next task? (yes/no)"

### Verify Phase

**Entry**: Plan is in `verify` phase.

**Workflow**:

1. **Display context**:
   ```
   Verifying: jwt-authentication

   Verification Steps:
   1. Build project
   2. Run tests
   3. Quality checks
   4. Documentation review
   ```

2. **Execute**:
   ```
   Skill: cui-task-workflow:plan-verify
   plan_directory: {path}
   ```

3. **Handle completion**:
   - If all checks pass → Transition to finalize phase
   - If checks fail → Report failures, offer retry
   - Prompt: "Continue with finalize phase? (yes/no)"

### Finalize Phase

**Entry**: Plan is in `finalize` phase.

**Workflow**:

1. **Display context**:
   ```
   Finalizing: jwt-authentication

   Actions:
   1. Commit changes
   2. Create/update PR
   3. Handle PR workflow
   ```

2. **Execute**:
   ```
   Skill: cui-task-workflow:plan-finalize
   plan_directory: {path}
   ```

3. **Handle completion**:
   - Mark plan as completed
   - Display summary with PR link
   - Suggest cleanup via `/plan-manage`

---

## Usage Examples

```bash
# Select from executable plans
/plan-execute

# Execute specific plan (by name, not path)
/plan-execute plan="jwt-auth"

# Force verify phase
/plan-execute plan="jwt-auth" phase="verify"

# Resume implementation
/plan-execute plan="jwt-auth" phase="implement"
```

**Important**: Always use plan **names** (e.g., `jwt-auth`) in parameters, not paths. Paths are shown in displays for reference only.

---

## Stripped Functionality

The following functionality is **removed** from this command (moved to `/plan-manage`):

| Removed | Moved To |
|---------|----------|
| Create new plan | `/plan-manage action=init` |
| List all plans | `/plan-manage action=list` |
| Refine requirements | `/plan-manage action=refine` |
| Cleanup completed | `/plan-manage action=cleanup` |
| Init phase handling | `/plan-manage action=init` |
| Refine phase handling | `/plan-manage action=refine` |

---

## Integration

### Skills Invoked

| Phase | Skill | Parameters |
|-------|-------|------------|
| implement | `cui-task-workflow:plan-implement` | plan_name (resolved to directory internally) |
| verify | `cui-task-workflow:plan-verify` | plan_name (resolved to directory internally) |
| finalize | `cui-task-workflow:plan-finalize` | plan_name (resolved to directory internally) |

**Note**: Skills receive the plan name and resolve paths internally. This keeps user-facing commands simple.

### Related Commands

| Command | Relationship |
|---------|--------------|
| `/plan-manage` | Use for init, refine, list, cleanup |

---

## Workflow Diagram

```
/plan-execute (no params)
    │
    ▼
┌─────────────────────┐
│ Discover Plans      │
│ (implement/verify/  │
│  finalize phases)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Display Numbered    │
│ List + AskUser      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Load Selected Plan  │
└──────────┬──────────┘
           │
    ┌──────┴──────┬────────────┐
    ▼             ▼            ▼
implement      verify      finalize
    │             │            │
    ▼             ▼            ▼
plan-implement plan-verify plan-finalize
    │             │            │
    └──────┬──────┴────────────┘
           │
           ▼
┌─────────────────────┐
│ Phase Transition    │
│ or Completion       │
└─────────────────────┘
```

---

## Error Handling

### No Executable Plans

```
No plans ready for execution.

All plans are in init/refine phases or completed.

Options:
- Use /plan-manage to create or refine plans
- Use /plan-manage action=list to view all plans
```

### Plan Not Found

```
Plan not found: nonexistent

Use /plan-manage to list available plans.
```

### Invalid Phase Override

```
Cannot skip to 'finalize' phase.

Current phase: implement
Pending tasks: 8 of 12

Complete implementation tasks first or use phase='verify' after implementation.
```

### Build/Verify Failures

```
Verification failed:

✗ Build: 2 compilation errors
✓ Tests: Passed (could not run due to build failure)
- Quality: Skipped
- Docs: Skipped

Options:
1. View error details
2. Return to implement phase (fix issues)
3. Exit

Select:
```
