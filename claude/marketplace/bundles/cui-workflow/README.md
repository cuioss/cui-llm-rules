# CUI Workflow

Complete development workflow from issue implementation to PR review and quality verification. This bundle provides end-to-end tools for the entire development cycle: analyzing requirements, implementing features, handling pull request reviews, and ensuring code quality.

## Purpose

This bundle integrates two critical workflow stages:

1. **Issue Implementation** - Transform GitHub issues and requirements into fully implemented, tested, and verified code changes
2. **PR Workflow** - Handle pull request reviews, respond to feedback, and automatically fix quality issues

By combining these workflows, developers get a seamless experience from task assignment through code review to final merge.

## Components Included

### Agents (5 agents)

#### Issue Implementation Agents

1. **task-reviewer** - Reviews task plans and provides feedback on clarity and completeness
   - Validates acceptance criteria
   - Verifies implementation steps are specific
   - Identifies missing technical details
   - Suggests improvements

2. **task-breakdown-agent** - Breaks down complex issues into structured, actionable task plans
   - Analyzes requirements and specifications
   - Researches relevant best practices
   - Creates numbered tasks with acceptance criteria
   - Defines clear implementation steps
   - Identifies dependencies and risks

3. **task-executor** - Executes task plan steps sequentially with build verification
   - Reads and parses task plans
   - Executes checklist items sequentially
   - Runs build verification when required
   - Verifies acceptance criteria
   - Returns detailed completion reports

#### PR Workflow Agents

4. **pr-review-responder** - Analyzes PR review comments and implements requested changes
   - Reads specific review comment context
   - Understands reviewer concerns
   - Implements requested improvements
   - Adds tests if needed
   - Verifies build passes
   - Prepares response comments

5. **pr-quality-fixer** - Automatically fixes common quality issues
   - Runs Maven build with quality checks
   - Identifies formatting violations
   - Improves test coverage for critical paths
   - Addresses JavaDoc warnings
   - Retrieves and resolves Sonar issues
   - Commits fixes with descriptive messages

### Commands (2 commands)

1. **cui-implement-task** - Orchestrates complete issue implementation workflow
   - Analyzes issue requirements
   - Creates structured task plan
   - Executes each task sequentially
   - Verifies builds after each change
   - Commits changes with proper messages
   - Reports completion status

2. **cui-handle-pull-request** - Orchestrates PR review handling and quality improvements
   - Fetches PR review comments using GitHub CLI
   - Analyzes reviewer feedback and requested changes
   - Categorizes comments (code changes, questions, discussions)
   - Implements requested code changes
   - Runs quality verification
   - Pushes updates and responds to comments

## Installation Instructions

To install this plugin bundle, run:

```bash
/plugin install cui-workflow
```

This will make all agents and commands available in your Claude Code environment.

## Usage Examples

### Complete Development Workflow

**Step 1: Implement a GitHub Issue**

```
/cui-implement-task

Implement GitHub issue #42: Add OAuth2 token refresh capability
```

The command will analyze requirements, create a task plan, execute implementation, and verify builds.

**Step 2: Create Pull Request**

After implementation is complete, create a PR using standard git workflow or the commit-changes agent with PR creation.

**Step 3: Handle PR Review Comments**

```
/cui-handle-pull-request

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
- **cui-utility-commands** (required) - Agents use commit-changes agent for commits and research-best-practices for best practices research

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
- **cui-implement-task** command orchestrates: task-breakdown-agent → task-executor workflow
- **cui-handle-pull-request** command orchestrates: pr-review-responder → pr-quality-fixer workflow

## Workflow Stages

### Stage 1: Issue Analysis and Planning
Use task-breakdown-agent or task-reviewer to analyze requirements and create actionable plans.

### Stage 2: Implementation
Use task-executor or cui-implement-task to execute the plan and implement features.

### Stage 3: Quality Verification
Agents automatically run builds and quality checks during implementation.

### Stage 4: PR Creation
Create pull request using standard git workflow.

### Stage 5: Review Response
Use pr-review-responder or cui-handle-pull-request to address reviewer feedback.

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
- **cui-utility-commands** - For git commit management and research capabilities
- **cui-java-expert** - For Java development standards and expertise
- **cui-documentation-standards** - For documentation quality standards

## Bundle Statistics

- **Total Agents**: 5 (3 issue implementation + 2 PR workflow)
- **Total Commands**: 2 (1 issue implementation + 1 PR workflow)
- **Total Skills**: 0 (uses skills from other bundles)

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
- Bundle: claude/marketplace/bundles/cui-workflow/

---

*CUI Workflow Bundle - Complete Development Cycle Integration*
