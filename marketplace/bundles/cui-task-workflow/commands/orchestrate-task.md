---
name: orchestrate-task
description: Self-contained command that executes and verifies a single task
---

# Execute Task Command

Self-contained command that implements ONE task and verifies it.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=orchestrate-task update="[improvement]"` with:
1. Task execution patterns and error recovery strategies
2. Build verification efficiency and issue categorization
3. Parameter preparation and context handling
4. Iteration strategies and convergence patterns
5. Any lessons learned about single-task implementation workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **task**: Task description (what to implement)
- **context**: (Optional) Additional context or constraints

## WORKFLOW

### Step 1: Execute Task

```
Task:
  subagent_type: task-executor
  description: Execute task
  prompt: |
    Execute the following task: {task}

    Additional context: {context or "None"}

    Implement the required changes following CUI standards.
    Return implementation details to caller.
```

### Step 2: Verify Implementation

```
Task:
  subagent_type: maven-builder
  description: Verify task implementation
  prompt: |
    Execute Maven build with goals: clean verify
    Return structured results (outputMode: STRUCTURED).
```

### Step 3: Analyze Results and Iterate

**If build FAILURE or issues found:**
- Analyze issues from maven-builder STRUCTURED output
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

## ARCHITECTURE

```
/orchestrate-task (Pattern 1 - self-contained)
  ├─> Task(task-executor) [implements]
  ├─> Task(maven-builder) [verifies]
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

- `task-executor` - Focused agent that implements the task
- `maven-builder` - Focused agent that verifies build
- `/orchestrate-workflow` - Orchestrator that may delegate to this command
