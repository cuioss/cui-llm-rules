---
name: plan-type-simple
description: Simple plan type providing 4-phase workflow (init→refine→execute→finalize) for documentation, config changes, and quick fixes
allowed-tools: Read, Bash
---

# Plan Type: Simple

**Phases**: 4 (init → refine → execute → finalize)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 4 |
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

phases[4]{name,order}:
init,1
refine,2
execute,3
finalize,4

phase_tasks:
  init:
    - title: Detect Environment
      steps: git branch --show-current
    - title: Analyze Task
      steps: Read task.md, Determine scope
    - title: Add Requirements
      steps: Create REQ file from task description
    - title: Confirm Configuration
      steps: Display summary, Confirm settings
  refine:
    - title: Refine Plan
      steps: Call plan-type-simple:refine, Iterates REQ→SPEC→TASK
  execute: (generated dynamically from TASK files)
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

**Process**:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Requirements → Specifications                             │
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
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Specifications → Tasks                                    │
├─────────────────────────────────────────────────────────────────────┤
│  3. Load specifications:                                            │
│     python3 {manage-specification.py} findAll --plan-id {plan_id}   │
│                                                                     │
│  4. FOR EACH specification:                                         │
│     - Create single task with simple steps                          │
│       python3 {manage-task.py} add \                                │
│         --plan-id {plan_id} \                                       │
│         --specification SPEC-{n} \                                  │
│         --title "{task title}" \                                    │
│         --description "{goal}" \                                    │
│         --steps "Execute task" "Verify result"                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Output**:

```toon
status: success
plan_id: {plan_id}

phase_1:
  requirements_processed: 1
  specs_created: 1

phase_2:
  specs_processed: 1
  tasks_created: 1
```

---

## Operation: get-next-phase

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `current_phase`

**Phase Transitions**:

| Current Phase | Next Phase |
|---------------|------------|
| init | refine |
| refine | execute |
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
- [x] Implements all 6 operations with correct signatures
- [x] Uses manage-* tools for all data I/O
- [x] Returns `status` field in all outputs
- [x] Defines phase transition matrix (4 phases)
- [x] Defines characteristics matrix
- [x] Handles errors with status and message
- [x] refine operation iterates REQ→SPEC→TASK with simple 1:1 mapping
