---
name: java-maintain-tests
description: Systematic workflow for maintaining and improving Java test quality
---

# Java Test Maintenance Command

Systematic workflow for maintaining and improving Java test quality while preserving functionality and adhering to CUI standards.

## PARAMETERS

- **module** - (Optional) Specific module name to process. If not provided, processes all modules
- **scope** - (Optional) Maintenance scope:
  - `full` - Complete test maintenance (default)
  - `anti-patterns` - Focus on forbidden patterns only (conditional logic, Optional.orElse, try-catch)
  - `ai-artifacts` - Remove AI-generated code artifacts
  - `value-objects` - Apply value object contract testing
  - `framework` - Migrate to CUI testing framework
- **priority** - (Optional) Priority filter for enhancements:
  - `all` - Process all tests (default)
  - `high` - Business logic tests only
  - `medium` - Business logic + value objects
  - `low` - Infrastructure tests only

## OVERVIEW

This command provides comprehensive test quality improvement workflow with:

* Pre-maintenance build verification
* Module-by-module systematic processing
* Test enhancement prioritization (High/Medium/Low)
* Forbidden anti-pattern detection and removal
* AI artifact cleanup
* Value object contract application
* CUI framework migration
* Bug handling protocol
* Coverage preservation

**Key Constraint**: NO production code changes except confirmed bugs. Must ask user approval before fixing production code.

## PREREQUISITES

**Load Required Skills**:
```
Skill: cui-java-unit-testing
```

This loads all CUI testing standards including:
- Core JUnit 5 patterns
- Quality standards and AI detection
- CUI test generator framework
- Value object testing
- Maintenance-specific reference

## WORKFLOW

### Step 1: Pre-Maintenance Verification

**Execute build verification to establish baseline**:

```
Task:
  subagent_type: maven-builder
  description: Pre-maintenance build verification
  prompt: |
    Execute three-phase verification: quality build, test execution, coverage analysis.
    Record coverage metrics for regression detection.
    If ANY build fails, STOP and report failures.
```

**Outcome**: Baseline established, ready for maintenance.

### Step 2: Module Identification

**Identify modules to process**:

If `module` parameter provided:
* Process only specified module
* Skip module listing

If NO `module` parameter:
* List all project modules
* Process modules in dependency order (dependencies first)

```
Task:
  subagent_type: Explore
  thoroughness: quick
  description: List all project modules
  prompt: |
    Find all Maven modules in this project.

    Search for pom.xml files to identify module structure.
    Return list of module names in dependency order if possible.
```

### Step 3: Analysis Phase (Per Module)

**For each module, execute comprehensive analysis**:

```
Task:
  subagent_type: Explore
  thoroughness: medium
  description: Analyze test quality in [module]
  prompt: |
    Analyze test quality in module: [module]

    Load comprehensive analysis checklist:
    Read: marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing/standards/test-quality-analysis-checklist.md

    Execute comprehensive analysis following the 10-category checklist.
    Apply priority filter: [priority parameter]

    Return structured analysis report with:
    - Test file inventory with priority classification
    - Violations by category with counts
    - Enhancement recommendations prioritized by impact
    - Estimated effort per improvement category
```

**Outcome**: Complete understanding of test quality issues in module.

### Step 4: Bug Detection and User Approval

**CRITICAL**: If analysis discovers production code bugs (not test issues):

1. STOP immediately, document details (location, issue, impact)
2. Use AskUserQuestion to request approval before fixing production code
3. Do NOT proceed with bug fix until user confirms

**If no bugs found**: Continue to Step 5.

### Step 5: Implementation Phase

**Apply test improvements based on scope**:

```
SlashCommand: /cui-java-expert:java-implement-tests task="Implement test quality improvements for module: [module]
Scope: [scope parameter]
Priority: [priority parameter]

Apply scope-specific improvements:
- anti-patterns: Remove forbidden patterns (if-else, Optional.orElse, try-catch)
- ai-artifacts: Clean AI-generated artifacts (long names, excessive comments)
- value-objects: Apply ShouldHandleObjectContracts<T> pattern
- framework: Migrate to CUI testing framework (Generators, @GeneratorsSource)
- full: All of the above

CRITICAL: Test-only changes. NO production code modifications.
If bugs discovered, STOP and report."
```

**Outcome**: Test quality improvements applied systematically.

### Step 6: Module Verification

**Verify improvements for current module**:

```
Task:
  subagent_type: maven-builder
  description: Verify test improvements for [module]
  prompt: |
    Execute three-phase verification for module: [module]
    Scope to module using -pl [module] flag.
    Verify minimum 80% coverage maintained.
    DO NOT proceed to next module if ANY build fails.
```

**Outcome**: Module improvements verified, ready to commit.

### Step 7: Incremental Commit

**Commit module improvements**:

After successful verification of each module:

1. Review all changes in module
2. Create focused commit message following conventional commits
3. Use git add/commit for module changes
4. Include improvement summary in commit message

**Commit Message Format**:
```
test(module-name): improve test quality and standards compliance

- Remove forbidden anti-patterns (if-else, Optional.orElse, try-catch)
- Clean AI-generated code artifacts
- Apply value object contract testing
- Migrate to CUI testing framework
- Ensure unit test focus and eliminate duplication

Coverage: [maintained/improved from X% to Y%]
Tests: [N tests improved, M tests added/removed]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Step 8: Multi-Module Processing

**If processing multiple modules**:

Repeat Steps 3-7 for each module:
* Process in dependency order
* Complete one module fully before starting next
* Commit after each module verification
* Maintain build stability throughout

**Progress Tracking**:
```
Modules completed: [N / Total]
Modules remaining: [list]
Current module: [name]
```

### Step 9: Final Verification

**After all modules processed, verify entire project**:

```
Task:
  subagent_type: maven-builder
  description: Final comprehensive verification
  prompt: |
    Execute three-phase verification across all modules (no -pl flag).
    Report final metrics: tests improved, coverage change, violations removed.
    Verify no inter-module conflicts.
```

**Outcome**: Full project verification complete.

### Step 10: Summary Report

**Provide comprehensive maintenance summary**:

Report:

1. **Modules Processed**: List of all modules completed
2. **Improvements Applied**:
   - Forbidden anti-patterns removed: [count]
   - AI artifacts cleaned: [count]
   - Value object contracts applied: [count]
   - Framework migrations: [count]
   - Non-sensible tests removed: [count]
   - Unit test focus improvements: [count]

3. **Coverage Results**:
   - Baseline coverage: [%]
   - Final coverage: [%]
   - Change: [+/- %]

4. **Build Verification**: All builds succeeded ✓
5. **Commits Created**: [N commits, 1 per module]
6. **Standards Compliance**: Achieved ✓

## PARAMETERS USAGE

**Example 1: Full maintenance of single module**
```
module: "cui-portal-core"
scope: "full"
priority: "all"
```
Processes all test improvements in cui-portal-core module.

**Example 2: Remove anti-patterns only, high priority tests**
```
scope: "anti-patterns"
priority: "high"
```
Focuses on business logic tests, removes forbidden patterns only.

**Example 3: AI artifact cleanup across all modules**
```
scope: "ai-artifacts"
```
Removes AI-generated code artifacts from all modules.

**Example 4: Value object contracts, medium priority**
```
scope: "value-objects"
priority: "medium"
```
Applies value object testing to business logic and value objects only.

## ERROR HANDLING

**Build/test failures**: maven-builder agent handles error analysis and reporting. Do NOT proceed until resolved.

**Production bugs discovered**: STOP immediately, ask user approval before fixing production code (Step 4 protocol).

**Coverage regressions**: Justify any decrease, ensure no critical paths untested, add tests if gap is unjustified.

**Reflection workarounds**: Document as CRITICAL (always a bug), recommend production refactoring, ask user guidance.

## CONSTRAINTS

**STRICT REQUIREMENTS**:

* **NO production code changes** except confirmed bugs
* **Bug discovery**: MUST ask user approval before fixing production code
* **Test-only changes**: Focus solely on test improvement
* **Behavior preservation**: All existing tests must continue to pass (unless non-sensible)
* **Coverage preservation**: Maintain minimum 80% coverage, no regressions
* **Module completion**: Finish one module completely before starting next
* **Incremental commits**: Commit after each module verification

## SUCCESS CRITERIA

Test maintenance is complete when:

- [ ] All modules processed systematically
- [ ] All forbidden anti-patterns removed
- [ ] AI artifacts cleaned from all tests
- [ ] Value object contracts applied where appropriate
- [ ] CUI framework adoption complete
- [ ] Unit test focus verified (dedicated tests per type, no duplication)
- [ ] All builds succeed (quality, test, coverage)
- [ ] Coverage maintained or improved (minimum 80%)
- [ ] All commits created following standards
- [ ] Comprehensive summary report provided

## CONTINUOUS IMPROVEMENT RULE

**This command should be improved using**: `/plugin-update-command java-maintain-tests`

**Improvement areas**:
- Analysis efficiency optimization for large multi-module projects
- Enhanced bug detection patterns and production code isolation
- Expanded value object contract detection heuristics
- Improved coverage regression analysis and reporting
- Additional test classification categories and priority refinement

## REFERENCES

**Skills Used**:
* cui-java-unit-testing - Complete testing standards and patterns

**Commands and Agents Orchestrated**:
* Explore - Test quality analysis and module identification
* /java-implement-tests - Test improvement implementation (Layer 2)
* maven-builder - Build verification and coverage analysis

**Related Commands**:
* /java-refactor-code - For production code refactoring
* /java-maintain-logger - For logging standards maintenance
