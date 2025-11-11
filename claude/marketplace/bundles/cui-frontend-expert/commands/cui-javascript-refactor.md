---
name: cui-javascript-refactor
description: Execute systematic JavaScript refactoring with standards compliance verification
---

# CUI JavaScript Refactor Command

Orchestrates systematic JavaScript code refactoring and maintenance workflow with comprehensive standards compliance verification.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-javascript-refactor update="[your improvement]"` with:
1. Improved violation detection patterns
2. Better file/workspace processing strategies
3. More effective agent coordination
4. Enhanced verification workflows
5. Any lessons learned about systematic refactoring

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **workspace** - Workspace name for single workspace refactoring (optional, processes all if not specified)
- **scope** - Refactoring scope: `full` (default), `standards`, `unused`, `modernize`, `documentation`
- **priority** - Priority filter: `high`, `medium`, `low`, `all` (default: `all`)

## WORKFLOW

### Step 0: Parameter Validation

**Validate parameters:**
- If `workspace` specified: verify workspace exists
- Validate `scope` is one of: full, standards, unused, modernize, documentation
- Validate `priority` is one of: high, medium, low, all
- Set defaults if not provided

### Step 1: Load Maintenance Standards

```
Skill: cui-javascript-maintenance
```

This loads comprehensive maintenance standards:
- Refactoring trigger criteria
- Prioritization framework
- Compliance verification checklist
- Test quality standards

**On load failure:**
- Report error
- Cannot proceed without standards
- Abort command

### Step 2: Pre-Maintenance Verification

Execute pre-maintenance checklist to establish baseline:

**2.1 Build Verification:**
```
Task:
  subagent_type: npm-builder
  description: Verify build before refactoring
  prompt: |
    Execute npm build to verify build health.

    Parameters:
    - command: run build
    - workspace: {workspace if specified, otherwise all}
    - outputMode: DEFAULT

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
  subagent_type: npm-builder
  description: Execute test suite
  prompt: |
    Execute complete test suite to verify baseline functionality.

    Parameters:
    - command: run test
    - workspace: {workspace if specified, otherwise all}
    - outputMode: DEFAULT

    All tests must pass before refactoring begins.
```

**On test failure:**
- Display test failures
- Prompt user: "[F]ix manually and retry / [A]bort"
- Track in `pre_verification_failures` counter
- Cannot proceed until tests pass

**2.3 Coverage Baseline:**
```
SlashCommand: /javascript-coverage-report
Parameters: workspace={workspace if specified}
```

Store baseline coverage metrics for comparison after refactoring.

**2.4 Workspace/File Identification:**

If `workspace` parameter not specified:
- Use Glob to identify all JavaScript files/workspaces
- Determine processing order (dependencies first if using workspaces)
- Display file/workspace list and order to user

If `workspace` parameter specified:
- Verify workspace exists
- Process single workspace only

### Step 3: Standards Compliance Audit

Analyze codebase for violations using loaded maintenance standards:

```
Task:
  subagent_type: Explore
  model: sonnet
  description: Identify standards violations
  prompt: |
    Analyze the codebase using cui-javascript-maintenance trigger criteria.

    Workspace: {workspace or 'all workspaces'}
    Scope: {scope parameter}

    Apply detection criteria from refactoring-triggers.md to identify:
    - Vanilla JavaScript enforcement opportunities (jQuery/library usage)
    - Test/mock code in production files
    - Modularization issues (large files, duplication)
    - Package.json problems (outdated deps, security)
    - JSDoc gaps and documentation issues (if scope=documentation or full)
    - Legacy patterns (var, callbacks) (if scope=modernize or full)
    - Unused code (if scope=unused or full)

    Return structured list of findings with:
    - Violation type
    - Location (file, function, line)
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
   - Library and Dependency Issues
   - Code Organization Problems
   - Vanilla JavaScript Adoption
   - Package Management
   - Code Quality
   - Documentation

2. **Assign priorities** using framework:
   - HIGH: Critical violations (security, test code in production, breaking issues)
   - MEDIUM: Maintainability (code quality, modernization, dependencies)
   - LOW: Style and optimization

3. **Filter by priority parameter** if specified:
   - If priority=high: only HIGH priority items
   - If priority=medium: HIGH and MEDIUM items
   - If priority=low: Only LOW items
   - If priority=all: all items

4. **Sort within each priority** by impact and file dependencies

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

Process violations systematically using file-by-file or workspace-by-workspace strategy:

**For each workspace/batch of files in processing order:**

**5.1 Workspace/File Focus:**
```
Current Workspace: {workspace-name or 'batch N'}
Violations to fix: {count} ({HIGH/MEDIUM/LOW distribution})
```

**5.2 Implement Fixes:**

For each violation in priority order (HIGH → MEDIUM → LOW):

```
Task:
  subagent_type: javascript-code-implementer
  description: Fix {violation type}
  prompt: |
    Fix the following violation using cui-javascript standards:

    Violation: {violation description}
    Location: {file}:{line}
    Type: {violation type}
    Priority: {priority}

    Apply appropriate fix following standards:
    - If vanilla JS: replace library usage with native APIs
    - If test code: remove test/mock imports from production
    - If modularization: split large files or extract duplication
    - If package.json: update dependencies or add missing scripts
    - If JSDoc: add or update documentation
    - If legacy patterns: modernize to ES6+
    - If unused code: remove after user approval

    Return implementation status.
```

Track in `fixes_applied` counter.

**On implementation error:**
- Log error details
- Track in `fixes_failed` counter
- Prompt user: "[S]kip this violation / [R]etry / [A]bort workspace"

**5.3 Workspace/Batch Verification:**

After all fixes for workspace/batch:

```
Task:
  subagent_type: npm-builder
  description: Verify workspace changes
  prompt: |
    Execute build and tests for workspace.

    Parameters:
    - command: run build && run test
    - workspace: {workspace-name}
    - outputMode: DEFAULT

    All must pass.
```

**On verification failure:**
- Increment `workspace_verification_failures` counter
- Attempt to rollback workspace changes
- Prompt user: "[R]etry / [S]kip workspace / [A]bort"

**5.4 Workspace Coverage Check:**

```
SlashCommand: /javascript-coverage-report
Parameters: workspace={workspace-name}
```

**Compare to baseline:**
- If coverage decreased: WARN user, ask if acceptable
- If coverage same/increased: OK

**5.5 Workspace Commit:**

Commit workspace changes:
```
Bash: git add {workspace files}
Bash: git commit -m "refactor(js): {workspace-name} - standards compliance improvements"
```

Track in `workspaces_completed` counter.

**Continue to next workspace/batch.**

### Step 6: Final Verification

After all workspaces/files processed:

**6.1 Complete Build:**
```
Task:
  subagent_type: npm-builder
  description: Final build verification
  prompt: |
    Execute complete build to verify all changes.

    Parameters:
    - command: run build

    Full build must pass.
```

**6.2 Full Test Suite:**
```
Task:
  subagent_type: npm-builder
  description: Final test verification
  prompt: |
    Execute complete test suite.

    Parameters:
    - command: run test

    All tests must pass.
```

**6.3 Lint Verification:**
```
Task:
  subagent_type: npm-builder
  description: Lint verification
  prompt: |
    Execute lint checks.

    Parameters:
    - command: run lint

    All lint checks must pass.
```

**6.4 Coverage Verification:**
```
SlashCommand: /javascript-coverage-report
```

Compare final coverage to baseline:
- Display coverage change
- Ensure no significant regression

**6.5 Standards Compliance Verification:**

Apply compliance checklist from cui-javascript-maintenance:

For sample of refactored files:
- Verify vanilla JavaScript usage
- Verify test code separation
- Verify modularization
- Verify package.json
- Verify JSDoc coverage
- Verify modern patterns
- Verify code quality

Report compliance status.

### Step 7: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║          Refactoring Summary                               ║
╚════════════════════════════════════════════════════════════╝

Scope: {scope}
Priority Filter: {priority}

Workspaces Processed: {workspaces_completed} / {total_workspaces}
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
Lint: {SUCCESS/FAILURE}

Compliance: {compliant_categories} / {total_categories} categories compliant

Time Taken: {elapsed_time}
```

## STATISTICS TRACKING

Track throughout workflow:
- `pre_verification_failures`: Pre-maintenance verification failures
- `analysis_failures`: Standards audit failures
- `workspaces_completed`: Workspaces successfully refactored
- `workspaces_failed`: Workspaces that failed verification
- `fixes_applied`: Individual violation fixes applied
- `fixes_failed`: Individual fixes that failed
- `fixes_skipped`: Violations skipped by user
- `workspace_verification_failures`: Workspace verification failures
- `coverage_baseline`: Initial coverage percentage
- `coverage_final`: Final coverage percentage
- `elapsed_time`: Total execution time

Display all statistics in final summary.

## CRITICAL CONSTRAINTS

**Functionality Preservation:**
- **NO BEHAVIOR CHANGES** unless fixing confirmed bugs
- All existing tests must continue to pass
- API compatibility maintained for public APIs
- Browser compatibility maintained

**Safety Protocols:**
- Incremental changes (workspace-by-workspace or file-by-file)
- Continuous verification after each workspace/batch
- Ability to rollback at workspace level
- User confirmation before major changes

**File-by-File/Workspace Strategy:**
- Process one workspace/batch completely before next
- Verify and commit each workspace independently
- Maintain build stability after each workspace
- Process in dependency order if applicable

## SCOPE DEFINITIONS

**`full` (default):**
- All violation types
- Complete standards compliance audit
- All priorities (unless filtered)

**`standards`:**
- Code organization violations
- Vanilla JavaScript enforcement
- Test code separation
- JSDoc coverage
- Modern pattern adoption

**`unused`:**
- Unused variables and imports
- Dead code elimination
- Unreachable code
- With user approval for removals

**`modernize`:**
- var → const/let
- Callbacks → async/await
- Legacy loops → array methods
- jQuery → vanilla JavaScript
- CommonJS → ES modules

**`documentation`:**
- Missing JSDoc
- Outdated documentation
- Trivial comments removal
- Documentation standards compliance

## PRIORITY FILTER BEHAVIOR

**`high`:**
- Only HIGH priority violations
- Security issues
- Test code in production
- Critical code quality issues

**`medium`:**
- HIGH and MEDIUM priority violations
- Includes maintainability issues
- Code organization and modernization

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
- Attempt automatic fixes via npm-builder
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

**Workspace-level rollback:**
```
Bash: git reset HEAD~1  # Rollback workspace commit
Bash: git checkout -- {workspace}  # Restore workspace files
```

**Complete rollback:**
```
Bash: git reset --hard {initial_commit}  # Restore to pre-refactor state
```

## USAGE EXAMPLES

**Full refactoring (all workspaces, all priorities):**
```
/cui-javascript-refactor
```

**Single workspace refactoring:**
```
/cui-javascript-refactor workspace=frontend
```

**Only high priority violations:**
```
/cui-javascript-refactor priority=high
```

**Modernize code only:**
```
/cui-javascript-refactor scope=modernize
```

**Remove unused code:**
```
/cui-javascript-refactor scope=unused priority=medium
```

**Documentation improvements only:**
```
/cui-javascript-refactor scope=documentation workspace=core
```

**Combination:**
```
/cui-javascript-refactor workspace=ui scope=standards priority=high
```

## ARCHITECTURE

Orchestrates agents and commands:
- **cui-javascript-maintenance skill** - Standards for detection, prioritization, verification
- **Explore agent** - Codebase analysis for violation detection
- **javascript-code-implementer agent** - Focused code fixes (Layer 3)
- **npm-builder agent** - Build and verification (Layer 3)
- **`/javascript-coverage-report` command** - Coverage analysis

## RELATED

- `cui-javascript-maintenance` skill - Standards this command implements
- `javascript-code-implementer` agent - Implementation fixes
- `npm-builder` agent - Build verification
- `/javascript-coverage-report` command - Coverage analysis
- `cui-javascript` skill - Implementation patterns
- `cui-task-planning` skill - For refactoring task planning
