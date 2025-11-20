# Refactoring Planning Standards

Standards for organizing and tracking categorized refactoring and improvement tasks.

## Purpose

Refactoring planning is designed for:
- Ongoing code improvements
- Technical debt reduction
- Performance optimizations
- Security enhancements
- Documentation improvements
- Dependency updates

## When to Use Refactoring Planning

Use this approach when:
- Tracking code improvements and refactoring
- Organizing technical debt reduction
- Managing security/performance enhancements
- Need categorized task organization
- Want task identifiers for commit messages
- Tracking ongoing improvements (not project-specific)

**Not appropriate for:**
- New feature implementation (use Issue Planning or Project Planning)
- Bug fixes from issues (use Issue Planning)
- Project-wide planning (use Project Planning)

## Document Structure

### File Format

Use AsciiDoc format for integration with project documentation:
```
Refactorings.adoc
ImprovementTasks.adoc
TechnicalDebt.adoc
```

Or use Markdown if preferred:
```
refactorings.md
improvements.md
technical-debt.md
```

### Document Header

```asciidoc
= Refactoring Tasks
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js
```

## Task Categories

### Standard Categories

Tasks are organized by category, each with its own prefix:

| Category | Prefix | Description | Examples |
|----------|--------|-------------|----------|
| **Code Structure** | C | Design improvements, refactoring | C1: Extract utilities, C2: Refactor large classes |
| **Performance** | P | Speed and efficiency | P1: Optimize queries, P2: Add caching |
| **Security** | S | Security enhancements | S1: Add input validation, S2: Fix vulnerabilities |
| **Testing** | T | Test improvements | T1: Increase coverage, T2: Add integration tests |
| **Dependency** | D | Dependency management | D1: Update libraries, D2: Remove unused deps |
| **Documentation** | DOC | Documentation improvements | DOC1: Add JavaDoc, DOC2: Update README |
| **Future** | F | Future enhancements | F1: New features, F2: Planned improvements |

### Custom Categories

Projects may add categories as needed:
- **I**: Infrastructure
- **A**: API improvements
- **UI**: User interface
- **DB**: Database optimization

**Rule:** Keep categories focused and non-overlapping.

## Task Structure

### Task Format

Each task follows this structure:

```asciidoc
[Category][Number]. [Task Title]
[ ] *Priority:* [High/Medium/Low]

*Description:* [Detailed description of what needs to be done]

*Rationale:* [Explanation of why this task is important]
```

### Example Tasks

```asciidoc
C1. Extract Common Validation Logic
[ ] *Priority:* High

*Description:* Extract repeated validation logic from UserService, OrderService, and PaymentService into a shared ValidationUtils class.

*Rationale:* Reduces code duplication and ensures consistent validation across services. Makes validation logic easier to test and maintain.
```

```asciidoc
P2. Add Redis Caching Layer
[ ] *Priority:* Medium

*Description:* Implement Redis caching for frequently accessed user profiles and configuration data. Add cache invalidation logic for data updates.

*Rationale:* Current database queries for user profiles account for 40% of response time. Caching will significantly improve performance under load.
```

```asciidoc
S3. Implement Rate Limiting
[x] *Priority:* High

*Description:* Add rate limiting to public API endpoints using token bucket algorithm. Configure limits per endpoint and user tier.

*Rationale:* Protects against DoS attacks and ensures fair resource usage. Required for production security compliance.
```

## Task Components

### Required Fields

1. **Task Identifier** - Format: `[Category][Number]`
   - Example: C1, P2, S3, T4, D5, DOC6, F7

2. **Task Title** - Brief, action-oriented description
   - Start with verb: Extract, Add, Implement, Update, etc.
   - Specific enough to understand scope

3. **Status Checkbox** - `[ ]` or `[x]`

4. **Priority** - High, Medium, or Low
   - High: Critical, blocking other work, security-related
   - Medium: Important, should be done soon
   - Low: Nice to have, can be deferred

5. **Description** - Detailed explanation of work required
   - What needs to be done
   - Which files/classes affected
   - Specific implementation guidance

6. **Rationale** - Why this task is important
   - Business or technical justification
   - Impact if not done
   - Benefits when completed

### Optional Fields

Add as needed for specific tasks:

**Dependencies:**
```asciidoc
*Depends on:* C1 must be completed first
```

**Estimated Effort:**
```asciidoc
*Effort:* 2-3 days
```

**Related Issues:**
```asciidoc
*Related:* See issue #234 for context
```

## Task Identifiers

### Identifier Format

**Pattern:** `[Category Prefix][Sequential Number]`

**Examples:**
- Code: C1, C2, C3, ...
- Performance: P1, P2, P3, ...
- Security: S1, S2, S3, ...
- Testing: T1, T2, T3, ...
- Documentation: DOC1, DOC2, DOC3, ...

### Numbering Rules

1. **Sequential within category** - C1, C2, C3 (no gaps)
2. **Independent across categories** - Can have C1 and P1 simultaneously
3. **Never reuse** - Don't reuse identifiers after completion
4. **Add new at end** - New tasks get next available number

### Identifier Benefits

**Commit message integration:**
```
refactor: C1. Extract common validation logic

Moved validation logic from services into ValidationUtils
for reuse and better testability.
```

**Cross-referencing:**
```asciidoc
C5. Refactor UserService
*Depends on:* C1 (validation utils must exist first)
```

**Progress tracking:**
- "Completed C1-C3, working on C4"
- "All high-priority Security tasks (S1-S5) done"

## Status Indicators

For complete status indicator definitions and rationale, see [task-planning-core.md](task-planning-core.md) section "Status Indicators".

Refactoring planning uses only the two basic status markers: `[ ]` (Pending) and `[x]` (Completed). Extended markers (`[~]`, `[!]`) are NOT used - refactoring tasks are tracked as simple pending/complete workflows.

## Priority Assignment

### Priority Guidelines

**High Priority:**
- Security vulnerabilities
- Critical performance issues
- Blocking other work
- Compliance requirements
- Production bugs

**Medium Priority:**
- Code quality improvements
- Non-critical performance
- Documentation gaps
- Technical debt reduction
- Dependency updates

**Low Priority:**
- Code style improvements
- Minor optimizations
- Future enhancements
- Nice-to-have features

### Priority Indicators in Task Lists

Can visually group by priority:

```asciidoc
== High Priority Tasks

C1. Extract Common Validation Logic
[ ] *Priority:* High

S1. Fix SQL Injection Vulnerability
[ ] *Priority:* High

== Medium Priority Tasks

P1. Optimize Database Queries
[ ] *Priority:* Medium

DOC1. Add API Documentation
[ ] *Priority:* Medium

== Low Priority Tasks

C5. Rename Variables for Clarity
[ ] *Priority:* Low
```

## Organization Strategies

### By Category (Recommended)

```asciidoc
== Code Structure Tasks

C1. Extract Common Validation Logic
[ ] *Priority:* High

C2. Refactor Large Classes
[ ] *Priority:* Medium

== Performance Tasks

P1. Optimize Database Queries
[ ] *Priority:* High

P2. Add Caching Layer
[ ] *Priority:* Medium
```

### By Priority

```asciidoc
== High Priority

C1. Extract Common Validation Logic (Code)
S1. Fix Security Vulnerability (Security)
P1. Optimize Critical Path (Performance)

== Medium Priority

C2. Refactor Classes (Code)
T1. Add Unit Tests (Testing)
```

### Hybrid Approach

```asciidoc
== Critical Items (All High Priority)

=== Security
S1. Fix SQL Injection Vulnerability

=== Performance
P1. Optimize Database Queries

== Ongoing Improvements (Medium/Low Priority)

=== Code Structure
C2. Refactor Large Classes
C3. Remove Code Duplication
```

## Progress Tracking

### Completion Tracking

Track progress within each category:

```
Code Structure: 3/7 completed (C1, C2, C3 done; C4-C7 pending)
Performance: 2/4 completed (P1, P2 done; P3-P4 pending)
Security: 5/5 completed (All done!)
Testing: 1/6 completed (T1 done; T2-T6 pending)
```

### Visual Progress

Use checkboxes for quick visual assessment:

```asciidoc
== Code Structure Tasks

C1. [x] Extract Common Validation Logic
C2. [x] Refactor Large Classes
C3. [x] Remove Code Duplication
C4. [ ] Split Monolithic Service
C5. [ ] Extract Interfaces
```

## Commit Message Integration

### Using Task Identifiers

Reference task identifiers in commit messages:

```
refactor: C1. Extract common validation logic

Moved validation logic from UserService, OrderService, and
PaymentService into ValidationUtils class. Reduces duplication
and improves testability.
```

```
perf: P2. Add Redis caching layer

Implemented Redis caching for user profiles and configuration.
Reduces database load and improves response time by 40%.
```

```
security: S3. Implement rate limiting

Added rate limiting to all public API endpoints using token
bucket algorithm. Protects against DoS attacks.
```

### Commit Type Mapping

Map categories to conventional commit types:

| Category | Commit Type |
|----------|-------------|
| Code (C) | `refactor:` |
| Performance (P) | `perf:` |
| Security (S) | `security:` or `fix:` |
| Testing (T) | `test:` |
| Dependency (D) | `chore:` or `build:` |
| Documentation (DOC) | `docs:` |
| Future (F) | `feat:` |

## Adding New Tasks

### Process

1. **Identify appropriate category** - Choose C, P, S, T, D, DOC, or F
2. **Use next available number** - Check highest number in category
3. **Follow standard format** - Include all required fields
4. **Start with unchecked** - `[ ]` status
5. **Assign priority** - High, Medium, or Low
6. **Provide rationale** - Explain why it's important

### Example

```asciidoc
== Performance Tasks

P1. [x] Optimize Database Queries
P2. [x] Add Redis Caching
P3. [ ] Implement Connection Pooling      ← Adding this new task
[ ] *Priority:* Medium

*Description:* Implement database connection pooling using HikariCP
to reduce connection overhead and improve throughput.

*Rationale:* Current implementation creates new connection per request,
causing significant overhead. Connection pooling will improve performance
under concurrent load.
```

## Task Completion Process

### Workflow

1. **Implement the task** - Follow description and rationale
2. **Verify completion** - Ensure all aspects addressed
3. **Update checkbox** - Change `[ ]` to `[x]`
4. **Commit with identifier** - Use task ID in commit message
5. **Leave in document** - Don't remove completed tasks

### Do NOT Remove Completed Tasks

Keep completed tasks for:
- Project history
- Progress tracking
- Context for future work
- Understanding what's been done

## Best Practices

### Task Granularity

For comprehensive task granularity guidance, see [task-planning-core.md](task-planning-core.md) section "Task Granularity". When applying this guidance to refactoring planning, ensure tasks are:
- Completable in reasonable time (hours to days)
- Focused on specific refactoring operations
- Not so broad they span multiple refactoring categories

### Clear Descriptions

**Good:** "Extract validation logic from UserService, OrderService, and PaymentService into ValidationUtils class. Include email validation, phone validation, and date validation methods."

**Poor:** "Fix validation stuff"

### Meaningful Rationale

**Good:** "Reduces code duplication across 3 services. Improves testability by isolating validation logic. Makes it easier to add new validation rules consistently."

**Poor:** "Code will be better"

## Quality Checklist

Before adding refactoring task, verify:

- [ ] Task has unique identifier (C1, P2, etc.)
- [ ] Title is clear and action-oriented
- [ ] Priority is assigned (High/Medium/Low)
- [ ] Description is detailed and specific
- [ ] Rationale explains why task is important
- [ ] Status checkbox is present
- [ ] Task follows standard format

## Related Standards

- task-planning-core.md - Core concepts and status indicators
- project-planning-standards.md - Long-term project planning
- issue-planning-standards.md - Short-term issue planning
