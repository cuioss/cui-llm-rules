---
name: manage-solution-outline
description: Manage solution outline documents - standards, examples, validation, and deliverable extraction
allowed-tools: Read, Glob, Bash
---

# Manage Solution Outline Skill

This skill provides structure guidelines, examples, and operations for `solution_outline.md` documents. Load this skill when creating or modifying solution outlines.

## When to Load This Skill

Load this skill in Step 0 when:
- Creating a solution outline (goals agents: java-solution-plan, js-solution-plan, plugin-solution-plan, plan-refine)
- Reviewing or updating an existing solution outline
- Validating solution document structure

**Not needed for**: Creating tasks from deliverables (use manage-tasks skill)

---

## Document Structure

Solution outlines have a fixed structure with required and optional sections:

```markdown
# Solution: {title}

plan_id: {plan_id}
created: {timestamp}

## Summary          ← REQUIRED: 2-3 sentences describing the approach

## Overview         ← REQUIRED: ASCII diagram showing architecture/flow

## Deliverables     ← REQUIRED: Numbered ### sections

## Approach         ← OPTIONAL: Execution strategy

## Dependencies     ← OPTIONAL: External requirements

## Risks and Mitigations  ← OPTIONAL: Risk analysis
```

See [standards/structure.md](standards/structure.md) for detailed requirements.

---

## Deliverables Format

Deliverables use numbered `###` headings:

```markdown
## Deliverables

### 1. Create JwtValidationService class

Description of what this deliverable produces.

**Location**: `src/main/java/de/cuioss/auth/jwt/JwtValidationService.java`

**Responsibilities**:
- Validate JWT signature
- Check token expiration

### 2. Add configuration support

Description...
```

**Key Rules**:
- Numbers must be sequential starting from 1
- Titles should be concrete work items (not abstract goals)
- Each deliverable should be independently achievable
- Include location, responsibilities, or success criteria

See [standards/deliverables.md](standards/deliverables.md) for reference format.

---

## Overview Diagrams

The Overview section contains ASCII diagrams showing component relationships. Different task types use different diagram patterns:

| Task Type | Diagram Style |
|-----------|---------------|
| Feature | Component/class relationships with dependencies |
| Refactoring | BEFORE → AFTER transformation comparison |
| Bugfix | Problem sequence + Solution architecture |
| Documentation | File structure with cross-references |
| Plugin | Integration flow with build phases |

See [standards/diagrams.md](standards/diagrams.md) for patterns and examples.

---

## Examples by Task Type

Examples provide starting points for different task categories:

| Example | Use When |
|---------|----------|
| [examples/java-feature.md](examples/java-feature.md) | Java feature implementation |
| [examples/javascript-feature.md](examples/javascript-feature.md) | JavaScript/frontend feature |
| [examples/plugin-feature.md](examples/plugin-feature.md) | Claude Code plugin development |
| [examples/refactoring.md](examples/refactoring.md) | Code refactoring tasks |
| [examples/bugfix.md](examples/bugfix.md) | Bug fix with root cause analysis |
| [examples/documentation-task.md](examples/documentation-task.md) | Documentation creation/updates |

---

## Writing the Solution Document

### Step 1: Analyze Request

Read the request document to understand:
- What is being requested
- Scope and constraints
- Success criteria

### Step 2: Design Architecture

Before writing, determine:
- Components involved
- Dependencies between components
- Execution order

### Step 3: Create Diagram

Draw ASCII diagram showing:
- New components (boxed)
- Existing components (labeled)
- Dependencies (arrows)
- Package/file structure

### Step 4: Write Document

Write directly using Claude Code's Write tool to: `.plan/plans/{plan_id}/solution_outline.md`

**Why direct Write?** Solution outlines contain ASCII diagrams with box-drawing characters (│, ─, ┌, └) that are difficult to pass via CLI parameters.

### Step 5: Validate

After writing, validate structure:

```bash
python3 .plan/execute-script.py planning:manage-solution-outline:manage-solution-outline \
  validate \
  --plan-id {plan_id}
```

---

## Deliverable References

When tasks reference deliverables, use the full reference format:

```toon
deliverable: "1. Create JwtValidationService class"
```

**Reference Format Rules**:
- Include number and full title
- Format: `N. Title` (number, dot, space, title)
- Title must match exactly what's in solution document

**Validation** (for scripts):
```python
import re

def validate_deliverable(deliverable_str: str) -> tuple[int, str]:
    """Parse 'N. Title' format, return (number, full_reference)"""
    match = re.match(r'^(\d+)\.\s+(.+)$', deliverable_str.strip())
    if not match:
        raise ValueError(f"Invalid format: {deliverable_str}. Expected 'N. Title'")
    return int(match.group(1)), deliverable_str.strip()
```

---

## Integration

**Loaded by**:
- `cui-java-expert:java-solution-plan` agent
- `cui-frontend-expert:js-solution-plan` agent
- `cui-plugin-development-tools:plugin-solution-plan` agent
- `planning:plan-refine` agent (for generic plans)

**Scripts Used**:
- `planning:manage-solution-outline:manage-solution-outline` - `validate`, `read`, `list-deliverables`, `exists`

**Related Skills**:
- `planning:manage-tasks` - Task creation with deliverable references
- `planning:manage-plan-documents` - Request document operations
