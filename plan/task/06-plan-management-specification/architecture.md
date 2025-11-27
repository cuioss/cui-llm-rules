# Plan Management Architecture

## Overview

The plan management system follows the **abstraction layer pattern** used consistently across documentation skills in the CUI ecosystem. This pattern isolates implementation details behind a clean API, allowing evolution without breaking callers.

## Abstraction Layer

The plan management system uses **one skill per phase** to maximize separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                   COMMANDS                          │
│  /task-plan, /task-implement                       │
└────────────────────┬────────────────────────────────┘
                     │ (delegates via TOON handoff)
                     ▼
┌─────────────────────────────────────────────────────┐
│              PHASE SKILLS                           │
│           (cui-task-workflow)                       │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ plan-init                                    │   │
│  │ • Create plan with type routing              │   │
│  │ • Environment detection, user confirmation   │   │
│  │ • Produces phase structure                   │   │
│  └──────────────────┬──────────────────────────┘   │
│                     ▼                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ plan-refine                                  │   │
│  │ • Analyze requirements                       │   │
│  │ • Plan implementation tasks                  │   │
│  │ • Identify documentation needs               │   │
│  └──────────────────┬──────────────────────────┘   │
│                     ▼                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ plan-implement                               │   │
│  │ • Execute implementation tasks               │   │
│  │ • Delegate to language agents                │   │
│  │ • Track implementation progress              │   │
│  └──────────────────┬──────────────────────────┘   │
│                     ▼                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ plan-verify                                  │   │
│  │ • Run builds and tests                       │   │
│  │ • Code quality checks                        │   │
│  │ • Documentation review                       │   │
│  └──────────────────┬──────────────────────────┘   │
│                     ▼                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ plan-finalize                                │   │
│  │ • Commit changes                             │   │
│  │ • Create/update PR                           │   │
│  │ • Handle PR workflow                         │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ (file I/O)
                     ▼
┌─────────────────────────────────────────────────────┐
│              FILE SYSTEM                            │
│    .claude/plans/{task-name}/                      │
│      ├── plan.md                                    │
│      └── references.md                              │
└─────────────────────────────────────────────────────┘
```

### One-Skill-Per-Phase Architecture

| Skill | Phase | Key Responsibilities |
|-------|-------|---------------------|
| **plan-init** | init | Create plan, environment detection, type routing, produce structure |
| **plan-refine** | refine | Analyze requirements, plan tasks, identify ADRs/interfaces needed |
| **plan-implement** | implement | Execute tasks, delegate to language agents, track progress |
| **plan-verify** | verify | Run builds, quality checks, testing, documentation review |
| **plan-finalize** | finalize | Commit changes, create PR, handle PR workflow via `/pr-fix` |

### Key Principles

1. **One Skill Per Phase**: Each phase has dedicated skill with focused responsibilities
2. **Sequential Handoff**: Each skill completes and hands off to next phase skill
3. **Self-Contained**: Each phase skill reads plan, executes, updates progress, transitions
4. **Progressive Disclosure**: Only load the skill needed for current phase
5. **No Direct File Access**: Commands delegate to phase skills for all plan I/O
6. **TOON Handoff Protocol**: All communication via token-efficient TOON format

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

**Benefits Over Single File**:
- ✅ Easier reference management
- ✅ Cleaner separation (tasks vs references)
- ✅ Extensible without format changes
- ✅ Better for version control (smaller diffs)

## Benefits of Abstraction

### 1. Location Flexibility

**Current**: `.claude/plans/`

**Future Options**:
- `target/plans/` (project-specific)
- `docs/plans/` (documentation directory)
- Remote storage (API-based)
- Database-backed storage

**Change Impact**: Update skill only, all callers unchanged

### 2. Format Evolution

**Current**: Markdown with phase-based structure

**Future Options**:
- Enhanced Markdown with YAML frontmatter
- JSON format for machine processing
- AsciiDoc for richer formatting
- Hybrid formats (Markdown + JSON metadata)

**Change Impact**: Update skill only, API unchanged

### 3. Phase-Based Workflow Management

**Current**: 5 sequential phases with automatic tracking

Phases:
- **init**: Setup and initialization tasks
- **refine**: Iterative plan refinement
- **implement**: Implementation tasks
- **verify**: Testing and verification tasks
- **finalize**: Documentation and completion tasks

**Benefits**:
- Structured workflow progression
- Automatic phase transition rules
- Helper fields (current_phase, current_task) for simplified model interaction
- Phase Progress Table for quick overview
- Sequential execution enforcement
- Completion validation at phase level

See [Templates & Workflow](templates-workflow.md) for complete phase specification.

### 4. Reference Management Integration

**Current**: Separate references.md with skill abstractions

**Integration Points**:
- `adr-management` skill: Verify/create ADRs before adding references
- `interface-management` skill: Verify/create interfaces before adding references
- GitHub API: Validate issue URLs
- Git: Validate branch names

**Benefits**:
- Centralized reference tracking
- Cross-document validation
- Automatic link verification
- Skill-based reference creation

See [Persistence](plan-files/persistence.md#references-file-format) for reference structure.

### 5. Additional Features

**Can Add Without Breaking Callers**:
- Plan versioning (git integration)
- Plan templates by project type
- Automated validation rules
- Plan metrics and analytics
- Plan search and indexing
- Custom phase definitions per project type
- Plan dependencies and prerequisites
- Multi-language plans

### 6. Consistent Interface

**All Plan Operations** follow same pattern:
- TOON handoff input
- File I/O via tools (Bash, Read, Write, Edit)
- TOON handoff output
- Error handling
- Validation

**Operation Template**:
```toon
# Input
from: caller
to: task-plan-skill
handoff_id: op-001
workflow: operation-name

task:
  description: Operation description
  type: operation_type
  status: pending

artifacts:
  plan_directory: .claude/plans/{task-name}/

next_action: Perform operation

# Output
from: task-plan-skill
to: caller
handoff_id: op-002
workflow: operation-name

task:
  description: Operation complete
  status: completed

artifacts:
  plan_directory: .claude/plans/{task-name}/

next_action: Next step
```

See [API Specification](api.md) for complete operation details.

## Error Handling

The abstraction layer provides consistent error handling across all operations.

### Error Types

1. **File Not Found**
   - Plan directory doesn't exist
   - Individual files missing (plan.md, references.md)

2. **Invalid Format**
   - Missing required sections
   - Malformed Markdown
   - Invalid phase structure

3. **Validation Failures**
   - Missing acceptance criteria
   - Invalid phase transitions
   - Incomplete task definitions

### Error Handoff Format

```toon
from: task-plan-skill
to: caller
handoff_id: error-001

task:
  status: failed

error:
  type: error_type
  message: Human-readable error message
  details: Extended error details

alternatives[N]:
- Alternative approach 1
- Alternative approach 2

next_action: How to resolve
```

### Common Error Scenarios

**File Not Found**:
```toon
error:
  type: file_not_found
  message: Plan directory not found
  details: .claude/plans/jwt-auth/ does not exist

alternatives[2]:
- Create new plan with /task-plan
- Check directory path and try again
```

**Invalid Format**:
```toon
error:
  type: invalid_format
  message: Plan file format invalid
  details: Missing required sections: Overview, Phase Progress

next_action: Regenerate plan or fix manually
```

**Validation Failures**:
```toon
error:
  type: validation_failed
  message: Plan validation incomplete

validation_results:
  quality_score: 60
  issues_count: 3

issues[3]:
- Missing acceptance criteria in Task 2
- No dependencies specified
- Incomplete task descriptions

next_action: Address validation issues before implementation
```

## Comparison with Other Patterns

### vs. Direct File Operations

**Without Abstraction** (❌):
```markdown
# In command:
1. Read file with Read tool
2. Parse Markdown manually
3. Extract tasks with regex
4. Update status manually
5. Write file with Edit tool
```

**With Abstraction** (✅):
```markdown
# In command:
1. Generate TOON handoff to task-plan skill
2. Receive structured response
```

**Benefits**:
- ✅ 80% less code in callers
- ✅ Consistent parsing logic
- ✅ Centralized validation
- ✅ Easier testing

### vs. Embedded Logic

**Without Abstraction** (❌):
- Plan parsing duplicated across commands/agents
- Format changes require updates in 10+ places
- No consistent validation

**With Abstraction** (✅):
- Plan parsing in single skill
- Format changes in one place
- Consistent validation for all callers

## Summary

The plan management abstraction provides:

1. ✅ **Clear Abstraction** - Single skill for all plan operations
2. ✅ **Consistent Interface** - TOON handoff API throughout
3. ✅ **Directory Structure** - Organized with plan.md + references.md
4. ✅ **Pattern Consistency** - Follows adr-management and interface-management patterns
5. ✅ **Location Flexibility** - Can change storage without breaking callers
6. ✅ **Format Evolution** - Can enhance format without breaking API
7. ✅ **Reference Integration** - Seamless integration with other documentation skills
8. ✅ **Error Handling** - Comprehensive error scenarios defined
9. ✅ **Extensibility** - Easy to add features without breaking existing functionality

---

**Related Documents**:
- [Refine Phase](plan-refine/refine.md) - Refine phase specification
- [Implement Phase](plan-implement/implement.md) - Implement phase specification
- [Verify Phase](plan-verify/verify.md) - Verify phase specification
- [Finalize Phase](plan-finalize/finalize.md) - Finalize phase specification
- [Persistence](plan-files/persistence.md) - File structure and directory organization
- [Templates & Workflow](templates-workflow.md) - Phase-based workflow and templates
- [API Specification](api.md) - Complete operation reference
- [Decomposition](decomposition.md) - Implementation guidance
