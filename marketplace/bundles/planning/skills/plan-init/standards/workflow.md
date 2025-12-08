# Plan Init Workflow

## Two-Agent Init Pattern

The init phase uses two sequential agents for context efficiency:

```
User Request (description, lesson_id, or issue)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ PLAN-INIT-AGENT (creates task.md)                   │
│                                                     │
│   1. Validate input (exactly one source)            │
│   2. Derive plan_id from input                      │
│   3. Create or reference plan (single atomic call)  │
│   4. Get task content from source                   │
│   5. Plan directory ready                           │
│   6. Write task.md (preserves original input)       │
│   7. Initialize references.toon (branch only)       │
│   8. Log creation                                   │
│   OUTPUT: plan_id                                   │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ PLAN-CONFIGURE-AGENT (analyzes and configures)      │
│                                                     │
│   1. Read task.md                                   │
│   2. Analyze task to extract requirements           │
│   3. Ask user for clarification (if needed)         │
│   4. Create numbered requirements (REQ-1, REQ-2)    │
│   5. Detect plan type from requirements             │
│   6. Create config.toon with plan type              │
│   7. Call plan-type:configure for domain fields     │
│   8. Transition phase to "refine"                   │
│   OUTPUT: plan_id, requirements summary             │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Refine Phase
```

## Plan Init Responsibilities

Plan-init is minimal. It ONLY:

| Does | Does NOT |
|------|----------|
| Creates plan directory | Determine plan type |
| Writes task.md | Create config.toon |
| Initializes references.toon (branch) | Create requirements |
| Logs creation | Ask about configuration |
| Returns plan_id | Call plan-type skills |

## Input Sources

Plan-init accepts exactly ONE of these inputs:

### Description (Free-form text)
```
description: "Add dark mode toggle to application settings"
```

- Stored verbatim in task.md
- No additional context extraction
- Simplest input type

### Lesson ID
```
lesson_id: "2025-12-02-001"
```

- Fetched via `manage-lessons-learned` skill
- Extracts: title, category, component, detail, related
- Context section populated with lesson metadata

### Issue URL
```
issue: "https://github.com/org/repo/issues/123"
```

- Fetched via `gh issue view`
- Extracts: title, body, labels, milestone, assignees
- Context section populated with issue metadata

## Plan ID Derivation

| Source | Derivation Rule | Example |
|--------|----------------|---------|
| Description | First 3-5 meaningful words | "add-dark-mode-toggle" |
| Lesson | Prefix + lesson ID | "lesson-2025-12-02-001" |
| Issue | Prefix + issue number | "issue-123" |

Rules:
- Always kebab-case
- Maximum 50 characters
- No special characters except hyphens
- User can override with `--plan-id` parameter

## Existing Plan Handling

When plan directory already exists:

```
AskUserQuestion:
  "Plan 'my-feature' already exists. What would you like to do?"

  Options:
  1. Resume - Continue with existing plan
  2. Replace - Delete and recreate
  3. Rename - Use different plan_id
```

## Validation Criteria

### Input Validation
- [ ] Exactly one source provided (description, lesson_id, OR issue)
- [ ] If lesson_id: lesson exists and is readable
- [ ] If issue: issue URL valid and accessible
- [ ] Plan ID format: kebab-case, max 50 chars

### Output Validation
- [ ] Plan directory created (via manage-files create-or-reference)
- [ ] task.md created with complete original input
- [ ] references.toon created with branch
- [ ] Work-log entry written
- [ ] plan_id returned

### NOT Created (plan-configure responsibility)
- [ ] config.toon NOT created
- [ ] requirements/ NOT created
- [ ] Plan type NOT determined

## Error Handling

### Invalid Lesson ID
```toon
status: error
error: invalid_lesson
message: Lesson not found: {lesson_id}
recovery: Check lesson ID with manage-lessons-learned list
```

### Invalid Issue URL
```toon
status: error
error: invalid_issue
message: Issue not found or inaccessible: {issue}
recovery: Verify URL, check permissions
```

### Multiple Sources
```toon
status: error
error: multiple_sources
message: Provide exactly one of: description, lesson_id, issue
recovery: Remove extra parameters
```

### Plan Already Exists (not resumed)
```toon
status: error
error: plan_exists
message: Plan already exists and resume not selected
recovery: Use resume option or provide different plan_id
```

## Integration Points

### Scripts Used

| Script | Purpose |
|--------|---------|
| `planning:manage-files` | Create/reference plan directory, write task.md |
| `planning:manage-references` | Initialize references |
| `planning:manage-log` | Log creation |
| `planning:manage-lessons` | Read lesson content |

### Subsequent Agent

After plan-init completes, `plan-configure-agent` is called to:
1. Read task.md
2. Analyze and create requirements
3. Detect plan type
4. Create configuration
5. Transition to refine phase
