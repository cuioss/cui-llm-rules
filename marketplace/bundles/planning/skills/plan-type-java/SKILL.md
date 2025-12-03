---
name: plan-type-java
description: Java plan type providing 4-phase workflow (init→refine→execute→finalize) for Java/Maven/Gradle projects
allowed-tools: Read
---

# Plan Type: Java

**Phases**: 4 (init → refine → execute → finalize)

**Use Cases**:
- Java implementation tasks
- Maven/Gradle projects
- CUI Java libraries and modules
- Quarkus/CDI applications

**Analysis Skill**: `cui-java-expert:java-analysis`

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 4 |
| Technology | java |
| Build System | maven, gradle |
| Analysis Skill | `cui-java-expert:java-analysis` |
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
      steps: Read task.md, Determine scope and technology, Add requirements
    - title: Detect Plan Type
      steps: From technology/scope, Apply detection rules
    - title: Confirm Configuration
      steps: Display config, Allow overrides, Confirm settings
  refine:
    - title: Analyze Requirements
      steps: Delegate to java-analysis, Identify classes, Map dependencies
    - title: Generate Specifications
      steps: Create SPEC files via manage-specifications
    - title: Generate Tasks
      steps: Create TASK files via manage-tasks, Order by dependencies
  execute: (generated dynamically)
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

**Input**: `branch`, `issue`, `build_system`

**Output**:

```toon
plan_type: java
branch: {branch}
issue: {issue}

technology: java
build_system: {build_system}

compatibility: deprecations
commit_strategy: fine-granular
finalizing: pr-workflow
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

## Operation: generate-tasks

**Contract**: See `planning:plan-type-api` for full specification.

**Input**: `plan_id`, `components[]`

**Components Input** (from `cui-java-expert:java-analysis`):

```toon
components[3]{name,type,scope,module,path,complexity}:
JwtService,class,create,auth-module,src/main/java/auth/JwtService.java,medium
AuthController,class,create,auth-module,src/main/java/auth/AuthController.java,low
AuthTest,test,create,auth-module,src/test/java/auth/AuthTest.java,low
```

**Process**:

1. For each component, call `manage-task.py add` (writes directly to disk)
2. Include CUI Java standards references in steps
3. Order by dependencies

**Task Generation**:

```bash
python3 manage-task.py add \
  --plan-id {plan_id} \
  --specification SPEC-{n} \
  --title "Implement {component-name}" \
  --description "Create/modify {type} at {path}" \
  --steps \
    "Create/modify implementation file at {path}" \
    "Add unit tests in {test_path}" \
    "Load cui-java-expert:cui-java-unit-testing for test patterns" \
    "Add JavaDoc (load cui-java-expert:cui-javadoc)" \
    "Verify mvn test -pl {module} passes"
```

**Output** (confirmation only, tasks already written):

```toon
status: success
plan_id: {plan_id}
tasks_created: 3

tasks[3]{number,title,specification,file}:
1,Implement JwtService,SPEC-1,TASK-001-implement-jwt-service.toon
2,Implement AuthController,SPEC-1,TASK-002-implement-auth-controller.toon
3,Implement AuthTest,SPEC-1,TASK-003-implement-auth-test.toon
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
- [x] Implements all 7 operations with correct signatures
- [x] Uses manage-tasks skill for task generation
- [x] Returns `status` field in all outputs
- [x] Defines phase transition matrix (4 phases)
- [x] Defines characteristics matrix
- [x] Handles errors with status and message
