# Work-Log Integration Guide

## Overview

This guide explains how phase skills should integrate with the work-log skill to record significant actions during plan execution.

## Integration Pattern

Phase skills delegate logging to the work-log skill:

```
Phase Skill → work-log skill (log-entry operation) → work-log.toon
```

## When to Log

### Log at These Points

| Phase | Log When |
|-------|----------|
| **init** | Environment detected, configuration confirmed |
| **refine** | Key design decisions made, analysis completed |
| **implement** | Files created/modified, tests written, build results |
| **verify** | Verification results, issues found/fixed |
| **finalize** | Commit created, PR submitted, plan completed |

### Entry Budget: 0-5 per Task

Most tasks should generate 1-3 log entries. Use judgment:

- **0 entries**: Trivial tasks with no significant actions
- **1-2 entries**: Standard tasks with clear outcomes
- **3-5 entries**: Complex tasks with multiple stages

## What to Log

### Required Elements

Every log entry should capture:

1. **Action**: What was done (result-oriented, past tense)
2. **Result**: What was produced or achieved

### Decision Logging

Decisions are high-value log entries. Include rationale:

```
Action: "Chose JWT over session auth"
Result: "Stateless requirement, microservices architecture"
```

### Examples by Phase

**init phase**:
```
Action: "Detected project environment"
Result: "Maven project with Java 17"
```

**refine phase**:
```
Action: "Decided to use strategy pattern for validation"
Result: "Extensible, testable, matches existing patterns"
```

**implement phase**:
```
Action: "Created authentication service"
Result: "src/main/java/AuthService.java"
```

**verify phase**:
```
Action: "Ran integration tests"
Result: "12/12 passed, coverage 85%"
```

**finalize phase**:
```
Action: "Created pull request"
Result: "PR #456: Add JWT authentication"
```

## Skill Invocation

### Log Entry

```
Skill: cui-task-workflow:work-log
operation: log-entry
plan_directory: {plan_directory}
phase: {current_phase}
task: {task_id}
action: "{action_description}"
result: "{result_or_artifact}"
```

### Read Log (for review)

```
Skill: cui-task-workflow:work-log
operation: read-log
plan_directory: {plan_directory}
[phase: {filter_phase}]
[task: {filter_task}]
```

## Script Integration

Phase skills can also call scripts directly:

```bash
# Log an entry
python3 {work-log-scripts}/write-entry.py \
  --plan-dir .plan/plans/my-task/ \
  --phase implement \
  --task task-1 \
  --action "Created validation service" \
  --result "src/ValidationService.java"

# Read entries
python3 {work-log-scripts}/read-log.py \
  --plan-dir .plan/plans/my-task/ \
  --phase implement
```

## Anti-Patterns

### Do NOT Log

- Every checklist item ("Checked item X" - use plan.md for this)
- Tool invocations ("Called Grep tool")
- Internal state changes ("Set variable to X")
- Redundant progress updates ("Still working on task")

### Avoid

- Vague actions ("Did some work on X")
- Missing results ("Created file" without path)
- Future tense ("Will create X")

## Implementation Checklist

For phase skill maintainers adding work-log support:

- [ ] Identify 1-3 key logging points per task type
- [ ] Use `log-entry` operation at those points
- [ ] Ensure action descriptions are result-oriented
- [ ] Include meaningful result values
- [ ] Log decisions with rationale
- [ ] Test that entries appear in work-log.toon
