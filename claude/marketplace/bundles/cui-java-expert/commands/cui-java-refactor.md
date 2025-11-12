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

### Scope Definitions

**`full` (default):** All violation types, complete standards compliance audit, all priorities (unless filtered)

**`standards`:** Code organization, method design, null safety, exception handling, naming conventions

**`unused`:** Unused private fields/methods, unused variables, dead code (with user approval)

**`modernize`:** Legacy switch statements, manual data classes, imperative loops, verbose patterns

**`documentation`:** Missing/outdated Javadoc, redundant comments, documentation standards compliance

### Priority Filter Behavior

**`high`:** Only HIGH priority violations (security, API contracts, fundamental design problems)

**`medium`:** HIGH and MEDIUM priority violations (includes maintainability issues, code cleanup, modernization)

**`low`:** Only LOW priority violations (style consistency, minor optimizations)

**`all` (default):** All priorities processed in HIGH → MEDIUM → LOW order

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

## WORKFLOW

### Step 0: Parameter Validation

- If `module` specified: verify module exists
- Validate `scope` is one of: full, standards, unused, modernize, documentation
- Validate `priority` is one of: high, medium, low, all
- Set defaults if not provided

### Step 1: Load Maintenance Standards

```
Skill: cui-java-maintenance
```

This loads comprehensive maintenance standards including:
- Refactoring trigger criteria (detection patterns)
- Prioritization framework (impact-based ordering)
- Compliance verification checklist

**On load failure:** Report error and abort command.

### Step 2: Pre-Maintenance Verification

**2.1 Build Verification:**

```
Task:
  subagent_type: maven-builder
  description: Verify build before refactoring
  prompt: |
    Execute Maven build with pre-commit profile.
    Parameters: -Ppre-commit clean verify -DskipTests
    Module: {module if specified, otherwise all}
    Build must pass before proceeding.
```

**On build failure:** Display errors, prompt user "[F]ix manually and retry / [A]bort", track in `pre_verification_failures`.

**2.2 Test Execution:**

```
Task:
  subagent_type: maven-builder
  description: Execute test suite
  prompt: |
    Execute complete test suite to verify baseline functionality.
    Parameters: clean test
    Module: {module if specified, otherwise all}
    All tests must pass before refactoring begins.
```

**On test failure:** Display failures, prompt user "[F]ix manually and retry / [A]bort", track in `pre_verification_failures`.

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

    Apply detection criteria from refactoring-triggers.md to identify violations.
    See cui-java-maintenance skill for comprehensive detection patterns.

    Return structured list of findings with:
    - Violation type
    - Location (file, class, method, line)
    - Description
    - Suggested priority (HIGH/MEDIUM/LOW)
```

Store findings for prioritization step.

**On analysis failure:** Increment `analysis_failures`, prompt user "[R]etry / [A]bort".

### Step 4: Prioritize Violations

Apply prioritization framework from cui-java-maintenance skill (maintenance-prioritization.md):

1. **Categorize findings** by type (API Contracts, Code Organization, Method Design, Modern Java, Code Cleanup, Style)

2. **Assign priorities** using framework:
   - HIGH: Critical violations (security, API contracts, fundamental design)
   - MEDIUM: Maintainability (method design, cleanup, modernization)
   - LOW: Style and optimization

3. **Filter by priority parameter** if specified

4. **Sort within each priority** by impact and module dependencies

5. **Display prioritized list** to user with counts per priority level

6. **Prompt user for confirmation:** "[P]roceed with refactoring / [M]odify priorities / [A]bort"

### Step 5: Execute Refactoring

Process violations systematically using module-by-module strategy:

**For each module in processing order:**

**5.1 Module Focus:**

Display current module, violations to fix, priority distribution.

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

    Apply appropriate fix following cui-java-core skill patterns.
    Return implementation status.
```

Track in `fixes_applied` counter.

**On implementation error:** Log error, track in `fixes_failed`, prompt user "[S]kip / [R]etry / [A]bort module".

**5.3 Module Verification:**

```
SlashCommand: /cui-build-and-fix
Parameters: module={module-name}
```

Self-contained command that runs build, fixes issues, verifies tests, commits fixes.

**On verification failure:** Increment `module_verification_failures`, attempt rollback, prompt user "[R]etry / [S]kip module / [A]bort".

**5.4 Module Coverage Check:**

```
SlashCommand: /java-coverage-report
Parameters: module={module-name}
```

Compare to baseline - if decreased warn user and ask if acceptable.

**5.5 Module Commit:**

```
Bash: git add {module files} && git commit -m "refactor: {module-name} - standards compliance improvements"
```

Track in `modules_completed` counter. Continue to next module.

### Step 6: Final Verification

After all modules processed:

**6.1 Complete Build:**

```
Task:
  subagent_type: maven-builder
  description: Final build verification
  prompt: |
    Execute complete build to verify all changes.
    Parameters: clean verify
    Full build must pass.
```

**6.2 Full Test Suite:**

```
Task:
  subagent_type: maven-builder
  description: Final test verification
  prompt: |
    Execute complete test suite.
    Parameters: clean test
    All tests must pass.
```

**6.3 Coverage Verification:**

```
SlashCommand: /java-coverage-report
```

Compare final coverage to baseline, display coverage change, ensure no significant regression.

**6.4 Standards Compliance Verification:**

Apply compliance checklist from cui-java-maintenance skill to sample of refactored classes. Report compliance status.

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
- `pre_verification_failures` - Pre-maintenance verification failures
- `analysis_failures` - Standards audit failures
- `modules_completed` / `modules_failed` - Module processing
- `fixes_applied` / `fixes_failed` / `fixes_skipped` - Individual fixes
- `module_verification_failures` - Module verification failures
- `coverage_baseline` / `coverage_final` - Coverage metrics
- `elapsed_time` - Total execution time

Display all statistics in final summary.

## ERROR HANDLING

**Build/Test Failures:** Display detailed errors, attempt automatic fixes via maven-builder, prompt for manual intervention if needed, track failures for reporting.

**Implementation Errors:** Log specific violation that failed, skip individual violations on user request, continue with other violations, report failures in summary.

**Coverage Regression:** Warn user if coverage decreases, request confirmation to proceed, suggest adding tests to restore coverage.

**Non-Logging Bugs:** If discovered during refactoring, stop and ask user for approval before fixing, separate commit if approved.

## ROLLBACK STRATEGY

**Module-level rollback:**
```
Bash: git reset HEAD~1 && git checkout -- {module}
```

**Complete rollback:**
```
Bash: git reset --hard {initial_commit}
```

## USAGE EXAMPLES

```
# Full refactoring (all modules, all priorities)
/cui-java-refactor

# Single module refactoring
/cui-java-refactor module=auth-service

# Only high priority violations
/cui-java-refactor priority=high

# Modernize code only
/cui-java-refactor scope=modernize

# Remove unused code
/cui-java-refactor scope=unused priority=medium

# Documentation improvements only
/cui-java-refactor scope=documentation module=core-api

# Combination
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
