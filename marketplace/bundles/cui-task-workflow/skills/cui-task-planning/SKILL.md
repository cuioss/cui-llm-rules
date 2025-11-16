---
name: cui-task-planning
description: Comprehensive task planning and tracking standards for project planning, issue implementation, and refactoring workflows
allowed-tools: []
standards:
  - standards/task-planning-core.md
  - standards/project-planning-standards.md
  - standards/issue-planning-standards.md
  - standards/refactoring-planning-standards.md
---

# CUI Task Planning Skill

Comprehensive standards for creating, organizing, and tracking tasks across all planning scenarios in CUI projects.

## What This Skill Provides

This skill provides unified task planning standards for three distinct use cases:

### 1. Project Planning (Long-Term)
- Project-wide TODO lists (doc/TODO.adoc)
- Roadmap and backlog tracking
- Hierarchical organization by component/feature/phase
- Extended status indicators (partial, blocked)
- Strong requirements traceability
- **Use when:** Planning entire projects over months/years

### 2. Issue Planning (Short-Term)
- Single-issue implementation plans (plan-issue-X.md)
- Sequential task execution
- Clear acceptance criteria per task
- Agent-friendly format for task-executor
- GitHub issue integration
- **Use when:** Implementing single GitHub issues or features

### 3. Refactoring Planning (Ongoing)
- Categorized improvement tracking (Refactorings.adoc)
- Task identifiers for commit messages (C1, P2, S3, etc.)
- Priority assignment (High/Medium/Low)
- Technical debt reduction
- Performance/security enhancements
- **Use when:** Tracking ongoing code improvements

## When to Activate This Skill

Use this skill when:

**Creating Plans:**
- Generating project TODO lists
- Breaking down GitHub issues into tasks
- Organizing refactoring efforts
- Planning feature implementations
- Tracking technical debt

**Reviewing Plans:**
- Validating plan structure
- Ensuring proper traceability
- Checking status indicators
- Verifying task completeness

**Working with Agents:**
- task-breakdown-agent creating issue plans
- task-executor implementing from plans
- Any agent that generates or consumes task lists

## Workflow

### Step 0: Determine Use Case

**Decision tree:**

```
What am I planning?
│
├─> Entire project or major feature?
│   └─> Use Project Planning (doc/TODO.adoc)
│       Read: standards/project-planning-standards.md
│
├─> Single GitHub issue?
│   └─> Use Issue Planning (plan-issue-X.md)
│       Read: standards/issue-planning-standards.md
│
└─> Code improvements/refactoring?
    └─> Use Refactoring Planning (Refactorings.adoc)
        Read: standards/refactoring-planning-standards.md
```

### Step 1: Load Core Concepts

**Always load core standards first:**

```
Read: standards/task-planning-core.md
```

This provides:
- Status indicator definitions ([ ], [x], [~], [!])
- Task element structure
- Traceability patterns
- Quality standards
- Format guidelines (AsciiDoc vs Markdown)

### Step 2: Load Use-Case-Specific Standards

**Based on use case from Step 0:**

**For Project Planning:**
```
Read: standards/project-planning-standards.md
```

Get standards for:
- doc/TODO.adoc structure
- Hierarchical organization
- 4 status indicators
- Requirements traceability
- Testing organization
- Long-term maintenance

**For Issue Planning:**
```
Read: standards/issue-planning-standards.md
```

Get standards for:
- plan-issue-X.md format
- Sequential task structure
- Goal statements
- Acceptance criteria
- Verification checklists
- Agent-friendly format

**For Refactoring Planning:**
```
Read: standards/refactoring-planning-standards.md
```

Get standards for:
- Category-based organization (C, P, S, T, D, DOC, F)
- Task identifier format
- Priority assignment
- Description + Rationale structure
- Commit message integration

### Step 3: Apply Standards

Use loaded standards to:

1. **Structure tasks** according to use case format
2. **Apply status indicators** consistently
3. **Maintain traceability** to requirements/specs/issues
4. **Verify completeness** using quality checklists
5. **Track progress** appropriately for use case

## Standards Organization

```
standards/
  task-planning-core.md              # Core concepts (status, traceability, formats)
  project-planning-standards.md      # Long-term project planning
  issue-planning-standards.md        # Short-term issue implementation
  refactoring-planning-standards.md  # Categorized improvement tracking
```

**Hierarchical design:**
- Core concepts apply to ALL use cases
- Specialized standards extend core for specific contexts
- No duplication - each standard covers distinct aspects

## Tool Access

**No special tools required** - This skill uses standard Read tool to load markdown standards.

## Usage Examples

### Example 1: task-breakdown-agent Creating Issue Plan

```markdown
## Step 0: Load Task Planning Standards

```
Skill: cui-task-planning
```

This loads comprehensive task planning standards for issue implementation.

## Step 1: Apply Issue Planning Format

Follow issue-planning-standards.md to generate plan-issue-X.md with:
- Sequential tasks (Task 1, Task 2, ...)
- Goal statements
- Acceptance criteria
- Verification checklists
```

### Example 2: Creating Project TODO

```markdown
## Step 1: Load Task Planning Standards

```
Skill: cui-task-planning
```

## Step 2: Structure Project Planning Document

Follow project-planning-standards.md to create doc/TODO.adoc with:
- Hierarchical organization
- Requirements traceability
- Extended status indicators ([~], [!])
- Testing section
```

### Example 3: Organizing Refactoring Tasks

```markdown
## Step 1: Load Task Planning Standards

```
Skill: cui-task-planning
```

## Step 2: Create Refactoring Task List

Follow refactoring-planning-standards.md to organize tasks:
- Categories: C (Code), P (Performance), S (Security), etc.
- Task identifiers: C1, C2, P1, P2, etc.
- Priority assignment
- Commit message integration
```

## Integration with cui-task-workflow Bundle

This skill integrates with cui-task-workflow bundle components:

### Agents
- **task-breakdown-agent** - Loads this skill to generate issue plans
- **task-executor** - Consumes plans created using these standards
- **task-reviewer** - Validates tasks against standards

### Commands
- **orchestrate-workflow** - Orchestrates work using plan standards
- Any command that creates or consumes task lists

### Other Skills
- **cui-git-workflow** - Commit message format works with task identifiers
- Works alongside other workflow skills

## Cross-References

### To cui-requirements Bundle

The cui-requirements bundle has a **planning-documentation** skill that covers similar project planning concepts. Key differences:

- **planning-documentation** (cui-requirements) - Focuses on requirements/specification traceability context
- **cui-task-planning** (cui-task-workflow) - Focuses on implementation/execution context

Both are valid and serve different audiences. Use planning-documentation when working in requirements context, use cui-task-planning when working in implementation/workflow context.

### To standards/process/refactoring-process.adoc

The refactoring-process.adoc file documents the refactoring workflow process. Parts of it will become a command. This skill provides the **task structure standards** used within that process.

## Quality Verification

Standards in this skill ensure:

- [x] Self-contained (no external references except URLs)
- [x] All content in standards/ directory
- [x] Markdown format for compatibility
- [x] Comprehensive coverage of three use cases
- [x] Practical examples included
- [x] Clear decision guidance
- [x] Agent-friendly structure

## References

- Conventional Commits: https://www.conventionalcommits.org/ (for commit message integration)
- Task Management Best Practices: https://www.atlassian.com/agile/project-management/user-stories
