---
name: javascript-implement-code
description: Self-contained command for JavaScript code implementation with verification and iteration
---

# JavaScript Implement Code Command

Self-contained command that orchestrates JavaScript implementation through code creation and build verification workflow with iteration until clean.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/cui-update-command command-name=javascript-implement-code update="[your improvement]"` with:
1. Improved agent coordination patterns and error recovery strategies
2. Better build error analysis and iterative fix workflows
3. More effective parameter preparation for agent handoffs
4. Enhanced detection of implementation vs build issues
5. Any lessons learned about JavaScript implementation verification workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **files** - File(s), component(s), or name(s) of file(s) to implement/create
- **description** - Detailed, precise description of what to implement
- **workspace** - (Optional) Workspace name for monorepo projects

## WORKFLOW

### Step 1: Verify Build Precondition

Execute clean build using npm-builder:

```
Task:
  subagent_type: npm-builder
  description: Verify clean build
  prompt: |
    Execute npm build to verify codebase compiles cleanly.

    Parameters:
    - command: run build
    - outputMode: DEFAULT
    {- workspace: [workspace] (if specified)}

    CRITICAL: Build must succeed with ZERO errors and ZERO warnings.
    Return status and any issues found.
```

**On build failure:**
- Display build errors/warnings
- Prompt user: "[F]ix manually and retry / [C]ontinue anyway (risky) / [A]bort"
- If continue: proceed with warning
- If abort: exit command

### Step 2: Implementation Phase

Call javascript-code-implementer agent:

```
Task:
  subagent_type: javascript-code-implementer
  description: Implement JavaScript code
  prompt: |
    Implement modern JavaScript code following CUI frontend standards.

    Parameters:
    - files: {files}
    - description: {description}
    - workspace: {workspace or 'single package'}

    Return implementation results including files created/modified.
```

**On success:**
- Analyze implementation result
- Extract files created/modified
- Continue to Step 3

**On error:**
- Display error details
- Prompt user for clarification if needed
- Retry or abort based on error type

### Step 3: Post-Implementation Build Verification

Execute build using npm-builder:

```
Task:
  subagent_type: npm-builder
  description: Verify implementation builds
  prompt: |
    Execute npm build to verify implementation compiles cleanly.

    Parameters:
    - command: run build
    - outputMode: STRUCTURED
    {- workspace: [workspace] (if specified)}

    Return structured results with categorized issues.
```

**Analyze build results:**
- If SUCCESS with no errors/warnings: Command complete, return success
- If SUCCESS with warnings: Fix warnings (Step 4)
- If FAILURE: Fix errors (Step 4)

### Step 4: Iterative Fix Loop

**Maximum 5 iterations**

For each build issue found:

1. **Categorize issue type** (from STRUCTURED output):
   - compilation_error: Syntax/type errors
   - lint_error: ESLint violations
   - other: Other build issues

2. **Delegate fix to javascript-code-implementer**:
   ```
   Task:
     subagent_type: javascript-code-implementer
     description: Fix build issue
     prompt: |
       Fix the following build issue:

       Issue Type: {issue_type}
       File: {file}
       Line: {line}
       Message: {message}

       Review the code and apply appropriate fix following standards.
   ```

3. **Re-run build** (return to Step 3)

4. **Track iterations**:
   - Increment `fix_iterations` counter
   - If > 5 iterations: Return failure with remaining issues
   - If build clean: Return success

### Step 5: Return Results

**Success format:**
```
IMPLEMENTATION COMPLETE

What Was Implemented:
{summary from javascript-code-implementer}

Files Created/Modified:
{list of files}

Build Status: ✅ SUCCESS (no errors, no warnings)
Build Iterations: {fix_iterations}

Total Time: {elapsed_time}

Result: ✅ Implementation verified and building cleanly
```

**Partial Success (max iterations reached):**
```
IMPLEMENTATION PARTIAL

What Was Implemented:
{summary}

Build Status: ⚠️ PARTIAL (still has issues after 5 fix iterations)

Remaining Issues:
{list of unresolved build issues}

Recommendation: Manual review and fixes needed for remaining issues

Result: ⚠️ Implementation complete but build has unresolved issues
```

## CRITICAL RULES

**Precondition Verification:**
- ALWAYS verify clean build before implementation
- PROMPT user if precondition fails
- ALLOW continue with warning or abort

**Agent Orchestration:**
- USE javascript-code-implementer for all code changes
- USE npm-builder for all build operations
- NEVER modify code directly in command
- ALWAYS delegate to appropriate agent

**Build Verification:**
- ALWAYS verify after implementation
- USE STRUCTURED output mode for detailed issue tracking
- ANALYZE and categorize each issue
- ITERATE until clean or max retries

**Iteration Control:**
- MAXIMUM 5 fix iterations
- TRACK iteration count
- RETURN failure if max exceeded
- CLEAR error messages for user

**Parameter Validation:**
- files and description are required
- workspace defaults to single package
- VALIDATE all parameters before delegation

## TOOL USAGE

- **Task**: Orchestrate javascript-code-implementer and npm-builder agents
- Other tools: Not needed (command orchestrates only)

## USAGE EXAMPLES

**Simple implementation:**
```
/javascript-implement-code files="src/utils/validator.js" description="Implement email and phone validation functions"
```

**Component implementation:**
```
/javascript-implement-code files="src/components/Button.js" description="Create reusable Button component with variants and sizes"
```

**Monorepo workspace:**
```
/javascript-implement-code files="src/services/api.js" description="Implement REST API client with authentication" workspace="packages/core"
```

## RELATED

- `javascript-code-implementer` - Agent that implements code (Layer 3)
- `npm-builder` - Agent that executes builds (Layer 3)
- `/cui-javascript-task-manager` - End-to-end task orchestration (Layer 2)

You orchestrate focused agents to implement and verify JavaScript code - reliable, iterative, and thorough.
