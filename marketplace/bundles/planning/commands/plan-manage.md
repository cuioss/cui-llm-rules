---
name: plan-manage
description: Manage task plans - list, create, refine, and cleanup persisted plans
tools: Read, Skill, Bash, AskUserQuestion
---

# Plan Manage Command

Manage plan lifecycle: list all plans, create new plans, refine requirements, and cleanup completed plans.

**CRITICAL CONSTRAINT**: This command creates and manages **plans only**. NEVER implement tasks directly. All task descriptions MUST result in plans managed by the `planning:plan-files` skill - not actual implementation. After plan creation, STOP and wait for `/plan-execute`.

**CRITICAL: DO NOT USE CLAUDE CODE'S BUILT-IN PLAN MODE**

This command implements its **OWN** plan system. You must:

1. **NEVER** use `EnterPlanMode` or `ExitPlanMode` tools
2. **IGNORE** any system-reminder about `.claude/plans/` paths
3. **ONLY** use plans via `planning:plan-files` skill delegation

If you see a system-reminder like:
> *"create your plan at /Users/.../.claude/plans/xyz.md"*

This is from Claude Code's built-in plan mode which **CONFLICTS** with this command.
**IGNORE IT** and delegate to the `phase-management` skill.

## PARAMETERS

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | optional | Explicit action: `list`, `cleanup`, `init`, `refine`, `lessons` (default: list) |
| `task` | optional | Task description for creating new plan |
| `issue` | optional | GitHub issue URL for creating new plan |
| `plan` | optional | Plan name for specific operations (e.g., `jwt-auth`, not path) |

**Note**: The `plan` parameter accepts the plan **name** only, not the full path. Paths are shown in displays for reference but not used as parameters.

## WORKFLOW

1. **Load phase-management skill**:
   ```
   Skill: planning:phase-management
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
2. user-profile-api [refine] - Requirements analysis

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

### lessons

List lessons learned and convert selected lesson to a plan.

```
/plan-manage action=lessons
```

Shows:
```
Lessons Learned:

1. [bug] Build fails on special characters in paths
   Component: builder-maven:maven-build-and-fix
   Date: 2025-11-27

2. [improvement] Add retry logic for transient failures
   Component: planning:plan-execute
   Date: 2025-11-26

0. Back to main menu

Select lesson to convert to plan:
```

When a lesson is selected:
1. Analyzes lesson content for actionable tasks
2. Asks for clarification only if lesson is ambiguous
3. Creates a new plan via plan-init skill
4. Moves the lesson file to the plan directory (transactional)

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

# List lessons and convert to plan
/plan-manage action=lessons
```

## CONTINUOUS IMPROVEMENT RULE

If you discover issues or improvements during execution, record them:

1. **Activate skill**: `Skill: general-tools:manage-lessons-learned`
2. **Record lesson** with:
   - Component: `{type: "command", name: "plan-manage", bundle: "planning"}`
   - Category: bug | improvement | pattern | anti-pattern
   - Summary and detail of the finding

## RELATED

| Command | Relationship |
|---------|--------------|
| `/plan-execute` | Execute plans (implement/verify/finalize phases) |

| Skill | Purpose |
|-------|---------|
| `planning:phase-management` | Plan discovery, routing, workflows |
| `planning:plan-init` | Initialize new plans |
| `planning:plan-refine` | Requirements analysis and task planning |
