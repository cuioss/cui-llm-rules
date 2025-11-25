---
name: claude-lessons-learned
description: Lessons learned storage and retrieval for commands and agents
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Claude Lessons Learned Skill

Centralized storage for lessons learned from command and agent executions in `.claude/lessons-learned/`.

## What This Skill Provides

- Structured storage for lessons learned by component
- Query and retrieval of lessons for specific components
- Lesson categorization (bug, improvement, pattern, anti-pattern)
- Component-to-lesson mapping

## When to Activate This Skill

Activate this skill when:
- Recording lessons learned after command/agent execution
- Querying existing lessons for a component
- Preparing to apply lessons to component documentation

---

## Directory Structure

```
.claude/lessons-learned/
├── commands/           # Lessons for commands
│   └── {command-name}.json
├── agents/             # Lessons for agents
│   └── {agent-name}.json
└── skills/             # Lessons for skills
    └── {skill-name}.json
```

---

## Lesson File Format

Each component has a JSON file with accumulated lessons:

```json
{
  "component": {
    "type": "command|agent|skill",
    "name": "component-name",
    "bundle": "bundle-name"
  },
  "lessons": [
    {
      "id": "2025-11-25-001",
      "date": "2025-11-25",
      "category": "bug|improvement|pattern|anti-pattern",
      "summary": "Brief description",
      "detail": "Full explanation of the lesson",
      "context": "What triggered this lesson",
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

### Step 1: Determine Component Path

```
component_type: command|agent|skill
component_name: the component name (e.g., "maven-build-and-fix")
file_path: .claude/lessons-learned/{component_type}s/{component_name}.json
```

### Step 2: Read Existing or Create New

If file exists, read and parse. Otherwise create structure:

```json
{
  "component": {
    "type": "{component_type}",
    "name": "{component_name}",
    "bundle": "{bundle-name}"
  },
  "lessons": []
}
```

### Step 3: Add Lesson Entry

Generate ID: `{date}-{sequence}` (e.g., `2025-11-25-001`)

Add to lessons array:
```json
{
  "id": "{generated-id}",
  "date": "{today}",
  "category": "{category}",
  "summary": "{brief summary}",
  "detail": "{full explanation}",
  "context": "{what triggered this}",
  "applied": false
}
```

### Step 4: Write File

Write JSON with proper formatting (2-space indent).

---

## Workflow: Query Lessons

**Pattern**: Direct File Operation

Query lessons for a component or across all components.

### Query Single Component

```bash
# Read component lessons file
cat .claude/lessons-learned/commands/{component-name}.json
```

### Query All Unapplied Lessons

Use Glob to find all lesson files, then filter for `"applied": false`.

### Query by Category

Read all files and filter by category field.

---

## Workflow: Mark Lesson Applied

**Pattern**: Direct File Operation

After applying a lesson to component documentation, mark it applied.

### Step 1: Read Lesson File

```bash
cat .claude/lessons-learned/{type}s/{component-name}.json
```

### Step 2: Update Applied Flag

Find lesson by ID and set `"applied": true`.

### Step 3: Write File

Write updated JSON.

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

The lessons-learned directory should be gitignored:

```
.claude/lessons-learned/
```

Lessons are project-specific runtime knowledge.
