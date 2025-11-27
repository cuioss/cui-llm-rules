# Lessons Learned Format

Markdown file specification for `.claude/lessons-learned/*.md`.

## Purpose

Individual lesson files store:
- Runtime insights from command/agent executions
- Categorized learnings (bugs, improvements, patterns, anti-patterns)
- Application status for each lesson
- Rich content with code examples, links, and formatting

## Storage Location

```
.claude/lessons-learned/
  2025-11-27-001.md
  2025-11-27-002.md
  2025-11-26-001.md
  ...
```

Each lesson is stored as an individual Markdown file.

---

## File Structure

### Frontmatter (YAML)

Required metadata at top of file:

```yaml
---
id: 2025-11-27-001
component:
  type: command|agent|skill
  name: component-name
  bundle: bundle-name
date: 2025-11-27
category: bug|improvement|pattern|anti-pattern
applied: false
---
```

### Content (Markdown)

After frontmatter, standard Markdown content:

```markdown
# Brief Summary Title

## Detail

Full explanation with rich formatting:
- Code blocks
- Lists
- Links
- Tables

## Example

```bash
# Code examples
Bash: ls "${file_path}"
```

## Solution

Steps to address the issue.

## Related

- Links to related lessons
- Affected components
- Similar issues
```

---

## Required Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier: `{YYYY-MM-DD}-{NNN}` |
| component | object | Component this lesson applies to |
| date | string | ISO date when lesson was recorded |
| category | string | One of: bug, improvement, pattern, anti-pattern |
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

**Example File**: `.claude/lessons-learned/2025-11-27-001.md`

```markdown
---
id: 2025-11-27-001
component:
  type: command
  name: maven-build-and-fix
  bundle: cui-maven
date: 2025-11-27
category: bug
applied: false
---

# Command fails with spaces in paths

## Detail

The glob pattern expansion doesn't handle paths with spaces correctly.
When processing files in directories with spaces, Bash tool calls fail
with "No such file or directory" errors.

## Root Cause

Unquoted path variables being passed to Bash commands.

## Solution

Always quote path variables in Bash tool calls:

```bash
# Before (fails)
Bash: ls ${file_path}

# After (works)
Bash: ls "${file_path}"
```

## Affected Commands

- `/maven-build-and-fix` - All Bash calls
- `/java-refactor-code` - File iteration
```

### improvement

Enhancement opportunities identified during execution.

**Example File**: `.claude/lessons-learned/2025-11-27-002.md`

```markdown
---
id: 2025-11-27-002
component:
  type: agent
  name: maven-builder
  bundle: cui-maven
date: 2025-11-27
category: improvement
applied: false
---

# Add progress indicator for long operations

## Detail

When processing many files (>50), user has no visibility into progress.
Long operations appear frozen.

## Proposed Enhancement

Add periodic status updates:
- Every 50 files: "Processed 150/300 files (50%)"
- Estimated time remaining

## Implementation

```markdown
### Step 3: Process Files

For each file:
  1. Process file
  2. If count % 50 == 0: Print progress
```
```

### pattern

Successful patterns worth documenting.

**Example File**: `.claude/lessons-learned/2025-11-27-003.md`

```markdown
---
id: 2025-11-27-003
component:
  type: skill
  name: cui-maven-rules
  bundle: cui-maven
date: 2025-11-27
category: pattern
applied: true
---

# Validate inputs early

## Detail

Validating inputs (file existence, format, permissions) in the first
workflow step prevents confusing error messages later in execution.

This pattern has proven valuable across multiple skills:
- Clearer error messages for users
- Faster failure (fail-fast principle)
- Easier debugging

## Example

```markdown
### Step 1: Validate Inputs

Before processing:
1. Check file exists: `[ -f "$file_path" ]`
2. Check file readable: `[ -r "$file_path" ]`
3. Check file format: Parse and validate structure
4. Check dependencies available
```

## Benefits

| Approach | Error Location | Error Message | Debug Time |
|----------|----------------|---------------|------------|
| Late validation | Step 5 of 8 | Generic parser error | 10+ min |
| Early validation | Step 1 of 8 | "File not found: X" | <1 min |

## Applied To

- cui-maven-rules skill ✓
- cui-java-core skill ✓
- cui-documentation skill ✓
```

### anti-pattern

Patterns to avoid that caused problems.

**Example File**: `.claude/lessons-learned/2025-11-27-004.md`

```markdown
---
id: 2025-11-27-004
component:
  type: command
  name: java-refactor-code
  bundle: cui-java-expert
date: 2025-11-27
category: anti-pattern
applied: false
---

# Don't modify files during glob iteration

## Detail

Modifying files while iterating over a glob result causes:
- Missed files (if new files match pattern)
- Double-processing (if filenames change)
- Inconsistent results

## Problem Example

```bash
# Bad - modifies during iteration
for file in $(glob "*.java"); do
  # Refactor might rename file, causing issues
  refactor_file "$file"
done
```

## Solution

Collect file list first, then process:

```bash
# Good - collect then process
files=($(glob "*.java"))
for file in "${files[@]}"; do
  refactor_file "$file"
done
```

## Impact

- Discovered after 3 bug reports
- Caused incomplete refactoring in 2 projects
- Fix applied to all Java refactor commands
```

---

## ID Generation

Lesson IDs follow pattern: `{YYYY-MM-DD}-{NNN}`

- Date: ISO date of lesson recording (YYYY-MM-DD)
- Sequence: 3-digit sequence number starting at 001

**Examples**:
- `2025-11-27-001` (first lesson on Nov 27, 2025)
- `2025-11-27-002` (second lesson on Nov 27, 2025)
- `2025-11-26-001` (first lesson on Nov 26, 2025)

**Filename**: `{id}.md`
- `2025-11-27-001.md`
- `2025-11-27-002.md`

### Algorithm

When adding a new lesson:
1. Get current date: `2025-11-27`
2. List files in `.claude/lessons-learned/`
3. Find files matching `2025-11-27-*.md`
4. Find highest sequence number (e.g., `002`)
5. Increment: `003`
6. Create: `2025-11-27-003.md`

---

## Querying Patterns

Use the `query-lessons.py` script to filter lessons.

### Filter by Component

```bash
python3 scripts/query-lessons.py --component maven-build-and-fix
```

### Filter Unapplied

```bash
python3 scripts/query-lessons.py --applied false
```

### Filter by Category

```bash
python3 scripts/query-lessons.py --category bug
```

### Filter by Component Type

```bash
python3 scripts/query-lessons.py --type command
```

### Filter by Bundle

```bash
python3 scripts/query-lessons.py --bundle cui-maven
```

### Combine Filters

```bash
python3 scripts/query-lessons.py --component maven-build-and-fix --applied false
```

---

## Content Guidelines

### Title (H1)

Brief, actionable summary (50 chars or less):
- ✅ "Command fails with spaces in paths"
- ✅ "Add progress indicator"
- ❌ "There is a bug in the command that causes it to fail"

### Detail Section

Full explanation with:
- What happened
- Why it happened
- Impact

### Example/Solution Section

Code blocks showing:
- Before/After
- Problem/Solution
- Implementation

### Related Section

- Affected components
- Similar issues
- Cross-references

---

## Best Practices

1. **Be Specific**: Include concrete examples, not vague descriptions
2. **Show Code**: Use code blocks for technical details
3. **Link Context**: Reference related lessons and components
4. **Update Status**: Mark `applied: true` when integrated into docs
5. **Rich Format**: Use Markdown features (tables, lists, code blocks)

---

## Migration from JSON

If you have existing lessons in `.claude/lessons-learned.json`:

1. For each JSON lesson, create `{id}.md` file
2. Use frontmatter for metadata (id, component, date, category, applied)
3. Use Markdown for content (summary as H1, detail as text)
4. Add code examples in proper code blocks
5. Delete or archive old JSON file
