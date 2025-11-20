---
name: backup-files-test
description: Test agent creating backup files (violation)
tools: [Read, Write, Bash]
---

# Test Agent - Backup Files

## Step 1: Read file

Use Read tool:
```
Read: path/to/file.md
```

## Step 2: Create backup

Create backup file:
```
Bash: cp file.md file.md.bak
```

## Step 3: Write modified file

Use Write tool:
```
Write: path/to/file.md
```

This violates standards - agents should not create .bak or .backup files.
