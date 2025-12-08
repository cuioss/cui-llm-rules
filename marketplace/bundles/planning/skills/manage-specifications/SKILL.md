---
name: manage-specifications
description: Manage numbered specifications within a plan using separate files per specification
allowed-tools: Read, Glob, Bash
---

# Manage Specifications Skill

Manage numbered specifications within a plan. Uses separate files per specification for clean git diffs and atomic operations. Each specification must reference at least one requirement.

## What This Skill Provides

- Individual TOON file storage for each specification
- Sequential, immutable numbering (SPEC-1, SPEC-2, etc.)
- Required requirement references (REQ-N) for traceability
- Status tracking (pending/done)
- CRUD operations via single CLI script with subcommands

## When to Activate This Skill

Activate this skill when:
- Creating or managing specifications for a plan
- Querying specifications status
- Marking specifications as complete
- Finding specifications by requirement reference

---

## Storage Location

Specifications are stored in the plan directory:

```
{plan_dir}/specifications/
  SPEC-001-jwt-token-format.toon
  SPEC-002-session-storage.toon
  SPEC-003-logout-endpoint.toon
```

Directory created on first `add` operation.

**Filename format**: `SPEC-{NNN}-{slug}.toon`
- `{NNN}` - Zero-padded 3-digit number (001, 002, etc.)
- `{slug}` - Kebab-case from title (max 40 chars)

---

## File Format

Individual TOON files with metadata and body:

```toon
number: 1
title: JWT Token Format
status: pending
created: 2025-12-02T10:30:00Z
updated: 2025-12-02T10:30:00Z
requirements: REQ-1, REQ-3

body: |
  Detailed specification description.
  Can be multiple lines.

  Supports paragraphs and formatting.
```

### Specification Fields

| Field | Required | Description |
|-------|----------|-------------|
| `number` | Yes | Unique number (assigned at creation, immutable) |
| `title` | Yes | Short descriptive title |
| `requirements` | Yes | Comma-separated REQ references (at least one) |
| `body` | Yes | Detailed specification description |
| `status` | Yes | `pending` or `done` |
| `created` | Yes | ISO timestamp when created |
| `updated` | Yes | ISO timestamp of last update |

**Numbering Rules**:
- Numbers assigned incrementally (next available)
- Numbers are **immutable** - removal creates gaps (1, 3, 4 if SPEC-2 removed)
- References use `SPEC-{n}` format (stable references)

**Requirements Reference Rules**:
- At least one REQ reference is **mandatory**
- Format: `requirements: REQ-1, REQ-3` (comma-separated)
- Validates format (REQ-N pattern)
- Enables traceability: SPEC -> REQ mapping

---

## Operations

Script: `planning:manage-specifications`

### add

Add a new specification file (creates directory if needed).

```bash
python3 .plan/execute-script.py planning:manage-specifications:add \
  --plan-id {plan_id} \
  --title "Specification title" \
  --requirements "REQ-1,REQ-3" \
  --body "Detailed specification description"
```

**Output**:
```toon
status: success
plan_id: my-feature
file: SPEC-001-jwt-token-format.toon
total_specifications: 1

specification:
  number: 1
  title: JWT Token Format
  requirements: REQ-1, REQ-3
  status: pending
```

**Error (no requirements)**:
```toon
status: error
message: At least one requirement reference is required
```

### update

Update an existing specification file.

```bash
python3 .plan/execute-script.py planning:manage-specifications:update \
  --plan-id {plan_id} \
  --number 2 \
  [--title "New title"] \
  [--requirements "REQ-1,REQ-2,REQ-4"] \
  [--body "New body"] \
  [--status pending|done]
```

**Output**:
```toon
status: success
plan_id: my-feature
file: SPEC-002-new-slug.toon
renamed: true

specification:
  number: 2
  title: New title
  requirements: REQ-1, REQ-2, REQ-4
  status: done
```

### remove

Remove a specification file (keeps gaps in numbering).

```bash
python3 .plan/execute-script.py planning:manage-specifications:remove \
  --plan-id {plan_id} \
  --number 2
```

**Output**:
```toon
status: success
plan_id: my-feature
total_specifications: 2

removed:
  number: 2
  title: Removed specification title
  file: SPEC-002-removed-spec.toon
```

### list

List all specifications (summary view with counts).

```bash
python3 .plan/execute-script.py planning:manage-specifications:list \
  --plan-id {plan_id} \
  [--status pending|done|all] \
  [--requirement REQ-1]
```

**Output**:
```toon
status: success
plan_id: my-feature

counts:
  total: 3
  pending: 2
  done: 1

specifications[3]{number,title,requirements,status,file}:
1,JWT Token Format,"REQ-1,REQ-3",done,SPEC-001-jwt-token-format.toon
2,Session Storage,REQ-2,pending,SPEC-002-session-storage.toon
3,Logout Endpoint,"REQ-1,REQ-2",pending,SPEC-003-logout-endpoint.toon
```

### findAll

Get all specifications with full content (body included).

```bash
python3 .plan/execute-script.py planning:manage-specifications:findAll \
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

specifications:
  - number: 1
    title: JWT Token Format
    requirements: REQ-1, REQ-3
    status: done
    created: 2025-12-02T10:30:00Z
    updated: 2025-12-02T11:00:00Z
    body: JWT token structure and validation rules...

  - number: 2
    title: Session Storage
    requirements: REQ-2
    status: pending
    created: 2025-12-02T10:35:00Z
    updated: 2025-12-02T10:35:00Z
    body: Redis-based session storage specification...
```

### get

Get a single specification by number.

```bash
python3 .plan/execute-script.py planning:manage-specifications:get \
  --plan-id {plan_id} \
  --number 2
```

**Output**:
```toon
status: success
plan_id: my-feature
file: SPEC-002-session-storage.toon

specification:
  number: 2
  title: Session Storage
  requirements: REQ-2
  status: pending
  created: 2025-12-02T10:30:00Z
  updated: 2025-12-02T10:35:00Z
  body: Detailed specification description...
```

### check

Mark specification as done or pending.

```bash
python3 .plan/execute-script.py planning:manage-specifications:check \
  --plan-id {plan_id} \
  --number 2 \
  --status done
```

**Output**:
```toon
status: success
plan_id: my-feature
file: SPEC-002-session-storage.toon

specification:
  number: 2
  title: Session Storage
  requirements: REQ-2
  status: done
```

### findByRequirement

Find all specifications that reference a specific requirement.

```bash
python3 .plan/execute-script.py planning:manage-specifications:findByRequirement \
  --plan-id {plan_id} \
  --requirement REQ-1
```

**Output**:
```toon
status: success
plan_id: my-feature
requirement: REQ-1

counts:
  total: 2
  pending: 1
  done: 1

specifications[2]{number,title,status,file}:
1,JWT Token Format,done,SPEC-001-jwt-token-format.toon
3,Logout Endpoint,pending,SPEC-003-logout-endpoint.toon
```

**Use case**: Traceability - "which specifications implement REQ-1?"

---

## Referencing Specifications

Specifications can be referenced elsewhere using `SPEC-{n}` format (no zero padding):

- In plan.md phases: "Implement SPEC-1, SPEC-2"
- In work-log entries: "Completed SPEC-3"
- In commit messages: "feat: implement SPEC-1 JWT token format"
- In task files: `specification: SPEC-1`

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-specifications` | All CRUD operations via subcommands | `python3 .plan/execute-script.py planning:manage-specifications::{command} --help` |

---

## Integration Points

### With plan-refine-agent

The plan-refine-agent uses this skill to add specifications:

```
Skill: planning:manage-specifications
operation: add
plan_id: {plan_id}
title: "JWT Token Format"
requirements: "REQ-1,REQ-3"
body: "Token structure, validation rules, expiration handling..."
```

### With plan-requirements

Specifications reference requirements via the `requirements` field, enabling:
- Forward traceability: REQ -> SPEC
- Backward traceability: SPEC -> REQ
- Coverage analysis: Which REQs have SPECs?

### With phase-management

Specifications can be tracked across phases and marked done as work progresses.

---

## Relationship to Requirements

| Aspect | requirements | specifications |
|--------|--------------|----------------|
| Directory | `{plan_dir}/requirements/` | `{plan_dir}/specifications/` |
| Prefix | REQ- | SPEC- |
| References | Independent (no links) | **Must reference REQ** |
| Created in | plan-configure phase | plan-refine phase |
| Purpose | What needs to be done | How it will be done |
| Granularity | Business-level | Technical-level |

**Flow**: REQ (what) -> SPEC (how) -> Implementation (code)
