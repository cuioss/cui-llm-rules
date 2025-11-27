---
name: java-fix-javadoc-agent
description: |
  Fix JavaDoc errors autonomously with content-preserving fixes.

  Examples:
  - Input: module="auth-service", max_iterations=3
  - Output: {status: "success", fixed: 8, errors_by_type: {unclosed_tag: 3}}
tools: Read, Edit, Glob, Grep, Skill
model: haiku
---

# Java Fix JavaDoc Agent

Autonomous JavaDoc error fixing with minimal, content-preserving fixes.

## Parameters

- **module** (optional): Module scope
- **max_iterations** (optional): Max fix attempts (default: 3)

## Workflow

### Step 1: Load JavaDoc Skill

```
Skill: cui-java-expert:cui-javadoc
```

### Step 2: Execute Fix JavaDoc Errors Workflow

Delegate to the skill's Fix JavaDoc Errors workflow:

```
Workflow: Fix JavaDoc Errors
Parameters:
  module: {module if provided}
  max_iterations: {max_iterations}
```

### Step 3: Return Results

Return the structured output from the skill workflow:

```json
{
  "status": "success|partial|failed",
  "iterations": 2,
  "fixed": 8,
  "remaining": 0,
  "files_modified": [],
  "errors_by_type": {
    "unclosed_tag": 3,
    "broken_link": 2,
    "missing_tag": 3
  },
  "build_status": "SUCCESS|FAILURE"
}
```

## Error Handling

- If error requires content changes → Apply minimal fix only
- If error is ambiguous → Use safest fix (remove problematic element)
- If error is in generated code → Skip and report
