---
name: java-fix-javadoc
description: Fix Javadoc errors and warnings from Maven builds with content preservation
---

# CUI Javadoc Fix Command

Systematically identifies and fixes Javadoc errors and warnings from Maven builds while preserving all documentation content.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-java-fix-javadoc update="[your improvement]"` with:
1. Improved error detection and categorization patterns
2. Better fix strategies that preserve content
3. More efficient verification workflows
4. Enhanced error pattern matching
5. Any lessons learned about Javadoc error resolution

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **module** - Module name for single module (optional, processes all if not specified)
- **verify-only** - Only verify and report errors without fixing (optional, default: false)

## CRITICAL CONSTRAINTS

### Content Preservation Rules

**MUST:**
- Fix ONLY Javadoc errors and warnings from build
- Make minimal modifications necessary
- Focus exclusively on formatting, references, and tags
- Preserve all existing documentation content

**MUST NOT:**
- Alter or improve documentation content
- Modify any code
- Rewrite documentation for style
- Make changes beyond error fixes

### Scope

**In Scope:**
- Fix invalid `{@link}` references
- Fix malformed HTML tags
- Fix missing/incorrect parameter documentation tags
- Fix missing/incorrect return value documentation tags
- Fix missing/incorrect exception documentation tags
- Fix tag ordering issues
- Fix unclosed HTML elements

**Out of Scope:**
- Documentation content improvements
- Code changes
- Content rewrites
- Style changes beyond error resolution

## WORKFLOW

### Step 0: Parameter Validation

**Validate parameters:**
- If `module` specified: verify module exists
- Set `verify-only` mode if requested
- Determine processing scope (single module vs all)

### Step 1: Load Javadoc Standards

```
Skill: cui-javadoc
```

This loads comprehensive Javadoc standards including:
- Core Javadoc principles
- Class and method documentation standards
- Error reference guide (javadoc-error-reference.md)

**On load failure:**
- Report error
- Cannot proceed without standards reference
- Abort command

### Step 2: Build Verification and Error Detection

**2.1 Run Maven Build with Javadoc:**

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: -Ppre-commit clean verify -DskipTests
  module: {module if specified}
  output_mode: structured
```

**On build failure (non-Javadoc):**
- Report non-Javadoc build errors
- Prompt user: "[F]ix build first / [A]bort"
- Cannot proceed until build passes (except for Javadoc errors)

**2.2 Extract and Categorize Javadoc Errors:**

Parse build output to identify Javadoc issues by category:

1. **Missing Tags:**
   - Missing `@param` tags
   - Missing `@return` tags
   - Missing `@throws` tags
   - Empty tag descriptions

2. **Invalid References:**
   - Invalid `{@link}` references
   - References to non-existent classes/methods
   - Malformed link syntax

3. **HTML Formatting:**
   - Unclosed HTML tags
   - Malformed HTML elements
   - Improper tag nesting
   - Bad HTML entities

4. **Tag Ordering:**
   - Tags in wrong order
   - Non-standard tag sequence

5. **Other Issues:**
   - Unknown tags
   - Malformed tags
   - Empty documentation blocks

**Store categorized errors** with:
- File path
- Line number
- Error type
- Error message
- Context (class/method name)

**2.3 Display Error Summary:**

```
╔════════════════════════════════════════════════════════════╗
║          Javadoc Error Analysis                            ║
╚════════════════════════════════════════════════════════════╝

Errors Found: {total_errors}

By Category:
- Missing Tags: {missing_tags_count}
- Invalid References: {invalid_refs_count}
- HTML Formatting: {html_issues_count}
- Tag Ordering: {ordering_issues_count}
- Other Issues: {other_count}

By Module:
- {module1}: {count1} errors
- {module2}: {count2} errors
...

Most Common Issues:
1. {most_common_issue} ({count} occurrences)
2. {second_issue} ({count} occurrences)
3. {third_issue} ({count} occurrences)
```

**If verify-only mode:**
- Display detailed error list
- Exit with error summary
- Return without fixing

**If no errors found:**
- Display success message
- Exit successfully

**If errors found and not verify-only:**
- Prompt user: "[P]roceed with fixes / [V]iew details / [A]bort"

### Step 3: Documentation Analysis

For each error, analyze context to plan minimal fix:

**3.1 Analyze Error Context:**

```
Task:
  subagent_type: Explore
  model: sonnet
  description: Analyze Javadoc error contexts
  prompt: |
    Analyze the context for each Javadoc error to determine minimal fix.

    Errors to analyze: {categorized_errors}

    For each error:
    1. Read the file and locate the error
    2. Analyze surrounding documentation
    3. Determine minimal fix required (preserve content)
    4. Identify any dependencies or related errors

    Return structured analysis with fix recommendations.
```

**3.2 Plan Fixes:**

Group errors by fix strategy:
- **Simple Additions:** Add missing tags with minimal descriptions
- **Reference Fixes:** Update or remove invalid references
- **HTML Fixes:** Close tags, fix nesting, escape entities
- **Reordering:** Reorder tags to standard sequence
- **Content-Neutral:** Fixes that require no content interpretation

**3.3 Identify Complex Cases:**

Flag errors requiring user guidance:
- Ambiguous parameter descriptions needed
- Unknown replacement for invalid references
- Unclear return value descriptions
- Exception conditions not apparent from code

**Prompt user for complex cases:**
- Display error context
- Request guidance for fix
- Continue with simple fixes while waiting

### Step 4: Apply Fixes

Apply fixes systematically by category:

**4.1 Apply Simple Fixes First:**

For each simple, content-neutral fix:

```
SlashCommand: /cui-java-expert:java-implement-code task="Apply Javadoc fix:
    Apply minimal Javadoc fix to resolve error.

    Error Details:
    - File: {file_path}
    - Line: {line_number}
    - Type: {error_type}
    - Message: {error_message}
    - Fix: {planned_fix}

    CRITICAL CONSTRAINTS:
    - Make MINIMAL changes only
    - DO NOT alter documentation content
    - DO NOT modify code
    - Focus ONLY on fixing the specific error
    - Preserve existing formatting and style

    Apply the fix and return status.
```

Track in `fixes_applied` counter.

**On implementation error:**
- Log error details
- Track in `fixes_failed` counter
- Continue with other fixes
- Prompt user: "[S]kip / [R]etry / [A]bort"

**4.2 Verify Each Fix:**

After each fix:
- Read modified file
- Verify no content loss
- Verify error addressed
- Check no new errors introduced

**4.3 Batch Verification:**

After batch of fixes (every 10 fixes or per file):

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: javadoc:javadoc
  module: {module if specified}
  output_mode: errors
```

Check if errors resolved without introducing new ones.

**If new errors introduced:**
- Rollback recent fixes
- Analyze what went wrong
- Adjust fix strategy
- Retry with corrected approach

### Step 5: Final Verification

**5.1 Complete Build Verification:**

```
Skill: cui-maven:cui-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: -Ppre-commit clean verify -DskipTests
  module: {module if specified}
  output_mode: errors
```

**On remaining errors:**
- Display remaining error list
- Analyze why not fixed
- Track in `unfixed_errors` counter
- Prompt user: "[R]etry fixes / [M]anual fix needed / [A]ccept partial fix"

**5.2 Content Verification:**

Sample check of fixed files:
- Verify documentation content unchanged
- Verify only formatting/tags/references changed
- Verify no code modifications

**5.3 Diff Review:**

```
Bash: git diff {module paths if specified, otherwise all}
```

Display changes and prompt user to review:
- Verify changes are minimal
- Verify no content alterations
- Verify only error fixes applied

**User confirmation required:**
- "[A]ccept changes / [R]eject and rollback / [V]iew specific file"

### Step 6: Commit Changes

If user accepts changes:

```
Bash: git add {affected files}
Bash: git commit -m "$(cat <<'EOF'
docs: fix Javadoc errors in {module or 'all modules'}

Fixed {total_errors} Javadoc errors:
- {category1}: {count1} fixes
- {category2}: {count2} fixes
...

Changes are content-preserving and address only build errors.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 7: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║          Javadoc Fix Summary                               ║
╚════════════════════════════════════════════════════════════╝

Scope: {module or 'all modules'}

Errors Found: {total_errors}
Fixes Applied: {fixes_applied}
Fixes Failed: {fixes_failed}
Unfixed Errors: {unfixed_errors}

By Category:
- Missing Tags: {missing_tags_fixed} / {missing_tags_total}
- Invalid References: {refs_fixed} / {refs_total}
- HTML Formatting: {html_fixed} / {html_total}
- Tag Ordering: {order_fixed} / {order_total}
- Other Issues: {other_fixed} / {other_total}

Files Modified: {files_modified}
Content Preservation: ✅ Verified
Build Status: {SUCCESS/PARTIAL/FAILURE}

Time Taken: {elapsed_time}
```

## STATISTICS TRACKING

Track throughout workflow:
- `total_errors`: Total Javadoc errors found
- `fixes_applied`: Individual fixes successfully applied
- `fixes_failed`: Individual fixes that failed
- `unfixed_errors`: Errors remaining after all attempts
- `files_modified`: Number of files changed
- `missing_tags_count`: Count by category
- `invalid_refs_count`: Count by category
- `html_issues_count`: Count by category
- `ordering_issues_count`: Count by category
- `elapsed_time`: Total execution time

Display all statistics in final summary.

## ERROR CATEGORIES AND FIX STRATEGIES

For comprehensive error detection patterns and fix strategies, refer to:

```
Read: marketplace/bundles/cui-java-expert/skills/cui-javadoc/standards/javadoc-error-reference.md
```

This reference covers all common Javadoc errors including:
- Missing parameter/return/exception documentation
- Invalid references and malformed tags
- HTML formatting issues and code blocks
- Tag ordering problems
- Empty documentation blocks

All fix strategies follow content-preservation rules and minimal modification approach.

## ERROR HANDLING

**Build Failures (non-Javadoc):**
- Display error details
- Require build fix before proceeding
- Cannot fix Javadoc if code doesn't compile

**Implementation Errors:**
- Log specific error that failed
- Skip individual errors on user request
- Continue with other errors
- Report failures in summary

**Rollback on New Errors:**
- Detect if fixes introduce new errors
- Rollback affected changes
- Analyze and adjust strategy
- Retry with corrected approach

**Partial Success:**
- Accept partial fixes if user approves
- Document unfixed errors
- Provide guidance for manual resolution

## USAGE EXAMPLES

**Fix all Javadoc errors:**
```
/java-fix-javadoc
```

**Fix single module:**
```
/java-fix-javadoc module=auth-service
```

**Verify only (no fixes):**
```
/java-fix-javadoc verify-only
```

**Verify specific module:**
```
/java-fix-javadoc module=user-api verify-only
```

## ARCHITECTURE

Orchestrates skill workflows and commands:
- **cui-javadoc skill** - Standards and error reference
- **Bash** - Maven build execution
- **cui-maven:cui-maven-rules skill** - Build output parsing
- **Explore agent** - Error context analysis
- **/cui-java-implement-code command** - Apply Javadoc fixes (Layer 2)

## RELATED

- `cui-javadoc` skill - Javadoc standards and error reference
- `cui-maven:cui-maven-rules` skill - Maven standards and output parsing
- `/java-implement-code` command - Code modifications
- `/java-refactor-code` command - Broader code refactoring
