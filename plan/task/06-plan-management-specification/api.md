# API Specification

Complete skill API with all operations and TOON handoff interfaces for plan management.

## Overview

Plan management uses **one skill per phase** plus a **dedicated persistence skill**:

| Skill | Purpose | Key Operations |
|-------|---------|----------------|
| [plan-files](#skill-plan-files) | **Persistence** | read-plan, read-config, get-references, write-plan, write-config, write-references |
| [plan-init](#skill-plan-init) | Init phase | create, detect-environment, configure |
| [plan-refine](#skill-plan-refine) | Refine phase | analyze, plan-tasks, identify-docs |
| [plan-implement](#skill-plan-implement) | Implement phase | execute-tasks, delegate, track-progress |
| [plan-verify](#skill-plan-verify) | Verify phase | run-build, check-quality, review-docs |
| [plan-finalize](#skill-plan-finalize) | Finalize phase | commit, create-pr, pr-workflow |

**Architecture**:
```
Phase Skills                    Persistence Skill
┌─────────────┐                ┌──────────────┐
│ plan-init   │──────────────▶│              │
├─────────────┤                │              │
│ plan-refine │──────────────▶│  plan-files  │──▶ .claude/plans/
├─────────────┤                │              │
│ plan-impl   │──────────────▶│              │
├─────────────┤                │              │
│ plan-verify │──────────────▶│              │
├─────────────┤                │              │
│ plan-final  │──────────────▶└──────────────┘
└─────────────┘
```

**Communication Protocol**: All operations use TOON handoff format for input/output

**File System**: All file I/O goes through `plan-files` skill

**Phase Flow**: Each phase skill handles its logic, delegates file operations to `plan-files`

---

## Skill: plan-files

The `plan-files` skill is the **dedicated persistence layer** for all plan file operations. All phase skills delegate file I/O to this skill.

**Purpose**: Centralize all file operations for plan management

**Operations**:
| Operation | Purpose | Tool |
|-----------|---------|------|
| create-directory | Create plan directory structure | Bash |
| read-plan | Read plan.md (tasks-only) | Read |
| read-config | Read config.md | Read |
| get-references | Read references.md | Read |
| write-plan | Write/update plan.md | Write/Edit |
| write-config | Write config.md | Write |
| write-references | Write/update references.md | Write/Edit |
| update-progress | Mark tasks complete, update phase table | Edit |

### Operation: Create Directory

**Purpose**: Create plan directory structure

```toon
# Input
from: plan-init-skill
to: plan-files-skill
handoff_id: mkdir-001

task_name: jwt-auth
next_action: Create plan directory

# Output
artifacts:
  plan_directory: .claude/plans/jwt-auth/
```

**File Operations**: Uses `Bash` tool: `mkdir -p .claude/plans/{task-name}/`

---

### Operation: Read Plan

**Purpose**: Read and parse plan.md (tasks-only)

```toon
# Input
from: caller
to: plan-files-skill
handoff_id: read-plan-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

# Output
plan_status:
  current_phase: implement
  current_task: task-6
  overall_status: in_progress

phases[5]{name,status,tasks,completed}:
init,completed,3,3/3
refine,completed,2,2/2
implement,in_progress,5,2/5
verify,pending,3,0/3
finalize,pending,2,0/2

tasks_current_phase[5]{id,name,status}:
task-6,Create JwtService,completed
task-7,Create TokenValidator,completed
task-8,Implement RefreshTokenService,in_progress
```

**File Operations**: Uses `Read` tool to read and parse `plan.md`

---

### Operation: Read Config

**Purpose**: Read configuration from config.md

```toon
# Input
from: caller
to: plan-files-skill
handoff_id: config-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

# Output
configuration:
  plan_type: implementation
  technology: java
  build_system: maven
  compatibility: deprecations
  commit_strategy: fine-granular
  finalizing: pr-workflow
  branch: feature/jwt-auth
  issue: "#123 - Add JWT Authentication"
```

**File Operations**: Uses `Read` tool to read and parse `config.md`

---

### Operation: Get References

**Purpose**: Read references from references.md

```toon
# Input
from: caller
to: plan-files-skill
handoff_id: refs-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

# Output
references:
  issue:
    url: "https://github.com/org/repo/issues/123"
    title: "Add JWT Authentication"
  branch: "feature/jwt-auth"
  adrs[2]: "ADR-015", "ADR-020"
  interfaces[2]: "IF-042", "IF-051"
  implementation_files[3]: "JwtService.java", "TokenValidator.java"
```

**File Operations**: Uses `Read` tool to read and parse `references.md`

---

### Operation: Write Config

**Purpose**: Write configuration to config.md (called by plan-init)

```toon
# Input
from: plan-init-skill
to: plan-files-skill
handoff_id: write-config-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

configuration:
  plan_type: implementation
  technology: java
  build_system: maven
  # ... all config fields
```

**File Operations**: Uses `Write` tool to create `config.md`

---

### Operation: Update Progress

**Purpose**: Update task/phase progress in plan.md

```toon
# Input
from: caller
to: plan-files-skill
handoff_id: progress-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

update:
  task_id: task-8
  status: completed

# Output
plan_status:
  current_phase: implement
  current_task: task-9
  phase_complete: false
```

**File Operations**: Uses `Edit` tool to update `plan.md` (checkboxes, phase table)

---

## Skill: plan-init

The `plan-init` skill handles plan creation with type-specific init workflows. **Delegates all file I/O to `plan-files` skill.**

#### Operation: Create Plan

**Purpose**: Create a new plan directory with plan.md, config.md, and references.md files

**Type Routing**: Routes to init implementation based on plan type:
- `implementation` → [plan-init/implementation.md](plan-init/implementation.md) → 5-phase plan
- `simple` → [plan-init/simple.md](plan-init/simple.md) → 3-phase plan

### Input (TOON Handoff)

```toon
from: task-plan-command
to: plan-init-skill
handoff_id: create-001
workflow: plan-creation

task:
  description: Implement JWT authentication service
  type: plan
  status: pending

context:
  source_type: description|issue|url
  source: [task description or issue reference]
  issue_url: https://github.com/org/repo/issues/123
  branch: feature/jwt-auth

next_action: Create structured plan with references
```

### Output (TOON Handoff)

```toon
from: plan-init-skill
to: task-plan-command
handoff_id: create-002
workflow: plan-creation

task:
  description: Plan directory created
  status: completed

plan_type: implementation

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  plan_file: .claude/plans/jwt-auth/plan.md
  config_file: .claude/plans/jwt-auth/config.md
  references_file: .claude/plans/jwt-auth/references.md
  task_count: 15
  phase_count: 5

plan_status:
  current_phase: refine
  current_task: task-1
  overall_status: in_progress

phases[5]{name,status,tasks,completed}:
init,completed,5,5/5
refine,in_progress,3,0/3
implement,pending,5,0/5
verify,pending,4,0/4
finalize,pending,3,0/3

configuration:
  technology: java
  build_system: maven
  compatibility: deprecations
  commit_strategy: fine-granular
  finalizing: pr-workflow
  branch: feature/jwt-auth
  issue: "#123 - Add JWT Authentication"

next_action: Start init phase
next_focus: Task 1: Define project structure
```

### File Operations (via plan-files skill)

Delegates all file operations to `plan-files` skill:
1. `plan-files.create-directory` → Create `.claude/plans/{task-name}/`
2. `plan-files.write-config` → Write `config.md`
3. `plan-files.write-plan` → Write `plan.md` (tasks-only)
4. `plan-files.write-references` → Write `references.md`

See [persistence.md](plan-files/persistence.md) for file format specifications.

---

## Skill: plan-refine

The `plan-refine` skill handles the refine phase: analyzing requirements, planning implementation tasks, and identifying documentation needs.

**Detailed Specification**: See [plan-refine/refine.md](plan-refine/refine.md) for complete workflow

**Operations**:
- `analyze` - Break down requirements into components
- `plan-tasks` - Create detailed implementation tasks
- `identify-docs` - Determine ADR/interface needs

**Output Artifact**: `implementation-requirements.md` - See [template](plan-refine/implementation-requirements-template.md)

### Operation: Analyze Requirements

**Purpose**: Break down task requirements into implementable units

### Input (TOON Handoff)

```toon
from: orchestrator
to: plan-refine-skill
handoff_id: refine-001
workflow: requirements-analysis

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Analyze requirements and plan tasks
```

### Output (TOON Handoff)

```toon
from: plan-refine-skill
to: orchestrator
handoff_id: refine-002
workflow: requirements-analysis

task:
  description: Requirements analyzed
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/

implementation_tasks[5]{id,name,complexity}:
task-1,Create JwtService,medium
task-2,Create TokenValidator,medium
task-3,Implement RefreshTokenService,high
task-4,Add JWT configuration,low
task-5,Update POM dependencies,low

documentation_needs:
  adrs_needed[1]: "JWT Authentication Strategy"
  interfaces_needed[1]: "Authentication Service Interface"

next_action: Transition to implement phase
```

### File Operations (via plan-files skill)

Delegates all file operations to `plan-files` skill:
- `plan-files.read-plan` → Read plan.md for current tasks
- `plan-files.read-config` → Read config.md for technology settings
- `plan-files.get-references` → Read references.md for context
- `plan-files.write-plan` → Add implementation tasks to implement phase
- `plan-files.write-references` → Update references.md with ADR/interface needs
- `plan-files.update-progress` → Transition to implement phase when complete

---

## Skill: plan-implement

The `plan-implement` skill handles the implement phase: executing implementation tasks and delegating to language agents.

### Operation: Execute Tasks

**Purpose**: Execute implementation tasks with appropriate language agents

### Input (TOON Handoff)

```toon
from: orchestrator
to: plan-implement-skill
handoff_id: implement-001
workflow: task-execution

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Execute implementation tasks
```

### Output (TOON Handoff)

```toon
from: plan-implement-skill
to: orchestrator
handoff_id: implement-002
workflow: task-execution

task:
  description: Implementation complete
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/

tasks_completed[5]{id,name,files_created}:
task-1,Create JwtService,JwtService.java
task-2,Create TokenValidator,TokenValidator.java
task-3,Implement RefreshTokenService,RefreshTokenService.java
task-4,Add JWT configuration,application.properties
task-5,Update POM dependencies,pom.xml

next_action: Transition to verify phase
```

### File Operations (via plan-files skill)

Delegates all file operations to `plan-files` skill:
- `plan-files.read-plan` → Read plan.md for current tasks
- `plan-files.read-config` → Read config.md for technology/build settings
- `plan-files.get-references` → Read references.md for context
- `plan-files.update-progress` → Mark tasks complete
- `plan-files.write-references` → Update references.md with created files

**Delegation to language agents**: java-implement-agent, js-implement-agent

---

## Skill: plan-verify

The `plan-verify` skill handles the verify phase: running builds, quality checks, and documentation review.

### Operation: Run Verification

**Purpose**: Verify implementation with builds, tests, and quality checks

### Input (TOON Handoff)

```toon
from: orchestrator
to: plan-verify-skill
handoff_id: verify-001
workflow: verification

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Run verification checks
```

### Output (TOON Handoff)

```toon
from: plan-verify-skill
to: orchestrator
handoff_id: verify-002
workflow: verification

task:
  description: Verification complete
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/

verification_results:
  build: passed
  tests: passed
  coverage: 85%
  quality_score: 92

issues_found[0]:

next_action: Transition to finalize phase
```

### File Operations (via plan-files skill)

Delegates all file operations to `plan-files` skill:
- `plan-files.read-plan` → Read plan.md for verification tasks
- `plan-files.read-config` → Read config.md for build system settings
- `plan-files.update-progress` → Mark verification tasks complete

**Delegation to build agents**: maven-builder, npm-builder

---

## Skill: plan-finalize

The `plan-finalize` skill handles the finalize phase: committing changes, creating PRs, and handling PR workflow.

### Operation: Finalize and PR

**Purpose**: Commit changes and create/update pull request

### Input (TOON Handoff)

```toon
from: orchestrator
to: plan-finalize-skill
handoff_id: finalize-001
workflow: finalization

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Commit and create PR
```

### Output (TOON Handoff)

```toon
from: plan-finalize-skill
to: orchestrator
handoff_id: finalize-002
workflow: finalization

task:
  description: Plan finalized
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/

finalization_results:
  commits_created: 3
  pr_url: "https://github.com/org/repo/pull/456"
  pr_status: open

next_action: Plan complete - awaiting PR review
```

### File Operations (via plan-files skill)

Delegates all file operations to `plan-files` skill:
- `plan-files.read-plan` → Read plan.md for finalization tasks
- `plan-files.read-config` → Read config.md for branch/commit settings
- `plan-files.update-progress` → Mark plan as completed

**Git operations**: Uses `Bash` tool for commit, push (not delegated to plan-files)

**Delegation to pr-workflow skill**: For PR creation and management

---

## Common Operations

All file operations are delegated to the **`plan-files` skill**. See [Skill: plan-files](#skill-plan-files) for complete operation documentation.

| Operation | Skill Call | Purpose |
|-----------|------------|---------|
| Read plan tasks | `plan-files.read-plan` | Get phases, tasks, status |
| Read configuration | `plan-files.read-config` | Get technology, build system, etc. |
| Get references | `plan-files.get-references` | Get ADRs, interfaces, files |
| Update progress | `plan-files.update-progress` | Mark tasks complete |
| Write plan | `plan-files.write-plan` | Create/update plan.md |

---

## Plan-Level Operations

These operations are for plan-level changes (not file I/O). They delegate file operations to `plan-files` skill.

### Operation: Refine Plan

**Purpose**: Iteratively refine existing plan based on feedback

### Input (TOON Handoff)

```toon
from: task-plan-command
to: task-plan-skill
handoff_id: refine-001
workflow: plan-refinement

artifacts:
  plan_directory: .claude/plans/jwt-auth/

refinements:
  type: add_task|modify_task|add_criteria|add_reference
  details: [refinement details]

context:
  feedback: User wants to add refresh token rotation
  reason: Security requirement

next_action: Update plan with refinements
```

### Output (TOON Handoff)

```toon
from: task-plan-skill
to: task-plan-command
handoff_id: refine-002
workflow: plan-refinement

task:
  description: Plan refined
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  plan_file: .claude/plans/jwt-auth/plan.md
  references_file: .claude/plans/jwt-auth/references.md

changes[2]:
- Added Task 3: Implement refresh token rotation
- Updated Task 2 acceptance criteria: Add token revocation check

next_action: Review refined plan
```

### File Operations (via plan-files)

Delegates to `plan-files` skill for file modifications:
- `plan-files.write-plan` → Update plan.md with new/modified tasks
- `plan-files.write-references` → Update references.md if needed

---

### Operation: Validate Plan

**Purpose**: Validate plan structure and completeness (both plan.md and references.md)

### Input (TOON Handoff)

```toon
from: task-plan-command
to: task-plan-skill
handoff_id: validate-001
workflow: plan-validation

artifacts:
  plan_directory: .claude/plans/jwt-auth/

validation_rules:
  check_structure: true
  check_acceptance_criteria: true
  check_completeness: true
  check_references: true

next_action: Validate plan and references quality
```

### Output (TOON Handoff)

```toon
from: task-plan-skill
to: task-plan-command
handoff_id: validate-002
workflow: plan-validation

task:
  description: Validation complete
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  plan_file: .claude/plans/jwt-auth/plan.md
  references_file: .claude/plans/jwt-auth/references.md

validation_results:
  structure_valid: true
  has_acceptance_criteria: true
  is_complete: true
  references_complete: true
  quality_score: 95

issues[1]:
- Task 2 missing dependency information

recommendations[3]:
- Add dependency: Task 2 depends on Task 1
- Consider adding edge cases to Task 3
- Add interface specification for token validation API

next_action: Address validation issues if any
```

### File Operations (via plan-files)

Uses `plan-files` skill for reading (no modifications):
- `plan-files.read-plan` → Read and validate plan.md structure
- `plan-files.read-config` → Read and validate config.md
- `plan-files.get-references` → Read and validate references.md

---

### Operation: Phase Transition

**Purpose**: Transition to the next phase when current phase is completed

### Input (TOON Handoff)

```toon
from: task-execute-skill
to: task-plan-skill
handoff_id: phase-001
workflow: phase-transition

artifacts:
  plan_directory: .claude/plans/jwt-auth/

phase_transition:
  current_phase: refine
  next_phase: implement
  reason: All refine tasks completed

next_action: Transition to implementation phase
```

### Output (TOON Handoff)

```toon
from: task-plan-skill
to: task-execute-skill
handoff_id: phase-002
workflow: phase-transition

task:
  description: Phase transition complete
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  plan_file: .claude/plans/jwt-auth/plan.md

plan_status:
  previous_phase: refine
  current_phase: implement
  current_task: task-6
  overall_status: in_progress

phases[5]{name,status,tasks,completed}:
init,completed,3,3/3
refine,completed,2,2/2
implement,in_progress,5,0/5
verify,pending,3,0/3
finalize,pending,2,0/2

next_action: Start first task of implement phase
next_focus: Task 6: Create JwtService
```

### Phase Transition Rules

**Sequential Progression**:
- Can only transition if current phase is completed (all tasks done)
- Cannot skip phases (must go sequentially: init → refine → implement → verify → finalize)
- Automatically updates Current Phase and Current Task fields
- Updates Phase Progress Table

**Validation**:
- Verifies all tasks in current phase are marked `[x]`
- Checks phase completion percentage is 100%
- Validates next phase is sequential

### File Operations (via plan-files skill)

Delegates all file operations to `plan-files` skill:
- `plan-files.read-plan` → Read current phase status
- `plan-files.update-progress` → Mark previous phase completed, next phase in_progress
- Updates Current Phase and Current Task headers
- Updates Phase Progress Table

---

### Operation: Task Progress Update

**Purpose**: Update task and checklist progress, handle phase completion

### Input (TOON Handoff)

```toon
from: task-execute-skill
to: task-plan-skill
handoff_id: progress-001
workflow: task-progress

artifacts:
  plan_directory: .claude/plans/jwt-auth/

task_update:
  task_id: task-8
  phase: implement
  status: completed
  checklist_items_completed[5]: 0,1,2,3,4

next_action: Mark task complete and check phase status
```

### Output (TOON Handoff)

```toon
from: task-plan-skill
to: task-execute-skill
handoff_id: progress-002
workflow: task-progress

task:
  description: Task progress updated
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  plan_file: .claude/plans/jwt-auth/plan.md

plan_status:
  current_phase: implement
  current_task: task-9
  overall_status: in_progress

phase_status:
  phase: implement
  status: in_progress
  tasks_total: 5
  tasks_completed: 3
  completion_percentage: 60
  phase_ready_for_transition: false

tasks_remaining_in_phase[2]{id,name}:
task-9,Add JWT configuration
task-10,Update POM dependencies

next_action: Continue to next task in phase
next_focus: Task 9: Add JWT configuration
```

### Auto Phase Transition

When the last task in a phase is completed, automatic phase transition is triggered:

```toon
# If last task in phase is completed:

phase_status:
  phase: implement
  status: completed
  tasks_total: 5
  tasks_completed: 5
  completion_percentage: 100
  phase_ready_for_transition: true
  next_phase: verify

next_action: Phase implementation completed
next_focus: Transition to verify phase
```

### File Operations (via plan-files skill)

Delegates all file operations to `plan-files` skill:
- `plan-files.update-progress` → Mark task complete, update checklist items
- Updates Phase Progress Table
- Checks if all phase tasks completed
- If phase complete, marks phase as completed
- Updates Current Task to next task or "phase-complete"

---

### Operation: Manage References

**Purpose**: Add, update, or remove references (files, ADRs, interfaces, external docs)

### Input (TOON Handoff)

```toon
from: task-plan-command
to: task-plan-skill
handoff_id: ref-001
workflow: reference-management

artifacts:
  plan_directory: .claude/plans/jwt-auth/

reference_update:
  action: add|update|remove
  type: file|adr|interface|external|dependency
  details:
    - type: adr
      identifier: ADR-015
      title: JWT Authentication Strategy
      path: .claude/adrs/ADR-015-jwt-authentication-strategy.adoc
    - type: interface
      identifier: IF-042
      title: Authentication Service Interface
      path: doc/interfaces/IF-042-authentication-service.adoc
    - type: file
      path: src/main/java/com/example/auth/JwtService.java
      category: implementation

next_action: Update references file
```

### Output (TOON Handoff)

```toon
from: task-plan-skill
to: task-plan-command
handoff_id: ref-002
workflow: reference-management

task:
  description: References updated
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  references_file: .claude/plans/jwt-auth/references.md

changes[3]:
- Added ADR-015: JWT Authentication Strategy
- Added IF-042: Authentication Service Interface
- Added implementation file: JwtService.java

references_summary:
  adrs_count: 2
  interfaces_count: 2
  files_count: 4
  external_docs_count: 2

next_action: Review updated references
```

### Reference Integration with Skills

#### For ADRs (via `adr-management` skill)

```toon
# Before adding ADR reference, check if ADR exists:
from: task-plan-skill
to: adr-management-skill
handoff_id: adr-check-001

operation: read
adr_identifier: ADR-015

# If ADR doesn't exist, create it:
from: task-plan-skill
to: adr-management-skill
handoff_id: adr-create-001

operation: create
title: JWT Authentication Strategy
context: [...]
decision: [...]
```

#### For Interface Specs (via `interface-management` skill)

```toon
# Before adding interface reference, check if it exists:
from: task-plan-skill
to: interface-management-skill
handoff_id: if-check-001

operation: read
interface_identifier: IF-042

# If interface doesn't exist, create it:
from: task-plan-skill
to: interface-management-skill
handoff_id: if-create-001

operation: create
title: Authentication Service Interface
description: [...]
endpoints: [...]
```

### File Operations (via plan-files skill)

Delegates file operations to `plan-files` skill:
- `plan-files.get-references` → Read current references
- `plan-files.write-references` → Add/update/remove references
- Maintains Markdown structure and formatting

**Delegation to documentation skills**:
- `adr-management` skill → Validate or create ADRs
- `interface-management` skill → Validate or create interface specs

---

## Integration Points

### With /task-plan Command

**Command Responsibility**:
- Parse user parameters (task, plan, output)
- Determine operation (create, refine)
- Generate TOON handoff
- Delegate to task-plan skill
- Format results for user

**Skill Responsibility**:
- All file I/O operations
- Plan structure generation
- Content parsing and validation
- Error handling

**Example Flow**:
```
User: /task-plan task="Add JWT auth" issue="https://github.com/org/repo/issues/123"
  ↓
/task-plan command
  ↓ (TOON handoff: create)
task-plan skill
  ↓ (Bash: mkdir -p .claude/plans/jwt-auth/)
  ↓ (Write: plan.md)
  ↓ (Write: references.md)
.claude/plans/jwt-auth/
  ├── plan.md
  └── references.md
  ↓ (TOON handoff: created)
/task-plan command
  ↓
User: "Created plan at .claude/plans/jwt-auth/"
```

### With /task-implement Command

**Command Responsibility**:
- Accept plan directory parameter
- Generate TOON handoff
- Delegate plan reading to skill
- Use parsed plan for orchestration

**Skill Responsibility**:
- Read plan.md and references.md
- Parse Markdown structure
- Extract tasks, metadata, and references
- Return structured data

**Example Flow**:
```
User: /task-implement plan=".claude/plans/jwt-auth/"
  ↓
/task-implement command
  ↓ (TOON handoff: read)
task-plan skill
  ↓ (Read: plan.md)
  ↓ (Read: references.md)
.claude/plans/jwt-auth/
  ├── plan.md
  └── references.md
  ↓ (parsed content)
task-plan skill
  ↓ (TOON handoff: parsed)
/task-implement command
  ↓ (orchestrate implementation)
Language agents, build verification, etc.
```

### With task-execute Skill

**Skill Responsibility** (task-execute):
- Track task progress
- Mark checklist items complete
- Delegate updates to task-plan skill

**Skill Responsibility** (task-plan):
- Update plan.md with progress
- Mark tasks/items as complete
- Track completion percentage

**Example Flow**:
```
task-execute skill
  ↓ (TOON handoff: update task 1 complete)
task-plan skill
  ↓ (Edit: plan.md, mark [x])
.claude/plans/jwt-auth/plan.md
  ↓ (TOON handoff: updated)
task-execute skill
```

---

## Error Handling

### Error Type: File Not Found

**Scenario**: Plan directory or file does not exist

```toon
from: task-plan-skill
to: caller
handoff_id: error-001

task:
  status: failed

error:
  type: file_not_found
  message: Plan directory not found
  details: .claude/plans/jwt-auth/ does not exist

alternatives[2]:
- Create new plan with /task-plan
- Check directory path and try again
```

### Error Type: Invalid Structure

**Scenario**: Plan file has invalid Markdown structure

```toon
from: task-plan-skill
to: caller
handoff_id: error-002

task:
  status: failed

error:
  type: invalid_structure
  message: Plan file has invalid structure
  details: Missing Phase Progress Table in plan.md

validation_errors[2]:
- Phase Progress Table not found
- Task 3 missing acceptance criteria

alternatives[2]:
- Refine plan to fix structure
- Recreate plan from scratch
```

### Error Type: Phase Transition Violation

**Scenario**: Attempting invalid phase transition

```toon
from: task-plan-skill
to: caller
handoff_id: error-003

task:
  status: failed

error:
  type: phase_transition_violation
  message: Cannot transition to next phase
  details: Current phase 'implement' is not completed

phase_status:
  phase: implement
  status: in_progress
  tasks_total: 5
  tasks_completed: 3
  completion_percentage: 60

remaining_tasks[2]{id,name}:
task-9,Add JWT configuration
task-10,Update POM dependencies

alternatives[2]:
- Complete remaining tasks before transition
- Mark remaining tasks as not applicable if valid
```

### Error Type: Reference Not Found

**Scenario**: Referenced ADR or interface does not exist

```toon
from: task-plan-skill
to: caller
handoff_id: error-004

task:
  status: failed

error:
  type: reference_not_found
  message: Referenced ADR not found
  details: ADR-015 does not exist in .claude/adrs/

alternatives[3]:
- Create ADR-015 using adr-management skill
- Remove reference from plan
- Update reference to correct ADR identifier
```

---

## Related Documents

- [Plan Types](plan-types.md) - Init phase router and configuration
- [Refine Phase](plan-refine/refine.md) - Refine phase specification
- [Implement Phase](plan-implement/implement.md) - Implement phase specification
- [Verify Phase](plan-verify/verify.md) - Verify phase specification
- [Finalize Phase](plan-finalize/finalize.md) - Finalize phase specification
- [Implementation Requirements Template](plan-refine/implementation-requirements-template.md) - Runtime artifact template
- [Architecture](architecture.md) - Abstraction layer design and patterns
- [Persistence](plan-files/persistence.md) - File structure and reference management
- [Templates & Workflow](templates-workflow.md) - Plan templates and phase-based workflow
- [Decomposition](decomposition.md) - Implementation details and integration
