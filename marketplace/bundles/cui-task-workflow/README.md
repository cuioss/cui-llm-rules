# CUI Workflow

Complete development workflow from issue implementation to PR review and quality verification. This bundle provides end-to-end tools for the entire development cycle: analyzing requirements, implementing features, handling pull request reviews, and ensuring code quality.

## Purpose

This bundle integrates two critical workflow stages:

1. **Issue Implementation** - Transform GitHub issues and requirements into fully implemented, tested, and verified code changes
2. **PR Workflow** - Handle pull request reviews, respond to feedback, and automatically fix quality issues

By combining these workflows, developers get a seamless experience from task assignment through code review to final merge.

## Components Included

### Agents (8 focused agents - Rule 6 compliant)

#### Core Workflow Agents

1. **commit-changes** - Git commit management with proper formatting (focused utility)
   - Commits repository changes with conventional commit format
   - Cleans build artifacts before committing
   - Auto-generates or accepts custom commit messages
   - Optional push and PR creation capabilities

2. **task-reviewer** - Reviews issues for implementation readiness (focused analyzer - Rule 6 compliant)
   - Validates requirements clarity and completeness
   - Returns delegation info (research needed, AsciiDoc files detected)
   - No Task/SlashCommand tools (caller handles delegation)

3. **task-breakdown-agent** - Breaks down issues into actionable tasks (focused planner)
   - Analyzes requirements and creates numbered task list
   - Defines acceptance criteria and dependencies

4. **task-executor** - Executes single implementation task (focused implementer - Rule 6 compliant)
   - Implements ONE task following specifications
   - No verification or commit (caller handles)
   - No Task or Bash(./mvnw:*) tools

#### PR Workflow Agents (Pattern 3: Fetch + Triage + Delegate)

5. **sonar-issue-fetcher** - Fetches Sonar issues with filtering (focused fetcher)
   - Retrieves issues from SonarQube API
   - Returns structured list: [{key, type, severity, file, line, rule, message}]
   - No analysis, pure data retrieval

6. **sonar-issue-triager** - Decides fix vs suppress for single issue (focused triager)
   - Analyzes code context around issue
   - Returns {action, reason, suggested_implementation, suppression_string}
   - No fixing, pure decision-making

7. **review-comment-fetcher** - Fetches GitHub review comments (focused fetcher)
   - Retrieves comments via GitHub API (gh CLI)
   - Returns structured list: [{id, author, file, line, body, resolved}]
   - No analysis, pure data retrieval

8. **review-comment-triager** - Decides code change vs explanation (focused triager)
   - Analyzes comment intent and code context
   - Returns {action, reason, suggested_implementation, explanation_text}
   - No changes, pure decision-making

### Commands (6 commands)

#### Orchestrator Commands

1. **/orchestrate-workflow** - Orchestrates complete issue implementation workflow
   - Delegates to task-reviewer, task-breakdown-agent
   - Pattern Decision: atomic (direct) vs batch (delegates to /orchestrate-task)
   - Uses /maven-build-and-fix for verification
   - Optionally commits and pushes

2. **/orchestrate-language** - Unified Java/JavaScript task orchestration (implementation → testing → coverage)
   - Supports both Java and JavaScript with auto-detection
   - Java: Uses maven-builder for iteration, delegates to /java-implement-code, /java-implement-tests, /java-generate-coverage
   - JavaScript: Uses npm-builder for iteration, delegates to /js-implement-code, /js-implement-tests, /js-generate-coverage
   - Note: Final workflow-level build always uses Maven (frontend-maven-plugin for JavaScript)
   - Iterates up to 5 cycles

3. **/pr-handle-pull-request** - Simple orchestrator for PR workflow (Pattern 3)
   - Waits for CI/Sonar checks
   - Delegates to /maven-build-and-fix for build fixes
   - Delegates to /pr-respond-to-review-comments for review handling
   - Delegates to /pr-fix-sonar-issues for quality fixes
   - Aggregates results from self-contained commands

#### Self-Contained Commands (Pattern 1 & Pattern 3)

4. **/orchestrate-task** - Implements and verifies single task (Pattern 1)
   - Uses task-executor agent for implementation
   - Uses maven-builder for verification
   - Iterates up to 5 cycles
   - Returns structured result

5. **/pr-fix-sonar-issues** - Fetches, triages, and fixes Sonar issues (Pattern 3)
   - Fetches issues with sonar-issue-fetcher
   - Triages each with sonar-issue-triager
   - Delegates fixes based on triage decision
   - Includes user approval for suppressions
   - Verifies, commits, and pushes

6. **/pr-respond-to-review-comments** - Fetches, triages, and responds to review comments (Pattern 3)
   - Fetches comments with review-comment-fetcher
   - Triages each with review-comment-triager
   - Code changes or explanations based on triage
   - Verifies, commits, and pushes if code changed

### Skills (2 skills)

1. **cui-git-workflow** - Git commit standards following conventional commits
   - Commit message format (type, scope, subject, body, footer)
   - Commit types (feat, fix, docs, style, refactor, perf, test, chore)
   - Subject, body, and footer guidelines with examples
   - Anti-patterns and verification checklist
   - Used by commit-changes agent

2. **cui-task-planning** - Comprehensive task planning and tracking standards
   - Project Planning - Long-term project-wide planning (doc/TODO.adoc)
   - Issue Planning - Short-term issue implementation plans (plan-issue-X.md)
   - Refactoring Planning - Categorized improvement tracking (Refactorings.adoc)
   - Status indicators, traceability patterns, task structures
   - Used by task-breakdown-agent

## Installation Instructions

To install this plugin bundle, run:

```bash
/plugin install cui-task-workflow
```

This will make all agents and commands available in your Claude Code environment.

## Usage Examples

### Complete Development Workflow

**Step 1: Implement a GitHub Issue**

```
/orchestrate-workflow

Implement GitHub issue #42: Add OAuth2 token refresh capability
```

The command will analyze requirements, create a task plan, execute implementation, and verify builds.

**Step 2: Create Pull Request**

After implementation is complete, create a PR using standard git workflow or the commit-changes agent with PR creation.

**Step 3: Handle PR Review Comments**

```
/pr-handle-pull-request

Handle the review comments on PR #156 for the OAuth2 feature.
```

The command will fetch comments, implement changes, verify quality, and push updates.

**Step 4: Fix Any Remaining Quality Issues**

```
/agent pr-quality-fixer

Fix all quality issues in the current PR branch before requesting re-review.
```

### Issue Implementation Examples

#### Break Down Complex Issue

```
/agent task-breakdown-agent

Break down the OAuth2 implementation issue into a detailed task plan.
```

#### Execute Existing Task Plan

```
/agent task-executor

Execute Task 3 from the plan at /path/to/oauth-plan.md
```

#### Review Task Plan Quality

```
/agent task-reviewer

Review the task plan at /path/to/feature-plan.md for quality and completeness.
```

### PR Workflow Examples

#### Respond to Specific Review Comment

```
/agent pr-review-responder

Respond to the review comment requesting error handling improvement in HttpClient.java line 45.
```

#### Proactive Quality Fixing

```
/agent pr-quality-fixer

Fix all quality issues before requesting code review.
```

## Dependencies

### Inter-Bundle Dependencies
- **cui-maven** (required) - Agents use maven-project-builder for build verification
- **cui-utilities** (recommended) - Agents may invoke research-best-practices for industry best practices research

### External Dependencies
- Requires GitHub CLI (`gh`) for issue and PR operations when working with GitHub
- Requires git repository with remote tracking branch
- Requires Maven wrapper (`./mvnw`) for build verification and quality checks
- PRs must exist on GitHub with review comments (for PR workflow)

### Integration Points
- Works with GitHub issue and PR systems
- Integrates with Maven quality checks (test coverage, JavaDoc, SonarQube)
- Uses git for branch management and pushing changes
- Supports Sonar issue status changes (accept, false positive, reopen)

### Internal Component Dependencies
- **task-reviewer** may invoke **research-best-practices** for validation
- **task-breakdown-agent** invokes **research-best-practices** for industry standards
- **orchestrate-workflow** command orchestrates: task-breakdown-agent → task-executor workflow
- **pr-handle-pull-request** command orchestrates: pr-review-responder → pr-quality-fixer workflow

## Workflow Stages

### Stage 1: Issue Analysis and Planning
Use task-breakdown-agent or task-reviewer to analyze requirements and create actionable plans.

### Stage 2: Implementation
Use task-executor or orchestrate-workflow to execute the plan and implement features.

### Stage 3: Quality Verification
Agents automatically run builds and quality checks during implementation.

### Stage 4: PR Creation
Create pull request using standard git workflow.

### Stage 5: Review Response
Use pr-review-responder or pr-handle-pull-request to address reviewer feedback.

### Stage 6: Quality Fixing
Use pr-quality-fixer to resolve any quality issues identified during review.

## Key Features

- **End-to-End Workflow**: Covers entire development cycle from issue to merge
- **Automated Quality Checks**: Build verification and quality fixing at every step
- **GitHub Integration**: Seamless integration with GitHub issues and PRs
- **Best Practices Research**: Agents can research industry standards when needed
- **Structured Task Management**: Clear task breakdowns with acceptance criteria
- **Intelligent Review Response**: Understands and implements reviewer feedback
- **Comprehensive Quality Fixing**: Handles formatting, testing, JavaDoc, and Sonar issues

## Related Bundles

This workflow bundle depends on and complements other CUI bundles:

- **cui-maven** - For Maven build and quality verification
- **cui-utilities** - For research capabilities (research-best-practices agent)
- **cui-java-expert** - For Java development standards and expertise
- **cui-documentation-standards** - For documentation quality standards

## Bundle Statistics

- **Total Agents**: 8 (1 core + 3 issue implementation + 4 PR workflow)
- **Total Commands**: 6 (3 orchestration + 3 self-contained)
- **Total Skills**: 2 (cui-git-workflow, cui-task-planning)

## Migration Notes

This bundle consolidates functionality from two previous bundles:
- **cui-issue-implementation** - Now integrated as issue implementation workflow
- **cui-pull-request-workflow** - Now integrated as PR workflow

All agents and commands from both bundles are available with the same names and behavior.

## License

Apache-2.0

## Support

For issues, questions, or contributions:
- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-task-workflow/

---

*CUI Workflow Bundle - Complete Development Cycle Integration*
