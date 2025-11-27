# plan-verify Handoff Protocol

**Scope**: Phase transitions, orchestrator communication, error patterns only. Internal delegations are documented in the main specification.

---

## Incoming Handoffs

### From: Orchestrator (Start Verify)

```toon
from: orchestrator
to: plan-verify-skill
handoff_id: verify-001
workflow: verification

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Run verification checks
```

### From: plan-implement (Phase Transition)

```toon
from: plan-implement-skill
to: plan-verify-skill
handoff_id: transition-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/

plan_status:
  previous_phase: implement
  current_phase: verify
  current_task: task-1

implementation_summary:
  files_created: 8
  files_modified: 3
  total_tests: 47
  technologies[1]: java

next_action: Begin verification
```

### From: User (Build Failure Decision)

```toon
from: user-interaction
to: plan-verify-skill
handoff_id: user-001

response:
  selection: 1|2|3|4

context:
  prompt_type: build_failure
```

### From: User (Quality Decision)

```toon
from: user-interaction
to: plan-verify-skill
handoff_id: user-002

response:
  selection: 1|2|3|4

context:
  prompt_type: quality_gate_failure
```

### From: User (Documentation Decision)

```toon
from: user-interaction
to: plan-verify-skill
handoff_id: user-003

response:
  selection: 1|2|3

context:
  prompt_type: documentation_incomplete
```

---

## Outgoing Handoffs

### Phase Complete → Finalize Phase

```toon
from: plan-verify-skill
to: plan-finalize-skill
handoff_id: transition-002

artifacts:
  plan_directory: .claude/plans/jwt-auth/

plan_status:
  previous_phase: verify
  current_phase: finalize
  current_task: task-1

verification_summary:
  build: passed
  tests: 147 passed, 0 failed
  coverage: 85%
  quality_gate: passed
  documentation: complete

next_action: Begin finalization
```

### To: Orchestrator (Verify Complete)

```toon
from: plan-verify-skill
to: orchestrator
handoff_id: verify-002
workflow: verification

task:
  description: Verification complete
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/

verification_results:
  build: passed
  tests: passed
  coverage: 85%
  quality_gate: passed
  documentation: complete

issues_fixed: 3
warnings_accepted: 2

next_action: Transition to finalize phase
```

---

## Error Handoffs

### Error: Build Failure

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

### Error: Quality Gate Failure

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
    critical_issues: 2

alternatives[3]:
- Fix quality issues (delegate to sonar-workflow)
- Return to implement phase (improve coverage)
- Accept technical debt (document reasons)
```

### Error: Documentation Incomplete

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

alternatives[3]:
- Fix documentation issues
- Add to backlog (create follow-up task)
- Proceed anyway (mark as incomplete)
```

### Error: Coverage Below Threshold

```toon
from: plan-verify-skill
to: caller
handoff_id: error-004

task:
  status: blocked

error:
  type: coverage_below_threshold
  message: Test coverage below required threshold
  details:
    current_coverage: 72%
    required_coverage: 80%
    gap: 8%

alternatives[3]:
- Add tests for uncovered areas (return to implement)
- Accept lower coverage (document justification)
- Adjust coverage threshold (if appropriate)
```

### Error: ADR Mismatch

```toon
from: plan-verify-skill
to: caller
handoff_id: error-005

task:
  status: blocked

error:
  type: adr_mismatch
  message: Implementation does not match ADR decision
  details:
    adr: ADR-015
    decision: "Use HMAC-SHA256 for token signing"
    implementation: "Found RSA algorithm in JwtService.java:67"

alternatives[3]:
- Update implementation to match ADR
- Update ADR to match implementation
- Document as accepted deviation
```

---

## Related

- [Verify Specification](verify.md) - Full workflow specification (includes internal delegations)
- [Implement Phase](../plan-implement/implement.md) - Previous phase specification
- [Plan Types](../plan-types.md) - Init phase router
