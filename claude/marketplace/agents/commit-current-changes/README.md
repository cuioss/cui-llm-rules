# Commit Current Changes Agent

Commits the current state of the repository with optional push and PR creation capabilities.

## Purpose

This agent automates the git commit workflow by:
- Analyzing uncommitted changes
- Cleaning build artifacts before committing
- Generating commit messages following Git Commit Standards
- Optionally pushing changes to remote
- Optionally creating pull requests

## Usage

```bash
# Commit changes with auto-generated message
"Commit my changes"

# Commit and push
"Commit my changes and push"

# Commit with custom message and create PR
"Commit my changes with 'fix(auth): resolve token issue', push and create a pr"
```

## Parameters

- **COMMIT_MESSAGE** (optional): Custom commit message instead of auto-generated
- **push** (optional): Push changes after committing
- **create a pr** (optional): Create pull request after pushing

## How It Works

1. **Check Changes**: Verifies uncommitted files exist
2. **Analyze Artifacts**: Finds build artifacts (*.class, *.temp, *.backup*)
3. **Clean Artifacts**: Removes unwanted files before commit
4. **Commit**: Creates commit with proper message format
5. **Push** (optional): Pushes to remote if requested
6. **PR** (optional): Creates pull request if requested

## Commit Message Format

Follows Git Commit Standards:
- Format: `<type>(<scope>): <subject>`
- Types: feat, fix, docs, style, refactor, perf, test, chore
- Examples:
  - `fix(auth): resolve token validation error`
  - `refactor: improve logging structure`
  - `feat(api): add user authentication endpoint`

## Examples

### Example 1: Auto-generated Commit Message

```
User: "Commit my changes"

Agent:
- Analyzes changes to UserController.java and AuthService.java
- Detects feature addition
- Generates: "feat(auth): add JWT token validation"
- Commits with Claude Code attribution
```

### Example 2: Custom Message with Push

```
User: "Commit my changes with 'docs: update API documentation', and push"

Agent:
- Uses provided message
- Commits changes
- Pushes to remote
- Reports success with commit hash
```

### Example 3: Full Workflow

```
User: "Commit my changes, push and create a pr"

Agent:
- Cleans 3 *.class artifacts
- Commits with auto-generated message
- Pushes to origin/feature-branch
- Creates PR with commit message as title
- Returns PR URL
```

## Notes

- Always cleans artifacts before committing (prevents committing build files)
- Asks for confirmation on uncertain file deletions
- Includes Claude Code attribution in commits and PRs
- Requires `gh` CLI tool for PR creation
- Validates but doesn't enforce commit message format if custom message provided

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
