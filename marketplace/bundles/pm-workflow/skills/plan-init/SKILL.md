---
name: plan-init
description: Init phase skill. Creates plan directory, request.md, config, and status. Complete initialization in a single agent call.
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Init Skill

**Role**: Complete init phase. Creates plan directory, request.md, detects domain, and creates configuration. Single-agent initialization pattern.

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
| manage-plan-document | `pm-workflow:manage-plan-documents` |
| manage-files | `pm-workflow:manage-files` |
| manage-references | `pm-workflow:manage-references` |
| manage-lessons | `plan-marshall:lessons-learned` |
| manage-log | `plan-marshall:logging:manage-log` |
| manage-config | `pm-workflow:manage-config` |
| manage-lifecycle | `pm-workflow:manage-lifecycle` |

---

## Operation: create

**Input** (exactly ONE required):
- `description`: Free-form task description
- `lesson_id`: Lesson identifier to implement (e.g., `2025-12-02-001`)
- `issue`: GitHub issue URL or identifier

**Optional**:
- `plan_id`: Override auto-generated plan_id
- `domain`: Override auto-detection (java, javascript, plugin, generic)

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
python3 .plan/execute-script.py pm-workflow:manage-files:manage-files create-or-reference \
  --plan-id {plan_id}
```

Parse the TOON output. The `action` field indicates:
- `action: created` - New plan directory was created, log phase start and continue to Step 4
- `action: exists` - Plan already exists, prompt user

**On successful creation**, log the phase start (directory now exists):

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "Starting init phase"
```

If `action: exists`, use AskUserQuestion:
- **Resume**: Continue with existing plan (skip to Step 9 with existing data)
- **Replace**: Delete existing plan and create new (see below)
- **Rename**: Ask for new plan_id and re-run from Step 2

**Replace Flow** (see `standards/plan-overwrite.md` for details):

1. Delete the existing plan:
```bash
python3 .plan/execute-script.py pm-workflow:manage-files:manage-files delete-plan \
  --plan-id {plan_id}
```

2. Re-run create-or-reference (should now return `action: created`):
```bash
python3 .plan/execute-script.py pm-workflow:manage-files:manage-files create-or-reference \
  --plan-id {plan_id}
```

3. Continue with Step 4 (Get Task Content)

### Step 4: Get Task Content

**From Description**:
- Use description directly as original input
- No additional context

**From Lesson**:

```bash
python3 .plan/execute-script.py plan-marshall:lessons-learned:manage-lesson get \
  --id {lesson_id}
```

Extract: title, category, component, detail, related

**From Issue**:

```bash
gh issue view {issue} --json title,body,labels,milestone,assignees
```

Extract: title, body, labels, milestone, assignees

### Step 5: Write request.md

Create the request document via manage-plan-documents:

```bash
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-documents \
  request create \
  --plan-id {plan_id} \
  --title "{derived_title}" \
  --source {description|lesson|issue} \
  --body "{verbatim_content}" \
  [--source-id "{lesson_id|issue_url}"] \
  [--context "{extracted_context}"]
```

**Parameters:**
- `--title`: Derived title from input
- `--source`: One of `description`, `lesson`, or `issue`
- `--body`: The verbatim original input content
- `--source-id`: (only for traceable sources) External reference identifier:
  - For `lesson`: The lesson ID (e.g., `2025-12-02-001`)
  - For `issue`: The issue URL
  - For `description`: Omit (no external reference)
- `--context`: (optional) Extracted context from lesson or issue metadata

**Note**: The skill handles template rendering and timestamps automatically.

### Step 6: Initialize References

**IMPORTANT**: Get the branch name first, then pass it as a plain string. Do NOT use shell expansion `$(...)` in the command as it triggers permission prompts.

First, get the current branch:
```bash
git branch --show-current
```

Then create references with the branch value:
```bash
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references create \
  --plan-id {plan_id} \
  --branch {branch_name}
```

If issue source, also include:
```bash
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references create \
  --plan-id {plan_id} \
  --branch {branch_name} \
  --issue-url {issue_url}
```

### Step 7: Detect Domain

Determine domain from task analysis.

| Indicator | Domain |
|-----------|--------|
| Java code, Maven/Gradle, .java files | `java` |
| JavaScript, npm, .js/.ts files | `javascript` |
| Plugin/skill/command development | `plugin` |
| Generic/simple task | `generic` |

**If domain parameter provided**: Use override value.

**If uncertain**, ask:

```
AskUserQuestion:
  question: "What technology stack does this task primarily involve?"
  options:
    - label: "Java"
      description: "Java code with Maven or Gradle"
      value: "java"
    - label: "JavaScript"
      description: "JavaScript/TypeScript with npm"
      value: "javascript"
    - label: "Plugin Development"
      description: "Claude Code plugin components"
      value: "plugin"
    - label: "Generic"
      description: "Generic task, no specific technology"
      value: "generic"
```

**After detecting domain**, log the decision with reasoning:

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "[DECISION] Detected domain: {domain} - {reasoning}"
```

### Step 8: Create Status

Create status.toon with detected domain and phases:

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle create \
  --plan-id {plan_id} \
  --title "{title_from_task_md}" \
  --domain {domain} \
  --phases init,refine,execute,finalize
```

**Note**: Phases depend on domain. Use standard 4-phase for java/javascript/plugin, 3-phase (init,execute,finalize) for generic.

### Step 9: Create Configuration

Create config.toon with base settings and finalize configuration. The `manage-config create` command looks up workflow_skills from domain defaults:

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config create \
  --plan-id {plan_id} \
  --domains {domain}
```

This creates config.toon with:
- `domains`: Array of detected domains
- `workflow_skills`: Looked up from domain defaults (java, javascript, plugin, generic)
- `commit_strategy`: From defaults (per_task)
- Finalize fields: `create_pr`, `verification_required`, `branch_strategy` (from defaults)

### Step 10: Log Creation

Log the plan creation as an artifact:

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "[ARTIFACT] Created plan: {derived_title} (source: {source_type}, domain: {domain})"
```

### Step 11: Transition Phase

The phase transitions from init → refine after configuration completes:

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed init
```

### Step 12: Return Result

**Output**:

```toon
status: success
plan_id: {plan_id}
domain: {domain}
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
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} ERROR "{error_type}: {full error context and message}"
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

This skill is called by `pm-workflow:plan-init-agent`. The agent completes the full init phase in a single call.

### Command Integration

- **/plan-manage action=init** - Orchestrates the init agent

### Scripts Used

| Script | Purpose |
|--------|---------|
| `pm-workflow:manage-plan-documents` | Write request.md (typed document) |
| `pm-workflow:manage-files` | Create/reference plan directory |
| `pm-workflow:manage-references` | Initialize references |
| `plan-marshall:logging:manage-log` | Log creation |
| `plan-marshall:lessons-learned` | Read lesson (if source=lesson) |
| `pm-workflow:manage-config` | Create config.toon |
| `pm-workflow:manage-lifecycle` | Create status.toon, phase transitions |

### Related Skills

- **plan-refine** - Next phase after init completes
- **Domain skills** - Loaded by thin agents via config.toon workflow_skills

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
- [x] Creates config.toon with domain and finalize fields
- [x] Creates status.toon with phases
- [x] Does NOT create goals (that's refine phase)
