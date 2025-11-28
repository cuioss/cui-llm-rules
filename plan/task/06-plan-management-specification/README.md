# Plan Management Specification

## Overview

This specification defines the **plan management abstraction layer** that provides a consistent interface for creating, reading, updating, and managing task plan files. This abstraction follows the same pattern as `adr-management` and `interface-management` skills in the codebase.

**Key Principle**: Plan operations are split between **two focused commands** with clear separation of concerns:

| Command | Purpose | Phases Handled |
|---------|---------|----------------|
| `/plan-manage` | Plan lifecycle management | init, refine |
| `/plan-execute` | Plan execution | implement, verify, finalize |

**Orchestration**: Both commands delegate to the `phase-management` skill, which routes to phase-specific skills:
- **plan-init**: Create plan, environment detection, type routing
- **plan-refine**: Analyze requirements, plan tasks, identify docs
- **plan-implement**: Execute tasks, delegate to language agents
- **plan-verify**: Run builds, quality checks, documentation review
- **plan-finalize**: Commit changes, create PR, handle PR workflow

## Document Structure

This specification is split into focused modules:

### 1. [Plan Types](plan-types.md) (Init Phase Router)
Init phase decision tree and selection logic

**Key Content**:
- Init phase decision tree (routes to specific init implementation)
- Selection logic and user prompts
- Progressive disclosure strategy
- Common configuration persistence

**Key Insight**: Plan type selection = init phase execution = plan structure creation

### 2. [Architecture](architecture.md)
Architecture patterns, abstraction layer design, and comparison with similar patterns (`adr-management`, `interface-management`)

**Key Content**:
- Two-command architecture diagram
- Pattern consistency across documentation skills
- Benefits of the abstraction approach

### 3. [Templates & Workflow](templates-workflow.md)
Plan file templates, phase-based workflow, and status management

**Key Content**:
- Phase-based workflow (5 phases: init, refine, implement, verify, finalize)
- Standard plan.md template
- Status values and helper fields
- Phase Progress Table format

### 4. [API Specification](api.md)
Complete skill API with all operations and TOON handoff interfaces

**Key Content**:
- Skill operations for phase-management
- Phase skill operations (init, refine, implement, verify, finalize)
- plan-files persistence operations

### 5. [Decomposition](decomposition.md)
Implementation details, integration points, and usage examples

**Key Content**:
- Integration with /plan-manage and /plan-execute commands
- Integration with skills (adr-management, interface-management)
- Usage examples for both commands

### 6. [Phase Management](phase-management.md)
Orchestration skill specification with workflows for both commands

**Key Content**:
- Workflow: Manage Plans (for /plan-manage)
- Workflow: Execute Plans (for /plan-execute)
- Operations: list-plans, cleanup-plans, init-plan, refine-plan, discover-executable

### 7. [Migration Plan](updated-plan/migration.md)
Implementation checklist for the refactoring

**Key Content**:
- Script updates (discover-plans.py --filter)
- Skill updates (new workflows and operations)
- Command creation (plan-manage, plan-execute)
- Old command removal (task.md)

### 8. Done (Completed Specifications)

Specification documents that have been incorporated into the skills (archived in `done/`):
- `plan-init/` - Init phase specification (→ `plan-init` skill)
- `plan-refine/` - Refine phase specification (→ `plan-refine` skill)
- `plan-implement/` - Implement phase specification (→ `plan-implement` skill)
- `plan-verify/` - Verify phase specification (→ `plan-verify` skill)
- `plan-finalize/` - Finalize phase specification (→ `plan-finalize` skill)
- `plan-files/` - Persistence layer specification (→ `plan-files` skill)

## Quick Reference

### Key Features

- **Two-Command Architecture**: Management (`/plan-manage`) vs execution (`/plan-execute`)
- **Plan Types**: Implementation (full dev workflow) and Simple (lightweight) init implementations
- **Directory Structure**: `.claude/plans/{task-name}/` with `plan.md` and `references.md`
- **Phase-Based Workflow**: 5 sequential phases with automatic progress tracking
- **Interactive Discovery**: Both commands offer numbered selection with `AskUserQuestion`
- **Lifecycle Management**: List, cleanup, and manage plans via `/plan-manage`

### Operations Summary

| Component | Purpose | Key Operations |
|-----------|---------|----------------|
| **/plan-manage** | Management command | list, cleanup, init, refine |
| **/plan-execute** | Execution command | execute implement/verify/finalize phases |
| **phase-management** | Orchestration | Manage Plans workflow, Execute Plans workflow |
| **plan-init** | Init phase | create, detect-environment, configure |
| **plan-refine** | Refine phase | analyze, plan-tasks, identify-docs |
| **plan-implement** | Implement phase | execute-tasks, delegate, track-progress |
| **plan-verify** | Verify phase | run-build, check-quality, review-docs |
| **plan-finalize** | Finalize phase | commit, create-pr, pr-workflow |
| **plan-files** | Persistence | read-plan, read-config, get-references, write-*, update-progress |

### Command Quick Reference

```bash
# Management (plan-manage)
/plan-manage                              # List all plans, interactive selection
/plan-manage action=init task="Feature"   # Create new plan
/plan-manage action=refine                # Refine plans (select from list)
/plan-manage action=cleanup               # Remove completed plans

# Execution (plan-execute)
/plan-execute                             # Execute plans (select from executable)
/plan-execute plan="jwt-auth"             # Execute specific plan (by name)
/plan-execute plan="jwt-auth" phase="verify"  # Force specific phase
```

## Navigation

Start with [Plan Types](plan-types.md) for init phase router and workflows, then [Architecture](architecture.md) for the design overview.

For phase-based workflow, see [Templates & Workflow](templates-workflow.md).

For API integration, refer to [API Specification](api.md) for all TOON handoff interfaces.

For implementation guidance, see [Decomposition](decomposition.md) for usage examples and [Migration Plan](updated-plan/migration.md) for the implementation checklist.

**Implemented Skills** (in `cui-task-workflow/skills/`):
- `phase-management` (orchestration)
- `plan-init`, `plan-refine`, `plan-implement`, `plan-verify`, `plan-finalize`, `plan-files`
