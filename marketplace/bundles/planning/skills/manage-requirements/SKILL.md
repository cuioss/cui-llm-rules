---
name: manage-requirements
description: Manage numbered requirements within a plan using separate files per requirement
allowed-tools: Read, Glob, Bash
---

# Manage Requirements Skill

Manage numbered requirements within a plan. Uses separate files per requirement for clean git diffs and atomic operations.

## What This Skill Provides

- Individual TOON file storage for each requirement
- Sequential, immutable numbering (REQ-1, REQ-2, etc.)
- Status tracking (pending/done)
- CRUD operations via single CLI script with subcommands

## When to Activate This Skill

Activate this skill when:
- Creating or managing requirements for a plan
- Querying requirements status
- Marking requirements as complete

---

## Storage Location

Requirements are stored in the plan directory:

```
{plan_dir}/requirements/
  REQ-001-implement-user-auth.toon
  REQ-002-add-session-mgmt.toon
  REQ-003-create-logout-flow.toon
```

Directory created on first `add` operation.

**Filename format**: `REQ-{NNN}-{slug}.toon`
- `{NNN}` - Zero-padded 3-digit number (001, 002, etc.)
- `{slug}` - Kebab-case from title (max 40 chars)

---

## File Format

Individual TOON files with metadata and body:

```toon
number: 1
title: Implement user authentication
status: pending
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T10:30:00Z

body: |
  Detailed requirement description.
  Can be multiple lines.

  Supports paragraphs and formatting.
```

### Requirement Fields

| Field | Required | Description |
|-------|----------|-------------|
| `number` | Yes | Unique number (assigned at creation, immutable) |
| `title` | Yes | Short descriptive title |
| `body` | Yes | Detailed requirement description |
| `status` | Yes | `pending` or `done` |
| `created` | Yes | ISO timestamp when created |
| `updated` | Yes | ISO timestamp of last update |

**Numbering Rules**:
- Numbers assigned incrementally (next available)
- Numbers are **immutable** - removal creates gaps (1, 3, 4 if REQ-2 removed)
- References use `REQ-{n}` format (stable references)

---

## Operations

Script: `planning:manage-requirements`

### add

Add a new requirement file (creates directory if needed).

```bash
python3 .plan/execute-script.py planning:manage-requirements:add \
  --plan-id {plan_id} \
  --title "Requirement title" \
  --body "Detailed requirement description"
```

**Output**:
```toon
status: success
plan_id: my-feature
file: REQ-004-implement-logout.toon
total_requirements: 4

requirement:
  number: 4
  title: Requirement title
  status: pending
```

### update

Update an existing requirement file.

```bash
python3 .plan/execute-script.py planning:manage-requirements:update \
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
file: REQ-002-new-slug.toon
renamed: true

requirement:
  number: 2
  title: New title
  status: done
```

### remove

Remove a requirement file (keeps gaps in numbering).

```bash
python3 .plan/execute-script.py planning:manage-requirements:remove \
  --plan-id {plan_id} \
  --number 2
```

**Output**:
```toon
status: success
plan_id: my-feature
total_requirements: 2

removed:
  number: 2
  title: Removed requirement title
  file: REQ-002-removed-req.toon
```

### list

List all requirements (summary view with counts).

```bash
python3 .plan/execute-script.py planning:manage-requirements:list \
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

requirements[3]{number,title,status,file}:
1,Implement user auth,done,REQ-001-implement-user-auth.toon
2,Add session management,pending,REQ-002-add-session-mgmt.toon
3,Create logout flow,pending,REQ-003-create-logout-flow.toon
```

### findAll

Get all requirements with full content (body included).

```bash
python3 .plan/execute-script.py planning:manage-requirements:findAll \
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

requirements:
  - number: 1
    title: Implement user auth
    status: done
    created: 2025-12-02T10:30:00Z
    updated: 2025-12-02T11:00:00Z
    body: User authentication with login/logout. Session management included.

  - number: 2
    title: Add session management
    status: pending
    created: 2025-12-02T10:35:00Z
    updated: 2025-12-02T10:35:00Z
    body: Handle session tokens and expiry.

  - number: 3
    title: Create logout flow
    status: pending
    created: 2025-12-02T10:40:00Z
    updated: 2025-12-02T10:40:00Z
    body: Clear session and redirect to login.
```

### get

Get a single requirement by number.

```bash
python3 .plan/execute-script.py planning:manage-requirements:get \
  --plan-id {plan_id} \
  --number 2
```

**Output**:
```toon
status: success
plan_id: my-feature
file: REQ-002-add-session.toon

requirement:
  number: 2
  title: Add session management
  status: pending
  created: 2025-12-02T10:30:00Z
  updated: 2025-12-02T10:35:00Z
  body: Detailed requirement description...
```

### check

Mark requirement as done or pending.

```bash
python3 .plan/execute-script.py planning:manage-requirements:check \
  --plan-id {plan_id} \
  --number 2 \
  --status done
```

**Output**:
```toon
status: success
plan_id: my-feature
file: REQ-002-add-session.toon

requirement:
  number: 2
  title: Add session management
  status: done
```

---

## Referencing Requirements

Requirements can be referenced elsewhere using `REQ-{n}` format (no zero padding):

- In plan.md phases: "Implement REQ-1, REQ-2"
- In work-log entries: "Completed REQ-3"
- In commit messages: "feat: implement REQ-1 user authentication"

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-requirements` | All CRUD operations via subcommands | `python3 .plan/execute-script.py planning:manage-requirements::{command} --help` |

---

## Integration Points

### With plan-configure-agent

The plan-configure-agent uses this skill to add requirements:

```
Skill: planning:manage-requirements
operation: add
plan_id: {plan_id}
title: "Implement user authentication"
body: "Create login/logout functionality with session management"
```

### With phase-management

Requirements can be tracked across phases and marked done as work progresses.
