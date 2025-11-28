# API Specification

Complete skill API with all operations and TOON handoff interfaces for plan management.

## Overview

Plan management uses **two commands**, **one orchestration skill**, **one skill per phase**, and a **dedicated persistence skill**:

| Component | Purpose | Key Operations |
|-----------|---------|----------------|
| [/plan-manage](#command-plan-manage) | **Management command** | list, cleanup, init, refine |
| [/plan-execute](#command-plan-execute) | **Execution command** | execute implement/verify/finalize phases |
| [phase-management](#skill-phase-management) | **Orchestration** | Manage Plans workflow, Execute Plans workflow |
| [plan-files](#skill-plan-files) | **Persistence** | read-plan, read-config, get-references, write-plan, write-config, write-references |
| [plan-init](#skill-plan-init) | Init phase | create, detect-environment, configure |
| [plan-refine](#skill-plan-refine) | Refine phase | analyze, plan-tasks, identify-docs |
| [plan-implement](#skill-plan-implement) | Implement phase | execute-tasks, delegate, track-progress |
| [plan-verify](#skill-plan-verify) | Verify phase | run-build, check-quality, review-docs |
| [plan-finalize](#skill-plan-finalize) | Finalize phase | commit, create-pr, pr-workflow |

**Architecture**:
```
Commands                       Orchestration              Phase Skills                    Persistence
┌──────────────┐              ┌───────────────┐          ┌─────────────┐                ┌──────────────┐
│ /plan-manage │──(Manage)───▶│               │──────────▶│ plan-init   │──────────────▶│              │
│              │              │    phase-     │──────────▶│ plan-refine │──────────────▶│  plan-files  │──▶ .claude/plans/
└──────────────┘              │  management   │──────────▶│ plan-impl   │──────────────▶│              │
┌──────────────┐              │               │──────────▶│ plan-verify │──────────────▶│              │
│ /plan-execute│──(Execute)──▶│               │──────────▶│ plan-final  │──────────────▶└──────────────┘
└──────────────┘              └───────────────┘           └─────────────┘
```

**Communication Protocol**: All operations use TOON handoff format for input/output

**File System**: All file I/O goes through `plan-files` skill

**Phase Flow**: Each phase skill handles its logic, delegates file operations to `plan-files`

---

## Command: plan-manage

Plan lifecycle management command. Handles creation, listing, cleanup, and refinement.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | optional | Explicit action: `list`, `cleanup`, `init`, `refine` |
| `task` | optional | Task description (for init) |
| `issue` | optional | GitHub issue URL (for init) |
| `plan` | optional | Path to specific plan directory |

**Actions**:
- `list` (default): Display all plans with numbered selection
- `cleanup`: List and remove completed plans
- `init`: Create new plan (checks for existing init-phase plans)
- `refine`: Refine requirements (select from refine-phase plans)

See [updated-plan/plan-manage.md](updated-plan/plan-manage.md) for full specification.

---

## Command: plan-execute

Plan execution command. Handles implementation, verification, and finalization phases.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `plan` | optional | Path to specific plan directory |
| `phase` | optional | Force specific phase: `implement`, `verify`, `finalize` |

**Behavior**:
- Default: Shows executable plans (implement/verify/finalize phases) with numbered selection
- With plan: Executes current phase of specified plan
- Rejects init/refine phase plans with redirect to `/plan-manage`

See [updated-plan/plan-execute.md](updated-plan/plan-execute.md) for full specification.

---

## Skill: phase-management

The `phase-management` skill is the **orchestration layer** for plan management. It provides two workflows:

### Workflow: Manage Plans (for /plan-manage)

| Operation | Purpose | Python Script |
|-----------|---------|---------------|
| list-plans | Find and display all plans | `discover-plans.py` |
| cleanup-plans | Find and remove completed plans | `discover-plans.py --filter=completed` |
| init-plan | Create new plan (with existing check) | - |
| refine-plan | Refine requirements | - |

### Workflow: Execute Plans (for /plan-execute)

| Operation | Purpose | Python Script |
|-----------|---------|---------------|
| discover-executable | Find executable plans | `discover-plans.py --filter=implement,verify,finalize` |
| route-phase | Determine target phase skill | `route-phase.py` |
| transition-phase | Handle phase completion | `transition-phase.py` |
| get-status | Return comprehensive plan status | `get-status.py` |

**Operations**:
| Operation | Purpose | Python Script |
|-----------|---------|---------------|
| discover-plans | Find plans in workspace | `discover-plans.py` |
| route-phase | Determine target phase skill | `route-phase.py` |
| transition-phase | Handle phase completion | `transition-phase.py` |
| get-status | Return comprehensive plan status | `get-status.py` |

### Operation: Discover Plans

```toon
# Input
from: task-command
to: phase-management-skill
handoff_id: discover-001

next_action: Find all plans in workspace

# Output
plans_found[2]{name,path,current_phase,status}:
jwt-auth,.claude/plans/jwt-auth/,implement,in_progress
feature-x,.claude/plans/feature-x/,refine,in_progress

recommendation:
  action: select
  message: Multiple plans found. Select one to continue.
```

### Operation: Route Phase

```toon
# Input
from: task-command
to: phase-management-skill
handoff_id: route-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  current_phase: implement
  explicit_phase: null  # Optional override

# Output
routing:
  target_skill: plan-implement
  phase: implement
  reason: Current phase is implement
```

### Operation: Transition Phase

```toon
# Input
from: phase-skill
to: phase-management-skill
handoff_id: transition-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  completed_phase: implement

# Output
transition:
  from_phase: implement
  to_phase: verify
  is_complete: false
  next_skill: plan-verify
```

### Operation: Get Status

```toon
# Input
from: task-command
to: phase-management-skill
handoff_id: status-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

# Output
plan_status:
  name: jwt-auth
  current_phase: implement
  current_task: task-8
  overall_progress: 45%

phases[5]{name,status,completed}:
init,completed,3/3
refine,completed,2/2
implement,in_progress,2/5
verify,pending,0/3
finalize,pending,0/2
```

---

## Skill: plan-files

The `plan-files` skill is the **dedicated persistence layer** for all plan file operations. All phase skills delegate file I/O to this skill.

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

**Type Routing**: Routes to init implementation based on plan type:
- `implementation` → 5-phase plan (see `plan-init` skill)
- `simple` → 3-phase plan (see `plan-init` skill)

### Input (TOON Handoff)

```toon
from: phase-management-skill
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
to: phase-management-skill
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

See [done/plan-files/persistence.md](done/plan-files/persistence.md) for file format specifications.

---

## Skill: plan-refine

The `plan-refine` skill handles the refine phase: analyzing requirements, planning implementation tasks, and identifying documentation needs.

**Operations**:
- `analyze` - Break down requirements into components
- `plan-tasks` - Create detailed implementation tasks
- `identify-docs` - Determine ADR/interface needs

**Output Artifact**: `implementation-requirements.md`

### Operation: Analyze Requirements

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

### Input (TOON Handoff)

```toon
from: phase-management-skill
to: plan-refine-skill
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
from: plan-refine-skill
to: phase-management-skill
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

### Input (TOON Handoff)

```toon
from: phase-management-skill
to: plan-verify-skill
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
from: plan-verify-skill
to: phase-management-skill
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

### Input (TOON Handoff)

```toon
from: plan-execute-skill
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
to: plan-execute-skill
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

### Input (TOON Handoff)

```toon
from: plan-execute-skill
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
to: plan-execute-skill
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

### Input (TOON Handoff)

```toon
from: phase-skill
to: plan-files-skill
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
from: plan-files-skill
to: phase-skill
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

### With /plan-manage Command

The `/plan-manage` command delegates to `phase-management` skill's "Manage Plans" workflow.

**Example Flow - List Plans**:
```
User: /plan-manage
  ↓
/plan-manage command
  ↓ (Manage Plans workflow)
phase-management skill
  ↓ (list-plans operation)
discover-plans.py
  ↓
Displays numbered list, prompts user selection
```

**Example Flow - Create Plan**:
```
User: /plan-manage action=init task="Add JWT auth"
  ↓
/plan-manage command
  ↓ (Manage Plans workflow → init-plan)
phase-management skill
  ↓ (checks for existing init-phase plans)
discover-plans.py --filter=init
  ↓ (if none found, creates new)
plan-init skill
  ↓ (creates)
.claude/plans/jwt-auth/
  ├── plan.md
  ├── config.md
  └── references.md
  ↓
Prompts: "Continue with refine phase? (yes/no)"
```

**Example Flow - Cleanup**:
```
User: /plan-manage action=cleanup
  ↓
/plan-manage command
  ↓ (Manage Plans workflow → cleanup-plans)
phase-management skill
  ↓
discover-plans.py --filter=completed
  ↓
Lists completed plans, prompts for deletion confirmation
```

### With /plan-execute Command

The `/plan-execute` command delegates to `phase-management` skill's "Execute Plans" workflow.

**Example Flow - Select and Execute**:
```
User: /plan-execute
  ↓
/plan-execute command
  ↓ (Execute Plans workflow)
phase-management skill
  ↓ (discover-executable operation)
discover-plans.py --filter=implement,verify,finalize
  ↓
Displays executable plans, prompts selection
  ↓ (user selects)
plan-implement/verify/finalize skill
  ↓ (executes phase)
```

**Example Flow - Direct Execute**:
```
User: /plan-execute plan="jwt-auth"
  ↓
/plan-execute command
  ↓ (Execute Plans workflow → route-phase)
phase-management skill
  ↓ (validates phase is executable)
  ↓ (routes to current phase skill)
plan-implement skill
  ↓ (executes tasks)
Language agents, build verification, etc.
```

### With plan-execute Skill

**Skill Responsibility** (plan-execute):
- Track task progress
- Mark checklist items complete
- Delegate updates to task-plan skill

**Skill Responsibility** (task-plan):
- Update plan.md with progress
- Mark tasks/items as complete
- Track completion percentage

**Example Flow**:
```
plan-execute skill
  ↓ (TOON handoff: update task 1 complete)
task-plan skill
  ↓ (Edit: plan.md, mark [x])
.claude/plans/jwt-auth/plan.md
  ↓ (TOON handoff: updated)
plan-execute skill
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
- Create new plan with /task
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
- [Architecture](architecture.md) - Two-command architecture design
- [Templates & Workflow](templates-workflow.md) - Plan templates and phase-based workflow
- [Decomposition](decomposition.md) - Implementation details and integration
- [Phase Management](phase-management.md) - Orchestration skill with both workflows
- [Migration Plan](updated-plan/migration.md) - Implementation checklist

**Command Specifications** (in `updated-plan/`):
- [plan-manage.md](updated-plan/plan-manage.md) - Full /plan-manage specification
- [plan-execute.md](updated-plan/plan-execute.md) - Full /plan-execute specification

**Implemented Skills** (in `cui-task-workflow/skills/`):
- `phase-management` (orchestration)
- `plan-init`, `plan-refine`, `plan-implement`, `plan-verify`, `plan-finalize`, `plan-files`
