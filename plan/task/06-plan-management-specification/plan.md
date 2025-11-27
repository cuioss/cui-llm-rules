# Implementation Plan

Tasks for implementing the plan management system. See related documents for details:

- [Plan Types](plan-types.md) - Init phase router and configuration
- [Refine Phase](plan-refine/refine.md) - Refine phase specification
- [Implementation Requirements Template](plan-refine/implementation-requirements-template.md) - Runtime artifact template
- [Architecture](architecture.md) - Abstraction layer design
- [Persistence](plan-files/persistence.md) - File structure and directory organization
- [Templates & Workflow](templates-workflow.md) - Plan templates and phase-based workflow
- [API Specification](api.md) - Complete skill API with TOON handoffs
- [Decomposition](decomposition.md) - Implementation details and usage examples

---

## Phase 1: Create Phase Skills (One Skill Per Phase)

### Directory Structure Support

**plan-init skill** (init phase):
- [ ] Create `cui-task-workflow/skills/plan-init/` directory
- [ ] Create SKILL.md with create operation and type routing (see [api.md](api.md))
- [ ] Create plan-init/ directory with init implementations
- [ ] Create README.md with skill documentation

**plan-refine skill** (refine phase):
- [ ] Create `cui-task-workflow/skills/plan-refine/` directory
- [ ] Create SKILL.md with analyze, plan-tasks, identify-docs operations
- [ ] Create README.md with skill documentation

**plan-implement skill** (implement phase):
- [ ] Create `cui-task-workflow/skills/plan-implement/` directory
- [ ] Create SKILL.md with execute-tasks, delegate, track-progress operations
- [ ] Create README.md with skill documentation

**plan-verify skill** (verify phase):
- [ ] Create `cui-task-workflow/skills/plan-verify/` directory
- [ ] Create SKILL.md with run-build, check-quality, review-docs operations
- [ ] Create README.md with skill documentation

**plan-finalize skill** (finalize phase):
- [ ] Create `cui-task-workflow/skills/plan-finalize/` directory
- [ ] Create SKILL.md with commit, create-pr, pr-workflow operations
- [ ] Create README.md with skill documentation

**plan-files skill** (persistence layer):
- [ ] Create `cui-task-workflow/skills/plan-files/` directory
- [ ] Create SKILL.md with persistence operations (see [api.md](api.md#skill-plan-files))
  - [ ] create-directory - Create plan directory structure
  - [ ] read-plan - Read plan.md (tasks, phases, status)
  - [ ] read-config - Read config.md (technology, build system, etc.)
  - [ ] get-references - Read references.md (ADRs, interfaces, files)
  - [ ] write-plan - Write/update plan.md
  - [ ] write-config - Write config.md
  - [ ] write-references - Write/update references.md
  - [ ] update-progress - Mark tasks complete, update phase table
- [ ] Create README.md with skill documentation

**Shared templates**:
- [ ] Create `cui-task-workflow/skills/plan-init/standards/` directory
- [ ] Create plan-template.md (see [templates-workflow.md](templates-workflow.md))
- [ ] Create references-template.md (see [persistence.md](plan-files/persistence.md))

### Init Phase Support (plan-init skill)

See [plan-types.md](plan-types.md) for init phase router design.

**Init Phase Router**:
- [ ] Implement init phase decision tree in plan-init skill
  - [ ] Detect from command parameters (task, issue, type)
  - [ ] Auto-detect from environment (branch name, build files)
  - [ ] Prompt user if plan type cannot be determined
- [ ] Implement progressive disclosure (load one init implementation per plan)

**Implementation Init** (see [plan-init/implementation.md](plan-init/implementation.md)):
- [ ] Branch detection and validation
  - [ ] Get current branch via `git branch --show-current`
  - [ ] Validate not on main/master for implementation work
  - [ ] Propose current if feature/fix/task/claude branch
- [ ] Issue detection and analysis
  - [ ] Parse from branch name: `feature/PROJ-123-desc` → `PROJ-123`
  - [ ] Fetch issue details from GitHub/GitLab/Jira
  - [ ] Pre-populate plan with issue content
- [ ] Build system detection
  - [ ] Scan for pom.xml → maven
  - [ ] Scan for build.gradle → gradle
  - [ ] Scan for package.json → npm/npx
- [ ] Technology derivation from build system
- [ ] Default values: compatibility=deprecations, commit-strategy=fine-granular, finalizing=pr-workflow
- [ ] **Output**: 5-phase plan structure

**Simple Init** (see [plan-init/simple.md](plan-init/simple.md)):
- [ ] Branch selection (current or main/master, no validation)
- [ ] Default values: build-system=none, technology=none, finalizing=commit-only
- [ ] Minimal user interaction (quick confirmation only)
- [ ] **Output**: 3-phase plan structure

**Configuration Persistence** (both init types):
- [ ] Write configuration block to plan.md header
- [ ] Write complete phase structure to plan.md
- [ ] Update references.md with issue and branch (Implementation only)

**User Confirmation Workflow**:
- [ ] Present detected/defaulted configuration
- [ ] Allow property overrides
- [ ] Iterate on user feedback

**Create Operation** (plan-init skill):
- [ ] Implement create operation (Bash + Write tools)
  - [ ] Create plan directory with `mkdir -p .claude/plans/{task-name}/` (see [persistence.md](plan-files/persistence.md))
  - [ ] Route to appropriate init implementation based on type
  - [ ] Generate config.md with build and workflow configuration (see [persistence.md](plan-files/persistence.md))
  - [ ] Generate plan.md (tasks-only) from init output (see [templates-workflow.md](templates-workflow.md))
  - [ ] Initialize Phase Progress Table
  - [ ] Set helper fields (current_phase based on init output, current_task: task-1)
  - [ ] Create references.md with initial structure (see [persistence.md](plan-files/persistence.md))

### Refine Phase Support (plan-refine skill)

See [plan-refine/refine.md](plan-refine/refine.md) for complete specification.

**Skill Structure**:
- [ ] Create `cui-task-workflow/skills/plan-refine/` directory
- [ ] Create SKILL.md with analyze, plan-tasks, identify-docs operations
- [ ] Create standards/implementation-requirements-template.md
- [ ] Create README.md with skill documentation

**Analyze Operation** (see [refine.md](plan-refine/refine.md#step-2-analyze-requirements)):
- [ ] Read plan.md for task description and context
- [ ] Break down requirements into implementable components
- [ ] Map dependencies between components
- [ ] Estimate complexity per component
- [ ] Present analysis to user via `AskUserQuestion` for confirmation

**Plan-Tasks Operation** (see [refine.md](plan-refine/refine.md#step-3-plan-implementation-tasks)):
- [ ] Generate implementation tasks per component
- [ ] Add standard checklists per technology (Java/JavaScript)
- [ ] Define acceptance criteria from requirements
- [ ] Order tasks by dependencies
- [ ] Present task list to user via `AskUserQuestion` for review
- [ ] Support task modification (add/remove/reorder)
- [ ] Support granularity adjustment (split/merge)
- [ ] Add tasks to plan.md implement phase
- [ ] Update Phase Progress Table

**Identify-Docs Operation** (see [refine.md](plan-refine/refine.md#step-4-identify-documentation-needs)):
- [ ] Check if ADRs needed for architectural decisions
- [ ] Check if interface specs needed for new APIs
- [ ] Prompt user via `AskUserQuestion` for decisions
- [ ] Delegate to `adr-management` skill for ADR creation/linking
- [ ] Delegate to `interface-management` skill for interface creation/linking
- [ ] Update references.md with documentation needs

**Implementation Requirements Artifact** (see [template](plan-refine/implementation-requirements-template.md)):
- [ ] Generate `implementation-requirements.md` on phase transition
- [ ] Include component summary with complexity estimates
- [ ] Include task details with implementation guidance
- [ ] Include dependency graph visualization
- [ ] Include references summary (ADRs, interfaces, code)
- [ ] Include quality gates and commit strategy

### Implement Phase Support (plan-implement skill)

- [ ] Implement execute-tasks operation
  - [ ] Read current tasks from plan.md
  - [ ] Execute tasks sequentially
  - [ ] Mark tasks complete as they finish
- [ ] Implement delegate operation
  - [ ] Route to java-implement-agent for Java tasks
  - [ ] Route to js-implement-agent for JavaScript tasks
  - [ ] Pass task context and references
- [ ] Implement track-progress operation
  - [ ] Update plan.md with task completion
  - [ ] Update references.md with created files
  - [ ] Update Phase Progress Table

### Verify Phase Support (plan-verify skill)

- [ ] Implement run-build operation
  - [ ] Delegate to `maven-builder` or `npm-builder` agent
  - [ ] Report build results
- [ ] Implement check-quality operation
  - [ ] Run linter/static analysis
  - [ ] Check Sonar issues if applicable
  - [ ] Report quality score
- [ ] Implement review-docs operation
  - [ ] Verify JavaDoc/JSDoc complete
  - [ ] Check ADR/interface docs exist
  - [ ] Update README if needed

### Finalize Phase Support (plan-finalize skill)

- [ ] Implement commit operation
  - [ ] Stage all changes
  - [ ] Create commit with descriptive message
  - [ ] Push to remote branch
- [ ] Implement create-pr operation
  - [ ] Create PR with summary
  - [ ] Link to issue
  - [ ] Add reviewers
- [ ] Implement pr-workflow operation
  - [ ] Delegate to `/pr-fix` for issue handling
  - [ ] Address review comments
  - [ ] Track PR status

### plan-files Skill (Persistence Layer)

All file operations are delegated to the `plan-files` skill. Phase skills call plan-files for all file I/O.

**Core Operations** (see [api.md](api.md#skill-plan-files)):
- [ ] Implement create-directory operation (Bash tool)
  - [ ] Create plan directory with `mkdir -p .claude/plans/{task-name}/`
- [ ] Implement read-plan operation (Read tool)
  - [ ] Read and parse plan.md (tasks-only)
  - [ ] Extract current phase and tasks
  - [ ] Return structured task data
- [ ] Implement read-config operation (Read tool)
  - [ ] Read and parse config.md
  - [ ] Return technology, build-system, compatibility, etc.
- [ ] Implement get-references operation (Read tool)
  - [ ] Read and parse references.md
  - [ ] Return ADRs, interfaces, files, external docs
- [ ] Implement write-plan operation (Write/Edit tool)
  - [ ] Create or update plan.md
  - [ ] Add new tasks to appropriate phase
  - [ ] Modify existing tasks
  - [ ] Update Phase Progress Table when tasks added
- [ ] Implement write-config operation (Write tool)
  - [ ] Create config.md with build and workflow settings
- [ ] Implement write-references operation (Write/Edit tool)
  - [ ] Create or update references.md
  - [ ] Add/modify file, ADR, interface references
- [ ] Implement update-progress operation (Edit tool)
  - [ ] Mark tasks complete (`[ ]` → `[x]`)
  - [ ] Update checklist items
  - [ ] Update Phase Progress Table

**Validation Operations**:
- [ ] Implement validate operation (Read tool + validation)
  - [ ] Validate plan.md structure
  - [ ] Validate config.md completeness
  - [ ] Validate references.md completeness
  - [ ] Check all tasks have acceptance criteria
  - [ ] Calculate quality score

### Phase Management (via plan-files skill)

Phase management operations delegate file I/O to `plan-files` skill:

- [ ] Implement phase transition operation (see [api.md#phase-transition](api.md))
  - [ ] Verify current phase completed (via `plan-files.read-plan`)
  - [ ] Mark previous phase as completed (via `plan-files.update-progress`)
  - [ ] Mark next phase as in_progress (via `plan-files.update-progress`)
  - [ ] Update Current Phase field
  - [ ] Update Current Task to first task of new phase
  - [ ] Update Phase Progress Table
- [ ] Implement task progress update operation (see [api.md#task-progress](api.md))
  - [ ] Mark task complete in plan.md (via `plan-files.update-progress`)
  - [ ] Update checklist items
  - [ ] Update Phase Progress Table
  - [ ] Check if all phase tasks completed
  - [ ] Auto-trigger phase transition if phase complete
- [ ] Implement phase transition rules (see [templates-workflow.md](templates-workflow.md))
  - [ ] Sequential enforcement (init→refine→implement→verify→finalize)
  - [ ] Completion validation (all tasks `[x]` before transition)
  - [ ] Error handling for invalid transitions

### Reference Management (via plan-files skill)

Reference operations are handled by `plan-files` skill with delegation to documentation skills:

- [ ] Implement get-references operation (via `plan-files.get-references`) (see [api.md](api.md))
  - [ ] Retrieve issue and branch references
  - [ ] Retrieve file references
  - [ ] Retrieve external doc references
  - [ ] Retrieve dependency references
  - [ ] Delegate ADR retrieval to `adr-management` skill
  - [ ] Delegate interface retrieval to `interface-management` skill
- [ ] Implement manage-references operation (via `plan-files.write-references`) (see [api.md#manage-references](api.md))
  - [ ] Add/update/remove file references
  - [ ] Add/update/remove ADR references
  - [ ] Add/update/remove interface references
  - [ ] Add/update/remove external doc references
  - [ ] Add/update/remove dependency references
- [ ] Implement ADR verification via `adr-management` skill (see [architecture.md](architecture.md))
  - [ ] Check ADR exists before adding reference
  - [ ] Optionally create ADR if missing
- [ ] Implement interface verification via `interface-management` skill (see [architecture.md](architecture.md))
  - [ ] Check interface exists before adding reference
  - [ ] Optionally create interface if missing

### Templates and Error Handling
- [ ] Create plan.md template with 5 phases (see [templates-workflow.md](templates-workflow.md))
- [ ] Create references.md template with 6 section types (see [persistence.md](plan-files/persistence.md))
- [ ] Add error handling for all operations
  - [ ] File not found errors
  - [ ] Invalid structure errors
  - [ ] Phase transition violations
  - [ ] Reference not found errors
- [ ] Add TOON error handoff responses (see [api.md](api.md))

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
