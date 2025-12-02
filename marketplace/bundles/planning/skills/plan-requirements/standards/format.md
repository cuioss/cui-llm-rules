# Requirements File Format Specification

## Overview

Requirements are stored as individual TOON files in the plan's `requirements/` directory. Each file represents one requirement with metadata and body content.

## Directory Structure

```
{plan_dir}/requirements/
├── REQ-001-implement-user-auth.toon
├── REQ-002-add-session-mgmt.toon
└── REQ-003-create-logout-flow.toon
```

## Filename Convention

**Pattern**: `REQ-{NNN}-{slug}.toon`

| Component | Description | Example |
|-----------|-------------|---------|
| `REQ-` | Fixed prefix | `REQ-` |
| `{NNN}` | Zero-padded 3-digit number | `001`, `042`, `123` |
| `-` | Separator | `-` |
| `{slug}` | Kebab-case from title (max 40 chars) | `implement-user-auth` |
| `.toon` | File extension | `.toon` |

### Slug Generation Rules

1. Convert title to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep alphanumeric and hyphens)
4. Collapse multiple hyphens to single
5. Truncate to 40 characters
6. Remove trailing hyphens

**Example**: "Implement User Authentication!" → `implement-user-authentication`

## File Format

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

## Field Definitions

### number (required)

- **Type**: Integer
- **Constraints**: Positive integer, unique within plan, immutable after creation
- **Assignment**: Next available number when created
- **Note**: Gaps allowed after removal (1, 3, 4 if REQ-2 removed)

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
- **Updates on**: title change, body change, status change

### body (required)

- **Type**: Multiline string
- **Format**: TOON multiline with `|` indicator
- **Purpose**: Detailed requirement description
- **Supports**: Multiple paragraphs, markdown formatting

## Numbering Rules

### Assignment

Numbers are assigned sequentially based on the highest existing number:

```
Existing: REQ-001, REQ-002, REQ-003
Next add → REQ-004
```

### Gaps After Removal

Numbers are never reassigned. Removing a requirement creates a gap:

```
Before: REQ-001, REQ-002, REQ-003
Remove REQ-002
After: REQ-001, REQ-003
Next add → REQ-004
```

### Reference Stability

External references use `REQ-{n}` (no zero padding):
- `REQ-1` (not `REQ-001`)
- `REQ-42` (not `REQ-042`)

This ensures references remain valid even if the file is renamed (due to title change).

## Validation Rules

### On Creation

1. Title must be non-empty
2. Body must be non-empty
3. Number must be next available

### On Update

1. Number cannot be changed
2. Created timestamp cannot be changed
3. Status must be valid enum value
4. If title changes, file must be renamed with new slug

### File Integrity

1. All required fields must be present
2. Timestamps must be valid ISO 8601
3. Number in file must match filename number
