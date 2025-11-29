# Proposals: Fix Edit Tool Prompting During Plan Execution

**Date**: 2025-11-28
**Context**: Analysis of prompting behavior during `/plan-execute` for `analyze-task-implement-removal` plan

---

## Problem Analysis

### What Happened

During execution of the `analyze-task-implement-removal` plan, the Edit tool prompted for user confirmation multiple times:

1. First prompt: `update-progress.py` script execution (should have been allowed)
2. Subsequent prompts: Direct `Edit` tool calls to modify `plan.md`

### Root Cause

**The plan execution did NOT follow the designed architecture.**

| Component | Designed Behavior | Actual Behavior |
|-----------|-------------------|-----------------|
| `phase-management` skill | `allowed-tools: Read, Glob, Bash, Skill, AskUserQuestion` | Used correctly |
| `plan-files` skill | `allowed-tools: Read, Bash, AskUserQuestion` (no Edit) | NOT invoked |
| Plan modifications | Via `update-progress.py` script | Via direct `Edit` tool |

**Key Finding**: The `plan-files` skill was designed to be the ONLY component that writes to `.claude/plans/` files. It uses Python scripts (`update-progress.py`, `write-plan.py`, etc.) which execute via Bash and don't trigger prompts.

However, during plan execution:
1. I did NOT delegate to `plan-files` skill for updates
2. I used the `Edit` tool directly
3. The Edit tool ALWAYS prompts for `.claude/` directory files (security feature)

### Why Scripts Work But Edit Doesn't

From `analysis.md`:
> **Key Finding**: Python scripts executed via Bash can write to `.claude/` without prompts, while Edit/Write tools always prompt.

The `.claude/` directory has special security protection in Claude Code. The Edit/Write tools will ALWAYS prompt for files in this directory, regardless of permissions configured. This is by design.

The workaround (implemented in `plan/file-writing-scripts/plan.md`) is to use Python scripts that:
1. Execute via Bash tool (which CAN be pre-approved)
2. Write files atomically (temp file + rename)
3. Output JSON results

---

## Architecture Gap Analysis

### Current State (Scripts Exist, Not Used)

The scripts were implemented per `plan.md`:

| Script | Location | Purpose | Status |
|--------|----------|---------|--------|
| `update-progress.py` | `plan-files/scripts/` | Update checklist items | ✅ Exists |
| `write-plan.py` | `plan-files/scripts/` | Create/update plan.md | ✅ Exists |
| `write-config.py` | `plan-files/scripts/` | Create config.md | ✅ Exists |
| `write-references.py` | `plan-files/scripts/` | Update references.md | ✅ Exists |

### Missing Integration

The scripts exist but the orchestration layer (`phase-management`) doesn't consistently delegate to `plan-files` skill for all file modifications. Instead:

1. **Current behavior**: Direct Edit tool calls from main conversation
2. **Designed behavior**: Route through `plan-files` skill which uses scripts

---

## Proposals

### Proposal 1: Enforce Skill Delegation (Recommended)

**Change**: Update `phase-management` skill to ALWAYS delegate plan file modifications to `plan-files` skill.

**Implementation**:
1. Add explicit rule in `phase-management/SKILL.md`:
   ```
   **FILE MODIFICATION RULE**:
   NEVER use Edit/Write tools directly on .claude/plans/ files.
   ALWAYS delegate to plan-files skill operations:
   - update-progress → plan-files:update-progress
   - write-plan → plan-files:write-plan
   - etc.
   ```

2. Add enforcement in skill's "Operation:" sections to specify exact script calls.

**Pros**:
- Uses existing infrastructure
- No new code needed
- Aligns with original design

**Cons**:
- Relies on LLM following instructions (can still violate)

---

### Proposal 2: Add Plan-Files Script to scripts.local.json Permissions

**Current permissions** in `scripts.local.json`:
```json
"Bash(python3 /Users/oliver/git/cui-llm-rules/marketplace/bundles/cui-task-workflow/skills/plan-files/scripts/*.py:*)"
```

This permission IS present, but the script call was still prompted.

**Investigation needed**: Why did `update-progress.py` prompt despite matching permission pattern?

**Possible causes**:
1. Path mismatch (relative vs absolute)
2. Permission pattern not matching exact command format
3. Claude Code caching issue

---

### Proposal 3: Remove Skill Abstraction for Plan Updates

**Change**: Inline the script calls directly in phase-management instead of delegating to plan-files skill.

**Implementation**:
Replace skill delegation patterns like:
```
Skill: cui-task-workflow:plan-files
operation: update-progress
```

With direct script calls:
```bash
python3 {scripts.local.json path} --plan-dir ... --phase ... --task-id ... --complete-items "..."
```

**Pros**:
- More direct, less indirection
- Easier to debug

**Cons**:
- Duplicates knowledge across skills
- Harder to maintain

---

## Recommended Actions

1. **Immediate**: Add explicit instruction in phase-management to NEVER use Edit tool for plan files
2. **Short-term**: Verify script permissions are correctly applied (test `update-progress.py` directly)
3. **Medium-term**: Consider adding validation/enforcement that prevents Edit tool usage on `.claude/` paths

---

## Test Case

To verify fix works:

```bash
# This should NOT prompt:
python3 /Users/oliver/git/cui-llm-rules/marketplace/bundles/cui-task-workflow/skills/plan-files/scripts/update-progress.py \
  --plan-dir .claude/plans/analyze-task-implement-removal \
  --phase finalize \
  --task-id 2 \
  --complete-items "Mark plan complete"
```

If this prompts, the permission pattern is not matching correctly.
