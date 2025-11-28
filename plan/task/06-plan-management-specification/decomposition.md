# Implementation Decomposition

Implementation details, integration points, and usage examples for the plan management system.

## Overview

This document provides concrete implementation guidance for building the plan management abstraction layer. It covers:

1. **Skill Implementation** - How to build the 5 phase skills
2. **Command Integration** - How two commands interact with phase skills
3. **Skill Integration** - How phase skills delegate to each other and to agents
4. **Usage Examples** - Real-world usage scenarios for both commands

**Implementation Tasks**: See [Migration Plan](updated-plan/migration.md) for the implementation checklist.

---

## Skill Implementation Details

### Directory Structure (Two Commands + Orchestration + Phase Skills + Persistence)

```
cui-task-workflow/
├── commands/
│   ├── plan-manage.md             # Management: list, cleanup, init, refine
│   └── plan-execute.md            # Execution: implement, verify, finalize
│
└── skills/
    ├── phase-management/          # Orchestration skill
    │   ├── SKILL.md               # discover-plans, route-phase, transition-phase, get-status
    │   ├── standards/             # orchestration.md, transitions.md
    │   └── scripts/               # Python scripts for deterministic operations
    │
    ├── plan-files/                # Persistence layer skill (file I/O)
    │   ├── SKILL.md               # read-plan, read-config, get-references, write-*, update-progress
    │   ├── standards/             # persistence.md, architecture.md
    │   └── README.md
    │
    ├── plan-init/                 # Init phase skill
    │   ├── SKILL.md               # create, detect-environment, configure
    │   ├── standards/             # implementation-init.md, simple-init.md, workflow.md
    │   └── README.md
    │
    ├── plan-refine/               # Refine phase skill
    │   ├── SKILL.md               # analyze, plan-tasks, identify-docs
    │   ├── standards/             # workflow.md
    │   ├── templates/             # implementation-requirements.md
    │   └── README.md
    │
    ├── plan-implement/            # Implement phase skill
    │   ├── SKILL.md               # execute-tasks, delegate, track-progress
    │   ├── standards/             # workflow.md
    │   └── README.md
    │
    ├── plan-verify/               # Verify phase skill
    │   ├── SKILL.md               # run-build, check-quality, review-docs
    │   ├── standards/             # workflow.md
    │   └── README.md
    │
    └── plan-finalize/             # Finalize phase skill
        ├── SKILL.md               # commit, create-pr, pr-workflow
        ├── standards/             # workflow.md
        └── README.md
```

**Architecture**: Phase skills handle business logic and delegate all file I/O to `plan-files` skill. See [api.md](api.md#skill-plan-files) for operation details.

### plan-init Skill Operations

#### Create Operation

**Skill**: `plan-init`

**Tools Used**: `Bash`, `Write`

**Implementation Steps**:
1. Determine plan type (see [plan-types.md](plan-types.md))
2. Load appropriate init implementation (implementation.md or simple.md)
3. Execute init workflow:
   - Detect environment (branch, build system, issue)
   - Configure properties with defaults
   - User confirmation
4. Generate directory name from task description (kebab-case)
5. Create directory: `mkdir -p .claude/plans/{task-name}/`
6. Generate plan.md from init output with:
   - Task title and overview
   - Technical decisions (if provided)
   - Phase structure based on plan type (5 phases for implementation, 3 for simple)
   - Phase Progress Table
   - Helper fields (current_phase based on init, current_task: task-1)
7. Generate references.md with:
   - Issue URL and branch (if provided)
   - Empty sections for ADRs, interfaces, files, external docs
8. Return TOON handoff with directory path

**Error Scenarios**:
- Directory already exists → offer to refine instead
- Invalid task name → sanitize and create
- Missing required parameters → prompt for details

---

### plan-files Skill Operations

The `plan-files` skill is the **dedicated persistence layer**. All phase skills delegate file I/O to plan-files. See [api.md](api.md#skill-plan-files) for complete API specification.

#### Read Operations

**Tools Used**: `Read`

**Implementation Steps** (read-plan, read-config, get-references):
1. Read `.claude/plans/{task-name}/plan.md` (via read-plan)
2. Read `.claude/plans/{task-name}/config.md` (via read-config)
3. Read `.claude/plans/{task-name}/references.md` (via get-references)
4. Parse Markdown structure:
   - Extract header fields (status, phase, task)
   - Parse Phase Progress Table
   - Extract all tasks with status and acceptance criteria
   - Parse references from references.md
4. Return TOON handoff with structured data

**Parsing Logic**:
```markdown
# From plan.md:
- **Status**: pending|in_progress|completed
- **Current Phase**: init|refine|implement|verify|finalize
- **Current Task**: task-id or "none"
- Phase Progress Table → phases array
- Task sections → tasks array with checklist items

# From references.md:
- Issue and Branch section → issue_url, branch
- Related Files → implementation_files array
- ADRs → adrs array with identifiers
- Interfaces → interfaces array with identifiers
- External Documentation → external_docs array
- Dependencies → dependencies array
```

#### Update Progress Operation

**Tools Used**: `Edit`

**Implementation Steps** (update-progress):
1. Read current plan.md
2. Locate task by ID
3. Mark task status: `[ ]` → `[x]`
4. Mark checklist items: `[ ]` → `[x]`
5. Update Phase Progress Table
6. Check if phase complete
7. Return TOON handoff with progress

**Edit Example**:
```markdown
# Before:
### Task 1: Setup project structure

**Phase**: init

**Checklist**:
- [ ] Create base directories
- [ ] Initialize configuration

# After:
### Task 1: Setup project structure

**Phase**: init

**Checklist**:
- [x] Create base directories
- [x] Initialize configuration
```

#### Write Plan Operation

**Tools Used**: `Write`, `Edit` (plan.md and references.md)

**Implementation Steps**:
1. Read current plan.md and references.md
2. Determine refinement type:
   - Add task → Insert new task in appropriate phase
   - Modify task → Update existing task content
   - Add criteria → Append to acceptance criteria
   - Add reference → Update references.md
3. Maintain Markdown structure
4. Update Phase Progress Table if tasks added
5. Return TOON handoff with changes

**Add Task Example**:
```markdown
# Adding task to implement phase:

## Phase: implement (in_progress)

### Task 6: Create JwtService
[existing content]

### Task 6a: Add token refresh logic   ← NEW TASK
**Phase**: implement
**Goal**: Implement refresh token rotation

**Acceptance Criteria**:
- Refresh tokens stored securely
- Old tokens invalidated on refresh

**Checklist**:
- [ ] Create RefreshTokenService
- [ ] Add rotation logic
- [ ] Update tests
```

#### Validate Operation

**Tools Used**: `Read`

**Implementation Steps**:
1. Read plan.md and references.md
2. Validate plan.md structure:
   - Has all required headers
   - Has Phase Progress Table
   - All tasks have status indicators
   - All tasks have acceptance criteria
   - Phase sections properly formatted
3. Validate references.md completeness:
   - Has issue reference
   - Has branch reference
   - References to ADRs exist (check via adr-management)
   - References to interfaces exist (check via interface-management)
4. Calculate quality score (0-100)
5. Return TOON handoff with results and recommendations

**Validation Checklist**:
- ✅ Structure valid (all sections present)
- ✅ Tasks have acceptance criteria
- ✅ Tasks have checklist items
- ✅ Phase Progress Table accurate
- ✅ References complete (issue, branch)
- ✅ ADR references valid
- ✅ Interface references valid

#### Phase Transition Operation (via update-progress)

**Tools Used**: `Edit`

**Implementation Steps**:
1. Read plan.md
2. Verify current phase completed (all tasks `[x]`)
3. Determine next phase (init→refine→implement→verify→finalize)
4. Update plan.md:
   - Mark current phase as `completed`
   - Mark next phase as `in_progress`
   - Update `**Current Phase**` field
   - Update `**Current Task**` to first task of new phase
   - Update Phase Progress Table
5. Return TOON handoff with new phase

**Phase Transition Rules**:
```
init → refine → implement → verify → finalize
  ✓      ✓         ✓          ✓         ✓
(complete all tasks before transition)
```

#### Task Progress Update Operation (via update-progress)

**Tools Used**: `Edit`

**Implementation Steps**:
1. Read plan.md
2. Locate task in current phase
3. Mark task complete: `[ ]` → `[x]`
4. Mark checklist items complete
5. Update Phase Progress Table
6. Check if all phase tasks complete:
   - If YES → trigger automatic phase transition
   - If NO → update current_task to next task
7. Return TOON handoff with progress

**Auto Phase Transition Logic**:
```python
def check_phase_completion(phase_tasks):
    if all(task.status == 'completed' for task in phase_tasks):
        trigger_phase_transition()
        return True
    return False
```

#### Write References Operation

**Tools Used**: `Write`, `Edit`, `Skill` (for ADR/interface verification)

**Implementation Steps**:
1. Read references.md
2. Determine action (add, update, remove)
3. For ADR references:
   - Check if ADR exists via `adr-management` skill
   - If not exists, optionally create via skill
   - Add reference to "Architecture Decision Records" section
4. For interface references:
   - Check if interface exists via `interface-management` skill
   - If not exists, optionally create via skill
   - Add reference to "Interface Specifications" section
5. For file/external/dependency references:
   - Add to appropriate section
6. Maintain Markdown structure
7. Return TOON handoff with changes

**Reference Section Updates**:
```markdown
# Before:
## Architecture Decision Records (ADRs)
**Related ADRs** (managed via `adr-management` skill):
- [ADR-010: Authentication Framework](.claude/adrs/ADR-010-auth-framework.adoc)

# After (adding ADR-015):
## Architecture Decision Records (ADRs)
**Related ADRs** (managed via `adr-management` skill):
- [ADR-010: Authentication Framework](.claude/adrs/ADR-010-auth-framework.adoc)
- [ADR-015: JWT Authentication Strategy](.claude/adrs/ADR-015-jwt-authentication-strategy.adoc)
```

---

## Command Integration

### Two-Command Architecture

The system uses **two commands** with clear separation:

| Command | Purpose | Phases | Primary Workflow |
|---------|---------|--------|------------------|
| `/plan-manage` | Plan lifecycle | init, refine | Manage Plans |
| `/plan-execute` | Plan execution | implement, verify, finalize | Execute Plans |

### /plan-manage Command

Management command (< 100 lines) for plan lifecycle operations.

**Parameters**:
```markdown
- action=STRING - Explicit action: list, cleanup, init, refine (default: list)
- task=STRING - Task description (for init)
- issue=URL - GitHub issue URL (for init)
- plan=PATH - Plan directory path (for specific operations)
```

**Command Flow**:
```
1. /plan-manage command receives parameters
2. Routes by action:
   - list (default) → list-plans operation
   - cleanup → cleanup-plans operation
   - init → init-plan operation → plan-init skill
   - refine → refine-plan operation → plan-refine skill
3. Displays numbered selection via AskUserQuestion
4. Executes selected action
5. On init complete → prompts to continue with refine
```

**Example Flow - List Plans**:
```
User: /plan-manage
  ↓
/plan-manage command
  ↓ (Manage Plans workflow)
phase-management skill
  ↓ (list-plans)
discover-plans.py
  ↓
Numbered list displayed, user selects
```

**Example Flow - Create Plan**:
```
User: /plan-manage action=init task="Add JWT auth"
  ↓
/plan-manage command
  ↓ (init-plan operation)
phase-management skill
  ↓ (checks existing init plans)
discover-plans.py --filter=init
  ↓ (creates via plan-init)
.claude/plans/jwt-auth/
  ↓
Prompts: "Continue with refine phase?"
```

### /plan-execute Command

Execution command (< 100 lines) for plan execution phases.

**Parameters**:
```markdown
- plan=PATH - Plan directory path (optional)
- phase=STRING - Force specific phase: implement, verify, finalize (optional)
```

**Command Flow**:
```
1. /plan-execute command receives parameters
2. If no plan:
   - discover-executable operation finds implement/verify/finalize plans
   - Displays numbered selection
3. If plan:
   - Validates phase is executable (not init/refine)
   - Routes to current phase skill
4. Executes phase
5. On phase complete → handles transition
```

**Example Flow - Select and Execute**:
```
User: /plan-execute
  ↓
/plan-execute command
  ↓ (Execute Plans workflow)
phase-management skill
  ↓ (discover-executable)
discover-plans.py --filter=implement,verify,finalize
  ↓
Numbered list displayed, user selects
  ↓
plan-implement/verify/finalize skill
```

**Example Flow - Direct Execute**:
```
User: /plan-execute plan="jwt-auth"
  ↓
/plan-execute command
  ↓ (route-phase)
phase-management skill
  ↓ (validates, routes to current phase)
plan-implement skill
  ↓ (executes tasks)
```

---

## Skill Integration

### With adr-management Skill

**Integration Points**:
1. **During Reference Addition**:
   - plan-files skill checks if ADR exists
   - Delegates to adr-management skill (read operation)
   - If ADR missing, optionally create via adr-management

2. **During Validation**:
   - plan-files skill reads references.md
   - For each ADR reference, verify existence
   - Report missing ADRs in validation results

**TOON Handoff Example**:
```toon
# plan-files → adr-management (check)
from: plan-files-skill
to: adr-management-skill
handoff_id: adr-check-001

operation: read
adr_identifier: ADR-015

# adr-management → plan-files (result)
from: adr-management-skill
to: plan-files-skill
handoff_id: adr-check-002

status: found
adr_path: .claude/adrs/ADR-015-jwt-authentication-strategy.adoc
title: JWT Authentication Strategy
```

### With interface-management Skill

**Integration Points**:
1. **During Reference Addition**:
   - plan-files skill checks if interface exists
   - Delegates to interface-management skill (read operation)
   - If interface missing, optionally create via interface-management

2. **During Validation**:
   - plan-files skill reads references.md
   - For each interface reference, verify existence
   - Report missing interfaces in validation results

**TOON Handoff Example**:
```toon
# plan-files → interface-management (check)
from: plan-files-skill
to: interface-management-skill
handoff_id: if-check-001

operation: read
interface_identifier: IF-042

# interface-management → plan-files (result)
from: interface-management-skill
to: plan-files-skill
handoff_id: if-check-002

status: found
interface_path: doc/interfaces/IF-042-authentication-service.adoc
title: Authentication Service Interface
```

### With plan-execute Skill

**Integration Points**:
1. **During Task Execution**:
   - plan-execute tracks progress
   - Marks checklist items complete
   - Delegates updates to plan-files skill

2. **After Task Completion**:
   - plan-execute marks task complete
   - Delegates to plan-files skill (update-progress operation)
   - Receives phase status and next task

**TOON Handoff Example**:
```toon
# plan-execute → plan-files (update)
from: plan-execute-skill
to: plan-files-skill
handoff_id: progress-001

operation: update-progress
plan_directory: .claude/plans/jwt-auth/
task_id: task-6
status: completed
checklist_items[3]: 0,1,2

# plan-files → plan-execute (result)
from: plan-files-skill
to: plan-execute-skill
handoff_id: progress-002

status: updated
current_phase: implement
current_task: task-7
phase_completion: 40%
```

---

## Implementation Checklist

**See [plan.md](plan.md)** for the complete 6-phase implementation checklist with cross-references to related documents.

**Phases Overview**:
1. **Phase 1**: Create Phase Management Skill - Orchestration skill with operations and Python scripts
2. **Phase 2**: Create Commands - /plan-manage and /plan-execute thin wrapper commands
3. **Phase 3**: Update Existing Phase Skills - Integration with phase-management
4. **Phase 4**: Update Documentation - Replace legacy command references
5. **Phase 5**: Remove Old Commands - Remove deprecated command files
6. **Phase 6**: Integration Testing - End-to-end workflow testing

---

## Usage Examples

### Example 1: List All Plans

**User Command**:
```bash
/plan-manage
```

**Flow**:
1. `/plan-manage` command (default action: list)
2. phase-management runs list-plans operation
3. discover-plans.py finds all plans
4. Displays numbered list with AskUserQuestion

**Output**:
```
Available Plans:

1. jwt-authentication [implement] - 3/12 tasks complete
2. user-profile-api [refine] - Requirements analysis
3. database-migration [finalize] - Ready for PR
4. old-feature [completed] - Done 2024-01-15

0. Create new plan

Select a plan (number) or action:
```

### Example 2: Create New Plan

**User Command**:
```bash
/plan-manage action=init task="Implement JWT authentication" \
  issue="https://github.com/org/repo/issues/123"
```

**Flow**:
1. `/plan-manage` with action=init
2. phase-management checks for existing init-phase plans
3. Routes to `plan-init` skill
4. Plan-init creates plan structure:
   - `plan-files.create-directory` → `.claude/plans/jwt-auth/`
   - `plan-files.write-config` → config.md
   - `plan-files.write-plan` → plan.md
   - `plan-files.write-references` → references.md
5. Prompts: "Continue with refine phase?"

**Result Files**:
```
.claude/plans/jwt-auth/
  ├── plan.md          # 15 tasks across 5 phases
  ├── config.md        # Technology, build system settings
  └── references.md    # Issue #123, branch feature/jwt-auth
```

### Example 3: Cleanup Completed Plans

**User Command**:
```bash
/plan-manage action=cleanup
```

**Flow**:
1. `/plan-manage` with action=cleanup
2. phase-management runs cleanup-plans operation
3. discover-plans.py --filter=completed finds completed plans
4. Displays list with AskUserQuestion

**Output**:
```
Completed Plans:

1. old-feature (completed 2024-01-15)
2. api-refactor (completed 2024-01-10)

Select plans to delete:
- 'all': Delete all
- Numbers: Delete specific (e.g., '1,2')
- 'cancel': Cancel

Select:
```

### Example 4: Execute Plan (Selection)

**User Command**:
```bash
/plan-execute
```

**Flow**:
1. `/plan-execute` with no params
2. phase-management runs discover-executable
3. discover-plans.py --filter=implement,verify,finalize
4. Displays executable plans with AskUserQuestion
5. User selects plan
6. Routes to current phase skill

**Output**:
```
Executable Plans:

1. jwt-authentication [implement] - Task 3/12: "Add token validation"
2. user-profile-api [verify] - Build verification pending
3. database-migration [finalize] - Ready for commit and PR

0. Exit (use /plan-manage to create plans)

Select plan to continue:
```

### Example 5: Execute Specific Plan

**User Command**:
```bash
/plan-execute plan="jwt-auth"
```

**Flow**:
1. `/plan-execute` with plan name
2. phase-management validates phase is executable
3. Routes to plan-implement skill (current phase)
4. Executes implementation tasks:
   - Delegates to `java-implement-agent`
   - Updates progress via `plan-files.update-progress`
5. On phase complete → offers transition to verify

**Progress Updates**:
```
Task 6: Create JwtService ✓
Task 7: Create TokenValidator ✓
Task 8: Implement RefreshTokenService ✓
...
Phase 'implement' completed. Continue with verify? [Y/n]
```

### Example 6: Refine Requirements

**User Command**:
```bash
/plan-manage action=refine
```

**Flow**:
1. `/plan-manage` with action=refine
2. phase-management finds refine-phase plans
3. discover-plans.py --filter=init,refine
4. Displays plans ready for refinement
5. User selects plan
6. Routes to plan-refine skill

**Output**:
```
Plans ready for refinement:

1. jwt-authentication [refine] - Requirements analysis needed
2. new-feature [init→refine] - Ready to refine

0. Return to main menu

Select plan to refine:
```

### Example 7: Force Phase Override

**User Command**:
```bash
/plan-execute plan="jwt-auth" phase="verify"
```

**Flow**:
1. `/plan-execute` with explicit phase override
2. phase-management validates override is reachable
3. If valid, routes to plan-verify skill
4. If invalid (e.g., current phase is refine), shows error

**Error (if invalid)**:
```
Cannot skip to 'verify' phase.

Current phase: implement
Pending tasks: 5 of 12

Complete implementation tasks first.
```

### Example 8: Phase Mismatch Error

**User Command**:
```bash
/plan-execute plan="new-feature"  # Plan is in 'init' phase
```

**Flow**:
1. `/plan-execute` attempts to execute
2. phase-management detects init phase
3. Returns error with redirect

**Output**:
```
Plan 'new-feature' is in 'init' phase.

This command handles execution phases only (implement, verify, finalize).
Use /plan-manage to complete init/refine phases first.
```

---

## Related Documents

- [Plan Types](plan-types.md) - Init phase router and configuration
- [Architecture](architecture.md) - Two-command architecture design
- [Templates & Workflow](templates-workflow.md) - Plan templates and phase-based workflow
- [API Specification](api.md) - Complete skill API with TOON handoffs
- [Phase Management](phase-management.md) - Orchestration skill with both workflows
- [Migration Plan](updated-plan/migration.md) - Implementation checklist

**Command Specifications** (in `updated-plan/`):
- [plan-manage.md](updated-plan/plan-manage.md) - Management command specification
- [plan-execute.md](updated-plan/plan-execute.md) - Execution command specification

**Implemented Skills** (in `cui-task-workflow/skills/`):
- `phase-management` (orchestration)
- `plan-init`, `plan-refine`, `plan-implement`, `plan-verify`, `plan-finalize`, `plan-files`

---

## Summary

This implementation guide provides:

1. ✅ **Two-Command Architecture** - `/plan-manage` for lifecycle, `/plan-execute` for execution
2. ✅ **Orchestration Layer** - `phase-management` skill with Manage Plans and Execute Plans workflows
3. ✅ **One-Skill-Per-Phase + Persistence Layer** - 5 phase skills + `plan-files` persistence skill
4. ✅ **Dedicated Persistence Skill** - `plan-files` handles all file I/O
5. ✅ **Interactive Discovery** - Numbered selection via AskUserQuestion in both commands
6. ✅ **Lifecycle Management** - List, cleanup, init, refine via `/plan-manage`
7. ✅ **Execution Focus** - Implement, verify, finalize via `/plan-execute`
8. ✅ **Skill Integration Examples** - ADR, interface, and language agent integration
9. ✅ **Real-World Usage Examples** - 8 practical scenarios for both commands
10. ✅ **Directory-Based Structure** - plan.md, config.md, references.md
11. ✅ **Phase-Appropriate Routing** - Each command handles its designated phases

**Implementation Tasks**: See [Migration Plan](updated-plan/migration.md) for the implementation checklist.

**Result**: A complete implementation guide for building the plan management abstraction layer with two focused commands (`/plan-manage` and `/plan-execute`), orchestration via `phase-management` skill, one skill per phase, a dedicated persistence layer, directory-based organization, interactive discovery, and lifecycle management.
