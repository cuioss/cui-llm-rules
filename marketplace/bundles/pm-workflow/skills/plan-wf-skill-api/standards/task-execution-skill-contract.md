# Task Execution Skill Contract

Standard interface for task execution skills that implement tasks from plans using two-tier skill loading.

## Purpose

Task execution skills:

1. Accept standardized input (plan_id, task_number)
2. Load workflow skill based on task.profile
3. Load domain skills from task.skills array (two-tier loading)
4. Iterate through steps
5. Track progress via manage-tasks
6. Return structured output

## Two-Tier Skill Loading

Task execution uses a two-tier skill loading pattern:

| Tier | Source | Purpose | Loaded By |
|------|--------|---------|-----------|
| **Tier 1** | Agent frontmatter | System skills (architecture, rules) | Agent automatically |
| **Tier 2** | `task.skills` array | Domain-specific skills | Agent from task file |

### Example Task with Skills

```toon
id: TASK-1
title: "Create CacheConfig class"
domain: java
profile: implementation
skills:
  - pm-dev-java:java-core
  - pm-dev-java:java-cdi
deliverables: [1]
...
```

The `task-execute-agent` will:
1. Load system skills from its frontmatter (Tier 1)
2. Load `pm-dev-java:java-core` and `pm-dev-java:java-cdi` (Tier 2)

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

The `task-execute-agent` follows this workflow:

### Step 0: Read Task

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks get \
  --plan-id {plan_id} --task {task_number}
```

Extract:
- `task.domain`
- `task.profile`
- `task.skills` (array)

### Step 1: Load Workflow Skill

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} --field workflow_skills
```

Then load: `config.workflow_skills.{task.domain}.{task.profile}`

### Step 2: Load Domain Skills (Tier 2)

For each skill in `task.skills`:
```
Skill: {skill_name}
```

### Step 3: Execute Implementation

Invoke the workflow skill's implementation workflow with:
- `plan_id`
- `task_number`

### Step 4: Return Structured Result

Return TOON output per this contract.

## Thin Agent Pattern

The `task-execute-agent` is a minimal wrapper:

```markdown
---
name: task-execute-agent
description: Execute single task with two-tier skill loading
tools: Read, Write, Edit, Bash, Skill
model: sonnet
skills: pm-workflow:task-execution, plan-marshall:general-development-rules
---

# Task Execute Agent

Thin agent that executes a single task. Loads workflow skill based on task.profile,
then loads task.skills array for domain knowledge.

## Step 0: Load System Skills (MANDATORY)

```
Skill: pm-workflow:task-execution
Skill: plan-marshall:general-development-rules
```

## Workflow

1. Read task via manage-tasks
2. Load workflow skill from config.workflow_skills.{domain}.{profile}
3. Load each skill from task.skills array
4. Execute skill's implement workflow
5. Return structured TOON output
```

## Step Progress Tracking

Skills MUST track progress via manage-tasks:

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
component: "task-execute-agent"
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

## Integration

**Callers**:
- `plan-execute` skill → spawns task-execute-agent
- `/plan-execute` command → orchestrates execution

**Dependencies**:
- `manage-tasks` → task retrieval and progress tracking
- `manage-config` → workflow skill resolution
- `manage-log` → work log entries

**Related**:
- [Task Contract](task-contract.md) - Task structure with domain, profile, skills
- [Config TOON Format](config-toon-format.md) - Workflow skill configuration
