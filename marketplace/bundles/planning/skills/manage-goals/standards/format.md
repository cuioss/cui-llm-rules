# Goals File Format Specification

## Overview

Goals are stored as individual TOON files in the plan's `goals/` directory. Each file represents one goal with metadata and body content.

## Directory Structure

```
{plan_dir}/goals/
├── GOAL-001-add-caffeine-dependency.toon
├── GOAL-002-create-cache-config.toon
└── GOAL-003-add-cacheable-annotation.toon
```

## Filename Convention

**Pattern**: `GOAL-{NNN}-{slug}.toon`

| Component | Description | Example |
|-----------|-------------|---------|
| `GOAL-` | Fixed prefix | `GOAL-` |
| `{NNN}` | Zero-padded 3-digit number | `001`, `042`, `123` |
| `-` | Separator | `-` |
| `{slug}` | Kebab-case from title (max 40 chars) | `add-caffeine-dependency` |
| `.toon` | File extension | `.toon` |

### Slug Generation Rules

1. Convert title to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep alphanumeric and hyphens)
4. Collapse multiple hyphens to single
5. Truncate to 40 characters
6. Remove trailing hyphens

**Example**: "Add Caffeine Cache Dependency!" → `add-caffeine-cache-dependency`

## File Format

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

## Field Definitions

### number (required)

- **Type**: Integer
- **Constraints**: Positive integer, unique within plan, immutable after creation
- **Assignment**: Next available number when created
- **Note**: Gaps allowed after removal (1, 3, 4 if GOAL-2 removed)

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
- **Purpose**: Detailed goal description
- **Supports**: Multiple paragraphs, markdown formatting

## Numbering Rules

### Assignment

Numbers are assigned sequentially based on the highest existing number:

```
Existing: GOAL-001, GOAL-002, GOAL-003
Next add → GOAL-004
```

### Gaps After Removal

Numbers are never reassigned. Removing a goal creates a gap:

```
Before: GOAL-001, GOAL-002, GOAL-003
Remove GOAL-002
After: GOAL-001, GOAL-003
Next add → GOAL-004
```

### Reference Stability

External references use `GOAL-{n}` (no zero padding):
- `GOAL-1` (not `GOAL-001`)
- `GOAL-42` (not `GOAL-042`)

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
