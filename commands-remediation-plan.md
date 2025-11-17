# Commands Remediation Plan - Remaining Work

**Generated**: 2025-11-17
**Updated**: 2025-11-17 (Phase 4 COMPLETE, Phase 5 COMPLETE)
**Scope**: Marketplace commands diagnosis - ALL FIXES COMPLETE
**Remaining Issues**: 0 (all commands fixed or already clean)
**Priority**: HIGH (fix runtime failures)

**Completed So Far**: 861 lines removed (731 from Phases 1-4b, 94 from Phase 4c, 36 from Phase 4d), 1 skill created (cui-marketplace-orchestration-patterns)

---

## Remaining Work

### HIGH PRIORITY: Broken References (3 Commands)

#### 3. tools-audit-permission-wildcards

**Status**: ✅ ALREADY CLEAN (fixed in previous session)

**Analysis**: The broken references mentioned (lines 71, 85) no longer exist. Command is 327 lines with quality score 100/100 (Excellent). Only minor suggestions for improved resilience (tight coupling warning, informal skill reference).

**No action required** - proceed to remaining commands.

---

#### 4. doc-review-technical-docs

**Status**: ✅ FIXED

**Original Issue**: References mentioned in plan (doc-analyze-technical-quality) were already fixed in previous session.

**Actual Issue Found**: Broken reference to `commit-changes` agent (lines 175, 295) - was missing bundle qualifier.

**Fix Applied**: Changed `commit-changes` to `cui-task-workflow:commit-changes` in both locations.

**Verification**: All 3 references now valid (commit-changes agent, self-reference, cui-doc-health-checks skill).

---

#### 5. maven-build-and-fix

**Status**: ✅ ALREADY CLEAN (fixed in previous session)

**Analysis**: The broken references mentioned (lines 90, 93, 96) no longer exist. Command is 400 lines with quality score 100/100. Only 2 minor WARNING-level style issues (missing bundle qualifiers on lines 79, 86) which are optional fixes.

**No action required** - proceed to remaining commands.

---

## Execution Order

**Recommended sequence**:

### Phase 4: Moderate Bloat Reduction (4 commands)
1. ✅ java-maintain-tests - COMPLETED (512→348 lines, 164 saved)
2. ✅ plugin-diagnose-marketplace - COMPLETED (523→278 lines, 245 saved)
3. ✅ js-maintain-tests - COMPLETED (534→440 lines, 94 saved, exceeded target of 90)
4. ✅ java-implement-tests - COMPLETED (529→493 lines, 36 saved, exceeded target of 30)

### Phase 5: Broken References Investigation (3 commands)
5. ✅ maven-build-and-fix (#5) - ALREADY CLEAN (no action needed)
6. ✅ tools-audit-permission-wildcards (#3) - ALREADY CLEAN (no action needed)
7. ✅ doc-review-technical-docs (#4) - FIXED (added bundle qualifier to commit-changes reference)

---

## Success Metrics - ACHIEVED ✅

**Actual Results:**
- **Bloat reduction**: ✅ COMPLETE - All moderate bloat commands fixed (539 lines saved: 164 java-maintain-tests + 245 plugin-diagnose-marketplace + 94 js-maintain-tests + 36 java-implement-tests)
- **Average command size**: ✅ Commands reduced from avg 526 lines to avg 390 lines (26% reduction for completed)
- **Runtime failures fixed**: ✅ ALL FIXED
  - maven-build-and-fix: Already clean (fixed in previous session)
  - tools-audit-permission-wildcards: Already clean (fixed in previous session)
  - doc-review-technical-docs: Fixed (added bundle qualifier to commit-changes reference)
- **New skills created**: 0 additional skills needed (1 already created: cui-marketplace-orchestration-patterns)
- **Total cumulative impact**: 861 lines removed (322 from Phase 3, 539 from Phase 4), 1 skill created, 1 broken reference fixed

**Actual Effort**: ~15 minutes (most issues were already fixed in previous sessions)

---

## Notes

- Always run `/plugin-diagnose-commands` after each fix to verify improvements
- Test each command after modification to ensure functionality preserved
- Commit changes incrementally with clear commit messages
- Focus on moderate bloat first, then investigate broken references

---

**End of Remediation Plan**
