# Plan Types (Init Phase Router)

The init phase determines the entire plan workflow. Each **plan type** is an **init-phase implementation** that:
1. Detects and configures the environment
2. Produces the complete phase structure for the plan
3. Transitions to the next phase automatically

**Skill**: `plan-init` (cui-task-workflow) - First of 5 phase skills, handles init phase with type routing

**All Phase Skills**: plan-init → plan-refine → plan-implement → plan-verify → plan-finalize

**Key Insight**: Selecting a plan type = executing that type's init phase = producing the plan structure.

---

## Init Phase Decision Tree

**MANDATORY**: Select init implementation based on input and execute IMMEDIATELY.

### If type = "implementation" or issue provided
→ **EXECUTE** [Implementation Init](plan-init/implementation.md)

### If type = "simple" or no-workflow flag
→ **EXECUTE** [Simple Init](plan-init/simple.md)

### If build files detected (pom.xml, package.json, etc.)
→ **EXECUTE** [Implementation Init](plan-init/implementation.md)

### If on feature/fix/task branch
→ **EXECUTE** [Implementation Init](plan-init/implementation.md)

### If nothing indicates implementation
→ **ASK USER** for plan type selection

---

## Available Plan Types (Init Implementations)

| Plan Type | Init Output | Phases Produced | Finalizing |
|-----------|-------------|-----------------|------------|
| [Implementation](plan-init/implementation.md) | Full dev workflow | 5 (init→refine→implement→verify→finalize) | PR via `/pr-fix` |
| [Simple](plan-init/simple.md) | Lightweight workflow | 3 (init→execute→finalize) | Commit only |

---

## Init Phase Execution Model

```
/task-plan invoked
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│ INIT PHASE                                                  │
│                                                             │
│   1. Determine plan type (decision tree above)              │
│   2. Load init implementation (progressive disclosure)      │
│   3. Execute init tasks:                                    │
│      - Detect environment (branch, build system, issue)     │
│      - Configure properties                                 │
│      - User confirmation                                    │
│   4. OUTPUT: Complete plan.md with all phases               │
│   5. Automatic transition to next phase                     │
└─────────────────────────────────────────────────────────────┘
        │
        │ Init produces different phase structures:
        │
        ├─────────────────────────────────────┐
        │                                     │
        ▼                                     ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ Implementation Output   │     │ Simple Output           │
│                         │     │                         │
│ Phases produced:        │     │ Phases produced:        │
│ ✓ init (completed)      │     │ ✓ init (completed)      │
│ → refine (3 tasks)      │     │ → execute (dynamic)     │
│   implement (dynamic)   │     │   finalize (2 tasks)    │
│   verify (4 tasks)      │     │                         │
│   finalize (3 tasks)    │     │                         │
└─────────────────────────┘     └─────────────────────────┘
```

---

## Init Phase Responsibilities

The init phase (regardless of type) is responsible for:

| Responsibility | Description |
|----------------|-------------|
| **Environment Detection** | Branch, build system, issue URL |
| **Configuration** | Set all plan properties with defaults |
| **User Confirmation** | Present config, allow overrides |
| **Plan Creation** | Write plan.md with complete phase structure |
| **Reference Setup** | Initialize references.md |
| **Transition** | Mark init complete, start next phase |

---

## Plan Type Selection Logic

### When `/task-plan` is Called

```python
def determine_plan_type(params, environment):
    # 1. Explicit type parameter
    if params.type:
        return params.type

    # 2. Issue provided → Implementation
    if params.issue:
        return "implementation"

    # 3. Build system detected → Implementation
    if environment.has_build_files():
        return "implementation"

    # 4. On feature branch → Implementation
    branch = environment.current_branch
    if branch and branch.startswith(('feature/', 'fix/', 'task/', 'claude/')):
        return "implementation"

    # 5. Nothing indicates implementation → Ask user
    return ask_user_plan_type()
```

### User Selection Prompt

When plan type cannot be determined:

```
Select plan type:

1. Implementation
   Full development workflow producing 5 phases:
   init → refine → implement → verify → finalize

   Features:
   - Branch management (feature/fix/task)
   - Issue tracking (GitHub/GitLab/Jira)
   - Build verification (Maven/npm)
   - PR workflow (/pr-fix)

2. Simple
   Lightweight workflow producing 3 phases:
   init → execute → finalize

   Features:
   - Any branch (including main)
   - No issue tracking
   - No build verification
   - Commit only (no PR)

Enter selection (1 or 2):
```

---

## Progressive Disclosure

**Load ONE init implementation per plan** (not both):

| Selection | Load |
|-----------|------|
| Implementation | `plan-init/implementation.md` (~350 lines) |
| Simple | `plan-init/simple.md` (~200 lines) |

**Context Efficiency**: ~300 lines per type vs ~550 lines if loading everything.

---

## Common Configuration Persistence

Both init implementations persist to the same locations.

### In plan.md Header

```markdown
# Task Plan: {task_title}

**Current Phase**: {next_phase_after_init}
**Current Task**: task-1
**Plan Type**: {Implementation|Simple}

## Configuration

| Property | Value |
|----------|-------|
| Branch | {branch} |
| Issue | {issue_link or "none"} |
| Build System | {build_system} |
| Technology | {technology} |
| Compatibility | {compatibility} |
| Commit Strategy | {commit_strategy} |
| Finalizing | {finalizing} |
```

### In references.md (Implementation only)

```markdown
## Issue and Branch

**Issue**: [{issue_id}: {issue_title}]({issue_url})
**Branch**: `{branch}`
**Base Branch**: `main`
```

---

## Property Summary by Plan Type

### Implementation Init Properties

| Property | Required | Default |
|----------|----------|---------|
| Branch | Yes | Current if feature branch |
| Issue | Recommended | None |
| Build System | Yes | Auto-detect |
| Technology | Yes | Derived |
| Compatibility | No | `deprecations` |
| Commit Strategy | No | `fine-granular` |
| Finalizing | No | `pr-workflow` |

**Full details**: [plan-init/implementation.md](plan-init/implementation.md)

### Simple Init Properties

| Property | Required | Default |
|----------|----------|---------|
| Branch | Yes | Current or main |
| Build System | No | `none` |
| Technology | No | `none` |
| Compatibility | No | `breaking` |
| Commit Strategy | No | `fine-granular` |
| Finalizing | No | `commit-only` |

**Full details**: [plan-init/simple.md](plan-init/simple.md)

---

## Plan Type Comparison

| Aspect | Implementation | Simple |
|--------|----------------|--------|
| **Use Case** | Code development | Documentation, config |
| **Init Tasks** | 5 | 2 |
| **Phases Produced** | 5 (init→refine→implement→verify→finalize) | 3 (init→execute→finalize) |
| **Total Tasks** | ~18+ | ~6 |
| **Branch** | Feature branch required | Any branch OK |
| **Issue** | Recommended | Not used |
| **Build System** | Auto-detected | None |
| **PR Workflow** | Yes (`/pr-fix`) | No |
| **User Interaction** | Full confirmation | Minimal |

---

## External Resources

### Init Implementations (plan-init/)

| File | Purpose | Init Tasks | Phases Produced |
|------|---------|------------|-----------------|
| `implementation.md` | Full dev workflow | 5 | 5 |
| `simple.md` | Lightweight workflow | 2 | 3 |

### Related Documents

- [Refine Phase](plan-refine/refine.md) - Refine phase specification (follows init)
- [Implement Phase](plan-implement/implement.md) - Implement phase specification (follows refine)
- [Verify Phase](plan-verify/verify.md) - Verify phase specification (follows implement)
- [Finalize Phase](plan-finalize/finalize.md) - Finalize phase specification (follows verify)
- [Architecture](architecture.md) - Overall abstraction design
- [Persistence](plan-files/persistence.md) - File format specifications
- [Templates & Workflow](templates-workflow.md) - Phase-based workflow
- [API Specification](api.md) - Skill API with create operation
- [Implementation Plan](plan.md) - Implementation tasks

---

## Adding New Plan Types

To add a new plan type (init implementation):

1. Create `plan-init/{name}.md` with:
   - Properties table (required/default/detection)
   - Init tasks (what happens during init)
   - Phase structure template (what init produces)
   - Example configuration

2. Add to decision tree in this file

3. Add to plan type comparison table

4. Update plan.md with implementation tasks
