---
name: manage-lessons-learned
description: Lessons learned storage and retrieval for commands and agents
allowed-tools: Read, Glob, Bash
---

# Claude Lessons Learned Skill

Centralized storage for lessons learned from command and agent executions using individual Markdown files.

## What This Skill Provides

- Individual Markdown file storage for each lesson
- Query and retrieval of lessons for specific components
- Lesson categorization (bug, improvement, pattern, anti-pattern)
- Component-to-lesson mapping
- Git-friendly format with clear diffs
- Rich content support (code blocks, links, formatting)

## When to Activate This Skill

Activate this skill when:
- Recording lessons learned after command/agent execution
- Querying existing lessons for a component
- Preparing to apply lessons to component documentation

---

## Storage Location

Lessons are stored in persistent storage (via `file-operations-base` skill) as individual Markdown files:

```
{lessons-storage}/
  2025-11-27-001.md
  2025-11-27-002.md
  2025-11-26-001.md
  ...
```

Each lesson is stored as an individual Markdown file with simple key=value metadata.

---

## File Format

Individual Markdown files with simple key=value metadata.

Metadata uses key=value pairs with dot notation for nested objects, separated from content by a blank line:

```markdown
id=2025-11-27-001
component.type=command
component.name=maven-build-and-fix
component.bundle=builder-maven
date=2025-11-27
category=bug
applied=false

# Brief Summary Title

## Detail

Full explanation of the lesson with rich formatting support.

## Example

```bash
# Code examples
Bash: ls "${file_path}"
```

## Related

- Affected: maven-build-and-fix command
- Similar issue in: java-refactor-code
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

**Pattern**: Script Automation

Record a lesson learned after command/agent execution using `write-lesson.py`.

### Usage

```bash
python3 scripts/write-lesson.py \
  --component-type {command|agent|skill} \
  --component-name NAME \
  --component-bundle BUNDLE \
  --category {bug|improvement|pattern|anti-pattern} \
  --title "Brief summary title" \
  --detail "Full explanation of the lesson" \
  [--example "Code example"] \
  [--related "Related components"] \
  [--lessons-dir DIR]
```

### Example

```bash
python3 scripts/write-lesson.py \
  --component-type command \
  --component-name maven-build-and-fix \
  --component-bundle builder-maven \
  --category bug \
  --title "Build fails on special characters in paths" \
  --detail "The build command fails when file paths contain special characters like spaces or quotes. Always quote path variables."
```

### Output

```json
{
  "success": true,
  "operation": "write-lesson",
  "file": "{lessons-storage}/2025-11-28-001.md",
  "id": "2025-11-28-001",
  "component": "builder-maven:maven-build-and-fix"
}
```

---

## Workflow: Query Lessons

**Pattern**: Script Automation

Use the `query-lessons.py` script to filter lessons by metadata criteria.

### Query All Lessons

```bash
python3 scripts/query-lessons.py --all
```

### Query for Specific Component

```bash
python3 scripts/query-lessons.py --component maven-build-and-fix
```

### Query Unapplied Lessons

```bash
python3 scripts/query-lessons.py --applied false
```

### Query by Category

```bash
python3 scripts/query-lessons.py --category bug
```

### Query by Bundle

```bash
python3 scripts/query-lessons.py --bundle builder-maven
```

### Combine Filters

```bash
python3 scripts/query-lessons.py --component maven-build-and-fix --applied false
```

**Output**: JSON array of matching lessons with metadata and content.

---

## Workflow: Update Lesson

**Pattern**: Script Automation

Update lesson metadata or content sections using `update-lesson.py`.

### Update Metadata

Use `--set KEY=VALUE` to update metadata fields:

```bash
python3 scripts/update-lesson.py \
  --lesson-id 2025-11-28-001 \
  --set applied=true
```

### Update Content Sections

Use `--set-detail`, `--set-example`, or `--set-related` to replace section content:

```bash
python3 scripts/update-lesson.py \
  --lesson-id 2025-11-28-001 \
  --set-detail "New detailed description of the issue"

python3 scripts/update-lesson.py \
  --lesson-id 2025-11-28-001 \
  --set-example "# New code example"

python3 scripts/update-lesson.py \
  --lesson-id 2025-11-28-001 \
  --set-related "component-a, component-b"
```

### Combine Metadata and Content Updates

```bash
python3 scripts/update-lesson.py \
  --lesson-id 2025-11-28-001 \
  --set applied=true \
  --set category=pattern \
  --set-detail "Updated description with more context"
```

### Output

```json
{
  "success": true,
  "operation": "update-lesson",
  "file": ".plan/lessons-learned/2025-11-28-001.md",
  "updated_fields": ["applied", "category"],
  "updated_sections": ["Detail"]
}
```

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

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `write-lesson.py` | Create new lesson file with metadata | `python3 scripts/write-lesson.py --help` |
| `update-lesson.py` | Update metadata or content sections | `python3 scripts/update-lesson.py --help` |
| `query-lessons.py` | Query and filter lessons by criteria | `python3 scripts/query-lessons.py --help` |
| `test-lessons-scripts.py` | Test suite for write/update scripts | `python3 scripts/test-lessons-scripts.py` |

---

## .gitignore

The lessons-learned directory should be gitignored (lessons storage is excluded by default in project `.gitignore`).

Lessons are project-specific runtime knowledge.
