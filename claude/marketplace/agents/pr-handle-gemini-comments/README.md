# Gemini Comment Handler Agent

Processes Gemini code review comments on GitHub pull requests by either fixing issues or explaining why changes are not applicable.

## Purpose

This agent automates the handling of Gemini (Google's AI code reviewer) comments on pull requests by:
- Retrieving all unresolved Gemini comments from a PR
- Analyzing each comment to determine if it's valid
- Fixing code/documentation for valid suggestions
- Explaining reasoning for inapplicable suggestions
- Verifying builds pass after code changes
- Committing changes systematically
- Replying to all comments with resolution status

## Usage

```bash
# Handle Gemini comments by PR number
"Handle the Gemini comments on PR #151"

# Handle Gemini comments by URL
"Process Gemini feedback for https://github.com/owner/repo/pull/123"

# Handle and auto-push changes
"Handle Gemini comments on PR #42 and push"
```

## Parameters

- **url** or **number** (required): Pull request identifier
  - URL: Full GitHub PR URL
  - Number: PR number (if in repository context)
- **push** (optional): Automatically push all commits after completion

## How It Works

1. **Validate PR**: Verifies pull request exists and is accessible
2. **Retrieve Comments**: Fetches all Gemini bot review comments via GitHub API
3. **Process Each Comment**:
   - Reads affected file and context
   - Determines if suggestion is valid
   - **If valid**: Fixes code/docs, verifies build, commits, replies "Resolved"
   - **If not applicable**: Replies with clear reasoning why not changed
4. **Commit Documentation**: Batches documentation fixes into single commit
5. **Push Changes**: If requested, pushes all commits to remote
6. **Report**: Returns comprehensive summary with metrics

## Examples

### Example 1: Handle Comments on PR

```
User: "Handle the Gemini comments on PR #151"

Agent:
- Fetches PR #151
- Finds 5 Gemini comments
- Comment 1: Valid suggestion for null check → Fixes code
  - Runs build → Passes
  - Commits fix
  - Replies "Resolved: Added null check for user parameter"
- Comment 2: Suggests renaming variable → Not applicable
  - Current name follows naming convention
  - Replies "Not applicable: Variable name aligns with project standards"
- Comments 3-5: Documentation improvements → Fixes
  - Updates .adoc files
  - Batches into one commit
- Total: 3 resolved, 2 not applicable
- 4 commits created (3 code + 1 docs)
```

### Example 2: Handle and Push

```
User: "Process Gemini feedback for https://github.com/cuioss/cui-http/pull/42 and push"

Agent:
- Processes all comments
- Fixes 2 code issues (2 commits)
- Fixes 3 documentation issues (1 commit)
- Explains 1 comment as not applicable
- Pushes all 3 commits to remote
- Returns summary with commit SHAs
```

## Resolution Strategies

**Strategy A - Fix the Code/Documentation**:
- Suggestion is valid and improves quality
- Uses Edit tool to apply changes
- For **code fixes**: Runs project-builder THEN commits individually
- For **doc fixes**: Batches together, commits at end
- Replies with "Resolved: {explanation}"

**Strategy B - Disagree with Comment**:
- Suggestion not applicable or would violate standards
- Formulates clear reasoning
- Replies with "Not applicable: {reasoning}"

## Critical Rules

- **Every comment gets a response** (resolved or not applicable)
- **Code changes verified before commit** (project-builder must pass)
- **Code and docs committed separately** (code individually, docs batched)
- **Uses gh CLI exclusively** (not GitHub MCP)
- **Commit via agent** (uses commit-current-changes, not direct git)
- **Push only at end** (if requested via parameter)

## Notes

- Agent invokes `project-builder` to verify code changes don't break build
- Agent invokes `commit-current-changes` for all commits
- Handles multiple Gemini bot username patterns
- Tracks all tool usage and reports in summary
- Includes lessons learned reporting for continuous improvement
- Code fixes committed immediately after build passes (faster feedback)
- Documentation fixes batched (more efficient)

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
