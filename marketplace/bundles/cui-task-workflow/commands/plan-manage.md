---
name: plan-manage
description: Manage task plans - list, create, refine, and cleanup persisted plans
tools: Read, Skill, Bash, AskUserQuestion
---

# Plan Manage Command

Manage plan lifecycle: list all plans, create new plans, refine requirements, and cleanup completed plans.

## PARAMETERS

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | optional | Explicit action: `list`, `cleanup`, `init`, `refine` (default: list) |
| `task` | optional | Task description for creating new plan |
| `issue` | optional | GitHub issue URL for creating new plan |
| `plan` | optional | Plan name for specific operations (e.g., `jwt-auth`, not path) |

**Note**: The `plan` parameter accepts the plan **name** only, not the full path. Paths are shown in displays for reference but not used as parameters.

## WORKFLOW

1. **Load phase-management skill**:
   ```
   Skill: cui-task-workflow:phase-management
   ```

2. **Execute Manage Plans workflow** with parameters:
   - `action`: Value of `action` parameter (default: list)
   - `task_description`: Value of `task` parameter (if provided)
   - `issue_url`: Value of `issue` parameter (if provided)
   - `plan_name`: Value of `plan` parameter (if provided)

The phase-management skill handles:
- Plan discovery and listing
- Cleanup of completed plans
- Init phase via plan-init skill
- Refine phase via plan-refine skill
- User interaction via AskUserQuestion

## ACTIONS

### list (default)

Display all plans with numbered selection.

```
/plan-manage
/plan-manage action=list
```

Shows:
```
Available Plans:

1. jwt-authentication [implement] - 3/12 tasks complete
   Path: .claude/plans/jwt-authentication/
2. user-profile-api [refine] - Requirements analysis
   Path: .claude/plans/user-profile-api/

0. Create new plan

Select plan (number) or action (c/n/q):
```

### init

Create a new plan.

```
/plan-manage action=init task="Implement JWT authentication"
/plan-manage action=init issue="https://github.com/org/repo/issues/123"
```

If init-phase plans exist, offers to continue existing or create new.

### refine

Refine requirements for a plan.

```
/plan-manage action=refine
/plan-manage action=refine plan="jwt-auth"
```

If no plan specified, shows plans in init/refine phase for selection.

### cleanup

Remove completed plans.

```
/plan-manage action=cleanup
```

Shows completed plans for selective or batch deletion with confirmation.

## USAGE EXAMPLES

```bash
# List all plans (interactive selection)
/plan-manage

# Create new plan from task description
/plan-manage action=init task="Add user authentication"

# Create new plan from GitHub issue
/plan-manage action=init issue="https://github.com/org/repo/issues/42"

# Refine specific plan
/plan-manage action=refine plan="user-auth"

# Refine (select from list)
/plan-manage action=refine

# Cleanup completed plans
/plan-manage action=cleanup
```

## RELATED

| Command | Relationship |
|---------|--------------|
| `/plan-execute` | Execute plans (implement/verify/finalize phases) |

| Skill | Purpose |
|-------|---------|
| `cui-task-workflow:phase-management` | Plan discovery, routing, workflows |
| `cui-task-workflow:plan-init` | Initialize new plans |
| `cui-task-workflow:plan-refine` | Requirements analysis and task planning |
