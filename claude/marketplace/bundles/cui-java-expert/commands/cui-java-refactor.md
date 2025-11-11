---
name: cui-java-refactor
description: Execute systematic Java refactoring with standards compliance verification
---

# CUI Java Refactor Command

Orchestrates systematic Java code refactoring and maintenance workflow with comprehensive standards compliance verification.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-java-refactor update="[your improvement]"` with:
1. Improved violation detection patterns
2. Better module processing strategies
3. More effective agent coordination
4. Enhanced verification workflows
5. Any lessons learned about systematic refactoring

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **module** - Module name for single module refactoring (optional, processes all if not specified)
- **scope** - Refactoring scope: `full` (default), `standards`, `unused`, `modernize`, `documentation`
- **priority** - Priority filter: `high`, `medium`, `low`, `all` (default: `all`)

## WORKFLOW

### Step 0: Parameter Validation

**Validate parameters:**
- If `module` specified: verify module exists
- Validate `scope` is one of: full, standards, unused, modernize, documentation
- Validate `priority` is one of: high, medium, low, all
- Set defaults if not provided

### Step 1: Load Maintenance Standards

```
Skill: cui-java-maintenance
```

This loads comprehensive maintenance standards:
- Refactoring trigger criteria
- Prioritization framework
- Compliance verification checklist

**On load failure:**
- Report error
- Cannot proceed without standards
- Abort command

### Step 2: Pre-Maintenance Verification

Execute pre-maintenance checklist to establish baseline:

**2.1 Build Verification:**
```
Task:
  subagent_type: maven-builder
  description: Verify build before refactoring
  prompt: |
    Execute Maven build with pre-commit profile to verify build health.

    Parameters:
    - command: -Ppre-commit clean verify -DskipTests
    - module: {module if specified, otherwise all}

    Return structured results. Build must pass before proceeding.
```

**On build failure:**
- Display build errors
- Prompt user: "[F]ix manually and retry / [A]bort"
- Track in `pre_verification_failures` counter
- Cannot proceed until build passes

**2.2 Test Execution:**
```
Task:
  subagent_type: maven-builder
  description: Execute test suite
  prompt: |
    Execute complete test suite to verify baseline functionality.

    Parameters:
    - command: clean test
    - module: {module if specified, otherwise all}

    All tests must pass before refactoring begins.
```

**On test failure:**
- Display test failures
- Prompt user: "[F]ix manually and retry / [A]bort"
- Track in `pre_verification_failures` counter
- Cannot proceed until tests pass

**2.3 Coverage Baseline:**
```
SlashCommand: /java-coverage-report
Parameters: module={module if specified}
```

Store baseline coverage metrics for comparison after refactoring.

**2.4 Module Identification:**

If `module` parameter not specified:
- Use Glob to identify all Maven modules
- Determine module processing order (dependencies first)
- Display module list and order to user

If `module` parameter specified:
- Verify module exists
- Process single module only

### Step 3: Standards Compliance Audit

Analyze codebase for violations using loaded maintenance standards:

```
Task:
  subagent_type: Explore
  model: sonnet
  description: Identify standards violations
  prompt: |
    Analyze the codebase using cui-java-maintenance trigger criteria.

    Module: {module or 'all modules'}
    Scope: {scope parameter}

    Apply detection criteria from refactoring-triggers.md to identify:
    - Code organization violations
    - Method design issues
    - Null safety violations
    - Naming convention problems
    - Exception handling issues
    - Legacy code patterns (if scope=modernize or full)
    - Unused code (if scope=unused or full)
    - Lombok integration opportunities
    - Documentation gaps (if scope=documentation or full)

    Return structured list of findings with:
    - Violation type
    - Location (file, class, method, line)
    - Description
    - Suggested priority (HIGH/MEDIUM/LOW)
```

**Store findings** for prioritization step.

**On analysis failure:**
- Increment `analysis_failures` counter
- Prompt user: "[R]etry / [A]bort"

### Step 4: Prioritize Violations

Apply prioritization framework from maintenance-prioritization.md:

1. **Categorize findings** by type:
   - API Contract Issues
   - Code Organization Problems
   - Method Design Problems
   - Modern Java Adoption
   - Code Cleanup
   - Style Consistency

2. **Assign priorities** using framework:
   - HIGH: Critical violations (security, API contracts, fundamental design)
   - MEDIUM: Maintainability (method design, cleanup, modernization)
   - LOW: Style and optimization

3. **Filter by priority parameter** if specified:
   - If priority=high: only HIGH priority items
   - If priority=medium: HIGH and MEDIUM items
   - If priority=low: Only LOW items
   - If priority=all: all items

4. **Sort within each priority** by impact and module dependencies

5. **Display prioritized list** to user:
   ```
   Prioritized Violations Found:

   HIGH Priority (X items):
   - [Type] Location: Description

   MEDIUM Priority (Y items):
   - [Type] Location: Description

   LOW Priority (Z items):
   - [Type] Location: Description

   Processing order: HIGH → MEDIUM → LOW
   ```

6. **Prompt user for confirmation**:
   - "[P]roceed with refactoring / [M]odify priorities / [A]bort"

### Step 5: Execute Refactoring

Process violations systematically using module-by-module strategy:

**For each module in processing order:**

**5.1 Module Focus:**
```
Current Module: {module-name}
Violations to fix: {count} ({HIGH/MEDIUM/LOW distribution})
```

**5.2 Implement Fixes:**

For each violation in priority order (HIGH → MEDIUM → LOW):

```
Task:
  subagent_type: java-code-implementer
  description: Fix {violation type}
  prompt: |
    Fix the following violation using cui-java-core standards:

    Violation: {violation description}
    Location: {file}:{line}
    Type: {violation type}
    Priority: {priority}

    Apply appropriate fix following standards:
    - If code organization: restructure per Package Structure Standards
    - If method design: extract methods per Method Design Standards
    - If null safety: add @NonNull or Optional per Null Safety Standards
    - If naming: improve names per Naming Conventions
    - If exceptions: use specific types per Exception Handling Standards
    - If legacy code: apply modern Java features
    - If unused code: remove after user approval
    - If Lombok: apply appropriate annotations
    - If documentation: add Javadoc per standards

    Return implementation status.
```

Track in `fixes_applied` counter.

**On implementation error:**
- Log error details
- Track in `fixes_failed` counter
- Prompt user: "[S]kip this violation / [R]etry / [A]bort module"

**5.3 Module Verification:**

After all fixes for module:

```
SlashCommand: /cui-build-and-fix
Parameters: module={module-name}
```

Self-contained command that:
- Runs build
- Fixes any build issues found
- Verifies tests pass
- Commits fixes

**On verification failure:**
- Increment `module_verification_failures` counter
- Attempt to rollback module changes
- Prompt user: "[R]etry / [S]kip module / [A]bort"

**5.4 Module Coverage Check:**

```
SlashCommand: /java-coverage-report
Parameters: module={module-name}
```

**Compare to baseline:**
- If coverage decreased: WARN user, ask if acceptable
- If coverage same/increased: OK

**5.5 Module Commit:**

Commit module changes:
```
Bash: git add {module files}
Bash: git commit -m "refactor: {module-name} - standards compliance improvements"
```

Track in `modules_completed` counter.

**Continue to next module.**

### Step 6: Final Verification

After all modules processed:

**6.1 Complete Build:**
```
Task:
  subagent_type: maven-builder
  description: Final build verification
  prompt: |
    Execute complete build to verify all changes.

    Parameters:
    - command: clean verify

    Full build must pass.
```

**6.2 Full Test Suite:**
```
Task:
  subagent_type: maven-builder
  description: Final test verification
  prompt: |
    Execute complete test suite.

    Parameters:
    - command: clean test

    All tests must pass.
```

**6.3 Coverage Verification:**
```
SlashCommand: /java-coverage-report
```

Compare final coverage to baseline:
- Display coverage change
- Ensure no significant regression

**6.4 Standards Compliance Verification:**

Apply compliance checklist from cui-java-maintenance:

For sample of refactored classes:
- Verify package organization
- Verify class design
- Verify method design
- Verify null safety
- Verify exception handling
- Verify naming conventions
- Verify modern features
- Verify unused code removed
- Verify Lombok usage
- Verify documentation

Report compliance status.

### Step 7: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║          Refactoring Summary                               ║
╚════════════════════════════════════════════════════════════╝

Scope: {scope}
Priority Filter: {priority}

Modules Processed: {modules_completed} / {total_modules}
Violations Found: {total_violations}
  - HIGH Priority: {high_count}
  - MEDIUM Priority: {medium_count}
  - LOW Priority: {low_count}

Fixes Applied: {fixes_applied}
Fixes Failed: {fixes_failed}
Fixes Skipped: {fixes_skipped}

Coverage:
  - Baseline: {baseline_coverage}%
  - Final: {final_coverage}%
  - Change: {coverage_delta}%

Build Status: {SUCCESS/FAILURE}
Tests: {passing_count} / {total_tests} passed

Compliance: {compliant_categories} / {total_categories} categories compliant

Time Taken: {elapsed_time}
```

## STATISTICS TRACKING

Track throughout workflow:
- `pre_verification_failures`: Pre-maintenance verification failures
- `analysis_failures`: Standards audit failures
- `modules_completed`: Modules successfully refactored
- `modules_failed`: Modules that failed verification
- `fixes_applied`: Individual violation fixes applied
- `fixes_failed`: Individual fixes that failed
- `fixes_skipped`: Violations skipped by user
- `module_verification_failures`: Module verification failures
- `coverage_baseline`: Initial coverage percentage
- `coverage_final`: Final coverage percentage
- `elapsed_time`: Total execution time

Display all statistics in final summary.

## CRITICAL CONSTRAINTS

**Functionality Preservation:**
- **NO BEHAVIOR CHANGES** unless fixing confirmed bugs
- All existing tests must continue to pass
- API compatibility maintained for public APIs
- Performance must not degrade

**Safety Protocols:**
- Incremental changes (module-by-module)
- Continuous verification after each module
- Ability to rollback at module level
- User confirmation before major changes

**Module-by-Module Strategy:**
- Process one module completely before next
- Verify and commit each module independently
- Maintain build stability after each module
- Process in dependency order

## SCOPE DEFINITIONS

**`full` (default):**
- All violation types
- Complete standards compliance audit
- All priorities (unless filtered)

**`standards`:**
- Code organization violations
- Method design issues
- Null safety violations
- Exception handling issues
- Naming conventions

**`unused`:**
- Unused private fields and methods
- Unused local variables
- Dead code elimination
- With user approval for removals

**`modernize`:**
- Legacy switch statements → switch expressions
- Manual data classes → records
- Imperative loops → streams
- Verbose patterns → modern Java

**`documentation`:**
- Missing Javadoc
- Outdated documentation
- Redundant comments
- Documentation standards compliance

## PRIORITY FILTER BEHAVIOR

**`high`:**
- Only HIGH priority violations
- Security issues
- API contract issues
- Fundamental design problems

**`medium`:**
- HIGH and MEDIUM priority violations
- Includes maintainability issues
- Code cleanup and modernization

**`low`:**
- Only LOW priority violations
- Style consistency
- Minor optimizations

**`all` (default):**
- All priorities processed
- HIGH → MEDIUM → LOW order

## ERROR HANDLING

**Build Failures:**
- Display detailed error information
- Attempt automatic fixes via maven-builder
- Prompt user for manual intervention if needed
- Track failures for reporting

**Test Failures:**
- Display failed test details
- Preserve test failure output
- Do not proceed with refactoring
- Rollback if failures introduced

**Implementation Errors:**
- Log specific violation that failed
- Skip individual violations on user request
- Continue with other violations
- Report failures in summary

**Coverage Regression:**
- Warn user if coverage decreases
- Request confirmation to proceed
- Suggest adding tests to restore coverage

## ROLLBACK STRATEGY

**Module-level rollback:**
```
Bash: git reset HEAD~1  # Rollback module commit
Bash: git checkout -- {module}  # Restore module files
```

**Complete rollback:**
```
Bash: git reset --hard {initial_commit}  # Restore to pre-refactor state
```

## USAGE EXAMPLES

**Full refactoring (all modules, all priorities):**
```
/cui-java-refactor
```

**Single module refactoring:**
```
/cui-java-refactor module=auth-service
```

**Only high priority violations:**
```
/cui-java-refactor priority=high
```

**Modernize code only:**
```
/cui-java-refactor scope=modernize
```

**Remove unused code:**
```
/cui-java-refactor scope=unused priority=medium
```

**Documentation improvements only:**
```
/cui-java-refactor scope=documentation module=core-api
```

**Combination:**
```
/cui-java-refactor module=user-service scope=standards priority=high
```

## ARCHITECTURE

Orchestrates agents and commands:
- **cui-java-maintenance skill** - Standards for detection, prioritization, verification
- **Explore agent** - Codebase analysis for violation detection
- **java-code-implementer agent** - Focused code fixes (Layer 3)
- **maven-builder agent** - Build and verification (Layer 3)
- **`/cui-build-and-fix` command** - Build verification and fixes
- **`/java-coverage-report` command** - Coverage analysis

## RELATED

- `cui-java-maintenance` skill - Standards this command implements
- `java-code-implementer` agent - Implementation fixes
- `maven-builder` agent - Build verification
- `/cui-build-and-fix` command - Build and fix workflow
- `/java-coverage-report` command - Coverage analysis
- `cui-java-core` skill - Implementation patterns
- `cui-task-planning` skill - For refactoring task planning
