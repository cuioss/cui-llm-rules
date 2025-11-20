---
name: unused-tool-test
description: Test agent declaring tool but not using it
tools: [Read, Write, Glob]
---

# Test Agent - Unused Tool

## Step 1: Read file

Use Read tool:
```
Read: path/to/file.md
```

## Step 2: Write result

Use Write tool:
```
Write: path/to/output.md
```

Note: Glob is declared but never used!
