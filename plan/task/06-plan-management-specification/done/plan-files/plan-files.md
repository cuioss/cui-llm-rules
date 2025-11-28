# plan-files Skill Specification

**Role**: Centralized file I/O for plan management - all phase skills delegate file operations here

**Use Cases**:
- Creating plan directory structure
- Reading plan.md, config.md, references.md
- Writing/updating plan files
- Tracking task progress
- Managing phase transitions

---

## Architecture

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

**Separation of Concerns**:
- Phase skills handle business logic (what to do)
- plan-files handles file I/O (how to persist)

---

## Operations

| Operation | Purpose | Tool | Input | Output |
|-----------|---------|------|-------|--------|
| create-directory | Create plan directory | Bash, AskUserQuestion | task_name | directory path, status |
| read-plan | Read plan.md | Read | directory | phases, tasks, status |
| read-config | Read config.md | Read | directory | configuration |
| get-references | Read references.md | Read | directory | references |
| write-plan | Create/update plan.md | Write/Edit | directory, content | success |
| write-config | Create config.md | Write | directory, config | success |
| write-references | Create/update references.md | Write/Edit | directory, refs | success |
| update-progress | Update task/phase status | Edit | directory, update | new status |

---

## Operation: create-directory

**Tool**: `Bash`, `Read`, `AskUserQuestion`

**Input**:
```toon
from: plan-init-skill
to: plan-files-skill
handoff_id: mkdir-001

task_name: jwt-auth
next_action: Create plan directory
```

**Implementation**:

### Step 1: Check Existence

```bash
# Check if directory already exists
test -d .claude/plans/{task-name}/ && echo "exists" || echo "not-exists"
```

### Step 2: Handle Existing Directory

If directory exists, prompt user:

```toon
from: plan-files-skill
to: user-interaction
handoff_id: exists-001

prompt: |
  Plan directory `.claude/plans/{task-name}/` already exists.

  Options:
  1. **Use existing** - Resume with existing plan
  2. **Create new** - Create with suffix (e.g., jwt-auth-2)
  3. **Replace** - Delete existing and create fresh

response_type: selection
options[3]: use-existing, create-new, replace
```

**User Response Handling**:

| Selection | Action |
|-----------|--------|
| `use-existing` | Return existing directory, set `status: resumed` |
| `create-new` | Generate unique name with suffix, create new directory |
| `replace` | Delete existing, create fresh directory |

### Step 3: Create Directory (if needed)

```bash
mkdir -p .claude/plans/{task-name}/
```

**Output (New Directory)**:
```toon
from: plan-files-skill
to: plan-init-skill
handoff_id: mkdir-002

artifacts:
  plan_directory: .claude/plans/jwt-auth/
status: created
```

**Output (Existing Directory - Use)**:
```toon
from: plan-files-skill
to: plan-init-skill
handoff_id: mkdir-002

artifacts:
  plan_directory: .claude/plans/jwt-auth/
status: resumed
existing_plan: true

plan_status:
  current_phase: implement
  current_task: task-6
```

**Output (Existing Directory - New Name)**:
```toon
from: plan-files-skill
to: plan-init-skill
handoff_id: mkdir-002

artifacts:
  plan_directory: .claude/plans/jwt-auth-2/
  original_name: jwt-auth
status: created
name_modified: true
```

**Validation**:
- Task name must be kebab-case
- Maximum 50 characters
- No special characters except hyphen
- Suffix format: `-{number}` (e.g., `-2`, `-3`)

---

## Operation: read-plan

**Tool**: `Read`

**Input**:
```toon
from: caller
to: plan-files-skill
handoff_id: read-plan-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/
```

**Implementation**:
1. Read `.claude/plans/{task-name}/plan.md`
2. Parse Markdown structure
3. Extract phases, tasks, status

**Parsing Logic**:
```markdown
# Extract from plan.md:
- **Status**: pending|in_progress|completed
- **Current Phase**: init|refine|implement|verify|finalize
- **Current Task**: task-id or "none"
- Phase Progress Table → phases array
- Task sections → tasks array with checklist items
```

**Output**:
```toon
from: plan-files-skill
to: caller
handoff_id: read-plan-002

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

---

## Operation: read-config

**Tool**: `Read`

**Input**:
```toon
from: caller
to: plan-files-skill
handoff_id: config-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/
```

**Implementation**:
1. Read `.claude/plans/{task-name}/config.md`
2. Parse configuration tables
3. Return structured configuration

**Output**:
```toon
from: plan-files-skill
to: caller
handoff_id: config-002

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

---

## Operation: get-references

**Tool**: `Read`

**Input**:
```toon
from: caller
to: plan-files-skill
handoff_id: refs-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/
```

**Implementation**:
1. Read `.claude/plans/{task-name}/references.md`
2. Parse reference sections
3. Return structured references

**Parsing Logic**:
```markdown
# Extract from references.md:
- Issue and Branch section → issue_url, branch
- Related Files → implementation_files array
- ADRs → adrs array with identifiers
- Interfaces → interfaces array with identifiers
- External Documentation → external_docs array
- Dependencies → dependencies array
```

**Output**:
```toon
from: plan-files-skill
to: caller
handoff_id: refs-002

references:
  issue:
    url: "https://github.com/org/repo/issues/123"
    title: "Add JWT Authentication"
  branch: "feature/jwt-auth"
  adrs[2]: "ADR-015", "ADR-020"
  interfaces[2]: "IF-042", "IF-051"
  implementation_files[3]: "JwtService.java", "TokenValidator.java"
  external_docs[2]: "RFC 7519", "OWASP JWT Cheat Sheet"
  dependencies[3]: "jjwt-api:0.11.5", "jjwt-impl:0.11.5"
```

---

## Operation: write-plan

**Tool**: `Write` (create) or `Edit` (update)

**Input**:
```toon
from: plan-init-skill
to: plan-files-skill
handoff_id: write-plan-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

plan_content:
  title: JWT Authentication
  status: in_progress
  current_phase: init
  current_task: task-1
  phases: [init, refine, implement, verify, finalize]
  tasks: [...]
```

**Implementation**:
1. Generate Markdown from plan content
2. Write to `.claude/plans/{task-name}/plan.md`
3. Include Phase Progress Table
4. Include all phase sections with tasks

**Output**:
```toon
from: plan-files-skill
to: plan-init-skill
handoff_id: write-plan-002

status: created
artifacts:
  plan_file: .claude/plans/jwt-auth/plan.md
```

---

## Operation: write-config

**Tool**: `Write`

**Input**:
```toon
from: plan-init-skill
to: plan-files-skill
handoff_id: write-config-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

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

**Implementation**:
1. Generate config.md from configuration
2. Write to `.claude/plans/{task-name}/config.md`
3. Use table format for clarity

**Output**:
```toon
from: plan-files-skill
to: plan-init-skill
handoff_id: write-config-002

status: created
artifacts:
  config_file: .claude/plans/jwt-auth/config.md
```

---

## Operation: write-references

**Tool**: `Write` (create) or `Edit` (update)

**Input**:
```toon
from: caller
to: plan-files-skill
handoff_id: write-refs-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

action: add|update|remove
reference_type: file|adr|interface|external|dependency
reference_data:
  type: adr
  identifier: ADR-015
  title: JWT Authentication Strategy
  path: .claude/adrs/ADR-015-jwt-authentication-strategy.adoc
```

**Implementation**:
1. Read current references.md (if exists)
2. Apply add/update/remove action
3. Write updated references.md
4. Maintain Markdown structure

**Output**:
```toon
from: plan-files-skill
to: caller
handoff_id: write-refs-002

status: updated
changes[1]:
- Added ADR-015: JWT Authentication Strategy

references_summary:
  adrs_count: 2
  interfaces_count: 1
  files_count: 3
```

---

## Operation: update-progress

**Tool**: `Edit`

**Input**:
```toon
from: caller
to: plan-files-skill
handoff_id: progress-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

update:
  task_id: task-8
  status: completed
  checklist_items: [0, 1, 2, 3, 4]
```

**Implementation**:
1. Read current plan.md
2. Locate task by ID
3. Mark task status: `[ ]` → `[x]`
4. Mark checklist items: `[ ]` → `[x]`
5. Update Phase Progress Table
6. Check if phase complete
7. Update Current Task to next task

**Edit Pattern**:
```markdown
# Before:
### Task 8: Implement RefreshTokenService
**Checklist**:
- [ ] Create service class
- [ ] Add rotation logic

# After:
### Task 8: Implement RefreshTokenService
**Checklist**:
- [x] Create service class
- [x] Add rotation logic
```

**Output**:
```toon
from: plan-files-skill
to: caller
handoff_id: progress-002

plan_status:
  current_phase: implement
  current_task: task-9
  phase_complete: false

phase_status:
  phase: implement
  tasks_total: 5
  tasks_completed: 3
  completion_percentage: 60
```

**Auto Phase Transition**:
When last task in phase is completed:
```toon
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

---

## Validation Operations

### validate-plan

**Implementation**:
1. Check required headers present
2. Check Phase Progress Table exists
3. Check all tasks have status indicators
4. Check all tasks have acceptance criteria
5. Calculate quality score

**Validation Checklist**:
- ✅ Structure valid (all sections present)
- ✅ Tasks have acceptance criteria
- ✅ Tasks have checklist items
- ✅ Phase Progress Table accurate
- ✅ Current phase/task fields valid

### validate-config

**Implementation**:
1. Check all required fields present
2. Validate field values against allowed values
3. Check branch and issue format

### validate-references

**Implementation**:
1. Check issue and branch present
2. Validate ADR references exist (via adr-management skill)
3. Validate interface references exist (via interface-management skill)
4. Check file paths valid

---

## Error Handling

### Error: File Not Found

```toon
from: plan-files-skill
to: caller
handoff_id: error-001

task:
  status: failed

error:
  type: file_not_found
  message: Plan directory not found
  details: .claude/plans/jwt-auth/ does not exist

alternatives[2]:
- Create new plan with plan-init skill
- Check directory path and try again
```

### Error: Invalid Structure

```toon
from: plan-files-skill
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

### Error: Parse Error

```toon
from: plan-files-skill
to: caller
handoff_id: error-003

task:
  status: failed

error:
  type: parse_error
  message: Failed to parse config.md
  details: Invalid value for technology field

alternatives[2]:
- Fix config.md manually
- Regenerate config via plan-init
```

---

## Integration with Documentation Skills

### ADR Verification

Before adding ADR reference:
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
```

### Interface Verification

Before adding interface reference:
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
```

---

## File Format Specifications

See [persistence.md](persistence.md) for complete file format specifications:
- Directory structure and naming
- plan.md format (tasks-only)
- config.md format
- references.md format
- implementation-requirements.md format

---

## Related Documents

- [Handoff Protocol](handoff.md) - TOON incoming/outgoing specifications
- [Persistence](persistence.md) - File structure and format specifications
- [API Specification](../api.md) - Complete skill API with TOON handoffs
- [Plan Types](../plan-types.md) - Init phase router
- [Refine Phase](../plan-refine/refine.md) - Refine phase specification
- [Implement Phase](../plan-implement/implement.md) - Implement phase specification
- [Verify Phase](../plan-verify/verify.md) - Verify phase specification
- [Finalize Phase](../plan-finalize/finalize.md) - Finalize phase specification
- [Templates & Workflow](../templates-workflow.md) - Plan templates
- [Decomposition](../decomposition.md) - Implementation details
