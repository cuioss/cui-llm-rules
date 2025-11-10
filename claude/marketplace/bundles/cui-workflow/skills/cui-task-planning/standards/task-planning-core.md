# Task Planning Core Standards

Common elements, concepts, and patterns that apply to all task planning use cases.

## Purpose

This document defines the foundational concepts and patterns used across all task planning approaches:
- Project Planning (long-term, project-wide)
- Issue Planning (short-term, single-issue)
- Refactoring Planning (ongoing, categorized improvements)

## Core Concepts

### What is a Task?

A **task** is a discrete unit of work that:
- Has a clear, actionable objective
- Can be implemented independently (or with explicit dependencies)
- Has measurable completion criteria
- Can be tracked through status indicators
- Maintains traceability to requirements, specifications, or issues

### Task Lifecycle

```
Created → In Progress → Completed
           ↓
        Blocked/Partial
```

Every task progresses through states tracked by status indicators.

## Status Indicators

### Standard Status Markers

All task planning uses checkbox notation for status tracking:

**`[ ]` - Not Started or In Progress**
- Task has not been started yet, OR
- Task is currently being worked on
- Use this as the default state for active work

**`[x]` - Completed**
- Task has been fully implemented
- All acceptance criteria met
- Verification passed
- Changes committed

### Extended Status Markers

Some use cases support additional status markers:

**`[~]` - Partially Completed**
- Task is partially done but needs more work
- Some acceptance criteria met, others pending
- Use when significant progress made but not complete
- Available in: Project Planning

**`[!]` - Blocked**
- Task cannot proceed due to external dependency
- Waiting for decisions, resources, or other tasks
- Blocker should be documented in notes
- Available in: Project Planning

### Status Progression Rules

**Sequential progression:**
```
[ ] → [x]           # Simple completion
[ ] → [~] → [x]     # Partial then complete
[ ] → [!] → [ ] → [x]  # Blocked then unblocked then complete
```

**Never reverse completion:**
```
[x] → [ ]           # ❌ DON'T reopen completed tasks
                    # ✅ DO create new task if needed
```

## Task Elements

### Core Fields

Every task, regardless of use case, should include:

**1. Task Identifier (Optional but Recommended)**
- Unique reference for the task
- Enables commit message integration
- Supports cross-referencing
- Format varies by use case

**2. Task Title**
- Concise, action-oriented description
- Start with verb (Implement, Add, Fix, Update, etc.)
- Specific enough to understand scope
- Example: "Implement token validation logic"

**3. Status Indicator**
- Required: `[ ]` or `[x]`
- Optional: `[~]` or `[!]` where supported

**4. Task Description**
- What needs to be done
- Scope and boundaries
- Key requirements

### Extended Fields

Use cases may add additional fields:

**Priority** (Refactoring Planning)
- High, Medium, or Low
- Guides implementation order

**Goal** (Issue Planning)
- What success looks like
- Expected outcome

**Rationale** (Refactoring Planning)
- Why this task is important
- Context and motivation

**Acceptance Criteria** (Issue Planning)
- Specific, measurable success conditions
- Test-like assertions

**References** (All use cases)
- Links to requirements, specs, issues
- Related code or documentation
- Dependencies on other tasks

**Checklist** (Issue Planning)
- Step-by-step verification
- Quality checks
- Build and test requirements

**Notes** (All use cases)
- Additional context
- Decisions needed
- Important considerations

## Traceability Patterns

### Purpose of Traceability

Every task should trace to its source:
- **Requirements** - Business need or functional requirement
- **Specification** - Technical design or implementation guidance
- **Issue** - GitHub issue or bug report
- **Refactoring Need** - Code improvement opportunity

### Link Formats

**To Requirements:**
```
See Requirement JWT-1: Token Validation Framework in Requirements.adoc
```

**To Specifications:**
```
See doc/specification/token-validation.adoc for implementation details
```

**To GitHub Issues:**
```
Issue Reference: https://github.com/cuioss/cui-java-tools/issues/4
```

**To Code:**
```
Related Code: src/main/java/com/example/TokenValidator.java
```

### Multiple References

When tasks relate to multiple sources:
```
References:
- Requirement JWT-1: Token Validation Framework
- Specification: doc/specification/token-validation.adoc lines 45-78
- Issue: #234 - Add retry logic
```

## Format Guidelines

### AsciiDoc vs Markdown

**Use AsciiDoc when:**
- Creating project-wide documentation (doc/TODO.adoc)
- Integrating with existing AsciiDoc documentation
- Need advanced features (cross-references, includes)
- Long-term, comprehensive planning documents

**Use Markdown when:**
- Creating agent-generated plans
- Quick, lightweight task lists
- GitHub issue integration
- Single-file, self-contained plans

**Both formats are valid** - choose based on context and tooling.

### Document Structure

**Header Section:**
- Document title
- Overview/purpose
- Scope statement
- Status indicators reference (if extended markers used)

**Task Sections:**
- Group related tasks
- Use hierarchical headings
- Maintain consistent structure

**Completion Section:**
- Overall completion criteria
- Verification requirements
- Next steps or follow-up

## Quality Standards

### Task Clarity

**Clear:** "Implement JWT signature validation using RS256 algorithm"

**Unclear:** "Fix token stuff"

Every task should be immediately understandable without additional context.

### Task Actionability

**Actionable:** "Add unit tests for TokenValidator with 80% coverage"

**Not Actionable:** "Think about testing strategy"

Every task should be something that can be directly implemented.

### Task Granularity

**Right-sized:**
- Can be completed in reasonable time (hours to days, not weeks)
- Has clear start and end
- Produces tangible result

**Too Large:** "Implement entire authentication system"
- Break into smaller tasks

**Too Small:** "Add opening brace to method"
- Combine with related work

### Task Independence

**Independent:** "Implement configuration loading" (can be done standalone)

**Dependent:** "Test configuration loading" (requires configuration to be implemented)

Mark dependencies explicitly when tasks must be done in order.

## Progress Tracking

### Completion Percentage

Calculate by counting completed tasks:

```
Completion = (Completed Tasks / Total Tasks) × 100%
```

Example: 15 completed out of 45 tasks = 33% complete

### Status Distribution

Track task status distribution:
- Not started: 20 tasks
- In progress: 5 tasks
- Partially complete: 3 tasks
- Blocked: 2 tasks
- Completed: 15 tasks

### Velocity Tracking

Monitor tasks completed per time period:
- Tasks per week
- Tasks per sprint
- Trend analysis

## Common Patterns

### Pattern 1: Sequential Tasks with Dependencies

```
Task 1: Implement data model
  [ ] Create entity classes
  [ ] Define relationships

Task 2: Implement repository layer (depends on Task 1)
  [ ] Create repository interfaces
  [ ] Implement queries

Task 3: Implement service layer (depends on Task 2)
  [ ] Create service classes
  [ ] Add business logic
```

### Pattern 2: Parallel Tasks by Area

```
Authentication Area:
  [ ] Implement login
  [ ] Implement logout
  [ ] Implement session management

Authorization Area:
  [ ] Implement role checking
  [ ] Implement permission verification
  [ ] Add access control
```

### Pattern 3: Categorized Improvements

```
Code Structure (C):
  C1. [ ] Extract common utilities
  C2. [ ] Refactor large classes
  C3. [ ] Remove code duplication

Performance (P):
  P1. [ ] Optimize database queries
  P2. [ ] Add caching layer
```

## Anti-Patterns to Avoid

### Avoid: Vague Tasks

❌ "Improve code quality"

✅ "Extract common validation logic into ValidationUtils class"

### Avoid: Missing Status

❌ Forgetting to update checkboxes

✅ Mark completed tasks immediately

### Avoid: Lost Traceability

❌ Tasks without links to requirements or issues

✅ Every task group references its source

### Avoid: Stale Plans

❌ Never updating task lists

✅ Update after each completion, review regularly

### Avoid: Overly Detailed

❌ Breaking down to individual lines of code

✅ Keep tasks at feature/component level

## Integration with Development Workflow

### Commit Messages

Reference tasks in commit messages:

**With Task IDs:**
```
refactor: C1. Extract common utilities

Extracted validation logic into ValidationUtils class
for reuse across components.
```

**With Task Numbers:**
```
feat: Task 3 - Implement service layer

Added UserService with business logic for
authentication and authorization.
```

### Pull Requests

Link PRs to tasks:
- Reference task identifiers in PR description
- Check off completed tasks in plan documents
- Update status after PR merge

### Code Reviews

Use tasks for review tracking:
- Review comments reference tasks
- Create new tasks for review findings
- Mark tasks as completed when addressed

## Related Concepts

**Task** vs **Requirement** vs **Specification**:
- **Requirement:** What the system must do (business need)
- **Specification:** How the system should be built (technical design)
- **Task:** Discrete implementation work (action item)

**Task** vs **Issue** vs **Story**:
- **Issue:** Problem to solve or enhancement request
- **Story:** User-centric functionality description
- **Task:** Implementation-level work item

## Summary

This document provides the foundation for all task planning in CUI projects. The three specialized use cases (Project Planning, Issue Planning, Refactoring Planning) extend these core concepts with additional structure and requirements specific to their contexts.

Key takeaways:
- Use status indicators consistently
- Maintain traceability to sources
- Keep tasks clear, actionable, and right-sized
- Update status as work progresses
- Choose appropriate format (AsciiDoc vs Markdown) for context
