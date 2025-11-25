# Lessons Learned Format

JSON schema specification for `.claude/lessons-learned.json`.

## Purpose

The lessons learned file stores:
- Runtime insights from command/agent executions
- Categorized learnings (bugs, improvements, patterns, anti-patterns)
- Application status for each lesson

## File Location

```
.claude/lessons-learned.json
```

## Schema

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

## Required Fields

### Root Object

| Field | Type | Description |
|-------|------|-------------|
| version | integer | Schema version (currently 1) |
| lessons | array | Array of lesson objects |

### Lesson Object

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier: `{date}-{sequence}` |
| component | object | Component this lesson applies to |
| date | string | ISO date when lesson was recorded |
| category | string | One of: bug, improvement, pattern, anti-pattern |
| summary | string | Brief one-line description |
| detail | string | Full explanation |
| applied | boolean | Whether lesson has been applied to component |

### Component Object

| Field | Type | Description |
|-------|------|-------------|
| type | string | One of: command, agent, skill |
| name | string | Component name |
| bundle | string | Parent bundle name |

---

## Categories

### bug

Defects or errors discovered during execution.

**Example:**
```json
{
  "id": "2025-11-25-001",
  "component": {"type": "command", "name": "maven-build-and-fix", "bundle": "cui-maven"},
  "date": "2025-11-25",
  "category": "bug",
  "summary": "Command fails when directory contains spaces",
  "detail": "The glob pattern expansion doesn't handle paths with spaces. Need to quote paths in Bash calls.",
  "applied": false
}
```

### improvement

Enhancement opportunities identified during execution.

**Example:**
```json
{
  "id": "2025-11-25-002",
  "component": {"type": "agent", "name": "maven-builder", "bundle": "cui-maven"},
  "date": "2025-11-25",
  "category": "improvement",
  "summary": "Add progress indicator for long operations",
  "detail": "When processing many files, user has no visibility into progress. Could add periodic status updates.",
  "applied": false
}
```

### pattern

Successful patterns worth documenting.

**Example:**
```json
{
  "id": "2025-11-25-003",
  "component": {"type": "skill", "name": "cui-maven-rules", "bundle": "cui-maven"},
  "date": "2025-11-25",
  "category": "pattern",
  "summary": "Validate inputs before processing",
  "detail": "Early validation of file existence and format prevents confusing errors later. Check all inputs in first workflow step.",
  "applied": false
}
```

### anti-pattern

Patterns to avoid that caused problems.

**Example:**
```json
{
  "id": "2025-11-25-004",
  "component": {"type": "command", "name": "java-refactor-code", "bundle": "cui-java-expert"},
  "date": "2025-11-25",
  "category": "anti-pattern",
  "summary": "Don't modify files during iteration",
  "detail": "Modifying files while iterating over a glob result causes missed files or double-processing. Collect file list first, then process.",
  "applied": false
}
```

---

## ID Generation

Lesson IDs follow pattern: `{YYYY-MM-DD}-{NNN}`

- Date: ISO date of lesson recording
- Sequence: 3-digit sequence number starting at 001

**Example:** `2025-11-25-001`, `2025-11-25-002`

When adding a lesson:
1. Read existing lessons
2. Find highest sequence number for today's date
3. Increment or start at 001

---

## Example Complete File

```json
{
  "version": 1,
  "lessons": [
    {
      "id": "2025-11-25-001",
      "component": {
        "type": "command",
        "name": "maven-build-and-fix",
        "bundle": "cui-maven"
      },
      "date": "2025-11-25",
      "category": "bug",
      "summary": "Javadoc warnings not captured in some modules",
      "detail": "Multi-module builds with inherited javadoc config don't always emit warnings to stdout. Need to check target/reports as well.",
      "applied": false
    },
    {
      "id": "2025-11-24-001",
      "component": {
        "type": "command",
        "name": "maven-build-and-fix",
        "bundle": "cui-maven"
      },
      "date": "2025-11-24",
      "category": "pattern",
      "summary": "Run verify phase for complete validation",
      "detail": "Using 'mvn verify' instead of 'mvn package' catches integration test failures and plugin validation issues.",
      "applied": true
    },
    {
      "id": "2025-11-23-001",
      "component": {
        "type": "agent",
        "name": "maven-builder",
        "bundle": "cui-maven"
      },
      "date": "2025-11-23",
      "category": "improvement",
      "summary": "Report warning count in summary",
      "detail": "Include count of warnings by category in final report for better visibility.",
      "applied": false
    }
  ]
}
```

---

## Querying Patterns

### Filter by Component

```javascript
lessons.filter(l => l.component.name === "maven-build-and-fix")
```

### Filter Unapplied

```javascript
lessons.filter(l => !l.applied)
```

### Filter by Category

```javascript
lessons.filter(l => l.category === "bug")
```

### Filter by Component Type

```javascript
lessons.filter(l => l.component.type === "command")
```
