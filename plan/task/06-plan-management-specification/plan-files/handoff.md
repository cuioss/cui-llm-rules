# plan-files Handoff Protocol

**Purpose**: External interface specifications for the persistence layer skill

**Scope**: Public API for all phase skills. This skill is internal infrastructure, so "external" means the interface exposed to phase skills.

---

## Public Operations

The plan-files skill exposes these operations to all phase skills:

| Operation | Purpose | Callers |
|-----------|---------|---------|
| `create-directory` | Create plan directory | plan-init |
| `write-config` | Write config.md | plan-init |
| `write-plan` | Write/update plan.md | plan-init, plan-refine |
| `read-plan` | Read plan status | All phases |
| `read-config` | Read configuration | All phases |
| `get-references` | Read references.md | All phases |
| `write-references` | Update references.md | plan-refine, plan-implement |
| `update-progress` | Update task/phase progress | All phases |

---

## Standard Request Pattern

All phase skills use this pattern to call plan-files:

```toon
from: {calling-phase}-skill
to: plan-files-skill
handoff_id: {operation}-001

operation: {operation-name}
plan_directory: .claude/plans/{task-name}/

{operation-specific-data}
```

---

## Standard Response Pattern

All responses follow this pattern:

```toon
from: plan-files-skill
to: {calling-phase}-skill
handoff_id: {operation}-002

status: success|failed

{operation-specific-result}
```

---

## Error Responses

### File Not Found

```toon
from: plan-files-skill
to: caller
handoff_id: error-001

task:
  status: failed

error:
  type: file_not_found
  message: Plan directory not found
  details: .claude/plans/jwt-auth/ does not exist

alternatives[2]:
- Create new plan with plan-init skill
- Check directory path and try again
```

### Invalid Structure

```toon
from: plan-files-skill
to: caller
handoff_id: error-002

task:
  status: failed

error:
  type: invalid_structure
  message: Plan file has invalid structure
  details: Missing Phase Progress Table in plan.md

alternatives[2]:
- Refine plan to fix structure
- Recreate plan from scratch
```

### Parse Error

```toon
from: plan-files-skill
to: caller
handoff_id: error-003

task:
  status: failed

error:
  type: parse_error
  message: Failed to parse config.md
  details: Invalid value for technology field

alternatives[2]:
- Fix config.md manually
- Regenerate config via plan-init
```

---

## Related

- [plan-files Specification](plan-files.md) - Full operation specifications
- [Persistence](persistence.md) - File format specifications
