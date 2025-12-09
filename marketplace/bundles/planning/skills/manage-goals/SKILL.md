---
name: manage-goals
description: Manage numbered goals within a plan using separate files per goal
allowed-tools: Read, Glob, Bash
---

# Manage Goals Skill

Manage numbered goals within a plan. Uses separate files per goal for clean git diffs and atomic operations.

## What This Skill Provides

- Individual TOON file storage for each goal
- Sequential, immutable numbering (GOAL-1, GOAL-2, etc.)
- Status tracking (pending/done)
- CRUD operations via single CLI script with subcommands

## When to Activate This Skill

Activate this skill when:
- Creating or managing goals for a plan
- Querying goals status
- Marking goals as complete

---

## Storage Location

Goals are stored in the plan directory:

```
{plan_dir}/goals/
  GOAL-001-add-caffeine-dependency.toon
  GOAL-002-create-cache-config.toon
  GOAL-003-add-cacheable-annotation.toon
```

Directory created on first `add` operation.

**Filename format**: `GOAL-{NNN}-{slug}.toon`
- `{NNN}` - Zero-padded 3-digit number (001, 002, etc.)
- `{slug}` - Kebab-case from title (max 40 chars)

---

## File Format

Individual TOON files with metadata and body:

```toon
number: 1
title: Add Caffeine cache dependency
status: pending
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T10:30:00Z

body: |
  Add Caffeine caching library to pom.xml.
  Use version from parent BOM if available.
```

### Goal Fields

| Field | Required | Description |
|-------|----------|-------------|
| `number` | Yes | Unique number (assigned at creation, immutable) |
| `title` | Yes | Short descriptive title |
| `body` | Yes | Detailed goal description |
| `status` | Yes | `pending` or `done` |
| `created` | Yes | ISO timestamp when created |
| `updated` | Yes | ISO timestamp of last update |

**Numbering Rules**:
- Numbers assigned incrementally (next available)
- Numbers are **immutable** - removal creates gaps (1, 3, 4 if GOAL-2 removed)
- References use `GOAL-{n}` format (stable references)

---

## Operations

Script: `planning:manage-goals:manage-goal`

### add

Add a new goal file (creates directory if needed).

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal add \
  --plan-id {plan_id} \
  --title "Goal title" \
  --body "Detailed goal description"
```

**Output**:
```toon
status: success
plan_id: my-feature
file: GOAL-004-add-cache-config.toon
total_goals: 4

goal:
  number: 4
  title: Goal title
  status: pending
```

### update

Update an existing goal file.

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal update \
  --plan-id {plan_id} \
  --number 2 \
  [--title "New title"] \
  [--body "New body"] \
  [--status pending|done]
```

**Output**:
```toon
status: success
plan_id: my-feature
file: GOAL-002-new-slug.toon
renamed: true

goal:
  number: 2
  title: New title
  status: done
```

### remove

Remove a goal file (keeps gaps in numbering).

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal remove \
  --plan-id {plan_id} \
  --number 2
```

**Output**:
```toon
status: success
plan_id: my-feature
total_goals: 2

removed:
  number: 2
  title: Removed goal title
  file: GOAL-002-removed-goal.toon
```

### list

List all goals (summary view with counts).

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal list \
  --plan-id {plan_id} \
  [--status pending|done|all]
```

**Output**:
```toon
status: success
plan_id: my-feature

counts:
  total: 3
  pending: 2
  done: 1

goals[3]{number,title,status,file}:
1,Add Caffeine dependency,done,GOAL-001-add-caffeine-dependency.toon
2,Create cache config,pending,GOAL-002-create-cache-config.toon
3,Add cacheable annotation,pending,GOAL-003-add-cacheable-annotation.toon
```

### findAll

Get all goals with full content (body included).

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal findAll \
  --plan-id {plan_id}
```

**Output**:
```toon
status: success
plan_id: my-feature

counts:
  total: 3
  pending: 2
  done: 1

goals:
  - number: 1
    title: Add Caffeine dependency
    status: done
    created: 2025-12-02T10:30:00Z
    updated: 2025-12-02T11:00:00Z
    body: Add Caffeine caching library to pom.xml.

  - number: 2
    title: Create cache config
    status: pending
    created: 2025-12-02T10:35:00Z
    updated: 2025-12-02T10:35:00Z
    body: Create CacheConfig class with @EnableCaching.

  - number: 3
    title: Add cacheable annotation
    status: pending
    created: 2025-12-02T10:40:00Z
    updated: 2025-12-02T10:40:00Z
    body: Add @Cacheable to UserService methods.
```

### get

Get a single goal by number.

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal get \
  --plan-id {plan_id} \
  --number 2
```

**Output**:
```toon
status: success
plan_id: my-feature
file: GOAL-002-create-cache-config.toon

goal:
  number: 2
  title: Create cache config
  status: pending
  created: 2025-12-02T10:30:00Z
  updated: 2025-12-02T10:35:00Z
  body: Create CacheConfig class with @EnableCaching.
```

### check

Mark goal as done or pending.

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal check \
  --plan-id {plan_id} \
  --number 2 \
  --status done
```

**Output**:
```toon
status: success
plan_id: my-feature
file: GOAL-002-create-cache-config.toon

goal:
  number: 2
  title: Create cache config
  status: done
```

---

## Referencing Goals

Goals can be referenced elsewhere using `GOAL-{n}` format (no zero padding):

- In tasks: `goal: GOAL-1`
- In work-log entries: "Completed GOAL-3"
- In commit messages: "feat: implement GOAL-1 cache dependency"

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-goals:manage-goal` | All CRUD operations via subcommands | `python3 .plan/execute-script.py planning:manage-goals:manage-goal {subcommand} --help` |

---

## Integration Points

### With plan-type agents

The plan-type agents (java-goals-agent, js-goals-agent, plugin-goals-agent) use this skill to add goals:

```
Skill: planning:manage-goals
operation: add
plan_id: {plan_id}
title: "Add Caffeine cache dependency"
body: "Add Caffeine caching library to pom.xml"
```

### With manage-tasks

Tasks reference goals directly via the `goal:` field:

```toon
number: 1
title: Create CacheConfig class
goal: GOAL-2
...
```
