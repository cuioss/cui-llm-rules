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

## PREREQUISITES

Load the task-planning skill:
```
Skill: cui-task-workflow:cui-task-planning
```

## WORKFLOW

### Step 1: Execute Task (Skill Execute Workflow)

Use **cui-task-planning** Execute workflow:

1. Parse task for references and checklist items
2. Read all referenced files
3. Execute checklist items sequentially using Edit, Write tools
4. Mark items complete in plan if plan file provided

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

### Step 4: Return Result

```json
{
  "status": "SUCCESS|FAILURE",
  "task_executed": "task description",
  "files_modified": ["list of files"],
  "iterations": count,
  "issues_fixed": count
}
```

## CRITICAL RULES

- **Pattern 1**: Self-contained (implements + verifies + iterates)
- **Single Task**: Handle ONE task at a time
- **No Commit**: Caller handles commit (this returns result for aggregation)
- **Iteration Limit**: Max 5 iterations to prevent infinite loops
- **Structured Results**: Enable batch orchestration
- **Skill-Based**: Uses cui-task-planning skill for execution guidance

## ARCHITECTURE

```
/orchestrate-task (Pattern 1 - self-contained)
  ├─> Skill(cui-task-planning) Execute workflow [implements]
  ├─> SlashCommand(/maven-build-and-fix) [verifies]
  ├─> Analyze and iterate (max 5 iterations)
  └─> Return structured result
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

## RELATED

- **cui-task-planning** skill - Provides execution workflow guidance
- `/maven-build-and-fix` - Build verification command
- `/orchestrate-workflow` - Orchestrator that may delegate to this command
