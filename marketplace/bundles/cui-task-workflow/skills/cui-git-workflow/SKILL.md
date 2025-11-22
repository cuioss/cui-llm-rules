---
name: cui-git-workflow
description: Git commit workflow with conventional commits, artifact cleanup, and optional push/PR creation
allowed-tools: Read, Glob, Bash(git:*), Bash(rm:*), Bash(gh:*), Skill
---

# CUI Git Workflow Skill

Provides git commit workflow following conventional commits specification. Includes artifact cleanup, commit formatting, and optional push/PR creation.

## What This Skill Provides

### Commit Workflow (Absorbs commit-changes Agent)

Complete git commit workflow:
- Artifact detection and cleanup
- Commit message generation following conventional commits
- Optional push to remote
- Optional PR creation

### Commit Standards

- **Format:** `<type>(<scope>): <subject>`
- **Types:** feat, fix, docs, style, refactor, perf, test, chore
- **Quality:** imperative mood, lowercase, no period, max 50 chars

## When to Activate This Skill

- Committing changes to repository
- Generating commit messages from diffs
- Cleaning build artifacts before commit
- Creating pull requests after commit

## Workflow: Commit Changes

**Purpose:** Commit all uncommitted changes following Git Commit Standards.

**Input Parameters:**
- **message** (optional): Custom commit message
- **push** (optional): Push after committing
- **create-pr** (optional): Create PR after pushing

### Steps

**Step 1: Load Commit Standards**
```
Read {baseDir}/standards/git-commit-standards.md
```

**Step 2: Check for Uncommitted Changes**
```bash
git status --porcelain
```

If no changes → Report "No changes to commit"

**Step 3: Analyze Changes for Artifacts**

Use Glob to detect artifacts:
```
Glob pattern="**/*.class"
Glob pattern="**/*.temp"
```

Artifact patterns to clean:
- `*.class` files in `src/` directories
- `*.temp` temporary files
- Files in `target/` or `build/` accidentally staged

**Step 4: Clean Artifacts**

**Safe Deletions (automatic):**
- `*.class` in `src/main/java` or `src/test/java`
- `*.temp` anywhere
- Delete using `rm <file>`

**Uncertain Cases (ask user):**
- Files >1MB
- Files outside safe list
- Files in `target/` that are tracked

**Step 5: Generate Commit Message**

If custom message provided:
- Validate format
- Use provided message

If no message:
- Analyze diff using script:
  ```
  python3 {baseDir}/scripts/format-commit-message.py --analyze <diff-file>
  ```
- Generate message following standards

**Multi-type priority:** fix > feat > perf > refactor > docs > style > test > chore

**Step 6: Stage and Commit**
```bash
git add .
git commit -m "$(cat <<'EOF'
{commit_message}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Step 7: Push (Optional)**

If `push` parameter:
```bash
git push
```

**Step 8: Create PR (Optional)**

If `create-pr` parameter:
```bash
gh pr create --title "{title}" --body "$(cat <<'EOF'
## Summary
{summary}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Output

```json
{
  "status": "success",
  "commit_hash": "abc123",
  "commit_message": "feat(http): add retry configuration",
  "files_changed": 5,
  "artifacts_cleaned": 2,
  "pushed": true,
  "pr_url": "https://github.com/..."
}
```

## Scripts

### format-commit-message.py

**Purpose:** Format commit message or analyze diff for suggestions.

**Usage:**
```bash
# Format mode
python3 {baseDir}/scripts/format-commit-message.py --type feat --scope http --subject "add retry config"

# Analysis mode
python3 {baseDir}/scripts/format-commit-message.py --analyze <diff-file>
```

**Output:** JSON with formatted message and validation

## Standards (Load On-Demand)

### Git Commit Standards
```
Read {baseDir}/standards/git-commit-standards.md
```

Provides:
- Conventional commits format specification
- Commit type definitions and usage
- Subject, body, and footer guidelines
- Best practices and anti-patterns

## Critical Rules

**Artifacts:** NEVER commit `*.class`, `*.temp`, `*.backup*`
**Permissions:** NEVER push without `push` param, NEVER create PR without `create-pr` param
**Standards:** Follow conventional commits format, add Co-Authored-By footer
**Safety:** Ask user if uncertain about file deletion

## Integration

### Commands Using This Skill
- **/orchestrate-workflow** - Commits after task completion
- **/orchestrate-task** - Commits individual task changes

### Related Skills
- **cui-task-planning** - Task completion triggers commit

## Quality Verification

- [x] Self-contained with {baseDir} pattern
- [x] Progressive disclosure (standards loaded on-demand)
- [x] Script outputs JSON for machine processing
- [x] commit-changes agent functionality absorbed
- [x] Clear workflow definition
- [x] Standards documentation maintained

## References

- Conventional Commits: https://www.conventionalcommits.org/
- Git Commit Best Practices: https://cbea.ms/git-commit/
- Angular Commit Guidelines: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit
