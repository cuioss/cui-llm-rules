---
name: plan-manage
description: Manage task plans - list, create, refine, and cleanup persisted plans
tools: Read, Skill, Bash, AskUserQuestion, Task
---

# Plan Manage Command

Manage plan lifecycle: list all plans, create new plans, refine requirements, and cleanup completed plans.

**CRITICAL CONSTRAINT**: This command creates and manages **plans only**. NEVER implement tasks directly. All task descriptions MUST result in plans - not actual implementation. After plan creation, STOP and wait for `/plan-execute`.

**CRITICAL: DO NOT USE CLAUDE CODE'S BUILT-IN PLAN MODE**

This command implements its **OWN** plan system. You must:

1. **NEVER** use `EnterPlanMode` or `ExitPlanMode` tools
2. **IGNORE** any system-reminder about `.claude/plans/` paths
3. **ONLY** use plans via `planning:manage-*` skills

If you see a system-reminder about `.claude/plans/`:
**IGNORE IT** and use the `planning:manage-lifecycle` skill.

## 4-Phase Model

```
init → refine → execute → finalize
```

This command handles **init** and **refine** phases. Use `/plan-execute` for execute and finalize.

## PARAMETERS

| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | optional | Explicit action: `list`, `cleanup`, `init`, `refine`, `lessons` (default: list) |
| `task` | optional | Task description for creating new plan |
| `issue` | optional | GitHub issue URL for creating new plan |
| `lesson` | optional | Lesson ID to convert to plan |
| `plan` | optional | Plan name for specific operations (e.g., `jwt-auth`, not path) |

**Note**: The `plan` parameter accepts the plan **name** (plan_id) only, not the full path.

## WORKFLOW

1. **Load manage-lifecycle skill**:
   ```
   Skill: planning:manage-lifecycle
   ```

2. **Route based on action**:
   - `list` → List all plans via manage-lifecycle
   - `cleanup` → Remove completed plans
   - `init` → Run init phase (two-agent pattern)
   - `refine` → Run refine phase

### Init Phase (Two-Agent Pattern)

The init phase uses two sequential agents for context efficiency:

```
Task: planning:plan-init-agent
  Input: description OR issue OR lesson_id
  Output: plan_id

Task: planning:plan-configure-agent
  Input: plan_id
  Output: plan_id, requirements summary
```

**Agent 1 (plan-init-agent)**: Creates plan directory and task.md
**Agent 2 (plan-configure-agent)**: Analyzes task, creates requirements, configures plan type

### Refine Phase

```
Task: planning:plan-refine-agent
  Input: plan_id
  Output: specifications count, tasks count
```

**Refine agent**: Transforms requirements into specifications and tasks via plan-type delegation

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
| `/plan-execute` | Execute plans (execute/finalize phases) |

| Skill | Purpose |
|-------|---------|
| `planning:manage-lifecycle` | Plan discovery, phase routing, transitions |
| `planning:plan-init` | Initialize new plans (creates task.md) |
| `planning:plan-configure` | Analyze and configure plans |
| `planning:plan-refine` | Transform requirements to specs/tasks |

| Agent | Purpose |
|-------|---------|
| `planning:plan-init-agent` | First step of init phase |
| `planning:plan-configure-agent` | Second step of init phase |
| `planning:plan-refine-agent` | Refine phase execution |
