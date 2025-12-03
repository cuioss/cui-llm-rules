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
| `generate-specifications` | `plan_id`, `components[]` | TOON spec files | plan-refine |
| `generate-tasks` | `plan_id`, `specifications[]` | TOON task files (linked to specs) | plan-refine |
| `get-next-phase` | `current_phase` | next phase name | manage-lifecycle |
| `get-finalize-config` | `plan_id` | finalize behavior | plan-finalize |

**Traceability Flow**: Components → Specifications → Tasks (each task references its specification)

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
      steps: Read task.md, Determine scope and technology, Add requirements
    - title: Detect Plan Type
      steps: From technology/scope, Apply detection rules
    - title: Confirm Configuration
      steps: Display config, Allow overrides, Confirm settings
  refine:
    - title: Analyze Requirements
      steps: Delegate to analysis skill, Review components
    - title: Generate Specifications
      steps: Create SPEC files via manage-specifications
    - title: Generate Tasks
      steps: Create TASK files via manage-tasks (linked to specs)
  execute: (generated dynamically)
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

## Operation: generate-specifications

Generates specifications from analyzed components. **Writes directly** to specifications/ directory via manage-specifications skill - does NOT return spec content, only confirmation.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `components` | array | Yes | Components from domain analysis |

**Components Structure** (from analysis-api):

```toon
components[3]{name,type,scope,path,complexity}:
jwt-service,class,create,src/main/java/auth/JwtService.java,medium
auth-controller,class,create,src/main/java/auth/AuthController.java,low
auth-tests,test,create,src/test/java/auth/AuthTest.java,low
```

**Process**:

1. For each component, call `manage-specification.py add` to create SPEC file
2. Group related components if applicable
3. Return confirmation (specs already written to disk)

**Specification Generation via manage-specifications**:

```bash
python3 manage-specification.py add \
  --plan-id {plan_id} \
  --title "{component-name} implementation" \
  --description "{what needs to be implemented}" \
  --acceptance-criteria "Criteria 1" "Criteria 2" "Criteria 3"
```

**Output Structure** (confirmation only, specs already written):

```toon
status: success
plan_id: {plan_id}
specs_created: 3

specifications[3]{number,title,file}:
1,JWT Service Implementation,SPEC-001-jwt-service.toon
2,Auth Controller Implementation,SPEC-002-auth-controller.toon
3,Auth Tests Implementation,SPEC-003-auth-tests.toon
```

---

## Operation: generate-tasks

Generates implementation tasks from specifications. **Writes directly** to tasks/ directory via manage-tasks skill - does NOT return task content, only confirmation. Each task is linked to its specification for traceability.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `specifications` | array | Yes | Specifications from generate-specifications |

**Specifications Structure** (from generate-specifications):

```toon
specifications[3]{number,title,file}:
1,JWT Service Implementation,SPEC-001-jwt-service.toon
2,Auth Controller Implementation,SPEC-002-auth-controller.toon
3,Auth Tests Implementation,SPEC-003-auth-tests.toon
```

**Process**:

1. For each specification, call `manage-task.py add` to create TASK file with `--specification SPEC-{n}`
2. Order tasks by dependencies
3. Return confirmation (tasks already written to disk)

**Task Generation via manage-tasks**:

```bash
python3 manage-task.py add \
  --plan-id {plan_id} \
  --specification SPEC-{n} \
  --title "Implement {component-name}" \
  --description "{goal-description}" \
  --steps "Create implementation" "Add tests" "Add documentation" "Verify build"
```

**Output Structure** (confirmation only, tasks already written):

```toon
status: success
plan_id: {plan_id}
tasks_created: 3

tasks[3]{number,title,specification,file}:
1,Implement JWT Service,SPEC-1,TASK-001-implement-jwt-service.toon
2,Add Auth Controller,SPEC-1,TASK-002-add-auth-controller.toon
3,Write Auth Tests,SPEC-1,TASK-003-write-auth-tests.toon
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
  ├─ Env detect  ├─ Requirements   ├─ Tasks from    ├─ Verify build
  ├─ Config      ├─ Analysis       │  manage-tasks  ├─ Commit
  └─ Confirm     ├─ Generate specs └─ Step loop     └─ PR (optional)
                 └─ Generate tasks
                    (linked to specs)
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
2. **Implement all operations**: All 7 operations with correct signatures
3. **Define phase structure**: Static phases with placeholder for execute
4. **Use manage-tasks**: Generate tasks via manage-task.py, not plan.md
5. **Return structured output**: All operations return status and data
6. **Handle errors gracefully**: Return error status with message

### Implementation Template

```markdown
---
name: plan-type-{domain}
description: {Domain} plan type providing {N}-phase workflow for {use-cases}
allowed-tools: Read
---

# Plan Type: {Domain}

**Phases**: {N} ({phase-list})

**Use Cases**:
- {use-case-1}
- {use-case-2}

**Analysis Skill**: `{bundle}:{skill}` (or null for simple)

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | {N} |
| Technology | {tech} |
| Build System | {build} |
| Analysis Skill | {skill} |
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

## Operation: generate-specifications

{Implementation per contract}

---

## Operation: generate-tasks

{Implementation per contract}

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
| `planning:plan-refine` | generate-specifications, generate-tasks |
| `planning:manage-lifecycle` | get-next-phase |
| `planning:plan-finalize` | get-finalize-config |

### Implementing Skills

| Skill | Domain |
|-------|--------|
| `planning:plan-type-simple` | Documentation, config, quick fixes |
| `planning:plan-type-plugin` | Marketplace components |
| `planning:plan-type-java` | Java/Maven/Gradle |
| `planning:plan-type-javascript` | JavaScript/npm |

---

## Quality Checklist

For implementing skills:

- [ ] Loads `planning:plan-type-api` for contract reference
- [ ] Implements all 7 operations with correct signatures
- [ ] Uses manage-tasks skill for task generation (not plan.md)
- [ ] Returns `status` field in all outputs
- [ ] Defines phase transition matrix
- [ ] Defines characteristics matrix
- [ ] Handles errors with status and message
