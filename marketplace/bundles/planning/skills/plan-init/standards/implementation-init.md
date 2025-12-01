# Implementation Init Standards

**Output**: 5-phase plan (init→refine→implement→verify→finalize)

**Use Cases**:
- Java implementation tasks
- JavaScript/frontend tasks
- Plugin/marketplace component tasks
- Requirements engineering with code artifacts

## Phase Structure Template

When creating an implementation plan, generate this structure:

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
- Build system identified
- Technology stack determined
- Branch validated

**Checklist**:
- [ ] Check current git branch
- [ ] Detect build system (pom.xml, package.json, etc.)
- [ ] Parse issue from parameters or branch name
- [ ] Determine technology stack

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

---

## Phase: refine (pending)

### Task 1: Analyze Requirements

**Phase**: refine
**Goal**: Break down task into implementable units

**Acceptance Criteria**:
- Components clearly identified
- Dependencies mapped

**Checklist**:
- [ ] Review issue requirements
- [ ] Identify implementation components
- [ ] Map component dependencies
- [ ] Estimate complexity per component

### Task 2: Plan Implementation Tasks

**Phase**: refine
**Goal**: Create detailed task list for implement phase

**Acceptance Criteria**:
- All tasks have acceptance criteria
- Tasks ordered by dependencies

**Checklist**:
- [ ] Generate implementation tasks
- [ ] Add acceptance criteria per task
- [ ] Order by dependencies
- [ ] Add tasks to implement phase

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

---

## Phase: implement (pending)

{Tasks generated dynamically by refine phase}

---

## Phase: verify (pending)

### Task 1: Run Full Build

**Phase**: verify
**Goal**: Ensure all code compiles and tests pass

**Acceptance Criteria**:
- Build successful
- All tests passing
- Coverage thresholds met

**Checklist**:
- [ ] Run build (maven/npm)
- [ ] Fix any build failures
- [ ] Verify test coverage

### Task 2: Code Quality Check

**Phase**: verify
**Goal**: Verify code meets quality standards

**Acceptance Criteria**:
- No critical violations
- Quality gates passed

**Checklist**:
- [ ] Run linter/static analysis
- [ ] Fix violations
- [ ] Review Sonar issues (if applicable)

### Task 3: Manual Testing

**Phase**: verify
**Goal**: Verify functionality works as expected

**Acceptance Criteria**:
- Happy path verified
- Edge cases tested

**Checklist**:
- [ ] Test happy path scenarios
- [ ] Test edge cases
- [ ] Document test results

### Task 4: Documentation Review

**Phase**: verify
**Goal**: Ensure documentation is complete

**Acceptance Criteria**:
- All code documented
- README updated if needed

**Checklist**:
- [ ] Verify JavaDoc/JSDoc complete
- [ ] Update README if needed
- [ ] Check ADR/interface docs

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

### Task 3: PR Workflow

**Phase**: finalize
**Goal**: Handle PR feedback and fixes

**Acceptance Criteria**:
- Sonar issues resolved
- Review comments addressed

**Checklist**:
- [ ] Execute /pr-fix if configured
- [ ] Address review comments
- [ ] Request re-review if needed

---

## Completion Criteria

All phases must be completed and all tasks marked with `[x]` before plan is complete.

**Final Verification**:
- [ ] All phases completed
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Build successful
- [ ] Documentation updated
- [ ] PR merged (if applicable)
```

## Config Format (TOON)

```toon
# Plan Configuration

plan_type: implementation
branch: {branch-name}
issue: {issue-id}

technology: {java|javascript|mixed}
build_system: {maven|gradle|npm}

compatibility: {deprecations|breaking}
commit_strategy: {fine-granular|phase-specific|complete}
finalizing: {pr-workflow|commit-only}
```

## References Template

```markdown
# References

## Issue

**GitHub Issue**: [{issue-id}: {issue-title}]({issue-url})

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

**To create new ADR**: Use `adr-management` skill operations

## Interface Specifications

**Related Interfaces** (managed via `interface-management` skill):
- (populated during refine phase)

**To create new interface**: Use `interface-management` skill operations

## External Documentation

**Standards and Specifications**:
- (add relevant external docs)

**Libraries and Tools**:
- (add relevant library docs)

## Dependencies

**Maven Dependencies**:
- (populated during implement phase)

**Related Plans**:
- (add related plan references)
```
