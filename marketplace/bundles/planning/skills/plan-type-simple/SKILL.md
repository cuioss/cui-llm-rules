---
name: plan-type-simple
description: Simple plan type providing 3-phase workflow (init→execute→finalize) for documentation, config changes, and quick fixes
allowed-tools: Read
---

# Plan Type: Simple

**Phases**: 3 (init → execute → finalize)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

**Analysis Skill**: None (tasks derived directly from description)

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 3 |
| Technology | none |
| Build System | none |
| Analysis Skill | null |
| Branch Required | false |
| Issue Required | false |
| PR Workflow | false |
| Verification | none |

---

## Operation: get-phase-structure

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`, `task_title`

**Output**:

```toon
status: success
current_phase: init
initial_status: pending

phases[3]{name,order}:
init,1
execute,2
finalize,3

phase_tasks:
  init:
    - title: Detect Environment
      steps: git branch --show-current
    - title: Analyze Task
      steps: Read task.md, Determine scope
    - title: Confirm Configuration
      steps: Display summary, Confirm settings
  execute: (generated from task description)
  finalize:
    - title: Commit Changes
      steps: Stage changes, Create commit, Push
    - title: Verify Completion
      steps: Verify changes, Mark complete
```

---

## Operation: get-config-template

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `branch`

**Output**:

```toon
plan_type: simple
branch: {branch}
issue: none

technology: none
build_system: none

compatibility: breaking
commit_strategy: fine-granular
finalizing: commit-only
```

---

## Operation: get-references-template

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `branch`

**Output**:

```toon
branch: {branch}
base_branch: main

files:
  modified: []

notes: []
```

---

## Operation: generate-tasks

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`, `components[]`

**Note**: Simple plans do NOT use domain analysis. The `components[]` input may be empty or contain a single component derived directly from the task description.

**Process**:

1. Parse task description for actionable items
2. Call `manage-task.py add` for each task (writes directly to disk)
3. Each task has goal and steps

**Task Generation**:

```bash
python3 manage-task.py add \
  --plan-id {plan_id} \
  --specification SPEC-1 \
  --title "{task-title-from-description}" \
  --description "{goal-statement}" \
  --steps "{step-1}" "{step-2}" "{step-3}"
```

**Output** (confirmation only, tasks already written):

```toon
status: success
plan_id: {plan_id}
tasks_created: 1

tasks[1]{number,title,specification,file}:
1,{derived-title},SPEC-1,TASK-001-{slug}.toon
```

**Task Generation Guidance**:

For simple plans, generate execute phase tasks directly from the task description:
- Goal statement (1 sentence)
- Steps (3-5 actionable items)

---

## Operation: get-next-phase

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `current_phase`

**Phase Transitions**:

| Current Phase | Next Phase |
|---------------|------------|
| init | execute |
| execute | finalize |
| finalize | complete |

**Output**:

```toon
status: success
phase: {next}
```

---

## Operation: get-finalize-config

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`

**Output**:

```toon
status: success
commit_strategy: fine-granular
create_pr: false
verification_required: false
verification_command: null
branch_strategy: direct
```

---

## Quality Checklist

- [x] Loads `planning:plan-type-api` for contract reference
- [x] Implements all 7 operations with correct signatures
- [x] Uses manage-tasks skill for task generation
- [x] Returns `status` field in all outputs
- [x] Defines phase transition matrix (3 phases)
- [x] Defines characteristics matrix
- [x] Handles errors with status and message
