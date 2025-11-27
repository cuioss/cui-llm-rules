# Finalize Phase Specification

**Purpose**: Complete the implementation workflow by committing changes, creating/updating PRs, and handling PR review feedback

**Input**: Plan from verify phase with passing builds and quality checks

**Output**: Committed code with PR created/updated and ready for merge

**Use Cases**:
- Committing verified implementation changes
- Creating new pull requests
- Updating existing PRs
- Handling PR review feedback loop

---

## Operations

The finalize phase provides three core operations:

| Operation | Description | Output |
|-----------|-------------|--------|
| **commit-changes** | Commit implementation with conventional commits | Commit hash and message |
| **create-pr** | Create new PR or update existing | PR URL and status |
| **handle-pr-workflow** | Process review feedback via /pr-fix | Updated PR ready for merge |

---

## Prerequisites

Before finalize phase can start:

1. **Verify phase completed** - All verification tasks passed
2. **Build passing** - No compilation errors, all tests green
3. **Quality gate passed** - Sonar/linting checks satisfied
4. **Documentation complete** - ADRs, interfaces, JavaDoc/JSDoc verified
5. **Branch exists** - Feature/fix branch created and checked out

---

## Configuration Options

The finalize phase behavior depends on plan configuration:

| Option | Values | Effect |
|--------|--------|--------|
| **commit_strategy** | `fine-granular` | One commit per task |
| | `single-commit` | All changes in one commit |
| | `squash` | Squash all commits before PR |
| **finalizing** | `pr-workflow` | Create PR and handle reviews |
| | `commit-only` | Commit without PR |
| | `merge-main` | Direct merge to main (rare) |
| **push** | `true/false` | Push after committing |

---

## Finalize Phase Workflow

### Step 1: Read Context

**Load plan and configuration** (via `plan-files` skill):
```
plan-files.read-plan:
- All tasks in finalize phase
- Current task (first pending or in_progress)
- Completed verify tasks for reference

plan-files.read-config:
- commit_strategy: fine-granular | single-commit | squash
- finalizing: pr-workflow | commit-only
- branch: feature/{name}
- issue: linked GitHub issue

plan-files.get-references:
- Implementation files
- Test files
- Documentation files
- Related ADRs and interfaces
```

**Determine commit scope**:
```
Based on commit_strategy:
- fine-granular: Group files by task
- single-commit: All files together
- squash: All commits to single
```

### Step 2: Clean Build Artifacts

**Purpose**: Ensure no temporary files are committed.

**Artifact Detection**:
```
Glob patterns to exclude:
- **/*.class
- **/*.temp
- **/*.backup*
- **/target/**
- **/node_modules/**
- **/.claude/plans/**/*.log
```

**TOON Handoff to plan-files**:
```toon
from: plan-finalize-skill
to: plan-files-skill
handoff_id: clean-001

operation: artifact-check
plan_directory: .claude/plans/jwt-auth/

artifacts_to_check:
  patterns[4]: *.class, *.temp, *.backup*, *.log
  directories[2]: target/, node_modules/

next_action: Identify files to exclude from commit
```

**Artifact Handling**:
- **Safe to delete**: `*.class` in `src/`, `*.temp` anywhere
- **Ask user**: Files >1MB, unrecognized patterns
- **Never delete**: Source files, test files, documentation

### Step 3: Generate Commit Message

**Purpose**: Create conventional commit message following standards.

**Commit Message Generation by Strategy**:

**Fine-Granular (per task)**:
```toon
from: plan-finalize-skill
to: cui-git-workflow-skill
handoff_id: msg-001

operation: format-commit-message
task:
  id: task-3
  name: Implement JWT token validation
  type: feat

changes:
  files_added[4]:
  - JwtService.java
  - JwtServiceTest.java
  - TokenValidator.java
  - TokenValidatorTest.java
  files_modified[1]:
  - application.properties

scope: auth

next_action: Generate conventional commit message
```

**Single-Commit (all changes)**:
```toon
from: plan-finalize-skill
to: cui-git-workflow-skill
handoff_id: msg-002

operation: format-commit-message
task:
  id: all
  name: Add JWT Authentication
  type: feat

changes:
  files_added: 8
  files_modified: 3
  total_tests: 47

scope: auth
issue_ref: "#123"

next_action: Generate comprehensive commit message
```

**Commit Message Format**:
```text
<type>(<scope>): <subject>

<body>

<footer>

---
Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Type Priority** (when multiple types apply):
`fix` > `feat` > `perf` > `refactor` > `docs` > `style` > `test` > `chore`

### Step 4: Stage and Commit

**Purpose**: Create git commit(s) with generated messages.

**Pre-Commit Checks**:
```bash
# Verify no uncommitted changes from wrong files
git status --porcelain

# Verify on correct branch
git branch --show-current

# Verify branch is up to date with remote
git fetch origin
git status -sb
```

**Staging and Commit**:
```bash
# Stage implementation files
git add src/main/java/com/example/auth/*.java
git add src/test/java/com/example/auth/*.java
git add src/main/resources/application.properties

# Commit with message
git commit -m "$(cat <<'EOF'
feat(auth): add JWT token validation service

Implement JWT authentication with RS256 signing, token validation,
and refresh token support. Includes comprehensive test coverage.

- Add JwtService for token generation
- Add TokenValidator for validation logic
- Add RefreshTokenService for token rotation
- Include 47 unit tests with 85% coverage

Fixes #123

---
Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Handle Pre-Commit Hooks**:
- If hooks modify files: Amend commit (if safe)
- If hooks fail: Report error, suggest fixes
- Always verify hook output before proceeding

**TOON Handoff for Commit**:
```toon
from: plan-finalize-skill
to: cui-git-workflow-skill
handoff_id: commit-001

operation: commit-changes
plan_directory: .claude/plans/jwt-auth/

commit:
  message: |
    feat(auth): add JWT token validation service
    ...
  files[5]:
  - JwtService.java
  - JwtServiceTest.java
  - TokenValidator.java
  - TokenValidatorTest.java
  - application.properties

options:
  verify_branch: true
  run_hooks: true

next_action: Stage and commit files
```

### Step 5: Push to Remote

**Purpose**: Push committed changes to remote repository.

**Pre-Push Validation**:
```bash
# Verify branch exists on remote (or needs creation)
git ls-remote --heads origin feature/jwt-auth

# Check for upstream changes
git fetch origin
git log origin/main..HEAD --oneline
```

**Push Command**:
```bash
# First push (set upstream)
git push -u origin feature/jwt-auth

# Subsequent pushes
git push
```

**Force Push Handling**:
- **NEVER** force push without explicit user confirmation
- Warn if rebase detected that requires force push
- Suggest `--force-with-lease` if force is necessary

**TOON Handoff for Push**:
```toon
from: plan-finalize-skill
to: cui-git-workflow-skill
handoff_id: push-001

operation: push-changes
plan_directory: .claude/plans/jwt-auth/

push:
  branch: feature/jwt-auth
  remote: origin
  set_upstream: true

validation:
  check_ahead: true
  verify_branch: true

next_action: Push to remote
```

### Step 6: Create or Update PR

**Purpose**: Create new PR or update existing one.

**PR Detection**:
```bash
# Check for existing PR
gh pr view --json number,state 2>/dev/null || echo "NO_PR"
```

**Create New PR**:
```bash
gh pr create \
  --title "feat(auth): Add JWT Authentication (#123)" \
  --body "$(cat <<'EOF'
## Summary

- Implement JWT token generation with RS256 signing
- Add token validation service
- Implement refresh token rotation
- Include comprehensive test coverage (85%)

## Changes

### New Files
- `JwtService.java` - Token generation service
- `TokenValidator.java` - Validation logic
- `RefreshTokenService.java` - Token rotation

### Test Coverage
- 47 unit tests
- 85% line coverage
- All edge cases covered

## Verification

- [x] Build passes (`mvn clean install`)
- [x] All tests pass
- [x] Quality gate passed (Sonar)
- [x] Documentation complete

## Related

- Fixes #123
- ADR-015: JWT Authentication Strategy
- IF-042: Authentication Service Interface

---
Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main \
  --head feature/jwt-auth
```

**Update Existing PR**:
```bash
# Update PR body with new information
gh pr edit --body "$(cat <<'EOF'
...updated body...
EOF
)"

# Add comment for significant updates
gh pr comment --body "Updated implementation based on review feedback"
```

**TOON Handoff for PR Creation**:
```toon
from: plan-finalize-skill
to: pr-workflow-skill
handoff_id: pr-001

operation: create-pr
plan_directory: .claude/plans/jwt-auth/

pr:
  title: "feat(auth): Add JWT Authentication (#123)"
  base: main
  head: feature/jwt-auth
  draft: false

body_template:
  summary: true
  changes: true
  verification: true
  related_docs: true

references:
  issue: "#123"
  adrs[1]: ADR-015
  interfaces[1]: IF-042

next_action: Create pull request
```

### Step 7: Handle PR Workflow (Review Loop)

**Purpose**: Process review feedback and iterate until approved.

**Workflow Loop**:
```
1. Wait for review
2. Fetch review comments
3. Triage comments
4. Implement changes or respond
5. Push updates
6. Repeat until approved
```

**Fetch Review Comments**:
```toon
from: plan-finalize-skill
to: pr-workflow-skill
handoff_id: review-001

operation: fetch-comments
pr_number: 456

filters:
  unresolved_only: true
  exclude_bot_comments: true

next_action: Fetch PR review comments
```

**Comment Triage Actions**:

| Pattern | Action | Priority |
|---------|--------|----------|
| security, vulnerability | code_change | high |
| bug, error, fix | code_change | high |
| please add/remove/change | code_change | medium |
| rename, variable name | code_change | low |
| why, explain, reasoning | explain | low |
| lgtm, approved | ignore | none |

**Handle Code Change Request**:
```toon
from: plan-finalize-skill
to: java-implement-agent
handoff_id: fix-001

operation: implement-fix
comment:
  id: "comment-123"
  path: "JwtService.java"
  line: 67
  body: "Please add null check for token parameter"

context:
  file: src/main/java/com/example/auth/JwtService.java
  method: validateToken

next_action: Implement requested change
```

**Push Review Fixes**:
```bash
git add -A
git commit -m "fix(auth): address review comments

- Add null check in JwtService.validateToken
- Improve error message clarity
- Add missing test case for empty token

---
Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

### Step 8: Update Progress and Complete

**Purpose**: Mark finalize phase complete and update plan.

**Update Plan Progress**:
```toon
from: plan-finalize-skill
to: plan-files-skill
handoff_id: progress-001

operation: update-progress
plan_directory: .claude/plans/jwt-auth/

update:
  task_id: finalize-task-1
  status: completed
  checklist_items[5]: 0, 1, 2, 3, 4

phase_status:
  phase: finalize
  status: completed
```

**Add Final References**:
```toon
from: plan-finalize-skill
to: plan-files-skill
handoff_id: refs-001

operation: write-references
plan_directory: .claude/plans/jwt-auth/

action: add
reference_type: pr
reference_data:
  url: "https://github.com/org/repo/pull/456"
  title: "feat(auth): Add JWT Authentication (#123)"
  status: open
```

**Completion Report**:
```toon
from: plan-finalize-skill
to: orchestrator
handoff_id: complete-001

task:
  description: Finalize phase complete
  status: completed

finalize_summary:
  commits: 1
  commit_hash: abc123def
  pr_url: "https://github.com/org/repo/pull/456"
  pr_status: open
  reviews_processed: 0

plan_status:
  all_phases_complete: true
  ready_for_merge: true

next_action: Await PR approval and merge
```

---

## Error Handling

### Build Artifacts in Commit

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-001

task:
  status: blocked

error:
  type: artifacts_detected
  message: Build artifacts detected in staging area
  details:
    artifacts[3]:
    - target/classes/JwtService.class
    - target/test-classes/JwtServiceTest.class
    - .idea/workspace.xml

alternatives[3]:
- Clean artifacts and retry commit
- Review .gitignore configuration
- Manually exclude specific files
```

### Push Rejected

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-002

task:
  status: blocked

error:
  type: push_rejected
  message: Push rejected by remote
  details:
    reason: non-fast-forward
    remote_commits: 3

alternatives[3]:
- Fetch and rebase on remote changes
- Merge remote changes into branch
- Force push (requires confirmation)
```

### PR Creation Failed

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-003

task:
  status: blocked

error:
  type: pr_creation_failed
  message: Failed to create pull request
  details:
    reason: "A pull request already exists for this branch"
    existing_pr: 455

alternatives[2]:
- Update existing PR instead
- Close existing PR and create new one
```

### Review Feedback Conflict

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-004

task:
  status: blocked

error:
  type: review_conflict
  message: Conflicting review feedback received
  details:
    comment_1: "Please add null check"
    comment_2: "Remove defensive programming, use assertions"
    conflict: Both address same code location

alternatives[2]:
- Ask user to clarify preferred approach
- Implement reviewer 1's suggestion (higher priority)
```

### Merge Conflicts

```toon
from: plan-finalize-skill
to: caller
handoff_id: error-005

task:
  status: blocked

error:
  type: merge_conflict
  message: Merge conflicts detected with base branch
  details:
    conflicts[2]:
    - src/main/java/com/example/auth/SecurityConfig.java
    - src/main/resources/application.properties
    base_branch: main
    commits_behind: 5

alternatives[3]:
- Rebase on main and resolve conflicts
- Merge main into feature branch
- Ask user for conflict resolution guidance
```

---

## User Interaction Points

### 1. Commit Message Confirmation

```
Generated commit message:
feat(auth): add JWT token validation service

Accept? (y/n/edit)
```

### 2. PR Title/Description Review

```
PR will be created with:
Title: feat(auth): Add JWT Authentication (#123)
Body: [summary of changes]

Proceed? (y/n/edit)
```

### 3. Review Comment Resolution

```
Review comment from @reviewer:
"Please add null check for token parameter"

Options:
1. Implement change
2. Explain why current approach is correct
3. Ask for clarification
4. Skip (mark as resolved)

Select action:
```

### 4. Force Push Warning

```
WARNING: Force push required due to rebase.
This will overwrite remote history.

Are you sure? (y/n)
```

---

## Integration Points

### Delegations to Other Skills/Agents

| Skill/Agent | When Used | Purpose |
|-------------|-----------|---------|
| **cui-git-workflow** | Step 3-5 | Commit message, staging, commit |
| **pr-workflow** | Step 6-7 | PR creation, review handling |
| **plan-files** | Throughout | Plan/config reading, progress updates |
| **java-implement-agent** | Step 7 | Implement review fixes (Java) |
| **js-implement-agent** | Step 7 | Implement review fixes (JS) |

### Tools Used

| Tool | Operations |
|------|------------|
| **Bash(git:*)** | All git operations |
| **Bash(gh:*)** | GitHub CLI for PRs |
| **Read** | File content for commit scope |
| **Edit** | Plan updates, review fixes |
| **Glob** | Artifact detection |

---

## Commit Strategy Patterns

### Fine-Granular Commits

```
Commit 1: feat(auth): add JWT token generation service
  - JwtService.java
  - JwtServiceTest.java

Commit 2: feat(auth): add token validation logic
  - TokenValidator.java
  - TokenValidatorTest.java

Commit 3: feat(auth): add refresh token rotation
  - RefreshTokenService.java
  - RefreshTokenServiceTest.java

Commit 4: feat(auth): configure JWT settings
  - application.properties
  - SecurityConfig.java
```

### Single Commit

```
Commit: feat(auth): add JWT authentication system

All 8 files in single commit with comprehensive message.
```

### Squash Before PR

```
Original: 5 commits during implementation

Squashed: feat(auth): add JWT authentication system (#123)
- Combines all implementation commits
- Preserves full message in body
```

---

## PR Templates

### Standard PR Body

```markdown
## Summary

{1-3 bullet points describing the change}

## Changes

### New Files
{list of new files with descriptions}

### Modified Files
{list of modified files with change summary}

## Test Coverage

- {N} unit tests
- {N}% line coverage

## Verification

- [x] Build passes
- [x] All tests pass
- [x] Quality gate passed
- [x] Documentation complete

## Related

- Fixes #{issue_number}
- {ADR references}
- {Interface references}

---
Generated with [Claude Code](https://claude.com/claude-code)
```

### Review Response Template

```markdown
Addressed review feedback:

- {change 1}
- {change 2}

Commit: {hash}
```

---

## Quality Verification

Before marking finalize phase complete:

- [ ] All commits follow conventional commits format
- [ ] No build artifacts committed
- [ ] PR created with complete description
- [ ] All review comments addressed
- [ ] Build passes on PR branch
- [ ] Quality gate passes on PR
- [ ] Documentation updated as needed
- [ ] Issue linked in PR

---

## Related

- [Handoff Protocol](handoff.md) - TOON incoming/outgoing specifications
- [Verify Phase](../plan-verify/verify.md) - Previous phase specification
- [Plan Types](../plan-types.md) - Init phase router
- [cui-git-workflow Skill](../../../marketplace/bundles/cui-task-workflow/skills/cui-git-workflow/SKILL.md) - Git commit standards
- [pr-workflow Skill](../../../marketplace/bundles/cui-task-workflow/skills/pr-workflow/SKILL.md) - PR handling
- [Templates & Workflow](../templates-workflow.md) - Phase workflow details
- [Persistence](../plan-files/persistence.md) - File format specifications
