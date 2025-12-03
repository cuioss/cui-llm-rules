---
name: plan-type-java
description: Java plan type providing 4-phase workflow (init→refine→execute→finalize) for Java/Maven/Gradle projects
allowed-tools: Read, Bash
---

# Plan Type: Java

**Phases**: 4 (init → refine → execute → finalize)

**Use Cases**:
- Java implementation tasks
- Maven/Gradle projects
- CUI Java libraries and modules
- Quarkus/CDI applications

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 4 |
| Technology | java |
| Build System | maven, gradle |
| Branch Required | true |
| Issue Required | recommended |
| PR Workflow | true |
| Verification | `/builder-build-and-fix` (auto-detects maven/gradle) |

---

## Operation: get-phase-structure

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`, `task_title`

**Output**:

```toon
status: success
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
      steps: Call plan-type-java:refine, Iterates REQ→SPEC→TASK
  execute: (generated dynamically from TASK files)
  finalize:
    - title: Run Full Build
      steps: /builder-build-and-fix, Address any issues, Iterate until clean
    - title: Code Quality Check
      steps: Review Sonar issues, Address warnings
    - title: Commit Changes
      steps: Stage changes, Create commit, Push branch
    - title: Create Pull Request
      steps: Create PR, Link issue, Add reviewers
```

---

## Operation: get-config-template

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: (none)

**Output**:

```toon
plan_type: java
compatibility: deprecations
commit_strategy: fine-granular
```

---

## Operation: get-references-template

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `branch`, `issue_id`, `issue_title`, `issue_url`

**Output**:

```toon
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

adrs: []

interfaces: []

standards:
  - cui-java-expert:cui-java-core
  - cui-java-expert:cui-javadoc
  - cui-java-expert:cui-java-unit-testing

dependencies: []

related_plans: []
```

---

## Operation: refine

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`

**Process**:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Requirements → Specifications                             │
├─────────────────────────────────────────────────────────────────────┤
│  1. Load requirements:                                              │
│     python3 {manage-requirement.py} findAll --plan-id {plan_id}     │
│                                                                     │
│  2. FOR EACH requirement:                                           │
│     - Analyze Java-specific implications                            │
│     - Identify affected classes, modules, packages                  │
│     - Create specification with technical details:                  │
│       python3 {manage-specification.py} add \                       │
│         --plan-id {plan_id} \                                       │
│         --title "{Java component} implementation" \                 │
│         --requirements "REQ-{n}" \                                  │
│         --body "{class design, dependencies, patterns}"             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Specifications → Tasks                                    │
├─────────────────────────────────────────────────────────────────────┤
│  3. Load specifications:                                            │
│     python3 {manage-specification.py} findAll --plan-id {plan_id}   │
│                                                                     │
│  4. FOR EACH specification:                                         │
│     - Generate implementation task with Java-specific steps         │
│     - Generate test task if applicable                              │
│     python3 {manage-task.py} add \                                  │
│       --plan-id {plan_id} \                                         │
│       --specification SPEC-{n} \                                    │
│       --title "Implement {component}" \                             │
│       --description "{goal}" \                                      │
│       --steps \                                                     │
│         "Create/modify implementation at {path}" \                  │
│         "Add unit tests (load cui-java-expert:cui-java-unit-testing)" \
│         "Add JavaDoc (load cui-java-expert:cui-javadoc)" \          │
│         "Verify build passes"                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Java-Specific Specification Content**:

When creating specifications, include:
- Class/interface design decisions
- Package placement rationale
- Dependencies (CDI, Spring, external libs)
- Module assignment (for multi-module projects)
- Integration points with existing code

**Java-Specific Task Steps**:

Standard steps for Java implementation tasks:
1. Create/modify implementation file at `{path}`
2. Add unit tests (load `cui-java-expert:cui-java-unit-testing`)
3. Add JavaDoc (load `cui-java-expert:cui-javadoc`)
4. Follow CUI patterns (load `cui-java-expert:cui-java-core`)
5. Verify `mvn test -pl {module}` passes

**Output**:

```toon
status: success
plan_id: {plan_id}

phase_1:
  requirements_processed: 2
  specs_created: 3

phase_2:
  specs_processed: 3
  tasks_created: 4

specifications[3]{number,title,requirements,file}:
1,JwtService Implementation,REQ-1,SPEC-001-jwt-service.toon
2,AuthController Implementation,REQ-1,SPEC-002-auth-controller.toon
3,Auth Integration Tests,REQ-2,SPEC-003-auth-tests.toon

tasks[4]{number,title,specification,file}:
1,Implement JwtService,SPEC-1,TASK-001-implement-jwt-service.toon
2,Implement AuthController,SPEC-2,TASK-002-implement-auth-controller.toon
3,Add JwtService Unit Tests,SPEC-1,TASK-003-add-jwt-unit-tests.toon
4,Add Auth Integration Tests,SPEC-3,TASK-004-add-auth-integration-tests.toon
```

---

## Operation: get-next-phase

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `current_phase`

**Phase Transitions**:

| Current Phase | Next Phase |
|---------------|------------|
| init | refine |
| refine | execute |
| execute | finalize |
| finalize | complete |

**Output**:

```toon
status: success
phase: {next}
```

---

## Operation: get-finalize-config

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`

**Output**:

```toon
status: success
commit_strategy: fine-granular
create_pr: true
verification_required: true
verification_command: /builder-build-and-fix
branch_strategy: feature
```

---

## Quality Checklist

- [x] Loads `planning:plan-type-api` for contract reference
- [x] Implements all 6 operations with correct signatures
- [x] Uses manage-* tools for all data I/O
- [x] Returns `status` field in all outputs
- [x] Defines phase transition matrix (4 phases)
- [x] Defines characteristics matrix
- [x] Handles errors with status and message
- [x] refine operation iterates REQ→SPEC→TASK with Java-specific content
