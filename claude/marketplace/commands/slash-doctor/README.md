# slash-doctor

Analyzes and verifies slash commands for structural issues, semantic ambiguities, path portability, permission patterns, and anti-bloat compliance with automated fixes.

## Purpose

Automates slash command quality assurance by checking structure, detecting ambiguities/inconsistencies, finding hardcoded paths, verifying bash permissions, enforcing temp directory rules, and applying anti-bloat principles.

## Usage

```bash
# Interactive mode - select from menu
/slash-doctor

# Verify all project commands
/slash-doctor project

# Verify all global commands
/slash-doctor global

# Verify specific command
/slash-doctor verify-project
/slash-doctor docs-adoc
```

## What It Does

The command performs comprehensive slash command analysis across 8 steps per command:

1. **Structural Analysis** - Check for missing sections, parameter issues, workflow problems
2. **Deep Semantic Analysis** - Detect ambiguities, inconsistencies, completeness gaps
3. **Best Practices Compliance** - Verify tool usage order, error handling, statistics tracking
4. **Maven/Build Context** - Flag temp directory violations (/tmp → target/)
5. **Absolute Path Detection** - Find hardcoded paths (/Users/oliver → ~/)
6. **Permission Pattern Verification** - Extract bash commands, delegate to setup-project-permissions
7. **Issue Categorization** - Critical/Warnings/Suggestions with impact analysis
8. **Auto-Fix** - Apply fixes automatically or review individually

## Key Features

- **Structural Validation**: Required sections (title, description, parameters, workflow, critical rules)
- **Semantic Analysis**: Ambiguity detection (vague quantities, unclear conditions, missing cases)
- **Inconsistency Detection**: Contradictions, overlapping steps, conflicting instructions
- **Completeness Check**: All parameters handled, error conditions covered, decision points defined
- **Path Portability**: Converts user-absolute paths (/Users/oliver/) to user-relative (~/)
- **Temp Directory Enforcement**: Flags system temp usage (/tmp), requires project-local (target/)
- **Permission Verification**: Extracts bash commands, delegates to setup-project-permissions for approval
- **Anti-Bloat Enforcement**: Commands should shrink or stay same length after fixes
- **Auto-Fix Capability**: Automatic or manual review mode for applying fixes
- **Interactive Mode**: Menu-driven selection of commands to analyze

## Parameters

### project (Optional)
- **Format**: `project` (flag)
- **Description**: Review all commands in `.claude/commands/`
- **Use Case**: Verify project-specific slash commands

### global (Optional)
- **Format**: `global` (flag)
- **Description**: Review all commands in `~/.claude/commands/`
- **Excludes**: slash-doctor.md (this file) from analysis
- **Use Case**: Verify global/marketplace commands

### command-name (Optional)
- **Format**: `<command-name>`
- **Description**: Review specific command by name
- **Search**: Looks in both `.claude/commands/` and `~/.claude/commands/`
- **Examples**:
  - `verify-project`
  - `docs-adoc`
  - `handle-pull-request`

### No Parameters (Default)
- **Behavior**: Interactive mode with numbered menu
- **Options**: Select single command, project, global, all, or quit

## Structural Analysis

### Required Sections

**Must Have:**
- ✅ Title (# heading)
- ✅ Description (summary of command purpose)
- ✅ PARAMETERS (if command accepts parameters)
- ✅ PARAMETER VALIDATION (if parameters exist)
- ✅ WORKFLOW INSTRUCTIONS
- ✅ CRITICAL RULES or similar constraints section

### Parameter Issues

**Checks:**
- Each parameter documented with description
- Parameter validation logic present
- Clear handling of parameter combinations
- Examples showing parameter usage
- No duplicate parameter names

### Workflow Issues

**Checks:**
- Clear step-by-step instructions
- Steps numbered/ordered logically
- Decision points clearly marked
- Error handling described for each tool
- User prompts are consistent format
- Tool invocations use correct syntax

### Consistency Issues

**Checks:**
- User prompt formats (Y/N/S vs 1/2/3 - should be uniform)
- Tool names referenced correctly
- File paths are absolute where needed
- Commands use proper bash syntax
- No conflicting instructions

### Documentation Quality

**Checks:**
- Usage examples provided
- CRITICAL RULES section exists
- Clear success/failure criteria
- Integration with other commands explained
- Best practices documented

## Deep Semantic Analysis

### Ambiguity Detection

**What It Finds:**
- Multiple interpretations possible
- Unclear referents ("this", "it", "that" without clear antecedent)
- Vague quantities ("some", "many", "few", "several")
- Conditional logic with missing cases
- Steps that skip or jump without explanation

**Example:**
```
❌ Ambiguous: "Fix issues found"
✅ Clear: "Fix all linter issues by applying suggested corrections"
```

### Inconsistency Detection

**What It Finds:**
- Step A says do X, Step B says do Y (conflicting)
- Parameter descriptions don't match workflow usage
- Examples don't match documented behavior
- Tool paths differ across steps
- Cleanup happens in wrong order

**Example:**
```
❌ Inconsistent:
- Step 4.2: "Fix whitespace issues"
- Step 4.5: "Also fix whitespace issues"

✅ Consistent:
- Step 4.2: "Fix Linter-detected whitespace (structure only)"
- Step 4.5: "Fix CUI-specific issues (NOT whitespace)"
```

### Completeness Check

**What It Verifies:**
- All parameters have corresponding workflow logic
- All error conditions have handling instructions
- All user prompt options are documented
- All decision points have outcomes defined
- All tool invocations have error handling

### Best Practices Compliance

**Internal Workflow Checks:**
- Uses Read before Edit/Write (tool usage order)
- Cleans up artifacts immediately (no orphaned files)
- Uses proper git commit format (if command commits)
- Tracks statistics throughout (counters maintained)
- Provides clear user feedback (progress updates)
- Never leaves orphaned state (complete or rollback)

**Note**: Does NOT check if command includes permission verification or self-analysis - that's slash-doctor's job, not the command's.

## Maven/Build Context Compliance

### Temp Directory Violations

**Flags:**
- ❌ Uses system temp directories (`/tmp/`, `/private/tmp/`)
- ❌ Uses `mktemp` or `tempfile` commands
- ❌ Writes to home directory temp (`~/tmp/`)
- ✅ Uses project-local directories (`target/`, `build/`)

**Why Important:**
- In Maven/Gradle contexts, ALL temp files should go in project's `target/` or `build/` directory
- Ensures proper cleanup with `mvn clean`
- Keeps artifacts project-scoped
- Avoids cross-project contamination

**Example:**
```
❌ BAD: mktemp /tmp/analysis.txt
✅ GOOD: mkdir -p target/analysis && echo > target/analysis/results.txt
```

## Absolute Path Detection

### Path Portability Issues

**Searches for:**
- `/Users/oliver/` → Should be `~/`
- `/home/username/` → Should be `~/`
- Hardcoded user paths in:
  - Source references (Essential Rules, external files)
  - Script paths (bash commands)
  - File paths in workflow examples
  - Directory references

**Acceptable (No Change):**
- Paths in user-facing examples showing format (if clearly marked as example)
- Paths in comments explaining structure
- Generic paths like `/tmp/`, `/etc/`, `/usr/`

**Example:**
```
❌ CRITICAL: ~/git/cui-llm-rules/scripts/validator.sh
✅ FIXED: ~/git/cui-llm-rules/scripts/validator.sh
Impact: Not portable across users
```

## Permission Pattern Verification

### Simplified Workflow

**slash-doctor extracts bash commands, setup-project-permissions handles verification.**

### A. Extract Bash Commands

**From Command Workflow:**

1. **Script paths:**
   - `~/git/project/scripts/validator.sh` → `Bash(~/git/project/scripts/validator.sh:*)`
   - `python3 ~/git/project/scripts/verify.py` → `Bash(python3 ~/git/project/scripts/verify.py:*)`

2. **Commands:**
   - `grep` → `Bash(grep:*)`
   - `find` → `Bash(find:*)`
   - `wc` → `Bash(wc:*)`
   - `sed` → `Bash(sed:*)`

3. **Build tools:**
   - `mvn` → `Bash(mvn:*)`
   - `./mvnw` → `Bash(./mvnw:*)`
   - `npm` → `Bash(npm:*)`

4. **Git commands:**
   - `git` → `Bash(git:*)`

5. **Build comma-separated list:**
   ```
   required_permissions="Bash(grep:*),Bash(find:*),Bash(wc:*),Bash(~/git/project/scripts/validator.sh:*)"
   ```

### B. Delegate to setup-project-permissions

**Invoke:**
```bash
/setup-project-permissions ensurePermissions="$required_permissions"
```

**setup-project-permissions handles:**
- Checks global and local settings for each permission
- Reports globally approved (no local action needed)
- Reports locally approved (already configured)
- Detects missing permissions (not approved anywhere)
- Detects over-permissions (approved locally but not required)
- Calculates Permission Fit Score (0-100%)
- Offers to fix issues (add missing, remove over-permissions)
- Handles all user prompts and safety checks

### C. Permission Fit Score

**Rating Scale:**
- 100%: Perfect - All required approved, no over-permissions
- 80-99%: Excellent - All required approved, minor over-permissions
- 60-79%: Good - Most required approved, some missing/over
- 40-59%: Fair - Significant missing or over-permissions
- 0-39%: Poor - Major permission gaps

**Components:**
- **Missing Permissions**: Not approved globally or locally
- **Over-Permissions**: Approved locally but not required (SECURITY RISK)
- **Globally Approved**: Already available (no local action needed)
- **Locally Approved**: Correctly configured in project

### D. Benefits of Delegation

**No Code Duplication:**
- All permission logic in setup-project-permissions only
- Consistent behavior across slash-doctor, agents-doctor, direct usage

**Automatic Global/Local Handling:**
- setup-project-permissions understands global vs local architecture
- Decides placement automatically based on permission type
- Never duplicates global permissions in local settings

**Comprehensive Safety:**
- Duplicate detection
- Suspicious permission flagging
- Path normalization (user-absolute → user-relative)
- Global/local architecture enforcement
- Security risk assessment

## Issue Categorization

### CRITICAL (Must Fix)

**Structural:**
- Hardcoded absolute paths (not portable across users)
- Contradictions causing incorrect behavior
- Missing required sections
- Broken tool invocations
- Ambiguities that could lead to errors

**Environmental:**
- Over-permissions (security risk) → Dangerous commands auto-approved unnecessarily
- Missing bash command approvals → Command will prompt user frequently

### WARNINGS (Should Fix)

- Inconsistent formatting
- Missing best practices
- Incomplete documentation
- Unclear instructions that might confuse
- Missing error handling
- Stale permission patterns → Confusing, maintenance burden

### SUGGESTIONS (Nice to Have)

- Additional examples
- Performance optimizations
- Enhanced user feedback
- Integration opportunities

## Anti-Bloat Enforcement

### Core Principle

**Commands should SHRINK or stay SAME LENGTH after fixes. Never grow unless CRITICAL missing sections.**

### Preferred Fix Types (In Order)

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

### Measurement

**Track Before/After:**
```
Anti-Bloat Metrics:
- Total lines: <before> → <after> (<+/- count>)
- Section count: <before> → <after>
- Redundant sections removed: <count>
- Duplicate text eliminated: <count>

Target: Net reduction or neutral (0 to -10% ideal)
Warning: If >5% increase, review all additions
Error: If >10% increase, revert and retry
```

### The Bloat Test

**Before saving fixes, verify:**
1. **Is the command CLEARER?** (Yes required)
2. **Is the command SHORTER or SAME LENGTH?** (Prefer yes)
3. **Did I remove redundancy?** (Yes preferred)
4. **Did I add only what's CRITICAL?** (Yes required)
5. **Can a user execute this command more easily now?** (Yes required)

**If any answer is NO**: Review fixes and apply stricter editing.

## Auto-Fix Capability

### Decision Point

**If NO issues found:**
- Display: "✅ Command is well-formed and consistent - No issues found"
- Continue to next command

**If issues found:**
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

### Auto-Fix Mode (F)

**For absolute paths:**
- Replace all `/Users/oliver/` → `~/`
- Replace all `/home/username/` → `~/`

**For other issues:**
- Apply deterministic fixes automatically
- Skip issues needing user judgment
- Display fixes applied

### Review Mode (R)

**For each issue:**
```
Issue <number> of <total>:
Severity: <CRITICAL/WARNING/SUGGESTION>
Location: Line <N>-<M>
Problem: <description>

Current Code:
<show relevant lines with context>

Proposed Fix:
<describe the fix or show replacement>

Options:
Y - Apply this fix
N - Skip this issue
E - Edit fix (provide alternative)
Q - Stop reviewing

Please choose [Y/n/e/q]:
```

## Analysis Patterns

### Common Issues Detected

**Pattern 1: Inconsistent User Prompts**
- Problem: Multiple prompt formats in same command
- Example: `[Y/n]`, `[1/2/3]`, `[yes/no]` all used
- Fix: Standardize to single format (letter-based preferred)

**Pattern 2: Overlapping Steps**
- Problem: Multiple steps handle same responsibility
- Example: Step 4.2 fixes whitespace, Step 4.5 also fixes whitespace
- Fix: Clarify which step handles what, add explicit boundaries

**Pattern 3: Missing Decision Logic**
- Problem: Step presents options but doesn't define what happens next
- Example: "Fix these issues: ..." but no logic for post-fix flow
- Fix: Add explicit decision points with all outcomes defined

**Pattern 4: Ambiguous Tool Responsibilities**
- Problem: Unclear what tools can/cannot detect
- Example: "Manual review catches remaining issues" but no list
- Fix: Add explicit reference section listing tool limitations

**Pattern 5: Cleanup Confusion**
- Problem: Cleanup steps scattered throughout workflow
- Example: Cleanup in steps 2, 5, 7, and 9
- Fix: Clean immediately after each tool, verify at end

**Pattern 6: Missing Error Handling**
- Problem: No instructions for tool failures
- Example: "Run tool X" but nothing about what if tool fails
- Fix: Add error handling with user options for each tool

**Pattern 7: Incomplete Statistics**
- Problem: Counters missing or not updated
- Example: Track `issues_fixed` but not `files_skipped`
- Fix: Add all relevant counters and update throughout

**Pattern 8: Missing Configuration Persistence**
- Problem: User decisions not persisted across runs
- Example: User skips file but decision not saved
- Fix: Add .claude/run-configuration.md pattern for persistence

## Expected Duration

- **Single Command** (simple, < 500 lines): 30-60 seconds
  - Structural analysis: 10 sec
  - Semantic analysis: 15 sec
  - Path detection: 5 sec
  - Permission verification: 10 sec
  - Report generation: instant

- **Single Command** (complex, > 1000 lines): 1-3 minutes
  - Structural analysis: 30 sec
  - Semantic analysis: 60 sec
  - Path detection: 10 sec
  - Permission verification: 30 sec
  - Report generation: instant

- **All Project Commands** (3-5 commands): 2-5 minutes

- **All Global Commands** (10-15 commands): 5-15 minutes

## Integration

Use this command:
- After creating new slash commands
- After updating existing commands
- Before committing command changes
- As part of quality assurance workflow
- Periodically to maintain command quality
- When commands seem to behave inconsistently

Often used with:
- `/slash-create` - Create new commands
- `/setup-project-permissions` - Verify and fix bash permissions
- `/agents-doctor` - Verify agents (similar workflow)
- `/skill-doctor` - Verify skills (similar workflow)

## Example Output

```
==================================================
Analyzing: verify-project
Location: .claude/commands/verify-project.md
==================================================

Command Overview:
- Title: Maven Project Verification
- Length: 847 lines
- Sections: 7
- Complexity: High

Structural Analysis:
✅ All required sections present
✅ Parameters properly documented
✅ Workflow is well-structured
✅ Consistent user prompts
✅ Documentation is comprehensive

Deep Analysis:
✅ No ambiguous instructions
✅ No inconsistencies
✅ All parameters properly handled
✅ Statistics tracking is complete
✅ Error handling present

Absolute Path Analysis:
✅ No hardcoded absolute paths found
✅ All paths properly use ~/ or relative references

Build Context Compliance:
✅ No system temp directory usage (/tmp, /private/tmp)
✅ Command uses target/ for build artifacts

Permission Pattern Analysis:
Extracted bash commands: grep, find, wc, mvn, git
Invoking: /setup-project-permissions ensurePermissions="Bash(grep:*),Bash(find:*),Bash(wc:*),Bash(mvn:*),Bash(git:*)"

Permission Status Analysis for verify-project:

✅ GLOBALLY APPROVED (no local action needed):
- Bash(grep:*) - Available via global settings
- Bash(find:*) - Available via global settings
- Bash(wc:*) - Available via global settings
- Bash(mvn:*) - Available via global settings
- Bash(git:*) - Available via global settings

✅ LOCALLY APPROVED: None needed

❌ MISSING: None

⚠️  OVER-PERMISSIONS: None

Permission Fit Score: 100% (Perfect)

────────────────────────────────────────────────────

Issue Report for verify-project:

CRITICAL (0 issues):
None found

WARNINGS (0 issues):
None found

SUGGESTIONS (0 items):
None - command is optimally structured

Total: 0 issues found

────────────────────────────────────────────────────

Summary for verify-project:
- Initial issues: 0
- Issues fixed: 0
- Remaining issues: 0
- Status: ✅ Clean - Perfect structure and quality

**Quality Score: 100/100**

==================================================
Slash Command Doctor - Analysis Complete
==================================================

Commands Analyzed: 1
- With issues: 0
- Fixed: 0
- Still have issues: 0

Issue Statistics:
- Total issues found: 0
- Critical: 0
- Warnings: 0
- Suggestions: 0
- Issues fixed: 0

Build Context Compliance:
- Commands using system temp directories (/tmp): 0

Permission Pattern Analysis:
- Total permission issues found: 0
- Missing bash command approvals: 0
- Over-permissions (security risks): 0
- Commands with perfect permission fit (100%): 1
- Commands with permission issues: 0

Recommendations:
✅ All analyzed commands are well-formed and consistent!
```

## Notes

- **Meta-command**: Analyzes slash commands, not skill content
- **Delegates permission verification**: Uses setup-project-permissions for bash approval checks
- **Anti-bloat enforced**: Fixes should reduce or maintain command length
- **Interactive by default**: Always asks before making changes
- **Tracks statistics**: Maintains comprehensive counters throughout
- **Path portability critical**: Converts user-absolute to user-relative paths
- **Temp directory enforcement**: Maven/Gradle projects must use target/build, not /tmp
- **Permission Fit Score**: 0-100% rating from setup-project-permissions
- **Structural + Environmental**: Reports both command file issues and permission issues
- **Auto-verify**: Can re-analyze after fixes to ensure quality

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
