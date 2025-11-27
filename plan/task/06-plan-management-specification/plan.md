# Implementation Plan

Tasks for implementing the plan management system. See related documents for details:

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

**Core Documents**:
- [Plan Types](plan-types.md) - Init phase router and configuration
- [Architecture](architecture.md) - Abstraction layer design
- [Persistence](plan-files/persistence.md) - File structure and directory organization
- [plan-files Skill](plan-files/plan-files.md) - Persistence layer operations
- [Templates & Workflow](templates-workflow.md) - Plan templates and phase-based workflow
- [API Specification](api.md) - Complete skill API with TOON handoffs
- [Decomposition](decomposition.md) - Implementation details and usage examples

**Phase Specifications**:
- [Init - Implementation](plan-init/implementation.md) - Full dev workflow (5 phases)
- [Init - Simple](plan-init/simple.md) - Lightweight workflow (3 phases)
- [Refine Phase](plan-refine/refine.md) - Requirement analysis and task planning
- [Implementation Requirements Template](plan-refine/implementation-requirements-template.md) - Runtime artifact template
- [Implement Phase](plan-implement/implement.md) - Task execution and delegation
- [Verify Phase](plan-verify/verify.md) - Build, quality, and documentation verification
- [Finalize Phase](plan-finalize/finalize.md) - Commit, PR creation, and review workflow

**TOON Handoff Protocols**:
- [plan-init Handoff](plan-init/handoff.md)
- [plan-refine Handoff](plan-refine/handoff.md)
- [plan-implement Handoff](plan-implement/handoff.md)
- [plan-verify Handoff](plan-verify/handoff.md)
- [plan-finalize Handoff](plan-finalize/handoff.md)
- [plan-files Handoff](plan-files/handoff.md)

---

## Phase 1: Create Phase Skills (One Skill Per Phase)

### Directory Structure Support

**plan-init skill** (init phase):
- [x] Create `cui-task-workflow/skills/plan-init/` directory
- [x] Create SKILL.md with create operation and type routing (see [api.md](api.md))
- [x] Create plan-init/ directory with init implementations
- [x] Create README.md with skill documentation

**plan-refine skill** (refine phase):
- [x] Create `cui-task-workflow/skills/plan-refine/` directory
- [x] Create SKILL.md with analyze, plan-tasks, identify-docs operations
- [x] Create README.md with skill documentation

**plan-implement skill** (implement phase):
- [x] Create `cui-task-workflow/skills/plan-implement/` directory
- [x] Create SKILL.md with execute-tasks, delegate, track-progress operations
- [x] Create README.md with skill documentation

**plan-verify skill** (verify phase):
- [x] Create `cui-task-workflow/skills/plan-verify/` directory
- [x] Create SKILL.md with run-build, check-quality, review-docs operations
- [x] Create README.md with skill documentation

**plan-finalize skill** (finalize phase):
- [x] Create `cui-task-workflow/skills/plan-finalize/` directory
- [x] Create SKILL.md with commit, create-pr, pr-workflow operations
- [x] Create README.md with skill documentation

**plan-files skill** (persistence layer):
- [x] Create `cui-task-workflow/skills/plan-files/` directory
- [x] Create SKILL.md with persistence operations (see [api.md](api.md#skill-plan-files))
  - [x] create-directory - Create plan directory structure
  - [x] read-plan - Read plan.md (tasks, phases, status)
  - [x] read-config - Read config.md (technology, build system, etc.)
  - [x] get-references - Read references.md (ADRs, interfaces, files)
  - [x] write-plan - Write/update plan.md
  - [x] write-config - Write config.md
  - [x] write-references - Write/update references.md
  - [x] update-progress - Mark tasks complete, update phase table
- [x] Create README.md with skill documentation

**Shared templates**:
- [x] Create `cui-task-workflow/skills/plan-init/standards/` directory
- [x] Create plan-template.md (see [templates-workflow.md](templates-workflow.md))
- [ ] Create references-template.md (see [persistence.md](plan-files/persistence.md))

### Init Phase Support (plan-init skill)

See [plan-types.md](plan-types.md) for init phase router design.

**Init Phase Router**:
- [x] Implement init phase decision tree in plan-init skill
  - [x] Detect from command parameters (task, issue, type)
  - [x] Auto-detect from environment (branch name, build files)
  - [x] Prompt user if plan type cannot be determined
- [x] Implement progressive disclosure (load one init implementation per plan)

**Implementation Init** (see [plan-init/implementation.md](plan-init/implementation.md)):
- [x] Branch detection and validation
  - [x] Get current branch via `git branch --show-current`
  - [x] Validate not on main/master for implementation work
  - [x] Propose current if feature/fix/task/claude branch
- [x] Issue detection and analysis
  - [x] Parse from branch name: `feature/PROJ-123-desc` → `PROJ-123`
  - [x] Fetch issue details from GitHub/GitLab/Jira
  - [x] Pre-populate plan with issue content
- [x] Build system detection
  - [x] Scan for pom.xml → maven
  - [x] Scan for build.gradle → gradle
  - [x] Scan for package.json → npm/npx
- [x] Technology derivation from build system
- [x] Default values: compatibility=deprecations, commit-strategy=fine-granular, finalizing=pr-workflow
- [x] **Output**: 5-phase plan structure

**Simple Init** (see [plan-init/simple.md](plan-init/simple.md)):
- [x] Branch selection (current or main/master, no validation)
- [x] Default values: build-system=none, technology=none, finalizing=commit-only
- [x] Minimal user interaction (quick confirmation only)
- [x] **Output**: 3-phase plan structure

**Configuration Persistence** (both init types):
- [x] Write configuration block to plan.md header
- [x] Write complete phase structure to plan.md
- [x] Update references.md with issue and branch (Implementation only)

**User Confirmation Workflow**:
- [x] Present detected/defaulted configuration
- [x] Allow property overrides
- [x] Iterate on user feedback

**Create Operation** (plan-init skill):
- [x] Implement create operation (Bash + Write tools)
  - [x] Create plan directory with `mkdir -p .claude/plans/{task-name}/` (see [persistence.md](plan-files/persistence.md))
  - [x] Route to appropriate init implementation based on type
  - [x] Generate config.md with build and workflow configuration (see [persistence.md](plan-files/persistence.md))
  - [x] Generate plan.md (tasks-only) from init output (see [templates-workflow.md](templates-workflow.md))
  - [x] Initialize Phase Progress Table
  - [x] Set helper fields (current_phase based on init output, current_task: task-1)
  - [x] Create references.md with initial structure (see [persistence.md](plan-files/persistence.md))

### Refine Phase Support (plan-refine skill)

See [plan-refine/refine.md](plan-refine/refine.md) for complete specification.

**Skill Structure**:
- [x] Create `cui-task-workflow/skills/plan-refine/` directory
- [x] Create SKILL.md with analyze, plan-tasks, identify-docs operations
- [x] Create standards/implementation-requirements-template.md
- [x] Create README.md with skill documentation

**Analyze Operation** (see [refine.md](plan-refine/refine.md#step-2-analyze-requirements)):
- [x] Read plan.md for task description and context
- [x] Break down requirements into implementable components
- [x] Map dependencies between components
- [x] Estimate complexity per component
- [x] Present analysis to user via `AskUserQuestion` for confirmation

**Plan-Tasks Operation** (see [refine.md](plan-refine/refine.md#step-3-plan-implementation-tasks)):
- [x] Generate implementation tasks per component
- [x] Add standard checklists per technology (Java/JavaScript)
- [x] Define acceptance criteria from requirements
- [x] Order tasks by dependencies
- [x] Present task list to user via `AskUserQuestion` for review
- [x] Support task modification (add/remove/reorder)
- [x] Support granularity adjustment (split/merge)
- [x] Add tasks to plan.md implement phase
- [x] Update Phase Progress Table

**Identify-Docs Operation** (see [refine.md](plan-refine/refine.md#step-4-identify-documentation-needs)):
- [x] Check if ADRs needed for architectural decisions
- [x] Check if interface specs needed for new APIs
- [x] Prompt user via `AskUserQuestion` for decisions
- [x] Delegate to `adr-management` skill for ADR creation/linking
- [x] Delegate to `interface-management` skill for interface creation/linking
- [x] Update references.md with documentation needs

**Implementation Requirements Artifact** (see [template](plan-refine/implementation-requirements-template.md)):
- [x] Generate `implementation-requirements.md` on phase transition
- [x] Include component summary with complexity estimates
- [x] Include task details with implementation guidance
- [x] Include dependency graph visualization
- [x] Include references summary (ADRs, interfaces, code)
- [x] Include quality gates and commit strategy

### Implement Phase Support (plan-implement skill)

- [x] Implement execute-tasks operation
  - [x] Read current tasks from plan.md
  - [x] Execute tasks sequentially
  - [x] Mark tasks complete as they finish
- [x] Implement delegate operation
  - [x] Route to java-implement-agent for Java tasks
  - [x] Route to js-implement-agent for JavaScript tasks
  - [x] Pass task context and references
- [x] Implement track-progress operation
  - [x] Update plan.md with task completion
  - [x] Update references.md with created files
  - [x] Update Phase Progress Table

### Verify Phase Support (plan-verify skill)

- [x] Implement run-build operation
  - [x] Delegate to `maven-builder` or `npm-builder` agent
  - [x] Report build results
- [x] Implement check-quality operation
  - [x] Run linter/static analysis
  - [x] Check Sonar issues if applicable
  - [x] Report quality score
- [x] Implement review-docs operation
  - [x] Verify JavaDoc/JSDoc complete
  - [x] Check ADR/interface docs exist
  - [x] Update README if needed

### Finalize Phase Support (plan-finalize skill)

- [x] Implement commit operation
  - [x] Stage all changes
  - [x] Create commit with descriptive message
  - [x] Push to remote branch
- [x] Implement create-pr operation
  - [x] Create PR with summary
  - [x] Link to issue
  - [x] Add reviewers
- [x] Implement pr-workflow operation
  - [x] Delegate to `/pr-fix` for issue handling
  - [x] Address review comments
  - [x] Track PR status

### plan-files Skill (Persistence Layer)

All file operations are delegated to the `plan-files` skill. Phase skills call plan-files for all file I/O.

**Core Operations** (see [api.md](api.md#skill-plan-files)):
- [x] Implement create-directory operation (Bash tool)
  - [x] Create plan directory with `mkdir -p .claude/plans/{task-name}/`
- [x] Implement read-plan operation (Read tool)
  - [x] Read and parse plan.md (tasks-only)
  - [x] Extract current phase and tasks
  - [x] Return structured task data
- [x] Implement read-config operation (Read tool)
  - [x] Read and parse config.md
  - [x] Return technology, build-system, compatibility, etc.
- [x] Implement get-references operation (Read tool)
  - [x] Read and parse references.md
  - [x] Return ADRs, interfaces, files, external docs
- [x] Implement write-plan operation (Write/Edit tool)
  - [x] Create or update plan.md
  - [x] Add new tasks to appropriate phase
  - [x] Modify existing tasks
  - [x] Update Phase Progress Table when tasks added
- [x] Implement write-config operation (Write tool)
  - [x] Create config.md with build and workflow settings
- [x] Implement write-references operation (Write/Edit tool)
  - [x] Create or update references.md
  - [x] Add/modify file, ADR, interface references
- [x] Implement update-progress operation (Edit tool)
  - [x] Mark tasks complete (`[ ]` → `[x]`)
  - [x] Update checklist items
  - [x] Update Phase Progress Table

**Validation Operations**:
- [x] Implement validate operation (Read tool + validation)
  - [x] Validate plan.md structure
  - [x] Validate config.md completeness
  - [x] Validate references.md completeness
  - [x] Check all tasks have acceptance criteria
  - [x] Calculate quality score

### Phase Management (via plan-files skill)

Phase management operations delegate file I/O to `plan-files` skill:

- [x] Implement phase transition operation (see [api.md#phase-transition](api.md))
  - [x] Verify current phase completed (via `plan-files.read-plan`)
  - [x] Mark previous phase as completed (via `plan-files.update-progress`)
  - [x] Mark next phase as in_progress (via `plan-files.update-progress`)
  - [x] Update Current Phase field
  - [x] Update Current Task to first task of new phase
  - [x] Update Phase Progress Table
- [x] Implement task progress update operation (see [api.md#task-progress](api.md))
  - [x] Mark task complete in plan.md (via `plan-files.update-progress`)
  - [x] Update checklist items
  - [x] Update Phase Progress Table
  - [x] Check if all phase tasks completed
  - [x] Auto-trigger phase transition if phase complete
- [x] Implement phase transition rules (see [templates-workflow.md](templates-workflow.md))
  - [x] Sequential enforcement (init→refine→implement→verify→finalize)
  - [x] Completion validation (all tasks `[x]` before transition)
  - [x] Error handling for invalid transitions

### Reference Management (via plan-files skill)

Reference operations are handled by `plan-files` skill with delegation to documentation skills:

- [x] Implement get-references operation (via `plan-files.get-references`) (see [api.md](api.md))
  - [x] Retrieve issue and branch references
  - [x] Retrieve file references
  - [x] Retrieve external doc references
  - [x] Retrieve dependency references
  - [x] Delegate ADR retrieval to `adr-management` skill
  - [x] Delegate interface retrieval to `interface-management` skill
- [x] Implement manage-references operation (via `plan-files.write-references`) (see [api.md#manage-references](api.md))
  - [x] Add/update/remove file references
  - [x] Add/update/remove ADR references
  - [x] Add/update/remove interface references
  - [x] Add/update/remove external doc references
  - [x] Add/update/remove dependency references
- [x] Implement ADR verification via `adr-management` skill (see [architecture.md](architecture.md))
  - [x] Check ADR exists before adding reference
  - [x] Optionally create ADR if missing
- [x] Implement interface verification via `interface-management` skill (see [architecture.md](architecture.md))
  - [x] Check interface exists before adding reference
  - [x] Optionally create interface if missing

### Templates and Error Handling
- [x] Create plan.md template with 5 phases (see [templates-workflow.md](templates-workflow.md))
- [x] Create references.md template with 6 section types (see [persistence.md](plan-files/persistence.md))
- [x] Add error handling for all operations
  - [x] File not found errors
  - [x] Invalid structure errors
  - [x] Phase transition violations
  - [x] Reference not found errors
- [x] Add TOON error handoff responses (see [api.md](api.md))

### Quality Verification (Phase 1 Skills)
- [x] Run `/plugin-doctor` for `plan-init` skill
- [x] Run `/plugin-doctor` for `plan-refine` skill
- [x] Run `/plugin-doctor` for `plan-implement` skill
- [x] Run `/plugin-doctor` for `plan-verify` skill
- [x] Run `/plugin-doctor` for `plan-finalize` skill
- [x] Run `/plugin-doctor` for `plan-files` skill

---

## Phase 2: Update Commands

### Update /task-plan Command
- [ ] Add directory-based operation support
- [ ] Add parameter parsing:
  - [ ] task (for create)
  - [ ] plan (for refine/validate)
  - [ ] issue and branch (optional)
  - [ ] feedback (for refine)
  - [ ] add-reference (for reference management)
  - [ ] validate (flag)
- [ ] Generate TOON handoffs with directory paths (see [api.md](api.md))
- [ ] Delegate to appropriate phase skills (plan-init, plan-refine, etc.)
- [ ] Phase skills delegate file I/O to plan-files skill
- [ ] Format results for user
- [ ] Remove direct file I/O from command
- [ ] Test command-skill integration

### Update /task-implement Command
- [ ] Add plan directory parameter
- [ ] Delegate to plan-implement skill
- [ ] Plan-implement uses plan-files for reading plan/config/references
- [ ] Parse references from skill response
- [ ] Use references for context (ADRs, interfaces, files)
- [ ] Update progress via plan-files skill
- [ ] Remove direct file I/O from command
- [ ] Test command-skill integration

### Quality Verification (Phase 2 Commands)
- [ ] Run `/plugin-doctor` for `task-plan` command
- [ ] Run `/plugin-doctor` for `task-implement` command

---

## Phase 3: Update Related Skills

### Update task-execute Skill
- [ ] Delegate progress updates to plan-files skill
- [ ] Use directory paths in handoffs
- [ ] Update task completion via `plan-files.update-progress`
- [ ] Remove direct plan file I/O
- [ ] Test skill-skill integration

### Update task-review Skill (if exists)
- [ ] Delegate validation to plan-files skill
- [ ] Validate plan.md via `plan-files.read-plan`
- [ ] Validate config.md via `plan-files.read-config`
- [ ] Validate references.md via `plan-files.get-references`
- [ ] Remove direct plan file I/O
- [ ] Test skill-skill integration

### Quality Verification (Phase 3 Skills)
- [ ] Run `/plugin-doctor` for `task-execute` skill
- [ ] Run `/plugin-doctor` for `task-review` skill (if updated)

---

## Phase 4: Integration with Documentation Skills

### Test ADR Integration
- [ ] Test ADR reference flow (see [architecture.md](architecture.md))
  - [ ] Verify ADR exists before adding reference
  - [ ] Create ADR if requested
  - [ ] Update references.md with ADR link
- [ ] Test validation with ADR references
- [ ] Test error handling (ADR not found)
- [ ] Add integration tests

### Test Interface Integration
- [ ] Test interface reference flow (see [architecture.md](architecture.md))
  - [ ] Verify interface exists before adding reference
  - [ ] Create interface if requested
  - [ ] Update references.md with interface link
- [ ] Test validation with interface references
- [ ] Test error handling (interface not found)
- [ ] Add integration tests

### Skill Delegation Tests
- [ ] Test phase skill → plan-files handoffs
- [ ] Test plan-files → adr-management handoffs
- [ ] Test plan-files → interface-management handoffs
- [ ] Test error propagation across skills
- [ ] Test TOON handoff chains

---

## Phase 5: Documentation and Testing

### Documentation Updates
- [ ] Update all architectural documents with directory structure
- [ ] Update command documentation with new parameters
- [ ] Update skill documentation with directory paths
- [ ] Create example plan directories
- [ ] Update README files

### Testing
- [ ] Unit tests for plan.md parsing
- [ ] Unit tests for references.md parsing
- [ ] Unit tests for phase management
- [ ] Unit tests for phase transition rules
- [ ] Integration tests for complete workflows
- [ ] Error scenario tests
- [ ] TOON handoff validation tests
- [ ] Performance tests (large plans)

### Example Creation
- [ ] Create example JWT auth plan directory
- [ ] Create example refactoring plan directory
- [ ] Create example feature plan directory
- [ ] Document best practices for plan creation
