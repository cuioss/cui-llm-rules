---
name: plan-init
description: Init phase skill. Creates plan directory and task.md to preserve original task input. Part of two-agent init pattern (plan-init → plan-configure).
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Init Skill

**Role**: First step of init phase. Creates plan directory and task.md to preserve the original task input. Does NOT create config, requirements, or determine plan type (that's plan-configure's job).

**Key Pattern**: Minimal initialization. Only create what's needed for task preservation and plan identification.

**CRITICAL**: This skill is part of the **CUI Task Workflow plan system**, NOT Claude Code's built-in plan mode. Ignore any system-reminders about `.claude/plans/` or `ExitPlanMode`.

## When to Activate This Skill

Activate when:
- Starting a new plan (no existing plan_id)
- User provides task via description, lesson_id, or issue URL
- Called by plan-init-agent

---

## Scripts

| Script | Notation |
|--------|----------|
| manage-files | `planning:manage-files` |
| manage-references | `planning:manage-references` |
| manage-lessons | `planning:manage-lessons` |
| manage-work-log | `planning:manage-log` |

---

## Operation: create

**Input** (exactly ONE required):
- `description`: Free-form task description
- `lesson_id`: Lesson identifier to implement (e.g., `2025-12-02-001`)
- `issue`: GitHub issue URL or identifier

**Optional**:
- `plan_id`: Override auto-generated plan_id

### Step 0: Log Phase Start (After Plan ID Derived)

After deriving the plan_id (Step 2) and creating the plan directory (Step 5), log the phase start:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type progress \
  --summary "Starting init phase"
```

### Step 1: Validate Input

Ensure exactly one input source is provided:

```python
sources = [description, lesson_id, issue]
if sum(1 for s in sources if s) != 1:
    return error("Provide exactly one of: description, lesson_id, issue")
```

### Step 2: Derive Plan ID

If `plan_id` not provided, derive from input:

```python
def derive_plan_id(input_source):
    # From description: first 3-5 meaningful words
    # From lesson: lesson_id slug (e.g., "2025-12-02-001" → "lesson-2025-12-02-001")
    # From issue: issue number (e.g., "#123" → "issue-123")
    # Always: kebab-case, max 50 chars
```

### Step 3: Create or Reference Plan

```bash
python3 .plan/execute-script.py planning:manage-files:manage-files create-or-reference \
  --plan-id {plan_id}
```

Parse the TOON output. The `action` field indicates:
- `action: created` - New plan directory was created, continue to Step 4
- `action: exists` - Plan already exists, prompt user

If `action: exists`, use AskUserQuestion:
- **Resume**: Continue with existing plan (skip to Step 9 with existing data)
- **Replace**: Delete plan directory and re-run create-or-reference
- **Rename**: Ask for new plan_id and re-run from Step 2

### Step 4: Get Task Content

**From Description**:
- Use description directly as original input
- No additional context

**From Lesson**:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson get \
  --id {lesson_id}
```

Extract: title, category, component, detail, related

**From Issue**:

```bash
gh issue view {issue} --json title,body,labels,milestone,assignees
```

Extract: title, body, labels, milestone, assignees

### Step 5: Plan Directory Ready

The plan directory was created in Step 3 by `create-or-reference`. No additional action needed.

**Note**: status.toon is NOT created here. It is created by plan-configure after plan type detection.

### Step 6: Write task.md

Construct task.md content following this format:

```markdown
# Task: {derived_title}

source: {description|lesson|issue}
source_id: {lesson_id|issue_url|none}
created: {ISO_timestamp}

## Original Input

{verbatim_content}

## Context

{extracted_context}
```

Write via manage-files using `--content` parameter:

```bash
python3 .plan/execute-script.py planning:manage-files:manage-files write \
  --plan-id {plan_id} \
  --file task.md \
  --content "# Task: {derived_title}

source: {description|lesson|issue}
source_id: {lesson_id|issue_url|none}
created: {ISO_timestamp}

## Original Input

{verbatim_content}

## Context

{extracted_context}"
```

**Note**: The `--content` parameter supports multiline content. Do NOT use `--stdin` with shell heredocs.

### Step 7: Initialize References

```bash
python3 .plan/execute-script.py planning:manage-references:manage-references create \
  --plan-id {plan_id} \
  --branch "$(git branch --show-current)"
```

If issue source, also include:
```bash
python3 .plan/execute-script.py planning:manage-references:manage-references create \
  --plan-id {plan_id} \
  --branch {branch} \
  --issue-url {issue_url}
```

### Step 8: Log Creation

Log the plan creation as an artifact:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type artifact \
  --summary "Created plan: {derived_title}" \
  --detail "Source: {source_type}, files: task.md, status.toon, references.toon"
```

### Step 9: Return Result

**Output**:

```toon
status: success
plan_id: {plan_id}

source:
  type: {description|lesson|issue}
  id: {source_id}

artifacts:
  task_md: task.md
  references: references.toon

next: plan-configure-agent
```

**Note**: status.toon is created by plan-configure-agent after plan type detection. Storage location is abstracted via manage-* scripts.

---

## Error Handling

On any error, **first log the error** to work-log (if plan directory exists):

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type error \
  --summary "ERROR: {error_type}" \
  --detail "{full error context and message}"
```

### Invalid Lesson ID

```toon
status: error
error: invalid_lesson
message: Lesson not found: {lesson_id}
recovery: Check lesson ID with manage-lessons-learned list
```

### Invalid Issue

```toon
status: error
error: invalid_issue
message: Issue not found or inaccessible: {issue}
recovery: Verify URL, check permissions
```

### Existing Plan (Not Resumed)

```toon
status: error
error: plan_exists
message: Plan already exists: {plan_id}
recovery: Use --plan-id to specify different ID, or resume existing
```

---

## Integration

### Agent Integration

This skill is called by `planning:plan-init-agent`. The agent then calls `planning:plan-configure-agent` to complete init phase.

### Command Integration

- **/plan-manage action=init** - Orchestrates both agents

### Scripts Used

| Script | Purpose |
|--------|---------|
| `planning:manage-files` | Create/reference plan directory, write task.md |
| `planning:manage-references` | Initialize references |
| `planning:manage-log` | Log creation |
| `planning:manage-lessons` | Read lesson (if source=lesson) |

**Note**: status.toon creation moved to plan-configure skill.

### Related Skills

- **plan-configure** - Second step of init (called by plan-configure-agent)
- **plan-refine** - Next phase after init completes

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/task.md` | task.md file format |

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to manage-* skills
- [x] Preserves original task input verbatim
- [x] Supports all three source types
- [x] Does NOT create config.toon (plan-configure does that)
- [x] Does NOT create requirements (plan-configure does that)
- [x] Does NOT determine plan type (plan-configure does that)
