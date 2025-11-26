# Token Budget Guidelines

Guidelines for efficient context allocation in agent orchestration.

## Typical Token Costs

### Content Types

| Content Type | Typical Tokens | Notes |
|--------------|----------------|-------|
| Interface definition | 50-100 | Per interface |
| Type definition | 20-50 | Per type |
| Function signature | 10-30 | Per function |
| Full file (small) | 200-500 | <100 lines |
| Full file (medium) | 500-2000 | 100-500 lines |
| Full file (large) | 2000-10000 | 500+ lines |
| Error message | 50-200 | With context |
| Stack trace | 200-1000 | Full trace |

### Context Components

| Component | Typical Tokens | Purpose |
|-----------|----------------|---------|
| System prompt | 500-2000 | Agent instructions |
| CLAUDE.md | 1000-5000 | Project context |
| Task specification | 200-500 | Current task |
| Conversation history | Variable | Session memory |

---

## Budget Allocation

### Recommended Distribution

| Component | Budget % | Rationale |
|-----------|----------|-----------|
| Architecture context | 20-30% | Decisions, constraints, interfaces |
| Task specification | 10-15% | Clear, focused task definition |
| Implementation space | 40-50% | Room for code generation |
| Buffer | 10-20% | Unexpected needs, errors |

### Example: 100K Token Context

| Component | Tokens | Content |
|-----------|--------|---------|
| System + CLAUDE.md | 10,000 | Base configuration |
| Architecture | 20,000 | Key interfaces, decisions |
| Task spec | 10,000 | Detailed requirements |
| Implementation | 45,000 | Code generation |
| Buffer | 15,000 | Errors, clarifications |

---

## Optimization Strategies

### Progressive Disclosure

Load context in stages:
1. **Initial**: Architecture + task overview (20%)
2. **On-demand**: Specific interfaces when needed
3. **Just-in-time**: File contents for modification

**Benefits**:
- Keeps architectural context prominent
- Avoids early context pollution
- Preserves implementation budget

### Context Windowing

For large files, load only relevant sections:

```
Instead of: Full 2000-line file (8000 tokens)
Load: Relevant 50 lines + interface (400 tokens)
Savings: 95%
```

### Interface-First Loading

Prioritize interfaces over implementations:

```
Load order:
1. Interface definitions (high value, low tokens)
2. Type definitions (high value, low tokens)
3. Implementation details (only when needed)
```

### Compression Checkpoints

Regular context maintenance:

| Usage | Action |
|-------|--------|
| <50% | Continue normally |
| 50-70% | Consider compression |
| 70-85% | Active compression |
| >85% | Force compression or handoff |

---

## Monitoring Thresholds

### Warning Thresholds

| Indicator | Threshold | Action |
|-----------|-----------|--------|
| Context usage | >70% | Plan compression |
| Repeated suggestions | 3+ times | Context pollution likely |
| Architecture references | <30% | Reload architecture |
| Error rate | Increasing | Check context quality |

### Critical Thresholds

| Indicator | Threshold | Action |
|-----------|-----------|--------|
| Context usage | >85% | Immediate compression |
| Implementation drift | Any | Reload architecture |
| Circular modifications | Detected | Reset or handoff |
| Quality degradation | Sustained | Force reset |

---

## Agent-Specific Budgets

### Orchestrator Agent

```
Total budget: ~10,000 tokens

Architecture: 40%   (4,000)
Task decomposition: 30%   (3,000)
Coordination state: 20%   (2,000)
Buffer: 10%   (1,000)

Key: NEVER load implementation details
```

### Specialist Agent

```
Total budget: ~15,000 tokens

Task context: 30%   (4,500)
Relevant interfaces: 20%   (3,000)
Implementation space: 40%   (6,000)
Buffer: 10%   (1,500)

Key: Only load context relevant to specialty
```

### Validator Agent

```
Total budget: ~10,000 tokens

Interface definitions: 40%   (4,000)
Contract specifications: 30%   (3,000)
Validation rules: 20%   (2,000)
Buffer: 10%   (1,000)

Key: Focus on contracts, not implementations
```

---

## Wave Processing Budget

### Per-Wave Budget

```
Wave budget calculation:
- Available context: 100,000 tokens
- Orchestrator overhead: 10,000 tokens
- Synthesis overhead: 5,000 tokens
- Per-task budget: (100,000 - 15,000) / task_count

Example with 5 tasks:
Per-task budget: 85,000 / 5 = 17,000 tokens
```

### Between-Wave Cleanup

After each wave:
1. Remove completed task details
2. Preserve only interfaces and decisions
3. Reset implementation context
4. Reload architecture if needed

---

## Budget Examples

### Single-Agent Task (Simple)

```
Task: Add validation to form
Budget: 50,000 tokens

Used:
- System prompt: 2,000
- CLAUDE.md: 3,000
- Form component: 500
- Validation schema: 200
- Implementation: 5,000
- Total: 10,700 (21%)

Status: Healthy, plenty of buffer
```

### Multi-Agent Feature (Complex)

```
Task: Implement authentication
Budget: 100,000 tokens

Orchestrator:
- Decomposition: 5,000
- Coordination: 3,000

Backend Specialist:
- API interfaces: 2,000
- Implementation: 12,000

Frontend Specialist:
- UI components: 3,000
- Implementation: 10,000

Integration:
- Validation: 5,000
- Fixes: 5,000

Total: 45,000 (45%)
Status: Efficient, good budget remaining
```

### Context Death Spiral (Anti-Pattern)

```
Task: Refactor codebase
Initial budget: 100,000 tokens

Hour 1:
- Loaded all files: 60,000
- Implementation attempts: 20,000
- Usage: 80%

Hour 2:
- More file loads: 10,000
- Debugging: 8,000
- Usage: 98%

Result: Architecture pushed out, drift begins
Solution: Should have used wave processing
```
