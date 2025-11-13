---
name: cui-orchestrate-java-task
description: Implements Java tasks end-to-end with automated testing and coverage verification
---

# CUI Java Task Manager Command

Orchestrates complete Java task implementation through code creation, unit testing, and coverage verification workflow. Delegates to self-contained commands iteratively until full coverage is achieved.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-orchestrate-java-task update="[your improvement]"` with:
1. Improved agent coordination patterns and error recovery strategies
2. Better coverage gap analysis and iterative fix workflows
3. More effective parameter preparation for agent handoffs
4. Enhanced detection of production vs. test code issues
5. Any lessons learned about Java task implementation workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **types** - Existing type(s), package(s), or name(s) of type(s) to be created
- **description** - Detailed, precise description of what to implement
- **module** - (Optional) Module name for multi-module projects; if unset, assume single-module

## WORKFLOW

### Step 1: Determine Entry Point

Analyze the `description` parameter to determine workflow entry point:

- **Contains "implement", "create", "add feature"** → Start at Step 2 (Implementation)
- **Contains "test", "unit test", "junit"** → Start at Step 3 (Testing)
- **Contains "coverage", "verify coverage", "fix coverage"** → Start at Step 4 (Coverage)

### Step 2: Implementation Phase

Call self-contained command `/cui-java-implement-code`:

```
SlashCommand: /cui-java-implement-code
Parameters: |
  types={types}
  description={description}
  module={module or 'single-module project'}
```

This command handles implementation AND verification internally (implements → verifies → iterates).

**On success:**
- Analyze implementation result
- Prepare parameters for Step 3
- Continue to Step 3

**On error/problems:**
- Command returns error details
- If unresolvable, ask caller for guidance
- Track in `implementation_retries` counter

### Step 3: Unit Testing Phase

Analyze Step 2 results and call self-contained command `/cui-java-implement-tests`:

```
SlashCommand: /cui-java-implement-tests
Parameters: |
  types={types}
  description=Implement unit tests for {types}
  context={summary from Step 2}
  module={module}
```

This command handles test implementation AND verification internally (writes tests → runs tests → iterates).

**On success:**
- Analyze test implementation result
- Continue to Step 4

**On error indicating production code issue:**
- Analyze root cause
- Return to Step 2 with adapted description: "Fix {identified issue} in {types}"
- Track in `production_fixes` counter

**On error indicating test code issue:**
- Command returns error details
- If unresolvable, ask caller
- Track in `test_retries` counter

### Step 4: Coverage Verification Phase

Call self-contained command `/cui-java-generate-coverage`:

```
SlashCommand: /cui-java-generate-coverage
Parameters: |
  types={types}
  module={module}
```

This command handles coverage generation AND analysis internally (builds with -Pcoverage → analyzes JaCoCo reports).

**On error indicating production code issue:**
- Return to Step 2 with adapted description
- Track in `production_fixes` counter

**On error indicating test code issue:**
- Return to Step 3 with adapted description
- Track in `test_fixes` counter

**On success with coverage results:**

Analyze each coverage finding:

- **For each "Coverage: ❌ INSUFFICIENT":**
  - Return to Step 3 with description: "Add tests for {specific uncovered code path}"
  - Process sequentially (one at a time)
  - Track in `coverage_fixes` counter

- **All "Coverage: ✅ SUFFICIENT":**
  - Workflow complete
  - Display final summary

### Step 5: Iterative Refinement

Continue cycling through Steps 2-4 until:
- All coverage reports show "✅ SUFFICIENT"
- No production or test errors remain

**Maximum iterations:** 5 cycles
- **If exceeded:** Report status and ask caller for guidance

## STATISTICS TRACKING

Track throughout workflow:
- `implementation_retries`: Implementation phase retries
- `test_retries`: Test phase retries
- `coverage_fixes`: Coverage gap fixes applied
- `production_fixes`: Production code fixes
- `test_fixes`: Test code fixes
- `total_cycles`: Complete workflow cycles executed

Display all statistics in final summary.

## CRITICAL RULES

**Parameter Validation:**
- `types` and `description` are required
- `module` defaults to single-module if unset
- Validate parameters before calling first agent

**Command Coordination:**
- Always analyze command results before next call
- Prepare precise parameters for each command
- Never guess - ask caller if command output unclear
- Self-contained commands handle their own verification internally

**Error Handling:**
- Distinguish production vs. test code issues
- Return to appropriate workflow step
- Track all retries and fixes
- Prevent infinite loops (max 5 cycles)

**Coverage Goals:**
- Continue until ALL findings show "✅ SUFFICIENT"
- Process coverage gaps sequentially
- Each gap gets dedicated test implementation

**Entry Point Flexibility:**
- Support starting at Steps 2, 3, or 4 based on description
- Validate entry point choice with caller if ambiguous

## USAGE EXAMPLES

**Full implementation:**
```
/cui-orchestrate-java-task types=UserService description="Implement user authentication with JWT tokens" module=auth-service
```

**Testing existing code:**
```
/cui-orchestrate-java-task types=OrderProcessor description="Implement unit tests for OrderProcessor" module=order-service
```

**Coverage verification:**
```
/cui-orchestrate-java-task types=PaymentHandler description="Verify and fix test coverage for PaymentHandler"
```

**Single-module project:**
```
/cui-orchestrate-java-task types=com.example.util.StringUtils description="Add string validation utilities"
```

## RELATED

- `/cui-java-implement-code` - Self-contained command for production code implementation + verification
- `/cui-java-implement-tests` - Self-contained command for unit test implementation + verification
- `/cui-java-generate-coverage` - Self-contained command for coverage generation + analysis
