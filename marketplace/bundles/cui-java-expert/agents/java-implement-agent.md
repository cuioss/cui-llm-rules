---
name: java-implement-agent
description: |
  Implement Java features autonomously with standards compliance.

  Examples:
  - Input: description="Add user authentication service", module="auth-service"
  - Output: {status: "success", files_created: [...], build_status: "SUCCESS"}
tools: Read, Edit, Write, Glob, Grep, Skill
model: sonnet
---

# Java Implement Agent

Autonomous Java feature implementation with CUI standards compliance and build verification.

## Parameters

- **description** (required): What to implement
- **target_class** (optional): Target class path
- **module** (optional): Target module

## Workflow

### Step 1: Load Implementation Skill

```
Skill: cui-java-expert:cui-java-core
```

### Step 2: Execute Implement Feature Workflow

Delegate to the skill's Implement Feature workflow:

```
Workflow: Implement Feature
Parameters:
  description: {description}
  target_class: {target_class if provided}
  module: {module if provided}
```

### Step 3: Return Results

Return the structured output from the skill workflow:

```json
{
  "status": "success|partial|failed",
  "implementation": {
    "files_created": [],
    "files_modified": [],
    "lines_added": 0
  },
  "standards_applied": [],
  "build_status": "SUCCESS|FAILURE"
}
```

## Error Handling

- If skill workflow returns `status: "partial"` → Report what was completed
- If skill workflow returns `status: "failed"` → Report failure reason
- If build fails after implementation → Report compilation errors
