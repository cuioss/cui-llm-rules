---
name: plan-type-api
description: Defines the unified API contract for plan-type skills. Load this skill to implement a domain-specific plan type.
allowed-tools: Read
---

# Plan Type API Skill

**Role**: API contract definition for plan-type skills. This skill defines the interface that all plan-type skills must implement.

**Usage**: Plan-type skills load this skill to ensure they implement the correct API contract.

## API Contract Overview

All plan-type skills implement these operations:

| Operation | Input | Output | Caller |
|-----------|-------|--------|--------|
| `get-phase-structure` | `plan_id`, `task_title` | Phase config | plan-init |
| `get-config-template` | context fields | config.toon template | plan-init |
| `get-references-template` | context fields | references.toon template | plan-init |
| `refine` | `plan_id` | SPEC + TASK files created | plan-refine |
| `get-next-phase` | `current_phase` | next phase name | manage-lifecycle |
| `get-finalize-config` | `plan_id` | finalize behavior | plan-finalize |

**Traceability Flow**: Requirements → Specifications → Tasks (each task references its specification)

---

## Operation: get-phase-structure

Returns the phase configuration for the plan type.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `task_title` | string | Yes | Human-readable task title |

**Output Structure**:

```toon
status: success|error
error_message: {message}              # Only if status=error
current_phase: init
initial_status: pending

phases[4]{name,order}:
init,1
refine,2
execute,3
finalize,4

phase_tasks:
  init:
    - title: Detect Environment
      steps: git branch --show-current, builder:environment-detection skill
    - title: Analyze Task
      steps: Read task.md, Determine scope and technology
    - title: Add Requirements
      steps: Create REQ files via manage-requirements
    - title: Detect Plan Type
      steps: From technology/scope, Apply detection rules
    - title: Confirm Configuration
      steps: Display config, Allow overrides, Confirm settings
  refine:
    - title: Refine Plan
      steps: Call plan-type:refine, Iterates REQ→SPEC→TASK automatically
  execute: (generated dynamically from TASK files)
  finalize:
    - title: Run Verification
      steps: /builder-build-and-fix or /plugin-doctor
    - title: Commit Changes
      steps: Stage and commit
```

---

## Operation: get-config-template

Returns the config.toon template for this plan type.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `branch` | string | Yes | Current git branch |
| `issue` | string | No | Issue reference (URL or ID) |
| `build_system` | string | No | Detected build system |
| `technology` | string | No | Technology stack |

**Output Structure**:

```toon
plan_type: {type}
branch: {branch}
issue: {issue}

technology: {technology}
build_system: {build_system}

compatibility: deprecations|breaking
commit_strategy: fine-granular|phase-specific|complete
finalizing: pr-workflow|commit-only

# Type-specific fields
{additional_fields}
```

---

## Operation: get-references-template

Returns the references.toon template for this plan type.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `branch` | string | Yes | Current git branch |
| `issue_id` | string | No | Issue identifier |
| `issue_title` | string | No | Issue title |
| `issue_url` | string | No | Issue URL |

**Output Structure**:

```toon
# References

issue:
  id: {issue_id}
  title: {issue_title}
  url: {issue_url}

branch: {branch}
base_branch: main

files:
  implementation: []
  configuration: []
  test: []

# Type-specific sections
{additional_sections}
```

---

## Operation: refine

Transforms requirements into specifications and tasks. **Iterates through existing data** using manage-* tools, creating the full traceability chain: REQ → SPEC → TASK.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Process**:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Requirements → Specifications                             │
├─────────────────────────────────────────────────────────────────────┤
│  1. Load all requirements:                                          │
│     python3 {manage-requirement.py} findAll --plan-id {plan_id}     │
│                                                                     │
│  2. FOR EACH requirement:                                           │
│     - Analyze requirement content                                   │
│     - Apply domain-specific spec generation logic                   │
│     - Create specification:                                         │
│       python3 {manage-specification.py} add \                       │
│         --plan-id {plan_id} \                                       │
│         --title "{derived-title}" \                                 │
│         --requirements "REQ-{n}" \                                  │
│         --body "{domain-specific-content}"                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Specifications → Tasks                                    │
├─────────────────────────────────────────────────────────────────────┤
│  3. Load all specifications:                                        │
│     python3 {manage-specification.py} findAll --plan-id {plan_id}   │
│                                                                     │
│  4. FOR EACH specification:                                         │
│     - Analyze specification content                                 │
│     - Apply domain-specific task generation logic                   │
│     - Create task(s):                                               │
│       python3 {manage-task.py} add \                                │
│         --plan-id {plan_id} \                                       │
│         --specification SPEC-{n} \                                  │
│         --title "{derived-title}" \                                 │
│         --description "{goal}" \                                    │
│         --steps "{step1}" "{step2}" ...                             │
└─────────────────────────────────────────────────────────────────────┘
```

**Domain-Specific Logic**:

Each plan-type skill provides domain knowledge for:
- **Spec title derivation**: How to name specs from requirements
- **Spec body content**: What technical details to include
- **Task generation**: How many tasks per spec, what steps
- **Standards references**: Which skills to load during execution

**Output Structure**:

```toon
status: success
plan_id: {plan_id}

phase_1:
  requirements_processed: 3
  specs_created: 3

phase_2:
  specs_processed: 3
  tasks_created: 5

specifications[3]{number,title,requirements,file}:
1,JWT Token Implementation,REQ-1,SPEC-001-jwt-token.toon
2,Auth Endpoint,REQ-2,SPEC-002-auth-endpoint.toon
3,Session Management,"REQ-1,REQ-3",SPEC-003-session-management.toon

tasks[5]{number,title,specification,file}:
1,Implement JwtService,SPEC-1,TASK-001-implement-jwt-service.toon
2,Add JWT Unit Tests,SPEC-1,TASK-002-add-jwt-unit-tests.toon
3,Create AuthController,SPEC-2,TASK-003-create-auth-controller.toon
4,Implement SessionManager,SPEC-3,TASK-004-implement-session-manager.toon
5,Add Integration Tests,SPEC-3,TASK-005-add-integration-tests.toon
```

**Error Handling**:

```toon
status: error
plan_id: {plan_id}
error: no_requirements
message: No requirements found. Add requirements before refining.
```

---

## Operation: get-next-phase

Returns the next phase in the workflow.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `current_phase` | string | Yes | Current phase name |

**Output Structure**:

```toon
status: success|error|complete
phase: {next-phase-name}              # Omitted if complete
message: {info}                       # Optional context
```

**Phase Transition Matrix** (plan-type defines its own):

| Plan Type | Phases | Transitions |
|-----------|--------|-------------|
| simple | 3 | init → execute → finalize |
| plugin | 4 | init → refine → execute → finalize |
| java | 4 | init → refine → execute → finalize |
| javascript | 4 | init → refine → execute → finalize |

---

## Operation: get-finalize-config

Returns finalize phase behavior configuration.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Output Structure**:

```toon
status: success
commit_strategy: fine-granular|phase-specific|complete
create_pr: true|false
verification_required: true|false
verification_command: {command}       # e.g., "/builder-build-and-fix", "/plugin-doctor"
branch_strategy: feature|direct
```

**Field Descriptions**:

| Field | Description |
|-------|-------------|
| `commit_strategy` | How to organize commits |
| `create_pr` | Whether to create a pull request |
| `verification_required` | Whether verification must pass before finalize |
| `verification_command` | Command to run for verification |
| `branch_strategy` | Feature branch or direct-to-main |

---

## Phase Model

### Standard 4-Phase Model

Most plan types use this model:

```
init ────────► refine ────────► execute ────────► finalize
  │              │                 │                 │
  │              │                 │                 │
  ├─ Env detect  ├─ REQ → SPEC     ├─ Tasks from    ├─ Verify build
  ├─ Config      │  (iterate)      │  manage-tasks  ├─ Commit
  └─ Confirm     └─ SPEC → TASK    └─ Step loop     └─ PR (optional)
                    (iterate)
```

**Refine Phase Detail**:
```
manage-requirements:findAll → REQ[]
        │
        ▼
   FOR EACH REQ:
        │
        └─► manage-specifications:add → SPEC
                    │
                    ▼
       manage-specifications:findAll → SPEC[]
                    │
                    ▼
              FOR EACH SPEC:
                    │
                    └─► manage-tasks:add → TASK
```

### Simple 3-Phase Model

For documentation/config tasks:

```
init ────────────────────────────► execute ────────► finalize
  │                                   │                 │
  │                                   │                 │
  ├─ Minimal config                   ├─ Direct tasks  ├─ Commit only
  └─ Quick confirm                    └─ from desc     └─ No PR
```

**Note**: Simple plans skip refine phase. Tasks are derived directly from the task description during init.

---

## Characteristics Matrix

Each plan type defines its characteristics:

| Characteristic | Description | Values |
|----------------|-------------|--------|
| `phases` | Number of phases | 3, 4 |
| `technology` | Target technology | java, javascript, none |
| `build_system` | Build tool | maven, gradle, npm, none |
| `analysis_skill` | Domain analysis skill | Full skill path or null |
| `branch_required` | Requires feature branch | true, false |
| `issue_required` | Requires issue reference | true, false, recommended |
| `pr_workflow` | Creates PR | true, false |
| `verification_cmd` | Verification command | Command string or null |

---

## Implementation Requirements

Plan-type skills that implement this API must:

1. **Load this skill**: Reference `planning:plan-type-api` for contract compliance
2. **Implement all operations**: All 6 operations with correct signatures
3. **Define phase structure**: Static phases with placeholder for execute
4. **Use manage-* tools**: All data I/O via manage-requirements, manage-specifications, manage-tasks
5. **Return structured output**: All operations return status and data
6. **Handle errors gracefully**: Return error status with message

### Implementation Template

```markdown
---
name: plan-type-{domain}
description: {Domain} plan type providing {N}-phase workflow for {use-cases}
allowed-tools: Read, Bash
---

# Plan Type: {Domain}

**Phases**: {N} ({phase-list})

**Use Cases**:
- {use-case-1}
- {use-case-2}

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | {N} |
| Technology | {tech} |
| Build System | {build} |
| Branch Required | {true/false} |
| Issue Required | {true/false/recommended} |
| PR Workflow | {true/false} |
| Verification | {command or none} |

---

## Operation: get-phase-structure

{Implementation per contract}

---

## Operation: get-config-template

{Implementation per contract}

---

## Operation: get-references-template

{Implementation per contract}

---

## Operation: refine

{Domain-specific implementation - iterate REQ→SPEC→TASK}

---

## Operation: get-next-phase

{Implementation per contract}

---

## Operation: get-finalize-config

{Implementation per contract}
```

---

## Integration

### Calling Skills

| Skill | Operations Used |
|-------|-----------------|
| `planning:plan-init` | get-phase-structure, get-config-template, get-references-template |
| `planning:plan-refine` | refine |
| `planning:manage-lifecycle` | get-next-phase |
| `planning:plan-finalize` | get-finalize-config |

### Implementing Skills

| Skill | Domain |
|-------|--------|
| `planning:plan-type-simple` | Documentation, config, quick fixes |
| `planning:plan-type-plugin` | Marketplace components |
| `planning:plan-type-java` | Java/Maven/Gradle |
| `planning:plan-type-javascript` | JavaScript/npm |

### Data Layer Tools (used by refine operation)

| Tool | Purpose |
|------|---------|
| `manage-requirements:findAll` | Load all requirements for plan |
| `manage-specifications:add` | Create specification from requirement |
| `manage-specifications:findAll` | Load all specifications for plan |
| `manage-tasks:add` | Create task from specification |

---

## Quality Checklist

For implementing skills:

- [ ] Loads `planning:plan-type-api` for contract reference
- [ ] Implements all 6 operations with correct signatures
- [ ] Uses manage-* tools for all data I/O
- [ ] Returns `status` field in all outputs
- [ ] Defines phase transition matrix
- [ ] Defines characteristics matrix
- [ ] Handles errors with status and message
- [ ] refine operation iterates REQ→SPEC→TASK with proper traceability
