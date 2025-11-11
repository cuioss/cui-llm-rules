# Issue Planning Standards

Standards for creating short-term implementation plans for single GitHub issues or feature requests.

## Purpose

Issue planning documents are designed for:
- Single GitHub issue implementation
- Feature requests with clear scope
- Bug fixes requiring multiple steps
- Short-term work (days to couple weeks)

## When to Use Issue Planning

Use this approach when:
- Implementing a single GitHub issue
- Planning work for a specific feature or bug
- Need sequential, step-by-step execution
- Working with task-executor or implementation agents
- Require clear acceptance criteria per task

**Not appropriate for:**
- Long-term project planning (use Project Planning)
- Ongoing improvements (use Refactoring Planning)
- Multi-issue coordination (use Project Planning)

## Document Structure

### File Locations

**For local issue directories:**
```
issue-4/plan-issue-4.md
issues/feature-x/plan-feature-x.md
```

**For GitHub issues without local directory:**
```
./plan-issue-4.md
./plan-feature-authentication.md
```

### Document Format

Use Markdown format for agent compatibility and GitHub integration.

### Document Template

```markdown
# [Issue Name/Number]: [One-sentence purpose]

**Issue Reference:** [Link to GitHub issue OR path to local issue directory]

---

## Instructions for Implementation Agent

**CRITICAL:** Implement tasks **ONE AT A TIME** in the order listed below.

After implementing each task:
1. ✅ Verify all acceptance criteria are met
2. ✅ Run all quality checks (tests, build, formatting)
3. ✅ Mark the task as done: `[x]`
4. ✅ Only proceed to next task when current task is 100% complete

**Do NOT skip ahead.** Each task builds on previous tasks.

---

## Tasks

### Task 1: [Task Name]

**Goal:** [What success looks like for this task]

**References:**
- Issue: [Specific section/paragraph/requirement from issue]
- Specification: [Path to relevant spec document, if any]
- Related Code: [Files/classes to reference, if any]

**Checklist:**
- [ ] Read and understand all references above
- [ ] If unclear, ask user for clarification (DO NOT guess)
- [ ] Implement the functionality
- [ ] Implement unit tests (minimum 80% coverage for new code)
- [ ] Update documentation (JavaDoc, AsciiDoc, README as appropriate)
- [ ] Run build to verify all tests pass
- [ ] Analyze build results - if issues found, fix and re-run
- [ ] Commit changes

**Acceptance Criteria:**
- [Specific, measurable criterion 1]
- [Specific, measurable criterion 2]

---

### Task 2: [Task Name]

**Goal:** [What success looks like for this task]

**References:**
- Issue: [Specific section/paragraph/requirement from issue]
- Specification: [Path to relevant spec document, if any]

**Checklist:**
- [ ] Read and understand all references above
- [ ] If unclear, ask user for clarification (DO NOT guess)
- [ ] Implement the functionality
- [ ] Implement unit tests (minimum 80% coverage for new code)
- [ ] Update documentation (JavaDoc, AsciiDoc, README as appropriate)
- [ ] Run build to verify all tests pass
- [ ] Analyze build results - if issues found, fix and re-run
- [ ] Commit changes

**Acceptance Criteria:**
- [Specific, measurable criterion 1]
- [Specific, measurable criterion 2]

---

[Repeat for all tasks...]

---

## Completion Criteria

All tasks above must be marked `[x]` before the issue is considered complete.

**Final verification:**
1. All acceptance criteria met for every task
2. All tests passing (unit + integration)
3. Code coverage ≥ 80% for new code
4. Documentation updated and complete
5. Build passes with no errors or warnings
6. All changes committed

---

**Plan created by:** task-breakdown-agent
**Date:** [Current date]
**Total tasks:** [Number of tasks]
```

## Task Structure

### Task Components

Each task MUST include:

1. **Task Number** - Sequential (Task 1, Task 2, etc.)
2. **Task Name** - Clear, action-oriented title
3. **Goal** - What success looks like
4. **References** - Links to issue, specs, code
5. **Checklist** - Step-by-step verification
6. **Acceptance Criteria** - Specific, measurable conditions

### Task Identifier Enhancement (Optional)

For better commit message integration, tasks can optionally include short identifiers:

```markdown
### Task 1 (T1): Add RetryConfig Record

**Goal:** Create configuration record for retry behavior

[Rest of task...]
```

This allows commit messages like:
```
feat: T1 - Add RetryConfig Record
```

## Task Organization

### Sequential Order

Tasks MUST be ordered by dependency:
1. Dependencies first
2. Core implementation
3. Related features
4. Testing enhancements
5. Documentation updates

### Task Numbering

Use simple sequential numbering:
- Task 1, Task 2, Task 3, ...
- No gaps in numbering
- No sub-tasks (break into separate tasks instead)

### Task Granularity

Each task should:
- Be completable in reasonable time (hours to 1-2 days)
- Produce tangible, verifiable result
- Build on previous tasks
- Have clear acceptance criteria

**Too large:** "Implement entire authentication system"
- Break into: authentication config, token generation, token validation, etc.

**Too small:** "Add import statement"
- Combine with: "Implement TokenValidator class"

## Status Indicators

Issue planning uses two status types:

**`[ ]` - Incomplete** (not started or in progress)
```markdown
- [ ] Implement the functionality
- [ ] Run build to verify
```

**`[x]` - Complete**
```markdown
- [x] Implement the functionality
- [x] Run build to verify
```

Status is tracked both at task level and checklist level.

## Goal Statements

Each task's goal should answer: "What does done look like?"

**Good goals:**
- "Configuration record exists with all retry parameters"
- "Retry logic integrated into HTTP adapter with exponential backoff"
- "All edge cases tested with 80%+ coverage"

**Poor goals:**
- "Work on config"
- "Fix the adapter"
- "Add tests"

## References

### Types of References

**To GitHub Issue:**
```markdown
**References:**
- Issue: Section "Configuration Requirements" (lines 15-23)
- Issue: Paragraph 3 under "Expected Behavior"
```

**To Specifications:**
```markdown
**References:**
- Specification: doc/http-client/05-resilient-adapter.adoc lines 45-78
- Specification: doc/configuration.adoc#retry-section
```

**To Related Code:**
```markdown
**References:**
- Related Code: src/main/java/com/example/HttpAdapter.java
- Related Code: Modify existing ResilientHttpAdapter class
```

### Reference Specificity

References must be SPECIFIC with exact locations:
- ✅ "Issue section 'Configuration Requirements' lines 15-23"
- ❌ "See issue for details"

## Checklist Requirements

### Standard Checklist Items

Every task checklist should include:

1. **Understanding:**
   ```markdown
   - [ ] Read and understand all references above
   - [ ] If unclear, ask user for clarification (DO NOT guess)
   ```

2. **Implementation:**
   ```markdown
   - [ ] Implement the functionality
   ```

3. **Testing:**
   ```markdown
   - [ ] Implement unit tests (minimum 80% coverage for new code)
   ```

4. **Documentation:**
   ```markdown
   - [ ] Update documentation (JavaDoc, AsciiDoc, README as appropriate)
   ```

5. **Verification:**
   ```markdown
   - [ ] Run build to verify all tests pass
   - [ ] Analyze build results - if issues found, fix and re-run
   ```

6. **Commit:**
   ```markdown
   - [ ] Commit changes
   ```

### Custom Checklist Items

Add task-specific items as needed:
```markdown
- [ ] Verify configuration properties are validated on startup
- [ ] Test with both RS256 and HS256 algorithms
- [ ] Ensure backward compatibility with existing code
```

## Acceptance Criteria

### Criteria Characteristics

Each acceptance criterion must be:
- **Specific** - No ambiguity about what's required
- **Measurable** - Can verify pass/fail objectively
- **Testable** - Can write a test to verify
- **Complete** - Covers all aspects of success

### Good Examples

```markdown
**Acceptance Criteria:**
- RetryConfig record exists with fields: maxAttempts, initialDelay, multiplier
- Builder pattern implemented with validation
- Test coverage ≥ 80% for RetryConfig
- JavaDoc present on all public methods
- Configuration loads correctly from properties file
```

### Poor Examples

❌ "Config works"
❌ "Tests are good"
❌ "Documentation updated"

## Agent Consumption

### For task-executor Agent

Plans should be designed for task-executor consumption:

1. **Sequential execution** - Tasks numbered and ordered
2. **Clear checklists** - Step-by-step verification
3. **Explicit criteria** - No ambiguity about done
4. **References included** - All context provided

### For Other Agents

Plans can also guide:
- Manual implementation
- Team coordination
- Progress tracking
- Review processes

## Completion Criteria

### Task-Level Completion

Task is complete when:
- All checklist items checked
- All acceptance criteria met
- Changes committed
- Status changed to `[x]`

### Plan-Level Completion

Plan is complete when:
- All tasks marked `[x]`
- Final verification section passed
- Issue can be closed

## Quality Checklist

Before finalizing issue plan, verify:

- [ ] All tasks numbered sequentially
- [ ] Each task has goal statement
- [ ] All tasks have specific references
- [ ] Checklists include standard items
- [ ] Acceptance criteria are measurable
- [ ] Tasks ordered by dependency
- [ ] Issue reference is complete
- [ ] Instructions for agent are clear

## Integration Patterns

### With task-breakdown-agent

task-breakdown-agent generates plans following this format.

### With task-executor

task-executor consumes plans and implements tasks one at a time.

### With GitHub Issues

Plans link to GitHub issues and track implementation progress.

## Related Standards

- task-planning-core.md - Core concepts and status indicators
- project-planning-standards.md - Long-term project planning
- refactoring-planning-standards.md - Refactoring task tracking
