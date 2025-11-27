# Implement Phase Specification

**Input**: Plan from refine phase with detailed tasks, acceptance criteria, and references

**Output**: Implemented code, updated tests, marked tasks, and progress updates

**Use Cases**:
- Executing tasks from implementation plans
- Delegating to Java or JavaScript implementation agents
- Tracking checklist item completion
- Verifying acceptance criteria
- Updating plan progress

---

## Operations

The implement phase provides three core operations:

| Operation | Description | Output |
|-----------|-------------|--------|
| **execute-tasks** | Execute tasks sequentially from plan | Updated plan with completed tasks |
| **delegate** | Route task to appropriate language agent | Agent completion report |
| **track-progress** | Update task and phase progress | Progress status update |

---

## Prerequisites

Before implement phase can start:

1. **Refine phase completed** - All refine tasks marked `[x]`
2. **Implementation tasks exist** - Tasks in implement phase section
3. **References complete** - ADRs, interfaces, code references available
4. **Current phase is implement** - Transitioned from refine
5. **implementation-requirements.md exists** - Runtime artifact from refine

---

## Implement Phase Workflow

### Step 1: Read Context

**Load plan and references** (via `plan-files` skill):
```
plan-files.read-plan:
- All tasks in implement phase
- Current task (first pending or in_progress)
- Task dependencies

plan-files.read-config:
- Technology (java, javascript, mixed)
- Build system (maven, npm/npx)
- Commit strategy (fine-granular, phase-specific, complete)

plan-files.get-references:
- ADRs for architectural context
- Interfaces for API contracts
- Code references for existing patterns
- External docs for guidance
```

**Load implementation requirements**:
```
Read implementation-requirements.md:
- Component summary
- Task details with guidance
- Dependency graph
- Quality requirements
```

### Step 2: Identify Target Task

**Task Selection Logic**:
```
1. If task specified → Find that task by ID
2. Else if in_progress task exists → Resume that task
3. Else → Find first pending task respecting dependencies
```

**Dependency Check**:
```python
def can_start_task(task, all_tasks):
    for dep_id in task.dependencies:
        dep_task = find_task(dep_id, all_tasks)
        if dep_task.status != "completed":
            return False
    return True
```

**User Notification** (via `AskUserQuestion` if resuming):
```
## Resuming Implementation

Found in-progress task:

### Task {N}: {Task Name}

Progress: {completed}/{total} checklist items
Last item completed: {item description}

Options:
1. Continue from where we left off
2. Start this task from beginning
3. Skip to next task

Select (1-3):
```

### Step 3: Load Task References

**For each reference in the task**:
1. Read file using `Read` tool
2. Extract relevant sections
3. Synthesize understanding

**Reference Types**:

| Type | Source | Action |
|------|--------|--------|
| Issue | GitHub/local | Extract specific requirements |
| ADR | `.claude/adrs/` | Load architectural decisions |
| Interface | `doc/interfaces/` | Load API contracts |
| Code | Source files | Understand existing patterns |
| External | URLs | Fetch documentation |

**If unclear** (via `AskUserQuestion`):
```
## Clarification Needed

Task {N}: {Task Name}

I need clarification on:
- {Specific question 1}
- {Specific question 2}

Context:
{What I understand so far}

Please provide guidance:
```

### Step 4: Execute Checklist Items

**Sequential Execution**:
For each checklist item in task:

```
1. Determine item type:
   - implement → Write/Edit code
   - test → Write/Edit tests
   - document → Write/Edit docs
   - verify → Run build/tests
   - commit → Git operations

2. Execute using appropriate tools:
   - Implement: Edit, Write tools
   - Test: Edit, Write tools + Bash for test run
   - Document: Edit, Write tools
   - Verify: Delegate to build agent
   - Commit: Bash for git operations

3. Mark item done:
   - Use Edit tool: `[ ]` → `[x]`
   - Update plan.md via plan-files skill

4. Report progress:
   - Item: {description}
   - Status: completed
   - Files modified: {list}
```

**Delegation to Language Agents**:

For implementation items, delegate to appropriate agent based on technology:

| Technology | Agent | Skill |
|------------|-------|-------|
| Java | java-implement-agent | cui-java-expert |
| JavaScript | npm-builder | cui-frontend-expert |
| Mixed | Both agents | Sequential delegation |

**TOON Handoff to Language Agent**:
```toon
from: plan-implement-skill
to: java-implement-agent
handoff_id: impl-001

task:
  id: task-6
  name: Create JwtService
  goal: Implement JWT token generation service

context:
  technology: java
  build_system: maven
  acceptance_criteria[3]:
  - Service generates valid JWT tokens
  - Tokens include standard claims
  - Configurable expiration time

references:
  adr: ADR-015 (JWT Authentication Strategy)
  interface: IF-042 (Authentication Service)
  code[2]: TokenValidator.java, SecurityConfig.java

checklist_items[4]:
- Create JwtService class
- Implement generateToken method
- Add token configuration
- Write unit tests

next_action: Implement JwtService following ADR-015
```

**Agent Response**:
```toon
from: java-implement-agent
to: plan-implement-skill
handoff_id: impl-002

task:
  status: completed

implementation_results:
  files_created[2]: JwtService.java, JwtServiceTest.java
  files_modified[1]: pom.xml
  lines_added: 245
  test_coverage: 87%

build_status:
  compile: passed
  tests: passed (12 tests)
  coverage: 87%

next_action: Mark task complete and proceed
```

### Step 5: Verify Acceptance Criteria

**After all checklist items complete**:

1. Review each acceptance criterion
2. Verify criterion is met
3. Run relevant tests/checks
4. Mark criterion as verified

**Verification Process**:
```markdown
## Acceptance Criteria Verification

Task {N}: {Task Name}

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | {criterion} | ✅ Pass | {test/file reference} |
| 2 | {criterion} | ✅ Pass | {test/file reference} |
| 3 | {criterion} | ⚠️ Partial | {what's missing} |
```

**If criterion fails** (via `AskUserQuestion`):
```
## Acceptance Criterion Not Met

Task {N}: {Task Name}

Criterion: {criterion description}
Status: Failed

Reason:
{Detailed explanation of why criterion is not met}

Options:
1. Continue implementing to meet criterion
2. Modify criterion (update plan)
3. Mark as partial and proceed
4. Skip task (mark as blocked)

Select (1-4):
```

### Step 6: Update Progress

**After task completion** (via `plan-files` skill):

1. Mark task status `[x]` in plan.md
2. Update checklist items `[x]`
3. Update Phase Progress Table
4. Check if phase complete
5. Update references.md with created files

**TOON Handoff to plan-files**:
```toon
from: plan-implement-skill
to: plan-files-skill
handoff_id: progress-001

operation: update-progress
plan_directory: .claude/plans/jwt-auth/

update:
  task_id: task-6
  status: completed
  checklist_items[4]: 0, 1, 2, 3

files_created[2]:
- src/main/java/com/example/auth/JwtService.java
- src/test/java/com/example/auth/JwtServiceTest.java
```

**Response**:
```toon
from: plan-files-skill
to: plan-implement-skill
handoff_id: progress-002

plan_status:
  current_phase: implement
  current_task: task-7
  phase_complete: false

phase_status:
  phase: implement
  tasks_total: 5
  tasks_completed: 3
  completion_percentage: 60

next_action: Continue with task-7
```

### Step 7: Commit (Based on Strategy)

**Commit Strategy** (from config.md):

| Strategy | When to Commit |
|----------|----------------|
| fine-granular | After each task completion |
| phase-specific | After implement phase complete |
| complete | After all phases complete |

**Fine-Granular Commit**:
```bash
git add -A
git commit -m "feat: Task {N} - {Task Name}

Implemented {brief description}.

- {Change 1}
- {Change 2}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**User Confirmation** (if configured):
```
## Commit Ready

Task {N}: {Task Name} completed.

Files to commit:
- {file1} (new)
- {file2} (modified)
- {file3} (modified)

Commit message:
feat: Task {N} - {Task Name}

Options:
1. Commit now
2. Modify commit message
3. Skip commit (commit later)

Select (1-3):
```

---

## Implement Phase Tasks

Standard implement phase tasks are generated by refine phase:

```markdown
## Phase: implement (in_progress)

### Task {N}: {Task Name}

**Phase**: implement
**Goal**: {What success looks like}

**References**:
- Issue: {Specific section from issue}
- ADR: {ADR reference if applicable}
- Interface: {Interface reference if applicable}
- Code: {Related code files}

**Acceptance Criteria**:
- {Criterion 1}
- {Criterion 2}

**Checklist**:
- [ ] Read and understand all references
- [ ] If unclear, ask for clarification
- [ ] {Implementation step 1}
- [ ] {Implementation step 2}
- [ ] Implement unit tests (≥80% coverage)
- [ ] Run build to verify tests pass
- [ ] Commit changes (if fine-granular)
```

---

## Task Execution Patterns

### Pattern 1: Sequential Dependency Chain

```
Task 1: Create base interface (foundation)
    ↓
Task 2: Implement service class (depends on Task 1)
    ↓
Task 3: Add configuration (depends on Task 2)
    ↓
Task 4: Write integration tests (depends on Task 3)
```

**Execution**: Tasks 1→2→3→4 in strict order.

### Pattern 2: Parallel Independent Tasks

```
Task 1: Foundation
    ↓
    ├── Task 2: Feature A (independent)
    ├── Task 3: Feature B (independent)
    └── Task 4: Feature C (independent)
    ↓
Task 5: Integration (depends on 2, 3, 4)
```

**Execution**: Task 1, then Tasks 2, 3, 4 can be done in any order, then Task 5.

### Pattern 3: Iterative Refinement

```
Task 1: Initial implementation
    ↓
Task 2: Add error handling
    ↓
Task 3: Add edge cases
    ↓
Task 4: Performance optimization
```

**Execution**: Each task refines the previous work.

---

## Language Agent Delegation

### Java Implementation

**Agent**: `cui-java-expert:java-implement-agent`

**Delegation Pattern**:
```toon
from: plan-implement-skill
to: java-implement-agent
handoff_id: java-impl-001

task:
  name: {task name}
  goal: {task goal}

context:
  standards: cui-java-core
  testing: JUnit 5
  coverage_target: 80%
  build_verification: maven-builder agent

files:
  create[N]: {paths}
  modify[N]: {paths}

acceptance_criteria[N]: {criteria list}
```

**Standard Java Checklist**:
```markdown
- [ ] Follow CUI Java coding standards
- [ ] Add JavaDoc to public methods
- [ ] Implement unit tests (JUnit 5)
- [ ] Verify build via maven-builder agent
- [ ] Check coverage via java-coverage-agent
```

### JavaScript Implementation

**Agent**: `cui-frontend-expert:npm-builder`

**Delegation Pattern**:
```toon
from: plan-implement-skill
to: npm-builder-agent
handoff_id: js-impl-001

task:
  name: {task name}
  goal: {task goal}

context:
  standards: cui-javascript
  testing: Jest
  coverage_target: 80%
  build_verification: npm-builder agent

files:
  create[N]: {paths}
  modify[N]: {paths}

acceptance_criteria[N]: {criteria list}
```

**Standard JavaScript Checklist**:
```markdown
- [ ] Follow CUI JavaScript standards
- [ ] Add JSDoc to exported functions
- [ ] Implement unit tests (Jest)
- [ ] Verify build via npm-builder agent
- [ ] Check coverage via js-generate-coverage command
```

### Mixed Implementation

For tasks involving both Java and JavaScript:

1. Identify components by technology
2. Delegate Java parts to java-implement-agent
3. Delegate JavaScript parts to npm-builder
4. Coordinate integration points
5. Verify both builds pass

---

## Progress Tracking

### Task Status

| Status | Indicator | Description |
|--------|-----------|-------------|
| Pending | `[ ]` | Not started |
| In Progress | `[ ]` with some `[x]` items | Partially complete |
| Completed | `[x]` | All items done |
| Blocked | `[!]` | Cannot proceed |

### Progress Calculation

```python
def calculate_task_progress(task):
    total = len(task.checklist)
    done = sum(1 for item in task.checklist if item.done)
    return (done / total * 100) if total > 0 else 0

def calculate_phase_progress(phase):
    total = len(phase.tasks)
    done = sum(1 for task in phase.tasks if task.status == "completed")
    return (done / total * 100) if total > 0 else 0
```

### Progress Report Format

```markdown
## Implementation Progress

**Phase**: implement

| Task | Status | Checklist | Progress |
|------|--------|-----------|----------|
| Task 6: Create JwtService | ✅ | 4/4 | 100% |
| Task 7: Create TokenValidator | 🔄 | 2/5 | 40% |
| Task 8: RefreshTokenService | ⏳ | 0/5 | 0% |

**Overall**: 3/5 tasks (60%)
```

---

## Error Handling

### Build Failure

```
## Build Failed

Task {N}: {Task Name}

Build error:
{Error details}

Options:
1. Fix build error and retry
2. View full build log
3. Skip to next task (mark as blocked)
4. Abort implementation phase

Select (1-4):
```

### Test Failure

```
## Tests Failed

Task {N}: {Task Name}

Failed tests:
- {TestClass}::{testMethod}: {reason}

Options:
1. Fix failing tests
2. View test details
3. Mark task as partial
4. Skip to next task

Select (1-4):
```

### Coverage Below Threshold

```
## Coverage Below Target

Task {N}: {Task Name}

Coverage: 72% (target: 80%)

Uncovered areas:
- {Class}:{lines}
- {Method}:{lines}

Options:
1. Add tests for uncovered areas
2. Accept current coverage
3. Adjust coverage target

Select (1-3):
```

### Dependency Not Met

```
## Dependency Not Complete

Task {N}: {Task Name}

Depends on: Task {M} - {status}

Cannot start task until dependencies are complete.

Options:
1. Complete dependency first
2. Skip dependency check (proceed anyway)
3. Choose different task

Select (1-3):
```

---

## Phase Transition

### When All Tasks Complete

**Auto-Transition Check**:
```python
def check_phase_completion(phase):
    if all(task.status == "completed" for task in phase.tasks):
        return "ready_for_transition"
    return "in_progress"
```

**Transition Prompt** (via `AskUserQuestion`):
```
## Implementation Phase Complete

All implementation tasks are complete:

| Task | Status |
|------|--------|
| Task 6: Create JwtService | ✅ |
| Task 7: Create TokenValidator | ✅ |
| Task 8: RefreshTokenService | ✅ |
| Task 9: SecurityConfig | ✅ |
| Task 10: Integration Tests | ✅ |

Files created: 12
Files modified: 5
Total tests: 47
Coverage: 85%

Options:
1. Proceed to verify phase
2. Review implementation before proceeding
3. Add additional implementation tasks

Select (1-3):
```

**Update via plan-files skill**:
```toon
from: plan-implement-skill
to: plan-files-skill
handoff_id: transition-001

operation: update-progress
plan_directory: .claude/plans/jwt-auth/

phase_transition:
  from_phase: implement
  to_phase: verify
  status: completed
```

---

## Input/Output Summary

### Input

| Source | Data | Required |
|--------|------|----------|
| plan.md | Implementation tasks, dependencies | Yes |
| config.md | Technology, build system, commit strategy | Yes |
| references.md | ADRs, interfaces, code references | Yes |
| implementation-requirements.md | Task guidance, quality requirements | Yes |
| User | Clarifications, decisions | When needed |

### Output

| Artifact | Location | Content |
|----------|----------|---------|
| Source code | Project files | Implemented features |
| Tests | Test directories | Unit/integration tests |
| Updated plan.md | `.claude/plans/{task}/plan.md` | Completed tasks |
| Updated references.md | `.claude/plans/{task}/references.md` | Created files |
| Commits | Git | Changes committed per strategy |

---

## Integration Points

### With plan-refine

Implement phase receives:
- Detailed implementation tasks
- Acceptance criteria
- Task dependencies
- Technology assignments

### With plan-verify

Implement phase produces:
- Implemented code
- Tests
- Documentation updates
- Build artifacts

### With plan-files

During implementation:
- Read tasks via `read-plan`
- Read configuration via `read-config`
- Read references via `get-references`
- Update progress via `update-progress`
- Update references via `write-references`

### With Language Agents

During implementation:
- Delegate to `java-implement-agent` for Java tasks
- Delegate to `npm-builder` for JavaScript tasks
- Receive completion reports
- Track implementation results

---

## Comparison with Refine Phase

| Aspect | Refine Phase | Implement Phase |
|--------|--------------|-----------------|
| **Focus** | Analysis and planning | Execution and delivery |
| **Input** | Plan from init | Tasks from refine |
| **Output** | Implementation tasks | Working code |
| **User Interaction** | Task review | Progress updates |
| **Delegation** | ADR/interface skills | Language agents |
| **Artifacts** | implementation-requirements.md | Source code, tests |

---

## Related

- [Handoff Protocol](handoff.md) - TOON incoming/outgoing specifications
- [Plan Types](../plan-types.md) - Init phase router
- [Refine Phase](../plan-refine/refine.md) - Refine phase specification
- [Verify Phase](../plan-verify/verify.md) - Next phase specification
- [Finalize Phase](../plan-finalize/finalize.md) - Final phase specification
- [Templates & Workflow](../templates-workflow.md) - Phase workflow details
- [Persistence](../plan-files/persistence.md) - File format specifications
- [API Specification](../api.md) - Complete skill API
