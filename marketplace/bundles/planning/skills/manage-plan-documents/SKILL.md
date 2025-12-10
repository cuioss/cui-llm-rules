---
name: manage-plan-documents
description: Manage typed documents (request, solution) within plan directories with schema validation
allowed-tools: Read, Glob, Bash
---

# Manage Plan Documents Skill

Domain-specific document management for plan content files. Provides logical document names, schema validation, template enforcement, and structured CRUD operations.

## What This Skill Provides

- Logical document names (abstract from physical filenames)
- Declarative document type definitions
- Template-based document creation
- Section-based updates
- TOON output format

## When to Activate This Skill

Activate this skill when:
- Creating or managing request documents
- Creating or managing solution outlines
- Reading plan documents with structured output
- Updating specific sections of plan documents

---

## Document Types

| Type | File | Purpose |
|------|------|---------|
| `request` | `request.md` | Original user input (source of truth) |
| `solution` | `solution_outline.md` | Consolidated goals and approach |

---

## API: Noun-Verb Pattern

```
manage-plan-document {document-type} {verb} [options]
```

### Verbs

| Verb | Description |
|------|-------------|
| `create` | Create document from template |
| `read` | Read document (parsed or raw) |
| `update` | Update specific section |
| `exists` | Check if document exists |
| `remove` | Delete document |

---

## Operations

Script: `planning:manage-plan-documents:manage-plan-document`

### request create

Create a request document.

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request create \
  --plan-id {plan_id} \
  --title "Feature Title" \
  --source description \
  --body "Full task description..."
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--plan-id` | Yes | Plan identifier |
| `--title` | Yes | Document title |
| `--source` | Yes | Source type: `description`, `lesson`, or `issue` |
| `--body` | Yes | Main content |
| `--source-id` | No | Source identifier (lesson ID, issue URL) |
| `--context` | No | Additional context |
| `--force` | No | Overwrite if exists |

**Output:**

```toon
status: success
plan_id: my-feature
document: request
file: request.md
action: created

document_info:
  title: Feature Title
  sections: title,source,source_id,body,context
```

### solution create

Create a solution outline document.

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution create \
  --plan-id {plan_id} \
  --title "Solution Overview" \
  --summary "Brief approach description" \
  --goals "### 1. First Goal\n\nDescription...\n\n### 2. Second Goal\n\nDescription..."
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--plan-id` | Yes | Plan identifier |
| `--title` | Yes | Solution title |
| `--summary` | Yes | Brief summary of approach |
| `--goals` | Yes | Goals content (markdown) |
| `--approach` | No | Technical approach details |
| `--dependencies` | No | Dependencies list |
| `--risks` | No | Risks and mitigations |

### read

Read a document with parsed sections.

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request read \
  --plan-id {plan_id}
```

**Output:**

```toon
status: success
plan_id: my-feature
document: request
file: request.md

content:
  _header: # Request: Feature Title...
  original_input: Full task description...
  context: Additional context...
```

Add `--raw` for raw markdown output.

### update

Update a specific section.

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution update \
  --plan-id {plan_id} \
  --section goals \
  --content "### 1. Updated Goal\n\nNew description..."
```

### exists

Check if document exists.

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request exists \
  --plan-id {plan_id}
```

Returns exit code 0 if exists, 1 if not.

### remove

Remove a document.

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request remove \
  --plan-id {plan_id}
```

### list-types

List available document types.

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  list-types
```

---

## Error Handling

```toon
status: error
plan_id: my-feature
document: request
error: document_not_found
message: Request document does not exist for plan my-feature

suggestions[2]:
- Create the request document first
- Check plan_id spelling
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `planning:manage-plan-documents:manage-plan-document` | All document operations |

---

## Architecture

See [standards/architecture.md](standards/architecture.md) for:
- Declarative engine design
- Document definition schema
- Adding new document types

See [standards/adding-document-types.md](standards/adding-document-types.md) for:
- Step-by-step guide to add new types

---

## Integration Points

### With plan-init

Plan initialization creates request document:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request create \
  --plan-id $PLAN_ID \
  --title "$TITLE" \
  --source description \
  --body "$BODY"
```

### With plan-refine

Plan refinement creates solution outline:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution create \
  --plan-id $PLAN_ID \
  --title "Solution Overview" \
  --summary "$SUMMARY" \
  --goals "$GOALS"
```

### With manage-files

This skill delegates file I/O to manage-files internally. Use manage-files directly only for non-typed documents.
