# Plan Management Architecture

## Overview

The plan management system follows the **abstraction layer pattern** used consistently across documentation skills in the CUI ecosystem. This pattern isolates implementation details behind a clean API, allowing evolution without breaking callers.

## Two-Command Architecture

The system uses **two focused commands** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             COMMANDS                                         │
│                                                                              │
│  ┌─────────────────────────────┐     ┌─────────────────────────────┐        │
│  │      /plan-manage           │     │      /plan-execute          │        │
│  │                             │     │                             │        │
│  │  Actions:                   │     │  Phases:                    │        │
│  │  • list (default)           │     │  • implement                │        │
│  │  • cleanup                  │     │  • verify                   │        │
│  │  • init                     │     │  • finalize                 │        │
│  │  • refine                   │     │                             │        │
│  └──────────────┬──────────────┘     └──────────────┬──────────────┘        │
│                 │                                    │                       │
└─────────────────┼────────────────────────────────────┼───────────────────────┘
                  │                                    │
                  │ (Manage Plans workflow)            │ (Execute Plans workflow)
                  │                                    │
                  ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION SKILL                                       │
│                    phase-management                                          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Workflows                                        │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────┐    ┌─────────────────────────┐        │   │
│  │  │  Manage Plans           │    │  Execute Plans          │        │   │
│  │  │  • list-plans           │    │  • discover-executable  │        │   │
│  │  │  • cleanup-plans        │    │  • route-phase          │        │   │
│  │  │  • init-plan            │    │  • transition-phase     │        │   │
│  │  │  • refine-plan          │    │  • get-status           │        │   │
│  │  └─────────────────────────┘    └─────────────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ (delegates via skill invocation)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE SKILLS                                         │
│                       (cui-task-workflow)                                    │
│                                                                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│  │   plan-init     │ │   plan-refine   │ │  plan-implement │               │
│  │                 │ │                 │ │                 │               │
│  │ • create        │ │ • analyze       │ │ • execute-tasks │               │
│  │ • detect-env    │ │ • plan-tasks    │ │ • delegate      │               │
│  │ • configure     │ │ • identify-docs │ │ • track-progress│               │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘               │
│           │                   │                   │                         │
│           │  ┌─────────────────┐ ┌─────────────────┐                       │
│           │  │   plan-verify   │ │  plan-finalize  │                       │
│           │  │                 │ │                 │                       │
│           │  │ • run-build     │ │ • commit        │                       │
│           │  │ • check-quality │ │ • create-pr     │                       │
│           │  │ • review-docs   │ │ • pr-workflow   │                       │
│           │  └────────┬────────┘ └────────┬────────┘                       │
│           │           │                   │                                 │
└───────────┼───────────┼───────────────────┼─────────────────────────────────┘
            │           │                   │
            └───────────┴───────────────────┘
                        │ (file I/O via plan-files)
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE SKILL                                         │
│                      plan-files                                              │
│                                                                              │
│  Operations:                                                                 │
│  • read-plan, read-config, get-references                                   │
│  • write-plan, write-config, write-references                               │
│  • update-progress, create-directory                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FILE SYSTEM                                            │
│                 .claude/plans/{task-name}/                                   │
│                   ├── plan.md                                                │
│                   ├── config.md                                              │
│                   └── references.md                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Command Separation

### /plan-manage (Management)

Handles plan lifecycle management:

| Action | Description | Phase Skills Used |
|--------|-------------|-------------------|
| `list` | Display all plans with status | None (reads only) |
| `cleanup` | Remove completed plans | None (deletes only) |
| `init` | Create new plan | plan-init |
| `refine` | Refine requirements | plan-refine |

**User Interaction**: Numbered selection via `AskUserQuestion` for plan/action selection.

### /plan-execute (Execution)

Handles plan execution phases:

| Phase | Description | Phase Skill |
|-------|-------------|-------------|
| implement | Execute implementation tasks | plan-implement |
| verify | Run builds, quality checks | plan-verify |
| finalize | Commit, create PR | plan-finalize |

**User Interaction**: Numbered selection for executable plans (implement/verify/finalize phases).

### Key Principles

1. **Clear Separation**: Management (create, list, cleanup, refine) vs execution (implement, verify, finalize)
2. **Interactive Discovery**: Both commands offer numbered selection when called without parameters
3. **Phase Filtering**: Each command only handles its designated phases
4. **No Overlap**: A plan in init/refine phase cannot be executed via `/plan-execute`

## Phase Skills Architecture

| Skill | Phase | Key Responsibilities |
|-------|-------|---------------------|
| **plan-init** | init | Create plan, environment detection, type routing, produce structure |
| **plan-refine** | refine | Analyze requirements, plan tasks, identify ADRs/interfaces needed |
| **plan-implement** | implement | Execute tasks, delegate to language agents, track progress |
| **plan-verify** | verify | Run builds, quality checks, testing, documentation review |
| **plan-finalize** | finalize | Commit changes, create PR, handle PR workflow via `/pr-fix` |

## Pattern Consistency

This pattern mirrors existing skill abstractions in the codebase:

| Skill | Domain | File Location | Key Operations |
|-------|--------|---------------|----------------|
| `adr-management` | ADRs | `.claude/adrs/` | create, read, update, list |
| `interface-management` | Interfaces | `doc/interfaces/` | create, read, update, list |
| `plan-init` | Init phase | `.claude/plans/` | create, detect-environment, configure |
| `plan-refine` | Refine phase | `.claude/plans/` | analyze, plan-tasks, identify-docs |
| `plan-implement` | Implement phase | `.claude/plans/` | execute-tasks, delegate, track-progress |
| `plan-verify` | Verify phase | `.claude/plans/` | run-build, check-quality, review-docs |
| `plan-finalize` | Finalize phase | `.claude/plans/` | commit, create-pr, pr-workflow |

### Why Directory Structure for Plans?

While ADRs and interfaces use single files, plans require a directory structure:

**Rationale**:
- **Separation of Concerns**: Plan content (plan.md) vs references (references.md)
- **Future Expansion**: Can add diagrams, attachments, sub-plans
- **Reference Management**: Dedicated file for ADRs, interfaces, files, issues, branches
- **Clean Organization**: Complex tasks need structured artifacts

## Benefits of Two-Command Architecture

### 1. Clear User Intent

| User Want | Command |
|-----------|---------|
| "What plans do I have?" | `/plan-manage` |
| "Create a new plan" | `/plan-manage action=init` |
| "Clean up old plans" | `/plan-manage action=cleanup` |
| "Work on requirements" | `/plan-manage action=refine` |
| "Implement my plan" | `/plan-execute` |
| "Verify my changes" | `/plan-execute phase=verify` |

### 2. Phase-Appropriate Routing

- `/plan-manage` only shows plans in init/refine phases
- `/plan-execute` only shows plans in implement/verify/finalize phases
- Users don't see irrelevant options

### 3. Lifecycle Management

With `/plan-manage`:
- List all plans with current phase and status
- Clean up completed plans (with confirmation)
- Resume or create plans in early phases

### 4. Execution Focus

With `/plan-execute`:
- Focus on executable plans only
- No management clutter
- Direct path to implementation

## Phase Transition Flow

```
/plan-manage                          /plan-execute
     │                                      │
     ├─► init (plan-init)                   │
     │        │                             │
     │        ▼                             │
     └─► refine (plan-refine)               │
              │                             │
              ▼                             │
              ─────────────────────────────►│
                                            │
                                    implement (plan-implement)
                                            │
                                            ▼
                                    verify (plan-verify)
                                            │
                                            ▼
                                    finalize (plan-finalize)
                                            │
                                            ▼
                                      [COMPLETED]
```

## Error Handling

### Phase Mismatch Errors

**User tries `/plan-execute` on init-phase plan**:
```
Plan 'jwt-auth' is in 'init' phase.

This command handles execution phases only (implement, verify, finalize).
Use /plan-manage to complete init/refine phases first.
```

**User tries `/plan-manage action=refine` on implement-phase plan**:
```
Plan 'jwt-auth' is in 'implement' phase, not 'refine'.

Options:
1. Force refine (will reset implement progress)
2. Continue with implement (→ /plan-execute)
3. Cancel

Select:
```

## Summary

The plan management architecture provides:

1. **Two-Command Design** - Clear separation of management vs execution
2. **Interactive Discovery** - Numbered selection via `AskUserQuestion`
3. **Phase-Based Routing** - Each command handles appropriate phases
4. **Orchestration Layer** - `phase-management` skill coordinates all workflows
5. **One Skill Per Phase** - Focused responsibilities per phase
6. **Persistence Layer** - `plan-files` handles all file I/O
7. **Pattern Consistency** - Follows adr-management and interface-management patterns
8. **Lifecycle Management** - List, cleanup, and manage plans effectively

---

**Related Documents**:
- [Plan Types](plan-types.md) - Init phase router and configuration
- [Phase Management](phase-management.md) - Orchestration skill with both workflows
- [Templates & Workflow](templates-workflow.md) - Phase-based workflow and templates
- [API Specification](api.md) - Complete operation reference
- [Migration Plan](updated-plan/migration.md) - Implementation checklist

**Implemented Skills** (in `cui-task-workflow/skills/`):
- `phase-management` (orchestration)
- `plan-init`, `plan-refine`, `plan-implement`, `plan-verify`, `plan-finalize`, `plan-files`
