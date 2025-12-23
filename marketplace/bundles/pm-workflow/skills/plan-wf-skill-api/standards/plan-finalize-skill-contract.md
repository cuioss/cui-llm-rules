# Plan Finalize Skill Contract

Workflow skill for finalize phase - verifies work, creates findings, delegates fixes.

**Implementation**: `pm-workflow:plan-finalize`

---

## Purpose

The finalize skill:

1. Runs a multi-step verification pipeline
2. Parses output for findings
3. Auto-fixes where possible
4. Creates fix tasks for remaining findings
5. Creates commit and PR if all verification passes

**Flow**: Completed tasks → Verification pipeline → Commit/PR or Fix tasks

**Pattern**: Quality-Manager (orchestrates verification, delegates fixes)

---

## Invocation

**Phase**: `finalize`

**Agent invocation**:
```bash
plan-phase-agent plan_id={plan_id} phase=finalize
```

**Skill resolution**:
```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill --phase finalize
```

Result:
```toon
status: success
domain: system
phase: finalize
workflow_skill: pm-workflow:plan-finalize
```

---

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

---

## Pipeline Overview

```
    execute phase complete
           │
           ▼
    ┌─────────────────────────────────────────────────────┐
    │              FINALIZE PIPELINE                      │
    │                                                     │
    │  local_opt → conformance → doc_sync → final_build  │
    │                                                     │
    │  commit_push → pr_roundtrip → sonar_roundtrip      │
    └─────────────────────────────────────────────────────┘
           │
     findings?
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
 findings     no findings
    │             │
    ▼             ▼
 create       COMPLETE
 tasks
    │
    ▼
 back to execute
```

---

## Workflow Skill Responsibilities

The workflow skill autonomously:

1. **Loads quality knowledge**: Calls `resolve-domain-skills --profile quality` per domain
2. **Loads triage extensions**: Calls `resolve-workflow-skill-extension --type triage` per domain
3. **Runs verification pipeline**: Executes each step in order
4. **Collects findings**: Parses output for issues
5. **Creates fix tasks**: For non-auto-fixable findings
6. **Creates commit/PR**: If all verification passes

```
Finalize Phase Workflow:
┌──────────────────────────────────────────────────────────────────┐
│ 1. Read domains from config.toon.domains                         │
│ 2. For each domain:                                              │
│    a. resolve-workflow-skill-extension --domain X --type triage  │
│    b. resolve-domain-skills --domain X --profile quality         │
│ 3. Execute pipeline steps in order:                              │
│    ├── local_optimizations (auto-fix lint/format)                │
│    ├── conformance_review (check against skill rules)            │
│    ├── doc_sync (update diagrams if needed)                      │
│    ├── final_build (MANDATORY - mvn verify, npm test)            │
│    ├── commit_push (stage, commit, push)                         │
│    ├── pr_roundtrip (create PR, wait CI, check reviews)          │
│    └── sonar_roundtrip (wait analysis, fetch issues)             │
│ 4. Collect all findings from steps                               │
│ 5. If findings detected:                                         │
│    a. Create TASK-{SEQ}.toon per finding                         │
│    b. Return status=findings_detected                            │
│    c. Back to execute phase (next iteration)                     │
│ 6. If no findings:                                               │
│    a. Return status=success                                      │
│    b. Plan complete                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Knowledge Loading

Finalize skill loads triage extension and quality-level knowledge per domain:

```bash
# For each domain in config.toon.domains:

# 1. Get triage extension (for domain-specific suppression rules)
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill-extension --domain java --type triage
# → pm-dev-java:java-triage (or empty if none)

# 2. Get domain knowledge
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-domain-skills --domain java --profile quality
```

Result:
```toon
status: success
domain: java
profile: quality

defaults:
  pm-dev-java:java-core: Core Java patterns
  pm-dev-java:java-build: Build and verify commands

optionals:
  pm-dev-java:java-sonar: SonarQube integration
```

**Knowledge includes**:
- Build/verify commands per domain
- Quality gate thresholds
- PR creation workflow
- Finding categorization

**Knowledge excludes**:
- How to fix specific issues (delegates to execute)
- Root cause analysis (delegates to execute)

---

## Pipeline Steps

| Step | Purpose | Auto-fixable | Requirement |
|------|---------|--------------|-------------|
| `local_optimizations` | Lint, format, imports | Yes | REQ-1 |
| `conformance_review` | Review against skill rules | Partial | REQ-2 |
| `doc_sync` | Architecture diagrams, README verify | Partial | REQ-3 |
| `final_build` | Compilation + tests (MANDATORY) | No | REQ-4 |
| `commit_push` | Via ci-commit-agent | N/A | REQ-5 |
| `pr_roundtrip` | PR + CI wait + reviews | Partial | REQ-6 |
| `sonar_roundtrip` | Quality gate + issues | Partial | REQ-7 |

### REQ-1: Local Optimizations

Apply automated improvements before commit:
- Linting (ESLint, Checkstyle)
- Formatting (Prettier, google-java-format)
- JavaDoc fixes
- Import organization

### REQ-2: Conformance Review

Review against loaded skill rules:
- Architecture patterns
- Coding standards
- Naming conventions

### REQ-3: Documentation Sync

- Architecture diagrams: update if structure changed
- README: verify alignment, flag major mismatches

### REQ-4: Final Build (MANDATORY)

- Full compilation
- Unit tests
- Integration tests (if configured)
- **No commit without passing build**

### REQ-5: Commit and Push

- Stage changes
- Create commit (conventional format)
- Push to remote

### REQ-6: PR Roundtrip

1. Create/update PR
2. Wait for CI (learned timeout)
3. Check reviews
4. Process findings → auto-fix or create tasks

### REQ-7: Sonar Roundtrip

1. Wait for analysis
2. Fetch issues by severity
3. Triage each issue (fix or suppress)
4. Create tasks if needed

---

## Step Contract

```yaml
Step Interface:
  name: string
  enabled: boolean
  execute() → StepResult

StepResult:
  status: success | warning | error
  findings: Finding[]
  changes_made: boolean

Finding:
  type: string (e.g., "sonar_issue", "pr_comment", "build_error")
  severity: info | warning | error
  description: string
  file_path: string (optional)
  line: number (optional)
  auto_fixable: boolean
```

---

## Quality-Manager Pattern

Finalize knows HOW to:
- Run build/verify commands per domain
- Parse build output for errors/warnings
- Apply quality gates (coverage thresholds, etc.)
- Create PR with proper description
- Create finding-based fix tasks

Finalize does NOT decide:
- Is this warning a real bug?
- How should this be fixed?
- What's the root cause?

Instead, delegates to execute phase via fix tasks.

---

## Finding-to-Task Flow

```
1. Run pipeline steps
      │
      ├─ All SUCCESS → COMPLETE
      │
      └─ FINDINGS → Collect and categorize
            │
            ▼
2. For each finding:
      │
      │  finding.file → detect domain
      │  finding.type → determine task profile
      │
      ▼
3. Create TASK-{SEQ}.toon:
      domain: {detected_domain}
      profile: {determined_profile}
      origin: fix
      finding: {original_finding}
      │
      ▼
4. Return to EXECUTE phase
      → Execute loads full domain knowledge
      → Execute decides how to fix
      │
      ▼
5. Return to FINALIZE (next iteration)
```

---

## Scope Configuration

The `scope` setting determines which files to verify:

| Scope | Description | Source |
|-------|-------------|--------|
| `changed_only` | Only files modified during execute | `references.toon` |
| `all` | All project files | Full project scan |

**Precondition**: Execute phase must track file changes in `references.toon`:

```bash
# Execute phase MUST call after each file change:
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references add-file \
    --plan-id {plan_id} --file {file_path}
```

If `references.toon` is empty with `scope=changed_only`, finalize WARNS and falls back to `all`.

---

## Script API Calls

### Domain Resolution

```bash
# Get domains from config
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} --field domains
```

### Quality Knowledge Loading

```bash
# For each domain
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill-extension --domain java --type triage
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-domain-skills --domain java --profile quality
```

### Fix Task Creation

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
  --plan-id {plan_id} <<'EOF'
title: Fix Sonar blocker in UserService
domain: java
profile: implementation
skills:
  - pm-dev-java:java-core
origin: fix
priority: critical
finding:
  type: sonar_issue
  file: src/main/java/UserService.java
  line: 42
  rule: java:S1234
  severity: BLOCKER
  message: Null pointer dereference
steps:
  - src/main/java/UserService.java
verification:
  commands:
    - mvn verify
  criteria: Sonar issue no longer reported
EOF
```

---

## Fix Task Examples

### From Sonar Issues

```toon
id: TASK-003
title: Fix Sonar blocker - Null pointer dereference in UserService
domain: java
profile: implementation
skills:
  - pm-dev-java:java-core
origin: fix
priority: critical

finding:
  type: sonar_issue
  file: src/main/java/UserService.java
  line: 42
  rule: java:S1234
  severity: BLOCKER
  message: Null pointer dereference

steps[1]{number,file,status}:
1,src/main/java/UserService.java,pending

verification:
  commands:
    - mvn verify
  criteria: Sonar issue no longer reported
```

### From PR Review Comments

```toon
id: TASK-004
title: Address PR review - Add input validation in AuthController
domain: java
profile: implementation
skills:
  - pm-dev-java:java-core
origin: fix
priority: high

finding:
  type: pr_comment
  file: src/main/java/AuthController.java
  line: 55
  reviewer: reviewer
  message: This should validate input before processing

steps[1]{number,file,status}:
1,src/main/java/AuthController.java,pending

verification:
  commands:
    - mvn test
  criteria: PR review comment resolved
```

### From Build Errors

```toon
id: TASK-005
title: Fix compilation error in CacheConfig
domain: java
profile: implementation
skills:
  - pm-dev-java:java-core
origin: fix
priority: critical

finding:
  type: compilation_error
  file: src/main/java/CacheConfig.java
  line: 42
  message: cannot find symbol - class RedisTemplate

steps[1]{number,file,status}:
1,src/main/java/CacheConfig.java,pending

verification:
  commands:
    - mvn compile
  criteria: Compilation succeeds
```

---

## Return Structure

### Success (No Findings)

```toon
status: success
plan_id: {plan_id}

pipeline:
  steps_completed: 7
  steps_total: 7

verification:
  domains_verified: [java, javascript]
  all_passed: true

commit:
  sha: {commit_sha}
  message: {commit message}

pr:
  number: {pr_number}
  url: {pr_url}

next_action: complete
```

### Findings Detected

```toon
status: findings_detected
plan_id: {plan_id}
iteration: {n}

pipeline:
  steps_completed: 5
  failed_step: sonar_roundtrip

verification:
  domains_verified: [java, javascript]
  all_passed: false

findings[N]{type,file,severity}:
sonar_issue,src/main/java/CacheConfig.java,error
pr_comment,src/main/java/AuthController.java,warning

fix_tasks_created[N]{id,type,priority}:
TASK-003,sonar_issue,critical
TASK-004,pr_comment,high

next_action: execute_fixes
```

### Error

```toon
status: error
plan_id: {plan_id}
message: {error message}
next_action: requires_attention
```

---

## Work-Log Requirement

Every significant interaction MUST have a work-log entry:

| Event | Format |
|-------|--------|
| Step boundary | `[STEP] (pm-workflow:plan-finalize) Starting {step}` |
| Fix applied | `[FIX] (pm-workflow:plan-finalize) Applied: {desc}` |
| Finding detected | `[FINDING] (pm-workflow:plan-finalize) {type} in {file}` |
| Task created | `[TASK] (pm-workflow:plan-finalize) Created {task_id}` |
| Iteration | `[ITERATE] (pm-workflow:plan-finalize) Iteration {n}: {count} findings` |

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
    work {plan_id} INFO "[TAG] (pm-workflow:plan-finalize) {message}"
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Build fails | Create fix task with finding, return to execute |
| PR creation fails | Return error, requires attention |
| Sonar timeout | WARN, continue without Sonar results |
| Maximum iterations exceeded | Return error with summary |

---

## Integration

**Callers**:
- `plan-phase-agent` → after execute phase completes

**Dependencies**:
- `manage-config` → Read domains
- `resolve-workflow-skill-extension` → Load triage extension
- `resolve-domain-skills` → Load quality knowledge
- `manage-tasks` → Create fix tasks
- `manage-references` → Read changed files
- `manage-log` → Work log entries
- Git tools → Create commit and PR
- CI tools → Wait for checks, fetch reviews

**Returns to**:
- Execute phase (if findings detected)
- Complete (if verification passes)

---

## Related Documents

- [task-execution-skill-contract.md](task-execution-skill-contract.md) - Previous phase (execute)
- [task-contract.md](task-contract.md) - Task structure including fix tasks
- [extension-api.md](extension-api.md) - Triage extension mechanism
- [config-toon-format.md](config-toon-format.md) - Plan configuration
