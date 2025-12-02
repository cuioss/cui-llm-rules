# Specifications File Format Specification

## Overview

Specifications are stored as individual TOON files in the plan's `specifications/` directory. Each file represents one specification with metadata, requirement references, and body content.

## Directory Structure

```
{plan_dir}/specifications/
├── SPEC-001-jwt-token-format.toon
├── SPEC-002-session-storage.toon
└── SPEC-003-logout-endpoint.toon
```

## Filename Convention

**Pattern**: `SPEC-{NNN}-{slug}.toon`

| Component | Description | Example |
|-----------|-------------|---------|
| `SPEC-` | Fixed prefix | `SPEC-` |
| `{NNN}` | Zero-padded 3-digit number | `001`, `042`, `123` |
| `-` | Separator | `-` |
| `{slug}` | Kebab-case from title (max 40 chars) | `jwt-token-format` |
| `.toon` | File extension | `.toon` |

### Slug Generation Rules

1. Convert title to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep alphanumeric and hyphens)
4. Collapse multiple hyphens to single
5. Truncate to 40 characters
6. Remove trailing hyphens

**Example**: "JWT Token Format!" -> `jwt-token-format`

## File Format

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

## Field Definitions

### number (required)

- **Type**: Integer
- **Constraints**: Positive integer, unique within plan, immutable after creation
- **Assignment**: Next available number when created
- **Note**: Gaps allowed after removal (1, 3, 4 if SPEC-2 removed)

### title (required)

- **Type**: String
- **Constraints**: Non-empty, max 100 characters
- **Purpose**: Short descriptive summary
- **Used for**: Filename slug generation, list displays

### status (required)

- **Type**: Enum
- **Values**: `pending`, `done`
- **Default**: `pending` (on creation)
- **Changed via**: `check` command

### created (required)

- **Type**: ISO 8601 timestamp
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Set**: Automatically on creation
- **Immutable**: Yes

### updated (required)

- **Type**: ISO 8601 timestamp
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Set**: Automatically on any modification
- **Updates on**: title change, body change, status change, requirements change

### requirements (required)

- **Type**: Comma-separated string
- **Format**: `REQ-1, REQ-3` or `REQ-1` (single)
- **Constraints**: At least one REQ reference required
- **Pattern**: Each reference must match `REQ-\d+`
- **Purpose**: Links specification to requirements for traceability

### body (required)

- **Type**: Multiline string
- **Format**: TOON multiline with `|` indicator
- **Purpose**: Detailed specification description
- **Supports**: Multiple paragraphs, markdown formatting

## Numbering Rules

### Assignment

Numbers are assigned sequentially based on the highest existing number:

```
Existing: SPEC-001, SPEC-002, SPEC-003
Next add -> SPEC-004
```

### Gaps After Removal

Numbers are never reassigned. Removing a specification creates a gap:

```
Before: SPEC-001, SPEC-002, SPEC-003
Remove SPEC-002
After: SPEC-001, SPEC-003
Next add -> SPEC-004
```

### Reference Stability

External references use `SPEC-{n}` (no zero padding):
- `SPEC-1` (not `SPEC-001`)
- `SPEC-42` (not `SPEC-042`)

This ensures references remain valid even if the file is renamed (due to title change).

## Requirements Reference Rules

### Mandatory Reference

Every specification must reference at least one requirement:
- **Valid**: `requirements: REQ-1`
- **Valid**: `requirements: REQ-1, REQ-3, REQ-5`
- **Invalid**: `requirements:` (empty)
- **Invalid**: Missing requirements field

### Format Validation

Each reference must match the pattern `REQ-N`:
- **Valid**: `REQ-1`, `REQ-42`, `REQ-100`
- **Invalid**: `REQ1`, `REQ-`, `REQ-A`, `REQUIREMENT-1`

### Traceability

The requirements field enables:
- Forward traceability: REQ -> SPEC (which specs implement this requirement?)
- Backward traceability: SPEC -> REQ (which requirements does this spec address?)
- Coverage analysis: Which requirements have specifications?

## Validation Rules

### On Creation

1. Title must be non-empty
2. Body must be non-empty
3. Requirements must contain at least one valid REQ-N reference
4. Number must be next available

### On Update

1. Number cannot be changed
2. Created timestamp cannot be changed
3. Status must be valid enum value
4. If title changes, file must be renamed with new slug
5. If updating requirements, at least one must remain

### File Integrity

1. All required fields must be present
2. Timestamps must be valid ISO 8601
3. Number in file must match filename number
4. Requirements must all match REQ-N pattern
