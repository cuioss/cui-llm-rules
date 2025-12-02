---
name: project-type-api
description: Reference documentation for long-term project planning and refactoring task tracking
allowed-tools: Read
---

# Project Type API

Reference documentation for manual project-wide planning approaches that operate outside the automated plan workflow.

## Purpose

This skill provides reference documentation for:
- Long-term project planning (doc/TODO.adoc)
- Categorized refactoring and technical debt tracking
- Manual task organization patterns

These are **different use cases** from the automated plan workflow (plan-init → plan-configure → plan-refine → plan-execute → plan-finalize).

## When to Use

| Use Case | Approach | Document |
|----------|----------|----------|
| Automated task implementation | Plan workflow | `.plan/plans/{plan_id}/` |
| Long-term project TODO tracking | Manual | `doc/TODO.adoc` |
| Technical debt / refactoring | Manual | `Refactorings.adoc` |

## Reference Documents

### Project Planning

See [references/project-planning-standards.md](references/project-planning-standards.md) for:
- Long-term, multi-month/year project planning
- Hierarchical task organization by component/feature/layer/phase
- Extended status indicators (`[ ]`, `[x]`, `[~]`, `[!]`)
- AsciiDoc format with TOC and traceability links

### Refactoring Planning

See [references/refactoring-planning-standards.md](references/refactoring-planning-standards.md) for:
- Categorized improvement tracking (C, P, S, T, D, DOC, F)
- Task identifiers for commit message integration
- Priority-based organization
- Technical debt reduction workflows

## Key Differences from Automated Planning

| Aspect | Automated Plan Workflow | Manual Project/Refactoring |
|--------|------------------------|---------------------------|
| **Scope** | Single task/issue | Entire project or ongoing |
| **Duration** | Hours to days | Months to years |
| **Format** | TOON files | AsciiDoc/Markdown |
| **Traceability** | REQ → SPEC → TASK | Manual xref links |
| **Execution** | Agent-driven | Human-driven |
| **Location** | `.plan/plans/` | `doc/` directory |

## Integration

These reference documents can be consulted when:
- Setting up project-wide TODO tracking
- Organizing technical debt reduction efforts
- Creating categorized improvement plans
- Establishing commit message conventions for refactoring
