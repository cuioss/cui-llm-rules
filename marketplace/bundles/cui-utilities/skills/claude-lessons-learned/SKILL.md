---
name: claude-lessons-learned
description: Lessons learned storage and retrieval for commands and agents
allowed-tools: Read, Write, Edit, Glob, Bash
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

```
.claude/lessons-learned/
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
component.bundle=cui-maven
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

**Pattern**: Direct File Operation

Record a lesson learned after command/agent execution.

### Step 1: Create Directory (if needed)

If `.claude/lessons-learned/` doesn't exist, create it:

```bash
mkdir -p .claude/lessons-learned
```

### Step 2: Generate Lesson ID and Filename

Format: `{YYYY-MM-DD}-{NNN}.md`

1. List existing files in `.claude/lessons-learned/`
2. Find highest sequence number for today's date
3. Increment or start at 001
4. Example: `2025-11-27-001.md`

### Step 3: Create Markdown File

Write lesson to `.claude/lessons-learned/{id}.md`:

```markdown
id=2025-11-27-001
component.type=command
component.name=maven-build-and-fix
component.bundle=cui-maven
date=2025-11-27
category=bug
applied=false

# Brief Summary

## Detail

Full explanation of the lesson.

## Example

```bash
# Code examples if applicable
```
```

Use Write tool to create the file with proper metadata and content.

---

## Workflow: Query Lessons

**Pattern**: Command Chain Execution

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
python3 scripts/query-lessons.py --bundle cui-maven
```

### Combine Filters

```bash
python3 scripts/query-lessons.py --component maven-build-and-fix --applied false
```

**Output**: JSON array of matching lessons with metadata and content.

---

## Workflow: Mark Lesson Applied

**Pattern**: Direct File Operation

After applying a lesson to component documentation:

1. Find lesson file: `.claude/lessons-learned/{lesson-id}.md`
2. Edit metadata: Change `applied=false` to `applied=true`
3. Use Edit tool to update the metadata only

**Example**:
```bash
# For lesson 2025-11-27-001.md
Edit .claude/lessons-learned/2025-11-27-001.md
old_string: "applied=false"
new_string: "applied=true"
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

| Script | Purpose |
|--------|---------|
| `query-lessons.py` | Query and filter lessons by metadata criteria (uses only Python standard library) |
| `test-query-lessons.sh` | Test suite for query script |

---

## .gitignore

The lessons-learned directory should be gitignored:

```
.claude/lessons-learned/*.md
```

Lessons are project-specific runtime knowledge.
