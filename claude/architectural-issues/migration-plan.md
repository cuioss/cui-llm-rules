# Migration Plan: Agent Nesting to Hybrid Architecture

**Date**: 2025-11-04
**Reference**: agent-nesting-limitation.md

## Critical Rules

These architectural constraints govern all agent and command design (see agent-nesting-limitation.md for details):

- ✅ Commands CAN invoke other commands (via SlashCommand tool)
- ✅ Commands CAN invoke agents (via Task tool)
- ❌ Agents CANNOT invoke other agents (Task tool unavailable at runtime)
- ❌ Agents CANNOT invoke commands (SlashCommand tool unavailable)
- ✅ Agents CAN use all other tools (Read, Write, Edit, Bash, Grep, Glob, Skill, etc.)
- 📋 Flow is unidirectional: command → command OR command → agent (NEVER agent → *)

## Primary Architectural Patterns

### Pattern 1: Self-Contained Command (Single Operation)

**For single, focused operations** (implement, test, analyze, build):

```
/command-name (self-contained)
  ├─> Task(focused-agent) [does the work]
  ├─> Task(maven-builder) [verifies if needed]
  ├─> Analyzes results
  ├─> Iterates if issues found
  └─> Returns structured result

Focused Agent (execution only)
  └─> Does ONE specific task
      NO Task delegation, NO verification, NO commit
```

**Examples**: `/java-implement-code`, `/java-implement-tests`, `/java-coverage-report`

### Pattern 2: Three-Layer Design (Batch Operations)

**For batch/collection operations** (multiple independent items):

```
Layer 1: Batch Command (collection/iteration)
  ├─> Collects items (files, issues, tasks, etc.)
  ├─> For each item:
  │    └─> SlashCommand(/self-contained-command item)
  └─> Aggregates results

Layer 2: Self-Contained Command (see Pattern 1)
  ├─> Task(focused-agent)
  ├─> Task(verification-agent)
  └─> Returns result

Layer 3: Focused Agents (execution)
  └─> Does ONE specific task
      NO Task delegation, NO verification, NO commit
```

**Examples**: `/review-technical-docs` → `/review-single-asciidoc`, `/cui-java-task-manager` → `/java-implement-code`

### Pattern 3: Fetch + Triage + Delegate (Smart Orchestration)

**For complex orchestration** (requires analysis before action):

```
Orchestrator Command
  ├─> Task(fetcher-agent) [retrieves all items with filtering]
  ├─> For each item:
  │    ├─> Task(triager-agent) [analyzes and decides action]
  │    ├─> Based on triage decision:
  │    │    ├─> Option A: SlashCommand(/implementation-command)
  │    │    ├─> Option B: Direct Edit for trivial changes
  │    │    └─> Option C: AskUserQuestion for user approval
  │    └─> Store result
  ├─> Task(verification-agent) [verify all changes together]
  └─> Task(commit-changes) [commit if clean]

Fetcher Agent (data retrieval)
  └─> Fetches items with optional filtering
      Returns structured list

Triager Agent (decision making)
  └─> Analyzes single item, decides action
      Returns: {action, reason, implementation_approach, suppression_string}
```

**When to Use**:
- Items require analysis before deciding how to handle them
- Different items need different actions (fix vs suppress, code change vs explanation)
- User approval may be needed for certain decisions
- Items are heterogeneous (not uniform like in batch processing)

**Examples**: `/fix-sonar-issues`, `/respond-to-review-comments`

**Concrete Examples**:

```
Documentation Review (Three-Layer):
/review-technical-docs (Layer 1: batch)
  ├─> Glob *.adoc files
  ├─> For each: SlashCommand(/review-single-asciidoc file.adoc)
  └─> Aggregate results

/review-single-asciidoc (Layer 2: self-contained)
  ├─> Task(asciidoc-format-validator) [Layer 3: focused]
  ├─> Task(asciidoc-link-verifier) [Layer 3: focused]
  ├─> Task(asciidoc-content-reviewer) [Layer 3: focused]
  └─> Return combined validation results

Java Implementation (Three-Layer):
/cui-java-task-manager (Layer 1: batch - if multiple implementations)
  ├─> Parse task for required implementations
  ├─> For each: SlashCommand(/java-implement-code class-task)
  ├─> For tests: SlashCommand(/java-implement-tests test-task)
  └─> Aggregate results

/java-implement-code (Layer 2: self-contained)
  ├─> Task(java-code-implementer) [Layer 3: focused]
  ├─> Task(maven-builder) [verifies]
  ├─> Analyze build output
  ├─> Iterate if issues
  └─> Return implementation result

/java-implement-tests (Layer 2: self-contained)
  ├─> Task(java-junit-implementer) [Layer 3: focused]
  ├─> Task(maven-builder) [verifies]
  ├─> Analyze test results
  ├─> Iterate if failures
  └─> Return test result

PR Quality Fix (Full PR Workflow):
/cui-handle-pull-request pr={number} (orchestrator - setup + wait + delegate + report)
  ├─> Get PR info, wait for CI/Sonar (30s polling, timeout handling)
  ├─> If build failed: SlashCommand(/cui-build-and-verify) [fix build]
  ├─> SlashCommand(/respond-to-review-comments) [self-contained: respond + verify + commit]
  ├─> SlashCommand(/fix-sonar-issues) [self-contained: fix + verify + commit]
  └─> Report: CI status, Sonar status, statistics, duration

/fix-sonar-issues (Pattern 3: Fetch + Triage + Delegate)
  PRECONDITIONS: PR checked out, CI complete, Sonar analysis done
  ├─> Task(sonar-issue-fetcher) [fetches all issues]
  ├─> For each: Task(sonar-issue-triager) → fix or suppress (with user approval)
  ├─> SlashCommand(/cui-build-and-verify push) [verify + commit]
  └─> Return summary: {issues_fixed, issues_suppressed, commits}

/respond-to-review-comments (Pattern 3: Fetch + Triage + Delegate)
  PRECONDITIONS: PR checked out, review comments available
  ├─> Task(review-comment-fetcher) [fetches all comments]
  ├─> For each: Task(review-comment-triager) → code change, explain, or ignore
  ├─> If code changed: SlashCommand(/cui-build-and-verify push) [verify + commit]
  └─> Return summary: {comments_addressed, code_changes, explanations}

Task Execution (Three-Layer):
/cui-implement-task (Layer 1: batch - if complex task with subtasks)
  ├─> Analyze and break into subtasks
  ├─> For each: SlashCommand(/execute-task subtask)
  └─> SlashCommand(/cui-build-and-verify push) [verify all + commit + push]

/execute-task (Layer 2: self-contained)
  ├─> Task(task-executor) [Layer 3: focused]
  ├─> Task(maven-builder) [verifies]
  ├─> Analyze build output
  ├─> Iterate if issues
  └─> Return task result
```

## Pattern Selection Guide

Choose the appropriate pattern based on your task characteristics:

### Pattern 1: Self-Contained Command
**Use when**: Single, focused operation on one item
- One implementation task
- One test class
- One analysis report
- One build execution

**Examples**: `/java-implement-code`, `/java-implement-tests`, `/execute-task`, `/java-coverage-report`

### Pattern 2: Three-Layer Design
**Use when**: Multiple **uniform** items (same type, same processing)
- All files in a directory
- All classes needing same change
- All subtasks of same type
- Batch processing where each item gets identical treatment

**Examples**: `/review-technical-docs` (all .adoc files), `/cui-java-task-manager` (multiple implementations)

### Pattern 3: Fetch + Triage + Delegate
**Use when**: **Heterogeneous** items requiring analysis before action
- Items need different actions (fix vs suppress, code vs explanation)
- Decision required before processing (what type of fix, which command to use)
- User approval needed for certain decisions
- Items vary in complexity or handling approach

**Examples**: `/fix-sonar-issues`, `/respond-to-review-comments`

**Why These Patterns Work**:
- ✅ No agent nesting (commands orchestrate, agents execute)
- ✅ Reusable components (Pattern 1 commands work standalone)
- ✅ Clear separation (Pattern 2: collection vs orchestration vs execution)
- ✅ Smart orchestration (Pattern 3: fetch → triage → delegate with user approval)
- ✅ Scalable (batch patterns handle 1 or 1000 items same way)
- ✅ Testable (test each layer/component independently)

## Architecture Standards

- [ ] Add Rule 6 "Agent Delegation Constraints" to `cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/architecture-rules.md`
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/architecture-rules.md
  ACTION: ADD NEW RULE 6
  ```

- [ ] Add Rule 7 "Maven Execution Principle" to `architecture-rules.md`: Agents NEVER call Maven directly (Bash(./mvnw:*) always a bug), Commands orchestrate maven-builder agent
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/architecture-rules.md
  ACTION: ADD NEW RULE 7

  EXCEPTION: maven-builder agent is ALLOWED Bash(./mvnw:*) - it's the central build execution agent
             All other agents must delegate to maven-builder instead of calling Maven directly

  WHY: Centralizes build execution, output capture, performance tracking
       Enables reusable build logic across all commands
       Prevents duplicate build configuration and error handling
  ```

- [ ] Add Rule 8 "Three-Layer Pattern" to `architecture-rules.md`: Batch command → Single-item command → Focused agents (PRIMARY PATTERN)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/architecture-rules.md
  ACTION: ADD NEW RULE 8
  ```

- [ ] Update Rule 5 "Component Organization" cross-layer communication section in `architecture-rules.md`
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/standards/architecture-rules.md
  ACTION: UPDATE RULE 5
  ```

- [ ] Add Task tool misuse detection to `cui-plugin-development-tools/standards/agent-quality-standards.md`
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/standards/agent-quality-standards.md
  ACTION: ADD TASK TOOL MISUSE DETECTION
  ```

- [ ] Add `Bash(./mvnw:*)` anti-pattern to `agent-quality-standards.md`: Always a bug in agents
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/standards/agent-quality-standards.md
  ACTION: ADD MAVEN ANTI-PATTERN DETECTION
  ```

## Diagnostic Tools

- [ ] Add Check 6 "Task Tool Misuse Detection" to `cui-plugin-development-tools/commands/cui-diagnose-agents.md`
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/commands/cui-diagnose-agents.md
  ACTION: ADD CHECK 6 - TASK TOOL MISUSE DETECTION
  ```

- [ ] Add Check 7 "Maven Anti-Pattern Detection" to `cui-diagnose-agents.md`: Detect `Bash(./mvnw:*)` in agent tools
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/commands/cui-diagnose-agents.md
  ACTION: ADD CHECK 7 - MAVEN ANTI-PATTERN DETECTION
  ```

- [ ] Add Task tool validation to questionnaire in `cui-plugin-development-tools/commands/cui-create-agent.md`
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/commands/cui-create-agent.md
  ACTION: ADD TASK TOOL VALIDATION TO QUESTIONNAIRE
  ```

- [ ] Add Maven tool validation to `cui-create-agent.md`: Reject `Bash(./mvnw:*)` in agent tool selection
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/commands/cui-create-agent.md
  ACTION: ADD MAVEN TOOL VALIDATION TO QUESTIONNAIRE
  ```

## Agent Migrations

### cui-maven

- [ ] Remove `maven-project-builder` agent entirely (logic moves to /cui-build-and-verify command)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-maven/agents/maven-project-builder.md
  ACTION: DELETE FILE

  BEFORE:
  /cui-build-and-verify (command)
    └─> Task(maven-project-builder) [agent]
         └─> Task(maven-builder) ❌ FAILS - Task not available to agents

  AFTER:
  /cui-build-and-verify (command - orchestrator)
    ├─> Task(maven-builder) [returns: structured issue data]
    ├─> Analyze issue types and locations
    ├─> Delegate to appropriate fix commands:
    │    └─> SlashCommand(/cui-java-task-manager "fix issues")
    ├─> Task(maven-builder) [verify fixes]
    └─> Iterate until clean

  WHY: Commands can orchestrate other commands (SlashCommand tool available)
       Commands can delegate based on issue analysis
       maven-project-builder tried to delegate (Task tool not available to agents)
  ```

- [ ] Update `/cui-build-and-verify` command: orchestrate build + delegate fixes to appropriate commands
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-maven/commands/cui-build-and-verify.md
  ACTION: UPDATE WORKFLOW

  BEFORE:
  /cui-build-and-verify
    └─> Delegates everything to maven-project-builder agent

  AFTER:
  /cui-build-and-verify (orchestrates verification workflow)
    ├─> Task(maven-builder) [returns: structured results with categorized issues]
    ├─> Analyze results to determine issue types and locations
    ├─> For each issue category:
    │    ├─> Java compilation errors → SlashCommand(/cui-java-task-manager "fix compilation errors")
    │    ├─> Test failures → SlashCommand(/cui-java-task-manager "fix failing tests")
    │    ├─> JavaDoc warnings → SlashCommand(/cui-java-task-manager "fix JavaDoc warnings")
    │    └─> Other issues → Analyze and delegate appropriately
    ├─> Task(maven-builder) [verify fixes]
    ├─> Repeat until clean
    └─> Task(commit-changes) if 'push' parameter provided

  NOTE: Command orchestrates and delegates, does NOT fix issues directly
        /cui-java-task-manager determines which classes need fixing and handles implementation
  ```

- [ ] Update `maven-builder` agent to return structured results (not just raw output)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-maven/agents/maven-builder.md
  ACTION: UPDATE RESPONSE FORMAT

  BEFORE:
  maven-builder [agent]
    ├─> Executes ./mvnw
    ├─> Captures output to timestamped file
    ├─> Extracts errors/warnings as text
    └─> Returns: status + file path + raw error/warning lines

  AFTER:
  maven-builder [agent]
    ├─> Executes ./mvnw with timeout
    ├─> Captures output to timestamped file
    ├─> Parses output to extract structured data
    └─> Returns: {
          status: SUCCESS|FAILURE,
          output_file: "target/build-output-*.log",
          issues: [
            {
              type: "compilation_error" | "test_failure" | "javadoc_warning" | etc,
              file: "path/to/File.java",
              line: 123,
              message: "error message",
              severity: "ERROR" | "WARNING"
            }
          ],
          summary: {
            compilation_errors: count,
            test_failures: count,
            javadoc_warnings: count,
            other_warnings: count
          }
        }

  NOTE: Structured results enable commands to delegate appropriately
        Commands can route issues to correct fix commands based on type/location
  ```

### cui-documentation-standards

- [ ] Create `/review-single-asciidoc` command (single-file orchestrator)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-documentation-standards/commands/review-single-asciidoc.md
  ACTION: CREATE NEW COMMAND FILE

  NEW COMMAND:
  /review-single-asciidoc <file.adoc> (single-item command)
    ├─> Task(asciidoc-format-validator) [focused: format only]
    ├─> Task(asciidoc-link-verifier) [focused: links only]
    ├─> Task(asciidoc-content-reviewer) [focused: content only]
    └─> Return combined validation results
  ```

- [ ] Update `/review-technical-docs` to use three-layer pattern
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-documentation-standards/commands/cui-review-technical-docs.md
  ACTION: UPDATE WORKFLOW

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
  FILES:
  - /Users/oliver/git/cui-llm-rules/claude/marketplace/bundles/cui-documentation-standards/agents/asciidoc-format-validator.md
  - /Users/oliver/git/cui-llm-rules/claude/marketplace/bundles/cui-documentation-standards/agents/asciidoc-link-verifier.md
  - /Users/oliver/git/cui-llm-rules/claude/marketplace/bundles/cui-documentation-standards/agents/asciidoc-content-reviewer.md
  ACTION: NO CHANGES NEEDED

  NO CHANGE:
  asciidoc-format-validator [agent]
    └─> Bash(asciidoc-validator.sh) - returns format issues

  asciidoc-link-verifier [agent]
    └─> Bash(python3 verify-adoc-links.py) - returns link issues

  asciidoc-content-reviewer [agent]
    └─> Direct analysis - returns content issues
  ```

- [ ] Remove old `asciidoc-reviewer` agent (replaced by /review-single-asciidoc command)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-documentation-standards/agents/asciidoc-reviewer.md
  ACTION: DELETE FILE (functionality moved to /review-single-asciidoc command)
  ```

### cui-java-expert

- [ ] Remove Task from `java-code-implementer` - make focused (just implements code, no verification)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/agents/java-code-implementer.md
  ACTION: UPDATE tools (remove Task)

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

- [ ] Create `/java-implement-code` command (self-contained implementation + verification)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/commands/java-implement-code.md
  ACTION: CREATE NEW COMMAND FILE

  NEW COMMAND:
  /java-implement-code <task-description>
    ├─> Task(java-code-implementer) [focused: just implements]
    ├─> Task(maven-builder) [verifies implementation]
    ├─> Analyze build output
    ├─> Iterate if issues found
    └─> Return result

  WHY: Self-contained command users can invoke directly
       Handles single implementation task end-to-end
       No need for /implement-single-java-class wrapper
  ```

- [ ] Update `/cui-java-task-manager` command: orchestrate using self-contained commands
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/commands/cui-java-task-manager.md
  ACTION: UPDATE WORKFLOW

  BEFORE:
  /cui-java-task-manager
    └─> Task(java-code-implementer)
         └─> implements + verifies internally ❌

  AFTER:
  /cui-java-task-manager (orchestrator)
    ├─> Parse task to determine scope
    ├─> SlashCommand(/java-implement-code "implement feature X")
    ├─> SlashCommand(/java-implement-tests "test feature X")
    └─> Return aggregated results

  NOTE: No three-layer needed - commands ARE already single-item
        /java-implement-code handles one implementation task
        /cui-java-task-manager orchestrates multiple if needed
  ```

- [ ] Remove Task from `java-junit-implementer` - make focused (just writes tests, no verification)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/agents/java-junit-implementer.md
  ACTION: UPDATE tools (remove Task)

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

- [ ] Create `/java-implement-tests` command (self-contained test writing + verification)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/commands/java-implement-tests.md
  ACTION: CREATE NEW COMMAND FILE

  NEW COMMAND:
  /java-implement-tests <test-description>
    ├─> Task(java-junit-implementer) [focused: just writes tests]
    ├─> Task(maven-builder) [runs tests]
    ├─> Analyze test results
    ├─> Iterate if tests fail
    └─> Return result

  WHY: Self-contained command users can invoke directly
       Handles single test implementation end-to-end
       Already single-item focused
  ```

- [ ] `/cui-java-task-manager` orchestrates these self-contained commands (see above)

- [ ] Convert `java-coverage-reporter` agent → `/java-coverage-report` command (self-contained)
  ```
  FILES:
  - DELETE: /Users/oliver/git/cui-llm-rules/claude/marketplace/bundles/cui-java-expert/agents/java-coverage-reporter.md
  - CREATE: /Users/oliver/git/cui-llm-rules/claude/marketplace/bundles/cui-java-expert/commands/java-coverage-report.md
  - CREATE: /Users/oliver/git/cui-llm-rules/claude/marketplace/bundles/cui-java-expert/agents/java-coverage-analyzer.md
  ACTION: DELETE AGENT, CREATE COMMAND + FOCUSED AGENT

  BEFORE:
  java-coverage-reporter [agent]
    tools: Read, Glob, Grep, Task
    ├─> Task(maven-builder) to generate coverage ❌
    └─> Analyzes coverage reports

  AFTER:
  /java-coverage-report [command - self-contained]
    ├─> Task(maven-builder) with -Pcoverage profile [generates coverage]
    ├─> Task(java-coverage-analyzer) [analyzes reports]
    └─> Returns structured coverage results

  java-coverage-analyzer [agent - NEW, focused]
    tools: Read, Glob, Grep
    └─> Analyzes existing JaCoCo XML/HTML reports ONLY

  WHY: Self-contained command that builds + analyzes
       Users can invoke /java-coverage-report directly
       Agent is focused (just analysis, no building)
  ```

- [ ] Update commands using it: invoke /java-coverage-report command instead
  ```
  BEFORE:
  command
    └─> Task(java-coverage-reporter)
         └─> builds + analyzes internally ❌

  AFTER:
  command
    └─> SlashCommand(/java-coverage-report)
         └─> self-contained (builds + analyzes)
  ```

- [ ] Create `logging-violation-analyzer` agent (focused: analyzes LOGGER usage)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/agents/logging-violation-analyzer.md
  ACTION: CREATE NEW AGENT FILE

  NEW AGENT:
  logging-violation-analyzer [agent]
    tools: Read, Grep, Glob
    └─> Analyzes all LOGGER statements, returns structured violation list

  WHAT IT DOES:
  - Uses Grep to find all LOGGER.(info|debug|trace|warn|error|fatal) calls
  - Parses each statement to determine LogRecord vs direct string usage
  - Applies validation rules (INFO/WARN/ERROR/FATAL need LogRecord, DEBUG/TRACE must NOT)
  - Returns: [{file, line, level, violation_type, current_usage}]
  ```

- [ ] Remove Task from `cui-log-record-documenter` - make focused (just updates AsciiDoc, no verification)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/agents/cui-log-record-documenter.md
  ACTION: UPDATE tools (remove Task)

  BEFORE:
  cui-log-record-documenter [agent]
    tools: Read, Edit, Write, Grep, Glob, Task
    ├─> Updates LogMessages.adoc documentation
    └─> Task(maven-builder) for verification ❌

  AFTER:
  cui-log-record-documenter [agent]
    tools: Read, Edit, Write, Grep, Glob
    └─> Updates LogMessages.adoc documentation ONLY (no verification)

  WHAT IT DOES:
  - Reads LogMessages Java class to extract LogRecord definitions
  - Updates corresponding LogMessages.adoc file (AsciiDoc format)
  - Synchronizes documentation with code (identifier, level, message)
  - Does NOT touch JavaDoc comments in Java files
  ```

- [ ] Update `/cui-log-record-enforcer` command: orchestrate multiple agents for complete workflow
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/commands/cui-log-record-enforcer.md
  ACTION: UPDATE WORKFLOW

  BEFORE:
  /cui-log-record-enforcer
    └─> Task(cui-log-record-documenter)
         └─> documents + verifies internally ❌

  AFTER:
  /cui-log-record-enforcer (orchestrates complete logging enforcement)
    ├─> Task(maven-builder) [pre-check: verify build before starting]
    ├─> Task(logging-violation-analyzer) [analyze LOGGER statements, return violations]
    ├─> Task(java-code-implementer) [fix logging violations based on analysis]
    ├─> Task(java-junit-implementer) [add LogAssert tests for coverage]
    ├─> Task(maven-builder) [verify: compilation + tests pass]
    ├─> Task(java-code-implementer) [renumber identifiers if needed]
    ├─> Task(cui-log-record-documenter) [update LogMessages.adoc documentation]
    ├─> Task(maven-builder) [final verification: compilation + tests]
    └─> Report compliance status

  NOTE: maven-builder verifies compilation + tests, NOT JavaDoc
        cui-log-record-documenter updates AsciiDoc files, NOT JavaDoc
        JavaDoc for LogRecord classes: handled by java-code-implementer when fixing violations (if needed)
        logging-violation-analyzer is NEW focused agent for LOGGER analysis
  ```

### cui-workflow

- [ ] Create `sonar-issue-fetcher` agent (focused: fetches issues from SonarQube)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/sonar-issue-fetcher.md
  ACTION: CREATE NEW AGENT FILE

  NEW AGENT:
  sonar-issue-fetcher [agent]
    tools: Bash(gh:*), mcp__sonarqube__*
    └─> Fetches Sonar issues with filtering options

  WHAT IT DOES:
  - Accepts filter parameters: "all", severity level, coverage-related, etc.
  - Queries SonarQube API (via MCP tools) for PR issues
  - Returns structured list: [{key, type, severity, file, line, rule, message}]
  - NO analysis, NO fixing - pure data retrieval
  ```

- [ ] Create `sonar-issue-triager` agent (focused: decides fix vs suppress)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/sonar-issue-triager.md
  ACTION: CREATE NEW AGENT FILE

  NEW AGENT:
  sonar-issue-triager [agent]
    tools: Read, Grep
    └─> Analyzes single issue and decides action

  WHAT IT DOES:
  - Reads code context around issue location
  - Analyzes issue rule, severity, pattern
  - Applies triage logic: is this fixable programmatically?
  - Returns decision: {
      action: "fix" | "suppress",
      reason: "explanation",
      suggested_implementation: "which command or approach to use",
      suppression_string: "// NOSONAR rule-key - reason" (ALWAYS derived from finding)
    }
  - For "fix": suggests which implementation approach (code change, test addition, etc.)
  - For "suppress": explains why suppression is appropriate
  - ALWAYS returns suppression_string regardless of decision (useful for fallback or user override)
  ```

- [ ] Create `/fix-sonar-issues` command (fetch + triage + fix Sonar issues)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/commands/fix-sonar-issues.md
  ACTION: CREATE NEW COMMAND FILE

  NEW COMMAND:
  /fix-sonar-issues [filter-options]

  PRECONDITIONS (handled by caller):
  - PR exists and is checked out locally
  - CI build has completed
  - Sonar analysis has finished and results are available
  - Caller has waited for all prerequisite steps

  WORKFLOW:
    ├─> Task(sonar-issue-fetcher) [returns all issues with optional filters]
    ├─> For each issue:
    │    ├─> Task(sonar-issue-triager) [returns: {action, reason, suggested_implementation, suppression_string}]
    │    ├─> If action = "fix":
    │    │    └─> Delegate to appropriate command based on suggested_implementation:
    │    │         ├─> SlashCommand(/java-implement-code "fix issue X")
    │    │         ├─> SlashCommand(/java-implement-tests "add test for Y")
    │    │         └─> Or direct Edit for trivial changes
    │    └─> If action = "suppress":
    │         └─> AskUserQuestion: "Triager suggests suppressing issue X because {reason}. Approve?"
    │              ├─> If approved: Add suppression_string to code
    │              └─> If rejected: Attempt fix anyway or skip
    ├─> SlashCommand(/cui-build-and-verify push) [verify all changes + commit + push]
    └─> Return summary: {issues_fixed: count, issues_suppressed: count, changes_made: file_list}

  WHY: Self-contained command with own verify + commit cycle
       Assumes prerequisites met (CI complete, Sonar results ready)
       NO waiting, NO setup - pure issue handling
       Reusable independently (not just for PRs)
       Returns structured result for orchestration
       Triage logic with user approval for suppressions
  ```

- [ ] Remove `pr-quality-fixer` agent file (logic moved to /fix-sonar-issues command)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/pr-quality-fixer.md
  ACTION: DELETE FILE
  ```

- [ ] Create `review-comment-fetcher` agent (focused: fetches review comments from GitHub)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/review-comment-fetcher.md
  ACTION: CREATE NEW AGENT FILE

  NEW AGENT:
  review-comment-fetcher [agent]
    tools: Bash(gh:*)
    └─> Fetches review comments with filtering options

  WHAT IT DOES:
  - Accepts filter parameters: "all", unresolved only, specific reviewers, etc.
  - Queries GitHub API (via gh CLI) for PR review comments
  - Returns structured list: [{id, author, file, line, body, resolved}]
  - NO analysis, NO responding - pure data retrieval
  ```

- [ ] Create `review-comment-triager` agent (focused: decides code change vs explanation)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/review-comment-triager.md
  ACTION: CREATE NEW AGENT FILE

  NEW AGENT:
  review-comment-triager [agent]
    tools: Read, Grep
    └─> Analyzes single review comment and decides action

  WHAT IT DOES:
  - Reads code context around comment location
  - Analyzes comment content and intent
  - Applies triage logic: code change needed, explanation sufficient, or ignore?
  - Returns decision: {
      action: "code_change" | "explain" | "ignore",
      reason: "explanation",
      suggested_implementation: "which command or approach to use",
      explanation_text: "draft explanation to post" (if action = "explain")
    }
  - For "code_change": suggests which implementation approach (refactor, test, fix)
  - For "explain": provides draft explanation (why no change needed, already addressed, etc.)
  - For "ignore": explains why comment doesn't require response
  ```

- [ ] Remove `pr-review-responder` agent (logic moved to /cui-handle-pull-request command)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/pr-review-responder.md
  ACTION: DELETE FILE

  BEFORE:
  pr-review-responder [agent]
    tools: Read, Edit, Bash(gh:*), Task
    ├─> Responds to Gemini review comments
    ├─> Task(maven-builder) ❌
    └─> Task(commit-changes) ❌

  AFTER:
  REMOVED - orchestration moved to /respond-to-review-comments command
           Fetch + triage pattern with focused agents instead

  WHY: Agent tried to orchestrate other agents (impossible)
       Fetch + triage pattern is consistent with Sonar issue handling
       Command handles orchestration
  ```

- [ ] Create `/respond-to-review-comments` command (fetch + triage + respond to review comments)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/commands/respond-to-review-comments.md
  ACTION: CREATE NEW COMMAND FILE

  NEW COMMAND:
  /respond-to-review-comments [filter-options]

  PRECONDITIONS (handled by caller):
  - PR exists and is checked out locally
  - CI build has completed (so reviewers have seen current state)
  - Review comments exist and are available via GitHub API
  - Caller has waited for all prerequisite steps

  WORKFLOW:
    ├─> Task(review-comment-fetcher) [returns all review comments with optional filters]
    ├─> For each comment:
    │    ├─> Task(review-comment-triager) [returns: {action, reason, suggested_implementation, explanation_text}]
    │    ├─> If action = "code_change":
    │    │    └─> Delegate based on suggested_implementation:
    │    │         ├─> SlashCommand(/java-implement-code "implement change")
    │    │         ├─> SlashCommand(/java-implement-tests "add test")
    │    │         └─> Or direct Edit for trivial changes
    │    ├─> If action = "explain":
    │    │    └─> Post explanation_text to GitHub using Bash(gh:*)
    │    └─> If action = "ignore":
    │         └─> Log reason, skip comment
    ├─> If any code changes made:
    │    └─> SlashCommand(/cui-build-and-verify push) [verify all changes + commit + push]
    └─> Return summary: {comments_addressed: count, code_changes: count, explanations_posted: count}

  WHY: Self-contained command with own verify + commit cycle (if code changed)
       Assumes prerequisites met (PR checked out, reviews available)
       NO waiting, NO setup - pure comment handling
       Reusable independently (not just for PRs)
       Returns structured result for orchestration
       Triage logic decides code change vs explanation
  ```

- [ ] Update `/cui-handle-pull-request` command: orchestrate specialized commands with setup/waiting
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/commands/cui-handle-pull-request.md
  ACTION: UPDATE WORKFLOW

  CURRENT WORKFLOW (from existing command):
  /cui-handle-pull-request pr={number}
    ├─> Step 1: Get PR info via gh pr view
    ├─> Step 2: Wait for CI and Sonar (poll every 30s, 30min timeout with user prompt)
    ├─> Step 3: If build failed → Task(maven-project-builder) to fix ❌
    ├─> Step 4: Handle review comments → Task(pr-review-responder) ❌
    ├─> Step 5: Handle Sonar issues → Loop with Task(pr-quality-fixer) ❌
    │    └─> User decision after each iteration: [C]ontinue/[S]kip/[A]bort
    ├─> Step 6: Final verification → Task(maven-project-builder) ❌
    └─> Step 7: Display summary with statistics

  AFTER (updated workflow):
  /cui-handle-pull-request pr={number}
    ├─> Step 1: Get PR info via gh pr view (KEEP)
    ├─> Step 2: Wait for CI and Sonar (KEEP - poll every 30s, timeout handling)
    ├─> Step 3: If build failed → SlashCommand(/cui-build-and-verify) to fix
    ├─> Step 4: Handle review comments → SlashCommand(/respond-to-review-comments)
    │    └─> Self-contained: responds + verifies + commits
    ├─> Step 5: Handle Sonar issues → SlashCommand(/fix-sonar-issues)
    │    └─> Self-contained: fixes + verifies + commits (includes triage + user approval)
    └─> Step 6: Display summary (KEEP - aggregate results from commands)
         - Track: reviews_responded_to, sonar_issues_fixed, build_verifications
         - Display: CI status, Sonar status, commits made, workflow duration

  WHY: Keeps existing user experience (wait, prompts, statistics)
       Replaces agent orchestration with command orchestration
       Removes duplicate final verification (commands verify themselves)
       Keeps timeout handling and user control patterns
       Each specialized command is self-contained and reusable
  ```

- [ ] Remove Task and Bash(./mvnw:*) from `task-executor` - make focused
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/task-executor.md
  ACTION: UPDATE tools (remove Task and Bash(./mvnw:*))

  BEFORE:
  task-executor [agent]
    tools: Read, Edit, Write, Glob, Grep, Task, Bash(./mvnw:*), Bash(./gradlew:*), Skill
    ├─> Executes implementation task
    ├─> Task(maven-builder) ❌ Agent delegation impossible
    └─> Task(commit-changes) ❌ Agent delegation impossible

  AFTER:
  task-executor [agent]
    tools: Read, Edit, Write, Glob, Grep, Skill
    └─> Executes implementation task ONLY (no verification/commit)

  WHY: Agents cannot delegate to other agents
       Bash(./mvnw:*) is anti-pattern (Rule 7)
       Task tool causes nesting limitation
  ```

- [ ] Create `/execute-task` command (self-contained: implement + verify single task)
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/commands/execute-task.md
  ACTION: CREATE NEW COMMAND FILE

  NEW COMMAND:
  /execute-task <task-description>
    ├─> Task(task-executor) [focused: implements task]
    ├─> Task(maven-builder) [verifies implementation]
    ├─> Analyze build output
    ├─> Iterate if verification fails
    └─> Return implementation result

  WHY: Self-contained command that implements and verifies ONE task
       Users can invoke directly for single task execution
       Returns structured result for batch aggregation
       Replaces agent attempting orchestration
  ```

- [ ] Update `/cui-implement-task` command: determine if atomic or batch
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/commands/cui-implement-task.md
  ACTION: UPDATE WORKFLOW

  BEFORE:
  /cui-implement-task
    └─> Task(task-executor)
         └─> executes + verifies + commits internally ❌

  AFTER (if single atomic task - self-contained pattern):
  /cui-implement-task (orchestrator)
    ├─> Task(task-executor) [focused: executes task]
    └─> SlashCommand(/cui-build-and-verify push) [verify + fix + commit + push]

  AFTER (if task has subtasks - three-layer pattern):
  /cui-implement-task (batch command - Layer 1)
    ├─> Analyze task and break into subtasks
    ├─> For each subtask:
    │    └─> SlashCommand(/execute-task subtask-description) [Layer 2: self-contained]
    │         └─> Task(task-executor) [Layer 3: focused execution]
    └─> SlashCommand(/cui-build-and-verify push) [verify all + fix + commit + push]

  WHY: Command determines pattern based on task complexity
       Atomic tasks: direct self-contained execution
       Complex tasks: three-layer decomposition
       /cui-build-and-verify handles verification, fixes, commit, push
       No duplication of verification/commit logic
  ```

- [ ] Update `task-reviewer` agent: Remove Task and SlashCommand from tools frontmatter
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/task-reviewer.md
  ACTION: UPDATE tools frontmatter (line 13)

  BEFORE:
  tools: Read, Edit, Write, Bash(gh:*), Task, SlashCommand

  AFTER:
  tools: Read, Edit, Write, Bash(gh:*)

  WHY: Agents cannot use Task (nesting limitation) or SlashCommand (unidirectional flow)
  ```

- [ ] Update `task-reviewer` agent: Remove Task(research-best-practices) delegation
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/task-reviewer.md
  ACTION: UPDATE Step 3 (lines 86-103)

  CHANGES:
  - Remove "If unclear aspect is researchable" branch entirely (Line 89)
  - Remove Task(research-best-practices) call
  - Simplify to: "If unclear aspect" → AskUserQuestion

  WHY: Agent cannot delegate to research-best-practices agent (Task tool unavailable)
       Calling command can handle research delegation if needed
  ```

- [ ] Update `task-reviewer` agent: Remove SlashCommand(/review-technical-docs) delegation
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/task-reviewer.md
  ACTION: UPDATE Step 8 (lines 222-242)

  CHANGES:
  - Remove Step 8 conditional AsciiDoc review entirely (Line 232)
  - Remove SlashCommand(/review-technical-docs) call

  WHY: Agent cannot invoke commands (SlashCommand tool unavailable)
       Calling command can handle doc review delegation if needed
  ```

- [ ] Update `task-reviewer` agent: Update RESPONSE FORMAT with delegation info
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/agents/task-reviewer.md
  ACTION: UPDATE RESPONSE FORMAT (line 292)

  ADD FIELDS:
  - **Research Needed**: {list of topics requiring research, or "None"}
  - **AsciiDoc Files Detected**: {list of .adoc file paths, or "None"}

  WHY: Agent returns delegation info so calling command (/cui-implement-task) can handle
       research and doc review as needed
  ```

### cui-plugin-development-tools

- [ ] Remove Task from `cui-diagnose-single-skill`
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/agents/cui-diagnose-single-skill.md
  ACTION: UPDATE tools (remove Task, inline validation)

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
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/agents/cui-diagnose-single-skill.md
  ACTION: INLINE VALIDATION LOGIC (covered by task above)
  ```

## Migration Summary

### Components Removed (5 agents)
Agents that attempted orchestration (Task delegation) or were replaced by commands:
- `maven-project-builder` (cui-maven) - orchestration moved to /cui-build-and-verify command
- `asciidoc-reviewer` (cui-documentation-standards) - replaced by /review-single-asciidoc command
- `java-coverage-reporter` (cui-java-expert) - converted to /java-coverage-report command + java-coverage-analyzer agent
- `pr-quality-fixer` (cui-workflow) - orchestration moved to /cui-handle-pull-request command
- `pr-review-responder` (cui-workflow) - orchestration moved to /cui-handle-pull-request command (fetch + triage pattern)

### New Focused Agents (6 agents)
Agents that do ONE specific task (no Task, no Bash(./mvnw:*), no verification):
- `logging-violation-analyzer` (cui-java-expert) - analyzes LOGGER statements, returns violations
- `java-coverage-analyzer` (cui-java-expert) - analyzes JaCoCo reports only
- `sonar-issue-fetcher` (cui-workflow) - fetches Sonar issues with filtering
- `sonar-issue-triager` (cui-workflow) - decides fix vs suppress for single issue
- `review-comment-fetcher` (cui-workflow) - fetches GitHub review comments with filtering
- `review-comment-triager` (cui-workflow) - decides code change vs explanation for single comment

### Existing Utility Agents (1 agent)
Agents already exist and are used by migrated commands:
- `commit-changes` (cui-workflow) - commits and pushes changes (used by multiple commands)

### New Self-Contained Commands (5 commands)
Layer 2 commands that orchestrate agent + verification for single items:
- `/java-implement-code` (cui-java-expert) - implements + verifies code changes
- `/java-implement-tests` (cui-java-expert) - writes + verifies tests
- `/java-coverage-report` (cui-java-expert) - generates + analyzes coverage
- `/review-single-asciidoc` (cui-documentation-standards) - validates single AsciiDoc file
- `/execute-task` (cui-workflow) - executes + verifies single task

### New Fetch+Triage+Delegate Commands (2 commands)
Pattern 3 commands that fetch, analyze, and delegate based on triage:
- `/fix-sonar-issues` (cui-workflow) - fetches Sonar issues, triages, fixes or suppresses
- `/respond-to-review-comments` (cui-workflow) - fetches review comments, triages, responds or explains

### Updated Orchestrator Commands (6 commands)
Commands that orchestrate agents and delegate to other commands:
- `/cui-build-and-verify` (cui-maven) - orchestrates maven-builder + delegates fixes to /cui-java-task-manager
- `/cui-java-task-manager` (cui-java-expert) - delegates to /java-implement-code, /java-implement-tests (batch pattern)
- `/cui-log-record-enforcer` (cui-java-expert) - orchestrates logging enforcement workflow
- `/review-technical-docs` (cui-documentation-standards) - delegates to /review-single-asciidoc per file (batch pattern)
- `/cui-handle-pull-request` (cui-workflow) - simple orchestrator: delegates to /fix-sonar-issues, /respond-to-review-comments, /cui-build-and-verify
- `/cui-implement-task` (cui-workflow) - delegates to /execute-task (batch if complex) or direct orchestration (if atomic)

### Modified Existing Agents (7 agents)
Agents with Task and/or Bash(./mvnw:*) removed, made focused:
- `maven-builder` (cui-maven) - update to return structured results, keep Bash(./mvnw:*) [EXCEPTION: central build agent]
- `java-code-implementer` (cui-java-expert) - remove Task, keep only implementation
- `java-junit-implementer` (cui-java-expert) - remove Task, keep only test writing
- `cui-log-record-documenter` (cui-java-expert) - remove Task, keep only AsciiDoc updates
- `task-executor` (cui-workflow) - remove Task and Bash(./mvnw:*), keep only execution
- `task-reviewer` (cui-workflow) - remove Task and SlashCommand, return delegation info to caller
- `cui-diagnose-single-skill` (cui-plugin-development-tools) - remove Task, inline validation

### Affected Validator Agents (3 agents)
AsciiDoc validators already focused, no changes needed (used by /review-single-asciidoc):
- `asciidoc-format-validator` (cui-documentation-standards)
- `asciidoc-link-verifier` (cui-documentation-standards)
- `asciidoc-content-reviewer` (cui-documentation-standards)

### Verified Clean Agents (5 agents)
cui-plugin-development-tools diagnostic agents verified to have no Task tool usage:
- `cui-analyze-integrated-standards` - tools: Read only
- `cui-analyze-standards-file` - tools: Read, Grep
- `cui-diagnose-single-command` - tools: Read only
- `cui-diagnose-single-agent` - tools: Read only
- `cui-analyze-cross-skill-duplication` - tools: Read, Glob

### Total Impact
- **Agents**: 5 removed, 6 new created, 7 modified = 18 agents changed
- **Commands**: 7 created (5 self-contained + 2 fetch+triage+delegate), 6 updated = 13 commands changed
- **Architecture rules**: 3 new rules added
- **Diagnostic checks**: 2 new checks added
- **Patterns**: 3 architectural patterns established (Self-Contained, Three-Layer, Fetch+Triage+Delegate)

## Testing

- [ ] Test `maven-project-builder` removal + `cui-build-and-verify` update
  ```
  ACTION: MANUAL TESTING - no specific file
  ```
- [ ] Test all migrated cui-java-expert agents
  ```
  ACTION: MANUAL TESTING - test all agents in cui-java-expert bundle
  ```
- [ ] Test all migrated cui-workflow agents
  ```
  ACTION: MANUAL TESTING - test all agents in cui-workflow bundle
  ```
- [ ] Test `asciidoc-reviewer` changes
  ```
  ACTION: MANUAL TESTING - test /review-single-asciidoc command
  ```
- [ ] Test `cui-diagnose-single-skill` changes
  ```
  ACTION: MANUAL TESTING - test cui-diagnose-single-skill agent
  ```
- [ ] Run `/cui-diagnose-agents` - verify 0 Task tool violations
  ```
  ACTION: EXECUTE DIAGNOSTIC COMMAND
  ```
- [ ] Run `/cui-diagnose-bundle` for each affected bundle
  ```
  ACTION: EXECUTE DIAGNOSTIC COMMAND FOR EACH BUNDLE
  ```
- [ ] Test `/cui-build-and-verify` end-to-end
  ```
  ACTION: MANUAL END-TO-END TESTING
  ```
- [ ] Test `/cui-handle-pull-request` end-to-end
  ```
  ACTION: MANUAL END-TO-END TESTING
  ```
- [ ] Test `/cui-implement-task` end-to-end
  ```
  ACTION: MANUAL END-TO-END TESTING
  ```

## Documentation

- [ ] Update cui-maven bundle README
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-maven/README.md
  ACTION: UPDATE BUNDLE DOCUMENTATION
  ```
- [ ] Update cui-documentation-standards bundle README
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-documentation-standards/README.md
  ACTION: UPDATE BUNDLE DOCUMENTATION
  ```
- [ ] Update cui-java-expert bundle README
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-java-expert/README.md
  ACTION: UPDATE BUNDLE DOCUMENTATION
  ```
- [ ] Update cui-workflow bundle README
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-workflow/README.md
  ACTION: UPDATE BUNDLE DOCUMENTATION
  ```
- [ ] Update cui-plugin-development-tools bundle README
  ```
  FILE: /cui-llm-rules/claude/marketplace/bundles/cui-plugin-development-tools/README.md
  ACTION: UPDATE BUNDLE DOCUMENTATION
  ```
