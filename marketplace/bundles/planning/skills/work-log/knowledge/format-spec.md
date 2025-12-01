# Work-Log Format Specification

## Overview

Work-log files use TOON format for token efficiency and LLM-friendly parsing. Each plan directory can contain a `work-log.toon` file that records significant actions during execution.

## File Location

```
.plan/plans/{plan-name}/work-log.toon
```

## Schema

```toon
# Work Log
# Plan: {plan-name}
# Created: {ISO-8601 timestamp}

entries[N]{timestamp,phase,task,action,result}:
{ISO-8601},{phase},{task-id},"{action description}","{result/artifact}"
```

## Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | ISO-8601 | When action occurred | `2025-11-29T10:30:00Z` |
| `phase` | string | Plan phase | `init`, `refine`, `implement`, `verify`, `finalize` |
| `task` | string | Task identifier | `task-1`, `task-2` |
| `action` | string | What was done (result-oriented) | `Created validation logic` |
| `result` | string | Outcome or artifact | `src/Validator.java`, `Build passed` |

## Example Work-Log

```toon
# Work Log
# Plan: jwt-authentication
# Created: 2025-11-29T09:00:00Z

entries[5]{timestamp,phase,task,action,result}:
2025-11-29T09:15:00Z,init,task-1,Detected Maven project,pom.xml found
2025-11-29T09:30:00Z,refine,task-1,Analyzed existing auth patterns,Using SecurityContext pattern
2025-11-29T10:00:00Z,implement,task-1,Created JWT validator class,src/main/java/JwtValidator.java
2025-11-29T10:30:00Z,implement,task-1,Added unit tests,src/test/java/JwtValidatorTest.java
2025-11-29T11:00:00Z,verify,task-1,Ran build with tests,Build successful - 15 tests passed
```

## Entry Guidelines

### What to Log (0-5 entries per task)

**Log these**:
- Significant file creations/modifications
- Key decisions with rationale
- Build/test results
- Configuration changes
- External API interactions

**Do NOT log**:
- Every checklist item completion
- Minor edits or formatting
- Internal tool operations
- Redundant status updates

### Action Description Style

Use result-oriented language:
- "Created X" (not "Creating X")
- "Fixed Y in Z" (not "Working on Y")
- "Decided to use X because Y" (for decisions)

### Result Field Usage

| Scenario | Result Value |
|----------|--------------|
| File created | File path |
| Decision made | Brief rationale |
| Build run | Status + summary |
| Test run | Pass/fail + count |
| Error handled | Resolution summary |

## Token Efficiency

TOON format provides ~50% token reduction vs JSON for log entries:

**JSON equivalent** (~120 tokens):
```json
{
  "entries": [
    {"timestamp": "2025-11-29T10:00:00Z", "phase": "implement", "task": "task-1", "action": "Created JWT validator", "result": "JwtValidator.java"}
  ]
}
```

**TOON format** (~60 tokens):
```toon
entries[1]{timestamp,phase,task,action,result}:
2025-11-29T10:00:00Z,implement,task-1,Created JWT validator,JwtValidator.java
```

## Parsing

Scripts parse work-log.toon and output JSON for programmatic use. The TOON format is for storage/display efficiency; operations return JSON.
