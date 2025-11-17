---
name: cui-marketplace-orchestration-patterns
description: Agent coordination and batch processing patterns
bundle: cui-plugin-development-tools
---

# CUI Marketplace Orchestration Patterns Skill

Standards for agent coordination, batch processing, token optimization, and result aggregation in marketplace diagnostic workflows.

## Workflow

### Step 1: Load Orchestration Standards

**Load standards based on orchestration context:**

1. **For batch processing workflows**:
   ```
   Read: standards/orchestration-patterns.md
   Read: standards/token-optimization-strategies.md
   ```

2. **For agent coordination**:
   ```
   Read: standards/agent-coordination-patterns.md
   ```

3. **For result aggregation**:
   ```
   Read: standards/result-aggregation-patterns.md
   ```

### Step 2: Apply Orchestration Patterns

**When to Execute**: During command/agent design that coordinates multiple sub-agents

**What to Apply**:

1. **Batch Processing**:
   - Determine optimal batch size
   - Implement batched agent invocation
   - Track batch progress and errors

2. **Token Optimization**:
   - Pre-load shared standards once
   - Use streamlined output formats
   - Minimize redundant reads

3. **Agent Coordination**:
   - Parallel vs sequential agent execution
   - Dependency management between agents
   - Error handling and retry logic

4. **Result Aggregation**:
   - Collect structured results from agents
   - Merge and deduplicate findings
   - Generate consolidated reports

### Step 3: Verify Orchestration Quality

**Quality Checks**:

- [x] Batch size optimized for token limits
- [x] Standards pre-loaded (not repeatedly read)
- [x] Agent results properly aggregated
- [x] Error handling covers all failure modes
- [x] Progress tracking visible to user

## Common Orchestration Patterns

### Pattern 1: Batched Agent Processing
```
Batch size: 5 components per batch
Total batches: ceil(total_count / 5)

For each batch:
  - Invoke 5 agents in parallel (single message, multiple Task calls)
  - Collect results
  - Report progress
```

### Pattern 2: Standards Pre-loading
```
Step 1: Load standards once
  Read: standards/orchestration-patterns.md
  Read: standards/token-optimization-strategies.md

Step 2: Pass to all agents
  Task: analyze-component
    Provide pre-loaded standards in prompt
```

### Pattern 3: Streamlined Output
```
Agent return format:
- If CLEAN: {"status": "CLEAN", "name": "..."}
- If issues: {"status": "ISSUES", "name": "...", "issues": [...]}

Reduces payload size by ~60%
```

## Quality Verification

All orchestration workflows must demonstrate:
- [x] Token efficiency (no redundant reads)
- [x] Proper batching (avoid parallel overload)
- [x] Clear progress tracking
- [x] Robust error handling
- [x] Structured result aggregation

## References

* Standards files:
  - standards/orchestration-patterns.md - Core batch processing patterns
  - standards/token-optimization-strategies.md - Token usage optimization
  - standards/agent-coordination-patterns.md - Multi-agent coordination
  - standards/result-aggregation-patterns.md - Result collection and reporting
