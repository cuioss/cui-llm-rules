# Migration Plan: Agent Nesting to Hybrid Architecture

**Date**: 2025-11-04
**Reference**: agent-nesting-limitation.md

## Primary Architectural Pattern: Three-Layer Design

**THE PATTERN** (use this everywhere):

```
Layer 1: Batch Command (collection/iteration)
  ├─> Collects items (files, issues, tasks, etc.)
  ├─> For each item:
  │    └─> SlashCommand(/single-item-command item)
  └─> Aggregates results

Layer 2: Single-Item Command (orchestration)
  ├─> Task(focused-agent-1) [does one thing]
  ├─> Task(focused-agent-2) [does another thing]
  ├─> Analyzes results in command context
  ├─> Iterates if needed
  └─> Returns structured result

Layer 3: Focused Agents (execution)
  └─> Does ONE specific task, returns result
      NO Task delegation, NO verification, NO commit
```

**Examples**:

```
Documentation Review:
/review-technical-docs (batch)
  ├─> Glob *.adoc
  ├─> For each: SlashCommand(/review-single-asciidoc file.adoc)
  └─> Aggregate results

/review-single-asciidoc (single-item)
  ├─> Task(asciidoc-format-validator)
  ├─> Task(asciidoc-link-verifier)
  ├─> Task(asciidoc-content-reviewer)
  └─> Report combined results

Java Implementation:
/implement-java-task (batch - if multiple classes)
  ├─> Parse task for affected classes
  ├─> For each class: SlashCommand(/implement-single-class task)
  └─> Aggregate results

/implement-single-class (single-item)
  ├─> Task(java-code-implementer)
  ├─> Task(maven-builder)
  ├─> Analyze build output
  ├─> Iterate if issues found
  └─> Return result

PR Quality:
/handle-pull-request (batch)
  ├─> Fetch all Sonar issues
  ├─> For each issue: SlashCommand(/fix-single-issue issue)
  ├─> Task(maven-builder) [verify all fixes]
  └─> Task(commit-changes)

/fix-single-issue (single-item)
  ├─> Task(issue-analyzer)
  ├─> Task(code-fixer)
  └─> Return fix result
```

**Why This Works**:
- ✅ No agent nesting (commands orchestrate, agents execute)
- ✅ Reusable components (single-item commands work standalone)
- ✅ Clear separation (collection vs orchestration vs execution)
- ✅ Scalable (batch handles 1 or 1000 items same way)
- ✅ Testable (test each layer independently)

## Architecture Standards

- [ ] Add Rule 6 "Agent Delegation Constraints" to `cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/architecture-rules.md`

- [ ] Add Rule 7 "Maven Execution Principle" to `architecture-rules.md`: Agents NEVER call Maven directly, Commands orchestrate maven-builder

- [ ] Add Rule 8 "Three-Layer Pattern" to `architecture-rules.md`: Batch command → Single-item command → Focused agents (PRIMARY PATTERN)

- [ ] Update Rule 5 "Component Organization" cross-layer communication section in `architecture-rules.md`

- [ ] Add Task tool misuse detection to `cui-plugin-development-tools/standards/agent-quality-standards.md`

- [ ] Add `Bash(./mvnw:*)` anti-pattern to `agent-quality-standards.md`: Always a bug in agents

## Diagnostic Tools

- [ ] Add Check 6 "Task Tool Misuse Detection" to `cui-plugin-development-tools/commands/cui-diagnose-agents.md`

- [ ] Add Check 7 "Maven Anti-Pattern Detection" to `cui-diagnose-agents.md`: Detect `Bash(./mvnw:*)` in agent tools

- [ ] Add Task tool validation to questionnaire in `cui-plugin-development-tools/commands/cui-create-agent.md`

- [ ] Add Maven tool validation to `cui-create-agent.md`: Reject `Bash(./mvnw:*)` in agent tool selection

## Agent Migrations

### cui-maven

- [ ] Remove `maven-project-builder` agent entirely
  ```
  BEFORE:
  /cui-build-and-verify (command)
    └─> Task(maven-project-builder) [agent]
         └─> Task(maven-builder) ❌ FAILS - Task not available to agents

  AFTER:
  /cui-build-and-verify (command)
    ├─> Task(maven-builder) [focused: just builds]
    ├─> Analyze output in command context
    ├─> Fix issues in command context
    └─> Iterate until clean
  ```

- [ ] Update `/cui-build-and-verify` command: add analysis/fixing logic, use Task(maven-builder) + iterate in command
  ```
  BEFORE:
  /cui-build-and-verify
    └─> Delegates everything to maven-project-builder agent

  AFTER:
  /cui-build-and-verify
    ├─> Task(maven-builder) - returns output file path + errors/warnings
    ├─> Read output file, analyze issues
    ├─> Fix each issue using Edit/Write tools
    ├─> Task(maven-builder) again to verify
    ├─> Repeat until clean
    └─> Task(commit-changes) if 'push' parameter provided
  ```

- [ ] Keep `maven-builder` agent as-is (focused executor)
  ```
  NO CHANGE:
  maven-builder [agent]
    ├─> Reads .claude/run-configuration.md for timeout
    ├─> Executes ./mvnw with timeout
    ├─> Captures output to timestamped file
    ├─> Extracts errors/warnings
    └─> Returns: status + file path + filtered output
  ```

### cui-documentation-standards

- [ ] Create `/review-single-asciidoc` command (single-file orchestrator)
  ```
  NEW COMMAND:
  /review-single-asciidoc <file.adoc> (single-item command)
    ├─> Task(asciidoc-format-validator) [focused: format only]
    ├─> Task(asciidoc-link-verifier) [focused: links only]
    ├─> Task(asciidoc-content-reviewer) [focused: content only]
    └─> Return combined validation results
  ```

- [ ] Update `/review-technical-docs` to use three-layer pattern
  ```
  BEFORE:
  /review-technical-docs (command)
    └─> Task(asciidoc-reviewer) [agent]
         └─> Does everything ❌

  AFTER:
  /review-technical-docs (batch command)
    ├─> Glob for all *.adoc files
    ├─> For each file:
    │    └─> SlashCommand(/review-single-asciidoc file.adoc)
    └─> Aggregate results from all files
  ```

- [ ] Keep focused validation agents as-is
  ```
  NO CHANGE:
  asciidoc-format-validator [agent]
    └─> Bash(asciidoc-validator.sh) - returns format issues

  asciidoc-link-verifier [agent]
    └─> Bash(python3 verify-adoc-links.py) - returns link issues

  asciidoc-content-reviewer [agent]
    └─> Direct analysis - returns content issues
  ```

- [ ] Remove old `asciidoc-reviewer` agent (replaced by /review-single-asciidoc command)

### cui-java-expert

- [ ] Remove Task from `java-code-implementer` - make focused (just implements code, no verification)
  ```
  BEFORE:
  java-code-implementer [agent]
    tools: Read, Write, Edit, Glob, Grep, Task, Skill
    ├─> Implements code changes
    └─> Task(maven-builder) for verification ❌

  AFTER:
  java-code-implementer [agent]
    tools: Read, Write, Edit, Glob, Grep, Skill
    └─> Implements code changes ONLY (no verification)
  ```

- [ ] Create `/implement-single-java-class` command if needed (single-item orchestrator)
  ```
  NEW COMMAND (optional - may not be needed):
  /implement-single-java-class <classname> <task-description>
    ├─> Task(java-code-implementer) [focused: just implements]
    ├─> Task(maven-builder) [focused: just builds]
    ├─> Analyze build output
    ├─> Iterate if issues found
    └─> Return result
  ```

- [ ] Update `/cui-java-task-manager` command: orchestrate using three-layer pattern if multiple classes
  ```
  BEFORE:
  /cui-java-task-manager
    └─> Task(java-code-implementer)
         └─> implements + verifies internally ❌

  AFTER (if single class):
  /cui-java-task-manager
    ├─> Task(java-code-implementer) [focused: just implements]
    ├─> Task(maven-builder) [focused: just builds]
    ├─> Analyze build output
    └─> Iterate if issues found

  AFTER (if multiple classes - three-layer):
  /cui-java-task-manager (batch)
    ├─> Parse task for affected classes
    ├─> For each class:
    │    └─> SlashCommand(/implement-single-java-class class task)
    ├─> Task(maven-builder) [verify all changes together]
    └─> Aggregate results
  ```

- [ ] Remove Task from `java-junit-implementer` - make focused (just writes tests, no verification)
  ```
  BEFORE:
  java-junit-implementer [agent]
    tools: Read, Write, Edit, Glob, Grep, Task, Skill
    ├─> Writes tests
    └─> Task(maven-builder) for verification ❌

  AFTER:
  java-junit-implementer [agent]
    tools: Read, Write, Edit, Glob, Grep, Skill
    └─> Writes tests ONLY (no verification)
  ```

- [ ] Update `/cui-java-task-manager` command: orchestrate Task(java-junit-implementer) + Task(maven-builder)
  ```
  BEFORE:
  /cui-java-task-manager
    └─> Task(java-junit-implementer)
         └─> writes tests + verifies internally ❌

  AFTER:
  /cui-java-task-manager
    ├─> Task(java-junit-implementer) [focused: just writes tests]
    ├─> Task(maven-builder) [focused: just builds + runs tests]
    ├─> Analyze test results in command
    └─> Iterate if tests fail
  ```

- [ ] Remove Task from `java-coverage-reporter` - make focused (just analyzes coverage, no building)
  ```
  BEFORE:
  java-coverage-reporter [agent]
    tools: Read, Glob, Grep, Task
    ├─> Task(maven-builder) to generate coverage ❌
    └─> Analyzes coverage reports

  AFTER:
  java-coverage-reporter [agent]
    tools: Read, Glob, Grep
    └─> Analyzes existing coverage reports ONLY (no building)
  ```

- [ ] Update commands using it: orchestrate Task(java-coverage-reporter) + Task(maven-builder)
  ```
  BEFORE:
  command
    └─> Task(java-coverage-reporter)
         └─> builds + analyzes internally ❌

  AFTER:
  command
    ├─> Task(maven-builder) with jacoco profile [generates coverage]
    └─> Task(java-coverage-reporter) [analyzes existing reports]
  ```

- [ ] Remove Task from `cui-log-record-documenter` - make focused (just documents LogRecords, no verification)
  ```
  BEFORE:
  cui-log-record-documenter [agent]
    tools: Read, Edit, Write, Grep, Glob, Task
    ├─> Documents LogRecord classes
    └─> Task(maven-builder) for verification ❌

  AFTER:
  cui-log-record-documenter [agent]
    tools: Read, Edit, Write, Grep, Glob
    └─> Documents LogRecord classes ONLY (no verification)
  ```

- [ ] Update `/cui-log-record-enforcer` command: orchestrate Task(cui-log-record-documenter) + Task(maven-builder)
  ```
  BEFORE:
  /cui-log-record-enforcer
    └─> Task(cui-log-record-documenter)
         └─> documents + verifies internally ❌

  AFTER:
  /cui-log-record-enforcer
    ├─> Task(cui-log-record-documenter) [focused: just documents]
    ├─> Task(maven-builder) [focused: just verifies JavaDoc]
    ├─> Analyze output in command
    └─> Iterate if JavaDoc errors found
  ```

### cui-workflow

- [ ] Create `/fix-single-sonar-issue` command (single-item orchestrator)
  ```
  NEW COMMAND:
  /fix-single-sonar-issue <issue-key>
    ├─> Task(sonar-issue-analyzer) [focused: analyzes issue type/location]
    ├─> Task(code-fixer) [focused: applies fix]
    └─> Return fix result (no verification)
  ```

- [ ] Remove Task from `pr-quality-fixer` - make focused OR split into focused agents
  ```
  BEFORE:
  pr-quality-fixer [agent]
    tools: Read, Edit, Bash(gh:*), Task, mcp__sonarqube__*
    ├─> Fixes Sonar issues
    ├─> Task(java-code-implementer) ❌
    ├─> Task(java-junit-implementer) ❌
    ├─> Task(maven-builder) ❌
    └─> Task(commit-changes) ❌

  AFTER (Option 1 - Keep as focused agent):
  pr-quality-fixer [agent]
    tools: Read, Edit, Bash(gh:*), mcp__sonarqube__*
    └─> Fixes Sonar issues ONLY (no verification/commit)

  AFTER (Option 2 - Split into focused agents):
  sonar-issue-analyzer [agent]
    └─> Analyzes issue type/location
  code-fixer [agent]
    └─> Applies fix based on analysis
  ```

- [ ] Update `/cui-handle-pull-request` command: use three-layer pattern
  ```
  BEFORE:
  /cui-handle-pull-request
    └─> Task(pr-quality-fixer)
         └─> fixes + verifies + commits internally ❌

  AFTER (three-layer):
  /cui-handle-pull-request (batch command)
    ├─> Fetch all Sonar issues for PR
    ├─> For each issue:
    │    └─> SlashCommand(/fix-single-sonar-issue issue-key)
    ├─> Task(maven-builder) [verify all fixes together]
    ├─> Analyze build output
    ├─> Iterate if issues found
    └─> Task(commit-changes) [commit all fixes]
  ```

- [ ] Create `/respond-to-single-review-comment` command (single-item orchestrator)
  ```
  NEW COMMAND:
  /respond-to-single-review-comment <comment-id>
    ├─> Task(review-comment-analyzer) [focused: understands request]
    ├─> Task(code-responder) [focused: makes changes or explains]
    └─> Return response result (no verification)
  ```

- [ ] Remove Task from `pr-review-responder` - make focused OR split
  ```
  BEFORE:
  pr-review-responder [agent]
    tools: Read, Edit, Bash(gh:*), Task
    ├─> Responds to Gemini review comments
    ├─> Task(maven-builder) ❌
    └─> Task(commit-changes) ❌

  AFTER (Option 1 - Keep as focused):
  pr-review-responder [agent]
    tools: Read, Edit, Bash(gh:*)
    └─> Responds to review comments ONLY (no verification/commit)

  AFTER (Option 2 - Split):
  review-comment-analyzer [agent]
    └─> Analyzes comment intent
  code-responder [agent]
    └─> Makes requested changes or explains
  ```

- [ ] Update `/cui-handle-pull-request` command: use three-layer for review responses
  ```
  BEFORE:
  /cui-handle-pull-request
    └─> Task(pr-review-responder)
         └─> responds + verifies + commits internally ❌

  AFTER (three-layer):
  /cui-handle-pull-request (batch command)
    ├─> Fetch all Gemini review comments
    ├─> For each comment:
    │    └─> SlashCommand(/respond-to-single-review-comment comment-id)
    ├─> Task(maven-builder) [verify all changes]
    ├─> Analyze build output
    ├─> Iterate if issues found
    └─> Task(commit-changes) [commit all responses]
  ```

- [ ] Create `/execute-single-subtask` command if task can be split (single-item orchestrator)
  ```
  NEW COMMAND (optional):
  /execute-single-subtask <subtask-description>
    ├─> Task(task-executor) [focused: implements subtask]
    └─> Return implementation result (no verification)
  ```

- [ ] Remove Task from `task-executor` - make focused (just executes task, no verification/commit)
  ```
  BEFORE:
  task-executor [agent]
    tools: Read, Edit, Write, Glob, Grep, Task, Bash(./mvnw:*), Bash(./gradlew:*), Skill
    ├─> Executes implementation task
    ├─> Task(maven-builder) ❌
    └─> Task(commit-changes) ❌

  AFTER:
  task-executor [agent]
    tools: Read, Edit, Write, Glob, Grep, Skill
    └─> Executes implementation task ONLY (no verification/commit)
  ```

- [ ] Update `/cui-implement-task` command: use three-layer if task has subtasks
  ```
  BEFORE:
  /cui-implement-task
    └─> Task(task-executor)
         └─> executes + verifies + commits internally ❌

  AFTER (if single atomic task):
  /cui-implement-task
    ├─> Task(task-executor) [focused: just executes task]
    ├─> Task(maven-builder) [focused: just verifies]
    ├─> Analyze output in command
    ├─> Iterate if issues found
    └─> Task(commit-changes) [focused: just commits]

  AFTER (if task has subtasks - three-layer):
  /cui-implement-task (batch)
    ├─> Break task into subtasks
    ├─> For each subtask:
    │    └─> SlashCommand(/execute-single-subtask subtask)
    ├─> Task(maven-builder) [verify all changes]
    ├─> Analyze output
    ├─> Iterate if issues found
    └─> Task(commit-changes) [commit all]
  ```

- [ ] Change `Task(/review-technical-docs)` → `SlashCommand(/review-technical-docs)` in `task-reviewer`
  ```
  BEFORE:
  task-reviewer [agent]
    tools: Read, Edit, Write, Bash(gh:*), Task, SlashCommand
    └─> Task(/review-technical-docs) ❌ Wrong tool

  AFTER:
  task-reviewer [agent]
    tools: Read, Edit, Write, Bash(gh:*), SlashCommand
    └─> SlashCommand(/review-technical-docs) ✅ Correct tool

  NOTE: SlashCommand executes in main context (available to agents)
        Task tool not available to agents (platform limitation)
  ```

### cui-plugin-development-tools

- [ ] Remove Task from `cui-diagnose-single-skill`
  ```
  BEFORE:
  cui-diagnose-single-skill [agent]
    tools: Read, Grep, Glob, Task
    └─> Task(validation-sub-agents) ❌

  AFTER:
  cui-diagnose-single-skill [agent]
    tools: Read, Grep, Glob
    └─> Direct validation using Grep/Read patterns
  ```

- [ ] Inline validation logic using Grep/Read/Glob in `cui-diagnose-single-skill`

## Testing

- [ ] Test `maven-project-builder` removal + `cui-build-and-verify` update
- [ ] Test all migrated cui-java-expert agents
- [ ] Test all migrated cui-workflow agents
- [ ] Test `asciidoc-reviewer` changes
- [ ] Test `cui-diagnose-single-skill` changes
- [ ] Run `/cui-diagnose-agents` - verify 0 Task tool violations
- [ ] Run `/cui-diagnose-bundle` for each affected bundle
- [ ] Test `/cui-build-and-verify` end-to-end
- [ ] Test `/cui-handle-pull-request` end-to-end
- [ ] Test `/cui-implement-task` end-to-end

## Documentation

- [ ] Update cui-maven bundle README
- [ ] Update cui-documentation-standards bundle README
- [ ] Update cui-java-expert bundle README
- [ ] Update cui-workflow bundle README
- [ ] Update cui-plugin-development-tools bundle README
