# Lessons Learned Format

JSON schema specification for `.claude/lessons-learned/` files.

## Purpose

The lessons learned system stores:
- Runtime insights from command/agent executions
- Categorized learnings (bugs, improvements, patterns, anti-patterns)
- Application status for each lesson

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

## Schema

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

## Required Fields

### Component Object

| Field | Type | Description |
|-------|------|-------------|
| type | string | One of: command, agent, skill |
| name | string | Component name (matches filename) |
| bundle | string | Parent bundle name |

### Lesson Object

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier: `{date}-{sequence}` |
| date | string | ISO date when lesson was recorded |
| category | string | One of: bug, improvement, pattern, anti-pattern |
| summary | string | Brief one-line description |
| detail | string | Full explanation |
| context | string | What triggered this lesson |
| applied | boolean | Whether lesson has been applied to component |

---

## Categories

### bug

Defects or errors discovered during execution.

**Example:**
```json
{
  "id": "2025-11-25-001",
  "date": "2025-11-25",
  "category": "bug",
  "summary": "Command fails when directory contains spaces",
  "detail": "The glob pattern expansion doesn't handle paths with spaces. Need to quote paths in Bash calls.",
  "context": "User reported failure on '/Users/name/My Projects/'",
  "applied": false
}
```

### improvement

Enhancement opportunities identified during execution.

**Example:**
```json
{
  "id": "2025-11-25-002",
  "date": "2025-11-25",
  "category": "improvement",
  "summary": "Add progress indicator for long operations",
  "detail": "When processing many files, user has no visibility into progress. Could add periodic status updates.",
  "context": "Processing 500 files took 3 minutes with no feedback",
  "applied": false
}
```

### pattern

Successful patterns worth documenting.

**Example:**
```json
{
  "id": "2025-11-25-003",
  "date": "2025-11-25",
  "category": "pattern",
  "summary": "Validate inputs before processing",
  "detail": "Early validation of file existence and format prevents confusing errors later. Check all inputs in first workflow step.",
  "context": "Refactored validation to Step 1, reduced debugging time",
  "applied": false
}
```

### anti-pattern

Patterns to avoid that caused problems.

**Example:**
```json
{
  "id": "2025-11-25-004",
  "date": "2025-11-25",
  "category": "anti-pattern",
  "summary": "Don't modify files during iteration",
  "detail": "Modifying files while iterating over a glob result causes missed files or double-processing. Collect file list first, then process.",
  "context": "File edits during glob iteration caused inconsistent state",
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
1. Read existing lessons for the component
2. Find highest sequence number for today's date
3. Increment or start at 001

---

## File Naming

Files are named after the component with `.json` extension:

| Component | File Path |
|-----------|-----------|
| `/maven-build-and-fix` command | `.claude/lessons-learned/commands/maven-build-and-fix.json` |
| `maven-builder` agent | `.claude/lessons-learned/agents/maven-builder.json` |
| `cui-maven-rules` skill | `.claude/lessons-learned/skills/cui-maven-rules.json` |

---

## Example Complete File

```json
{
  "component": {
    "type": "command",
    "name": "maven-build-and-fix",
    "bundle": "cui-maven"
  },
  "lessons": [
    {
      "id": "2025-11-25-001",
      "date": "2025-11-25",
      "category": "bug",
      "summary": "Javadoc warnings not captured in some modules",
      "detail": "Multi-module builds with inherited javadoc config don't always emit warnings to stdout. Need to check target/reports as well.",
      "context": "User reported 'clean build' but javadoc had 15 warnings",
      "applied": false
    },
    {
      "id": "2025-11-24-001",
      "date": "2025-11-24",
      "category": "pattern",
      "summary": "Run verify phase for complete validation",
      "detail": "Using 'mvn verify' instead of 'mvn package' catches integration test failures and plugin validation issues.",
      "context": "Switched to verify phase after missing integration failures",
      "applied": true
    }
  ]
}
```

---

## Querying Patterns

### Find All Unapplied Lessons

```bash
# Glob all lesson files
.claude/lessons-learned/**/*.json

# Filter for "applied": false in each file
```

### Find Lessons by Category

Read all files and filter where `category` matches target.

### Find Lessons for Component Type

```bash
# All command lessons
.claude/lessons-learned/commands/*.json

# All agent lessons
.claude/lessons-learned/agents/*.json
```
