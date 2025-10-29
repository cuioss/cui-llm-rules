---
name: diagnose-commands
description: Analyze, verify, and fix slash commands for ambiguities, inconsistencies, and structural issues
---

# Slash Command Doctor - Verify and Fix Slash Commands

Analyze, verify, and fix slash commands for ambiguities, inconsistencies, and structural issues.

## PARAMETERS

- **project** (optional): Review all project-specific slash commands in `.claude/commands/`
- **global** (optional): Review all global slash commands in `~/.claude/commands/`
- **command-name** (optional): Review a specific command by name (e.g., `build-and-verify`)
- **No parameters**: Interactive mode - display menu of all commands and let user select

## PARAMETER VALIDATION

**If `project` parameter is provided:**
- Process all `.md` files in `.claude/commands/` directory
- Skip if directory doesn't exist (display message)

**If `global` parameter is provided:**
- Process all `.md` files in `~/.claude/commands/` directory
- Exclude `diagnose-commands.md` (this file) from analysis

**If specific command name is provided:**
- Look for command in both `.claude/commands/` and `~/.claude/commands/`
- Process the first match found
- Report error if command not found

**If no parameters provided:**
- Display interactive menu with numbered list of all commands
- Let user select which command(s) to review

## WORKFLOW INSTRUCTIONS

### Step 1: Determine Scope and Discover Commands

**A. Parse Parameters**

Determine what to process based on parameters:

1. If `project` → Set scope to `.claude/commands/`
2. If `global` → Set scope to `~/.claude/commands/`
3. If command name provided → Search both directories
4. If no parameters → Interactive mode

**B. Discover Commands**

Based on scope, find all slash command files:

```bash
# For project scope
find .claude/commands -name "*.md" -type f 2>/dev/null | sort

# For global scope
find ~/.claude/commands -name "*.md" -type f ! -name "diagnose-commands.md" | sort

# For specific command (search both)
find .claude/commands ~/.claude/commands -name "<command-name>.md" -type f 2>/dev/null | head -1
```

**C. Interactive Mode (if no parameters)**

Display menu:

```
Available Slash Commands:

PROJECT COMMANDS (.claude/commands/):
1. build-and-verify
2. verify-integration-tests
3. verify-micro-benchmark
...

GLOBAL COMMANDS (~/.claude/commands/):
10. docs-adoc
11. handle-pull-request
12. diagnose-commands
...

Options:
- Enter number to select single command
- Enter "project" to review all project commands
- Enter "global" to review all global commands
- Enter "all" to review everything
- Enter "quit" to exit

Your choice:
```

Wait for user input and set scope accordingly.

### Step 2: Initialize Analysis Statistics

Create tracking variables:
- `total_commands`: Total number of commands to analyze
- `commands_with_issues`: Number of commands with problems
- `commands_fixed`: Number of commands fixed
- `total_issues`: Total issues found across all commands
- `issues_fixed`: Total issues fixed
- `critical_issues`: Number of critical issues found
- `warnings`: Number of warnings found
- `temp_directory_violations`: Commands using /tmp instead of target/ (Step 3.4)
- `permission_issues`: Total permission pattern problems found (Step 3.6)
- `missing_approvals`: Count of commands needing approval
- `over_permissions`: Count of approved patterns not used by command
- `stale_patterns`: Count of outdated/redundant patterns

### Step 3: Analyze Each Command

For EACH command file, execute the following analysis:

#### Step 3.1: Display Command Header

```
==================================================
Analyzing: <command-name>
Location: <file-path>
==================================================
```

#### Step 3.2: Read and Parse Command

1. Read the entire command file
2. Parse structure:
   - Extract title (first heading)
   - Extract description (text after title)
   - Extract PARAMETERS section
   - Extract WORKFLOW INSTRUCTIONS section
   - Extract any other major sections

3. Count command length:
   - Total lines
   - Total sections
   - Complexity score (lines / 100 = complexity points)

Display:
```
Command Overview:
- Title: <title>
- Length: <lines> lines
- Sections: <count>
- Complexity: <Low/Medium/High>
```

#### Step 3.3: Perform Structural Analysis

Check for common structural issues:

**A. YAML Frontmatter Validation** (CRITICAL)

**REQUIRED**: Every command MUST have valid YAML frontmatter at the very beginning:

```yaml
---
name: command-name
description: Brief description
---
```

Check:
- ✅ Frontmatter exists at line 1
- ✅ Starts with `---` and ends with `---`
- ✅ Contains `name:` field matching filename (without .md extension)
- ✅ Contains `description:` field (max 100 characters recommended)
- ✅ Valid YAML syntax (no tabs, proper indentation)

**CRITICAL**: Without proper frontmatter, the command will NOT be discovered by Claude Code.

**B. Missing Critical Sections**

Required sections for well-formed commands:
- ✅ YAML Frontmatter (validated above)
- ✅ Title (# heading)
- ✅ Description (summary of what command does)
- ✅ PARAMETERS (if command accepts parameters)
- ✅ WORKFLOW INSTRUCTIONS or similar execution section

**C. Frontmatter-Filename Consistency**

Verify that:
- ✅ `name:` in frontmatter matches filename (without .md extension)
  - Example: `build-and-verify.md` → `name: build-and-verify`
- ✅ No mismatches that would prevent command discovery

**D. Parameter Issues**

If command has parameters:
- ✅ Each parameter documented
- ✅ Parameter validation logic present
- ✅ Clear handling of each parameter combination
- ✅ Examples showing parameter usage

**E. Workflow Issues**

Check workflow structure:
- ✅ Clear step-by-step instructions
- ✅ Steps are numbered/ordered
- ✅ Decision points clearly marked
- ✅ Error handling described
- ✅ User prompts are consistent
- ✅ Tool invocations use correct syntax

**F. Consistency Issues**

- ✅ User prompt formats (Y/N/S/P/Q vs inconsistent)
- ✅ Tool names referenced correctly
- ✅ File paths are absolute where needed
- ✅ Commands use proper bash syntax
- ✅ No conflicting instructions

**G. Documentation Quality**

- ✅ Examples provided
- ✅ CRITICAL RULES or similar section exists
- ✅ Clear success/failure criteria
- ✅ Integration with other commands explained

Display findings:
```
Structural Analysis:
❌ MISSING FRONTMATTER - Command will not be discovered!
✅ All required sections present
⚠️  Parameter validation could be clearer
✅ Workflow is well-structured
❌ User prompts use inconsistent format (Y/n vs 1/2/3)
✅ Documentation is comprehensive
```

#### Step 3.4: Perform Deep Semantic Analysis

**A. Ambiguity Detection**

Look for ambiguous instructions:
- Multiple interpretations possible
- Unclear referents ("this", "it", "that" without clear antecedent)
- Vague quantities ("some", "many", "few")
- Conditional logic with missing cases
- Steps that skip or jump without explanation

**B. Inconsistency Detection**

Look for contradictions:
- Step A says do X, Step B says do Y (conflicting)
- Parameter descriptions don't match workflow usage
- Examples don't match documented behavior
- Tool paths differ across steps
- Cleanup happens in wrong order

**C. Completeness Check**

Verify all cases are handled:
- All parameters have corresponding workflow logic
- All error conditions have handling instructions
- All user prompt options are documented
- All decision points have outcomes defined
- All tool invocations have error handling

**D. Best Practices Compliance**

**IMPORTANT**: Check the command's INTERNAL workflow practices, NOT whether it has meta-features like permission checking (that's Step 3.6's job).

Check against Claude Code workflow best practices:
- Uses Read before Edit/Write (tool usage order)
- Cleans up artifacts immediately (no orphaned files)
- Uses proper git commit format (if command commits)
- Tracks statistics throughout (counters maintained)
- Provides clear user feedback (progress updates)
- Never leaves orphaned state (complete or rollback)

**Note**: Do NOT check if command includes permission verification, self-analysis, or other meta-features. Those are diagnose-commands's responsibilities, not the command's.

**E. Maven/Build Context Best Practices**

Search command workflow for temp directory usage:
```bash
grep -E '/tmp/|/private/tmp/|mktemp|tempfile|~/tmp/' {command_file}
```

Check for violations:
- ❌ Uses system temp directories (`/tmp/`, `/private/tmp/`) - should use `target/` in Maven projects
- ❌ Uses `mktemp` or `tempfile` commands - should create directories in `target/`
- ❌ Writes to home directory temp (`~/tmp/`) - should use project `target/` directory
- ✅ Uses project-local directories (e.g., `target/`, `build/`) for temporary files

**Note**: In Maven/Gradle build contexts, ALL temporary files and build artifacts should go in the project's `target/` or `build/` directory, not system temp directories. This ensures proper cleanup with `mvn clean` and keeps artifacts project-scoped.

**Update Statistics**: If violations found, increment `temp_directory_violations`

Display findings:
```
Deep Analysis:
❌ CRITICAL: Step 4.2 and Step 4.5 both fix whitespace (ambiguous overlap)
⚠️  Step 4.4 mentions "fix issues" but no clear mechanism defined
✅ All parameters properly handled
❌ Three different user prompt formats used (inconsistent)
✅ Statistics tracking is complete
⚠️  Missing error handling for tool failures
```

#### Step 3.5: Detect Absolute Path Issues

**CRITICAL**: Scan for hardcoded absolute paths that should be user-relative.

**Search for absolute path patterns:**
```bash
# Search for common absolute path patterns
grep -n "~/" <command-file>
grep -n "/home/[^/]*/" <command-file>
```

**Categorize absolute paths:**

**CRITICAL - Must Replace:**
- `~/` → `~/`
- `/home/username/` → `~/`
- Hardcoded user paths in:
  - Source references (Essential Rules, external files)
  - Script paths (bash commands)
  - File paths in workflow examples
  - Directory references

**Acceptable - No Change:**
- Paths in user-facing examples showing format (if clearly marked as example)
- Paths in comments explaining structure
- Generic paths like `/tmp/`, `/etc/`, `/usr/`

**Count absolute path issues:**
- Store in `absolute_path_count`
- Track each occurrence: file, line number, path pattern

**Example findings:**
```
Absolute Path Issues (3 found):

Line 140: `~/git/cui-llm-rules/scripts/validator.sh`
  → Should be: `~/git/cui-llm-rules/scripts/validator.sh`
  Impact: Not portable across users

Line 245: Source: ~/git/cui-llm-rules/standards/logging.adoc
  → Should be: Source: ~/git/cui-llm-rules/standards/logging.adoc
  Impact: Essential Rules reference breaks for other users

Line 312: find ~/.claude/commands
  → Should be: find ~/.claude/commands
  Impact: Command won't work for other users
```

#### Step 3.6: Verify Permission Patterns

**Purpose**: Extract bash commands from command workflow and ensure they're approved via `/setup-project-permissions`.

**SIMPLIFIED WORKFLOW**: diagnose-commands just extracts, setup-project-permissions handles all the verification and fixing.

**A. Extract Bash Commands from Command Workflow**

Scan command file for bash command usage:

1. **Extract bash code blocks**:
   ```bash
   # Find all ```bash or ```sh blocks in command file
   grep -A 100 '```bash\|```sh' <command-file>
   ```

2. **Extract commands and convert to permission format**:

   **Script paths**:
   - `~/git/cui-llm-rules/scripts/validator.sh` → `Bash(~/git/cui-llm-rules/scripts/validator.sh:*)`
   - `python3 ~/git/cui-llm-rules/scripts/verify.py` → `Bash(python3 ~/git/cui-llm-rules/scripts/verify.py:*)`

   **Commands**:
   - `grep` → `Bash(grep:*)`
   - `find` → `Bash(find:*)`
   - `wc` → `Bash(wc:*)`
   - `sed` → `Bash(sed:*)`
   - `sort` → `Bash(sort:*)`

   **Build tools**:
   - `./mvnw` → `Bash(./mvnw:*)`
   - `npm` → `Bash(npm:*)`
   - `mvn` → `Bash(mvn:*)`

   **Git commands**:
   - `git` → `Bash(git:*)`

   **Control structures**:
   - `for` loops → `Bash(for:*)`
   - `while` loops → `Bash(while:*)`

3. **Build comma-separated list of required permissions**:
   ```
   required_permissions="Bash(grep:*),Bash(find:*),Bash(wc:*),Bash(~/git/cui-llm-rules/scripts/validator.sh:*)"
   ```

**B. Delegate to setup-project-permissions**

Invoke setup-project-permissions with ensurePermissions parameter:

```bash
/setup-project-permissions ensurePermissions="$required_permissions"
```

This triggers setup-project-permissions Step 3.5 which:
- Checks global and local settings for each required permission
- Reports globally approved (no local action needed)
- Reports locally approved (already configured)
- Detects missing permissions (not approved anywhere)
- Detects over-permissions (approved locally but not required)
- Calculates Permission Fit Score
- Offers to fix issues (add missing, remove over-permissions)
- Handles all user prompts and safety checks

**C. Display Results from setup-project-permissions**

setup-project-permissions returns a report like:

```
Permission Status Analysis for <command-name>:

✅ GLOBALLY APPROVED (no local action needed):
- Bash(grep:*) - Available via global settings
- Bash(find:*) - Available via global settings
- Bash(git:*) - Available via global settings

✅ LOCALLY APPROVED (already configured):
- Bash(~/git/cui-llm-rules/scripts/validator.sh:*)

❌ MISSING (needs approval):
- Bash(wc:*) - Not approved globally or locally

⚠️  OVER-PERMISSIONS (approved locally but not required):
- Bash(asciidoctor:*) - Command doesn't use this (SECURITY RISK)
- Bash(npm:*) - Command doesn't use this

Permission Fit Score: 67% (Fair fit)
- Will prompt for: wc
- Over-permissions: 2
- Security risks: 1 (asciidoctor)

Fix issues? [F/r/s]: <user response>

[If user fixes:]
✅ Permission Sync Complete:
- Added: 1 permission
- Removed: 2 over-permissions
- New Permission Fit Score: 100% (Perfect)
```

**D. Parse Results and Update Statistics**

Extract from setup-project-permissions report:
- Permission Fit Score: `<percentage>`
- Missing permissions count: `<count>`
- Over-permissions count: `<count>`

Update tracking:
```
permission_issues += (missing_count + over_permission_count)
missing_approvals += missing_count
over_permissions += over_permission_count
```

**E. Benefits of Delegation**

**No Code Duplication**:
- All permission logic in setup-project-permissions only
- Consistent behavior across diagnose-commands, diagnose-agents, and direct usage

**Automatic Global/Local Handling**:
- setup-project-permissions understands global vs local architecture
- Decides placement automatically based on permission type
- Never duplicates global permissions in local settings

**Comprehensive Safety Checks**:
- Duplicate detection
- Suspicious permission flagging
- Path normalization (user-absolute → user-relative)
- Global/local architecture enforcement
- Security risk assessment

**Consistent Reporting**:
- Same Permission Fit Score calculation everywhere
- Same categorization (globally approved, locally approved, missing, over-permissions)
- Same user prompts and fix options

**Easier Maintenance**:
- Update permission logic once in setup-project-permissions
- Automatically benefits all callers (diagnose-commands, diagnose-agents)
- No synchronization needed between commands

#### Step 3.7: Generate Issue Report

Categorize all issues found:

**NOTE**: Issues fall into two categories:
1. **STRUCTURAL** - Problems with the command file itself (ambiguity, contradictions, missing sections)
2. **ENVIRONMENTAL** - Problems with settings/approvals (from Step 3.6 permission analysis)

Both are reported together, but fixes differ: structural issues require editing the command, environmental issues require editing settings.

**CRITICAL Issues (Must Fix):**
- Hardcoded absolute paths (not portable across users)
- Structural problems preventing command execution
- Contradictions causing incorrect behavior
- Missing required sections
- Broken tool invocations
- Ambiguities that could lead to errors
- Over-permissions (security risk) → Dangerous commands auto-approved unnecessarily
- Missing bash command approvals → Command will prompt user frequently

**Warnings (Should Fix):**
- Inconsistent formatting
- Missing best practices
- Incomplete documentation
- Unclear instructions that might confuse
- Missing error handling
- Stale permission patterns → Confusing, maintenance burden

**Suggestions (Nice to Have):**
- Additional examples
- Performance optimizations
- Enhanced user feedback
- Integration opportunities

Display categorized report:
```
Issue Report for <command-name>:

CRITICAL (3 issues):
1. Line 177-193: Step 4.2 and 4.5 overlap - both fix whitespace
   Impact: Duplicate fixes, confusion about which step handles what
   Fix: Clarify Step 4.2 is "Linter fixes only", Step 4.5 is "CUI fixes only"

2. Line 680-708: Step 4.6 purpose unclear - fixes already handled in 4.4
   Impact: Redundant step, workflow confusion
   Fix: Convert to informational reference section

3. Line 235-260: Three different prompt formats (Y/N/S/A, F/S/P/Q, 1/2/3)
   Impact: Inconsistent user experience
   Fix: Standardize all to letter format

WARNINGS (4 issues):
...

SUGGESTIONS (2 items):
...

Total: 9 issues found
```

#### Step 3.8: Decision Point - Fix Issues?

**If NO issues found:**
- Display: "✅ Command is well-formed and consistent - No issues found"
- Continue to next command

**If issues found:**

Display:
```
Found <count> issues in <command-name>:
- Critical: <count>
- Warnings: <count>
- Suggestions: <count>

Options:
F - Fix all issues automatically
R - Review each issue individually before fixing
S - Skip this command (do not fix)
Q - Quit analysis entirely

Please choose [F/r/s/q]:
```

**If user responds:**
- `F` or `f` → Fix all issues automatically (Step 3.9)
- `R` or `r` → Review each issue individually (Step 3.10)
- `S` or `s` → Skip this command, move to next
- `Q` or `q` → Stop analysis, exit command

#### Step 3.9: Auto-Fix All Issues

**For absolute path issues:**
1. Use Edit tool to replace all occurrences of `~/` with `~/`
2. Use Edit tool to replace all occurrences of `/home/username/` patterns with `~/`
3. Display: "✅ Fixed: Replaced <count> absolute paths with user-relative paths"

**For other issues:**

For each issue, apply the fix automatically:

**For CRITICAL issues:**
1. Read the command file
2. Apply the specific fix (use Edit tool)
3. Update tracking: `critical_issues_fixed++`
4. Display: "✅ Fixed: <issue-summary>"

**For WARNINGS:**
1. Apply fixes when deterministic
2. Skip warnings that need user judgment
3. Update tracking: `warnings_fixed++`
4. Display: "✅ Fixed: <issue-summary>" or "⚠️ Skipped: <reason>"

**For SUGGESTIONS:**
- Skip suggestions in auto-fix mode
- Display: "ℹ️ Skipped <count> suggestions (auto-fix mode)"

After fixing:
```
Auto-Fix Complete:
- Critical issues fixed: <count>
- Warnings fixed: <count>
- Remaining issues: <count>
```

Continue to Step 3.11 (Verification)

#### Step 3.10: Review and Fix Individually

For EACH issue (in order: Critical → Warnings → Suggestions):

Display:
```
Issue <number> of <total>:
Severity: <CRITICAL/WARNING/SUGGESTION>
Location: Line <N>-<M>
Problem: <description>

Current Code:
<show relevant lines with context>

Proposed Fix:
<describe the fix or show the replacement>

Options:
Y - Apply this fix
N - Skip this issue
E - Edit fix (provide alternative)
Q - Stop reviewing, skip remaining issues

Please choose [Y/n/e/q]:
```

**If user responds:**
- `Y` or `y` → Apply the fix, continue to next issue
- `N` or `n` → Skip this issue, continue to next issue
- `E` or `e` → Ask for user's alternative fix, apply it, continue
- `Q` or `q` → Stop reviewing, move to Step 3.9

After review:
```
Review Complete:
- Issues fixed: <count>
- Issues skipped: <count>
- Remaining: <count>
```

Continue to Step 3.11 (Verification)

#### Step 3.11: Verify Fixes

If any fixes were applied:

1. Re-read the command file
2. Re-run analysis (Steps 3.3 and 3.4)
3. Compare before/after:
   ```
   Verification Results:
   - Issues before: <old_count>
   - Issues after: <new_count>
   - Issues fixed: <fixed_count>
   - New issues introduced: <new_count - (old_count - fixed_count)>
   ```

4. If new issues introduced:
   - Display: "⚠️ WARNING: Fixes introduced <count> new issues"
   - Offer to revert: "Revert changes? [y/N]:"

5. Update statistics:
   - `commands_fixed++`
   - `issues_fixed += <count>`

#### Step 3.12: Display Command Summary

```
Summary for <command-name>:
- Initial issues: <count>
- Issues fixed: <count>
- Remaining issues: <count>
- Status: ✅ Clean / ⚠️ Has warnings / ❌ Has critical issues
```

### Step 4: Generate Final Report

After processing all commands, display comprehensive summary:

```
==================================================
Slash Command Doctor - Analysis Complete
==================================================

Commands Analyzed: <total_commands>
- With issues: <commands_with_issues>
- Fixed: <commands_fixed>
- Still have issues: <remaining>

Issue Statistics:
- Total issues found: <total_issues>
- Critical: <critical_count>
- Warnings: <warning_count>
- Suggestions: <suggestion_count>
- Issues fixed: <issues_fixed>

Build Context Compliance:
- Commands using system temp directories (/tmp): <temp_directory_violations>
- Should use project target/ directory instead

Permission Pattern Analysis:
- Total permission issues found: <permission_issues>
- Missing bash command approvals: <missing_approvals>
- Over-permissions (security risks): <over_permissions>
- Stale/redundant patterns: <stale_patterns>
- Commands with perfect permission fit (100%): <count>
- Commands with permission issues: <count>

By Command:
<for each command with issues>
- <command-name>: <issue_count> issues (<critical>C / <warnings>W / <suggestions>S)
  Permission Fit: <percentage>% (<rating>)
  Permission Issues: <missing> missing, <over> over-permissions, <stale> stale
  Status: <Clean/Warnings/Critical>
</for each>

Recommendations:
<if critical issues remain>
⚠️  CRITICAL: <count> commands still have critical issues
- <command-1>: <issue>
- <command-2>: <issue>
Re-run diagnose-commands on these commands to fix.
</if>

<if all clean>
✅ All analyzed commands are well-formed and consistent!
</if>
```

## CRITICAL RULES

- **READ ENTIRE COMMAND** before analyzing - context is essential
- **CATEGORIZE ISSUES PROPERLY** - Critical vs Warning vs Suggestion
- **EXPLAIN FIXES CLEARLY** - User should understand why each change is made
- **VERIFY AFTER FIXING** - Always re-analyze to ensure fixes worked
- **PRESERVE INTENT** - Fix structure/consistency but preserve command's purpose
- **USE EDIT TOOL** - Never rewrite entire files, use targeted edits
- **TRACK STATISTICS** - Maintain counters throughout analysis
- **HANDLE ERRORS** - If command file is malformed/unreadable, report and skip
- **INTERACTIVE BY DEFAULT** - Ask before making changes unless told otherwise
- **LEARN FROM PATTERNS** - If multiple commands have same issue, mention it in report

## ANTI-BLOAT RULES

**CRITICAL: Prevent command bloat on every run**

The diagnose-commands command must IMPROVE commands without making them longer or more complex. Follow these strict rules:

### 1. Never Add, Only Fix

- **DO:** Fix existing content for clarity, consistency, correctness
- **DO NOT:** Add new sections, examples, or explanations unless CRITICAL
- **Exception:** Only add if something is fundamentally missing (e.g., no PARAMETERS section when command has parameters)

**Example:**
```markdown
BAD (adds bloat):
Original: "Run the linter"
Fixed: "Run the linter. The linter checks code quality and finds issues. It uses various rules to detect problems. Results are displayed in console format."

GOOD (clarifies without bloat):
Original: "Run the linter"
Fixed: "Run AsciiDoc Linter to check code quality"
```

### 2. Consolidate, Don't Duplicate

- **DO:** Merge redundant sections
- **DO NOT:** Add explanatory text that repeats existing content
- **If:** Two steps say the same thing → Merge or remove one

**Example:**
```markdown
BAD (duplicates):
Step 4.2: Fix whitespace issues
Step 4.5: Also fix whitespace issues
Fixed: Added note in both steps explaining whitespace handling

GOOD (consolidates):
Step 4.2: Fix whitespace issues (Linter only)
Step 4.5: Fix CUI-specific issues (NOT whitespace)
```

### 3. Clarify, Don't Expand

- **DO:** Make ambiguous text precise
- **DO NOT:** Turn short instructions into paragraphs
- **Target:** Reduce ambiguity with FEWER words when possible

**Example:**
```markdown
BAD (expands):
Original: "Clean up artifacts"
Fixed: "Clean up artifacts. This means removing all temporary files, intermediate outputs, HTML files generated during processing, backup files with .bak extension, and any other files that were created during the validation process."

GOOD (clarifies):
Original: "Clean up artifacts"
Fixed: "Remove .html, .bak, .tmp files immediately after each tool"
```

### 4. Remove, Don't Accumulate

When fixing issues:
- **DO:** Remove redundant text, unnecessary steps, obsolete notes
- **DO NOT:** Keep old content "just in case"
- **Philosophy:** Every word should earn its place

**Example:**
```markdown
BAD (accumulates):
Step 4.6: Manual Fix Guidance (DEPRECATED - now handled in Step 4.4)
[Keep entire section for reference]

GOOD (removes):
Step 4.6: Reference - Issues Tools Cannot Detect
[Convert to brief informational section, remove redundant fix instructions]
```

### 5. Structural Fixes Only

- **DO:** Fix step numbering, section organization, flow logic
- **DO NOT:** Add "helpful" comments, warnings, or reminders everywhere
- **Limit:** One CRITICAL/IMPORTANT note per major section maximum

**Example:**
```markdown
BAD (adds warnings everywhere):
Step 4.2: Run Linter
**IMPORTANT:** Make sure to run this step
**WARNING:** Do not skip this
**NOTE:** Results are displayed in console
[Original instructions...]

GOOD (minimal warnings):
Step 4.2: Run AsciiDoc Linter
**CRITICAL:** Use absolute path for tool invocation
[Original instructions...]
```

### 6. Efficiency Over Completeness

- **DO:** Trust the AI to understand context
- **DO NOT:** Over-specify every detail
- **Remember:** Claude can infer reasonable defaults

**Example:**
```markdown
BAD (over-specifies):
Display: "Processing file"
Display the file path relative to the project root, using forward slashes even on Windows, with proper escaping of special characters, truncating if longer than 80 characters...

GOOD (efficient):
Display: "Processing: <relative_file_path>"
```

### 7. Measure Impact

After fixing, command should be:
- **Shorter** or **same length** (never longer, except for critical missing sections)
- **Clearer** (reduced ambiguities)
- **More consistent** (unified style)
- **Less redundant** (no duplicate logic)

**Acceptable length changes:**
- Remove 50 lines, add 10 lines for clarity: ✅ Good (-40 net)
- Remove 10 lines, add 10 lines for consistency: ✅ Acceptable (0 net)
- Remove 0 lines, add 50 lines for "better documentation": ❌ Bad (+50 bloat)

### 8. Before/After Metrics

Track these metrics before and after fixes:

```
Anti-Bloat Metrics:
- Total lines: <before> → <after> (<+/- count>)
- Section count: <before> → <after>
- Average section length: <before> → <after>
- Redundant sections removed: <count>
- Duplicate text eliminated: <count>

Target: Net reduction or neutral (0 to -10% lines ideal)
Warning: If >5% increase, review all additions for necessity
Error: If >10% increase, revert and try again with stricter editing
```

### 9. Bloat Detection

If fixes increase file size significantly, analyze why:

```
Bloat Analysis:
- Added sections: <list>
- Added examples: <list>
- Added warnings/notes: <count>
- Expanded explanations: <list>

For each addition, justify:
- Is this CRITICAL? (missing parameter validation, broken workflow)
- Can it be shorter? (use fewer words)
- Can it be merged? (combine with existing section)
- Can it be removed? (command works without it)
```

### 10. The Bloat Test

Before saving fixes, ask:

1. **Is the command CLEARER?** (Yes required)
2. **Is the command SHORTER or SAME LENGTH?** (Prefer yes)
3. **Did I remove redundancy?** (Yes preferred)
4. **Did I add only what's CRITICAL?** (Yes required)
5. **Can a user execute this command more easily now?** (Yes required)

**If any answer is NO**: Review fixes and apply stricter editing.

## FIXING STRATEGY TO AVOID BLOAT

### Preferred Fix Types (In Order):

1. **Delete/Merge** (Best - reduces size)
   - Remove duplicate sections
   - Merge redundant steps
   - Delete obsolete notes

2. **Reword** (Good - same size or smaller)
   - Change ambiguous text to precise text
   - Shorten verbose explanations
   - Simplify complex sentences

3. **Reorganize** (Neutral - same size)
   - Fix step numbering
   - Move sections to better locations
   - Improve flow

4. **Add Minimally** (Use sparingly - increases size)
   - Only when something critical is missing
   - Keep additions under 10 lines
   - Ensure no other way to fix

### Examples of Good vs Bad Fixes:

**Issue: Inconsistent user prompts**

❌ BAD Fix (adds bloat):
```markdown
Add new section "User Prompt Standards":
"All user prompts in this command should follow a consistent format.
We use letter-based options for consistency with other commands.
The format is [Y/n/s/p] where uppercase is default.
When prompting users, always use this format..."
[100 lines of explanation]

Then: Update each prompt to match.
```

✅ GOOD Fix (consolidates):
```markdown
Edit each prompt from:
"Options: 1-Yes, 2-No, 3-Skip"
To:
"Please choose [Y/n/s]:"

No additional explanation needed - pattern is self-evident.
```

**Issue: Overlapping step responsibilities**

❌ BAD Fix (expands both):
```markdown
Step 4.2: Add note "This step handles Linter fixes ONLY, not CUI fixes.
CUI fixes are in Step 4.5. Do not confuse these. Linter fixes include..."
[50 lines explaining boundary]

Step 4.5: Add note "This step handles CUI fixes ONLY, not Linter fixes.
Linter fixes are in Step 4.2. Do not confuse these. CUI fixes include..."
[50 lines explaining boundary]
```

✅ GOOD Fix (clarifies titles):
```markdown
Step 4.2: Run AsciiDoc Linter (Structure Fixes Only)
Step 4.5: Apply CUI Automated Fixes (CUI-Specific Only)

Add one line in each:
4.2: "**IMPORTANT:** These are AsciiDoc structure fixes only. CUI-specific issues handled in Step 4.5."
4.5: "**IMPORTANT:** This handles CUI-specific issues only. Linter fixes already applied in Step 4.2."
```

## ENFORCEMENT

When analyzing commands, **actively look for opportunities to reduce length**:

- ✅ Found redundant section → Remove it
- ✅ Found verbose explanation → Shorten it
- ✅ Found duplicate logic → Merge it
- ✅ Found obsolete note → Delete it

**Report in final summary:**
```
Anti-Bloat Results:
✅ Reduced command length by 150 lines (10% reduction)
✅ Removed 3 redundant sections
✅ Shortened 12 verbose explanations
✅ Merged 2 duplicate steps
⚠️ Added 20 lines for critical missing error handling
Net change: -130 lines (8% reduction)
```

This keeps commands tight, focused, and maintainable over time.

## ANALYSIS PATTERNS

Common issues to look for across all commands:

### Pattern 1: Inconsistent User Prompts

**Problem:** Multiple prompt formats in same command
**Example:** `[Y/n]`, `[1/2/3]`, `[yes/no]` all used
**Fix:** Standardize to single format (letter-based preferred)

### Pattern 2: Overlapping Steps

**Problem:** Multiple steps handle same responsibility
**Example:** Step 4.2 fixes whitespace, Step 4.5 also fixes whitespace
**Fix:** Clarify which step handles what, add explicit boundaries

### Pattern 3: Missing Decision Logic

**Problem:** Step presents options but doesn't define what happens next
**Example:** "Fix these issues: ..." but no logic for post-fix flow
**Fix:** Add explicit decision points with all outcomes defined

### Pattern 4: Ambiguous Tool Responsibilities

**Problem:** Unclear what tools can/cannot detect
**Example:** "Manual review catches remaining issues" but no list of what to check
**Fix:** Add explicit reference section listing tool limitations

### Pattern 5: Cleanup Confusion

**Problem:** Cleanup steps scattered throughout workflow
**Example:** Cleanup in steps 2, 5, 7, and 9
**Fix:** Clean immediately after each tool, verify at end

### Pattern 6: Missing Error Handling

**Problem:** No instructions for tool failures
**Example:** "Run tool X" but nothing about what if tool fails
**Fix:** Add error handling with user options for each tool

### Pattern 7: Incomplete Statistics

**Problem:** Counters missing or not updated
**Example:** Track `issues_fixed` but not `files_skipped`
**Fix:** Add all relevant counters and update throughout

### Pattern 8: Missing Configuration Persistence

**Problem:** User decisions not persisted across runs
**Example:** User skips file but decision not saved
**Fix:** Add .claude/run-configuration.md pattern for persistence

### Pattern 9: Unclear Step Purpose

**Problem:** Step exists but its role in workflow is unclear
**Example:** Step 4.6 provides guidance but Step 4.4 already handles fixes
**Fix:** Clarify as informational reference or merge with related step

### Pattern 10: Parameter Validation Gap

**Problem:** Parameters documented but validation logic missing
**Example:** "file=<path>" parameter but no check if file exists
**Fix:** Add explicit validation section with error handling

## BEST PRACTICES FOR WELL-FORMED COMMANDS

A well-formed slash command should have:

1. **Clear Title and Description** - User knows exactly what command does
2. **Documented Parameters** - All parameters explained with examples
3. **Parameter Validation** - Check all inputs before processing
4. **Structured Workflow** - Numbered steps in logical order
5. **Decision Points** - All conditional logic clearly defined
6. **Error Handling** - What to do when tools fail
7. **User Feedback** - Progress updates and clear messages
8. **Statistics Tracking** - Counters for all important metrics
9. **Cleanup Instructions** - Artifacts removed immediately
10. **Examples** - Show how to use the command
11. **Critical Rules** - Important constraints highlighted
12. **Verification** - Check that work was successful
13. **Consistent Style** - Formatting, prompts, terminology uniform
14. **Integration Notes** - How command relates to others
15. **Performance Expectations** - How long command takes to run

## USAGE EXAMPLES

### Analyze All Project Commands
```
/diagnose-commands project
```

### Analyze All Global Commands
```
/diagnose-commands global
```

### Analyze Specific Command
```
/diagnose-commands docs-adoc
/diagnose-commands build-and-verify
```

### Interactive Mode
```
/diagnose-commands
[Select from menu]
```

### Review Multiple Commands
```
/diagnose-commands project
[Fix all automatically]
```

## ERROR HANDLING

**If command file not found:**
```
❌ ERROR: Command '<name>' not found
Searched in:
- .claude/commands/
- ~/.claude/commands/

Available commands: <list>
```

**If command file is malformed:**
```
⚠️ WARNING: Command '<name>' could not be parsed
Error: <description>

Options:
V - View file contents
S - Skip this command
Q - Quit analysis

Please choose [V/s/q]:
```

**If fixes introduce errors:**
```
⚠️ WARNING: Fixes to '<name>' introduced new issues:
- <issue 1>
- <issue 2>

Options:
R - Revert all changes
K - Keep changes anyway
M - Manually review and fix

Please choose [R/k/m]:
```

## INTEGRATION WITH OTHER COMMANDS

This command helps maintain quality of:
- `/build-and-verify` - Ensures CI/CD verification command is correct
- `/docs-adoc` - Keeps documentation review command accurate
- All custom slash commands - Maintains consistency

Run `diagnose-commands` periodically to:
- After creating new commands
- After major updates to existing commands
- When commands seem to behave inconsistently
- As part of project maintenance

## NOTES

- This command analyzes command STRUCTURE and CONSISTENCY
- It does NOT test command FUNCTIONALITY
- For functionality testing, actually run the command
- Slash-doctor focuses on: clarity, consistency, completeness
- Always backup important commands before fixing
- Git tracks command files, so changes can be reverted
