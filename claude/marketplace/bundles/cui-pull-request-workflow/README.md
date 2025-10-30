# CUI Pull Request Workflow

## Purpose

PR review response and quality fixing workflow. This bundle provides specialized tools for handling GitHub pull request reviews, responding to reviewer feedback, and automatically fixing common quality issues to maintain high code standards.

## Components Included

This bundle includes the following components:

### Agents
- **pr-review-responder** - Analyzes PR review comments and implements requested changes
- **pr-quality-fixer** - Automatically fixes common quality issues (formatting, linting, test coverage)

### Commands
- **handle-pull-request** - Orchestrates PR review handling and quality improvements

## Installation Instructions

To install this plugin bundle, run:

```
/plugin install cui-pull-request-workflow
```

This will make all agents and commands available in your Claude Code environment.

## Usage Examples

### Example 1: Handle PR Review Comments

Use the handle-pull-request command to respond to review feedback:

```
/handle-pull-request

Handle the review comments on PR #156 for the OAuth2 feature.
```

The command will:
1. Fetch PR review comments using GitHub CLI
2. Analyze reviewer feedback and requested changes
3. Categorize comments (code changes, questions, discussions)
4. Implement requested code changes
5. Run quality verification
6. Push updates and respond to comments

### Example 2: Fix Quality Issues Before Review

Use pr-quality-fixer to proactively address quality problems:

```
/agent pr-quality-fixer

Fix all quality issues in the current PR branch before requesting review.
```

The agent will:
- Run Maven build with quality checks
- Identify formatting violations
- Improve test coverage for critical paths
- Address JavaDoc warnings
- Commit fixes with descriptive messages

### Example 3: Respond to Specific Review Comment

Use pr-review-responder for targeted changes:

```
/agent pr-review-responder

Respond to the review comment requesting error handling improvement in HttpClient.java line 45.
```

The agent will:
- Read the specific review comment context
- Understand the reviewer's concern
- Implement the requested improvement
- Add tests if needed
- Verify build passes
- Prepare response comment explaining the changes

### Example 4: Combined PR Workflow

Typical workflow for handling PR reviews:

1. Receive review notification
2. Handle all comments: `/handle-pull-request` - "Address all review feedback on PR #156"
3. Fix remaining quality issues: `/agent pr-quality-fixer` - "Clean up any remaining quality violations"
4. Push changes and mark review comments as resolved

## Dependencies

### Inter-Bundle Dependencies
- **cui-maven** (required) - Both agents use maven-project-builder for build verification
- **cui-project-quality-gates** (required) - Both agents use commit-changes for commits

### External Dependencies
- Requires GitHub CLI (`gh`) for fetching PR comments and posting responses
- Requires git repository with remote tracking branch
- Requires Maven wrapper (`./mvnw`) for quality verification
- PR must exist on GitHub with review comments

### Integration Points
- Works with GitHub PR review system
- Integrates with Maven quality checks (test coverage, SonarQube)
- Uses git for branch management and pushing changes
