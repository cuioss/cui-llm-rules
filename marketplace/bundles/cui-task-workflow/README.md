# CUI Task Workflow

Complete development workflow from issue implementation to PR review and quality verification. This bundle provides end-to-end tools for the entire development cycle: analyzing requirements, implementing features, handling pull request reviews, and ensuring code quality.

## Purpose

This bundle integrates two critical workflow stages:

1. **Issue Implementation** - Transform GitHub issues and requirements into fully implemented, tested, and verified code changes
2. **PR Workflow** - Handle pull request reviews, respond to feedback, and automatically fix quality issues

By combining these workflows, developers get a seamless experience from task assignment through code review to final merge.

## Components Included

### Commands (6 goal-based orchestrators)

#### Full Workflow Commands

1. **/orchestrate-workflow** - Complete issue implementation workflow
   - Reviews issue for clarity (uses cui-task-planning skill)
   - Creates task breakdown plan (uses cui-task-planning skill)
   - Executes tasks sequentially (uses cui-task-planning skill)
   - Verifies with /maven-build-and-fix
   - Optionally commits and pushes

2. **/orchestrate-language** - Unified Java/JavaScript task orchestration
   - Supports both Java and JavaScript with auto-detection
   - Java: Delegates to /java-implement-code, /java-implement-tests, /java-generate-coverage
   - JavaScript: Delegates to /js-implement-code, /js-implement-tests, /js-generate-coverage
   - Iterates up to 5 cycles for coverage improvement

3. **/pr-handle-pull-request** - Complete PR workflow orchestrator
   - Waits for CI/Sonar checks
   - Delegates to /maven-build-and-fix for build fixes
   - Delegates to /pr-respond-to-review-comments for review handling
   - Delegates to /pr-fix-sonar-issues for quality fixes

#### Self-Contained Commands

4. **/orchestrate-task** - Single task implementation
   - Executes one task (uses cui-task-planning skill)
   - Verifies with /maven-build-and-fix
   - Iterates up to 5 cycles
   - Returns structured result

5. **/pr-fix-sonar-issues** - Sonar issue handling
   - Fetches issues via MCP tool (uses sonar-workflow skill)
   - Triages each issue with Python script (uses sonar-workflow skill)
   - Delegates fixes or adds suppressions with user approval
   - Verifies and commits

6. **/pr-respond-to-review-comments** - Review comment handling
   - Fetches comments via gh CLI (uses pr-workflow skill)
   - Triages each comment with Python script (uses pr-workflow skill)
   - Makes code changes or posts explanations
   - Verifies and commits if code changed

### Skills (4 skills with workflows and scripts)

1. **cui-task-planning** - Task planning and execution workflows
   - **Plan workflow** - Creates actionable task breakdowns from issues
   - **Execute workflow** - Implements tasks from plan files
   - **Review workflow** - Validates issue documentation for clarity
   - Scripts: create-task-breakdown.py, track-task-progress.py, validate-acceptance.py

2. **cui-git-workflow** - Git commit workflow
   - **Commit workflow** - Commits with conventional commits format
   - Artifact detection and cleanup
   - Optional push and PR creation
   - Script: format-commit-message.py

3. **pr-workflow** - PR review comment handling
   - **Fetch Comments workflow** - Retrieves PR comments via gh CLI
   - **Handle Review workflow** - Triages and responds to comments
   - Scripts: fetch-pr-comments.py, triage-comment.py

4. **sonar-workflow** - Sonar issue handling
   - **Fetch Issues workflow** - Retrieves issues via SonarQube MCP
   - **Fix Issues workflow** - Triages and resolves issues
   - Scripts: fetch-sonar-issues.py, triage-issue.py

## Installation

```bash
/plugin install cui-task-workflow
```

## Usage Examples

### Complete Development Workflow

**Step 1: Implement a GitHub Issue**

```
/orchestrate-workflow issue=42
```

The command will analyze requirements, create a task plan, execute implementation, and verify builds.

**Step 2: Handle PR Review Comments**

```
/pr-handle-pull-request pr=156
```

The command will fetch comments, implement changes, verify quality, and push updates.

### Individual Operations

**Break down an issue:**
```
/orchestrate-workflow issue=42
# Creates plan-issue-42.md with task breakdown
```

**Execute single task:**
```
/orchestrate-task task="Add validation method to UserService"
```

**Fix Sonar issues:**
```
/pr-fix-sonar-issues
# Fetches, triages, fixes/suppresses all issues
```

**Respond to review comments:**
```
/pr-respond-to-review-comments
# Fetches, triages, responds to all comments
```

## Dependencies

### Inter-Bundle Dependencies
- **cui-maven** (required) - Commands use /maven-build-and-fix for verification
- **cui-java-expert** (optional) - For Java implementation delegation
- **cui-frontend-expert** (optional) - For JavaScript implementation delegation

### External Dependencies
- GitHub CLI (`gh`) for issue and PR operations
- Maven wrapper (`./mvnw`) for build verification
- SonarQube MCP tool for Sonar issue fetching

## Architecture

```
cui-task-workflow/
├── commands/           # 6 goal-based orchestrators
│   ├── orchestrate-workflow.md
│   ├── orchestrate-task.md
│   ├── orchestrate-language.md
│   ├── pr-handle-pull-request.md
│   ├── pr-fix-sonar-issues.md
│   └── pr-respond-to-review-comments.md
└── skills/             # 4 skills with workflows
    ├── cui-task-planning/
    │   ├── SKILL.md    # Plan, Execute, Review workflows
    │   ├── scripts/    # 3 Python scripts
    │   └── standards/  # Planning standards
    ├── cui-git-workflow/
    │   ├── SKILL.md    # Commit workflow
    │   ├── scripts/    # 1 Python script
    │   └── standards/  # Git commit standards
    ├── pr-workflow/
    │   ├── SKILL.md    # Fetch Comments, Handle Review workflows
    │   └── scripts/    # 2 Python scripts
    └── sonar-workflow/
        ├── SKILL.md    # Fetch Issues, Fix Issues workflows
        └── scripts/    # 2 Python scripts
```

## Bundle Statistics

- **Commands**: 6 (thin orchestrators, <100 lines each)
- **Skills**: 4 (with 8 Python scripts total)
- **Agents**: 0 (all absorbed into skills)

## Support

- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-task-workflow/
