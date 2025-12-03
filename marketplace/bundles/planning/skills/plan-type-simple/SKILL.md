---
name: plan-type-simple
description: Simple plan type providing 3-phase workflow (init→execute→finalize) for documentation, config changes, and quick fixes
allowed-tools: Read, Bash
---

# Plan Type: Simple

**Phases**: 3 (init → execute → finalize)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

**API**: Implements `planning:plan-type-api` contract.

**Note**: Simple plans skip the refine phase. Tasks are generated during init from the task description. The `refine` operation is a no-op for this plan type.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 3 |
| Technology | none |
| Build System | none |
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
    - title: Add Requirements
      steps: Create REQ file from task description
    - title: Generate Tasks
      steps: Create TASK files directly (no refine phase)
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

**Input**: (none)

**Output**:

```toon
plan_type: simple
compatibility: breaking
commit_strategy: fine-granular
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

## Operation: refine

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`

**Note**: Simple plans skip the refine phase. This operation is a **no-op** that returns immediately. Tasks are generated during init phase instead.

**Output**:

```toon
status: skipped
plan_id: {plan_id}
message: Simple plans skip refine phase. Tasks generated during init.

phase_1:
  requirements_processed: 0
  specs_created: 0

phase_2:
  specs_processed: 0
  tasks_created: 0
```

**Alternative**: If called with `--force`, will generate tasks from existing requirements:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Simple Task Generation (if forced)                                 │
├─────────────────────────────────────────────────────────────────────┤
│  1. Load requirements:                                              │
│     python3 {manage-requirement.py} findAll --plan-id {plan_id}     │
│                                                                     │
│  2. FOR EACH requirement:                                           │
│     - Create 1:1 specification (minimal body)                       │
│       python3 {manage-specification.py} add \                       │
│         --plan-id {plan_id} \                                       │
│         --title "{requirement title}" \                             │
│         --requirements "REQ-{n}" \                                  │
│         --body "{requirement body}"                                 │
│                                                                     │
│  3. FOR EACH specification:                                         │
│     - Create single task with simple steps                          │
│       python3 {manage-task.py} add \                                │
│         --plan-id {plan_id} \                                       │
│         --specification SPEC-{n} \                                  │
│         --title "{task title}" \                                    │
│         --description "{goal}" \                                    │
│         --steps "Execute task" "Verify result"                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Operation: get-next-phase

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `current_phase`

**Phase Transitions** (3-phase model - skips refine):

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

## Init Phase Task Generation

Since simple plans skip refine, tasks are generated during init phase:

```bash
# During init phase, after requirements are added:
python3 {manage-task.py} add \
  --plan-id {plan_id} \
  --specification SPEC-1 \
  --title "{task-title-from-description}" \
  --description "{goal-statement}" \
  --steps "{step-1}" "{step-2}" "{step-3}"
```

**Task Generation Guidance**:

For simple plans, generate execute phase tasks directly from the task description:
- Goal statement (1 sentence)
- Steps (3-5 actionable items)

---

## Quality Checklist

- [x] Loads `planning:plan-type-api` for contract reference
- [x] Implements all 6 operations with correct signatures
- [x] Uses manage-* tools for all data I/O
- [x] Returns `status` field in all outputs
- [x] Defines phase transition matrix (3 phases - skips refine)
- [x] Defines characteristics matrix
- [x] Handles errors with status and message
- [x] Documents that refine is skipped (no-op)
