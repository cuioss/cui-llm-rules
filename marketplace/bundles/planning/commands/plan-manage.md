---
name: plan-manage
description: Manage task plans - list, create, refine, and cleanup persisted plans
tools: Read, Skill, Bash, AskUserQuestion, Task
---

# Plan Manage Command

Manage plan lifecycle: list all plans, create new plans, refine requirements, and cleanup completed plans.

**CRITICAL CONSTRAINT**: This command creates and manages **plans only**. NEVER implement tasks directly. All task descriptions MUST result in plans - not actual implementation. After completing init AND refine phases, STOP and wait for `/plan-execute`.

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
| `stop-after-init` | optional | If true, stop after init phase without continuing to refine (default: false) |

**Note**: The `plan` parameter accepts the plan **name** (plan_id) only, not the full path.

## WORKFLOW

1. **Load manage-lifecycle skill**:
   ```
   Skill: planning:manage-lifecycle
   ```

2. **Route based on action**:
   - `list` → List all plans via manage-lifecycle
   - `cleanup` → Remove completed plans
   - `init` → Run init phase, then **automatically continue to refine** (unless `stop-after-init=true`)
   - `refine` → Run refine phase only

### Init Phase

The init phase uses a single agent:

```
Task: planning:plan-init-agent
  Input: description OR issue OR lesson_id
  Output: plan_id, goals summary
```

**plan-init-agent**: Creates plan directory, writes request.md, analyzes task, creates goals, configures plan type

### Automatic Continuation to Refine

After init phase completes successfully:
1. **Check** `stop-after-init` parameter
2. **If false (default)**: Automatically invoke refine phase with the new plan_id
3. **If true**: Stop and display plan summary

This provides a seamless flow from task description to actionable tasks in a single command invocation.

### Refine Phase

The refine phase uses **skill-based routing**: load the plan-type skill and invoke its documented domain agents directly.

**Step 1**: Get plan_type from config:
```bash
python3 .plan/execute-script.py planning:manage-config:manage-config get \
  --plan-id {plan_id} --field plan_type
```

**Step 2**: Load the plan-type skill:
```
Skill: {plan_type}
```
Example: `Skill: planning:plan-type-java`

The skill's `domain:` frontmatter contains:
```yaml
domain:
  solution_outline_agent: cui-java-expert:java-solution-outline-agent
  task_plan_agent: cui-java-expert:java-task-plan-agent
  verification_command: /builder:builder-build-and-fix
  pr_workflow: true
```

**Step 3**: Route based on skill.domain:

**If domain.solution_outline_agent is NOT null** (domain-specific plan type):
```
Task: {domain.solution_outline_agent}
  Input: plan_id={plan_id}
  Output: goals created

Task: {domain.task_plan_agent}
  Input: plan_id={plan_id}
  Output: tasks created
```

Log each domain agent invocation:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Invoked {agent_name}" \
  --detail "Domain agent from skill frontmatter"
```

**If domain.solution_outline_agent IS null** (generic plan type):
```
Task: planning:plan-refine-agent
  Input: plan_id
  Output: tasks count
```

**Refine agent**: Fallback for generic plans without domain-specific agents

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

Create a new plan and automatically continue to refine phase.

```
/plan-manage action=init task="Implement JWT authentication"
/plan-manage action=init issue="https://github.com/org/repo/issues/123"
/plan-manage action=init task="Add feature" stop-after-init=true
```

**Default behavior**: After init completes, automatically runs refine phase to create tasks from goals. The command completes when the plan is ready for `/plan-execute`.

**With `stop-after-init=true`**: Stops after init phase, useful when you want to review/edit goals before refining.

If init-phase plans exist, offers to continue existing or create new.

### refine

Create tasks from goals for a plan. Uses skill-based domain agent routing.

```
/plan-manage action=refine
/plan-manage action=refine plan="jwt-auth"
```

**Routing**: Loads plan-type skill and reads `domain:` frontmatter. For domain-specific types (Java, JavaScript, Plugin), invokes goals and plan agents from skill. For generic types, falls back to plan-refine-agent.

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

# Create new plan from task description (auto-continues to refine)
/plan-manage action=init task="Add user authentication"

# Create new plan from GitHub issue (auto-continues to refine)
/plan-manage action=init issue="https://github.com/org/repo/issues/42"

# Create plan but stop after init (to review goals first)
/plan-manage action=init task="Complex feature" stop-after-init=true

# Refine specific plan (if stopped after init or needs re-refining)
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
| `/plan-marshall` | Configure project-level planning settings |

| Skill | Purpose |
|-------|---------|
| `planning:manage-lifecycle` | Plan discovery, phase routing, transitions |
| `planning:plan-init` | Initialize new plans (creates request.md, goals, config) |
| `planning:plan-refine` | Transform goals to tasks (fallback for generic plans) |
| `planning:plan-type-java` | Java domain config (provides domain agents in frontmatter) |
| `planning:plan-type-javascript` | JavaScript domain config |
| `planning:plan-type-plugin` | Plugin domain config |
| `planning:plan-type-generic` | Generic config (no domain agents) |

| Script | Purpose |
|--------|---------|
| `planning:manage-config:manage-config` | Plan config field access |
| `planning:manage-log:manage-work-log` | Work log entries |

| Agent | Purpose |
|-------|---------|
| `planning:plan-init-agent` | Init phase execution |
| `planning:plan-refine-agent` | Refine phase fallback (generic plans) |
| `cui-java-expert:java-solution-outline-agent` | Java: Request → Goals |
| `cui-java-expert:java-task-plan-agent` | Java: Goals → Tasks |
| `cui-frontend-expert:js-solution-outline-agent` | JavaScript: Request → Goals |
| `cui-frontend-expert:js-task-plan-agent` | JavaScript: Goals → Tasks |
| `cui-plugin-development-tools:plugin-solution-outline-agent` | Plugin: Request → Goals |
| `cui-plugin-development-tools:plugin-task-plan-agent` | Plugin: Goals → Tasks |
