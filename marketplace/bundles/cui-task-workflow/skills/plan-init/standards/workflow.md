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

### Quick Decision Guide

| Task Characteristic | Template | Reason |
|---------------------|----------|--------|
| Updates to `marketplace/bundles/` | Plugin-Development | Built-in `/plugin-doctor` verification |
| Creates/modifies agents, commands, skills | Plugin-Development | Marketplace-aware workflow |
| Involves maven/gradle/npm builds | Implementation | Requires build/test verification |
| Has GitHub issue reference | Implementation | Full tracking workflow |
| Pure documentation updates | Simple | Minimal overhead |
| Configuration file changes | Simple | No build verification needed |
| Quick fixes without tests | Simple | Streamlined execution |

### Decision Tree Rules

**1. If type = "implementation" or issue provided**
→ **EXECUTE** Implementation Init (5-phase workflow)

**2. If type = "simple" or no-workflow flag**
→ **EXECUTE** Simple Init (3-phase workflow)

**3. If type = "plugin-development" or marketplace component work detected**
→ **EXECUTE** Plugin Development Init (3-phase workflow with verification)

**4. If task involves marketplace/bundles/ paths**
→ **EXECUTE** Plugin Development Init

**5. If task mentions creating/modifying agents, commands, or skills**
→ **EXECUTE** Plugin Development Init

**6. If build files detected (pom.xml, package.json, etc.) AND task involves code**
→ **EXECUTE** Implementation Init

**7. If on feature/fix/task/claude branch AND task involves code**
→ **EXECUTE** Implementation Init

**8. If nothing indicates implementation**
→ **ASK USER** for plan type selection

### Key Decision Factors

**Use Plugin-Development when**:
- Task path includes `marketplace/bundles/`
- Task description mentions skill, command, agent, or plugin modifications
- Task involves marketplace component verification needs
- Changes affect skill SKILL.md files or command *.md files

**Use Implementation when**:
- Task requires maven, gradle, or npm build execution
- Task involves Java, JavaScript, or other compiled code
- Task has a GitHub issue for tracking
- Task requires unit test execution or coverage verification

**Use Simple when**:
- Task is pure documentation (AsciiDoc, Markdown, README)
- Task involves configuration files without code impact
- Task is a quick fix that doesn't need build verification
- Task doesn't involve any build system

### Config Property Guidance

| Scenario | compatibility | finalizing |
|----------|---------------|------------|
| API changes | `breaking` | `pr-workflow` |
| File path changes | `breaking` | `commit-only` or `pr-workflow` |
| New features (backward-compatible) | `deprecations` | `pr-workflow` |
| Marketplace updates | `breaking` | `commit-only` |
| Documentation only | `breaking` | `commit-only` |

**Note**: `finalizing: commit-only` is appropriate when `/plugin-doctor` handles verification (plugin-development plans) or when external review isn't needed.

### Examples

**Example 1: Marketplace Skill Update**
```
Task: "Update plan-init skill to improve template selection"
Path contains: marketplace/bundles/cui-task-workflow/skills/plan-init
Decision: Plugin-Development (marketplace component)
Config: compatibility=breaking, finalizing=commit-only
```

**Example 2: Java Feature Implementation**
```
Task: "Add JWT validation to authentication service"
Build files: pom.xml detected
Decision: Implementation (requires maven build/test)
Config: compatibility=deprecations, finalizing=pr-workflow
```

**Example 3: Documentation Update**
```
Task: "Update README with new installation steps"
Build files: none relevant
Path: docs/ or README.md
Decision: Simple (no build verification needed)
Config: compatibility=breaking, finalizing=commit-only
```

**Example 4: Cross-Cutting Change**
```
Task: "Rename .claude/ directory to .cui/ across all skills"
Path contains: marketplace/bundles/
Decision: Plugin-Development (marketplace-wide change)
Config: compatibility=breaking (paths change), finalizing=commit-only
```

## Available Plan Types

| Plan Type | Phases Produced | Use Case |
|-----------|-----------------|----------|
| Implementation | 5 (init→refine→implement→verify→finalize) | Code development |
| Simple | 3 (init→execute→finalize) | Documentation, config |
| Plugin-Development | 4 (init→refine→execute→finalize) | Marketplace components with `/plugin-doctor` verification |

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

### Plugin-Development (4 phases)
- init: 2 tasks (detect environment, confirm configuration)
- refine: 4 tasks (assess complexity, strategic analysis, component breakdown, generate implementation-requirements.md)
- execute: dynamic (based on components to add/modify) + verification sub-tasks
- finalize: 3 tasks (verify all components, commit, verify completion)

**Refine Phase Artifacts** (same as Implementation plan):
- `analysis.md` (optional) - Created for complex tasks with design decisions
- `implementation-requirements.md` - Always created with task details and guidance

**Refine Phase Purpose**:
- Assess complexity and decide if analysis.md is needed
- Document design decisions and trade-offs (if complex)
- Analyze existing components for patterns and conventions
- Generate implementation-requirements.md with detailed tasks

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
