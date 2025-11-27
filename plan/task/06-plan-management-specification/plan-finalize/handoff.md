# plan-finalize Handoff Protocol

**Purpose**: External interface specifications for the finalize phase skill

**Scope**: Phase transitions, orchestrator communication, error patterns only. Internal delegations are documented in the main specification.

---

## Incoming Handoffs

### From: Orchestrator (Start Finalize)

```toon
from: orchestrator
to: plan-finalize-skill
handoff_id: finalize-001
workflow: finalization

artifacts:
  plan_directory: .claude/plans/jwt-auth/

next_action: Begin finalization workflow
```

### From: plan-verify (Phase Transition)

```toon
from: plan-verify-skill
to: plan-finalize-skill
handoff_id: transition-001

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

### From: User (Commit Message Decision)

```toon
from: user-interaction
to: plan-finalize-skill
handoff_id: user-001

response:
  selection: accept|edit|regenerate

context:
  prompt_type: commit_message_confirmation
```

### From: User (PR Confirmation)

```toon
from: user-interaction
to: plan-finalize-skill
handoff_id: user-002

response:
  selection: 1|2|3

context:
  prompt_type: pr_creation
  options[3]:
  - Create PR now
  - Edit title/body first
  - Skip PR creation
```

### From: User (Review Comment Decision)

```toon
from: user-interaction
to: plan-finalize-skill
handoff_id: user-003

response:
  selection: 1|2|3|4

context:
  prompt_type: review_comment_action
  comment_id: "comment-123"
```

### From: User (Force Push Confirmation)

```toon
from: user-interaction
to: plan-finalize-skill
handoff_id: user-004

response:
  confirmed: true|false

context:
  prompt_type: force_push_warning
  reason: rebase_required
```

---

## Outgoing Handoffs

### To: Orchestrator (Finalize Complete)

```toon
from: plan-finalize-skill
to: orchestrator
handoff_id: finalize-002
workflow: finalization

task:
  description: Finalization complete
  status: completed

artifacts:
  plan_directory: .claude/plans/jwt-auth/

finalize_results:
  commits: 1
  commit_hash: abc123def456
  pushed: true
  pr_created: true
  pr_url: "https://github.com/org/repo/pull/456"
  pr_status: open
  reviews_processed: 3

plan_status:
  all_phases_complete: true
  ready_for_merge: pending_approval

next_action: Await PR approval
```

### Plan Complete (All Phases Done)

```toon
from: plan-finalize-skill
to: orchestrator
handoff_id: complete-001

plan_status:
  status: completed
  all_phases: done

artifacts:
  plan_directory: .claude/plans/jwt-auth/

summary:
  phase_count: 5
  tasks_completed: 15
  commits: 1
  pr_url: "https://github.com/org/repo/pull/456"

next_action: Plan archived - await PR merge
```

---

## Error Handoffs

### Error: Artifacts Detected

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-001

task:
  status: blocked

error:
  type: artifacts_detected
  message: Build artifacts detected in staging area
  details:
    artifacts[3]:
    - target/classes/JwtService.class
    - target/test-classes/JwtServiceTest.class
    - .idea/workspace.xml

alternatives[3]:
- Clean artifacts and retry commit
- Review .gitignore configuration
- Manually exclude specific files
```

### Error: Commit Failed

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-002

task:
  status: blocked

error:
  type: commit_failed
  message: Git commit failed
  details:
    reason: pre-commit hook failed
    hook_output: |
      Checkstyle violation in JwtService.java:45
      Missing Javadoc for public method

alternatives[3]:
- Fix checkstyle violations and retry
- Skip hooks (--no-verify) - not recommended
- Review and update pre-commit configuration
```

### Error: Push Rejected

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-003

task:
  status: blocked

error:
  type: push_rejected
  message: Push rejected by remote
  details:
    reason: non-fast-forward
    remote_ahead: 3
    local_ahead: 1

alternatives[3]:
- Fetch and rebase on remote changes
- Merge remote changes into branch
- Force push with lease (requires confirmation)
```

### Error: PR Creation Failed

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-004

task:
  status: blocked

error:
  type: pr_creation_failed
  message: Failed to create pull request
  details:
    reason: "A pull request already exists for feature/jwt-auth"
    existing_pr:
      number: 455
      url: "https://github.com/org/repo/pull/455"

alternatives[2]:
- Update existing PR #455 instead
- Close existing PR and create new one
```

### Error: Review Conflict

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-005

task:
  status: blocked

error:
  type: review_conflict
  message: Conflicting review feedback received
  details:
    file: JwtService.java
    line: 67
    comment_1:
      author: reviewer1
      body: "Please add null check"
    comment_2:
      author: reviewer2
      body: "Remove defensive programming, use assertions"

alternatives[3]:
- Ask reviewers to resolve conflict
- Implement reviewer1's suggestion (more senior)
- Present both options to user for decision
```

### Error: Merge Conflicts

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-006

task:
  status: blocked

error:
  type: merge_conflict
  message: Merge conflicts detected with base branch
  details:
    conflicts[2]:
    - src/main/java/com/example/auth/SecurityConfig.java
    - src/main/resources/application.properties
    base_branch: main

alternatives[3]:
- Rebase on main and resolve conflicts
- Merge main into feature branch and resolve
- Ask user for conflict resolution guidance
```

### Error: CI Failed

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-007

task:
  status: blocked

error:
  type: ci_failed
  message: CI checks failed on PR
  details:
    pr_number: 456
    checks[3]:
    - name: build
      status: failed
      details: "Compilation error in JwtService.java"
    - name: test
      status: skipped
    - name: sonar
      status: skipped

alternatives[2]:
- Fix build errors and push update
- Review CI logs for detailed error
```

---

## Related

- [Finalize Specification](finalize.md) - Full workflow specification (includes internal delegations)
- [Verify Phase](../plan-verify/verify.md) - Previous phase specification
- [Plan Types](../plan-types.md) - Init phase router
