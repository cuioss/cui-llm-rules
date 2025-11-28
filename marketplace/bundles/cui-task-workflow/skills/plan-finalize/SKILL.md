---
name: plan-finalize
description: Finalize phase skill for plan management. Handles final commits, PR creation, and workflow automation (Sonar fixes, review requests). Marks plan as complete and archives results.
allowed-tools: Read, Write, Edit, Bash, Skill, Task, AskUserQuestion
---

# Plan Finalize Skill

**EXECUTION MODE**: Execute finalization tasks immediately. Do not explain or summarize.

**Role**: Fifth and final phase skill in the plan management system. Commits changes, creates PRs, and handles workflow automation. Delegates all file I/O to `plan-files` skill.

## Standards (Load On-Demand)

### Workflow
```
Read standards/workflow.md
```
Contains: Phase overview, finalizing modes, commit strategy, PR template, completion report

---

## Operation: commit-changes

**Input**: `plan_directory`

**Steps**:

1. **Read config**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-config
   ```
   Extract: commit_strategy, branch, task_title

2. **Handle commit strategy**:

   | Strategy | Action |
   |----------|--------|
   | fine-granular | Verify commits exist, no additional commit |
   | phase-specific | Single commit for all phase changes |
   | complete | Single commit for all work |

3. **Delegate to git workflow** (for phase-specific or complete):
   ```
   Skill: cui-task-workflow:cui-git-workflow
   message: feat: {task-title}
   push: true
   ```

4. **Report status**: Commit hash, message, branch, files changed

---

## Operation: create-pr

**Input**: `plan_directory`

**Steps**:

1. **Check existing PR**: `gh pr list --head {branch} --json number,url`

2. **If no PR, create**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-plan, get-references
   ```

   ```bash
   gh pr create --title "{task-title}" --body "$(cat <<'EOF'
   ## Summary
   {description}

   **Related Issue**: {issue-link}

   ## Changes
   {key changes}

   ## Testing
   - Build: ✅ Passed
   - Tests: {count} passed
   - Coverage: {percentage}%

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

3. **If PR exists**: `gh pr edit {number} --body "{updated}"`

4. **Link issue**: `gh pr edit {number} --add-issue {issue-number}`

5. **Add reviewers** (if configured): `gh pr edit {number} --add-reviewer {list}`

---

## Operation: pr-workflow

**Input**: `plan_directory`, `finalizing` (pr-workflow|manual-pr|commit-only)

**Steps**:

1. **Determine workflow** from config:

   | Mode | Actions |
   |------|---------|
   | pr-workflow | Full automation: fix Sonar, request reviews |
   | manual-pr | PR created, manual follow-up |
   | commit-only | No PR |

2. **Execute PR workflow** (if pr-workflow):
   ```
   SlashCommand: /cui-task-workflow:pr-doctor
   ```

3. **Report status** per mode

---

## Operation: complete-plan

**Input**: `plan_directory`

**Steps**:

1. **Verify all tasks complete**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-plan
   ```
   Check: All tasks in all phases are `[x]`

2. **Update plan status**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: update-progress
   task_id: {last-finalize-task}
   status: completed
   ```

3. **Generate completion report** (see `standards/workflow.md` for template)

4. **Archive plan** (optional):
   ```bash
   mv {plan_directory} .claude/plans/archive/{task-name}-{date}/
   ```

---

## Error Handling

### Commit Conflict
Options: Resolve manually / Abort / View details

### PR Creation Failed
Options: Push and retry / Create manually / Skip

### Sonar Gate Failed
Options: Fix issues / Request exception / Proceed anyway

---

## Integration

### Command Integration
- **/plan-execute** - Primary command invoking this skill via phase-management

### Skills Used
- **plan-files** - All file I/O operations
- **cui-git-workflow** - Git commit operations
- **pr-workflow** - PR automation and Sonar fixes
- **phase-management** - Orchestration (invokes this skill)

### Related Skills
- **plan-init** - Init phase
- **plan-refine** - Refine phase
- **plan-implement** - Implement phase
- **plan-verify** - Previous phase

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to plan-files skill
- [x] All finalizing modes supported
- [x] PR creation with formatting
- [x] Commit via cui-git-workflow
