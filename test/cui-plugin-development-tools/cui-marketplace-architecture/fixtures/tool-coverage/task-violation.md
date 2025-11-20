---
name: task-violation-test
description: Test agent with Task tool in frontmatter (violation)
tools: [Read, Task]
---

# Test Agent - Task Violation

## Step 1: Read file

Use Read tool:
```
Read: path/to/file.md
```

## Step 2: Delegate to sub-agent

Use Task tool:
```
Task:
  subagent_type: some-agent
  prompt: Do something
```

This violates Pattern 22 - agents should not have Task in frontmatter.
