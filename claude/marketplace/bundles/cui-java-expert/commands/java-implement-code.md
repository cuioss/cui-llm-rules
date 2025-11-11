---
name: java-implement-code
description: Self-contained command for Java code implementation with verification and iteration
---

# Java Implement Code Command

Self-contained command that implements Java code using java-code-implementer agent, verifies with maven-builder, and iterates until clean.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=java-implement-code update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **task** (required): Implementation task description
- **files** (optional): Specific files to modify

## WORKFLOW

### Step 1: Parse Task

Extract task requirements and determine scope.

### Step 2: Implement Code

```
Task:
  subagent_type: java-code-implementer
  description: Implement {task}
  prompt: |
    Implement: {task}

    Files: {files if specified}

    Return implementation results.
```

### Step 3: Verify Implementation

```
Task:
  subagent_type: maven-builder
  description: Verify implementation
  prompt: |
    Execute Maven build with goals: clean compile test

    Return structured results (outputMode: STRUCTURED).
```

### Step 4: Analyze Results

**If build SUCCESS and issues count == 0:**
- Return success result

**If build FAILURE or issues found:**
- Analyze issues
- If fixable: repeat Step 2-3 (max 3 iterations)
- If not fixable: return error with details

### Step 5: Return Result

```json
{
  "status": "SUCCESS|FAILURE",
  "iterations": count,
  "files_modified": [list],
  "issues_resolved": count,
  "issues_remaining": count
}
```

## CRITICAL RULES

- **Self-Contained**: Handles ONE implementation task end-to-end
- **Layer 2 Pattern**: Can be invoked by users OR batch commands
- **Uses Task**: Can invoke agents (java-code-implementer, maven-builder)
- **No SlashCommand**: Does NOT invoke other commands (single-item focus)
- **Iteration**: Max 3 build-fix cycles

## USAGE

```
/java-implement-code task="Add getUserById method to UserService"
```

## ARCHITECTURE

Pattern 1: Self-Contained Command
```
/java-implement-code
  ├─> Task(java-code-implementer) [focused: implements only]
  ├─> Task(maven-builder) [verifies]
  ├─> Analyze and iterate
  └─> Return result
```

## RELATED

- `java-code-implementer` - Implementation agent (Layer 3)
- `maven-builder` - Verification agent (Layer 3)
- `/cui-java-task-manager` - Orchestrates multiple implementations (Layer 1)
