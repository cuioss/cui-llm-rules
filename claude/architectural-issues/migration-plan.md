# Migration Plan: Agent Nesting to Hybrid Architecture

**Date**: 2025-11-04
**Reference**: agent-nesting-limitation.md

## Architecture Standards

- [ ] Add Rule 6 "Agent Delegation Constraints" to `cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/architecture-rules.md`

- [ ] Add Rule 7 "Maven Execution Principle" to `architecture-rules.md`: Agents NEVER call Maven directly, Commands orchestrate maven-builder

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

- [ ] Remove Task from `asciidoc-reviewer` tools
  ```
  BEFORE:
  asciidoc-reviewer [agent]
    tools: Read, Glob, Task, Skill
    └─> Task(asciidoc-format-validator) ❌
    └─> Task(asciidoc-link-verifier) ❌
    └─> Task(asciidoc-content-reviewer) ❌

  AFTER:
  asciidoc-reviewer [agent]
    tools: Read, Glob, Bash(asciidoc-validator.sh:*), Bash(python3:*), Skill
    ├─> Bash(asciidoc-validator.sh) for format validation
    ├─> Bash(python3 verify-adoc-links.py) for link verification
    └─> Direct analysis for content review
  ```

- [ ] Inline validation logic from sub-agents into `asciidoc-reviewer`

- [ ] Add `Bash(asciidoc-validator.sh:*)` and `Bash(python3:*)` to tools

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

- [ ] Update `/cui-java-task-manager` command: orchestrate Task(java-code-implementer) + Task(maven-builder)
  ```
  BEFORE:
  /cui-java-task-manager
    └─> Task(java-code-implementer)
         └─> implements + verifies internally ❌

  AFTER:
  /cui-java-task-manager
    ├─> Task(java-code-implementer) [focused: just implements]
    ├─> Task(maven-builder) [focused: just builds]
    ├─> Analyze build output in command
    └─> Iterate if issues found
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

- [ ] Remove Task from `pr-quality-fixer` - make focused (just fixes issues, no verification/commit)
  ```
  BEFORE:
  pr-quality-fixer [agent]
    tools: Read, Edit, Bash(gh:*), Task, mcp__sonarqube__*
    ├─> Fixes Sonar issues
    ├─> Task(java-code-implementer) ❌
    ├─> Task(java-junit-implementer) ❌
    ├─> Task(maven-builder) ❌
    └─> Task(commit-changes) ❌

  AFTER:
  pr-quality-fixer [agent]
    tools: Read, Edit, Bash(gh:*), mcp__sonarqube__*
    └─> Fixes Sonar issues ONLY (no verification/commit)
  ```

- [ ] Update `/cui-handle-pull-request` command: orchestrate Task(pr-quality-fixer) + Task(maven-builder) + Task(commit-changes)
  ```
  BEFORE:
  /cui-handle-pull-request
    └─> Task(pr-quality-fixer)
         └─> fixes + verifies + commits internally ❌

  AFTER:
  /cui-handle-pull-request
    ├─> Task(pr-quality-fixer) [focused: just fixes issues]
    ├─> Task(maven-builder) [focused: just verifies build]
    ├─> Analyze build output in command
    ├─> Iterate if issues found
    └─> Task(commit-changes) [focused: just commits]
  ```

- [ ] Remove Task from `pr-review-responder` - make focused (just responds to reviews, no verification/commit)
  ```
  BEFORE:
  pr-review-responder [agent]
    tools: Read, Edit, Bash(gh:*), Task
    ├─> Responds to Gemini review comments
    ├─> Task(maven-builder) ❌
    └─> Task(commit-changes) ❌

  AFTER:
  pr-review-responder [agent]
    tools: Read, Edit, Bash(gh:*)
    └─> Responds to review comments ONLY (no verification/commit)
  ```

- [ ] Update `/cui-handle-pull-request` command: orchestrate Task(pr-review-responder) + Task(maven-builder) + Task(commit-changes)
  ```
  BEFORE:
  /cui-handle-pull-request
    └─> Task(pr-review-responder)
         └─> responds + verifies + commits internally ❌

  AFTER:
  /cui-handle-pull-request
    ├─> Task(pr-review-responder) [focused: just responds]
    ├─> Task(maven-builder) [focused: just verifies]
    ├─> Analyze output in command
    ├─> Iterate if issues found
    └─> Task(commit-changes) [focused: just commits]
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

- [ ] Update `/cui-implement-task` command: orchestrate Task(task-executor) + Task(maven-builder) + Task(commit-changes)
  ```
  BEFORE:
  /cui-implement-task
    └─> Task(task-executor)
         └─> executes + verifies + commits internally ❌

  AFTER:
  /cui-implement-task
    ├─> Task(task-executor) [focused: just executes task]
    ├─> Task(maven-builder) [focused: just verifies]
    ├─> Analyze output in command
    ├─> Iterate if issues found
    └─> Task(commit-changes) [focused: just commits]
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
