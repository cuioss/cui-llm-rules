# Declarative Document Engine Architecture

## Design Principle

Document types are **data, not code**. The engine is a generic processor that:
1. Loads document definitions from `documents/{type}.toon`
2. Validates input against field schemas
3. Renders templates with provided values
4. Writes files using `file_ops` utilities

This separation enables adding new document types without code changes.

---

## Component Layers

```
┌─────────────────────────────────────────────────────────────┐
│ CLI Layer                                                   │
│   - Parses: {doc-type} {verb} [options]                     │
│   - Dynamically builds subparsers from document definitions │
│   - Routes to command handlers                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Document Type Registry                                      │
│   - Discovers types from documents/*.toon                   │
│   - Parses field and section definitions                    │
│   - Provides schema for validation                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Validation Layer                                            │
│   - Checks required fields present                          │
│   - Validates field types (enum, date, etc.)                │
│   - Reports structured errors                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Template Engine                                             │
│   - Loads template from templates/                          │
│   - Substitutes {field} placeholders                        │
│   - Handles built-in placeholders ({plan_id}, {timestamp})  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ File Operations (via file_ops)                              │
│   - Atomic writes via atomic_write_file()                   │
│   - Path resolution via base_path()                         │
│   - Plan directory management                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Document Definition Schema

Document types are defined in `documents/{type}.toon`:

```toon
name: {type_name}
file: {physical_filename}
template: templates/{template_file}

fields[N]{name,type,required,default}:
{field_name},{field_type},{true|false},{default_value}
...

sections[N]{name,heading,order}:
{section_name},{markdown_heading},{display_order}
...
```

### Field Types

| Type | Description | Validation |
|------|-------------|------------|
| `string` | Single-line text | Non-empty if required |
| `text` | Multi-line text | Non-empty if required |
| `enum(a\|b\|c)` | Enumerated values | Must match one of values |
| `date` | ISO date/timestamp | Valid ISO format |
| `list` | Pipe-separated values | Split on `\|` |

---

## Data Flow

### Create Operation

```
Input: doc_type, plan_id, field values
         │
         ▼
    ┌────────────┐
    │ Load Type  │──→ documents/{type}.toon
    └────────────┘
         │
         ▼
    ┌────────────┐
    │ Validate   │──→ Check required fields, enum values
    └────────────┘
         │
         ▼
    ┌────────────┐
    │ Render     │──→ templates/{type}.md + field substitution
    └────────────┘
         │
         ▼
    ┌────────────┐
    │ Write      │──→ .plan/plans/{plan_id}/{file}
    └────────────┘
         │
         ▼
Output: TOON status response
```

### Read Operation

```
Input: doc_type, plan_id
         │
         ▼
    ┌────────────┐
    │ Load Type  │──→ Resolve physical filename
    └────────────┘
         │
         ▼
    ┌────────────┐
    │ Read File  │──→ .plan/plans/{plan_id}/{file}
    └────────────┘
         │
         ▼
    ┌────────────┐
    │ Parse      │──→ Extract sections by ## headings
    └────────────┘
         │
         ▼
Output: TOON with content sections
```

### Update Operation

```
Input: doc_type, plan_id, section, content
         │
         ▼
    ┌────────────┐
    │ Read       │──→ Load existing document
    └────────────┘
         │
         ▼
    ┌────────────┐
    │ Find/Replace│──→ Locate section, replace content
    └────────────┘
         │
         ▼
    ┌────────────┐
    │ Write      │──→ Atomic write back
    └────────────┘
```

---

## Extensibility Points

| Extension | Mechanism |
|-----------|-----------|
| New document type | Add `documents/{type}.toon` + `templates/{type}.md` |
| New field type | Extend `validate_fields()` with type handler |
| Custom validation | Add validation rules to field type definition |
| Output format | Modify serialization in command handlers |

---

## Dependencies

| Component | Source | Purpose |
|-----------|--------|---------|
| `toon_parser` | `general-tools:toon-usage` | Parse/serialize TOON format |
| `file_ops` | `general-tools:file-operations-base` | Atomic writes, path resolution |

---

## Design Decisions

### Why Declarative?

- **Separation of concerns**: Schema definition vs processing logic
- **Maintainability**: Non-developers can add document types
- **Testability**: Definitions can be validated independently
- **Consistency**: All types follow same structure

### Why TOON for Definitions?

- Matches existing infrastructure
- Token-efficient for LLM consumption
- Human-readable
- Supports tables for field definitions

### Why Markdown Templates?

- Standard format for documentation
- Section-based structure maps to fields
- Easy to preview and edit
- Git-friendly diffs
