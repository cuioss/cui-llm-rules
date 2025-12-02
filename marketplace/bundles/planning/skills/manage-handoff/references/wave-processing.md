# Wave-Based Processing

Parallel task management with synchronization points for multi-agent orchestration.

## Wave Structure

A wave is a batch of tasks that can execute in parallel, followed by a synchronization point.

```
Wave 1: [Task A, Task B, Task C] -> Sync -> Merge
Wave 2: [Task D, Task E] -> Sync -> Merge
Wave 3: [Task F] -> Sync -> Complete
```

### Wave Phases

| Phase | Purpose | Activities |
|-------|---------|------------|
| Deployment | Launch tasks | Assign to agents, provide context |
| Execution | Independent work | Parallel implementation |
| Sync | Wait for completion | Collect results, detect issues |
| Synthesis | Merge results | Integrate, validate, prepare next wave |

---

## Wave Definition

### Defining Wave Boundaries

Tasks should be in the same wave when:
- No dependencies between them
- Can execute in isolation
- Don't modify the same files
- Combined context fits budget

Tasks should be in different waves when:
- Task B depends on Task A output
- Shared resource requires sequential access
- Combined context exceeds budget

### Wave Dependencies

```
Wave 1: Define interfaces
  - AuthService interface
  - UserService interface
  - DataService interface
  [No dependencies - can parallelize]

Wave 2: Implement services (depends on Wave 1)
  - AuthService implementation
  - UserService implementation
  - DataService implementation
  [Depend on interfaces - must wait for Wave 1]

Wave 3: Integration (depends on Wave 2)
  - Wire services together
  - Integration tests
  [Depend on implementations - must wait for Wave 2]
```

---

## Synchronization Points

### Wave Completion Sync

After all tasks in wave complete:

1. **Collect Results**: Gather all agent outputs
2. **Validate**: Check for conflicts and issues
3. **Merge**: Combine changes
4. **Prepare**: Set up next wave context

### Sync Checklist

- [ ] All tasks in wave reported completion
- [ ] No file conflicts between tasks
- [ ] Interface implementations match definitions
- [ ] No circular dependencies introduced
- [ ] Combined changes pass validation

### Handling Incomplete Tasks

If task doesn't complete:

| Scenario | Action |
|----------|--------|
| Blocked by external | Move to next wave with blocker noted |
| Failed with error | Retry or escalate to orchestrator |
| Partially complete | Split: completed portion merges, rest to next wave |

---

## Example Workflows

### Feature Implementation

```
Feature: User Authentication

Wave 1: Interfaces and Types
  Task 1.1: Define AuthService interface
  Task 1.2: Define User types
  Task 1.3: Define Token types
  [Parallel - no dependencies]

Wave 2: Backend Implementation
  Task 2.1: Implement AuthService (depends on 1.1, 1.3)
  Task 2.2: Implement UserRepository (depends on 1.2)
  [Parallel - different files]

Wave 3: Frontend Implementation
  Task 3.1: Login form (depends on 2.1 interface)
  Task 3.2: Auth context (depends on 2.1)
  Task 3.3: Protected routes (depends on 3.2)
  [3.1 and 3.2 parallel, 3.3 sequential]

Wave 4: Integration
  Task 4.1: Wire frontend to backend
  Task 4.2: Integration tests
  [Sequential within wave]
```

### Refactoring Workflow

```
Refactor: Extract shared utilities

Wave 1: Analysis
  Task 1.1: Identify duplicate code
  Task 1.2: Define utility interfaces
  [Parallel]

Wave 2: Extraction
  Task 2.1: Create utility module
  Task 2.2: Extract first pattern
  Task 2.3: Extract second pattern
  [2.1 first, then 2.2 and 2.3 parallel]

Wave 3: Migration
  Task 3.1: Update module A to use utilities
  Task 3.2: Update module B to use utilities
  Task 3.3: Update module C to use utilities
  [Parallel - different files]

Wave 4: Cleanup
  Task 4.1: Remove old implementations
  Task 4.2: Update imports
  Task 4.3: Run tests
  [Sequential]
```

---

## Batch Size Guidelines

### Context Budget Consideration

```
Max wave size = (Available context - Overhead) / Per-task budget

Example:
- Available: 100,000 tokens
- Orchestrator overhead: 15,000 tokens
- Per-task estimate: 17,000 tokens
- Max parallel tasks: (100,000 - 15,000) / 17,000 ≈ 5 tasks
```

### Practical Limits

| Factor | Recommendation |
|--------|----------------|
| Simple tasks | 5-8 per wave |
| Complex tasks | 2-4 per wave |
| File conflicts likely | 2-3 per wave |
| Independent modules | Up to 10 per wave |

### Diminishing Returns

Beyond optimal batch size:
- Coordination overhead increases
- Conflict probability increases
- Context per task decreases
- Quality may degrade

---

## Token Budget Integration

### Per-Wave Budget

```
Wave budget = Total available / Number of waves

Distribute within wave:
- Orchestration: 10%
- Task execution: 80%
- Synthesis: 10%
```

### Between-Wave Cleanup

After each wave:

1. **Remove**: Implementation details from completed tasks
2. **Keep**: Interfaces, decisions, constraints
3. **Add**: New interfaces from completed wave
4. **Reset**: Clear agent-specific context

### Budget Tracking

```
Wave 1: Used 35,000 / 100,000 (35%)
  - Orchestration: 8,000
  - Tasks (3): 22,000
  - Synthesis: 5,000

After cleanup: 15,000 retained (interfaces + decisions)

Wave 2: Starting with 85,000 available
```

---

## Wave Processing Examples

### Successful Wave Execution

```
WAVE 2 EXECUTION REPORT

Tasks:
  ✓ AuthService implementation - 12,000 tokens
  ✓ UserService implementation - 10,000 tokens
  ✓ DataService implementation - 11,000 tokens

Sync Results:
  ✓ No file conflicts
  ✓ All interfaces implemented correctly
  ✓ No circular dependencies

Merge:
  ✓ 3 files created
  ✓ 1 file updated (exports)
  ✓ Tests added

Context Cleanup:
  - Removed: Implementation details (33,000 tokens)
  - Retained: Interface references (3,000 tokens)

Ready for Wave 3
```

### Wave with Issues

```
WAVE 3 EXECUTION REPORT

Tasks:
  ✓ Login form - completed
  ✗ Auth context - blocked (missing type export)
  ✓ Protected routes - partial (depends on auth context)

Sync Results:
  ✗ Blocking issue detected

Resolution:
  1. Merge login form (complete)
  2. Fix type export (quick fix)
  3. Move auth context to Wave 3.5
  4. Move protected routes completion to Wave 3.5

Wave 3.5 created with:
  - Auth context (unblocked)
  - Protected routes (remaining work)
```

### Context Death Prevention

```
CONTEXT MONITOR - Wave 4

Pre-wave status:
  - Available: 100,000 tokens
  - Used: 72,000 tokens (72%)
  - Status: WARNING

Action: Force compression before wave

Compression:
  - Removed: Old debugging sessions (-15,000)
  - Summarized: Implementation details (-20,000)
  - Retained: Interfaces, decisions

Post-compression:
  - Used: 37,000 tokens (37%)
  - Status: HEALTHY

Proceeding with Wave 4
```
