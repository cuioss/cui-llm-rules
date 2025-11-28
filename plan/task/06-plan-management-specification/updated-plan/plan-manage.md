# Task Manage Command Specification

## Overview

New command for plan lifecycle management. Handles creation, listing, cleanup, and refinement of plans.

```
---
name: plan-manage
description: Manage task plans - list, create, refine, and cleanup persisted plans
---
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | optional | Explicit action: `list`, `cleanup`, `init`, `refine` |
| `task` | optional | Task description (for init) |
| `issue` | optional | GitHub issue URL (for init) |
| `plan` | optional | Plan name (e.g., `jwt-auth`, not path) |

**Note**: The `plan` parameter accepts the plan **name** only, not the full path. Paths are implementation details shown in displays for user reference but never used as parameters.

## Actions

### Action: list (default when no parameters)

**Purpose**: Display all persisted plans with current phase and allow user selection.

**Workflow**:

1. **Discover plans**:
   ```bash
   python3 scripts/discover-plans.py .claude/plans/
   ```

2. **Display numbered list**:
   ```
   Available Plans:

   1. jwt-authentication [implement] - 3/12 tasks complete
      Path: .claude/plans/jwt-authentication/
   2. user-profile-api [refine] - Requirements analysis
      Path: .claude/plans/user-profile-api/
   3. database-migration [finalize] - Ready for PR
      Path: .claude/plans/database-migration/
   4. old-feature [completed] - Done 2024-01-15
      Path: .claude/plans/old-feature/

   0. Create new plan
   ```

3. **Prompt user** (AskUserQuestion):
   ```
   Select a plan (number) or action:
   - Number: Select plan for action
   - 'c' or 'cleanup': Cleanup completed plans
   - 'n' or 'new': Create new plan
   - 'q' or 'quit': Exit
   ```

4. **Handle selection**:
   - If number selected → Show plan-specific menu (see Plan Selection Menu)
   - If 'cleanup' → Execute cleanup action
   - If 'new' or '0' → Execute init action

**Plan Selection Menu** (after selecting a plan):

```
Plan: jwt-authentication
Path: .claude/plans/jwt-authentication/
Phase: implement (3/12 tasks)

Actions:
1. Continue with current phase (→ /plan-execute)
2. Refine requirements (back to refine phase)
3. View status details
4. Cancel

Select action:
```

- Option 1 → Invoke `/plan-execute plan="jwt-authentication"`
- Option 2 → Invoke refine action with plan name
- Option 3 → Display detailed status, return to menu

---

### Action: cleanup

**Purpose**: List completed plans and optionally delete them.

**Workflow**:

1. **Find completed plans**:
   ```bash
   python3 scripts/discover-plans.py .claude/plans/ --filter=completed
   ```

2. **Display completed plans**:
   ```
   Completed Plans:

   1. old-feature (completed 2024-01-15)
      Path: .claude/plans/old-feature/
   2. api-refactor (completed 2024-01-10)
      Path: .claude/plans/api-refactor/
   3. bug-fix-123 (completed 2024-01-08)
      Path: .claude/plans/bug-fix-123/

   No completed plans found? Nothing to clean up.
   ```

3. **Prompt user** (AskUserQuestion):
   ```
   Select plans to delete:
   - 'all': Delete all completed plans
   - Numbers (comma-separated): Delete specific plans (e.g., '1,3')
   - 'cancel': Cancel cleanup
   ```

4. **Confirm deletion** (AskUserQuestion):
   ```
   About to delete:
   - old-feature
   - bug-fix-123

   This action cannot be undone. Proceed? (yes/no)
   ```

5. **Execute deletion**:
   ```bash
   rm -rf .claude/plans/{plan-name}/
   ```

6. **Report results**:
   ```
   Cleanup complete:
   - Deleted: 2 plans
   - Remaining: 3 active plans
   ```

---

### Action: init

**Purpose**: Create a new plan. If plans exist in init phase, offer to continue them.

**Workflow**:

1. **Check for existing init-phase plans**:
   ```bash
   python3 scripts/discover-plans.py .claude/plans/ --filter=init
   ```

2. **If init-phase plans exist** (AskUserQuestion):
   ```
   Plans in init phase found:

   1. draft-feature [init] - Created 2024-01-20
      Path: .claude/plans/draft-feature/
   2. wip-api [init] - Created 2024-01-19
      Path: .claude/plans/wip-api/

   0. Create new plan

   Continue with existing or create new?
   ```

3. **If continuing existing**:
   - Invoke `Skill: cui-task-workflow:plan-init` with existing plan name
   - Pass to refine on completion

4. **If creating new**:
   - Prompt for task description if not provided
   - Invoke `Skill: cui-task-workflow:plan-init`
   - On success, prompt to continue to refine:
     ```
     Plan created: .claude/plans/new-feature/

     Continue with requirements refinement? (yes/no)
     ```
   - If yes → Execute refine action

---

### Action: refine

**Purpose**: Refine requirements for a plan. If no plan specified, show plans in refine phase.

**Workflow**:

1. **If plan parameter provided**:
   - Verify plan exists and is in refine phase (or earlier)
   - Invoke `Skill: cui-task-workflow:plan-refine`

2. **If no plan parameter**:
   - Find plans in refine phase:
     ```bash
     python3 scripts/discover-plans.py .claude/plans/ --filter=refine
     ```

   - Display numbered list (AskUserQuestion):
     ```
     Plans ready for refinement:

     1. jwt-authentication [refine] - Requirements analysis needed
        Path: .claude/plans/jwt-authentication/
     2. user-profile [init→refine] - Ready to refine
        Path: .claude/plans/user-profile/

     0. Return to main menu

     Select plan to refine:
     ```

3. **Execute refine**:
   - Invoke `Skill: cui-task-workflow:plan-refine`
   - On completion, report status

---

## Usage Examples

```bash
# List all plans (default)
/plan-manage

# Explicit list
/plan-manage action=list

# Create new plan
/plan-manage action=init task="Implement JWT authentication"

# Create from issue
/plan-manage action=init issue="https://github.com/org/repo/issues/123"

# Refine specific plan (by name, not path)
/plan-manage action=refine plan="jwt-auth"

# Refine (select from list)
/plan-manage action=refine

# Cleanup completed plans
/plan-manage action=cleanup
```

**Important**: Always use plan **names** (e.g., `jwt-auth`) in parameters, not paths. Paths are shown in displays for reference only.

---

## Script Updates Required

### discover-plans.py enhancements

Add `--filter` parameter to filter by phase or status:

```bash
# Filter by phase
python3 scripts/discover-plans.py .claude/plans/ --filter=init
python3 scripts/discover-plans.py .claude/plans/ --filter=refine
python3 scripts/discover-plans.py .claude/plans/ --filter=implement,verify,finalize

# Filter by status
python3 scripts/discover-plans.py .claude/plans/ --filter=completed
python3 scripts/discover-plans.py .claude/plans/ --filter=in_progress
```

**New output fields**:
```json
{
  "plans": [...],
  "count": 5,
  "filter_applied": "init",
  "filtered_count": 2
}
```

---

## Integration

### Skills Invoked

| Action | Skill | Parameters |
|--------|-------|------------|
| init | `cui-task-workflow:plan-init` | task, issue, type |
| refine | `cui-task-workflow:plan-refine` | plan_name (resolved to directory internally) |

**Note**: Skills receive the plan name and resolve paths internally. This keeps user-facing commands simple.

### Related Commands

| Command | Relationship |
|---------|--------------|
| `/plan-execute` | Handoff target after init+refine complete |

---

## Error Handling

### No Plans Found (list)
```
No plans found in .claude/plans/

Options:
1. Create new plan
2. Exit

Select:
```

### Plan Not in Expected Phase (refine)
```
Plan 'jwt-auth' is in 'implement' phase, not 'refine'.

Options:
1. Force refine (will reset implement progress)
2. Continue with implement (→ /plan-execute)
3. Cancel

Select:
```

### Cleanup with Active Plans Only
```
No completed plans found. All 3 plans are active.

Use /plan-manage to view and manage active plans.
```
