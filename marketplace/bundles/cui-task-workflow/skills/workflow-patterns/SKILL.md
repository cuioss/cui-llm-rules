---
name: workflow-patterns
description: Orchestration patterns for agent coordination, handoffs, and context management
allowed-tools: Read, Glob
---

# Workflow Patterns Skill

Orchestration patterns for agent coordination, handoffs, and context management in multi-agent workflows.

## What This Skill Provides

- Handoff protocol for structured state transfer between agents
- Context compression strategies for long-running sessions
- Integration validation patterns for parallel execution
- Token budget guidelines for efficient context usage
- Wave-based processing for parallel task management

## When to Activate This Skill

Activate this skill when:
- Coordinating multiple agents or skills
- Managing handoffs between workflow stages
- Optimizing context usage in long sessions
- Validating integration points after parallel execution

---

## Handoff Protocol

Structured state transfer between agents/skills prevents information loss and maintains context boundaries.

### Handoff Levels

| Level | Use Case | Template |
|-------|----------|----------|
| Minimal | Simple task completion | `templates/handoff-minimal.json` |
| Standard | Multi-step workflows | `templates/handoff-standard.json` |
| Full | Complex orchestration | `templates/handoff-full.json` |

See `references/handoff-protocol.md` for detailed guidance.

---

## Context Compression

Mid-session context reduction to maintain quality in long-running sessions.

### Compression Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Context usage high | >70% | Consider compression |
| Quality degradation | Repeated errors | Force compression |
| Session handoff | Always | Compress before handoff |

See `references/context-compression.md` for detailed guidance.

---

## Integration Validation

Consistency validation across parallel skill executions.

### Validation Types

| Type | Purpose |
|------|---------|
| Interface | Type and contract alignment |
| Dependency | Version and import consistency |
| State | Shared state coherence |

See `references/integration-validation.md` for detailed guidance.

---

## Token Budget

Guidelines for efficient context allocation.

### Budget Allocation

| Component | Typical Budget |
|-----------|---------------|
| Architecture context | 20-30% |
| Task specification | 10-15% |
| Implementation space | 40-50% |
| Buffer | 10-20% |

See `references/token-budget-guidelines.md` for detailed guidance.

---

## Wave-Based Processing

Parallel task management with synchronization points.

### Wave Structure

| Phase | Purpose |
|-------|---------|
| Deployment | Launch parallel tasks |
| Execution | Independent work |
| Synthesis | Merge results |
| Cleanup | Reset for next wave |

See `references/wave-processing.md` for detailed guidance.

---

## Templates

| Template | Purpose |
|----------|---------|
| `handoff-minimal.json` | Simple task completion handoff |
| `handoff-standard.json` | Multi-step workflow handoff |
| `handoff-full.json` | Complex orchestration handoff |

---

## References

| Reference | Purpose |
|-----------|---------|
| `handoff-protocol.md` | Complete handoff protocol documentation |
| `context-compression.md` | Context compression strategies |
| `integration-validation.md` | Integration validation patterns |
| `token-budget-guidelines.md` | Token budget allocation |
| `wave-processing.md` | Wave-based processing patterns |

---

## Integration Points

### With claude-memory Skill
- Handoffs can reference memory files via `context_references`
- Context compression can persist to memory layer

### With cui-task-planning Skill
- Wave processing aligns with task decomposition
- Handoff protocol enables task state transfer
