---
name: plan-init
description: Init phase skill. Creates plan directory, request.md, config, and status. Complete initialization in a single agent call.
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Init Skill

**Role**: Complete init phase. Creates plan directory, request.md, detects plan type, and creates configuration. Single-agent initialization pattern.

**Key Pattern**: Complete initialization. Creates request.md, status.toon, config.toon, and references.toon. Does NOT create goals (that's the refine phase via decompose).

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
| manage-plan-document | `planning:manage-plan-documents` |
| manage-files | `planning:manage-files` |
| manage-references | `planning:manage-references` |
| manage-lessons | `planning:manage-lessons` |
| manage-work-log | `planning:manage-log` |
| manage-config | `planning:manage-config` |
| manage-lifecycle | `planning:manage-lifecycle` |

---

## Operation: create

**Input** (exactly ONE required):
- `description`: Free-form task description
- `lesson_id`: Lesson identifier to implement (e.g., `2025-12-02-001`)
- `issue`: GitHub issue URL or identifier

**Optional**:
- `plan_id`: Override auto-generated plan_id
- `plan_type`: Override auto-detection (bundle:skill notation, e.g., planning:plan-type-java)

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

Ensure exactly one input source is provided (description, lesson_id, or issue). If multiple or none provided, return error: "Provide exactly one of: description, lesson_id, issue"

### Step 2: Derive Plan ID

If `plan_id` not provided, derive from input:
- From description: first 3-5 meaningful words
- From lesson: lesson_id slug (e.g., `2025-12-02-001` → `lesson-2025-12-02-001`)
- From issue: issue number (e.g., `#123` → `issue-123`)
- Always: kebab-case, max 50 chars

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

### Step 6: Write request.md

Create the request document via manage-plan-documents:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request create \
  --plan-id {plan_id} \
  --title "{derived_title}" \
  --source {description|lesson|issue} \
  --body "{verbatim_content}" \
  --source-id "{lesson_id|issue_url}" \
  --context "{extracted_context}"
```

**Parameters:**
- `--title`: Derived title from input
- `--source`: One of `description`, `lesson`, or `issue`
- `--body`: The verbatim original input content
- `--source-id`: (optional) Lesson ID or issue URL if applicable
- `--context`: (optional) Extracted context from lesson or issue metadata

**Note**: The skill handles template rendering and timestamps automatically.

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

### Step 8: Detect Plan Type

Determine plan type from task analysis. Plan types use `bundle:skill` notation.

| Indicator | Plan Type |
|-----------|-----------|
| Java code, Maven/Gradle, .java files | `planning:plan-type-java` |
| JavaScript, npm, .js/.ts files | `planning:plan-type-javascript` |
| Plugin/skill/command development | `planning:plan-type-plugin` |
| Generic/simple task | `planning:plan-type-generic` |

**If plan_type parameter provided**: Use override value (must be bundle:skill notation).

**If uncertain**, ask:

```
AskUserQuestion:
  question: "What technology stack does this task primarily involve?"
  options:
    - label: "Java"
      description: "Java code with Maven or Gradle"
      value: "planning:plan-type-java"
    - label: "JavaScript"
      description: "JavaScript/TypeScript with npm"
      value: "planning:plan-type-javascript"
    - label: "Plugin Development"
      description: "Claude Code plugin components"
      value: "planning:plan-type-plugin"
    - label: "Generic"
      description: "Generic task, no specific technology"
      value: "planning:plan-type-generic"
```

**After detecting plan type**, log the decision with reasoning:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type decision \
  --summary "Selected {plan_type}" \
  --detail "{reasoning why this plan type was chosen}"
```

### Step 9: Create Status

Create status.toon with detected plan type and phases:

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle create \
  --plan-id {plan_id} \
  --title "{title_from_task_md}" \
  --plan-type {plan_type} \
  --phases init,refine,execute,finalize
```

**Note**: Phases depend on plan type. Use standard 4-phase for java/javascript/plugin, 3-phase (init,execute,finalize) for generic.

### Step 10: Create Configuration

Create config.toon with base settings:

```bash
python3 .plan/execute-script.py planning:manage-config:manage-config create \
  --plan-id {plan_id} \
  --plan-type {plan_type}
```

### Step 11: Call Plan-Type Configure

Delegate to plan-type skill for domain-specific configuration:

```
Skill: {plan_type}
operation: configure
plan_id: {plan_id}
```

This adds finalize configuration to config.toon:
- `create_pr`: Whether to create PR
- `verification_required`: Whether verification needed
- `verification_command`: Command for verification
- `branch_strategy`: feature or direct

### Step 12: Log Creation

Log the plan creation as an artifact:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type artifact \
  --summary "Created plan: {derived_title}" \
  --detail "Source: {source_type}, type: {plan_type}"
```

### Step 13: Transition Phase

The phase transitions from init → refine after configuration completes:

```bash
python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed init
```

### Step 14: Return Result

**Output**:

```toon
status: success
plan_id: {plan_id}
plan_type: {plan_type}
next_phase: refine

source:
  type: {description|lesson|issue}
  id: {source_id}

artifacts:
  request_md: request.md
  status: status.toon
  config: config.toon
  references: references.toon
```

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

This skill is called by `planning:plan-init-agent`. The agent completes the full init phase in a single call.

### Command Integration

- **/plan-manage action=init** - Orchestrates the init agent

### Scripts Used

| Script | Purpose |
|--------|---------|
| `planning:manage-plan-documents` | Write request.md (typed document) |
| `planning:manage-files` | Create/reference plan directory |
| `planning:manage-references` | Initialize references |
| `planning:manage-log` | Log creation |
| `planning:manage-lessons` | Read lesson (if source=lesson) |
| `planning:manage-config` | Create config.toon |
| `planning:manage-lifecycle` | Create status.toon, phase transitions |

### Related Skills

- **plan-refine** - Next phase after init completes
- **plan-type-*** - Called for domain-specific configuration

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/request.md` | request.md file format |

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to manage-* scripts
- [x] Preserves original task input verbatim
- [x] Supports all three source types
- [x] Creates config.toon with plan type
- [x] Creates status.toon with phases
- [x] Delegates to plan-type skill for domain config
- [x] Does NOT create goals (that's refine phase)
