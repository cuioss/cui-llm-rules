# plan-implement Handoff Protocol

**Purpose**: External interface specifications for the implement phase skill

**Scope**: Phase transitions, orchestrator communication, error patterns only. Internal delegations are documented in the main specification.

---

## Incoming Handoffs

### From: Orchestrator (Start Implement)

```toon
from: orchestrator
to: plan-implement-skill
handoff_id: implement-001
workflow: task-execution

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Execute implementation tasks
```

### From: plan-refine (Phase Transition)

```toon
from: plan-refine-skill
to: plan-implement-skill
handoff_id: transition-001

artifacts:
  plan_directory: .claude/plans/jwt-auth/
  implementation_requirements: .claude/plans/jwt-auth/implementation-requirements.md

plan_status:
  previous_phase: refine
  current_phase: implement
  current_task: task-6

implementation_tasks[5]{id,name,complexity}:
task-6,Create JwtService,medium
task-7,Create TokenValidator,medium
task-8,Implement RefreshTokenService,high
task-9,Add JWT configuration,low
task-10,Update POM dependencies,low

next_action: Begin task execution
```

### From: User (Resume Decision)

```toon
from: user-interaction
to: plan-implement-skill
handoff_id: user-001

response:
  selection: 1|2|3

context:
  prompt_type: resume_task
  task_id: task-7
  progress: 2/5
```

### From: User (Clarification Response)

```toon
from: user-interaction
to: plan-implement-skill
handoff_id: user-002

response:
  clarification: |
    For the token validator, use HMAC-SHA256 algorithm.
    Key should be loaded from configuration.

context:
  prompt_type: clarification_needed
  task_id: task-7
```

### From: User (Error Decision)

```toon
from: user-interaction
to: plan-implement-skill
handoff_id: user-003

response:
  selection: 1|2|3|4

context:
  prompt_type: build_failure|test_failure|coverage_below
```

---

## Outgoing Handoffs

### Phase Complete → Verify Phase

```toon
from: plan-implement-skill
to: plan-verify-skill
handoff_id: transition-002

artifacts:
  plan_directory: .claude/plans/jwt-auth/

plan_status:
  previous_phase: implement
  current_phase: verify
  current_task: task-1

implementation_summary:
  total_files_created: 8
  total_files_modified: 3
  total_tests: 47
  overall_coverage: 85%

next_action: Begin verification
```

### To: Orchestrator (Implement Complete)

```toon
from: plan-implement-skill
to: orchestrator
handoff_id: implement-002
workflow: task-execution

task:
  description: Implementation complete
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/

tasks_completed[5]{id,name,files_created}:
task-6,Create JwtService,JwtService.java
task-7,Create TokenValidator,TokenValidator.java
task-8,Implement RefreshTokenService,RefreshTokenService.java
task-9,Add JWT configuration,application.properties
task-10,Update POM dependencies,pom.xml

implementation_summary:
  total_files_created: 8
  total_files_modified: 3
  total_tests: 47
  overall_coverage: 85%

next_action: Transition to verify phase
```

---

## Error Handoffs

### Error: Build Failure

```toon
from: plan-implement-skill
to: caller
handoff_id: error-001

task:
  status: blocked

error:
  type: build_failure
  message: Build failed during task execution
  details: |
    Compilation error in JwtService.java:45
    Cannot resolve symbol 'TokenGenerator'

alternatives[4]:
- Fix build error and retry
- View full build log
- Skip to next task (mark as blocked)
- Abort implementation phase
```

### Error: Test Failure

```toon
from: plan-implement-skill
to: caller
handoff_id: error-002

task:
  status: blocked

error:
  type: test_failure
  message: Tests failed during task execution
  details:
    failed_tests[2]:
    - JwtServiceTest::testGenerateToken - assertion failed
    - JwtServiceTest::testExpiration - timeout

alternatives[4]:
- Fix failing tests
- View test details
- Mark task as partial
- Skip to next task
```

### Error: Coverage Below Threshold

```toon
from: plan-implement-skill
to: caller
handoff_id: error-003

task:
  status: blocked

error:
  type: coverage_below_threshold
  message: Coverage below required threshold
  details:
    current_coverage: 72%
    required_coverage: 80%

alternatives[3]:
- Add tests for uncovered areas
- Accept current coverage
- Adjust coverage target
```

### Error: Dependency Not Met

```toon
from: plan-implement-skill
to: caller
handoff_id: error-004

task:
  status: blocked

error:
  type: dependency_not_met
  message: Cannot start task - dependency not complete
  details:
    task: task-7 (Create TokenValidator)
    depends_on: task-6 (Create JwtService)

alternatives[3]:
- Complete dependency first
- Skip dependency check (proceed anyway)
- Choose different task
```

### Error: Acceptance Criterion Failed

```toon
from: plan-implement-skill
to: caller
handoff_id: error-005

task:
  status: blocked

error:
  type: acceptance_criterion_failed
  message: Acceptance criterion not met
  details:
    task: task-6 (Create JwtService)
    criterion: "Tokens include standard claims"
    reason: Token missing 'iat' (issued at) claim

alternatives[4]:
- Continue implementing to meet criterion
- Modify criterion (update plan)
- Mark as partial and proceed
- Skip task (mark as blocked)
```

---

## Related

- [Implement Specification](implement.md) - Full workflow specification (includes internal delegations)
- [Refine Phase](../plan-refine/refine.md) - Previous phase specification
- [Plan Types](../plan-types.md) - Init phase router
