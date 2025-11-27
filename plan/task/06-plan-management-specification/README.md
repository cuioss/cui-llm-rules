# Plan Management Specification

## Overview

This specification defines the **plan management abstraction layer** that provides a consistent interface for creating, reading, updating, and managing task plan files. This abstraction follows the same pattern as `adr-management` and `interface-management` skills in the codebase.

**Key Principle**: All plan file operations are abstracted through **one skill per phase**:
- **plan-init**: Create plan, environment detection, type routing
- **plan-refine**: Analyze requirements, plan tasks, identify docs
- **plan-implement**: Execute tasks, delegate to language agents
- **plan-verify**: Run builds, quality checks, documentation review
- **plan-finalize**: Commit changes, create PR, handle PR workflow

No commands or agents directly interact with plan files - they delegate to phase skills for all file I/O operations.

## Document Structure

This specification is split into focused modules:

### 1. [Plan Types](plan-types.md) (Init Phase Router)
Init phase decision tree and selection logic

**Key Content**:
- Init phase decision tree (routes to specific init implementation)
- Selection logic and user prompts
- Progressive disclosure strategy
- Common configuration persistence

**Init Implementations** (plan-init/):
- [Implementation](plan-init/implementation.md) - Full dev workflow producing 5 phases
- [Simple](plan-init/simple.md) - Lightweight workflow producing 3 phases
- [Handoff Protocol](plan-init/handoff.md) - TOON incoming/outgoing specifications

**Key Insight**: Plan type selection = init phase execution = plan structure creation

### 2. [Refine Phase](plan-refine/refine.md) (Requirement Analysis)
Refine phase implementation for analyzing requirements and planning tasks

**Key Content**:
- Component analysis workflow
- Task planning with user interaction
- Documentation needs identification (ADRs, interfaces)
- Runtime artifact generation

**Refine Documents** (plan-refine/):
- [Refine Specification](plan-refine/refine.md) - Main refine phase workflow
- [Implementation Requirements Template](plan-refine/implementation-requirements-template.md) - Runtime artifact template
- [Handoff Protocol](plan-refine/handoff.md) - TOON incoming/outgoing specifications

**Key Insight**: Refine phase produces implementation-requirements.md with detailed task guidance

### 3. [Implement Phase](plan-implement/implement.md) (Task Execution)
Implement phase implementation for executing tasks and delegating to language agents

**Key Content**:
- Task execution workflow
- Language agent delegation (Java, JavaScript)
- Progress tracking and updates
- Acceptance criteria verification
- Commit strategy execution

**Implement Documents** (plan-implement/):
- [Implement Specification](plan-implement/implement.md) - Main implement phase workflow
- [Handoff Protocol](plan-implement/handoff.md) - TOON incoming/outgoing specifications

**Key Insight**: Implement phase executes tasks from refine, delegating to language agents

### 4. [Verify Phase](plan-verify/verify.md) (Verification)
Verify phase implementation for running builds, quality checks, and documentation review

**Key Content**:
- Build execution workflow
- Quality checks (Sonar, linting)
- Documentation review
- Error handling and recovery

**Verify Documents** (plan-verify/):
- [Verify Specification](plan-verify/verify.md) - Main verify phase workflow
- [Handoff Protocol](plan-verify/handoff.md) - TOON incoming/outgoing specifications

**Key Insight**: Verify phase validates implementation through builds, quality gates, and documentation review

### 5. [Finalize Phase](plan-finalize/finalize.md) (Completion)
Finalize phase implementation for committing changes, creating PRs, and handling PR review workflow

**Key Content**:
- Commit workflow with conventional commits
- PR creation and updates
- Review feedback handling
- Merge preparation

**Finalize Documents** (plan-finalize/):
- [Finalize Specification](plan-finalize/finalize.md) - Main finalize phase workflow
- [Handoff Protocol](plan-finalize/handoff.md) - TOON incoming/outgoing specifications

**Key Insight**: Finalize phase completes workflow with commits, PR creation, and review handling via /pr-fix

### 6. [Architecture](architecture.md)
Architecture patterns, abstraction layer design, and comparison with similar patterns (`adr-management`, `interface-management`)

**Key Content**:
- Abstraction layer diagram
- Pattern consistency across documentation skills
- Benefits of the abstraction approach

### 7. [Persistence](plan-files/persistence.md) & [plan-files Skill](plan-files/plan-files.md)
File specifications, directory structure, reference management, and persistence layer skill

**Key Content**:
- Directory structure: `.claude/plans/{task-name}/`
- File format specifications (plan.md, references.md)
- References file structure with ADR and interface integration
- Naming conventions and rationale

**Persistence Documents** (plan-files/):
- [plan-files Specification](plan-files/plan-files.md) - Persistence layer skill operations
- [Persistence](plan-files/persistence.md) - File format specifications
- [Handoff Protocol](plan-files/handoff.md) - TOON incoming/outgoing specifications

### 8. [Templates & Workflow](templates-workflow.md)
Plan file templates, phase-based workflow, and status management

**Key Content**:
- Phase-based workflow (5 phases: init, refine, implement, verify, finalize)
- Standard plan.md template
- Status values and helper fields
- Phase Progress Table format

### 9. [API Specification](api.md)
Complete skill API with all operations and TOON handoff interfaces

**Key Content**:
- Create Plan operation
- Read Plan operation
- Update Plan operation
- Refine Plan operation
- Validate Plan operation
- Phase Transition operation
- Task Progress Update operation
- Manage References operation

### 10. [Decomposition](decomposition.md)
Implementation details, integration points, and usage examples

**Key Content**:
- Integration with commands (/task-plan, /task-implement)
- Integration with skills (task-execute, adr-management, interface-management)
- Usage examples (6 practical scenarios)

### 11. [Implementation Plan](plan.md)
Complete 5-phase implementation checklist with cross-references

**Key Content**:
- Phase 1: Create Phase Skills (5 skills: plan-init, plan-refine, plan-implement, plan-verify, plan-finalize)
- Phase 2: Update Commands (`/task-plan`, `/task-implement`)
- Phase 3: Update Related Skills (`task-execute`, `task-review`)
- Phase 4: Integration with Documentation Skills (ADR, interface)
- Phase 5: Documentation and Testing

## Quick Reference

### Key Features

- **Plan Types**: Implementation (full dev workflow) and Simple (lightweight) init implementations
- **Directory Structure**: `.claude/plans/{task-name}/` with `plan.md` and `references.md`
- **Phase-Based Workflow**: 5 sequential phases with automatic progress tracking
- **Reference Management**: Centralized tracking of files, ADRs, interfaces, issues, branches, external docs
- **Skill Integration**: Seamless integration with `adr-management` and `interface-management` skills
- **TOON Format**: Token-efficient handoff protocol throughout (30-60% token reduction)

### Operations Summary (One Skill Per Phase)

| Skill | Phase | Key Operations |
|-------|-------|----------------|
| **plan-init** | init | create, detect-environment, configure |
| **plan-refine** | refine | analyze, plan-tasks, identify-docs |
| **plan-implement** | implement | execute-tasks, delegate, track-progress |
| **plan-verify** | verify | run-build, check-quality, review-docs |
| **plan-finalize** | finalize | commit, create-pr, pr-workflow |

**Common operations** (shared across phase skills):
- read-plan, update-progress, phase-transition

## Navigation

Start with [Plan Types](plan-types.md) for init phase router and workflows, then [Architecture](architecture.md) for the design overview.

For file structure details, see [Persistence](plan-files/persistence.md). For phase-based workflow, see [Templates & Workflow](templates-workflow.md).

For API integration, refer to [API Specification](api.md) for all TOON handoff interfaces.

For implementation guidance, see [Decomposition](decomposition.md) for usage examples and [Implementation Plan](plan.md) for the task checklist.
