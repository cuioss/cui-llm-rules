---
name: plan-type-java
description: Java implementation plan type providing 5-phase workflow (init→refine→implement→verify→finalize) for Java/Maven/Gradle projects.
allowed-tools: Read
---

# Plan Type: Java

**Phases**: 5 (init→refine→implement→verify→finalize)

**Use Cases**:
- Java implementation tasks
- Maven/Gradle projects
- CUI Java libraries and modules
- Quarkus/CDI applications

**Analysis Skill**: `cui-java-expert:java-analysis`

---

## API Summary

All plan-type skills implement this uniform API:

| Operation | Input | Output | Used By |
|-----------|-------|--------|---------|
| `get-phase-structure` | `plan_id`, `task_title` | Phase structure for plan.md | plan-init |
| `generate-tasks` | `plan_id`, `components[]` | **Writes directly** to plan.md | plan-refine |
| `get-finalize-config` | `plan_id` | Finalize behavior (commit, PR) | plan-execute |
| `get-next-phase` | `plan_id`, `current_phase` | Next phase name | phase-management |

**Key Design**: `generate-tasks` writes directly to plan.md via scripts (no ping-pong between skills).

---

## Operation: get-phase-structure

**Input**: `plan_id`, `task_title`

**Output**: Complete phase structure for plan.md

```markdown
# Task Plan: {task_title}

**Configuration**: See [config.toon](./config.toon)
**References**: See [references.toon](./references.toon)

**Current Phase**: init
**Current Task**: task-1

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 5 | 0/5 |
| refine | pending | 3 | 0/3 |
| implement | pending | 0 | 0/0 |
| verify | pending | 4 | 0/4 |
| finalize | pending | 3 | 0/3 |

---

## Phase: init (in_progress)

### Task 1: Detect Environment

**Phase**: init
**Goal**: Gather information from command parameters and environment

**Acceptance Criteria**:
- Build system identified (Maven/Gradle)
- Java version determined
- Branch validated

**Checklist**:
- [ ] Check current git branch
- [ ] Detect build system (pom.xml or build.gradle)
- [ ] Parse issue from parameters or branch name
- [ ] Determine Java version from pom.xml/build.gradle
- [ ] **Log**: Record completion in work-log

### Task 2: Fetch Issue Details

**Phase**: init
**Goal**: Retrieve and analyze issue information

**Acceptance Criteria**:
- Issue title and description available
- Acceptance criteria extracted (if present)
- Related issues identified

**Checklist**:
- [ ] Fetch issue title and description
- [ ] Extract acceptance criteria
- [ ] Identify related issues/dependencies
- [ ] Pre-populate plan with issue content
- [ ] **Log**: Record completion in work-log

### Task 3: Validate Configuration

**Phase**: init
**Goal**: Ensure configuration is complete and valid

**Acceptance Criteria**:
- No configuration conflicts
- All required properties have values

**Checklist**:
- [ ] Verify branch is not main/master
- [ ] Confirm issue reference (or explicit skip)
- [ ] Validate build system detection
- [ ] Check for conflicting settings
- [ ] **Log**: Record completion in work-log

### Task 4: User Confirmation

**Phase**: init
**Goal**: Present configuration and get user approval

**Acceptance Criteria**:
- User has reviewed configuration
- All overrides applied

**Checklist**:
- [ ] Display detected configuration
- [ ] Highlight warnings or recommendations
- [ ] Allow property overrides
- [ ] Confirm final configuration
- [ ] **Log**: Record completion in work-log

### Task 5: Persist and Transition

**Phase**: init
**Goal**: Save configuration and move to refine phase

**Acceptance Criteria**:
- All files created
- Plan ready for refine phase

**Checklist**:
- [ ] Write config.toon with build and workflow configuration
- [ ] Write plan.md (tasks-only)
- [ ] Update references.toon with issue/branch
- [ ] Transition to refine phase
- [ ] **Log**: Record completion in work-log

---

## Phase: refine (pending)

### Task 1: Analyze Requirements

**Phase**: refine
**Goal**: Break down task into implementable Java components

**Acceptance Criteria**:
- Java components clearly identified
- Dependencies mapped

**Checklist**:
- [ ] Delegate to `cui-java-expert:java-analysis`
- [ ] Identify classes, interfaces, modules
- [ ] Map component dependencies
- [ ] Estimate complexity per component
- [ ] **Log**: Record completion in work-log

### Task 2: Plan Implementation Tasks

**Phase**: refine
**Goal**: Create detailed task list for implement phase

**Acceptance Criteria**:
- All tasks have acceptance criteria
- Tasks ordered by dependencies

**Checklist**:
- [ ] Generate implementation tasks from components
- [ ] Add acceptance criteria per task
- [ ] Order by dependencies
- [ ] Add tasks to implement phase
- [ ] **Log**: Record completion in work-log

### Task 3: Identify Documentation Needs

**Phase**: refine
**Goal**: Determine ADRs and interfaces needed

**Acceptance Criteria**:
- ADR decisions documented (if needed)
- Interface specifications created (if needed)

**Checklist**:
- [ ] Check if ADR needed for architectural decisions
- [ ] Check if interface specs needed for new APIs
- [ ] Create/link ADRs via adr-management skill
- [ ] Create/link interfaces via interface-management skill
- [ ] **Log**: Record completion in work-log

---

## Phase: implement (pending)

{Tasks generated dynamically by refine phase via generate-tasks operation}

---

## Phase: verify (pending)

### Task 1: Run Full Build

**Phase**: verify
**Goal**: Ensure all code compiles and tests pass

**Acceptance Criteria**:
- Maven/Gradle build successful
- All tests passing
- Coverage thresholds met

**Checklist**:
- [ ] Run `mvn verify` or `./gradlew build`
- [ ] Fix any build failures
- [ ] Verify test coverage meets thresholds
- [ ] **Log**: Record completion in work-log

### Task 2: Code Quality Check

**Phase**: verify
**Goal**: Verify code meets quality standards

**Acceptance Criteria**:
- No critical violations
- Quality gates passed

**Checklist**:
- [ ] Run `mvn checkstyle:check` (if configured)
- [ ] Check for compiler warnings
- [ ] Review Sonar issues (if applicable)
- [ ] Load `cui-java-expert:cui-java-core` for standards
- [ ] **Log**: Record completion in work-log

### Task 3: JavaDoc Verification

**Phase**: verify
**Goal**: Ensure JavaDoc is complete and valid

**Acceptance Criteria**:
- All public APIs documented
- No JavaDoc warnings

**Checklist**:
- [ ] Run `mvn javadoc:javadoc`
- [ ] Fix any JavaDoc warnings
- [ ] Load `cui-java-expert:cui-javadoc` for standards
- [ ] **Log**: Record completion in work-log

### Task 4: Manual Testing

**Phase**: verify
**Goal**: Verify functionality works as expected

**Acceptance Criteria**:
- Happy path verified
- Edge cases tested

**Checklist**:
- [ ] Test happy path scenarios
- [ ] Test edge cases
- [ ] Document test results
- [ ] **Log**: Record completion in work-log

---

## Phase: finalize (pending)

### Task 1: Commit Changes

**Phase**: finalize
**Goal**: Create final commit(s) per commit strategy

**Acceptance Criteria**:
- All changes committed
- Commit messages follow conventions

**Checklist**:
- [ ] Stage all changes
- [ ] Create commit with descriptive message
- [ ] Push to remote branch
- [ ] **Log**: Record completion in work-log

### Task 2: Create Pull Request

**Phase**: finalize
**Goal**: Prepare PR for review

**Acceptance Criteria**:
- PR created with summary
- Issue linked

**Checklist**:
- [ ] Create PR with summary
- [ ] Link to issue
- [ ] Add reviewers
- [ ] **Log**: Record completion in work-log

### Task 3: PR Workflow

**Phase**: finalize
**Goal**: Handle PR feedback and fixes

**Acceptance Criteria**:
- Sonar issues resolved
- Review comments addressed

**Checklist**:
- [ ] Execute /pr-doctor if configured
- [ ] Address review comments
- [ ] Request re-review if needed
- [ ] **Log**: Record completion in work-log

---

## Completion Criteria

Plan is complete when all phase tasks are marked `[x]`.
```

---

## Operation: get-config-template

**Input**: `branch`, `issue`, `build_system`

**Output**: Config format for config.toon

```toon
# Plan Configuration

plan_type: java
branch: {branch}
issue: {issue}

technology: java
build_system: {build_system}  # maven or gradle

compatibility: deprecations
commit_strategy: fine-granular
finalizing: pr-workflow
```

---

## Operation: get-references-template

**Input**: `issue_id`, `issue_title`, `issue_url`, `branch`

**Output**: References format for references.toon

```markdown
# References

## Issue

**GitHub Issue**: [{issue_id}: {issue_title}]({issue_url})

**Branch**: `{branch}`
**Base Branch**: `main`

## Related Files

**Implementation Files**:
- (populated during implement phase)

**Configuration Files**:
- (populated during implement phase)

**Test Files**:
- (populated during implement phase)

## Architecture Decision Records (ADRs)

**Related ADRs** (managed via `adr-management` skill):
- (populated during refine phase)

## Interface Specifications

**Related Interfaces** (managed via `interface-management` skill):
- (populated during refine phase)

## External Documentation

**CUI Java Standards**:
- Load `cui-java-expert:cui-java-core` for coding standards
- Load `cui-java-expert:cui-javadoc` for documentation standards
- Load `cui-java-expert:cui-java-unit-testing` for testing standards

## Dependencies

**Maven/Gradle Dependencies**:
- (populated during implement phase)

**Related Plans**:
- (add related plan references)
```

---

## Operation: generate-tasks

**Input**: `plan_id`, `components[]`

**Purpose**: Generate implement phase tasks and write them directly to plan.md.

**Components Input**: Provided by `cui-java-expert:java-analysis`:

```yaml
components:
  - name: "{component-name}"
    type: "class|interface|module|package|config"
    scope: "create|modify|refactor"
    module: "{module-name}"
    path: "{relative-path}"
    test_required: true|false
    test_path: "{test-path}"
    dependencies: [...]
    complexity: "low|medium|high"
```

**Process** (internal to this skill):
1. For each component, generate Java-specific task
2. Include CUI Java standards references
3. Write tasks directly to plan.md via scripts
4. Return success confirmation

**Task Template**:

```yaml
task:
  id: task-{n}
  title: "Implement {component-name}"
  phase: implement
  goal: "{goal-description}"
  technology: java
  module: "{module-name}"
  acceptance_criteria:
    - "{criterion-1}"
    - "Unit tests passing"
    - "JavaDoc complete"
  checklist:
    - "Create/modify implementation file at {path}"
    - "Add unit tests in {test_path}"
    - "Load `cui-java-expert:cui-java-unit-testing` for test patterns"
    - "Add JavaDoc (load `cui-java-expert:cui-javadoc`)"
    - "Verify `mvn test -pl {module}` passes"
    - "**Log**: Record completion in work-log"
```

**Write to plan.md**:
```bash
python3 {write-plan.py} --plan-dir .plan/plans/{plan_id} --add-task --phase implement --task-content "{task-yaml}"
```

**Output**:
```yaml
generate_tasks_result:
  status: success
  tasks_written: {count}
  plan_file: .plan/plans/{plan_id}/plan.md
  components_processed:
    - name: "{component-1}"
      task_id: "task-1"
      module: "{module-name}"
```

---

## Operation: get-next-phase

**Input**: `plan_id`, `current_phase`

**Output**: Next phase in workflow

| Current Phase | Next Phase |
|---------------|------------|
| init | refine |
| refine | implement |
| implement | verify |
| verify | finalize |
| finalize | complete |

---

## Operation: get-finalize-config

**Input**: `plan_id`

**Purpose**: Returns finalize phase behavior configuration.

**Output**:

```yaml
finalize_config:
  commit_strategy: fine-granular
  create_pr: true
  verification_required: true
  verification_command: "mvn verify"  # or "./gradlew build" for Gradle
```

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Phases | 5 |
| Technology | Java |
| Build Systems | Maven, Gradle |
| Analysis Skill | `cui-java-expert:java-analysis` |
| Branch Requirement | Feature branch required |
| Issue | Recommended |
| PR Workflow | Yes |
| User Interaction | Full confirmation |

---

## Auto-Detection Criteria

Use java plan type when:
1. `pom.xml` or `build.gradle` detected
2. Branch starts with feature/, fix/, task/, claude/
3. GitHub issue is referenced
4. Task involves Java code implementation
5. User explicitly selects "java"
