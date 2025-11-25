---
name: claude-lessons-learned
description: Lessons learned storage and retrieval for commands and agents
allowed-tools: Read, Write, Edit
---

# Claude Lessons Learned Skill

Centralized storage for lessons learned from command and agent executions in `.claude/lessons-learned.json`.

## What This Skill Provides

- Single file storage for all lessons learned
- Query and retrieval of lessons for specific components
- Lesson categorization (bug, improvement, pattern, anti-pattern)
- Component-to-lesson mapping

## When to Activate This Skill

Activate this skill when:
- Recording lessons learned after command/agent execution
- Querying existing lessons for a component
- Preparing to apply lessons to component documentation

---

## File Location

```
.claude/lessons-learned.json
```

---

## File Format

Single JSON file with all lessons organized by component:

```json
{
  "version": 1,
  "lessons": [
    {
      "id": "2025-11-25-001",
      "component": {
        "type": "command|agent|skill",
        "name": "component-name",
        "bundle": "bundle-name"
      },
      "date": "2025-11-25",
      "category": "bug|improvement|pattern|anti-pattern",
      "summary": "Brief description",
      "detail": "Full explanation of the lesson",
      "applied": false
    }
  ]
}
```

### Lesson Categories

| Category | Description |
|----------|-------------|
| `bug` | Defect or error discovered during execution |
| `improvement` | Enhancement opportunity identified |
| `pattern` | Successful pattern worth documenting |
| `anti-pattern` | Pattern to avoid, caused problems |

---

## Workflow: Record Lesson

**Pattern**: Direct File Operation

Record a lesson learned after command/agent execution.

### Step 1: Read or Initialize File

If `.claude/lessons-learned.json` exists, read it. Otherwise create:

```json
{
  "version": 1,
  "lessons": []
}
```

### Step 2: Generate Lesson ID

Format: `{YYYY-MM-DD}-{NNN}`

Find highest sequence for today's date, increment or start at 001.

### Step 3: Add Lesson Entry

```json
{
  "id": "2025-11-25-001",
  "component": {
    "type": "command",
    "name": "maven-build-and-fix",
    "bundle": "cui-maven"
  },
  "date": "2025-11-25",
  "category": "bug",
  "summary": "Brief description",
  "detail": "Full explanation",
  "applied": false
}
```

### Step 4: Write File

Write JSON with proper formatting (2-space indent).

---

## Workflow: Query Lessons

**Pattern**: Direct File Operation

### Query All Lessons

```bash
cat .claude/lessons-learned.json
```

### Query for Specific Component

Read file, filter where `component.name` matches.

### Query Unapplied Lessons

Read file, filter where `"applied": false`.

### Query by Category

Read file, filter where `category` matches target.

---

## Workflow: Mark Lesson Applied

**Pattern**: Direct File Operation

After applying a lesson to component documentation:

1. Read `.claude/lessons-learned.json`
2. Find lesson by ID
3. Set `"applied": true`
4. Write file

---

## Integration Points

### With Commands/Agents

Commands and agents that specify "Any lessons learned about X" in their output requirements should:
1. Activate this skill
2. Record lessons via the Record Lesson workflow
3. Include lesson IDs in their output

### With plugin-apply-lessons-learned Command

The `/plugin-apply-lessons-learned` command uses this skill to:
1. Query unapplied lessons for components
2. Analyze component documentation
3. Apply lessons and mark them applied

---

## .gitignore

The lessons-learned file should be gitignored:

```
.claude/lessons-learned.json
```

Lessons are project-specific runtime knowledge.
