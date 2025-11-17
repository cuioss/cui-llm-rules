# Commands Remediation Plan - Remaining Work

**Generated**: 2025-11-17
**Updated**: 2025-11-17 (Phases 1-3 complete)
**Scope**: Marketplace commands diagnosis - remaining fixes
**Remaining Issues**: 7 commands requiring fixes
**Priority**: Execute in order listed (MEDIUM → HIGH)

---

## What's Been Completed

**✅ Phase 1: CONTINUOUS IMPROVEMENT RULE Fixes (5 commands)**
- java-generate-coverage, js-generate-coverage, plugin-create-bundle, js-fix-jsdoc, maven-build-and-fix
- All upgraded to proper self-update format

**✅ Phase 2: Reference Investigation (3 commands)**
- plugin-create-bundle, java-maintain-tests, java-implement-tests
- All verified as false positives

**✅ Phase 3: Critical Bloat Reduction (4 commands)**
- plugin-diagnose-agents: 621→599 lines (22 saved)
- plugin-diagnose-commands: 577→560 lines (17 saved)
- plugin-diagnose-skills: 564→394 lines (170 saved)
- plugin-diagnose-bundle: 569→456 lines (113 saved)
- **Total: 322 lines removed, 1 skill created (cui-marketplace-orchestration-patterns)**
- **Result: 0 BLOATED commands remaining in critical category**

---

## Remaining Work

### MEDIUM PRIORITY: Moderate Bloat Issues (4 Commands)

#### 1. js-maintain-tests (534 lines → ~444 lines)

**Current State**: LARGE (bloat score: 134 - approaching BLOATED)

**Issue**: Contains extractable test improvement categories and verification checklist.

**Remediation**:
```bash
/plugin-update-command command-name=js-maintain-tests update="Extract TEST IMPROVEMENT CATEGORIES section (lines 413-449, ~70 lines) to cui-javascript-maintenance skill. Extract test quality verification checklist (lines 315-328) to same skill. Reference skill instead of inline documentation. Reduce from 534 to ~444 lines."
```

**Expected Reduction**: 90 lines (16.9%)

**Files to Modify**:
- `/marketplace/bundles/cui-frontend-expert/commands/js-maintain-tests.md`
- `/marketplace/bundles/cui-frontend-expert/skills/cui-javascript-maintenance/` (add standards files)

---

#### 2. java-implement-tests (530 lines → optimize structure)

**Current State**: LARGE (bloat score: 133 - just over threshold)

**Issue**: Well-structured command, just slightly over 500-line threshold.

**Remediation**:
```bash
/plugin-update-command command-name=java-implement-tests update="Minor optimization only - command is well-structured at 530 lines. Consider condensing verbose sections if possible, but major restructuring not required. Focus on removing any redundant explanations."
```

**Expected Reduction**: 0-30 lines (0-6%)

**Files to Modify**:
- `/marketplace/bundles/cui-java-expert/commands/java-implement-tests.md`

**Note**: Lowest priority bloat fix - command quality is good.

---

#### 3. plugin-diagnose-marketplace (523 lines → ~350 lines)

**Current State**: BLOATED (bloat score: 131)

**Issue**: Verbose validation procedures, duplicate validation patterns across Steps 2-5, educational overview content.

**Remediation**:
```bash
# Step 1: Create validate-marketplace-config skill
/plugin-create-skill bundle-name=cui-plugin-development-tools skill-name=validate-marketplace-config

# Step 2: Update command
/plugin-update-command command-name=plugin-diagnose-marketplace update="Extract Steps 2-5 validation logic (~150 lines) to validate-marketplace-config skill. Move Overview section (lines 10-45, educational content) to separate architecture guide. Condense phase transition warnings (lines 286-305) to single note. Trust AI inference for JSON parsing - remove over-specification. Reduce from 523 to ~350 lines."
```

**Expected Reduction**: 173 lines (33.1%)

**Files to Modify**:
- `/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-marketplace.md`

**Skills to Create**:
- `validate-marketplace-config`

---

#### 4. java-maintain-tests (512 lines → ~380 lines)

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

### HIGH PRIORITY: Broken References (3 Commands)

#### 5. tools-audit-permission-wildcards

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

#### 6. doc-review-technical-docs

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

#### 7. maven-build-and-fix

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

## Execution Order

**Recommended sequence**:

### Phase 4: Moderate Bloat Reduction (4 commands)
1. java-maintain-tests (#4) - Create 2 skills, reduce 132 lines
2. plugin-diagnose-marketplace (#3) - Create 1 skill, reduce 173 lines
3. js-maintain-tests (#1) - Update existing skill, reduce 90 lines
4. java-implement-tests (#2) - Minor optimization only

### Phase 5: Broken References Investigation (3 commands)
5. maven-build-and-fix (#7) - Fix reference format, investigate missing agents
6. tools-audit-permission-wildcards (#5) - Investigate and fix
7. doc-review-technical-docs (#6) - Investigate and fix or create missing agent

---

## Success Metrics

**Target After All Remaining Fixes:**
- **Bloat reduction**: ~450 lines removed across 4 moderate bloat commands
- **Average command size**: Commands reduced from avg 525 lines to avg 410 lines (22% reduction)
- **Clean rate improvement**: From current ~55% clean to target ~70% clean
- **Runtime failures fixed**: 3 commands with broken references repaired
- **New skills created**: 3-5 additional reusable skills
- **Total cumulative impact**: ~770 lines removed, 4-6 skills created

**Effort Estimate**: 4-6 hours remaining

---

## Notes

- Always run `/plugin-diagnose-commands` after each fix to verify improvements
- Test each command after modification to ensure functionality preserved
- Commit changes incrementally with clear commit messages
- Focus on moderate bloat first, then investigate broken references

---

**End of Remediation Plan**
