---
name: cui-fix-intellij-diagnostics
description: Retrieve and fix IDE diagnostics automatically, suppressing only when no reasonable fix is available
---

# Fix IDE Diagnostics Command

Retrieves IDE diagnostics for the current file, analyzes issues, and applies sensible fixes. Suppresses Sonar issues only when no reasonable fix is available.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** with:
1. Improved diagnostic retrieval methods (especially file activation techniques)
2. Better fix patterns for specific diagnostic types
3. More effective suppression strategies and documentation
4. Enhanced IDE MCP server interaction patterns
5. New categories of auto-fixable issues discovered
6. Improved build verification and loop-back logic
7. Any lessons learned about diagnostic analysis

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

### Standard Parameters

- **push**: Optional flag to automatically commit and push changes after successful execution
  - Usage: `/fix-intellij-diagnostics push`
  - Only executes if all post-conditions are met (build passes, no new errors)

### Custom Parameters

- **file=<path>**: Optional. Specifies the file to check for diagnostics
  - If not provided: Uses currently active file in IDE
  - If provided: Must be an existing project file
  - Path can be absolute or relative to project root
  - Examples:
    - `/fix-intellij-diagnostics file=src/main/java/MyClass.java`
    - `/fix-intellij-diagnostics file=src/test/java/MyTest.java push`

- **auto-fix=<boolean>**: Optional. Controls automatic fixing behavior
  - Default: `true`
  - If `true`: Automatically applies fixes that are 100% certain
  - If `false`: Prompts user for approval before each fix
  - Must be boolean value (true/false)
  - Examples:
    - `/fix-intellij-diagnostics auto-fix=false`
    - `/fix-intellij-diagnostics file=MyClass.java auto-fix=true push`

## PARAMETER VALIDATION

**Step 1: Validate Parameters**

1. **Validate file parameter** (if provided):
   - Check that file exists in project directory
   - Verify it's not outside project bounds
   - Confirm file is readable
   - If validation fails: Display error and exit

2. **Validate auto-fix parameter** (if provided):
   - Must be exactly "true" or "false" (case-insensitive)
   - If invalid: Display error with valid options and exit
   - If not provided: Default to `true`

3. **Validate push parameter** (if provided):
   - No validation needed (flag parameter)
   - Store for use in final step

## WORKFLOW INSTRUCTIONS

### PRE-CONDITION VERIFICATION

**Before starting main workflow, verify all pre-conditions:**

1. **Check JetBrains IDE and MCP Server**:
   - Verify MCP server is responding (check if port 64342 is active or attempt a diagnostic call)
   - If not available: Display error message with instructions to start IDE with MCP enabled
   - Exit if pre-condition not met

2. **Determine Target File**:
   - If `file` parameter provided: Use that file path
   - If no `file` parameter: Attempt to detect currently active file in IDE
   - If no active file and no parameter: Prompt user to either:
     - Activate a file in IDE and retry
     - Provide file parameter explicitly

3. **Verify File Accessibility**:
   - Confirm file exists and is within project directory
   - Verify user has write permissions
   - If file not accessible: Display error and exit

4. **Verify Project is Build-able**:
   - Check for build configuration (pom.xml, build.gradle, etc.)
   - If no build system detected: Warn user that step 7 (build verification) will be skipped
   - Continue execution (build verification is nice-to-have but not blocking)

**If any critical pre-condition fails, STOP execution and inform user.**

---

### MAIN WORKFLOW

**Step 1: Retrieve IDE Diagnostics**

1.1. Use `mcp__jetbrains__get_file_problems` tool to retrieve diagnostics:
   - Set `filePath` to the target file (relative to project root)
   - Set `errorsOnly: false` to get both errors and warnings
   - Set reasonable timeout (e.g., 120000ms)

1.2. Handle common retrieval issues:
   - **Timeout**: File may not be active in IDE
     - Inform user: "The file must be active (focused) in your IDE. Please click on the file tab in IntelliJ and run the command again."
     - Exit and ask user to retry after activating file
   - **Empty result**: No diagnostics found
     - Inform user: "No diagnostics found for this file. File is clean!"
     - Skip to Step 8 (Report Results)
   - **MCP Error**: Server not responding
     - Inform user to check IDE MCP server status
     - Exit with instructions

1.3. Parse diagnostics:
   - Extract: message, severity, line number, character range
   - Count total: errors, warnings, info messages
   - Display summary: "Found X errors, Y warnings in {filename}"

**Step 2: Analyze Each Diagnostic**

For each diagnostic issue found:

2.1. **Read Code Context**:
   - Use Read tool to examine the file around the diagnostic location
   - Read at least 10 lines before and after the issue line
   - Understand the surrounding code structure

2.2. **Categorize the Issue**:
   - **Category A - Auto-fixable**: 100% certain fix available
     - Examples: unused imports, missing @Override, simple type errors
     - Can be fixed without risk of breaking logic
   - **Category B - Manual review needed**: Fix requires understanding of business logic
     - Examples: null-safety issues, complex refactoring, architectural decisions
     - Requires user approval before fixing
   - **Category C - Suppress candidate**: No reasonable fix available
     - Examples: false positives, intentional patterns, external library issues
     - Last resort - only if Categories A and B don't apply

2.3. **Create Fix Strategy**:
   - For Category A: Prepare exact Edit operation
   - For Category B: Prepare options for user to choose
   - For Category C: Prepare suppression comment with justification

**Step 3: Apply Fixes Based on auto-fix Setting**

3.1. **If auto-fix=true**:
   - For each Category A issue:
     - Apply fix using Edit tool
     - Log the fix: "Fixed: {issue message} at line {line}"
     - Track fix count

   - For each Category B issue:
     - Display issue details and proposed fix
     - Ask user: "Apply this fix? (y/n/s for skip)"
     - If 'y': Apply fix and log
     - If 'n': Skip this issue (flag for manual review)
     - If 's': Skip all remaining Category B issues

   - For Category C issues:
     - Skip to Step 5 (Handle Suppressions)

3.2. **If auto-fix=false**:
   - For ALL issues (A, B, C):
     - Display issue details
     - Show proposed action (fix, manual review, or suppress)
     - Ask user: "Proceed with this action? (y/n/s for skip all)"
     - Apply only if user confirms

**Step 4: Track Applied Changes**

4.1. Maintain a log of all changes made:
   - Fixes applied (with line numbers)
   - Issues skipped for manual review
   - User decisions recorded

4.2. Display progress:
   - "Processed X of Y issues"
   - "Applied Z fixes so far"

**Step 5: Handle Suppressions (Last Resort)**

5.1. For each Category C issue (suppress candidates):
   - **Attempt to fix first**: Double-check if there's ANY reasonable fix
   - Only proceed to suppression if truly no sensible fix exists

5.2. **If suppression is necessary**:
   - Determine appropriate suppression syntax:
     - Sonar: `//NOSONAR` or `@SuppressWarnings`
     - Checkstyle: `//CHECKSTYLE:OFF` / `//CHECKSTYLE:ON`
     - SpotBugs: `@SuppressFBWarnings`
     - IDE inspections: `//noinspection {InspectionName}`

   - Add suppression comment with justification:
     ```java
     // Suppressed: {issue message}
     // Reason: {why no reasonable fix exists}
     // Reviewed: {date}
     @SuppressWarnings("specific-warning-name")
     ```

5.3. **Document each suppression**:
   - Log: "Suppressed: {issue} at line {line} - Reason: {justification}"
   - Track suppression count

**Step 6: Re-verify Diagnostics (Loop Point A)**

6.1. Re-run diagnostics on the modified file:
   - Use same `mcp__jetbrains__get_file_problems` call
   - Compare new diagnostics with original set

6.2. **Analyze results**:
   - If new errors introduced by fixes:
     - Display: "Fixes introduced new errors. Analyzing..."
     - **Loop back to Step 2** with new diagnostic set
     - Track loop count (max 3 iterations to prevent infinite loops)

   - If all original issues resolved/suppressed and no new issues:
     - Proceed to Step 7

   - If unable to resolve after 3 loops:
     - Display: "Unable to fully resolve all issues after 3 attempts"
     - Proceed to Step 7 with current state

**Step 7: Verify Project Build**

7.1. **Use maven-project-builder agent**:
   - Use Task tool with `subagent_type: "maven-project-builder"`
   - Prompt: "Build and verify the project with all quality checks. Include pre-commit verification."
   - This will run Maven/Gradle with tests and quality gates

7.2. **Handle build results**:
   - **If build succeeds**:
     - Log: "✓ Project build successful - all tests passing"
     - Proceed to Step 8

   - **If build fails**:
     - Display: "Build failed after applying fixes. Analyzing failures..."
     - Read build output to identify issues
     - Categorize failures:
       - Related to our fixes: Need to revert or adjust
       - Unrelated: Pre-existing issues

     - **If related to our fixes (Loop Point B)**:
       - Ask user: "Revert last fixes and retry? (y/n)"
       - If yes: Revert problematic changes, loop back to Step 3
       - If no: Proceed to Step 8 with build failure noted

     - **If unrelated**:
       - Inform user: "Build failures appear unrelated to diagnostic fixes"
       - Proceed to Step 8

7.3. **Track build attempt**:
   - Record build success/failure
   - Note any build-related issues for final report

**Step 8: Report Results**

8.1. **Generate comprehensive summary**:

```
╔════════════════════════════════════════════════════════════╗
║          IDE Diagnostics Fix Report                        ║
╔════════════════════════════════════════════════════════════╝

File: {filename}

Original Diagnostics:
  - Errors: {error_count}
  - Warnings: {warning_count}
  - Total: {total_count}

Actions Taken:
  ✓ Fixes Applied: {fix_count}
    {list each fix with line number}

  ⚠ Suppressions Added: {suppression_count}
    {list each suppression with reason}

  ⏭ Skipped for Manual Review: {skip_count}
    {list each skipped issue with reason}

Build Verification:
  {✓ or ✗} Build Status: {Success/Failed}
  {✓ or ✗} Tests: {X passed, Y failed}
  {✓ or ✗} Quality Gates: {Passed/Failed}

Remaining Work:
  {list any issues that need manual attention}

Diagnostic Re-check:
  - Remaining Errors: {remaining_errors}
  - Remaining Warnings: {remaining_warnings}

Post-Conditions Status:
  {✓ or ✗} All auto-fixable issues resolved
  {✓ or ✗} Project builds successfully
  {✓ or ✗} No new errors introduced
  {✓ or ✗} All changes justified and documented

╚════════════════════════════════════════════════════════════
```

8.2. **Provide recommendations**:
   - If issues remain: Suggest next steps for manual fixes
   - If suppressions added: Recommend reviewing them periodically
   - If build failed: Provide debugging guidance

**Step 9: Commit & Push (if push parameter provided)**

9.1. **Verify post-conditions before push**:
   - Build MUST be successful (if build verification was run)
   - No new errors introduced
   - At least one fix applied (don't push if no changes)

9.2. **If post-conditions met**:
   - Invoke commit-changes agent to commit and push:
     - Use Task tool with subagent_type: "commit-changes"
     - Prompt: "Commit all changes with message 'fix: resolve IDE diagnostics in {filename}

     - Applied {fix_count} automatic fixes
     - Suppressed {suppression_count} issues (with justification)
     - All tests passing

     Issues resolved:
     {list key issues fixed}', and push"
     - Wait for agent completion
   - Display agent's final report showing commit status and push result

9.3. **If post-conditions NOT met**:
   - Display: "Cannot push: Post-conditions not satisfied"
   - List which conditions failed
   - Suggest: "Fix remaining issues and run with 'push' parameter again"
   - Exit without pushing

---

### POST-CONDITION VERIFICATION

**After workflow completion, verify all post-conditions:**

1. **All auto-fixable diagnostics resolved**:
   - Re-run diagnostics one final time
   - Confirm no Category A issues remain
   - If any remain: Report as incomplete execution

2. **Issues appropriately handled**:
   - Fixed issues: Verified in code
   - Suppressed issues: Have justification comments
   - Manual review issues: Flagged in report

3. **Project builds successfully**:
   - Build exit code is 0
   - All tests passing
   - No quality gate failures

4. **No new errors introduced**:
   - Compare final diagnostic count with original
   - Final error count ≤ original error count
   - New warnings are documented and justified

5. **Changes tracked**:
   - If push used: Changes committed and pushed
   - If push not used: User informed of uncommitted changes
   - All changes logged in report

6. **User informed**:
   - Comprehensive report displayed
   - Remaining work clearly identified
   - Next steps suggested

**If any post-condition fails: Report it clearly in final summary.**

---

## CRITICAL RULES

### Absolute Constraints (NEVER Violate)

1. **NEVER suppress issues without attempting to fix them first**
   - Suppression is the last resort
   - Must document why no fix is possible
   - Requires clear justification in code comments

2. **NEVER apply fixes that you're less than 100% certain about (unless user approves)**
   - Auto-fix only for Category A (completely certain) issues
   - All Category B issues require user approval
   - When in doubt, ask the user

3. **NEVER proceed with push if project build fails**
   - Build success is a hard requirement for push
   - Must verify all tests pass
   - Quality gates must be satisfied

4. **NEVER modify files outside the project directory**
   - All file operations must be within project bounds
   - Validate file paths before any write operation
   - Reject absolute paths outside project

### Pre-Conditions (Must Be True Before Execution)

- JetBrains IDE must be running with MCP server enabled
- Target file must exist in the project (if file parameter provided)
- If no file parameter: IDE must have an active file open
- User must have write permissions to modify files
- Project must be a valid build-able project

### Post-Conditions (Must Be True After Successful Execution)

- All auto-fixable diagnostics have been resolved
- Remaining issues are either suppressed (with justification) or flagged for manual review
- Project builds successfully with all tests passing
- No new errors or warnings introduced by fixes
- If push parameter used: Changes are committed and pushed to remote
- User is informed of all changes made and remaining work

### Best Practices for Diagnostic Fixing

1. **Always read context before fixing**
   - Understand surrounding code
   - Consider business logic implications
   - Don't blindly apply fixes

2. **Categorize carefully**
   - Be conservative with Category A (auto-fix)
   - When uncertain, move to Category B (user approval)
   - Only suppress as absolute last resort

3. **Loop protection**
   - Maximum 3 iterations of fix-verify-refix
   - Track changes between iterations
   - If stuck in loop, stop and report

4. **Build verification is critical**
   - Never skip if build system exists
   - Always analyze build failures
   - Relate failures back to applied fixes

5. **Clear communication**
   - Show progress at each step
   - Explain why each fix is being applied
   - Document suppressions thoroughly

6. **File activation issues**
   - JetBrains MCP requires file to be active/focused in IDE
   - If timeout occurs, instruct user to activate file
   - Don't attempt to activate files programmatically

## USAGE EXAMPLES

### Example 1: Fix diagnostics in current file with auto-fix
```bash
/fix-intellij-diagnostics
```
Result: Analyzes and fixes issues in currently active IDE file automatically.

### Example 2: Fix specific file without auto-fix
```bash
/fix-intellij-diagnostics file=src/main/java/MyClass.java auto-fix=false
```
Result: Analyzes MyClass.java, prompts for approval before each fix.

### Example 3: Fix and push changes
```bash
/fix-intellij-diagnostics push
```
Result: Fixes current file, verifies build, commits and pushes if successful.

### Example 4: Fix specific file and push
```bash
/fix-intellij-diagnostics file=src/test/java/MyTest.java auto-fix=true push
```
Result: Auto-fixes MyTest.java, builds, and pushes if all post-conditions met.

### Example 5: Manual review mode
```bash
/fix-intellij-diagnostics auto-fix=false
```
Result: Shows all issues and asks for user approval before any action.

## IMPORTANT NOTES

### File Activation Requirement

The JetBrains MCP server (port 64342) only returns diagnostics for the **currently active/focused file** in the IDE. If you experience timeouts:

1. Click on the target file tab in IntelliJ to make it active
2. Ensure the file has cursor focus
3. Then re-run the command

This is a limitation of the MCP server, not this command.

### Suppression Strategies

Different tools require different suppression syntax:

- **Sonar**: `//NOSONAR` or `@SuppressWarnings("sonar:S1234")`
- **Checkstyle**: `//CHECKSTYLE:OFF` ... `//CHECKSTYLE:ON`
- **PMD**: `@SuppressWarnings("PMD.RuleName")`
- **SpotBugs**: `@SuppressFBWarnings("RULE_NAME")`
- **IDE**: `//noinspection InspectionName`

Always include a comment explaining why suppression is necessary.

### Build Verification

The command uses the `maven-project-builder` agent which:
- Runs full Maven/Gradle build
- Executes all tests
- Checks quality gates (if configured)
- Includes pre-commit verification

This ensures fixes don't break the build.

### Continuous Improvement

This command implements a continuous improvement rule. When you discover:
- Better diagnostic retrieval techniques
- New categories of auto-fixable issues
- Improved suppression strategies
- Better IDE MCP server interaction patterns

**YOU MUST update this command file** with those improvements.

### Performance Considerations

- Initial diagnostic retrieval: ~2-5 seconds
- Per-fix analysis and application: ~1-3 seconds each
- Build verification: Varies by project (typically 30-120 seconds)
- Re-verification: ~2-5 seconds

For files with many diagnostics, expect several minutes for complete execution.
