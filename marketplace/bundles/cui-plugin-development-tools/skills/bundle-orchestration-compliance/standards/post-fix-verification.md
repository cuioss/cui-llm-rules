# Post-Fix Verification

Mandatory verification using git status to confirm fixes were actually applied to files.

## Purpose

Prevents accepting agent "fix" claims without verifying actual file modifications occurred.

## The Problem

**Agents can claim fixes without actually editing files:**

1. Agent reports: "Fixed 9 references - added bundle prefixes"
2. Command accepts: "✅ 9 fixes applied"
3. Reality: `git status` shows 0 modified files
4. Actual result: Fixes were NOT applied

**Root cause:** Agents may:
- Generate edit commands but not execute them
- Report success without verification
- Fail silently due to tool errors
- Return claimed fixes in reports without actual edits

## The Solution

**After ANY fixes applied, MUST verify with git status:**

```bash
Bash: git status
```

**Then compare claimed fixes vs actual file modifications.**

## Verification Requirements

**Step 5i-verification: POST-FIX VERIFICATION (MANDATORY)**

**⚠️ CRITICAL**: After applying ANY fixes (Steps 5e-5i), you MUST verify actual file changes occurred.

**Execute:**
```
Bash: git status
```

**Verification checks:**
1. If reference fixes were "applied" by agents: `git status` MUST show modified .md files
2. If safe fixes were applied: `git status` MUST show modified files
3. If NO files show as modified but agents reported fixes: **FIXES FAILED** - agents did not actually edit files
4. Count actual modified files and compare to fix count

**Report verification:**
```
POST-FIX VERIFICATION:
- Fixes claimed: {total_fixes_from_agents}
- Files actually modified: {git_status_count}
- Verification: {PASS if counts match / FAIL if mismatch}
```

**If verification FAILS:**
- Report: "⚠️ WARNING: Agents claimed {X} fixes but only {Y} files were modified"
- Do NOT proceed to next bundle
- Investigate why fixes were not applied

## When to Execute

**Required when:**
- ANY fixes applied in Step 5g (safe fixes)
- ANY fixes applied in Step 5h (risky fixes)
- ANY reference fixes applied in Step 5f

**Not required when:**
- No fixes applied (nothing to verify)
- auto-fix=false AND user declined all risky fixes
- No issues found (Steps 5e-5i skipped legitimately)

**Mark as N/A when not required:**
```
✓ Step 5i-verification: Git status checked (N/A - no fixes applied)
```

## Parsing Git Status

**Extract modified file count:**

```bash
# Count modified files (not staged)
git status | grep "modified:" | wc -l

# Count both staged and unstaged
git status --short | wc -l
```

**Expected patterns:**

**Success (fixes applied):**
```
Changes not staged for commit:
  modified:   marketplace/bundles/cui-plugin-development-tools/commands/plugin-create-skill.md
  modified:   marketplace/bundles/cui-plugin-development-tools/commands/plugin-update-command.md
  modified:   marketplace/bundles/cui-plugin-development-tools/commands/plugin-update-agent.md
```
Result: 3 files modified

**Failure (fixes claimed but not applied):**
```
On branch main
nothing to commit, working tree clean
```
Result: 0 files modified (but agents claimed 9 fixes!)

## Handling Verification Failure

**If fixes claimed > files modified:**

1. **STOP - do not proceed to next bundle**
2. **Report failure:**
   ```
   ❌ POST-FIX VERIFICATION FAILED

   Agents claimed: 9 fixes
   Files modified: 0

   This means agents did not actually edit files despite reporting fixes.
   Diagnosis results are INVALID.

   Possible causes:
   - Agent Edit commands failed silently
   - Tool permissions issues
   - Agents generated fixes but didn't execute edits

   Action required:
   - Investigate why fixes were not applied
   - Re-run with verbose logging
   - Check agent tool access
   ```

3. **Offer options:**
   - Retry fix workflow
   - Continue without fixes (mark bundle as incomplete)
   - Abort entire diagnosis

## Handling Partial Success

**If fixes claimed = some files modified (but not all):**

```
⚠️ PARTIAL SUCCESS
Agents claimed: 9 fixes
Files modified: 4

Some fixes applied but not all. Possible causes:
- Some files had errors
- Some edits conflicted
- Mixed success/failure rates

Review git diff to see which files were modified.
```

## Integration Pattern

**In diagnose commands:**

```markdown
**Step 5i-verification: POST-FIX VERIFICATION (MANDATORY)**

Load verification patterns:
```
Skill: cui-plugin-development-tools:bundle-orchestration-compliance
Read: standards/post-fix-verification.md
```

**After applying ANY fixes (Steps 5e-5i):**

```
Bash: git status
```

Count modified files and compare to claimed fixes.

**Report:**
- Fixes claimed: {N}
- Files modified: {M}
- Verification: {PASS/FAIL}

If FAIL: STOP and investigate.
If PASS: Proceed to Step 5j.
```

## Git Status Examples

**Example 1: Reference fixes applied successfully**
```bash
$ git status
Changes not staged for commit:
  modified:   marketplace/bundles/cui-plugin-development-tools/commands/plugin-create-skill.md
  modified:   marketplace/bundles/cui-plugin-development-tools/commands/plugin-update-command.md
```
Claimed: 2 reference fixes
Modified: 2 files
Result: ✅ PASS

**Example 2: Fixes claimed but not applied**
```bash
$ git status
On branch main
nothing to commit, working tree clean
```
Claimed: 9 reference fixes
Modified: 0 files
Result: ❌ FAIL

**Example 3: Safe fixes applied**
```bash
$ git status
Changes not staged for commit:
  modified:   marketplace/bundles/cui-plugin-development-tools/commands/plugin-create-bundle.md
  modified:   marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md
```
Claimed: 2 CONTINUOUS IMPROVEMENT RULE additions
Modified: 2 files
Result: ✅ PASS

## Quality Standards

- Verification must use observable evidence (git status)
- Claimed vs actual counts must be compared
- Failures must stop progression
- Partial success must be noted
- Root cause guidance must be provided

## Enforcement

**Commands MUST:**
1. Execute git status after any fixes
2. Parse and count modified files
3. Compare to claimed fix count
4. Report PASS/FAIL explicitly
5. STOP if verification fails

**Commands MUST NOT:**
1. Trust agent reports without verification
2. Proceed with failed verification
3. Skip verification when fixes applied
4. Accept partial success without investigation
5. Assume fixes worked

## Related Standards

- `bundle-processing-rules.md` - Sequential processing requirements
- `mandatory-completion-checklist.md` - Includes verification in checklist (item 10)
- `anti-skip-protections.md` - Warnings against skipping verification
