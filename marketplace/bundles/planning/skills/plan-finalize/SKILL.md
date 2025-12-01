---
name: plan-finalize
description: Finalize phase skill for plan management. Handles final commits, PR creation, and workflow automation (Sonar fixes, review requests). Marks plan as complete and archives results.
allowed-tools: Read, Write, Edit, Bash, Skill, Task, AskUserQuestion
---

# Plan Finalize Skill

**EXECUTION MODE**: Execute finalization tasks immediately. Do not explain or summarize.

**OUTPUT RULES**:
- Do NOT narrate internal process or tool invocations
- Do NOT display raw script output - format as structured status
- DO show commit status, PR creation results, and completion summary
- Work silently until you have results to display

**MANDATORY PROGRESS TRACKING**:

After EVERY finalization task, you MUST call update-progress:
```
python3 {update-progress.py} --plan-dir {plan_directory} --phase finalize --task-id {task_id} --complete-items "{item_text}"
```

**NEVER skip this step**. The plan.md is the source of truth. Plan completion WILL FAIL if checklist items are not marked as `[x]`.

**Anti-Patterns** (DO NOT DO):
- Committing without updating progress
- Creating PR without marking progress
- Assuming git operations auto-update plan.md

**MANDATORY WORK-LOG**:

After completing significant actions, you MUST log via work-log skill:
```
Skill: planning:work-log
operation: log-entry
plan_directory: {plan_directory}
phase: finalize
task: {task_id}
action: "{what was done}"
result: "{outcome or artifact}"
```

**Entry Budget**: 1-2 entries for finalize phase.

**Log Points**:
- Commit created: action="Created commit", result="{commit hash}: {message summary}"
- PR submitted (if applicable): action="Created pull request", result="PR #{number}: {title}"
- Plan completed: action="Marked plan complete", result="All phases completed"

**Anti-Patterns** (DO NOT DO):
- Completing finalize without logging commit
- Not logging PR creation

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
   Skill: planning:plan-files
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
   Skill: planning:git-workflow
   message: feat: {task-title}
   push: true
   ```

4. **Report status**: Commit hash, message, branch, files changed

5. **Log commit**:
   ```
   Skill: planning:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: finalize
   task: task-1
   action: "Committed changes"
   result: "commit {short_hash}: {message}"
   ```

---

## Operation: create-pr

**Input**: `plan_directory`

**Steps**:

1. **Check existing PR**: `gh pr list --head {branch} --json number,url`

2. **If no PR, create**:
   ```
   Skill: planning:plan-files
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

6. **Log PR creation** (if PR created):
   ```
   Skill: planning:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: finalize
   task: task-2
   action: "Created pull request"
   result: "PR #{number}: {title}"
   ```

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
   SlashCommand: /planning:pr-doctor
   ```

3. **Report status** per mode

---

## Operation: complete-plan

**Input**: `plan_directory`

**Steps**:

1. **Verify all tasks complete**:
   ```
   Skill: planning:plan-files
   operation: read-plan
   ```
   Check: All tasks in all phases are `[x]`

2. **Update plan status**:
   ```
   Skill: planning:plan-files
   operation: update-progress
   task_id: {last-finalize-task}
   status: completed
   ```

3. **Generate completion report** (see `standards/workflow.md` for template)

4. **Archive plan** (optional):
   ```bash
   mv {plan_directory} {plan-storage}/archive/{task-name}-{date}/
   ```

5. **Log plan completion**:
   ```
   Skill: planning:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: finalize
   task: task-3
   action: "Plan completed successfully"
   result: "All {count} tasks completed"
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
- **git-workflow** - Git commit operations
- **pr-workflow** - PR automation and Sonar fixes
- **phase-management** - Orchestration (invokes this skill)
- **work-log** - Logging significant actions

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
- [x] Commit via git-workflow

---

## Continuous Improvement

**MANDATORY**: When executing scripts from this skill, unexpected behavior or errors MUST be documented as lessons learned immediately.

### When to Document

File a lesson learned when a script:
- Returns unexpected output
- Fails to update files as expected
- Requires a workaround to achieve the desired result
- Has unclear or misleading documentation

### How to Document

Use the `general-tools:manage-lessons-learned` skill:
```bash
python3 {write-lesson.py path} --component "planning:plan-finalize" --category {bug|improvement|anti-pattern} --title "Brief description" --detail "What happened, why, workaround, suggested fix"
```

**Categories**:
- `bug`: Script is broken or produces wrong results
- `improvement`: Script works but could be better
- `anti-pattern`: Script was misused or documentation unclear

**Why This Matters**: Script errors indicate gaps in validation, documentation, or implementation. Documented lessons improve future sessions and identify systemic issues.
