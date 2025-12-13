# Implement Agent Contract

Standard interface for implement agents that execute tasks from plans.

## Purpose

All implement agents MUST:

1. Accept standardized input (plan_id, task_number)
2. Load skills per delegation block
3. Iterate through steps
4. Track progress via manage-tasks
5. Return structured output

## Input Contract

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `plan_id` | string | Plan identifier |
| `task_number` | number | Task to execute |

### Prompt Format

```
Execute task for plan.

plan_id: {plan_id}
task_number: {task_number}
```

## Output Contract

### Success Output

```toon
status: success
plan_id: {plan_id}
task_number: {task_number}

execution_summary:
  steps_completed: {N}
  steps_total: {M}
  files_modified[N]:
    - {path1}
    - {path2}

verification:
  passed: true
  command: "{verification command used}"

next_action: task_complete
```

### Error Output

```toon
status: error
plan_id: {plan_id}
task_number: {task_number}

execution_summary:
  steps_completed: {N}
  steps_failed: {M}

failure:
  step: {step_number}
  file: "{file path}"
  error: "{error message}"
  recoverable: true|false

next_action: requires_attention
```

## Output Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success` or `error` |
| `plan_id` | string | Echo of input plan_id |
| `task_number` | number | Echo of input task_number |
| `execution_summary.steps_completed` | number | Steps successfully executed |
| `execution_summary.steps_total` | number | Total steps in task |
| `execution_summary.files_modified` | array | Paths of modified files |
| `verification.passed` | boolean | Whether verification succeeded |
| `verification.command` | string | Command used for verification |
| `failure.step` | number | Step number where failure occurred |
| `failure.error` | string | Error message |
| `failure.recoverable` | boolean | Whether retry might succeed |
| `next_action` | string | `task_complete` or `requires_attention` |

## Agent Workflow

All implement agents follow this workflow:

### Step 0: Load Foundation Skills

```
Skill: {domain-architecture-skill}
Skill: plan-marshall:general-development-rules
```

### Step 1: Load Implementation Skill

```
Skill: {domain-plan-implement-skill}
```

### Step 2: Delegate to Skill

Invoke the skill's `implement` workflow with:
- `plan_id`
- `task_number`

### Step 3: Return Structured Result

Return TOON output per this contract.

## Minimal Agent Wrapper Pattern

Implement agents SHOULD follow the minimal wrapper pattern:

```markdown
---
name: {domain}-implement-agent
description: Implement {domain} tasks from plan
tools: Read, Write, Edit, Bash, Skill
model: sonnet
skills: {domain}-plan-implement, plan-marshall:general-development-rules
---

# {Domain} Implement Agent

Minimal wrapper that loads {domain}-plan-implement skill and implements tasks.

## Step 0: Load Skills (MANDATORY)

```
Skill: {bundle}:{domain}-plan-implement
Skill: plan-marshall:general-development-rules
```

## Input

| Parameter | Type | Required |
|-----------|------|----------|
| `plan_id` | string | Yes |
| `task_number` | number | Yes |

## Workflow

After skills loaded, invoke:

```
operation: implement
plan_id: {plan_id}
task_number: {task_number}
```

## Return Results

Return the skill's output in TOON format per implement-agent-contract.
```

## Step Progress Tracking

Agents MUST track progress via manage-tasks:

### Mark Step Started

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks step-start \
  --plan-id {plan_id} --task {task_number} --step {step_number}
```

### Mark Step Done

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks step-done \
  --plan-id {plan_id} --task {task_number} --step {step_number}
```

### Log Progress

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "[STEP] Completed step {N}: {file_path}"
```

## Error Handling Requirements

### Skill Loading Failure

If skills fail to load:

```toon
status: error
error_type: skill_loading_failure
component: "{agent-name}"
message: "Failed to load skill: {skill_name}"
failure:
  recoverable: false
next_action: requires_attention
```

### Step Execution Failure

If a step fails:

1. Log the error to work-log
2. Do NOT mark step as done
3. Return error status with failure details
4. Set `recoverable: true` if retry might help

### Verification Failure

If verification fails:

1. Log verification failure
2. Return error status
3. Include which command failed
4. Set `recoverable: true` (fix and retry)

## Validation Rules

| Rule | Description |
|------|-------------|
| Input required | Both plan_id and task_number required |
| Status required | Output must include status field |
| Summary required | Output must include execution_summary |
| Progress tracked | All step transitions logged |

## Domain Implement Agents

| Domain | Agent | Implementation Skill |
|--------|-------|----------------------|
| `plugin` | `pm-plugin-development:plugin-plan-implement-agent` | `plugin-plan-implement` |
| `java` | `pm-dev-java:java-plan-implement-agent` | `java-plan-implement` |
| `javascript` | `pm-dev-frontend:js-plan-implement-agent` | `js-plan-implement` |

## Integration

**Callers**:
- `plan-execute` skill → invokes agent via Task tool
- `/plan-execute` command → orchestrates execution

**Dependencies**:
- `manage-tasks` → task retrieval and progress tracking
- `manage-log` → work log entries
- Domain implementation skills → actual implementation logic

**Related**:
- [Implementation Delegation Contract](implementation-delegation-contract.md) - How tasks specify delegation
- [Task Contract](task-contract.md) - Task structure including delegation block
