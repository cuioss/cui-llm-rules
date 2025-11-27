# Plan Templates & Workflow

This document defines the plan.md template structure, phase-based workflow, and status management system.

## Phase-Based Workflow

Plans are organized into **5 sequential phases** that must be completed in order. This provides structured progression from planning through implementation to completion.

### Phase Definitions

#### 1. init - Initialization

**Purpose**: Setup and initial planning

**Typical Tasks**:
- Read and understand requirements
- Define initial approach
- Identify key components
- Establish naming conventions
- List dependencies
- Define constraints

**Completion Criteria**:
- All initial setup tasks completed
- Approach clearly defined
- Ready to refine details

#### 2. refine - Iterative Refinement

**Purpose**: Refine plan until ready to implement

**Detailed Specification**: See [plan-refine/refine.md](plan-refine/refine.md) for complete workflow

**Operations**:
- Analyze requirements into components
- Plan implementation tasks with acceptance criteria
- Identify documentation needs (ADRs, interfaces)

**Output Artifact**: `implementation-requirements.md` - See [template](plan-refine/implementation-requirements-template.md)

**Completion Criteria**:
- All tasks have acceptance criteria
- No ambiguities remain
- Plan is actionable
- Ready for implementation

#### 3. implement - Implementation

**Purpose**: Create/modify code and configuration

**Typical Tasks**:
- Implement features
- Create classes/functions
- Update configuration
- Add dependencies
- Follow coding standards
- Add inline documentation

**Completion Criteria**:
- All code implemented
- Standards followed
- Configuration updated
- Ready for testing

#### 4. verify - Testing & Verification

**Purpose**: Test and verify implementation

**Typical Tasks**:
- Write unit tests
- Write integration tests
- Run build verification
- Check test coverage
- Fix test failures
- Verify acceptance criteria

**Completion Criteria**:
- All tests passing
- Coverage targets met
- Build successful
- Acceptance criteria verified
- Ready for finalization

#### 5. finalize - Documentation & Completion

**Purpose**: Complete documentation and prepare for PR

**Typical Tasks**:
- Update user documentation
- Update technical documentation
- Verify all tasks completed
- Commit changes
- Create PR

**Completion Criteria**:
- Documentation updated
- All tasks verified
- Changes committed
- PR created (optional)
- Task complete

### Phase Rules

**Sequential Progression**:
- A phase can only be started if the previous phase is `completed`
- Cannot skip phases (must go: init → refine → implement → verify → finalize)
- Phases must be completed in order

**Completion Requirements**:
- A phase can only be marked as `completed` if **all tasks** in that phase are done (`[x]`)
- Automatic phase completion detection when last task marked complete
- Phase Progress Table automatically updated

**Status Flow**:
```
Phase: pending → in_progress → completed
Task:  [ ] → [x]
Plan:  pending → in_progress → completed
```

## Standard Template

### File: plan.md

Complete template for plan.md file (tasks-only):

```markdown
# [Task Title]

**Configuration**: See [config.md](./config.md)
**References**: See [references.md](./references.md)

**Status**: [pending|in_progress|completed]
**Current Phase**: [init|refine|implement|verify|finalize]
**Current Task**: [Task ID or "none"]

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| refine | in_progress | 3 | 1/3 |
| implement | pending | 5 | 0/5 |
| verify | pending | 3 | 0/3 |
| finalize | pending | 2 | 0/2 |

---

## Phase: init (completed)

### Task 1: [Setup task name]

**Phase**: init
**Status**: [x]
**Goal**: [What success looks like]

**Acceptance Criteria**:
- [Criterion 1]
- [Criterion 2]

**Checklist**:
- [x] Read and understand requirements
- [x] Define initial approach
- [x] Identify key components

### Task 2: [Naming task]

**Phase**: init
**Status**: [x]
**Goal**: [Define naming conventions]

**Acceptance Criteria**:
- [Criterion 1]

**Checklist**:
- [x] Establish naming patterns
- [x] Document naming decisions

---

## Phase: refine (in_progress)

### Task 3: [Refinement task]

**Phase**: refine
**Status**: [x]
**Goal**: [Refine approach based on feedback]

**Acceptance Criteria**:
- [Criterion 1]

**Checklist**:
- [x] Incorporate feedback
- [x] Update technical decisions

### Task 4: [Validation task]

**Phase**: refine
**Status**: [ ]
**Goal**: [Validate approach]

**Acceptance Criteria**:
- [Criterion 1]
- [Criterion 2]

**Checklist**:
- [ ] Validate design decisions
- [ ] Check for edge cases
- [ ] Confirm readiness

---

## Phase: implement (pending)

### Task 5: [Implementation task]

**Phase**: implement
**Status**: [ ]
**Goal**: [Implement feature X]

**Acceptance Criteria**:
- [Criterion 1]
- [Criterion 2]

**Checklist**:
- [ ] Implement functionality
- [ ] Follow coding standards
- [ ] Add inline documentation

[More implementation tasks...]

---

## Phase: verify (pending)

### Task N: [Testing task]

**Phase**: verify
**Status**: [ ]
**Goal**: [Test feature X]

**Acceptance Criteria**:
- [Test coverage ≥ 80%]

**Checklist**:
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Run build verification

[More testing tasks...]

---

## Phase: finalize (pending)

### Task M: [Documentation task]

**Phase**: finalize
**Status**: [ ]
**Goal**: [Document feature]

**Acceptance Criteria**:
- [Documentation complete]

**Checklist**:
- [ ] Update user documentation
- [ ] Update technical documentation
- [ ] Verify all tasks completed
- [ ] Commit changes
- [ ] Create PR

---

## Completion Criteria

All phases must be completed and all tasks marked with `[x]` before plan is considered complete.

**Final Verification**:
- [ ] All phases completed
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Build successful
- [ ] Documentation updated
```

## Status Management

### Status Levels

The plan management system uses **3 levels** of status tracking:

#### 1. Plan-Level Status

**Values**:
- `pending` - Plan created, implementation not started
- `in_progress` - Currently implementing tasks
- `completed` - All phases and tasks completed and verified

**Location**: Top of plan.md (`**Status**: pending`)

**Updates**: Automatically when phases progress

#### 2. Phase-Level Status

**Values**:
- `pending` - Phase not yet started (previous phase not completed)
- `in_progress` - Phase active, tasks being worked on
- `completed` - All tasks in phase completed

**Location**:
- Phase Progress Table
- Phase section headers (`## Phase: implement (in_progress)`)

**Updates**: Automatically based on task completion and phase transitions

#### 3. Task-Level Status

**Values**:
- `[ ]` - Task pending (not started or in progress)
- `[x]` - Task completed

**Location**: Task definition (`**Status**: [x]`)

**Updates**: Manually by user or automatically by task-plan skill

### Helper Fields

To simplify model interaction, the plan includes helper fields that track current state:

#### Current Phase

**Purpose**: Tracks which phase is currently active

**Values**: `init|refine|implement|verify|finalize`

**Location**: Top of plan.md (`**Current Phase**: implement`)

**Updates**: Automatically when phase transitions occur

**Usage**: Quick reference for "where are we now?"

#### Current Task

**Purpose**: Tracks which task is currently being worked on

**Values**:
- Task ID (e.g., `task-3`, `task-8`)
- `"none"` if no task active

**Location**: Top of plan.md (`**Current Task**: task-3`)

**Updates**: Automatically when tasks start/complete

**Usage**: Quick reference for "what are we working on?"

#### Phase Progress Table

**Purpose**: Quick overview of all phases

**Format**:
```markdown
| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | completed | 2 | 2/2 |
| refine | in_progress | 3 | 1/3 |
| implement | pending | 5 | 0/5 |
| verify | pending | 3 | 0/3 |
| finalize | pending | 2 | 0/2 |
```

**Location**: After Overview section in plan.md

**Updates**: Automatically by all plan management operations

**Usage**: At-a-glance progress tracking

## Workflow Operations

### Creating Initial Plan

**Operation**: Create Plan (see [API Specification](api.md#operation-create-plan))

**Initial State**:
- Plan Status: `in_progress`
- Current Phase: `init`
- Current Task: `task-1` (first task of init phase)
- All phases: `init: in_progress`, others: `pending`

### Task Progression

**Operation**: Task Progress Update (see [API Specification](api.md#operation-task-progress-update))

**Flow**:
1. Mark current task as complete (`[x]`)
2. Update Phase Progress Table
3. Check if all tasks in phase are complete
4. If yes, automatic phase completion
5. Update Current Task to next task

### Phase Transition

**Operation**: Phase Transition (see [API Specification](api.md#operation-phase-transition))

**Flow**:
1. Verify all tasks in current phase completed
2. Mark current phase as `completed`
3. Mark next phase as `in_progress`
4. Update Current Phase field
5. Update Current Task to first task of new phase
6. Update Phase Progress Table

**Automatic Triggering**:
- Triggered automatically when last task of phase completed
- No manual phase transition needed

### Plan Completion

**Criteria**:
- All 5 phases marked as `completed`
- All tasks marked as `[x]`
- Plan Status: `completed`
- Current Phase: `finalize`
- Current Task: `none`

## Task Structure

### Task Template

```markdown
### Task N: [Task Name]

**Phase**: [phase-name]
**Status**: [ ] or [x]
**Goal**: [What success looks like]

**Acceptance Criteria**:
- [Specific, measurable criterion 1]
- [Specific, measurable criterion 2]

**Checklist**:
- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3
```

### Task Best Practices

**Task Naming**:
- Start with verb (Implement, Add, Fix, Update, etc.)
- Be specific (not "Add authentication" but "Add JWT token validation")
- Include scope (feature, component, module)

**Goal Definition**:
- Clear success statement
- Measurable outcome
- User or system benefit

**Acceptance Criteria**:
- Specific, testable conditions
- 2-5 criteria per task
- Use "must" language
- Examples: "API must return 401 for invalid tokens"

**Checklist Items**:
- Concrete action items
- Implementation steps
- Verification steps
- 3-7 items per task

## Future Enhancements

This section is a placeholder for future workflow enhancements:

### Planned Features

- **Custom Phase Definitions**: Per-project phase customization
- **Phase Templates**: Pre-defined phase structures by task type
- **Task Dependencies**: Explicit task dependency tracking
- **Time Estimates**: Optional time tracking per phase/task
- **Parallel Tasks**: Support for concurrent task execution
- **Conditional Phases**: Optional phases based on task type

### Integration Points

- **Memory Layer**: Store phase transitions for analytics
- **Git Integration**: Link phases to commits
- **Issue Tracking**: Sync phase progress with issues
- **Metrics**: Track phase completion times

## Summary

The template and workflow system provides:

1. ✅ **Structured Progression** - 5 sequential phases guide implementation
2. ✅ **Tasks-Only Design** - plan.md contains only phases, tasks, and status
3. ✅ **Clear Separation** - Configuration in config.md, references in references.md
4. ✅ **Status Tracking** - 3 levels (plan, phase, task)
5. ✅ **Helper Fields** - Current phase and task for quick reference
6. ✅ **Automatic Updates** - Phase Progress Table stays current
7. ✅ **Phase Rules** - Sequential enforcement prevents mistakes
8. ✅ **Task Structure** - Consistent task format with goals and criteria

---

**Related Documents**:
- [Plan Types](plan-types.md) - Init phase router
- [Refine Phase](plan-refine/refine.md) - Refine phase specification
- [Implement Phase](plan-implement/implement.md) - Implement phase specification
- [Verify Phase](plan-verify/verify.md) - Verify phase specification
- [Finalize Phase](plan-finalize/finalize.md) - Finalize phase specification
- [Architecture](architecture.md) - Abstraction layer design
- [Persistence](plan-files/persistence.md) - File structure and references.md format
- [API Specification](api.md) - Operations that use these templates
- [Decomposition](decomposition.md) - Implementation guidance
