# Agent Coordination Patterns

Patterns for coordinating multiple agents in diagnostic and fix workflows.

## Parallel Agent Invocation

### Single-Message Multiple-Task Pattern

**Rule**: Launch all independent agents in one message using multiple Task calls.

**Example**:
```markdown
I'll analyze batch 1 (5 commands) using parallel agent invocation:

Task: diagnose-command
  subagent_type: cui-plugin-development-tools:diagnose-command
  prompt: Analyze command-1...

Task: validate-references
  subagent_type: cui-plugin-development-tools:analyze-plugin-references
  prompt: Validate references in command-1...

Task: diagnose-command
  subagent_type: cui-plugin-development-tools:diagnose-command
  prompt: Analyze command-2...

Task: validate-references
  subagent_type: cui-plugin-development-tools:analyze-plugin-references
  prompt: Validate references in command-2...

[Repeat for commands 3-5]
```

**Benefits**:
- Maximum parallelism (10 agents run concurrently)
- Single atomic operation (all succeed or all fail together)
- No intermediate messages needed

### Anti-Pattern: Sequential Single-Task Messages

**DON'T DO**:
```markdown
Task: diagnose-command for command-1

[Wait for result]

Task: diagnose-command for command-2

[Wait for result]
...
```

**Why Not**:
- 10x slower (sequential vs parallel)
- 10x more messages (clutter)
- No batching benefits

## Dependency Management

### Independent Operations

**Pattern**: Parallel execution when no dependencies exist

```
Operation A (analyze command-1) ← No dependency
Operation B (analyze command-2) ← No dependency
Operation C (analyze command-3) ← No dependency

→ Execute A, B, C in parallel (single message)
```

### Dependent Operations

**Pattern**: Sequential execution when operations depend on results

```
Operation 1: Analyze issues
Operation 2: Fix issues (depends on analysis results)
Operation 3: Re-analyze (depends on fix completion)

→ Execute sequentially:
  Message 1: Task(analyze)
  [Wait for results]
  Message 2: SlashCommand(fix)
  [Wait for completion]
  Message 3: Task(re-analyze)
```

### Mixed Dependencies

**Pattern**: Batch independent operations, serialize dependent chains

```
Batch 1: Analyze commands 1-5 (parallel)
[Wait for batch completion]
Fix issues in commands 1-5 (parallel - each fix is independent)
[Wait for fixes]
Batch 2: Re-analyze commands 1-5 (parallel)
```

## Agent Type Selection

### Diagnosis Agents (Layer 3)

**Characteristics**:
- Read-only operations
- Return structured analysis
- No file modifications
- Fast execution

**Use for**:
- Initial analysis
- Validation checks
- Report generation

### Fix Agents (Layer 3)

**Characteristics**:
- Focused single-aspect fixes
- File modifications
- Structured success/failure results
- No further delegation

**Use for**:
- Automated safe fixes
- Content preservation edits
- Standards enforcement

### Implementation Agents (Layer 2)

**Characteristics**:
- Can delegate to Layer 3 agents
- Orchestrates complex workflows
- Iterates until success
- Comprehensive task completion

**Use for**:
- Multi-step implementations
- Fix verification loops
- Complex refactoring

## Error Handling Coordination

### Agent Failure Strategies

**Strategy 1: Continue on Error (Batch Processing)**
```
For batch of 5 agents:
  Agent 1: ✅ Success
  Agent 2: ❌ Timeout → Log error, continue
  Agent 3: ✅ Success
  Agent 4: ❌ Analysis failure → Log error, continue
  Agent 5: ✅ Success

Result: 3/5 successful, 2/5 failed
Action: Report partial success, list failures
```

**Strategy 2: Stop on Error (Critical Operations)**
```
Step 1: Build project
  If fails → STOP, report error
Step 2: Run tests (only if build succeeded)
Step 3: Deploy (only if tests passed)
```

**Strategy 3: Retry on Error (Transient Failures)**
```
Attempt 1: Agent timeout
  → Retry with increased timeout
Attempt 2: Success
```

### Error Reporting Pattern

**Structured Error Collection**:
```json
{
  "batch_number": 3,
  "total_agents": 5,
  "successful": 3,
  "failed": 2,
  "failures": [
    {
      "agent": "diagnose-command",
      "component": "foo-command",
      "error": "Timeout after 120s",
      "retry_possible": true
    },
    {
      "agent": "analyze-references",
      "component": "bar-command",
      "error": "Invalid JSON in response",
      "retry_possible": false
    }
  ]
}
```

## Progress Reporting

### Batch-Level Progress

**Pattern**: Report after each batch completion

```
Processing batch 1/9 (commands 1-5)...
✅ Batch 1/9 complete
  - Analyzed: 5 commands
  - Clean: 3
  - Issues: 2

Processing batch 2/9 (commands 6-10)...
✅ Batch 2/9 complete
  - Analyzed: 5 commands
  - Clean: 4
  - Issues: 1

Overall progress: 10/45 commands analyzed (22%)
```

### Operation-Level Progress

**Pattern**: Report major workflow transitions

```
Phase 1: Analysis
  ✅ Loaded standards
  ✅ Discovered 45 commands
  ✅ Analyzed all commands (9 batches)

Phase 2: Fix Planning
  ✅ Categorized issues
  ✅ Created remediation plan

Phase 3: Execution
  ⏳ Fixing CONTINUOUS IMPROVEMENT RULE issues (5 files)
  ⏳ Investigating reference issues (3 files)
  ⏳ Reducing bloat (8 files)
```

## Coordination Anti-Patterns

### Anti-Pattern 1: Agent Nesting

**WRONG**:
```
Command → Agent A → Agent B (nested delegation)
```

**Reason**: Agents cannot invoke other agents (architecture rule violation)

**FIX**: Commands orchestrate agents
```
Command → Agent A (parallel)
Command → Agent B (parallel)
```

### Anti-Pattern 2: Excessive Agent Granularity

**WRONG**:
```
Agent: read-file
Agent: parse-json
Agent: validate-schema
Agent: format-output

Command invokes 4 micro-agents
```

**Reason**: Overhead exceeds benefits, agents should be substantial units of work

**FIX**: Single focused agent
```
Agent: validate-manifest (does all steps internally)
```

### Anti-Pattern 3: Synchronous Waiting

**WRONG**:
```
Task: agent-1
[Wait, then in next message...]
Task: agent-2
[Wait, then in next message...]
```

**Reason**: Sequential execution wastes time when operations are independent

**FIX**: Parallel invocation
```
Task: agent-1
Task: agent-2
[Both in same message]
```

## References

* Related standards:
  - orchestration-patterns.md - Batch processing patterns
  - token-optimization-strategies.md - Token usage optimization
  - result-aggregation-patterns.md - Result collection
* Architecture rules: See cui-marketplace-architecture skill
