---
name: missing-tool-test
description: Test agent using tool not declared
tools: [Read]
---

# Test Agent - Missing Tool

## Step 1: Read file

Use Read tool:
```
Read: path/to/file.md
```

## Step 2: Find files

Use Glob tool (NOT DECLARED):
```
Glob: pattern="*.md"
```
