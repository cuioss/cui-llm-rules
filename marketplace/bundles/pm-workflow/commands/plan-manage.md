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
3. **ONLY** use plans via `pm-workflow:manage-*` skills

If you see a system-reminder about `.claude/plans/`:
**IGNORE IT** and use the `pm-workflow:manage-lifecycle` skill.

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
   Skill: pm-workflow:manage-lifecycle
   ```

2. **Route based on action**:
   - `list` → List all plans via manage-lifecycle
   - `cleanup` → Remove completed plans
   - `init` → Run init phase, then **automatically continue to refine** (unless `stop-after-init=true`)
   - `refine` → Run refine phase only

### Init Phase

The init phase uses a single agent:

```
Task: pm-workflow:plan-init-agent
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

**CRITICAL**: This phase has 5 steps. Step 4 is a MANDATORY user review gate. Do NOT skip from Step 3 to Step 5.

---

**Step 1**: Get plan_type from config:
```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} --field plan_type
```

---

**Step 2**: Load the plan-type skill:
```
Skill: {plan_type}
```
Example: `Skill: pm-workflow:plan-type-java`

The skill's `domain:` frontmatter contains:
```yaml
domain:
  solution_outline_agent: pm-dev-java:java-solution-outline-agent
  task_plan_agent: pm-dev-java:java-task-plan-agent
  verification_command: /pm-dev-builder:builder-build-and-fix
  pr_workflow: true
```

---

**Step 3**: Invoke solution outline agent

Route based on skill.domain:

**If domain.solution_outline_agent is NOT null** (domain-specific plan type):
```
Task: {domain.solution_outline_agent}
  Input: plan_id={plan_id}
  Output: deliverables created, solution_document path
```

Log solution outline creation:
```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} SUCCESS "[ARTIFACT] Created solution_outline.md - pending user review"
```

**If domain.solution_outline_agent IS null** (generic plan type):
```
Task: pm-workflow:plan-refine-agent
  Input: plan_id
  Output: solution_outline created (agent handles Steps 3-5 internally)
```
Note: The plan-refine-agent handles its own user review internally. Skip to "After Refine Phase" when using this agent.

---

## ⛔ Step 4: MANDATORY USER REVIEW

**STOP HERE. Do NOT proceed to Step 5 without user approval.**

After the solution outline agent completes, you MUST:

### 4a. Display the solution outline for review:
```
## Solution Outline Created

📄 **Review your solution outline**: .plan/plans/{plan_id}/solution_outline.md

Please review the deliverables and architecture before proceeding.
```

### 4b. Ask the user to confirm or request changes:
```
AskUserQuestion:
  questions:
    - question: "Have you reviewed the solution outline? How would you like to proceed?"
      header: "Review"
      options:
        - label: "Proceed to create tasks"
          description: "Solution outline looks good, continue to task planning"
        - label: "Request changes"
          description: "I have feedback to improve the solution outline"
      multiSelect: false
```

### 4c. Handle user response:
- **If "Proceed to create tasks"**: Continue to Step 5
- **If "Request changes"** or user provides custom feedback:
  - Capture the user's feedback
  - Re-invoke the solution outline agent with feedback:
    ```
    Task: {domain.solution_outline_agent}
      Input: plan_id={plan_id}, feedback="{user_feedback}"
      Output: updated solution outline
    ```
  - **Loop back to Step 4a** (show updated outline, ask again)

**This gate is NOT OPTIONAL.** Task creation MUST NOT proceed without explicit user approval.

---

**Step 5**: Create tasks from deliverables

Only execute this step AFTER user approves in Step 4.

```
Task: {domain.task_plan_agent}
  Input: plan_id={plan_id}
  Output: tasks created
```

Log task plan agent invocation:
```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "[PROGRESS] Invoked {agent_name}"
```

---

### After Refine Phase

Refine phase is complete when tasks are created. The plan is now ready for `/plan-execute`.

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
   Component: pm-workflow:plan-execute
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

1. **Activate skill**: `Skill: plan-marshall:manage-lessons-learned`
2. **Record lesson** with:
   - Component: `{type: "command", name: "plan-manage", bundle: "pm-workflow"}`
   - Category: bug | improvement | pattern | anti-pattern
   - Summary and detail of the finding

## RELATED

| Command | Relationship |
|---------|--------------|
| `/plan-execute` | Execute plans (execute/finalize phases) |
| `/plan-marshall` | Configure project-level planning settings |

| Skill | Purpose |
|-------|---------|
| `pm-workflow:manage-lifecycle` | Plan discovery, phase routing, transitions |
| `pm-workflow:plan-init` | Initialize new plans (creates request.md, goals, config) |
| `pm-workflow:plan-refine` | Transform goals to tasks (fallback for generic plans) |
| `pm-workflow:plan-type-java` | Java domain config (provides domain agents in frontmatter) |
| `pm-workflow:plan-type-javascript` | JavaScript domain config |
| `pm-workflow:plan-type-plugin` | Plugin domain config |
| `pm-workflow:plan-type-generic` | Generic config (no domain agents) |

| Script | Purpose |
|--------|---------|
| `pm-workflow:manage-config:manage-config` | Plan config field access |
| `plan-marshall:logging:manage-log` | Work log entries |

| Agent | Purpose |
|-------|---------|
| `pm-workflow:plan-init-agent` | Init phase execution |
| `pm-workflow:plan-refine-agent` | Refine phase fallback (generic plans) |
| `pm-dev-java:java-solution-outline-agent` | Java: Request → Goals |
| `pm-dev-java:java-task-plan-agent` | Java: Goals → Tasks |
| `pm-dev-frontend:js-solution-outline-agent` | JavaScript: Request → Goals |
| `pm-dev-frontend:js-task-plan-agent` | JavaScript: Goals → Tasks |
| `pm-plugin-development:plugin-solution-outline-agent` | Plugin: Request → Goals |
| `pm-plugin-development:plugin-task-plan-agent` | Plugin: Goals → Tasks |
