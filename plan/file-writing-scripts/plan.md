# Implementation Plan: .claude File Writing Scripts

**Related**: See [analysis.md](./analysis.md) for detailed analysis

---

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

## Phase 1: Base Infrastructure

### Task 1.1: Create file-operations-base module

**Location**: `marketplace/bundles/cui-utilities/skills/file-operations-base/`

**Goal**: Extract common file writing patterns into reusable module

**Files to Create**:
- `SKILL.md` - Skill documentation
- `scripts/file-ops.py` - Core file operations module
- `scripts/test-file-ops.py` - Test suite

**Acceptance Criteria**:
- [x] Atomic file write with temp file + rename
- [x] Directory creation (mkdir -p equivalent)
- [x] JSON success/error output helpers
- [x] Markdown metadata parsing (key=value format)
- [x] Markdown metadata generation
- [x] All tests pass

**Verification**:
- [x] Run `plugin-doctor` on `cui-utilities:file-operations-base`

---

## Phase 2: Lessons Learned Scripts

### Task 2.1: Create write-lesson.py

**Location**: `marketplace/bundles/cui-utilities/skills/claude-lessons-learned/scripts/`

**Goal**: Create new lesson MD files without Edit/Write tool

**Input Parameters**:
```
--component-type {command|agent|skill}
--component-name NAME
--component-bundle BUNDLE
--category {bug|improvement|pattern|anti-pattern}
--title TITLE
--detail DETAIL
[--example EXAMPLE]
[--related RELATED]
[--lessons-dir DIR]
```

**Acceptance Criteria**:
- [x] Generates unique ID (YYYY-MM-DD-NNN format)
- [x] Creates proper key=value metadata header
- [x] Writes markdown content sections
- [x] Creates directory if not exists
- [x] Outputs JSON with file path and ID
- [x] Test: `test-lessons-scripts.py::test_write_lesson`

---

### Task 2.2: Create update-lesson.py

**Location**: `marketplace/bundles/cui-utilities/skills/claude-lessons-learned/scripts/`

**Goal**: Update metadata in existing lesson files

**Input Parameters**:
```
--file PATH
--set KEY=VALUE [--set KEY=VALUE ...]
```

**Acceptance Criteria**:
- [x] Parses existing metadata
- [x] Updates specified key=value pairs
- [x] Preserves content unchanged
- [x] Atomic write
- [x] Outputs JSON with updated file path
- [x] Test: `test-lessons-scripts.py::test_update_lesson`

---

### Task 2.3: Update claude-lessons-learned SKILL.md

**Goal**: Replace Edit/Write tool usage with script calls

**Changes**:
- [x] Update `allowed-tools` to remove `Write, Edit`
- [x] Update "Workflow: Record Lesson" to use `write-lesson.py`
- [x] Update "Workflow: Mark Lesson Applied" to use `update-lesson.py`
- [x] Add scripts table with new scripts

**Verification**:
- [x] Run `plugin-doctor` on `cui-utilities:claude-lessons-learned`

---

## Phase 3: Plan Files Scripts

### Task 3.1: Create write-plan.py

**Location**: `marketplace/bundles/cui-task-workflow/skills/plan-files/scripts/`

**Goal**: Create/update plan.md from structured input

**Input Parameters**:
```
--plan-dir DIR
--title TITLE
--current-phase PHASE
--current-task TASK
--phases-json JSON_ARRAY
```

**Acceptance Criteria**:
- [x] Creates plan.md from template structure
- [x] Populates phase progress table
- [x] Generates task sections with checklists
- [x] Handles both create and update
- [x] Outputs JSON with file path
- [x] Test: `test-plan-scripts.py::test_write_plan`

---

### Task 3.2: Create write-config.py

**Location**: `marketplace/bundles/cui-task-workflow/skills/plan-files/scripts/`

**Goal**: Create config.md from structured input

**Input Parameters**:
```
--plan-dir DIR
--plan-type {implementation|simple}
--technology {java|javascript|mixed|none}
--build-system {maven|gradle|npm|npx|none}
--compatibility {breaking|deprecations}
--commit-strategy {fine-granular|phase-specific|complete}
--finalizing {commit-only|pr-workflow}
[--branch BRANCH]
[--issue ISSUE]
```

**Acceptance Criteria**:
- [x] Creates config.md with all tables
- [x] Validates enum values
- [x] Creates plan directory if not exists
- [x] Outputs JSON with file path
- [x] Test: `test-plan-scripts.py::test_write_config`

---

### Task 3.3: Create write-references.py

**Location**: `marketplace/bundles/cui-task-workflow/skills/plan-files/scripts/`

**Goal**: Create/update references.md

**Input Parameters**:
```
--plan-dir DIR
--action {add|update|remove|set}
--section {issue|branch|adrs|interfaces|implementation_files|external_docs|dependencies}
--value VALUE
[--key KEY]  # For update/remove in objects
```

**Acceptance Criteria**:
- [x] Creates references.md from template if not exists
- [x] Adds entries to appropriate sections
- [x] Updates existing entries
- [x] Removes entries
- [x] Outputs JSON with changes made
- [x] Test: `test-plan-scripts.py::test_write_references`

---

### Task 3.4: Create update-progress.py

**Location**: `marketplace/bundles/cui-task-workflow/skills/plan-files/scripts/`

**Goal**: Update checklist items and progress in plan.md

**Input Parameters**:
```
--plan-dir DIR
--phase PHASE
--task-id ID
--complete-items "ITEM1,ITEM2,..."
[--set-status {pending|in_progress|completed}]
```

**Acceptance Criteria**:
- [x] Locates correct task section
- [x] Updates checklist items `[ ]` → `[x]`
- [x] Updates phase progress table counts
- [x] Updates current task pointer if needed
- [x] Detects phase completion
- [x] Outputs JSON with progress status
- [x] Test: `test-plan-scripts.py::test_update_progress`

---

### Task 3.5: Update plan-files SKILL.md

**Goal**: Replace Edit/Write tool usage with script calls

**Changes**:
- [x] Update `allowed-tools` to remove `Write, Edit`
- [x] Update "Operation: write-plan" to use `write-plan.py`
- [x] Update "Operation: write-config" to use `write-config.py`
- [x] Update "Operation: write-references" to use `write-references.py`
- [x] Update "Operation: update-progress" to use `update-progress.py`
- [x] Add scripts table with new scripts

**Verification**:
- [x] Run `plugin-doctor` on `cui-task-workflow:plan-files`

---

## Phase 4: Integration Testing

### Task 4.1: End-to-end lessons-learned test

**Goal**: Verify complete workflow without prompts

**Test Scenario**:
1. Create lesson via `write-lesson.py`
2. Query lesson via `query-lessons.py`
3. Mark applied via `update-lesson.py`
4. Query again to verify

**Acceptance Criteria**:
- [x] No Edit/Write prompts during entire flow
- [x] Files created correctly in `.claude/lessons-learned/`

---

### Task 4.2: End-to-end plan-files test

**Goal**: Verify complete workflow without prompts

**Test Scenario**:
1. Create directory via `mkdir -p`
2. Create config via `write-config.py`
3. Create references via `write-references.py`
4. Create plan via `write-plan.py`
5. Update progress via `update-progress.py`
6. Parse plan via `parse-plan.py`

**Acceptance Criteria**:
- [x] No Edit/Write prompts during entire flow
- [x] Files created correctly in `.claude/plans/`
- [x] Parse output matches expected structure

---

### Task 4.3: Plugin-doctor verification

**Goal**: Verify all modified components pass quality checks

**Components to Verify**:
- [x] `cui-utilities:file-operations-base` (new)
- [x] `cui-utilities:claude-lessons-learned` (modified)
- [x] `cui-task-workflow:plan-files` (modified)

---

## Summary

| Phase | Tasks | New Scripts | Tests |
|-------|-------|-------------|-------|
| 1. Base Infrastructure | 1 | 1 | 1 |
| 2. Lessons Learned | 3 | 2 | 1 |
| 3. Plan Files | 5 | 4 | 1 |
| 4. Integration | 3 | 0 | 2 |
| **Total** | **12** | **7** | **5** |

---

## Dependencies

```
Phase 1 ──► Phase 2 ──► Phase 4
        └──► Phase 3 ──►
```

- Phase 2 and 3 can run in parallel after Phase 1
- Phase 4 requires Phase 2 and 3 complete

---

## Completion Criteria

All tasks marked `[x]` and:
- No Edit/Write tool usage for `.claude/` files in updated skills
- All plugin-doctor checks pass
- All integration tests pass
- Documentation updated
