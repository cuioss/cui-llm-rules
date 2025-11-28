# Migration Plan

## CRITICAL RULES

### Before Starting Implementation

```
Skill: cui-plugin-development-tools:plugin-architecture
```

Load this skill FIRST to understand component patterns, frontmatter standards, and architecture rules.

### Execution Rules

1. **Execute tasks ONE-AFTER-ANOTHER** - Do not parallelize implementation tasks
2. **After each task completion** - Mark the checkbox as done `[x]`
3. **Run /plugin-doctor after each component** - Verify before proceeding
4. **Do not skip verification steps** - Each phase has validation tasks

---

## Overview

Step-by-step migration from unified `/task` command to split `/plan-manage` and `/plan-execute` commands.

**Immediate removal**: Old `/task` command and `Orchestrate Task` workflow are deleted immediately, not deprecated.

---

## Phase 1: Script Updates

### 1.1 Update discover-plans.py

- [x] Add `--filter` parameter to discover-plans.py
- [x] Implement filter logic for phases: init, refine, implement, verify, finalize
- [x] Implement filter logic for statuses: completed, in_progress, pending
- [x] Update JSON output to include `filter_applied` and `filtered_count`
- [x] Update `--help` text with filter examples

**File**: `marketplace/bundles/cui-task-workflow/skills/phase-management/scripts/discover-plans.py`

### 1.2 Create test for discover-plans.py filter

- [x] Create test file `test/cui-task-workflow/phase-management/test_discover_plans_filter.py`
- [x] Add test: `test_filter_by_single_phase`
- [x] Add test: `test_filter_by_multiple_phases`
- [x] Add test: `test_filter_by_status_completed`
- [x] Add test: `test_filter_no_matches_returns_empty`
- [x] Add test: `test_filter_preserves_recommendation_logic`
- [x] Run tests: `python3 -m pytest test/cui-task-workflow/phase-management/test_discover_plans_filter.py -v`

**Test commands after update**:
```bash
python3 scripts/discover-plans.py .claude/plans/
python3 scripts/discover-plans.py .claude/plans/ --filter=init
python3 scripts/discover-plans.py .claude/plans/ --filter=implement,verify,finalize
python3 scripts/discover-plans.py .claude/plans/ --filter=completed
```

---

## Phase 2: Skill Updates

### 2.1 Update phase-management SKILL.md

- [x] Add `Operation: list-plans` specification
- [x] Add `Operation: cleanup-plans` specification
- [x] Add `Operation: init-plan` specification
- [x] Add `Operation: refine-plan` specification
- [x] Add `Operation: discover-executable` specification
- [x] Add `Workflow: Manage Plans` specification
- [x] Add `Workflow: Execute Plans` specification
- [x] **REMOVE** `Workflow: Orchestrate Task` (immediate removal, no deprecation)
- [x] Update Integration section to reference new commands

**File**: `marketplace/bundles/cui-task-workflow/skills/phase-management/SKILL.md`

### 2.2 Verify phase-management skill

- [x] Run `/plugin-doctor` on `cui-task-workflow:phase-management`
- [x] Fix any issues reported
- [x] Confirm skill loads without errors

---

## Phase 3: Command Changes

### 3.1 Create plan-manage.md

- [x] Create command file `marketplace/bundles/cui-task-workflow/commands/plan-manage.md`
- [x] Add frontmatter (name, description)
- [x] Add parameters section (action, task, issue, plan)
- [x] Add workflow section referencing `Workflow: Manage Plans`
- [x] Add usage examples
- [x] Add related commands section

**Content source**: See [plan-manage.md](plan-manage.md) specification

### 3.2 Verify plan-manage command

- [x] Run `/plugin-doctor` on `cui-task-workflow` bundle (commands check)
- [x] Fix any issues reported
- [x] Confirm command is discoverable via `/plan-manage --help` or similar

### 3.3 Create plan-execute.md (replace task.md)

- [x] Create command file `marketplace/bundles/cui-task-workflow/commands/plan-execute.md`
- [x] Add frontmatter (name, description)
- [x] Add parameters section (plan, phase) - NO task/issue/action params
- [x] Add workflow section referencing `Workflow: Execute Plans`
- [x] Add usage examples (execution focus only)
- [x] Add related commands section pointing to `/plan-manage`

**Content source**: See [plan-execute.md](plan-execute.md) specification

### 3.4 Verify plan-execute command

- [x] Run `/plugin-doctor` on `cui-task-workflow` bundle (commands check)
- [x] Fix any issues reported
- [x] Confirm command is discoverable

### 3.5 Delete old task.md

- [x] **DELETE** `marketplace/bundles/cui-task-workflow/commands/task.md` (immediate removal)
- [x] Verify no broken references in bundle

---

## Phase 4: Documentation Updates

### 4.1 Update specification README.md

- [x] Update Operations Summary table with new commands
- [x] Replace `/task` references with `/plan-manage` and `/plan-execute`
- [x] Update navigation section

**File**: `plan/task/06-plan-management-specification/README.md`

### 4.2 Update decomposition.md

- [x] Update all usage examples to use new commands
- [x] Replace `/task` → `/plan-manage` or `/plan-execute` as appropriate

**File**: `plan/task/06-plan-management-specification/decomposition.md`

### 4.3 Update plan.md

- [x] Mark this migration as a completed phase (N/A - file doesn't exist)
- [x] Update any /task references (N/A - file doesn't exist)

**File**: `plan/task/06-plan-management-specification/plan.md`

---

## Phase 5: Final Verification

### 5.1 Bundle verification

- [x] Run `/plugin-doctor` on full `cui-task-workflow` bundle
- [x] Verify all commands are listed correctly
- [x] Verify all skills are listed correctly
- [x] Fix any remaining issues

### 5.2 Integration test scenarios

Manual testing (document results):

```bash
# Test plan-manage list (default action)
/plan-manage
# Expected: Shows numbered list of plans, prompts for selection

# Test plan-manage init
/plan-manage action=init task="Test feature"
# Expected: Creates new plan, offers to continue to refine

# Test plan-manage refine
/plan-manage action=refine
# Expected: Shows plans in refine phase for selection

# Test plan-manage cleanup
/plan-manage action=cleanup
# Expected: Shows completed plans, asks for deletion confirmation

# Test plan-execute (no params)
/plan-execute
# Expected: Shows executable plans (implement/verify/finalize phases)

# Test plan-execute with plan (by name, not path)
/plan-execute plan="test-feature"
# Expected: Executes current phase of specified plan

# Verify old /task is gone
/task
# Expected: Command not found or error
```

---

## Implementation Checklist Summary

### Phase 1: Scripts
- [x] 1.1 Update discover-plans.py with --filter
- [x] 1.2 Create filter tests
- [x] 1.2 Run and pass all tests

### Phase 2: Skill
- [x] 2.1 Add all new operations to phase-management
- [x] 2.1 Add new workflows to phase-management
- [x] 2.1 Remove Orchestrate Task workflow
- [x] 2.2 Run /plugin-doctor and fix issues

### Phase 3: Commands
- [x] 3.1 Create plan-manage.md
- [x] 3.2 Run /plugin-doctor and fix issues
- [x] 3.3 Create plan-execute.md
- [x] 3.4 Run /plugin-doctor and fix issues
- [x] 3.5 Delete task.md

### Phase 4: Documentation
- [x] 4.1 Update README.md
- [x] 4.2 Update decomposition.md
- [x] 4.3 Update plan.md (N/A - file doesn't exist)

### Phase 5: Verification
- [x] 5.1 Run /plugin-doctor on full bundle
- [ ] 5.2 Complete integration test scenarios (manual testing)

---

## Files Changed Summary

### Created
- `marketplace/bundles/cui-task-workflow/commands/plan-manage.md`
- `marketplace/bundles/cui-task-workflow/commands/plan-execute.md`
- `test/cui-task-workflow/phase-management/test_discover_plans_filter.py`

### Modified
- `marketplace/bundles/cui-task-workflow/skills/phase-management/scripts/discover-plans.py`
- `marketplace/bundles/cui-task-workflow/skills/phase-management/SKILL.md`
- `plan/task/06-plan-management-specification/README.md`
- `plan/task/06-plan-management-specification/decomposition.md`
- `plan/task/06-plan-management-specification/plan.md`

### Deleted
- `marketplace/bundles/cui-task-workflow/commands/task.md`
