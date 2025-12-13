# Implementation Delegation Contract

Standard structure for task delegation blocks that enables plan-execute to invoke implement agents.

## Purpose

Task delegation blocks specify HOW a task should be executed. This contract defines:

1. **Agent Discovery** - How plan-execute finds the implement agent
2. **Parameter Mapping** - What parameters are passed to the agent
3. **Invocation Strategy** - Per-task invocation (not per-step)
4. **Return Handling** - How plan-execute interprets agent results

## Required Delegation Structure

All tasks with implementation work MUST include a delegation block:

```toon
delegation:
  agent: {bundle}:{implement-agent}
  domain: {domain}
  context_skills[N]:
    - {optional-skill-1}
    - {optional-skill-2}
```

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent` | string | Yes | Implement agent in `bundle:agent` format |
| `domain` | string | Yes | Domain for loading default skills |
| `context_skills` | array | No | Optional skills to load before execution |

## Agent Reference Format

Agent references use `{bundle}:{agent-name}` format:

```yaml
agent: pm-plugin-development:plugin-implement-agent
agent: pm-dev-java:java-implement-agent
agent: pm-dev-frontend:js-implement-agent
```

## Invocation Strategy

### Per-Task Invocation (Required)

Plan-execute invokes the implement agent **once per task**, not once per step:

```
Task:
  subagent_type: {delegation.agent}
  prompt: |
    Execute task {task_number} for plan {plan_id}

    plan_id: {plan_id}
    task_number: {task_number}
```

**Rationale**:
- Single context load (skills, domain defaults)
- Agent tracks step progress internally
- More efficient than N separate invocations

### Step Iteration

The implement agent iterates through steps internally:

```
steps[4]{number,title,status}:
1,path/to/file1.md,pending
2,path/to/file2.md,pending
3,path/to/file3.md,pending
4,path/to/file4.md,pending
```

Each step `title` is a file path. The agent:
1. Reads task details including steps
2. Loads domain + context skills
3. Iterates pending steps
4. Applies changes per step
5. Marks step complete
6. Returns aggregate result

## Domain Skill Loading

Before execution, the agent loads skills in order:

### 1. Domain Default Skills

Retrieved via config:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-defaults --domain {delegation.domain}
```

### 2. Context Skills

From delegation block:

```
Skill: {delegation.context_skills[0]}
Skill: {delegation.context_skills[1]}
```

### Loading Order

```
Domain Defaults → Context Skills → Execute Steps
```

## Plan-Execute Integration

### Reading Tasks

Plan-execute retrieves next task:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks next \
  --plan-id {plan_id} --include-context
```

### Checking Delegation

If task has `delegation.agent`:

```python
if task.delegation and task.delegation.agent:
    # Invoke implement agent
    invoke_agent(task.delegation.agent, plan_id, task.number)
else:
    # Execute steps directly (simple tasks)
    execute_steps_inline(task.steps)
```

### Invoking Agent

```
Task:
  subagent_type: {task.delegation.agent}
  prompt: |
    Execute task for plan.

    plan_id: {plan_id}
    task_number: {task.number}
```

### Handling Result

Agent returns structured TOON (see implement-agent-contract.md):

```toon
status: success
plan_id: my-plan
task_number: 3
execution_summary:
  steps_completed: 4
  steps_failed: 0
  verification_passed: true
```

Plan-execute actions based on result:

| Result | Plan-Execute Action |
|--------|---------------------|
| `status: success` | Mark task done, proceed to next |
| `status: error` + recoverable | Log error, offer retry |
| `status: error` + blocking | Stop, report to user |

## Validation Rules

| Rule | Description |
|------|-------------|
| Agent format | Must be `{bundle}:{agent}` |
| Domain required | Must specify valid domain |
| Agent exists | Bundle must contain the agent |
| Steps present | Task must have steps array |

## Domain-to-Agent Mapping

Each domain has a corresponding implement agent:

| Domain | Implement Agent |
|--------|-----------------|
| `plugin` | `pm-plugin-development:plugin-implement-agent` |
| `java` | `pm-dev-java:java-implement-agent` |
| `java-testing` | `pm-dev-java:java-implement-tests-agent` |
| `javascript` | `pm-dev-frontend:js-implement-agent` |
| `javascript-testing` | `pm-dev-frontend:js-implement-tests-agent` |

Task-plan agents use this mapping when creating tasks.

## Example Task with Delegation

```toon
number: 2
title: Add Error Handling to Plugin Commands
phase: execute
status: pending
deliverables: [1]
depends_on: none

description: Add standardized error handling blocks to plugin commands.

delegation:
  agent: pm-plugin-development:plugin-implement-agent
  domain: plugin
  context_skills[1]:
    - pm-plugin-development:plugin-architecture

steps[3]{number,title,status}:
1,marketplace/bundles/pm-plugin-development/commands/plugin-create.md,pending
2,marketplace/bundles/pm-plugin-development/commands/plugin-doctor.md,pending
3,marketplace/bundles/pm-plugin-development/commands/plugin-maintain.md,pending

verification:
  commands[1]:
    - /pm-plugin-development:plugin-doctor --bundle marketplace/bundles/pm-plugin-development
  criteria: No quality issues detected
```

## Integration

**Readers**:
- `plan-execute` skill → reads delegation block for agent invocation
- Task-plan agents → create tasks with proper delegation blocks

**Producers**:
- `java-task-plan-agent` → creates tasks with `java-implement-agent`
- `js-task-plan-agent` → creates tasks with `js-implement-agent`
- `plugin-task-plan-agent` → creates tasks with `plugin-implement-agent`

**Related**:
- [Implement Agent Contract](implement-agent-contract.md) - Agent input/output structure
- [Task Contract](task-contract.md) - Full task structure
