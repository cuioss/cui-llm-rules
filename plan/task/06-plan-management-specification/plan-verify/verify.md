# Verify Phase Specification

**Input**: Plan from implement phase with completed implementation tasks

**Output**: Verified implementation with passing builds, quality checks, and documentation

**Use Cases**:
- Running full build verification
- Executing quality checks (Sonar, linting)
- Reviewing documentation completeness
- Validating acceptance criteria fulfillment

---

## Operations

The verify phase provides three core operations:

| Operation | Description | Output |
|-----------|-------------|--------|
| **run-build** | Execute build with tests | Build status with coverage |
| **check-quality** | Run quality analysis (Sonar, linting) | Quality report with issues |
| **review-docs** | Verify documentation completeness | Documentation status |

---

## Prerequisites

Before verify phase can start:

1. **Implement phase completed** - All implementation tasks marked `[x]`
2. **Code exists** - Implementation files created/modified
3. **Tests exist** - Unit/integration tests implemented
4. **Current phase is verify** - Transitioned from implement
5. **Build system available** - Maven/npm configured and working

---

## Verify Phase Workflow

### Step 1: Read Context

**Load plan and configuration** (via `plan-files` skill):
```
plan-files.read-plan:
- All tasks in verify phase
- Current task (first pending or in_progress)
- Completed implementation tasks for reference

plan-files.read-config:
- Technology (java, javascript, mixed)
- Build system (maven, npm/npx)
- Commit strategy (for any fix commits)

plan-files.get-references:
- Implementation files created
- Test files created
- Documentation files
```

**Gather implementation summary**:
```
From references.md:
- Files created during implement phase
- Files modified during implement phase
- Test coverage targets
```

### Step 2: Run Full Build

**Build Execution by Technology**:

| Technology | Agent | Command |
|------------|-------|---------|
| Java | maven-builder | `./mvnw -l target/build.log -Ppre-commit clean install` |
| JavaScript | npm-builder | `npm run build && npm test` |
| Mixed | Both agents | Sequential execution |

**TOON Handoff to Build Agent**:
```toon
from: plan-verify-skill
to: maven-builder-agent
handoff_id: build-001

operation: full-build
plan_directory: .claude/plans/jwt-auth/

build_options:
  profile: pre-commit
  clean: true
  test: true
  coverage: true

expected_results:
  compile: pass
  tests: pass
  coverage_threshold: 80

next_action: Execute full build with quality checks
```

**Build Result Handling**:

```toon
from: maven-builder-agent
to: plan-verify-skill
handoff_id: build-002

build_status:
  compile: passed
  tests: passed
  test_count: 147
  test_failures: 0
  coverage: 85%

quality_checks:
  checkstyle: passed
  pmd: passed (2 warnings)
  javadoc: passed

artifacts:
  log_file: target/build-output-2025-01-15-143022.log
  coverage_report: target/site/jacoco/index.html

next_action: Proceed to quality check
```

**If Build Fails** (via `AskUserQuestion`):
```
## Build Failed

Build verification failed.

**Error Summary**:
- Compilation: {passed|failed}
- Tests: {X failed, Y passed}
- Coverage: {N%} (target: 80%)

**Failure Details**:
{error summary from build log}

Options:
1. View full build log
2. Return to implement phase (fix issues)
3. Delegate to fix agent (auto-fix)
4. Skip verification (mark as partial)

Select (1-4):
```

### Step 3: Check Quality

**Quality Check Types**:

| Check | Tool | Agent |
|-------|------|-------|
| Static Analysis | SonarQube | sonar-workflow |
| Code Style | Checkstyle/ESLint | Build agent |
| Documentation | JavaDoc/JSDoc validator | Build agent |
| Coverage | JaCoCo/Istanbul | Build agent |

**TOON Handoff to Sonar Workflow**:
```toon
from: plan-verify-skill
to: sonar-workflow-skill
handoff_id: quality-001

operation: fetch-issues
project_key: {sonar-project-key}
pull_request: {pr-number}

filters:
  severities: BLOCKER,CRITICAL,MAJOR
  new_issues_only: true

next_action: Fetch Sonar issues for quality check
```

**Sonar Result**:
```toon
from: sonar-workflow-skill
to: plan-verify-skill
handoff_id: quality-002

project_key: cui-jwt
pull_request: 456

issues:
  total: 3
  by_severity:
    BLOCKER: 0
    CRITICAL: 1
    MAJOR: 2
  by_type:
    BUG: 1
    CODE_SMELL: 2
    VULNERABILITY: 0

issues_list[3]:
- rule: java:S1135, severity: MAJOR, file: JwtService.java:45, message: "Complete this TODO"
- rule: java:S1068, severity: MAJOR, file: TokenValidator.java:12, message: "Remove unused field"
- rule: java:S2259, severity: CRITICAL, file: RefreshTokenService.java:78, message: "Null check required"

quality_gate: FAILED

next_action: Fix quality issues before proceeding
```

**Quality Issue Handling** (via `AskUserQuestion`):
```
## Quality Issues Found

SonarQube quality gate: FAILED

**Issues Summary**:
| Severity | Count | Types |
|----------|-------|-------|
| CRITICAL | 1 | BUG |
| MAJOR | 2 | CODE_SMELL |

**Critical Issues** (must fix):
1. RefreshTokenService.java:78 - Null check required (java:S2259)

**Major Issues** (recommended):
2. JwtService.java:45 - Complete this TODO (java:S1135)
3. TokenValidator.java:12 - Remove unused field (java:S1068)

Options:
1. Fix all issues (delegate to sonar-workflow)
2. Fix critical only (suppress major)
3. View issue details
4. Return to implement phase

Select (1-4):
```

**If Fixing Issues**:
```toon
from: plan-verify-skill
to: sonar-workflow-skill
handoff_id: fix-001

operation: fix-issues
issues[3]: [issue-keys]
strategy: fix-preferred

next_action: Fix quality issues
```

### Step 4: Review Documentation

**Documentation Checks**:

| Document Type | Check | Tool |
|---------------|-------|------|
| JavaDoc | Public methods documented | javadoc plugin |
| JSDoc | Exported functions documented | ESLint JSDoc plugin |
| README | Updated if needed | Manual review |
| ADRs | Referenced ADRs complete | adr-management skill |
| Interfaces | Interface specs accurate | interface-management skill |

**Documentation Review Process**:
```
1. Check JavaDoc/JSDoc completeness:
   - All public methods have documentation
   - Parameters documented
   - Return values documented
   - Exceptions documented

2. Check README updates:
   - Configuration changes documented
   - API changes documented
   - Usage examples updated

3. Verify referenced ADRs:
   - ADR exists and is approved
   - ADR content matches implementation

4. Verify interface specifications:
   - Interface spec exists
   - Endpoints match implementation
   - Request/response formats accurate
```

**TOON Handoff for Documentation Check**:
```toon
from: plan-verify-skill
to: plan-files-skill
handoff_id: docs-001

operation: get-references
plan_directory: .claude/plans/jwt-auth/
```

**Then verify each reference**:
```toon
# For ADR verification
from: plan-verify-skill
to: adr-management-skill
handoff_id: adr-verify-001

operation: read
adr_identifier: ADR-015

# For Interface verification
from: plan-verify-skill
to: interface-management-skill
handoff_id: if-verify-001

operation: read
interface_identifier: IF-042
```

**Documentation Status Report**:
```
## Documentation Review

| Document | Status | Notes |
|----------|--------|-------|
| JavaDoc | ✅ Pass | All public methods documented |
| README | ⚠️ Needs update | Missing configuration section |
| ADR-015 | ✅ Pass | Implementation matches decision |
| IF-042 | ⚠️ Needs update | New endpoint not documented |

Issues to address:
1. Update README with JWT configuration properties
2. Add /auth/refresh endpoint to IF-042

Options:
1. Fix documentation issues
2. Mark as TODO and proceed
3. Return to implement phase

Select (1-3):
```

### Step 5: Manual Testing (Optional)

**Manual Test Checklist**:
```markdown
### Manual Testing Checklist

- [ ] Happy path scenarios tested
- [ ] Edge cases verified
- [ ] Error handling confirmed
- [ ] Performance acceptable
- [ ] Security requirements met
```

**User Prompt** (via `AskUserQuestion`):
```
## Manual Testing

Would you like to perform manual testing?

Current status:
- Build: ✅ Passed
- Quality: ✅ Passed (or fixed)
- Documentation: ✅ Complete

Manual testing areas:
1. Authentication flow - login, token refresh, logout
2. Error handling - invalid tokens, expired tokens
3. Edge cases - concurrent requests, rate limiting

Options:
1. Skip manual testing (proceed to finalize)
2. Perform manual testing (provide checklist)
3. Return to previous step

Select (1-3):
```

### Step 6: Update Progress and Transition

**After all verification tasks complete** (via `plan-files` skill):

1. Mark all verify tasks `[x]` in plan.md
2. Update Phase Progress Table
3. Update references.md with any new artifacts
4. Check if phase complete
5. Transition to finalize phase

**TOON Handoff to plan-files**:
```toon
from: plan-verify-skill
to: plan-files-skill
handoff_id: progress-001

operation: update-progress
plan_directory: .claude/plans/jwt-auth/

update:
  task_id: verify-task-4
  status: completed
  checklist_items[4]: 0, 1, 2, 3

phase_transition:
  from_phase: verify
  to_phase: finalize
  status: completed
```

**Transition Prompt** (via `AskUserQuestion`):
```
## Verification Phase Complete

All verification tasks are complete:

| Task | Status |
|------|--------|
| Run Full Build | ✅ Passed |
| Check Quality | ✅ Passed |
| Review Documentation | ✅ Complete |
| Manual Testing | ✅ Skipped |

**Summary**:
- Build: 147 tests passed, 85% coverage
- Quality: 0 issues (3 fixed during verification)
- Documentation: Complete

Options:
1. Proceed to finalize phase
2. Review verification results
3. Return to implement (additional changes)

Select (1-3):
```

---

## Verify Phase Tasks

Standard verify phase tasks:

```markdown
## Phase: verify (in_progress)

### Task 1: Run Full Build
**Goal**: Ensure all code compiles and tests pass

**Checklist**:
- [ ] Delegate to build agent (maven-builder or npm-builder)
- [ ] Verify compilation succeeds
- [ ] Verify all tests pass
- [ ] Verify coverage threshold met (≥80%)
- [ ] Fix any failures before proceeding

### Task 2: Code Quality Check
**Goal**: Verify code meets quality standards

**Checklist**:
- [ ] Run static analysis (Sonar/linting)
- [ ] Review quality gate status
- [ ] Fix or suppress issues as appropriate
- [ ] Document any accepted technical debt

### Task 3: Manual Testing
**Goal**: Verify functionality works as expected

**Checklist**:
- [ ] Test happy path scenarios
- [ ] Test edge cases
- [ ] Verify error handling
- [ ] Document test results

### Task 4: Documentation Review
**Goal**: Ensure documentation is complete

**Checklist**:
- [ ] Verify JavaDoc/JSDoc complete
- [ ] Update README if needed
- [ ] Verify ADR/interface docs current
- [ ] Check for outdated documentation
```

---

## Build Agent Delegation

### Java Build (maven-builder)

**Agent**: `cui-maven:maven-builder`

**Delegation Pattern**:
```toon
from: plan-verify-skill
to: maven-builder-agent
handoff_id: maven-001

operation: full-build

build_config:
  profile: pre-commit
  goals: clean install
  coverage: true

quality_config:
  checkstyle: true
  pmd: true
  javadoc: true

timeout: 300000

next_action: Execute Maven build with quality checks
```

**Build Response**:
```toon
from: maven-builder-agent
to: plan-verify-skill
handoff_id: maven-002

build_status:
  overall: SUCCESS
  compile: passed
  tests: passed (147 tests)
  coverage: 85%

quality_status:
  checkstyle: passed
  pmd: 2 warnings (acceptable)
  javadoc: passed

artifacts:
  log_file: target/build-output-2025-01-15-143022.log
  coverage_report: target/site/jacoco/index.html
  test_report: target/surefire-reports/

next_action: Proceed to quality check
```

### JavaScript Build (npm-builder)

**Agent**: `cui-frontend-expert:npm-builder`

**Delegation Pattern**:
```toon
from: plan-verify-skill
to: npm-builder-agent
handoff_id: npm-001

operation: full-build

build_config:
  scripts[3]: lint, test, build
  coverage: true

quality_config:
  eslint: true
  prettier: true
  jsdoc: true

timeout: 120000

next_action: Execute npm build with quality checks
```

**Build Response**:
```toon
from: npm-builder-agent
to: plan-verify-skill
handoff_id: npm-002

build_status:
  overall: SUCCESS
  lint: passed
  tests: passed (52 tests)
  build: passed
  coverage: 82%

quality_status:
  eslint: 0 errors, 3 warnings
  prettier: formatted
  jsdoc: complete

artifacts:
  coverage_report: coverage/lcov-report/index.html
  test_report: coverage/test-results.json

next_action: Proceed to quality check
```

---

## Quality Check Patterns

### Sonar Quality Gate

**Quality Gate Criteria**:
```
Pass if:
- Coverage ≥ 80%
- Duplications ≤ 3%
- No BLOCKER issues
- No CRITICAL bugs
- Maintainability rating ≥ B
```

**Quality Issue Classification**:

| Severity | Action | Rationale |
|----------|--------|-----------|
| BLOCKER | Must fix | Security/reliability critical |
| CRITICAL | Must fix | Major bugs or vulnerabilities |
| MAJOR | Should fix | Code quality issues |
| MINOR | May suppress | Style issues with justification |
| INFO | May ignore | Informational only |

### Linting Quality

**Java (Checkstyle/PMD)**:
- Zero errors required
- Warnings acceptable if documented

**JavaScript (ESLint)**:
- Zero errors required
- Warnings acceptable for specific rules

---

## Error Handling

### Build Failure

```toon
from: plan-verify-skill
to: caller
handoff_id: error-001

task:
  status: blocked

error:
  type: build_failure
  message: Build verification failed
  details:
    compile: passed
    tests: 3 failed
    failures[3]:
    - JwtServiceTest::testTokenGeneration - assertion failed
    - TokenValidatorTest::testExpiredToken - timeout
    - RefreshTokenServiceTest::testRotation - null pointer

alternatives[4]:
- Return to implement phase (fix failing tests)
- View full test report
- Run specific failing tests only
- Skip failing tests (not recommended)
```

### Quality Gate Failure

```toon
from: plan-verify-skill
to: caller
handoff_id: error-002

task:
  status: blocked

error:
  type: quality_gate_failure
  message: Quality gate failed
  details:
    coverage: 72% (required: 80%)
    duplications: 5% (required: ≤3%)
    issues: 2 CRITICAL

quality_gate_conditions[3]:
- Coverage: FAILED (72% < 80%)
- Duplications: FAILED (5% > 3%)
- Critical Issues: FAILED (2 > 0)

alternatives[3]:
- Fix quality issues (delegate to sonar-workflow)
- Return to implement phase (improve coverage)
- Accept technical debt (document reasons)
```

### Documentation Incomplete

```toon
from: plan-verify-skill
to: caller
handoff_id: error-003

task:
  status: blocked

error:
  type: documentation_incomplete
  message: Documentation review failed
  details:
    missing_javadoc[2]:
    - JwtService.generateToken() - no documentation
    - TokenValidator.validate() - missing @param tags
    outdated_docs[1]:
    - README.md - missing configuration section

alternatives[3]:
- Fix documentation issues
- Add to backlog (create follow-up task)
- Proceed anyway (mark as incomplete)
```

---

## Input/Output Summary

### Input

| Source | Data | Required |
|--------|------|----------|
| plan.md | Verify tasks, completed implement tasks | Yes |
| config.md | Technology, build system, quality settings | Yes |
| references.md | Implementation files, ADRs, interfaces | Yes |
| Implementation code | Source files to verify | Yes |
| User | Decisions on failures, manual test results | When needed |

### Output

| Artifact | Location | Content |
|----------|----------|---------|
| Build logs | `target/build-output-*.log` | Full build output |
| Coverage report | `target/site/jacoco/` | Coverage analysis |
| Quality report | SonarQube | Issue analysis |
| Updated plan.md | `.claude/plans/{task}/plan.md` | Completed verify tasks |
| Updated references.md | `.claude/plans/{task}/references.md` | Verification artifacts |

---

## Integration Points

### With plan-implement

Verify phase receives:
- Implemented source code
- Test files
- Modified configuration
- Implementation summary

### With plan-finalize

Verify phase produces:
- Verified code (build passes)
- Quality gate status
- Documentation status
- Ready-for-commit state

### With plan-files

During verification:
- Read tasks via `read-plan`
- Read configuration via `read-config`
- Read references via `get-references`
- Update progress via `update-progress`

### With Build Agents

During verification:
- Delegate to `maven-builder` for Java builds
- Delegate to `npm-builder` for JavaScript builds
- Receive build status and artifacts

### With sonar-workflow

During quality check:
- Fetch Sonar issues
- Triage and fix issues
- Update quality status

### With Documentation Skills

During documentation review:
- Verify ADRs via `adr-management`
- Verify interfaces via `interface-management`
- Check documentation completeness

---

## Comparison with Implement Phase

| Aspect | Implement Phase | Verify Phase |
|--------|-----------------|--------------|
| **Focus** | Code creation | Code validation |
| **Input** | Tasks from refine | Code from implement |
| **Output** | Working code | Verified code |
| **User Interaction** | Clarifications | Failure decisions |
| **Delegation** | Language agents | Build/quality agents |
| **Artifacts** | Source code, tests | Build logs, reports |

---

## Technology-Specific Standards

### For Java Verification

**Build Requirements**:
- Maven pre-commit profile passes
- All unit tests pass
- Coverage ≥ 80%
- Checkstyle/PMD clean

**Quality Requirements**:
- Sonar quality gate passes
- No BLOCKER/CRITICAL issues
- Maintainability rating ≥ B

**Documentation Requirements**:
- All public methods have JavaDoc
- @param, @return, @throws documented
- Package-info.java present

### For JavaScript Verification

**Build Requirements**:
- npm build succeeds
- All Jest tests pass
- Coverage ≥ 80%
- ESLint clean (errors)

**Quality Requirements**:
- Sonar quality gate passes (if configured)
- No ESLint errors
- Prettier formatting applied

**Documentation Requirements**:
- All exported functions have JSDoc
- @param, @returns documented
- Module documentation present

---

## Related

- [Handoff Protocol](handoff.md) - TOON incoming/outgoing specifications
- [Plan Types](../plan-types.md) - Init phase router
- [Implement Phase](../plan-implement/implement.md) - Previous phase specification
- [Finalize Phase](../plan-finalize/finalize.md) - Next phase specification
- [Templates & Workflow](../templates-workflow.md) - Phase workflow details
- [Persistence](../plan-files/persistence.md) - File format specifications
- [API Specification](../api.md) - Complete skill API
