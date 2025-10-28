# Issue Manager Agent

Plans and structures implementation tasks for issues by creating detailed, actionable implementation plans.

## Purpose

This agent automates the planning phase of software development by:
- Analyzing issues from GitHub or local directories
- Breaking down requirements into discrete, actionable tasks
- Creating structured implementation plans with checklists
- Providing clear acceptance criteria for each task
- Ordering tasks logically based on dependencies

## Usage

```bash
# Plan a GitHub issue by URL
"Plan the issue https://github.com/cuioss/cui-java-tools/issues/4"

# Plan a GitHub issue by number (in current repo)
"Plan the issue #4"
"Plan the issue 4"

# Plan an issue from local directory
"Plan the issue issue-4/"
"Plan the issue ./issues/feature-request/"
```

## How It Works

1. **Identify Source**: Detects if issue is from GitHub or local directory
2. **Read Content**: Fetches issue details via `gh` CLI or reads local files
3. **Analyze**: Extracts requirements, acceptance criteria, constraints
4. **Decompose**: Breaks issue into 3-15 actionable tasks
5. **Structure**: Creates plan document with:
   - Task goals and references
   - Implementation checklists
   - Acceptance criteria
   - Sequential ordering
6. **Save**: Writes plan to appropriate location

## Plan Structure

Generated plans follow this format:

```markdown
# Issue #X: [Purpose]

## Instructions for Implementation Agent
- Implement tasks ONE AT A TIME
- Verify acceptance criteria before proceeding
- Run quality checks after each task

## Tasks

### Task 1: [Name]
**Goal**: [What success looks like]
**References**: [Specific issue sections/specs]
**Checklist**:
- [ ] Read references
- [ ] Implement functionality
- [ ] Add tests (≥80% coverage)
- [ ] Update documentation
- [ ] Run maven-project-builder
- [ ] Commit changes

**Acceptance Criteria**:
- [Measurable criterion 1]
- [Measurable criterion 2]
```

## Examples

### Example 1: GitHub Issue

```
User: "Plan the issue https://github.com/cuioss/cui-http/issues/4"

Agent:
- Fetches issue via gh CLI
- Issue: "Add Retry Logic to HTTP Client"
- Identifies 4 tasks:
  1. Add RetryConfig record
  2. Implement retry logic in adapter
  3. Add exponential backoff
  4. Update documentation
- Creates plan at ./plan-issue-4.md
- Returns summary with 4 tasks
```

### Example 2: Local Directory

```
User: "Plan the issue ./feature-requests/http-caching/"

Agent:
- Scans directory for *.md and *.adoc files
- Reads requirements.md and spec.adoc
- Identifies 6 tasks across implementation, testing, docs
- Creates plan at ./feature-requests/http-caching/plan-http-caching.md
- Returns summary with 6 tasks
```

## Task Decomposition

The agent intelligently breaks down issues into these categories:

**Research/Analysis**
- Understand existing code
- Review related specifications
- Identify integration points

**Implementation**
- Create new classes/methods
- Update existing code
- Handle edge cases

**Testing**
- Unit tests (≥80% coverage)
- Integration tests
- Edge case testing

**Documentation**
- JavaDoc for public APIs
- Update AsciiDoc specs
- README examples

**Verification**
- Run maven-project-builder
- Analyze build results
- Fix any issues

## Critical Rules

- **Planning Only**: Agent creates plans, does NOT implement code
- **No Guessing**: Asks user for clarification when requirements unclear
- **Explicit References**: All task references include specific sections/line numbers
- **Measurable Criteria**: Acceptance criteria must be verifiable
- **Sequential Order**: Tasks ordered with dependencies first

## Notes

- Supports both GitHub issues (via `gh` CLI) and local issue directories
- Generated plans are designed for use with `task-executor` agent
- Plan location: Same directory as issue (if local) or project root (if GitHub)
- Typical plan contains 3-15 tasks
- Each task includes checklist for systematic implementation

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
