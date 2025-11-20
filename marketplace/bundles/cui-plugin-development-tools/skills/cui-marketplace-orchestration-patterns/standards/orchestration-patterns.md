# Orchestration Patterns

Core patterns for orchestrating multiple agents in batch processing workflows.

## Batch Processing Pattern

### Optimal Batch Size

**Rule**: Process components in batches of **5** to balance token usage and progress visibility.

**Rationale**:
- Each batch launches 10 agents (5 diagnosis + 5 validation)
- Token usage per batch: ~60K-80K tokens
- Total capacity: 415K tokens
- Safety margin: 5x batches comfortably within limits

### Parallel Agent Invocation

**Pattern**: Single message with multiple Task calls

```markdown
Task: diagnose-command
  subagent_type: cui-plugin-development-tools:diagnose-command
  prompt: Analyze command X...

Task: diagnose-command
  subagent_type: cui-plugin-development-tools:diagnose-command
  prompt: Analyze command Y...

[Repeat for all 5 in batch]
```

**Benefits**:
- Maximizes parallelism
- Reduces wall-clock time
- Single message = atomic batch

### Progress Tracking

**Pattern**: Report after each batch completion

```
Batch 1/9 complete (5 commands analyzed)
Batch 2/9 complete (10 commands analyzed)
...
```

**User Experience**:
- Clear visibility into long-running workflows
- Ability to abort if needed
- Confidence that progress is being made

## Sequential vs Parallel Execution

### When to Use Parallel

- **Independent analyses**: Each component analyzed separately
- **No dependencies**: Results don't affect subsequent analyses
- **Token budget allows**: Batch size * agent cost < limits

### When to Use Sequential

- **Dependent operations**: Fix must complete before re-analysis
- **Iteration required**: Results inform next step
- **Resource constraints**: Large payloads require serialization

## Error Handling

### Batch-Level Errors

**Pattern**: Continue processing remaining batches

```
If batch N fails:
  - Log error for batch N
  - Continue with batch N+1
  - Report all errors in final summary
```

**Rationale**: Partial results better than complete failure

### Agent-Level Errors

**Pattern**: Track individual failures within batch

```
Batch 3 results:
  - Command A: ✅ CLEAN
  - Command B: ❌ Agent error
  - Command C: ✅ Issues found
  - Command D: ✅ CLEAN
  - Command E: ❌ Timeout
```

**Rationale**: Isolate failures, maximize successful analyses

## Iteration Patterns

### Fix-Verify Loop

```
Loop:
  1. Analyze → Identify issues
  2. Fix → Apply corrections
  3. Re-analyze → Verify fixes
  4. Repeat if issues remain (max iterations)
```

### Convergence Detection

**Stop conditions**:
- All issues resolved (success)
- Max iterations reached (partial success)
- No progress in last iteration (stuck)

## References

* Related standards:
  - token-optimization-strategies.md - Token usage patterns
  - agent-coordination-patterns.md - Multi-agent coordination
  - result-aggregation-patterns.md - Result collection
