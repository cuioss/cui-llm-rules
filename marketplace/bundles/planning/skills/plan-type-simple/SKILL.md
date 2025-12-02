---
name: plan-type-simple
description: Simple plan type providing 3-phase workflow (init→execute→finalize) for documentation, config changes, and quick fixes.
allowed-tools: Read
---

# Plan Type: Simple

**Phases**: 3 (init→execute→finalize)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes
- Non-code tasks
- Direct-to-main work

---

## API Summary

All plan-type skills implement this uniform API:

| Operation | Input | Output | Used By |
|-----------|-------|--------|---------|
| `get-phase-structure` | `plan_id`, `task_title` | Phase structure for plan.md | plan-init |
| `generate-tasks` | `plan_id`, `components[]` | **Writes directly** to plan.md | plan-refine |
| `get-finalize-config` | `plan_id` | Finalize behavior (commit, PR) | plan-execute |
| `get-next-phase` | `plan_id`, `current_phase` | Next phase name | phase-management |

**Key Design**: `generate-tasks` writes directly to plan.md via scripts (no ping-pong between skills).

---

## Operation: get-phase-structure

**Input**: `plan_id`, `task_title`

**Output**: Complete phase structure for plan.md

```markdown
# Task Plan: {task_title}

**Configuration**: See [config.toon](./config.toon)
**References**: See [references.toon](./references.toon)

**Current Phase**: init
**Current Task**: task-1

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 0/2 |
| execute | pending | 0 | 0/0 |
| finalize | pending | 2 | 0/2 |

---

## Phase: init (in_progress)

### Task 1: Detect Environment

**Phase**: init
**Goal**: Gather basic information

**Acceptance Criteria**:
- Current branch identified
- Task scope understood

**Checklist**:
- [ ] Check current git branch
- [ ] Understand task scope
- [ ] Identify files to modify
- [ ] **Log**: Record completion in work-log

### Task 2: Confirm Configuration

**Phase**: init
**Goal**: Quick confirmation of defaults

**Acceptance Criteria**:
- User has confirmed settings

**Checklist**:
- [ ] Display quick summary
- [ ] Confirm or edit settings
- [ ] Transition to execute phase
- [ ] **Log**: Record completion in work-log

---

## Phase: execute (pending)

{Tasks generated from task description}

---

## Phase: finalize (pending)

### Task 1: Commit Changes

**Phase**: finalize
**Goal**: Commit all changes

**Acceptance Criteria**:
- All changes committed
- Commit message follows conventions

**Checklist**:
- [ ] Stage all changes
- [ ] Create commit with descriptive message
- [ ] Push to branch (if remote)
- [ ] **Log**: Record completion in work-log

### Task 2: Verify Completion

**Phase**: finalize
**Goal**: Ensure task is complete

**Acceptance Criteria**:
- All acceptance criteria met

**Checklist**:
- [ ] Verify all changes applied
- [ ] Check no issues remaining
- [ ] Mark plan complete
- [ ] **Log**: Record completion in work-log

---

## Completion Criteria

Plan is complete when all phase tasks are marked `[x]`.
```

---

## Operation: get-config-template

**Input**: `branch`

**Output**: Config format for config.toon

```toon
# Plan Configuration

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

**Input**: `branch`

**Output**: References format for references.toon

```markdown
# References

## Context

**Branch**: `{branch}`

## Related Files

**Files to Modify**:
- (populated during execute phase)

## Notes

(add any relevant notes)
```

---

## Operation: generate-tasks

**Input**: `plan_id`, `components[]`

**Purpose**: Generate execute phase tasks and write them directly to plan.md.

**Note**: Simple plans do NOT use domain analysis. Tasks are generated directly from the task description. The `components[]` input may be empty or contain a single "task" component derived from the task description.

**Process**:
1. Generate task definitions from task description
2. Write tasks directly to plan.md execute phase via scripts
3. Return success confirmation

**Task Generation**:
```yaml
# For each component or the main task if no components:
task:
  id: task-{n}
  title: "{derived-from-task-description}"
  phase: execute
  goal: "{goal-from-task}"
  acceptance_criteria:
    - "{criterion-1}"
    - "{criterion-2}"
  checklist:
    - "{action-1}"
    - "{action-2}"
    - "{action-3}"
    - "**Log**: Record completion in work-log"
    - "**Learn**: Capture lesson if unexpected behavior"
```

**Write to plan.md**:
```bash
python3 {write-plan.py} --plan-dir .plan/plans/{plan_id} --add-task --phase execute --task-content "{task-yaml}"
```

**Output**:
```yaml
generate_tasks_result:
  status: success
  tasks_written: 1
  plan_file: .plan/plans/{plan_id}/plan.md
```

**Task Generation Guidance**:
For simple plans, generate execute phase tasks directly from the task description:
- Goal statement
- Acceptance criteria (1-3 items)
- Checklist (3-5 items)
- Log and Learn items at the end

---

## Operation: get-next-phase

**Input**: `plan_id`, `current_phase`

**Output**: Next phase in workflow

| Current Phase | Next Phase |
|---------------|------------|
| init | execute |
| execute | finalize |
| finalize | complete |

---

## Operation: get-finalize-config

**Input**: `plan_id`

**Purpose**: Returns finalize phase behavior configuration.

**Output**:

```yaml
finalize_config:
  commit_strategy: fine-granular    # fine-granular | phase-specific | complete
  create_pr: false                  # Simple plans don't create PRs
  verification_required: false      # No build verification
  verification_command: null
```

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 3 |
| Refine Phase | No |
| Branch Requirement | Any branch OK |
| Issue | Not used |
| Build System | None |
| PR Workflow | No |
| User Interaction | Minimal |
| Total Init Tasks | 2 |
| Total Finalize Tasks | 2 |

---

## Auto-Detection Criteria

Use simple plan type when:
1. Task involves documentation only
2. Task involves configuration changes only
3. No build system detected
4. Branch is main/master (direct commits)
5. User explicitly selects "simple"
