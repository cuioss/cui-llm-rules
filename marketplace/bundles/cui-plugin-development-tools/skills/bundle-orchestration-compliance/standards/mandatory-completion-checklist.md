# Mandatory Completion Checklist

10-item checklist that MUST be verified before proceeding from one bundle to the next.

## Purpose

Prevents advancing to next bundle with incomplete processing of current bundle.

## The Checklist

**Step 5j: MANDATORY Bundle Completion Check**

**⚠️ BEFORE proceeding to next bundle, verify ALL of the following are complete:**

- [ ] **Step 5a**: All components analyzed (not partial subset)
- [ ] **Step 5b**: All components reference-validated (not partial subset)
- [ ] **Step 5c**: Results aggregated for bundle
- [ ] **Step 5d**: Bundle summary displayed
- [ ] **Step 5e**: Issues categorized (if any issues found)
- [ ] **Step 5f**: Reference issues handled (if any found)
- [ ] **Step 5g**: Safe fixes applied (if auto-fix=true and safe issues found)
- [ ] **Step 5h**: Risky fixes prompted (if any risky issues found)
- [ ] **Step 5i**: Fixes verified (if any fixes applied)
- [ ] **Step 5i-verification**: Git status checked (if any fixes applied)

**If ANY checkbox above is unchecked: STOP. Complete that step before proceeding.**

**Only after ALL steps complete: Proceed to next bundle**

## Usage Pattern

```markdown
**Step 5j: Verify Bundle Completion**

Before proceeding to next bundle, apply mandatory-completion-checklist from bundle-orchestration-compliance skill:

[Display 10-item checklist above]

**Verification:**
- Current bundle: {bundle-name}
- Components processed: {N}/{N} (100%)
- Steps completed: {N}/10 checklist items
- Ready for next bundle: {YES/NO}

If NO: Complete unchecked items.
If YES: Proceed to next bundle.
```

## Conditional Steps

**Some steps are conditional:**

**Step 5e (Categorize issues):**
- Required IF: Any issues found in Steps 5a or 5b
- Not required IF: All components CLEAN

**Step 5f (Handle reference issues):**
- Required IF: Reference validation found issues
- Not required IF: All references correct

**Step 5g (Apply safe fixes):**
- Required IF: auto-fix=true AND safe issues found
- Not required IF: auto-fix=false OR no safe issues

**Step 5h (Prompt risky fixes):**
- Required IF: Risky issues found
- Not required IF: No risky issues

**Step 5i (Verify fixes):**
- Required IF: Any fixes applied in 5g or 5h
- Not required IF: No fixes applied

**Step 5i-verification (Git status):**
- Required IF: Any fixes applied in 5g or 5h
- Not required IF: No fixes applied

**How to handle conditional steps:**

If step is "not required" for current bundle, mark as COMPLETE (✓) with note:

```
✓ Step 5e: Issues categorized (N/A - no issues found)
✓ Step 5g: Safe fixes applied (N/A - auto-fix disabled)
✓ Step 5i-verification: Git status checked (N/A - no fixes applied)
```

This ensures checklist is 100% complete even when some steps are skipped due to conditions.

## Verification Example

**Good (all items checked):**
```
Bundle: cui-plugin-development-tools
✓ Step 5a: 13/13 components analyzed
✓ Step 5b: 13/13 components reference-validated
✓ Step 5c: Results aggregated
✓ Step 5d: Bundle summary displayed
✓ Step 5e: Issues categorized (9 commands with issues)
✓ Step 5f: Reference issues handled (9 references fixed)
✓ Step 5g: Safe fixes applied (0 - none found)
✓ Step 5h: Risky fixes prompted (4 bloat issues - user declined)
✓ Step 5i: Fixes verified (reference fixes only)
✓ Step 5i-verification: Git status checked (0 files modified - fixes failed!)

⚠️ STOP: Git status verification failed. Fixes claimed but not applied.
Proceeding to next bundle: NO
```

**Bad (items missing):**
```
Bundle: cui-plugin-development-tools
✓ Step 5a: 13/13 components analyzed
✗ Step 5b: 4/13 components reference-validated (INCOMPLETE)
✗ Step 5c: Results aggregated (SKIPPED)
✗ Step 5d: Bundle summary displayed (SKIPPED)
... (rest skipped)

❌ VIOLATION: Cannot proceed to next bundle with 9/10 steps incomplete.
```

## Integration with Commands

**In plugin-diagnose-commands (and agents, skills):**

```markdown
**Step 5j: MANDATORY Bundle Completion Check**

Load and apply checklist from skill:
```
Skill: cui-plugin-development-tools:bundle-orchestration-compliance
Read: standards/mandatory-completion-checklist.md
```

[Display 10-item checklist]

Verify current bundle completion before proceeding.
```

## Enforcement

**Commands MUST:**
1. Display the checklist at Step 5j
2. Verify each item is complete
3. Not proceed if ANY item incomplete
4. Note conditional items as N/A when not applicable

**Commands MUST NOT:**
1. Skip the checklist
2. Proceed with incomplete items
3. Mark items as complete without verification
4. Assume steps are complete without checking

## Quality Standards

- Checklist must cover all critical steps
- Conditional steps must be clearly marked
- Verification must be explicit (not assumed)
- Incomplete items must stop progression
- Display format must be clear and scannable

## Related Standards

- `bundle-processing-rules.md` - Sequential processing requirements
- `anti-skip-protections.md` - Consequences of skipping steps
- `post-fix-verification.md` - Git status verification (item 10)
