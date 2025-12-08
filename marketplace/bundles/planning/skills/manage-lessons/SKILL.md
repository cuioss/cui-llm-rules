---
name: manage-lessons
description: Manage lessons learned with global scope
allowed-tools: Read, Glob, Bash
---

# Manage Lessons Skill

Manage lessons learned with global scope. Stores lessons as markdown files with key=value metadata headers.

## What This Skill Provides

- Create lessons from errors or discoveries
- Query lessons by component, category, or applied status
- Update lesson metadata
- Global scope (not plan-specific)

## When to Activate This Skill

Activate this skill when:
- Documenting a lesson from an error
- Querying applicable lessons for a component
- Marking lessons as applied

---

## Storage Location

Lessons are stored globally:

```
.plan/lessons-learned/
  2025-12-02-001.md
  2025-12-02-002.md
  ...
```

---

## File Format

Markdown with key=value metadata header:

```markdown
id=2025-12-02-001
component=maven-build
category=bug
applied=false
created=2025-12-02

# Build fails with missing dependency

When running `mvn clean install`, the build fails with a missing
dependency error for `jakarta.json-api`.

## Solution

Add the dependency explicitly to pom.xml:

```xml
<dependency>
    <groupId>jakarta.json</groupId>
    <artifactId>jakarta.json-api</artifactId>
</dependency>
```

## Impact

This affects all projects using jakarta.json without explicit dependency.
```

### Metadata Fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (date-sequence) |
| `component` | Component that lesson applies to |
| `category` | bug, improvement, anti-pattern |
| `applied` | Whether lesson has been applied (true/false) |
| `created` | Creation date |
| `bundle` | Optional bundle reference |

---

## Operations

Script: `planning:manage-lessons`

### add

Create a new lesson.

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component maven-build \
  --category bug \
  --title "Build fails with missing dependency" \
  --detail "When running mvn clean install..."
```

**Output** (TOON):
```toon
status: success
id: 2025-12-02-001
file: 2025-12-02-001.md
component: maven-build
category: bug
```

### update

Update lesson metadata.

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson update \
  --id 2025-12-02-001 \
  --applied true
```

**Output** (TOON):
```toon
status: success
id: 2025-12-02-001
field: applied
value: true
previous: false
```

### get

Get a single lesson.

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson get \
  --id 2025-12-02-001
```

**Output** (TOON):
```toon
status: success
id: 2025-12-02-001
component: maven-build
category: bug
applied: false
created: 2025-12-02
title: Build fails with missing dependency

content: |
  When running `mvn clean install`...
```

### list

List lessons with filtering.

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson list \
  [--component maven-build] \
  [--category bug] \
  [--applied false]
```

**Output** (TOON):
```toon
status: success
total: 5
filtered: 2

lessons[2]{id,component,category,applied,title}:
2025-12-02-001,maven-build,bug,false,Build fails with missing dependency
2025-12-02-002,plan-files,improvement,true,Add validation for plan_id format
```

### from-error

Create lesson from error context.

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson from-error \
  --context '{"component":"maven-build","error":"Missing dependency"}'
```

**Output** (TOON):
```toon
status: success
id: 2025-12-02-003
created_from: error_context
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-lessons` | All lesson operations via subcommands | `python3 .plan/execute-script.py planning:manage-lessons::{command} --help` |

---

## Categories

| Category | When to Use |
|----------|-------------|
| `bug` | Script is broken or produces wrong results |
| `improvement` | Script works but could be better |
| `anti-pattern` | Script was misused or documentation unclear |

---

## Integration Points

### With plan-execute

When errors occur during execution, create lessons to document the issue and solution.

### With plugin-doctor

Apply lessons to fix recurring issues in marketplace components.
