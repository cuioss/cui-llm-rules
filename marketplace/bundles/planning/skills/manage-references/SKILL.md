---
name: manage-references
description: Manage references.toon files with field-level access and list management
allowed-tools: Read, Glob, Bash
---

# Manage References Skill

Manage references.toon files with field-level access and list management. Tracks files, branches, and external references for a plan.

## What This Skill Provides

- Read/write references.toon
- Field-level get/set operations
- List management (add/remove items)
- File tracking for modified files

## When to Activate This Skill

Activate this skill when:
- Setting branch or issue references
- Adding modified files to tracking
- Managing external documentation references

---

## Storage Location

References are stored in the plan directory:

```
.plan/plans/{plan_id}/references.toon
```

---

## File Format

TOON format with scalar and list fields:

```toon
# Plan References

branch: feature/my-feature
issue_url: https://github.com/org/repo/issues/123
build_system: maven

modified_files[3]:
- src/main/java/Foo.java
- src/main/java/Bar.java
- src/test/java/FooTest.java

external_docs[1]{title,url}:
JWT Guide,https://jwt.io/introduction
```

### Schema Fields

| Field | Type | Description |
|-------|------|-------------|
| `branch` | string | Git branch name |
| `issue_url` | string | GitHub issue URL |
| `build_system` | string | Build system (maven, gradle, npm, none) |
| `modified_files` | list | Files modified during implementation |
| `config_files` | list | Configuration files changed |
| `test_files` | list | Test files created/modified |
| `external_docs` | table | External documentation references |

---

## Operations

Script: `planning:manage-references`

### create

Create references.toon with basic fields. Plan-type-specific fields are added later by `plan-type-*:configure`.

```bash
python3 .plan/execute-script.py planning:manage-references:create \
  --plan-id {plan_id} \
  --branch {branch_name} \
  [--issue-url {url}] \
  [--build-system {maven|gradle|npm}]
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
file: references.toon
created: true

fields[5]:
- branch
- base_branch
- modified_files
- config_files
- test_files
```

**Note**: After `create`, call `plan-type-{type}:configure` to add domain-specific fields (standards, adrs, etc.).

### read

Read entire references.toon content.

```bash
python3 .plan/execute-script.py planning:manage-references:read \
  --plan-id {plan_id}
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature

references:
  branch: feature/my-feature
  issue_url: https://github.com/org/repo/issues/123
  modified_files: 3 items
```

### get

Get a specific field value.

```bash
python3 .plan/execute-script.py planning:manage-references:get \
  --plan-id {plan_id} \
  --field branch
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: branch
value: feature/my-feature
```

### set

Set a specific field value.

```bash
python3 .plan/execute-script.py planning:manage-references:set \
  --plan-id {plan_id} \
  --field branch \
  --value feature/new-branch
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
field: branch
value: feature/new-branch
previous: feature/my-feature
```

### add-file

Add a file to modified_files list.

```bash
python3 .plan/execute-script.py planning:manage-references:add-file \
  --plan-id {plan_id} \
  --file src/main/java/NewClass.java
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
section: modified_files
added: src/main/java/NewClass.java
total: 4
```

### remove-file

Remove a file from modified_files list.

```bash
python3 .plan/execute-script.py planning:manage-references:remove-file \
  --plan-id {plan_id} \
  --file src/main/java/OldClass.java
```

**Output** (TOON):
```toon
status: success
plan_id: my-feature
section: modified_files
removed: src/main/java/OldClass.java
total: 2
```

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `planning:manage-references` | All reference operations via subcommands | `python3 .plan/execute-script.py planning:manage-references::{command} --help` |

---

## Error Handling

```toon
status: error
plan_id: my-feature
error: file_not_found
message: references.toon not found
```

---

## Integration Points

### With plan-execute

Execution phase adds modified files as work progresses.

### With plan-finalize

Finalization reads modified files for commit/PR creation.
