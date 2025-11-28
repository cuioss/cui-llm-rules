# Implementation Plan

Tasks for implementing the plan management system with unified `/task` command.

## CRITICAL RULES

### Before Starting Implementation

```
Skill: cui-plugin-development-tools:plugin-architecture
```

Load this skill FIRST to understand component patterns, frontmatter standards, and architecture rules.

### Execution Rules

1. **Execute tasks ONE-AFTER-ANOTHER** - Do not parallelize implementation tasks
2. **After each task completion** - Mark the checkbox as done `[x]`
3. **Run /plugin-doctor after each component** - Verify before proceeding
4. **Do not skip verification steps** - Each phase has validation tasks

---

## Architecture Overview

### Single Command Design

**Before** (two commands):
```
/task-plan     → Creates plan, handles init/refine
/task-implement → Executes implement/verify/finalize
```

**After** (unified command):
```
/task → Auto-routes based on plan state
```

### Component Structure

```
/task command (entry point)
      │
      ▼
phase-management skill (orchestration)
      │
      ├── plan-init      (init phase)
      ├── plan-refine    (refine phase)
      ├── plan-implement (implement phase)
      ├── plan-verify    (verify phase)
      └── plan-finalize  (finalize phase)
           │
           └── plan-files (persistence layer)
```

### Key Documents

| Document | Purpose |
|----------|---------|
| [task-command.md](task-command.md) | /task command specification |
| [phase-management.md](phase-management.md) | Orchestration skill specification |
| [plan-types.md](plan-types.md) | Init phase router and plan types |
| [architecture.md](architecture.md) | Abstraction layer design |
| [templates-workflow.md](templates-workflow.md) | Plan templates and phase workflow |
| [api.md](api.md) | Complete skill API with TOON handoffs |
| [decomposition.md](decomposition.md) | Implementation details |

---

## Phase 1: Create Phase Management Skill

### Skill Structure

- [x] Create `cui-task-workflow/skills/phase-management/` directory
- [x] Create SKILL.md with operations:
  - [x] `discover-plans` - Find plans in workspace
  - [x] `route-phase` - Determine target phase skill
  - [x] `transition-phase` - Handle phase completion
  - [x] `get-status` - Return plan status
- [x] Create `standards/orchestration.md` - Orchestration patterns
- [x] Create `standards/transitions.md` - Phase transition rules
- [x] ~~Create README.md with skill documentation~~ (anti-pattern, skipped)

### Discover Plans Operation

- [x] Implement plan discovery via Glob tool
  - [x] Search `.claude/plans/*/plan.md`
  - [x] Parse each plan for current_phase and status
  - [x] Sort by last modified time
- [x] Return structured list with recommendation
- [x] Handle empty results (no plans found)

### Route Phase Operation

- [x] Implement phase routing logic
  - [x] Read plan.md via plan-files skill
  - [x] Map current_phase to target skill
  - [x] Validate explicit phase override requests
- [x] Return routing decision with context
- [x] Handle invalid phase override attempts

### Transition Phase Operation

- [x] Implement phase transition logic
  - [x] Verify all tasks in phase complete
  - [x] Determine next phase in sequence
  - [x] Update plan via plan-files skill
- [x] Handle plan completion (after finalize)
- [x] Return transition result

### Get Status Operation

- [x] Implement comprehensive status retrieval
  - [x] Read plan, config, references
  - [x] Calculate overall progress
  - [x] Format phase progress table
- [x] Return structured status data

### Python Scripts for Deterministic Operations

Scripts output JSON for consistent parsing. Location: `cui-task-workflow/skills/phase-management/scripts/`

#### discover-plans.py

- [x] Implement `discover-plans.py`
  - [x] Search `.claude/plans/*/plan.md` using glob
  - [x] Parse each plan.md for: name, path, current_phase, status
  - [x] Sort by file modification time (most recent first)
  - [x] Output JSON array with plan metadata
  - [x] Handle empty results gracefully

#### route-phase.py

- [x] Implement `route-phase.py`
  - [x] Input: current_phase, optional explicit_phase override
  - [x] Map phase to skill name (init→plan-init, refine→plan-refine, etc.)
  - [x] Validate explicit phase is allowed (no skipping)
  - [x] Output JSON with target_skill, phase_info

#### transition-phase.py

- [x] Implement `transition-phase.py`
  - [x] Input: plan directory, completed_phase
  - [x] Define phase order: init → refine → implement → verify → finalize
  - [x] Determine next phase in sequence
  - [x] Detect plan completion (after finalize)
  - [x] Output JSON with from_phase, to_phase, is_complete

#### get-status.py

- [x] Implement `get-status.py`
  - [x] Input: plan directory
  - [x] Aggregate data from plan.md, config.md, references.md
  - [x] Calculate overall progress percentage
  - [x] Format phase progress data
  - [x] Output comprehensive JSON status

### Python Script Tests

Location: `test/cui-task-workflow/phase-management/`

- [x] Create `test_discover_plans.py`
  - [x] Test: Single plan discovery
  - [x] Test: Multiple plans discovery
  - [x] Test: Empty directory (no plans)
  - [x] Test: Invalid plan.md structure handling

- [x] Create `test_route_phase.py`
  - [x] Test: Valid phase routing (all 5 phases)
  - [x] Test: Explicit phase override (valid)
  - [x] Test: Invalid phase override (skip attempt)
  - [x] Test: Unknown phase handling

- [x] Create `test_transition_phase.py`
  - [x] Test: All valid transitions (init→refine, etc.)
  - [x] Test: Plan completion detection
  - [x] Test: Invalid transition attempt
  - [x] Test: Out-of-order transition

- [x] Create `test_get_status.py`
  - [x] Test: Complete status aggregation
  - [x] Test: Progress calculation
  - [x] Test: Missing files handling
  - [x] Test: Partial plan data

### Quality Verification

- [x] Run `/plugin-doctor` for phase-management skill
- [x] Test all operations individually
- [x] Test error scenarios
- [x] Run all Python script tests: `pytest test/cui-task-workflow/phase-management/`

---

## Phase 2: Create /task Command

### Command Structure

- [x] Create `cui-task-workflow/commands/task.md` (thin wrapper, 62 lines)
- [x] Create command with:
  - [x] Parameter definitions (plan, task, issue, phase)
  - [x] Decision tree delegated to phase-management skill
  - [x] Integration with phase-management skill

### Parameter Handling

- [x] Implement parameter parsing
  - [x] `plan=PATH` - Existing plan directory
  - [x] `task=STRING` - Task description for new plan
  - [x] `issue=URL` - GitHub issue for new plan
  - [x] `phase=PHASE` - Explicit phase override
- [x] Validate parameter combinations (in phase-management)
- [x] Handle missing/conflicting parameters (in phase-management)

### Decision Logic

- [x] Implement action selection (in phase-management Orchestrate Task workflow)
  - [x] If `task` or `issue` → Create new plan (plan-init)
  - [x] If `plan` → Load and route to current phase
  - [x] If no params → Discover plans, ask user
- [x] Handle single plan auto-selection
- [x] Handle multiple plans user selection

### Phase Execution Loop

- [x] Implement execution flow (in phase-management)
  - [x] Route to phase skill via phase-management
  - [x] Execute phase operations
  - [x] Handle phase completion
  - [x] Offer to continue or stop
- [x] Implement user interaction points
- [x] Handle interruptions gracefully

### Output Formatting

- [x] Implement success output formats (in phase-management)
  - [x] New plan created
  - [x] Phase in progress
  - [x] Phase completed
  - [x] Plan completed
- [x] Implement error output formats
- [x] Format progress displays

### Quality Verification

- [x] Run `/plugin-doctor` for task command
- [ ] Test new plan creation flow
- [ ] Test continue existing plan flow
- [ ] Test auto-discovery flow
- [ ] Test error scenarios

---

## Phase 3: Update Existing Phase Skills

### Update plan-init Skill

- [x] Update SKILL.md for /task integration
  - [x] Add Command Integration section
  - [x] Add phase-management to Skills Used
- [x] Ensure returns proper completion signal (already had Phase Transition section)
- [ ] Test with phase-management orchestration

### Update plan-refine Skill

- [x] Update SKILL.md for /task integration
- [x] Ensure returns proper completion signal (already had Phase Transition section)
- [ ] Test with phase-management orchestration

### Update plan-implement Skill

- [x] Update SKILL.md for /task integration
- [x] Ensure returns proper completion signal (already had Phase Transition section)
- [ ] Test with phase-management orchestration

### Update plan-verify Skill

- [x] Update SKILL.md for /task integration
- [x] Ensure returns proper completion signal (already had Phase Transition section)
- [ ] Test with phase-management orchestration

### Update plan-finalize Skill

- [x] Update SKILL.md for /task integration
- [x] Ensure returns proper completion signal (already had complete-plan operation)
- [x] Handle plan completion scenario (already implemented)
- [ ] Test with phase-management orchestration

### Quality Verification

- [x] Run `/plugin-doctor` for all updated skills (line count verification)
- [ ] Test complete workflow: init → refine → implement → verify → finalize

---

## Phase 4: Update Documentation

### Update Architecture Documents

- [x] Update [architecture.md](architecture.md)
  - [x] Replace /task-plan, /task-implement with /task
  - [x] Add phase-management skill to diagram
  - [x] Update abstraction layer description
- [x] Update [api.md](api.md)
  - [x] Add phase-management skill API
  - [x] Update command integration examples
- [x] Update [decomposition.md](decomposition.md)
  - [x] Update skill directory structure
  - [x] Update command integration patterns
  - [x] Update usage examples for /task

### Update README

- [x] Update [README.md](README.md)
  - [x] Add phase-management skill to overview
  - [x] Update operations summary table
  - [x] Update navigation section

### Remove Obsolete Content

- [x] Remove /task-plan command references
- [x] Remove /task-implement command references
- [x] Update all cross-references

---

## Phase 5: Remove Old Commands

**Note**: The old `/task-plan` command never existed as a file. The existing `/task-implement` command is for GitHub issue implementation (different workflow), not plan management. Phase 5 is N/A.

### Deprecate /task-plan Command

- [x] Mark command as deprecated (if exists) - N/A (command never existed)
- [x] Add redirect to /task - N/A
- [x] Update any external references - Done in Phase 4

### Deprecate /task-implement Command

- [x] Mark command as deprecated (if exists) - N/A (existing task-implement is different command)
- [x] Add redirect to /task - N/A
- [x] Update any external references - Done in Phase 4

### Clean Up

- [x] Remove deprecated command files - N/A (none to remove)
- [x] Verify no broken references remain - Verified
- [x] Final documentation review - Completed in Phase 4

---

## Phase 6: Integration Testing

### End-to-End Workflows

- [ ] Test: Create new plan from task description
  - [ ] `/task task="Implement feature X"`
  - [ ] Verify plan created
  - [ ] Verify init phase complete
  - [ ] Continue through all phases
- [ ] Test: Create new plan from issue
  - [ ] `/task issue="https://github.com/..."`
  - [ ] Verify issue content extracted
  - [ ] Verify plan created
- [ ] Test: Continue existing plan
  - [ ] `/task plan=".claude/plans/xxx/"`
  - [ ] Verify routes to current phase
  - [ ] Verify phase execution
- [ ] Test: Auto-discover single plan
  - [ ] `/task` (with one plan in workspace)
  - [ ] Verify auto-selects
- [ ] Test: Select from multiple plans
  - [ ] `/task` (with multiple plans)
  - [ ] Verify prompts for selection

### Error Scenarios

- [ ] Test: No plans, no parameters
- [ ] Test: Invalid plan path
- [ ] Test: Invalid phase override
- [ ] Test: Incomplete phase transition attempt

### Phase Transitions

- [ ] Test: init → refine transition
- [ ] Test: refine → implement transition
- [ ] Test: implement → verify transition
- [ ] Test: verify → finalize transition
- [ ] Test: finalize → plan complete

---

## Summary

This plan implements a unified `/task` command that:

1. **Simplifies UX** - One command instead of two
2. **Auto-routes** - Determines action from plan state
3. **Maintains flexibility** - Supports explicit overrides
4. **Preserves architecture** - Phase skills unchanged (only orchestration added)

**New Components**:
- `phase-management` skill (orchestration)
- `/task` command (unified entry point)
- Python scripts (4): `discover-plans.py`, `route-phase.py`, `transition-phase.py`, `get-status.py`
- Python tests (4): Corresponding test files for each script

**Updated Components**:
- All phase skills (integration updates)
- All documentation (reference updates)

**Removed Components**:
- `/task-plan` command
- `/task-implement` command
