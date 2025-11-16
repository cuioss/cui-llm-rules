---
name: orchestrate-language
description: Implements Java or JavaScript tasks end-to-end with automated testing and coverage verification
---

# CUI Language Task Orchestrator Command

Orchestrates complete task implementation through code creation, unit testing, and coverage verification workflow. Supports both Java and JavaScript projects with language-specific tooling.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=orchestrate-language update="[your improvement]"` with:
1. Improved agent coordination patterns and error recovery strategies
2. Better coverage gap analysis and iterative fix workflows
3. More effective parameter preparation for agent handoffs
4. Enhanced detection of production vs. test code issues
5. Language-specific patterns and tooling improvements
6. Any lessons learned about task implementation workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **language** - (Optional) Target language: `java` or `javascript`. If not specified, auto-detects from targets
- **targets** - For Java: type(s), package(s), or name(s) of type(s). For JavaScript: file(s), component(s), or name(s)
- **description** - Detailed, precise description of what to implement
- **module** - (Optional) Maven module name (Java) or npm workspace name (JavaScript) for monorepo projects

## LANGUAGE CONFIGURATION

The command adapts its behavior based on the language parameter:

### Java Configuration
- **Builder for iteration**: maven-builder agent (fast verification during development)
- **Implementation**: `/java-implement-code` command
- **Testing**: `/java-implement-tests` command
- **Coverage**: `/java-generate-coverage` command
- **Parameter name**: `types` (forwarded from `targets`)
- **Module type**: Maven module

### JavaScript Configuration
- **Builder for iteration**: npm-builder agent (fast verification during development: `npm test`, `npm run build`)
- **Implementation**: `/js-implement-code` command
- **Testing**: `/js-implement-tests` command
- **Coverage**: `/js-generate-coverage` command
- **Parameter name**: `files` (forwarded from `targets`)
- **Module type**: npm workspace

### Final Build Verification
**Note**: Regardless of language, final build verification at workflow level (orchestrate-workflow) always uses Maven build. JavaScript projects use `frontend-maven-plugin` for Maven integration.

## WORKFLOW

### Step 0: Language Detection

If `language` parameter not provided, auto-detect from `targets`:

**Detection rules:**
- Contains `.java` extension or Java-style names (CamelCase without extension) → `language=java`
- Contains `.js`, `.ts`, `.jsx`, `.tsx` extensions → `language=javascript`
- If ambiguous: Prompt user to specify language parameter explicitly

**Validation:**
- Verify `language` is either `java` or `javascript`
- If invalid: Display error "Invalid language. Must be 'java' or 'javascript'" and abort

### Step 1: Determine Entry Point

Analyze the `description` parameter to determine workflow entry point:

- **Contains "implement", "create", "add feature"** → Start at Step 2 (Implementation)
- **Contains "test", "unit test", "junit" (Java) or "jest" (JavaScript)** → Start at Step 3 (Testing)
- **Contains "coverage", "verify coverage", "fix coverage"** → Start at Step 4 (Coverage)

### Step 2: Implementation Phase

Call language-specific self-contained command:

**For Java:**
```
SlashCommand: /cui-java-expert:java-implement-code
Parameters: |
  types={targets}
  description={description}
  module={module or 'single-module project'}
```

**For JavaScript:**
```
SlashCommand: /cui-frontend-expert:js-implement-code
Parameters: |
  files={targets}
  description={description}
  workspace={module}
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

Analyze Step 2 results and call language-specific self-contained command:

**For Java:**
```
SlashCommand: /cui-java-expert:java-implement-tests
Parameters: |
  types={targets}
  description=Implement unit tests for {targets}
  context={summary from Step 2}
  module={module}
```

**For JavaScript:**
```
SlashCommand: /cui-frontend-expert:js-implement-tests
Parameters: |
  files={targets}
  description=Implement unit tests for {targets}
  context={summary from Step 2}
  workspace={module}
```

This command handles test implementation AND verification internally (writes tests → runs tests → iterates).

**On success:**
- Analyze test implementation result
- Continue to Step 4

**On error indicating production code issue:**
- Analyze root cause
- Return to Step 2 with adapted description: "Fix {identified issue} in {targets}"
- Track in `production_fixes` counter

**On error indicating test code issue:**
- Command returns error details
- If unresolvable, ask caller
- Track in `test_retries` counter

### Step 4: Coverage Verification Phase

Call language-specific self-contained command:

**For Java:**
```
SlashCommand: /cui-java-expert:java-generate-coverage
Parameters: |
  types={targets}
  module={module}
```

**For JavaScript:**
```
SlashCommand: /cui-frontend-expert:js-generate-coverage
Parameters: |
  files={targets}
  workspace={module}
```

This command handles coverage generation AND analysis internally.

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
- `production_fixes`: Production code fixes (Java only tracks this separately)
- `test_fixes`: Test code fixes (Java only tracks this separately)
- `total_cycles`: Complete workflow cycles executed
- `language_used`: Language selected/detected for the workflow

Display all statistics in final summary.

## CRITICAL RULES

**Parameter Validation:**
- `targets` and `description` are required
- `language` auto-detects from targets if not specified
- `module` defaults to single-module/workspace if unset
- Validate parameters before calling first command

**Language-Specific Handling:**
- Use correct builder for iteration: maven-builder (Java) vs npm-builder (JavaScript)
- Use correct command prefix: /cui-java-expert vs /cui-frontend-expert
- Use correct parameter names: types (Java) vs files (JavaScript)
- Note: Final workflow-level build always uses Maven regardless of language

**Command Coordination:**
- Always analyze command results before next call
- Prepare precise parameters for each command
- Never guess - ask caller if command output unclear
- Self-contained commands handle their own verification internally

**Error Handling:**
- Distinguish production vs. test code issues
- Return to appropriate workflow step
- Track all retries and fixes
- Prevent infinite loops (max 5 iterations)

**Coverage Goals:**
- Continue until ALL findings show "✅ SUFFICIENT"
- Process coverage gaps sequentially
- Each gap gets dedicated test implementation

**Entry Point Flexibility:**
- Support starting at Steps 2, 3, or 4 based on description
- Validate entry point choice with caller if ambiguous

## USAGE EXAMPLES

**Java - Full implementation:**
```
/orchestrate-language language=java targets=UserService description="Implement user authentication with JWT tokens" module=auth-service
```

**Java - Auto-detect language:**
```
/orchestrate-language targets=UserService,TokenValidator description="Implement user authentication with JWT tokens"
```

**Java - Testing existing code:**
```
/orchestrate-language targets=OrderProcessor description="Implement unit tests for OrderProcessor" module=order-service
```

**Java - Coverage verification:**
```
/orchestrate-language targets=PaymentHandler description="Verify and fix test coverage for PaymentHandler"
```

**JavaScript - Full implementation:**
```
/orchestrate-language language=javascript targets="src/services/auth.js" description="Implement user authentication with JWT tokens" module="packages/core"
```

**JavaScript - Auto-detect language:**
```
/orchestrate-language targets="src/utils/formatter.js,src/utils/validator.js" description="Implement utility functions for data formatting and validation"
```

**JavaScript - Testing existing code:**
```
/orchestrate-language targets="src/components/UserProfile.jsx" description="Implement unit tests for UserProfile component"
```

## RELATED

### Java Commands
- `/java-implement-code` - Self-contained command for Java production code implementation + verification
- `/java-implement-tests` - Self-contained command for JUnit test implementation + verification
- `/java-generate-coverage` - Self-contained command for JaCoCo coverage generation + analysis

### JavaScript Commands
- `/js-implement-code` - Self-contained command for JavaScript production code implementation + verification
- `/js-implement-tests` - Self-contained command for Jest test implementation + verification
- `/js-generate-coverage` - Self-contained command for JavaScript coverage generation + analysis

### Orchestration
- `/orchestrate-workflow` - End-to-end issue implementation (uses Maven for final build regardless of language)
- `/orchestrate-task` - Self-contained single task execution and verification
