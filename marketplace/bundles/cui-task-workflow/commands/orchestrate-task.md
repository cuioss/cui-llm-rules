---
name: orchestrate-task
description: Self-contained command that executes and verifies a single task
---

# Execute Task Command

Self-contained command that implements ONE task and verifies it.

## CONTINUOUS IMPROVEMENT RULE

If you discover issues or improvements during execution, record them:

1. **Activate skill**: `Skill: cui-utilities:claude-lessons-learned`
2. **Record lesson** with:
   - Component: `{type: "command", name: "orchestrate-task", bundle: "cui-task-workflow"}`
   - Category: bug | improvement | pattern | anti-pattern
   - Summary and detail of the finding

## PARAMETERS

- **task**: Task description (what to implement)
- **context**: (Optional) Additional context or constraints
- **handoff**: (Optional) Handoff structure from previous task (JSON)

## PREREQUISITES

Load required skills:
```
Skill: cui-task-workflow:cui-task-planning
Skill: cui-utilities:claude-memory
Skill: cui-task-workflow:workflow-patterns
```

## WORKFLOW

### Step 0: Process Handoff Input (If Provided)

If `handoff` parameter provided:

1. Parse handoff JSON structure
2. Extract context:
   - `artifacts.interfaces` - Interfaces to use
   - `artifacts.decisions` - Decisions to honor
   - `context.constraints` - Constraints to follow
   - `context_refs` - Memory references to load
3. Load any referenced memory files:
   ```bash
   python3 manage-memory.py load --category context --identifier "{ref}"
   ```

Expected handoff format (see `workflow-patterns/templates/handoff-standard.json`):
```json
{
  "handoff": {
    "from": "previous-task",
    "artifacts": {"interfaces": [], "decisions": []},
    "context": {"constraints": []},
    "memory_refs": []
  }
}
```

### Step 1: Execute Task (Skill Execute Workflow)

Use **cui-task-planning** Execute workflow:

1. Parse task for references and checklist items
2. Read all referenced files
3. Apply constraints from handoff (if provided)
4. Execute checklist items sequentially using Edit, Write tools
5. Mark items complete in plan if plan file provided

Implementation is done directly by this command following CUI standards.

### Step 2: Verify Implementation

```
SlashCommand: /cui-maven:maven-build-and-fix
```

Self-contained command that runs Maven build and fixes issues if found.

### Step 3: Analyze Results and Iterate

**If build FAILURE or issues found:**
- Analyze issues from maven-builder output
- Categorize: compilation_error, test_failure, etc.
- Return to Step 1 with refined task description
- Max 5 iterations

**If build SUCCESS:**
- Proceed to Step 4

### Step 4: Save State on Failure (For Retry)

If task failed after max iterations:

```bash
python3 manage-memory.py save \
  --category handoffs \
  --identifier "task-{task_id}-retry" \
  --content '{"task": "{task}", "status": "failed", "last_error": "...", "files_modified": [...]}'
```

This enables manual retry or continuation.

### Step 5: Return Structured Result

Return result with handoff for next task:

```json
{
  "status": "SUCCESS|FAILURE|BLOCKED",
  "task_executed": "task description",
  "files_modified": ["list of files"],
  "iterations": count,
  "issues_fixed": count,
  "decisions": ["decisions made during implementation"],
  "handoff": {
    "from": "this-task",
    "to": "next-task",
    "task": {"status": "completed|failed", "progress": "100%"},
    "artifacts": {
      "files": ["modified files"],
      "interfaces": ["any new interfaces"],
      "decisions": ["decisions made"]
    },
    "context": {
      "constraints": ["discovered constraints"],
      "notes": "implementation notes"
    },
    "next": {
      "action": "suggested next action",
      "blockers": ["any blockers for next task"]
    }
  }
}
```

Format follows `workflow-patterns/templates/handoff-standard.json`.

## CRITICAL RULES

- **Pattern 1**: Self-contained (implements + verifies + iterates)
- **Single Task**: Handle ONE task at a time
- **No Commit**: Caller handles commit (this returns result for aggregation)
- **Iteration Limit**: Max 5 iterations to prevent infinite loops
- **Structured Results**: Enable batch orchestration with handoff data
- **Skill-Based**: Uses cui-task-planning skill for execution guidance
- **Handoff In/Out**: Accept handoff input, return handoff output for chaining
- **Failure Persistence**: Save state on failure to enable retry

## ARCHITECTURE

```
/orchestrate-task (Pattern 1 - self-contained)
  ├─> Process handoff input (if provided)
  ├─> Skill(cui-task-planning) Execute workflow [implements]
  ├─> SlashCommand(/maven-build-and-fix) [verifies]
  ├─> Analyze and iterate (max 5 iterations)
  ├─> Save state on failure (for retry)
  └─> Return structured result with handoff
```

## USAGE EXAMPLES

**Single task execution:**
```
/orchestrate-task task="Add validation method to UserService"
```

**With context:**
```
/orchestrate-task task="Implement authentication filter" context="Use JWT tokens, integrate with existing SecurityContext"
```

**With handoff from previous task:**
```
/orchestrate-task task="Build login form" handoff='{"from": "backend-task", "artifacts": {"interfaces": ["AuthService"]}, "context": {"constraints": ["Must use JWT"]}}'
```

## RELATED

- **cui-task-planning** skill - Provides execution workflow guidance
- **cui-utilities:claude-memory** skill - State persistence for retry
- **cui-task-workflow:workflow-patterns** skill - Handoff templates
- `/maven-build-and-fix` - Build verification command
- `/orchestrate-workflow` - Orchestrator that may delegate to this command
