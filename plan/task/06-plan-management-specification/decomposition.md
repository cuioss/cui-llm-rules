# Implementation Decomposition

Implementation details, integration points, and usage examples for the plan management system.

## Overview

This document provides concrete implementation guidance for building the plan management abstraction layer. It covers:

1. **Skill Implementation** - How to build the 5 phase skills
2. **Command Integration** - How commands interact with phase skills
3. **Skill Integration** - How phase skills delegate to each other and to agents
4. **Usage Examples** - Real-world usage scenarios

**Implementation Tasks**: See [plan.md](plan.md) for the 5-phase implementation checklist.

---

## Skill Implementation Details

### Directory Structure (One Skill Per Phase + Persistence Layer)

```
cui-task-workflow/
└── skills/
    ├── plan-files/                # Persistence layer skill (file I/O)
    │   ├── SKILL.md               # read-plan, read-config, get-references, write-*, update-progress
    │   └── README.md
    │
    ├── plan-init/                 # Init phase skill
    │   ├── SKILL.md               # create, detect-environment, configure
    │   ├── plan-init/
    │   │   ├── implementation.md  # Full workflow init (5 phases)
    │   │   └── simple.md          # Lightweight init (3 phases)
    │   ├── standards/
    │   │   ├── plan-template.md   # plan.md template
    │   │   └── references-template.md # references.md template
    │   └── README.md
    │
    ├── plan-refine/               # Refine phase skill
    │   ├── SKILL.md               # analyze, plan-tasks, identify-docs
    │   ├── standards/
    │   │   └── implementation-requirements-template.md
    │   └── README.md
    │   # See: plan-refine/refine.md for full specification
    │
    ├── plan-implement/            # Implement phase skill
    │   ├── SKILL.md               # execute-tasks, delegate, track-progress
    │   └── README.md
    │
    ├── plan-verify/               # Verify phase skill
    │   ├── SKILL.md               # run-build, check-quality, review-docs
    │   └── README.md
    │
    └── plan-finalize/             # Finalize phase skill
        ├── SKILL.md               # commit, create-pr, pr-workflow
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

### /task-plan Command

**Responsibilities**:
- Parse user parameters
- Determine current phase from plan
- Route to appropriate phase skill
- Generate TOON handoff
- Format results for user

**Parameter Parsing**:
```markdown
Parameters:
- task=STRING - Task description (for create → plan-init)
- type=STRING - Plan type: implementation|simple (optional, auto-detected)
- plan=PATH - Plan directory path (for phase operations)
- phase=STRING - Explicit phase to run (optional, auto-detected from plan)
- issue=URL - GitHub issue URL (optional)
- branch=STRING - Git branch name (optional)
```

**Command Flow**:
```
1. Parse parameters
2. Determine phase skill to invoke:
   - Has 'task' → plan-init skill (create plan)
   - Has 'plan' → read current_phase from plan.md
     - current_phase=init → plan-init skill
     - current_phase=refine → plan-refine skill
     - current_phase=implement → plan-implement skill
     - current_phase=verify → plan-verify skill
     - current_phase=finalize → plan-finalize skill
3. Generate TOON handoff with parsed data
4. Invoke appropriate phase skill
5. Process TOON response
6. Format output for user
```

**Example Implementation Outline**:
```markdown
# In task-plan.md command:

When user provides task description:
1. Invoke Skill: cui-task-workflow:plan-init
2. Pass TOON handoff:
   - operation: create
   - task_description: [from user]
   - type: [auto-detect or from user]
   - issue_url: [if provided]
   - branch: [if provided]
3. Receive TOON response with plan_directory
4. Output to user: "Created plan at {plan_directory}"

When user provides plan directory (continue workflow):
1. Read plan.md to get current_phase
2. Route to appropriate phase skill:
   - cui-task-workflow:plan-refine
   - cui-task-workflow:plan-implement
   - cui-task-workflow:plan-verify
   - cui-task-workflow:plan-finalize
3. Pass TOON handoff with plan_directory
4. Receive TOON response with progress
5. Output to user: "Phase {phase} complete"
```

### /task-implement Command

**Responsibilities**:
- Accept plan directory parameter
- Delegate to plan-implement skill
- Plan-implement uses plan-files for reading plan/config/references
- Update progress via plan-files skill during implementation

**Parameter Parsing**:
```markdown
Parameters:
- plan=PATH - Plan directory path (required)
- start-from=TASK_ID - Start from specific task (optional)
```

**Command Flow**:
```
1. Parse plan directory parameter
2. Invoke plan-implement skill
3. Plan-implement uses plan-files to read:
   - Tasks array (via read-plan)
   - Configuration (via read-config)
   - References (via get-references)
4. Orchestrate implementation:
   - Delegate to language agents (java-implement, js-implement)
   - Use references for context
   - Update progress via plan-files skill after each task
5. Verify completion
6. Report results
```

**Example Implementation Outline**:
```markdown
# In task-implement.md command:

1. Invoke Skill: cui-task-workflow:plan-implement
2. Pass TOON handoff:
   - operation: execute-tasks
   - plan_directory: [from user]
3. Plan-implement uses plan-files for:
   - plan-files.read-plan → tasks array
   - plan-files.read-config → technology settings
   - plan-files.get-references → ADRs, interfaces, files
4. For each pending task in current phase:
   a. Invoke language agent (based on file types)
   b. Pass task details + references
   c. Wait for completion
   d. Invoke plan-files.update-progress
   e. Update plan.md with completion
5. Check phase completion
6. Offer to transition or finalize
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

### With task-execute Skill

**Integration Points**:
1. **During Task Execution**:
   - task-execute tracks progress
   - Marks checklist items complete
   - Delegates updates to plan-files skill

2. **After Task Completion**:
   - task-execute marks task complete
   - Delegates to plan-files skill (update-progress operation)
   - Receives phase status and next task

**TOON Handoff Example**:
```toon
# task-execute → plan-files (update)
from: task-execute-skill
to: plan-files-skill
handoff_id: progress-001

operation: update-progress
plan_directory: .claude/plans/jwt-auth/
task_id: task-6
status: completed
checklist_items[3]: 0,1,2

# plan-files → task-execute (result)
from: plan-files-skill
to: task-execute-skill
handoff_id: progress-002

status: updated
current_phase: implement
current_task: task-7
phase_completion: 40%
```

---

## Implementation Checklist

**See [plan.md](plan.md)** for the complete 5-phase implementation checklist with cross-references to related documents.

**Phases Overview**:
1. **Phase 1**: Create Plan Management Skill - Directory structure, core operations, phase management, reference management
2. **Phase 2**: Update Commands - `/task-plan` and `/task-implement` command integration
3. **Phase 3**: Update Related Skills - `task-execute` and `task-review` skill updates
4. **Phase 4**: Integration with Documentation Skills - ADR and interface management integration tests
5. **Phase 5**: Documentation and Testing - Documentation updates, testing, and example creation

---

## Usage Examples

### Example 1: Create New Plan

**User Command**:
```bash
/task-plan task="Implement JWT authentication with refresh tokens" \
  issue="https://github.com/org/repo/issues/123" \
  branch="feature/jwt-auth"
```

**Flow**:
1. `/task-plan` command parses parameters
2. Generates TOON handoff (create operation)
3. Delegates to `plan-init` skill
4. Plan-init uses `plan-files` skill:
   - `plan-files.create-directory` → `.claude/plans/jwt-auth/`
   - `plan-files.write-config` → config.md with settings
   - `plan-files.write-plan` → plan.md with 5 phases and initial tasks
   - `plan-files.write-references` → references.md with issue and branch
5. Skill returns TOON handoff with directory path
6. Command outputs: "Created plan at `.claude/plans/jwt-auth/`"

**Result Files**:
```
.claude/plans/jwt-auth/
  ├── plan.md          # 15 tasks across 5 phases
  ├── config.md        # Technology, build system, workflow settings
  └── references.md    # Issue #123, branch feature/jwt-auth
```

### Example 2: Refine Existing Plan

**User Command**:
```bash
/task-plan plan=".claude/plans/jwt-auth/" \
  feedback="Add token revocation support and refresh token rotation"
```

**Flow**:
1. Command generates TOON handoff (refine operation)
2. Delegates to `plan-refine` skill
3. Plan-refine uses `plan-files`:
   - `plan-files.read-plan` → existing tasks
   - `plan-files.read-config` → configuration
   - `plan-files.write-plan` → adds new tasks to implement phase
4. Skill updates Phase Progress Table (5 → 7 tasks in implement)
5. Skill returns changes list
6. Command outputs: "Added 2 tasks to implement phase"

**Changes**:
```markdown
# In plan.md:
## Phase: implement (in_progress)
...
### Task 8: Implement token revocation   ← NEW
### Task 9: Implement refresh token rotation   ← NEW
```

### Example 3: Add References to Plan

**User Command**:
```bash
/task-plan plan=".claude/plans/jwt-auth/" \
  add-reference="ADR-015" \
  add-reference="IF-042"
```

**Flow**:
1. Command generates TOON handoff (manage-references operation)
2. Delegates to appropriate phase skill
3. Phase skill uses `plan-files`:
   - `plan-files.get-references` → check existing refs
   - Verify ADR-015 via `adr-management` skill
   - Verify IF-042 via `interface-management` skill
   - `plan-files.write-references` → add references to references.md
4. Skill returns changes and summary
5. Command outputs: "Added 1 ADR and 1 interface reference"

**Changes**:
```markdown
# In references.md:
## Architecture Decision Records (ADRs)
**Related ADRs**:
- [ADR-015: JWT Authentication Strategy](.claude/adrs/ADR-015-jwt-authentication-strategy.adoc)

## Interface Specifications
**Related Interfaces**:
- [IF-042: Authentication Service Interface](doc/interfaces/IF-042-authentication-service.adoc)
```

### Example 4: Implement from Plan

**User Command**:
```bash
/task-implement plan=".claude/plans/jwt-auth/"
```

**Flow**:
1. Command generates TOON handoff (execute-tasks operation)
2. Delegates to `plan-implement` skill
3. Plan-implement uses `plan-files`:
   - `plan-files.read-plan` → all tasks
   - `plan-files.read-config` → technology, build system
   - `plan-files.get-references` → ADRs, interfaces, files
4. Orchestrates implementation:
   - For each task in implement phase:
     - Delegate to `java-implement-agent`
     - Pass task details + references
     - Wait for completion
     - `plan-files.update-progress` → mark task complete
5. After all tasks complete, check phase status
6. Offer to transition to verify phase

**Progress Updates**:
```
Task 6: Create JwtService ✓ (updated plan.md)
Task 7: Create TokenValidator ✓ (updated plan.md)
Task 8: Implement RefreshTokenService ✓ (updated plan.md)
...
Phase 'implement' completed. Ready to transition to 'verify'?
```

### Example 5: Manual Edit + Implement

**Scenario**: User manually edits plan files before implementation

**Manual Edits**:
```bash
# User edits .claude/plans/jwt-auth/plan.md
# - Updates task descriptions
# - Adds new acceptance criteria

# User edits .claude/plans/jwt-auth/references.md
# - Adds external documentation links
# - Adds Maven dependencies
```

**User Command**:
```bash
/task-implement plan=".claude/plans/jwt-auth/"
```

**Flow**:
1. Command delegates to `plan-implement` skill
2. Plan-implement uses `plan-files` to read:
   - `plan-files.read-plan` → manually edited tasks
   - `plan-files.read-config` → configuration
   - `plan-files.get-references` → updated external docs, dependencies
3. All manual updates are parsed:
   - New acceptance criteria
   - Additional external docs
   - Dependencies
4. Implementation proceeds with all changes and full context
5. Progress updates via `plan-files.update-progress`

**Benefit**: Manual editing is fully supported; `plan-files` skill abstracts file I/O

### Example 6: Validate Plan Before Implementation

**User Command**:
```bash
/task-plan plan=".claude/plans/jwt-auth/" validate
```

**Flow**:
1. Command generates TOON handoff (validate operation)
2. Delegates to appropriate phase skill
3. Phase skill uses `plan-files` to read all files:
   - `plan-files.read-plan`
   - `plan-files.read-config`
   - `plan-files.get-references`
4. Skill performs validation:
   - Structure check ✓
   - Acceptance criteria check ✓
   - References completeness check ⚠️ (missing interface IF-043)
   - ADR references verification ✓
4. Skill calculates quality score: 85/100
5. Skill returns validation results with recommendations
6. Command outputs results with actionable items

**Output**:
```
Validation Results:
✓ Structure valid
✓ All tasks have acceptance criteria
✓ ADR references exist
⚠️ Missing interface IF-043 referenced in Task 7
⚠️ Task 2 missing dependency information

Quality Score: 85/100

Recommendations:
- Create interface IF-043 or remove reference
- Add dependency: Task 2 depends on Task 1
```

---

## Related Documents

- [Plan Types](plan-types.md) - Init phase router and configuration
- [Refine Phase](plan-refine/refine.md) - Refine phase specification
- [Implement Phase](plan-implement/implement.md) - Implement phase specification
- [Verify Phase](plan-verify/verify.md) - Verify phase specification
- [Finalize Phase](plan-finalize/finalize.md) - Finalize phase specification
- [Implementation Requirements Template](plan-refine/implementation-requirements-template.md) - Runtime artifact template
- [Architecture](architecture.md) - Abstraction layer design
- [Persistence](plan-files/persistence.md) - File structure and directory organization
- [Templates & Workflow](templates-workflow.md) - Plan templates and phase-based workflow
- [API Specification](api.md) - Complete skill API with TOON handoffs
- [Implementation Plan](plan.md) - Complete 5-phase implementation checklist
- [../README.md](../README.md) - Overall architectural redesign overview
- [../03-target-architecture.md](../03-target-architecture.md) - Target architecture
- [../04-generic-workflow-patterns.md](../04-generic-workflow-patterns.md) - TOON handoff patterns

---

## Summary

This implementation guide provides:

1. ✅ **One-Skill-Per-Phase + Persistence Layer** - 5 phase skills + `plan-files` persistence skill
2. ✅ **Dedicated Persistence Skill** - `plan-files` handles all file I/O (read-plan, read-config, get-references, write-*, update-progress)
3. ✅ **Detailed Operation Implementation** - Concrete steps for all phase operations
4. ✅ **Command Integration Patterns** - How commands route to phase skills based on current_phase
5. ✅ **Skill Integration Examples** - ADR, interface, and language agent integration
6. ✅ **Real-World Usage Examples** - 6 practical scenarios
7. ✅ **Directory-Based Structure** - Organized plan directories with plan.md, config.md, references.md
8. ✅ **Phase Management Details** - Sequential workflow with automatic transitions
9. ✅ **Reference Management Details** - Skill abstraction integration via plan-files
10. ✅ **Error Handling Patterns** - Comprehensive error scenarios

**Implementation Tasks**: See [plan.md](plan.md) for the complete implementation checklist.

**Result**: A complete implementation guide for building the plan management abstraction layer with one skill per phase, a dedicated persistence layer (`plan-files`), directory-based organization, automatic phase transitions, comprehensive reference management, and seamless integration with existing architectural documentation patterns.
