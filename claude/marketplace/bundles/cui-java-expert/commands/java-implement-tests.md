---
name: java-implement-tests
description: Self-contained command for JUnit test implementation with verification and iteration
---

# Java Implement Tests Command

Self-contained command that implements JUnit tests using java-junit-implementer agent, verifies with maven-builder, and iterates until tests pass.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=java-implement-tests update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **task** (required): Test implementation task description
- **target-class** (optional): Class to test

## WORKFLOW

### Step 1: Parse Task

Extract test requirements and determine target class.

### Step 2: Implement Tests

```
Task:
  subagent_type: java-junit-implementer
  description: Implement tests for {task}
  prompt: |
    Implement JUnit tests for: {task}

    Target class: {target-class if specified}

    Return test implementation results.
```

### Step 3: Verify Tests

```
Task:
  subagent_type: maven-builder
  description: Run tests
  prompt: |
    Execute Maven build with goals: test

    Return structured results (outputMode: STRUCTURED).
```

### Step 4: Analyze Results

**If tests SUCCESS and no failures:**
- Return success result

**If tests FAILURE:**
- Analyze test failures
- If fixable: repeat Step 2-3 (max 3 iterations)
- If not fixable: return error with details

### Step 5: Return Result

```json
{
  "status": "SUCCESS|FAILURE",
  "iterations": count,
  "test_files_created": [list],
  "tests_passed": count,
  "tests_failed": count
}
```

## CRITICAL RULES

- **Self-Contained**: Handles ONE test task end-to-end
- **Layer 2 Pattern**: Can be invoked by users OR batch commands
- **Uses Task**: Can invoke agents (java-junit-implementer, maven-builder)
- **No SlashCommand**: Does NOT invoke other commands (single-item focus)
- **Iteration**: Max 3 test-fix cycles

## USAGE

```
/java-implement-tests task="Test UserService.getUserById method"
```

## ARCHITECTURE

Pattern 1: Self-Contained Command
```
/java-implement-tests
  ├─> Task(java-junit-implementer) [focused: writes tests only]
  ├─> Task(maven-builder) [runs tests]
  ├─> Analyze and iterate
  └─> Return result
```

## RELATED

- `java-junit-implementer` - Test implementation agent (Layer 3)
- `maven-builder` - Test execution agent (Layer 3)
- `/cui-java-task-manager` - Orchestrates multiple test tasks (Layer 1)
