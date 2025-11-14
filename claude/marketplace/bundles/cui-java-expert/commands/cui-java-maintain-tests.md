---
name: cui-java-maintain-tests
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

**Execute build verification before starting**:

```
Task:
  subagent_type: maven-builder
  description: Pre-maintenance build verification
  prompt: |
    Execute pre-maintenance verification to establish baseline.

    Execute in sequence:
    1. Quality build (no tests): ./mvnw -Ppre-commit clean verify -DskipTests
    2. Test execution: ./mvnw clean test
    3. Coverage baseline: ./mvnw clean verify -Pcoverage

    CRITICAL: Wait for each build to complete. If ANY build fails, STOP and report failures.
    Record coverage metrics for regression detection.

    Expected: All builds succeed, all tests pass, establish coverage baseline.
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
    Read: claude/marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing/standards/test-quality-analysis-checklist.md

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

**CRITICAL - Production Code Protection**:

If analysis discovers **production code bugs** (not test issues):

1. **STOP the maintenance process immediately**
2. **Document bug details**:
   - Exact location (file, line)
   - Nature of the bug
   - Impact assessment
3. **Ask user for approval** to fix production code
4. **Wait for user confirmation**
5. **Do NOT proceed** with bug fix until user approves

**User Interaction**:
```
Use AskUserQuestion tool:

Question: "Production code bug discovered during test maintenance analysis.
Details:
- Location: [file:line]
- Issue: [description]
- Impact: [assessment]

May I fix this production code bug as part of maintenance?
This requires modifying production code, not just tests."

Options:
- "Yes, fix the bug now"
- "No, skip this bug and continue with test maintenance only"
- "Stop maintenance, I'll handle the bug separately"
```

**If bugs NOT found**: Continue to Step 5.

### Step 5: Implementation Phase

**Apply test improvements based on scope**:

```
SlashCommand: /cui-java-expert:cui-java-implement-tests task="Implement test quality improvements for module: [module]
Scope: [scope parameter]
Priority: [priority parameter]

Load testing maintenance reference:
Read: claude/marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing/standards/testing-maintenance-reference.md

Apply improvements based on scope:

    [If scope = "anti-patterns" or "full"]
    **Remove Forbidden Anti-Patterns**:
    - Eliminate all if-else, switch, ternary operators from tests
    - Replace Optional.orElse() with explicit Optional state testing
    - Remove all try-catch blocks:
      * Add throws declarations for checked exceptions
      * Use assertThrows() for expected exceptions
      * Use assertDoesNotThrow() for explicit no-exception verification
    - Create separate focused tests instead of conditional tests

    [If scope = "ai-artifacts" or "full"]
    **Remove AI-Generated Artifacts**:
    - Shorten method names > 75 characters
    - Remove excessive obvious comments
    - Remove verbose @DisplayName annotations
    - Remove boilerplate AAA comments unless structure unclear

    [If scope = "value-objects" or "full"]
    **Apply Value Object Testing**:
    - Apply ShouldHandleObjectContracts<T> to qualifying classes:
      * Custom equals/hashCode implementations
      * Domain data with value semantics
      * Classes used in collections/maps
    - Do NOT apply to: enums, utilities, infrastructure, builders

    [If scope = "framework" or "full"]
    **Migrate to CUI Framework**:
    - Replace manual data creation with Generators.*
    - Apply @GeneratorsSource for parameterized tests
    - Remove forbidden libraries (Mockito, Hamcrest, PowerMock)
    - Use cui-test-mockwebserver-junit5 for HTTP mocking

    [Always apply]
    **Ensure Unit Test Focus**:
    - Verify each type has dedicated unit test with comprehensive corner/edge cases
    - Eliminate test duplication across unit tests
    - Remove non-sensible tests (meaningless constructors, framework behavior)
    - Remove reflection workarounds (always a bug)

    **Quality Requirements**:
    - All assertion statements MUST have descriptive messages
    - Follow AAA pattern (but no comments unless unclear)
    - Use meaningful test method names
    - Maintain or improve coverage (no regressions)

    **Test-Only Changes**:
    - Modify ONLY test code
    - NO production code changes
    - If bugs discovered, STOP and report

    Execute improvements one category at a time:
    1. Remove forbidden anti-patterns
    2. Clean AI artifacts
    3. Apply value object contracts
    4. Migrate to CUI framework
    5. Final quality pass

    After EACH category:
    - Run tests: ./mvnw clean test -pl [module]
    - Verify all tests pass
    - Check for any test failures

    Return summary of changes made per category.
```

**Outcome**: Test quality improvements applied systematically.

### Step 6: Module Verification

**Verify improvements and coverage**:

```
Task:
  subagent_type: maven-builder
  description: Verify test improvements for [module]
  prompt: |
    Verify test quality improvements for module: [module]

    Execute verification builds in sequence:

    1. **Quality Build**: ./mvnw -Ppre-commit clean verify -DskipTests -pl [module]
       - Verifies code quality without test execution
       - Fast feedback on compilation and static analysis

    2. **Test Execution**: ./mvnw clean test -pl [module]
       - All tests must pass
       - No test failures allowed

    3. **Coverage Analysis**: ./mvnw clean verify -Pcoverage -pl [module]
       - Verify minimum 80% line/branch coverage maintained
       - Check for coverage regressions
       - Document any coverage improvements

    CRITICAL: Wait for each build to complete.

    If ANY build fails:
    - Capture full error output
    - Analyze failure cause
    - Report detailed failure information
    - DO NOT proceed to next module

    Expected: All builds succeed, coverage maintained or improved.
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

**After all modules processed**:

```
Task:
  subagent_type: maven-builder
  description: Final comprehensive verification
  prompt: |
    Execute final comprehensive verification across all modules.

    Execute full project builds:

    1. **Full Quality Build**: ./mvnw -Ppre-commit clean verify -DskipTests
    2. **Full Test Suite**: ./mvnw clean test
    3. **Full Coverage Analysis**: ./mvnw clean verify -Pcoverage

    CRITICAL: Wait for each build to complete.

    Verify:
    - All modules compile successfully
    - All tests pass across entire project
    - Coverage maintained or improved project-wide
    - No inter-module test conflicts

    Report final metrics:
    - Total tests improved
    - Coverage change (baseline vs final)
    - Violations removed by category
    - Module completion status

    Expected: All builds succeed, comprehensive improvement achieved.
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

### Build Failures

If any build fails:
1. Capture complete error output
2. Analyze failure cause
3. Report detailed failure information
4. Provide fix recommendations
5. Do NOT proceed until resolved

### Test Failures

If tests fail after improvements:
1. Identify which changes caused failure
2. Analyze test failure output
3. Determine if issue is in test or production code
4. If production bug: Ask user for approval (Step 4 protocol)
5. If test issue: Fix test implementation
6. Re-run verification

### Coverage Regressions

If coverage decreases:
1. Identify which tests were removed/changed
2. Analyze coverage gap
3. Document justification for any coverage decrease
4. Ensure no critical paths are untested
5. Add tests if coverage gap is unjustified

### Reflection Workarounds

If reflection workarounds found:
1. Document as CRITICAL issue
2. Explain why this is always a bug
3. Recommend production code refactoring
4. Ask user for guidance on handling

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

**This command should be improved using**: `/plugin-update-command cui-java-maintain-tests`

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
* /cui-java-implement-tests - Test improvement implementation (Layer 2)
* maven-builder - Build verification and coverage analysis

**Related Commands**:
* /cui-java-refactor-code - For production code refactoring
* /cui-java-maintain-logger - For logging standards maintenance
