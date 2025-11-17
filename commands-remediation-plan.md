# Commands Remediation Plan

**Generated**: 2025-11-17
**Updated**: 2025-11-17 (Phases 1-2 complete)
**Scope**: Marketplace commands diagnosis findings
**Remaining Issues**: 7 commands requiring fixes
**Priority**: Execute in order listed (HIGH → MEDIUM → LOW)

---

## Executive Summary

**✅ COMPLETED (6 fixes)**:
- Phase 1: Fixed 5 CONTINUOUS IMPROVEMENT RULE format issues
- Phase 2: Investigated 3 broken references (all false positives)
- Phase 3: Fixed 2 critical bloat issues (plugin-diagnose-agents, plugin-diagnose-commands)
  - Created `cui-marketplace-orchestration-patterns` skill (92.5/100 quality)
  - Reduced 39 lines total, improved architecture documentation

**⏳ REMAINING (7 fixes)**:
- **4 LARGE/BLOATED commands** requiring optimization
- **3 commands** with actual broken references (need investigation)

**Expected Impact**:
- Bloat reduction: ~450 lines remaining across 4 commands
- Fix broken runtime failures in 3 commands

---

## MEDIUM PRIORITY: Moderate Bloat Issues (4 Commands)

### 3. js-maintain-tests (534 lines → ~444 lines)

**Current State**: LARGE (bloat score: 134 - approaching BLOATED)

**Issue**: Contains extractable test improvement categories (lines 413-449) and verification checklist.

**Remediation**:

```bash
/plugin-update-command command-name=js-maintain-tests update="Extract TEST IMPROVEMENT CATEGORIES section (lines 413-449, ~70 lines) to cui-javascript-maintenance skill. Extract test quality verification checklist (lines 315-328) to same skill. Reference skill instead of inline documentation. Reduce from 534 to ~444 lines."
```

**Expected Reduction**: 90 lines (16.9%)

**Files to Modify**:
- `/marketplace/bundles/cui-frontend-expert/commands/js-maintain-tests.md`
- `/marketplace/bundles/cui-frontend-expert/skills/cui-javascript-maintenance/` (add standards files)

---

### 4. java-implement-tests (530 lines → optimize structure)

**Current State**: LARGE (bloat score: 133 - just over threshold)

**Issue**: Well-structured command, just slightly over 500-line threshold.

**Remediation**:

```bash
/plugin-update-command command-name=java-implement-tests update="Minor optimization only - command is well-structured at 530 lines. Consider condensing verbose sections if possible, but major restructuring not required. Focus on removing any redundant explanations."
```

**Expected Reduction**: 0-30 lines (0-6%)

**Files to Modify**:
- `/marketplace/bundles/cui-java-expert/commands/java-implement-tests.md`

**Note**: This is the lowest priority bloat fix - command quality is good.

---

### 5. plugin-diagnose-marketplace (523 lines → ~350 lines)

**Current State**: BLOATED (bloat score: 131)

**Issue**: Verbose validation procedures, duplicate validation patterns across Steps 2-5, educational overview content.

**Remediation**:

```bash
# Step 1: Create validate-marketplace-config skill (if not exists from #3)
/plugin-create-skill bundle-name=cui-plugin-development-tools skill-name=validate-marketplace-config

# Step 2: Update command
/plugin-update-command command-name=plugin-diagnose-marketplace update="Extract Steps 2-5 validation logic (~150 lines) to validate-marketplace-config skill. Move Overview section (lines 10-45, educational content) to separate architecture guide. Condense phase transition warnings (lines 286-305) to single note. Trust AI inference for JSON parsing - remove over-specification. Reduce from 523 to ~350 lines."
```

**Expected Reduction**: 173 lines (33.1%)

**Files to Modify**:
- `/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-marketplace.md`

**Skills to Create/Update**:
- `validate-marketplace-config` (consolidate with validate-bundle-inventory if appropriate)

---

### 6. java-maintain-tests (512 lines → ~380 lines)

**Current State**: BLOATED (bloat score: 128)

**Issue**: Duplicate build verification steps, over-specified bug detection protocol, extractable test improvement procedures.

**Remediation**:

```bash
# Step 1: Create test-improvement-procedures skill
/plugin-create-skill bundle-name=cui-java-expert skill-name=test-improvement-procedures

# Add to standards/:
# - scope-specific-improvements.md (lines 172-244 from java-maintain-tests)

# Step 2: Create test-maintenance-error-handling skill
/plugin-create-skill bundle-name=cui-java-expert skill-name=test-maintenance-error-handling

# Step 3: Update command
/plugin-update-command command-name=java-maintain-tests update="Fix CONTINUOUS IMPROVEMENT RULE to use correct self-update pattern (not caller-reporting). Extract test improvement procedures (lines 172-244, ~72 lines) to test-improvement-procedures skill. Consolidate duplicated build verification steps (appears 3x, ~75 lines saved). Remove over-specified bug detection protocol - trust AI inference. Extract error handling protocols (lines 424-460) to skill. Reduce from 512 to ~380 lines."
```

**Expected Reduction**: 132 lines (25.8%)

**Files to Modify**:
- `/marketplace/bundles/cui-java-expert/commands/java-maintain-tests.md`

**Skills to Create**:
- `test-improvement-procedures`
- `test-maintenance-error-handling`

---

## HIGH PRIORITY: Broken References (3 Commands)

### 7. tools-audit-permission-wildcards

**Issue**: References `/cui-utilities:tools-check-file-permissions` (lines 71, 85) but command doesn't exist.

**Investigation Needed**:
- Is this a typo? Similar command exists: `tools-check-permission-wildcards`
- Should the missing command be created?
- Should references be removed?

**Remediation Options**:

**Option A - Fix typo** (if it's meant to be tools-check-permission-wildcards):
```bash
/plugin-update-command command-name=tools-audit-permission-wildcards update="Fix broken references on lines 71 and 85. Change '/cui-utilities:tools-check-file-permissions' to '/cui-utilities:tools-check-permission-wildcards' (correct existing command name)."
```

**Option B - Create missing command**:
```bash
# Create the missing command
/plugin-create-command bundle-name=cui-utilities command-name=tools-check-file-permissions
# Then update references to use correct format
```

**Option C - Remove references**:
```bash
/plugin-update-command command-name=tools-audit-permission-wildcards update="Remove broken SlashCommand references on lines 71 and 85 (command doesn't exist). Update workflow to not depend on non-existent command."
```

**Recommended**: Option A (likely a naming error)

---

### 8. doc-review-technical-docs

**Issue**: References `/cui-documentation-standards:doc-analyze-technical-quality` (line 27) and lists it in Related Resources (line 59), but this command/agent doesn't exist.

**Investigation Needed**:
- Was this planned but never created?
- Should it be implemented inline instead?
- Should references be removed?

**Remediation Options**:

**Option A - Create missing agent**:
```bash
/plugin-create-agent bundle-name=cui-documentation-standards agent-name=doc-analyze-technical-quality
# Implement technical documentation analysis functionality
# Then no changes needed to doc-review-technical-docs
```

**Option B - Implement inline**:
```bash
/plugin-update-command command-name=doc-review-technical-docs update="Remove SlashCommand invocation of non-existent doc-analyze-technical-quality (line 27). Implement analysis logic inline in workflow. Remove Related Resources reference (line 59). Update workflow to be self-contained."
```

**Option C - Reference existing alternative**:
```bash
# If equivalent functionality exists elsewhere, update references to point to it
/plugin-update-command command-name=doc-review-technical-docs update="Update references from doc-analyze-technical-quality to [existing-alternative-command]."
```

**Recommended**: Option A (create the missing agent for proper separation of concerns)

---

### 9. maven-build-and-fix

**Issue**: 3 reference problems:
- Line 90: `java-code-analyzer` agent doesn't exist
- Line 93: `maven-dependency-analyzer` agent doesn't exist
- Line 96: `/cui-maven-run-integration-tests` uses wrong format (should be `/cui-maven:maven-run-integration-tests`)

**Remediation**:

```bash
# Fix #1: Incorrect command reference format (easiest)
/plugin-update-command command-name=maven-build-and-fix update="Fix line 96 reference format. Change '/cui-maven-run-integration-tests' to '/cui-maven:maven-run-integration-tests' (correct bundle:command format)."

# Fix #2 & #3: Investigate missing agents
# Option A: Create missing agents if they should exist
# Option B: Remove references if they're obsolete
# Option C: Use alternative agents if equivalents exist

# Recommended: Check if these agents were planned or are obsolete, then either create or remove references
```

**Priority**: Fix format issue immediately (line 96), investigate missing agents separately.

---

## ✅ COMPLETED: CONTINUOUS IMPROVEMENT RULE Format Fixes (5 Commands)

All 5 commands with CONTINUOUS IMPROVEMENT RULE format issues have been fixed:
- ✅ java-generate-coverage - Updated to imperative format with explicit command-name parameter
- ✅ js-generate-coverage - Changed from caller-reporting to self-update pattern
- ✅ plugin-create-bundle - Updated to proper parameter format
- ✅ js-fix-jsdoc - Changed to imperative format with self-update instruction
- ✅ maven-build-and-fix - Fixed to use self-update pattern

---

## Execution Status

**✅ COMPLETED**:
- ✅ Phase 1: Quick Wins - Fixed 5 CONTINUOUS IMPROVEMENT RULE format issues
- ✅ Phase 2: Reference Investigation - Verified 3 broken references were false positives
- ✅ Phase 3: Critical Bloat (4/4 COMPLETE):
  - ✅ plugin-diagnose-agents (621→599 lines, created cui-marketplace-orchestration-patterns skill)
  - ✅ plugin-diagnose-commands (577→560 lines, reused orchestration skill)
  - ✅ plugin-diagnose-skills (564→394 lines, removed duplicate fix workflow)
  - ✅ plugin-diagnose-bundle (569→456 lines, removed duplicate fix workflow)
  - **Total Phase 3 reduction: 322 lines across 4 commands**

**⏳ REMAINING**:
- ⏳ Phase 4: Moderate Bloat (4 commands):
  - plugin-diagnose-marketplace (#5) - Create 1 skill, reduce 173 lines
  - java-maintain-tests (#6) - Create 2 skills, reduce 132 lines
  - js-maintain-tests (#3) - Update existing skill, reduce 90 lines
  - java-implement-tests (#4) - Minor optimization only
- ⏳ Phase 5: Actual Broken References (3 commands):
  - tools-audit-permission-wildcards (#7) - Needs investigation
  - doc-review-technical-docs (#8) - Needs investigation
  - maven-build-and-fix (#9) - Fix reference format

---

## Success Metrics

**✅ COMPLETED SO FAR:**
- **CONTINUOUS IMPROVEMENT RULE fixes**: 5 commands upgraded to proper self-update format
- **Bloat reduction**: 322 lines removed from 4 critical commands
- **New skills created**: 1 new skill (cui-marketplace-orchestration-patterns, 92.5/100 quality)
- **False positive investigation**: 3 reference issues verified as non-issues
- **All critical bloat issues resolved**: 4/4 commands now ACCEPTABLE or LARGE (none BLOATED)

**⏳ REMAINING TARGETS:**
- **Bloat reduction**: ~450 lines remaining across 4 moderate bloat commands
- **Average command size**: Target reduction from avg 525 lines to avg 410 lines (22% reduction)
- **Clean rate improvement**: From 47% clean to current ~55% clean, target ~70% clean
- **Runtime failures fixed**: 3 commands with actual broken references to repair
- **New skills to create**: 2-4 additional reusable skills (for moderate bloat fixes)

**Total effort remaining estimate**: 4-6 hours

---

## Notes

- Always run `/plugin-diagnose-commands` after each fix to verify improvements
- Test each command after modification to ensure functionality preserved
- Commit changes incrementally with clear commit messages
- Update this plan as you complete items (mark completed, update estimates)

---

**End of Remediation Plan**
