# fix-ide-diagnostics

Retrieves IDE diagnostics via JetBrains MCP server, analyzes issues intelligently, and applies safe fixes automatically. Uses suppression only as a last resort.

## Purpose

Integrates with JetBrains IDE (IntelliJ, WebStorm, etc.) to retrieve compiler errors, warnings, and inspections for the current file, then systematically fixes auto-fixable issues, requests user approval for complex changes, and suppresses only when no reasonable fix exists.

## Usage

```bash
# Fix diagnostics in currently active IDE file
/fix-ide-diagnostics

# Fix specific file without auto-fix (prompt for each change)
/fix-ide-diagnostics file=src/main/java/MyClass.java auto-fix=false

# Fix current file, build, commit, and push if successful
/fix-ide-diagnostics push

# Fix specific file and push
/fix-ide-diagnostics file=src/test/java/MyTest.java auto-fix=true push
```

## What It Does

The command performs intelligent diagnostic fixing:

1. **Retrieves IDE diagnostics** via JetBrains MCP server (port 64342)
2. **Analyzes each issue** to determine best approach:
   - **Category A**: 100% certain fix (auto-apply)
   - **Category B**: Needs user judgment (prompt for approval)
   - **Category C**: No reasonable fix (suppress with justification)
3. **Applies fixes** using Edit tool
4. **Re-verifies** diagnostics to ensure no new issues introduced
5. **Builds project** using project-builder agent
6. **Commits and pushes** (if requested and all post-conditions met)

## Key Features

- **Intelligent Categorization**: Distinguishes between safe auto-fixes and changes requiring user approval
- **Suppression as Last Resort**: Only suppresses when no reasonable fix exists, with full justification
- **Loop Detection**: Prevents infinite fix-verify-refix cycles (max 3 iterations)
- **Build Verification**: Ensures fixes don't break compilation or tests
- **Multiple File Modes**: Works with currently active IDE file or specified file path
- **Auto-fix Control**: Toggle between fully automatic and manual approval mode
- **Comprehensive Reporting**: Detailed summary of all fixes, suppressions, and remaining issues

## Parameters

### Standard Parameters

- **push**: Auto-commit and push changes if all post-conditions met
  - Requires: Build success, no new errors, at least one fix applied

### Custom Parameters

- **file=\<path\>**: Target file path (absolute or relative to project root)
  - Default: Currently active file in IDE
  - Example: `file=src/main/java/MyClass.java`

- **auto-fix=\<boolean\>**: Auto-apply certain fixes vs. prompt for all
  - Default: `true`
  - `true`: Auto-apply Category A (100% certain) fixes, prompt for Category B
  - `false`: Prompt for user approval before ANY change
  - Example: `auto-fix=false`

## Pre-Conditions

The command verifies before execution:
- JetBrains IDE running with MCP server enabled (port 64342)
- Target file exists in project (if file parameter provided)
- IDE has an active file open (if no file parameter provided)
- User has write permissions to modify files
- Project has build configuration (pom.xml, build.gradle, etc.)

## Workflow Overview

1. **Retrieve Diagnostics**: Call MCP `get_file_problems` for target file
2. **Analyze Issues**: Categorize each diagnostic (A: auto-fix, B: user approval, C: suppress)
3. **Apply Fixes**: Execute based on auto-fix setting and issue category
4. **Track Changes**: Log all fixes, suppressions, and skipped issues
5. **Re-verify**: Check diagnostics again to detect new issues from fixes
6. **Build Project**: Run full build with tests via project-builder agent
7. **Report Results**: Comprehensive summary with metrics and recommendations
8. **Commit & Push**: If requested and post-conditions satisfied

## Issue Categories

### Category A: Auto-Fixable (100% Certain)
- Unused imports
- Missing @Override annotations
- Simple type errors
- Formatting issues
- Deprecated API usage with clear replacement

### Category B: Manual Review Needed
- Null-safety issues requiring business logic understanding
- Complex refactoring with multiple approaches
- Architectural decisions
- Performance optimizations
- API design changes

### Category C: Suppress Candidates (Last Resort)
- False positives from static analysis tools
- Intentional patterns flagged incorrectly
- External library issues beyond control
- Platform-specific workarounds

## Suppression Strategies

Different tools use different syntax:

- **Sonar**: `//NOSONAR` or `@SuppressWarnings("sonar:S1234")`
- **Checkstyle**: `//CHECKSTYLE:OFF` ... `//CHECKSTYLE:ON`
- **PMD**: `@SuppressWarnings("PMD.RuleName")`
- **SpotBugs**: `@SuppressFBWarnings("RULE_NAME")`
- **IDE**: `//noinspection InspectionName`

All suppressions include justification comments explaining why no fix is available.

## Post-Conditions

After successful execution:
- All auto-fixable diagnostics resolved
- Remaining issues either suppressed (with justification) or flagged for manual review
- Project builds successfully with all tests passing
- No new errors or warnings introduced by fixes
- If push used: Changes committed and pushed to remote
- User informed of all changes and remaining work

## File Activation Requirement

**IMPORTANT**: The JetBrains MCP server only returns diagnostics for the **currently active/focused file** in the IDE.

If you encounter timeouts:
1. Click on the target file tab in IntelliJ to make it active
2. Ensure the file has cursor focus
3. Re-run the command

This is a limitation of the MCP server architecture.

## Build Verification

The command uses the `project-builder` agent to:
- Run full Maven/Gradle build
- Execute all tests
- Check quality gates (Sonar, Checkstyle, etc.)
- Include pre-commit verification

This ensures diagnostic fixes don't introduce build failures.

## Loop Protection

The command prevents infinite fix-verify cycles:
- Maximum 3 iterations of fix → verify → refix
- Tracks changes between iterations
- If stuck in loop, reports status and stops

## Expected Performance

- Diagnostic retrieval: ~2-5 seconds
- Per-fix analysis and application: ~1-3 seconds each
- Build verification: 30-120 seconds (varies by project)
- Re-verification: ~2-5 seconds

For files with many diagnostics, expect several minutes for complete execution.

## Integration

Use this command:
- Before committing changes (catch issues early)
- After major refactoring (verify no new issues)
- As part of pre-PR checklist
- When IDE shows many warnings/errors

Often used with:
- `/project-builder` - Verify full build after fixes
- `/commit-current-changes` - Commit diagnostic fixes
- `/handle-pull-request` - Include in PR workflow

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║          IDE Diagnostics Fix Report                        ║
╔════════════════════════════════════════════════════════════╝

File: src/main/java/MyClass.java

Original Diagnostics:
  - Errors: 5
  - Warnings: 12
  - Total: 17

Actions Taken:
  ✓ Fixes Applied: 14
    - Line 45: Removed unused import
    - Line 67: Added missing @Override
    - Line 102: Fixed type mismatch
    ...

  ⚠ Suppressions Added: 2
    - Line 234: Sonar S3776 (Cognitive Complexity)
      Reason: Business logic complexity inherent to domain
    - Line 456: Sonar S1135 (TODO tag)
      Reason: Intentional tracking of future enhancement

  ⏭ Skipped for Manual Review: 1
    - Line 123: Null-safety issue requires business logic review

Build Verification:
  ✓ Build Status: Success
  ✓ Tests: 45 passed, 0 failed
  ✓ Quality Gates: Passed

Diagnostic Re-check:
  - Remaining Errors: 0
  - Remaining Warnings: 1 (flagged for manual review)

Post-Conditions Status:
  ✓ All auto-fixable issues resolved
  ✓ Project builds successfully
  ✓ No new errors introduced
  ✓ All changes justified and documented
```

## Notes

- **Requires JetBrains IDE with MCP**: This command specifically uses the JetBrains MCP server
- **File Must Be Active**: The IDE must have the target file as the active/focused tab
- **Suppression is Last Resort**: Command always attempts to fix before suppressing
- **Build Verification Critical**: Never push if build fails
- **Loop Detection**: Prevents runaway fix attempts
- **User Control**: auto-fix parameter gives fine-grained control

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
