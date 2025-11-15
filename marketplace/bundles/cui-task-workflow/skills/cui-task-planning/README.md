# CUI Task Planning Skill

Comprehensive task planning and tracking standards for all CUI projects.

## Overview

This skill provides unified standards for creating, organizing, and tracking tasks across three distinct planning scenarios:

1. **Project Planning** - Long-term, project-wide planning (months/years)
2. **Issue Planning** - Short-term, single-issue implementation (days/weeks)
3. **Refactoring Planning** - Ongoing, categorized improvements (continuous)

## What's Included

### Standards Files

**task-planning-core.md** - Foundational concepts for all planning
- Status indicator definitions ([ ], [x], [~], [!])
- Task element structure
- Traceability patterns
- Format guidelines (AsciiDoc vs Markdown)
- Quality standards

**project-planning-standards.md** - Long-term project planning
- doc/TODO.adoc structure
- Hierarchical organization strategies
- 4 status indicators including partial and blocked
- Requirements traceability
- Testing task organization
- Comprehensive example

**issue-planning-standards.md** - Short-term issue implementation
- plan-issue-X.md format
- Sequential task structure (Task 1, Task 2, ...)
- Goal statements and acceptance criteria
- Verification checklists
- Agent-friendly format for task-executor
- GitHub issue integration

**refactoring-planning-standards.md** - Ongoing improvement tracking
- Category-based organization (C, P, S, T, D, DOC, F)
- Task identifiers (C1, P2, S3, etc.)
- Priority assignment (High/Medium/Low)
- Description + Rationale structure
- Commit message integration

## Key Features

### Unified Core Concepts

All three planning approaches share:
- Standard status indicators
- Consistent traceability patterns
- Common task elements
- Quality verification

### Use-Case-Specific Extensions

Each planning approach adds:
- Specialized structure
- Context-appropriate fields
- Format recommendations
- Integration patterns

### Agent-Friendly Design

Standards are designed for:
- Agent generation of plans
- Agent consumption of plans
- Automated verification
- Tool integration

## Quick Decision Guide

**Choose Project Planning when:**
- Planning entire project or major feature
- Need hierarchical organization
- Tracking work over months/years
- Require partial/blocked status indicators
- Strong requirements traceability needed

**Choose Issue Planning when:**
- Implementing single GitHub issue
- Need sequential, step-by-step execution
- Working with task-executor agent
- Clear acceptance criteria required
- Short-term work (days to couple weeks)

**Choose Refactoring Planning when:**
- Tracking code improvements
- Need categorized organization
- Want task IDs for commit messages
- Managing technical debt
- Ongoing, continuous improvements

## Usage

### In Agents

```markdown
### Step 1: Load Task Planning Standards

```
Skill: cui-task-planning
```

### Step 2: Determine Use Case

Based on planning needs, load appropriate standards:
- Project Planning: standards/project-planning-standards.md
- Issue Planning: standards/issue-planning-standards.md
- Refactoring Planning: standards/refactoring-planning-standards.md
```

### In Commands

Commands that create plans should delegate to agents that load this skill.

## Integration

### With cui-task-workflow Bundle

**Agents:**
- **task-breakdown-agent** - Creates issue plans using issue-planning-standards
- **task-executor** - Implements tasks following plan format
- **task-reviewer** - Validates task completeness

**Commands:**
- **wf-orchestrate-task-workflow** - Orchestrates implementation using plans
- Any command creating or consuming task lists

**Skills:**
- **cui-git-workflow** - Commit messages reference task identifiers
- Works with other workflow skills

### With cui-requirements Bundle

The cui-requirements bundle has a **planning-documentation** skill for requirements-focused planning. This skill focuses on implementation/execution planning. Both are valid for different contexts.

## Status Indicators

### All Use Cases ([ ] and [x])

**Not Started/In Progress:**
```
- [ ] Implement feature
- [ ] Add tests
```

**Completed:**
```
- [x] Implement feature
- [x] Add tests
```

### Project Planning Only ([~] and [!])

**Partially Completed:**
```
- [~] Implement error handling (basic done, edge cases pending)
```

**Blocked:**
```
- [!] Add caching (waiting for Redis infrastructure)
```

## Task Identifier Formats

### Project Planning

No formal identifiers - uses hierarchical structure:
```
=== Core Components
==== Token Validator
* [ ] Implement interface
* [ ] Add validation
```

### Issue Planning

Sequential task numbers:
```
### Task 1: Add Configuration
### Task 2: Implement Logic
### Task 3: Add Tests
```

Optional short IDs for commits:
```
### Task 1 (T1): Add Configuration
```

### Refactoring Planning

Category-based identifiers:
```
C1. Extract Common Utilities
P2. Optimize Database Queries
S3. Fix Security Vulnerability
T4. Increase Test Coverage
```

## Examples

### Project Planning Example

```asciidoc
== Implementation Tasks

=== Token Validation
_See Requirement JWT-1 in link:Requirements.adoc[Requirements]_

* [x] Implement TokenValidator interface
* [x] Add signature validation
* [ ] Add expiration checking
* [ ] Implement clock skew tolerance
```

### Issue Planning Example

```markdown
### Task 1: Add RetryConfig Record

**Goal:** Create configuration record for retry behavior

**References:**
- Issue: Section "Configuration Requirements" (lines 15-23)
- Spec: doc/http-client/resilient-adapter.adoc lines 45-78

**Checklist:**
- [ ] Implement RetryConfig record
- [ ] Add unit tests (80%+ coverage)
- [ ] Update JavaDoc
- [ ] Run build and verify

**Acceptance Criteria:**
- RetryConfig record exists with all fields
- Builder pattern implemented
- Test coverage ≥ 80%
```

### Refactoring Planning Example

```asciidoc
C1. Extract Common Validation Logic
[ ] *Priority:* High

*Description:* Extract repeated validation logic from UserService,
OrderService, and PaymentService into ValidationUtils class.

*Rationale:* Reduces code duplication and ensures consistent
validation across services. Makes validation easier to test.
```

## Commit Message Integration

### Project Planning

```
feat(auth): implement token validation

Added TokenValidator interface and signature validation
following JWT-1 requirements.
```

### Issue Planning

```
feat: T1 - Add RetryConfig Record

Implemented configuration record for retry behavior
with builder pattern and validation.
```

### Refactoring Planning

```
refactor: C1. Extract common validation logic

Moved validation logic into ValidationUtils class
for reuse across services.
```

## Quality Standards

All planning formats ensure:
- Clear, actionable tasks
- Consistent status tracking
- Proper traceability
- Measurable completion
- Agent compatibility

## Migration Notes

### From planning-documentation.md

If using cui-requirements planning-documentation skill:
- Content is compatible
- Same core concepts
- Different context focus
- Can reference both

### From task-breakdown-agent embedded format

If task-breakdown-agent had embedded format:
- Now delegates to this skill
- Same structure maintained
- Enhanced with standards
- Better consistency

### From refactoring-process.adoc

Refactoring process document remains but references this skill for task structure standards.

## Bundle

Part of the **cui-task-workflow** bundle - Complete development workflow from issue to PR.

## See Also

- cui-git-workflow skill - Commit message standards
- cui-requirements bundle planning-documentation skill - Requirements-focused planning
- task-breakdown-agent - Creates plans using these standards
- task-executor - Implements plans following these standards
