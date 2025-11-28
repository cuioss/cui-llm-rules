# Plan Init Workflow

## Phase Overview

The init phase determines the entire plan workflow:

```
/task-plan invoked
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ INIT PHASE                                          │
│                                                     │
│   1. Determine plan type (decision tree)            │
│   2. Load init implementation (progressive)         │
│   3. Execute init tasks:                            │
│      - Detect environment (branch, build, issue)    │
│      - Configure properties                         │
│      - User confirmation                            │
│   4. OUTPUT: Complete plan.md with all phases       │
│   5. Automatic transition to next phase             │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Next Phase (refine or execute)
```

## Plan Type Decision Tree

**MANDATORY**: Select init implementation based on input and execute IMMEDIATELY.

### If type = "implementation" or issue provided
→ **EXECUTE** Implementation Init (5-phase workflow)

### If type = "simple" or no-workflow flag
→ **EXECUTE** Simple Init (3-phase workflow)

### If type = "plugin-development" or marketplace component work detected
→ **EXECUTE** Plugin Development Init (3-phase workflow with verification)

### If task involves marketplace/bundles/ paths
→ **EXECUTE** Plugin Development Init

### If task mentions creating/modifying agents, commands, or skills
→ **EXECUTE** Plugin Development Init

### If build files detected (pom.xml, package.json, etc.)
→ **EXECUTE** Implementation Init

### If on feature/fix/task/claude branch
→ **EXECUTE** Implementation Init

### If nothing indicates implementation
→ **ASK USER** for plan type selection

## Available Plan Types

| Plan Type | Phases Produced | Use Case |
|-----------|-----------------|----------|
| Implementation | 5 (init→refine→implement→verify→finalize) | Code development |
| Simple | 3 (init→execute→finalize) | Documentation, config |
| Plugin-Development | 3 (init→execute→finalize) | Marketplace components with `/plugin-doctor` verification |

## Property Specifications

### Implementation Properties

| Property | Required | Default |
|----------|----------|---------|
| Branch | Yes | Current if feature branch |
| Issue | Recommended | None |
| Build System | Yes | Auto-detect |
| Technology | Yes | Derived from build |
| Compatibility | No | `deprecations` |
| Commit Strategy | No | `fine-granular` |
| Finalizing | No | `pr-workflow` |

### Simple Properties

| Property | Required | Default |
|----------|----------|---------|
| Branch | Yes | Current or main |
| Build System | No | `none` |
| Technology | No | `none` |
| Compatibility | No | `breaking` |
| Commit Strategy | No | `fine-granular` |
| Finalizing | No | `commit-only` |

### Plugin-Development Properties

| Property | Required | Default |
|----------|----------|---------|
| Branch | Yes | Current or main |
| Target Bundle | Yes | Auto-detect from path |
| Component Types | Yes | Auto-detect (agents, commands, skills) |
| Build System | No | `none` |
| Technology | No | `none` |
| Compatibility | No | `breaking` |
| Commit Strategy | No | `fine-granular` |
| Finalizing | No | `commit-only` |

## Phase Structure Templates

### Implementation (5 phases)
- init: 5 tasks (detect, fetch, validate, confirm, persist)
- refine: 3 tasks (analyze, plan-tasks, identify-docs)
- implement: dynamic (populated by refine phase)
- verify: 4 tasks (build, quality, manual, docs)
- finalize: 3 tasks (commit, pr, workflow)

### Simple (3 phases)
- init: 2 tasks (detect, confirm)
- execute: dynamic (based on task description)
- finalize: 2 tasks (commit, verify)

### Plugin-Development (3 phases)
- init: 2 tasks (detect environment, confirm configuration)
- execute: dynamic (based on components to add/modify) + verification sub-tasks
- finalize: 3 tasks (verify all components, commit, verify completion)

**Execute Phase Special Rules**:
- Each component task MUST include verification checklist item: `/plugin-doctor {type}={name}`
- After all implementation tasks, add explicit verification tasks for each component
- Finalize phase includes mandatory full verification pass

## Property Edit Prompts

### Branch
```
Enter target branch (current: {current}):
```

### Issue
```
Enter issue reference:
1. Enter issue URL
2. Enter issue identifier
3. Skip
```

### Build System
```
Select build system:
1. maven - Java/JVM with Maven
2. gradle - Java/JVM with Gradle
3. npm - JavaScript with npm
4. npx - JavaScript with npx scripts
5. none - No build system
```

### Technology
```
Select technology:
1. java - Java/JVM development
2. javascript - JavaScript/TypeScript
3. mixed - Both Java and JavaScript
4. none - No specific technology
```

### Compatibility
```
Select compatibility level:
1. deprecations (default) - Deprecate old APIs
2. breaking - Allow breaking changes
```

### Commit Strategy
```
Select commit strategy:
1. fine-granular (default) - After each task
2. phase-specific - End of each phase
3. complete - Single commit when done
```

### Finalizing
```
Select finalizing mode:
1. pr-workflow (default) - Full automation
2. manual-pr - Create PR only
3. commit-only - No PR creation
```
