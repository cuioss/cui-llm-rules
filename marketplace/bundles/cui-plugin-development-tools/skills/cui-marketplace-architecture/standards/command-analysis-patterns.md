# Command Analysis Patterns

Common issues and patterns to detect when analyzing slash commands.

## Pattern 1: Inconsistent User Prompts

**Problem:** Multiple prompt formats in same command
**Example:** `[Y/n]`, `[1/2/3]`, `[yes/no]` all used
**Impact:** Confusing user experience
**Fix:** Standardize to single format (letter-based preferred: `[Y/n/q]`)

## Pattern 2: Overlapping Steps

**Problem:** Multiple steps handle same responsibility
**Example:** Step 4.2 fixes whitespace, Step 4.5 also fixes whitespace
**Impact:** Unclear ownership, potential conflicts
**Fix:** Clarify which step handles what, add explicit boundaries

## Pattern 3: Missing Decision Logic

**Problem:** Step presents options but doesn't define what happens next
**Example:** "Fix these issues: ..." but no logic for post-fix flow
**Impact:** Command execution unclear
**Fix:** Add explicit decision points with all outcomes defined

## Pattern 4: Ambiguous Tool Responsibilities

**Problem:** Unclear what tools can/cannot detect
**Example:** "Manual review catches remaining issues" but no list of what to check
**Impact:** User doesn't know what to verify
**Fix:** Add explicit reference section listing tool limitations

## Pattern 5: Cleanup Confusion

**Problem:** Cleanup steps scattered throughout workflow
**Example:** Cleanup in steps 2, 5, 7, and 9
**Impact:** Artifacts may accumulate
**Fix:** Clean immediately after each tool, verify at end

## Pattern 6: Missing Error Handling

**Problem:** No instructions for tool failures
**Example:** "Run tool X" but nothing about what if tool fails
**Impact:** Command crashes or hangs on errors
**Fix:** Add error handling with user options for each critical tool

## Pattern 7: Incomplete Statistics

**Problem:** Counters missing or not updated
**Example:** Track `issues_fixed` but not `files_skipped`
**Impact:** Final report incomplete
**Fix:** Add all relevant counters and update throughout workflow

## Pattern 8: Missing Configuration Persistence

**Problem:** User decisions not persisted across runs
**Example:** User skips file but decision not saved
**Impact:** User must repeat decisions on every run
**Fix:** Add .claude/run-configuration.md pattern for persistence

## Pattern 9: Unclear Step Purpose

**Problem:** Step exists but its role in workflow is unclear
**Example:** Step 4.6 provides guidance but Step 4.4 already handles fixes
**Impact:** Redundant steps, confusion
**Fix:** Clarify as informational reference or merge with related step

## Pattern 10: Parameter Validation Gap

**Problem:** Parameters documented but validation logic missing
**Example:** `file=<path>` parameter but no check if file exists
**Impact:** Command fails with unclear error
**Fix:** Add explicit validation section with error handling

## Pattern 11: Command Bloat (> 500 lines)

**Problem:** Command file exceeds reasonable length
**Detection:** Line count > 500 (bloated), > 400 (large)
**Impact:** Hard to maintain, understand, and update
**Fix:** Extract detailed knowledge to skill, reference from command

**Restructuring Strategy:**
1. Identify extractable content (patterns, standards, best practices)
2. Create skill with `standards/` directory
3. Move extracted content to skill
4. Update command to reference skill
5. Result: Command 300-400 lines, skill contains details

## Pattern 12: Duplicate Content

**Problem:** Same information repeated in multiple sections
**Example:** Parameter explanation in both PARAMETERS and WORKFLOW sections
**Impact:** Maintenance burden, inconsistency risk
**Fix:** Keep in one authoritative location, cross-reference from others

## Pattern 13: Over-Specification

**Problem:** Excessive detail that AI can infer
**Example:** "Display file path using forward slashes, escape special characters, truncate if > 80 chars..."
**Impact:** Unnecessary verbosity
**Fix:** "Display: `<relative_file_path>`" - trust AI inference

## Pattern 14: Accumulated Warnings

**Problem:** CRITICAL/IMPORTANT/WARNING notes everywhere
**Example:** Every step has 2-3 warning boxes
**Impact:** Warning fatigue, real issues hidden
**Fix:** Limit to one CRITICAL note per major section maximum

## Pattern 15: Obsolete Content

**Problem:** Deprecated steps, old notes, "to be implemented" comments
**Example:** "Step 4.6: DEPRECATED - now handled in Step 4.4 [keep entire section for reference]"
**Impact:** Confusion, bloat
**Fix:** Remove obsolete content entirely

## Pattern 16: Missing YAML Frontmatter

**Problem:** No frontmatter or invalid YAML
**Example:** File starts directly with content, no `---` delimiters
**Impact:** Command not recognized by Claude Code
**Fix:** Add proper YAML frontmatter with name and description

## Pattern 17: Invalid YAML Syntax

**Problem:** YAML syntax errors
**Example:** Tabs instead of spaces, missing quotes, invalid nesting
**Impact:** Command fails to load
**Fix:** Repair YAML structure

## Pattern 18: Description Too Short

**Problem:** Description field < 10 characters
**Example:** `description: "Command"`
**Impact:** User doesn't understand purpose
**Fix:** Write clear description (50-200 chars recommended)

## Pattern 19: Description Too Long

**Problem:** Description exceeds 1024 characters
**Impact:** Violates Claude Code limit
**Fix:** Condense to essential information

## Pattern 20: Documentation-Only Noise

**Problem:** Sections with only broken external links
**Example:** "Related Commands" section with xref links to non-existent files
**Fix:** Remove section (zero information loss)

## Pattern 21: Command Self-Improvement Pattern

**Note:** Commands have DIFFERENT continuous improvement rules than agents.

**Agent Rule (Pattern 22 in agent-analysis-patterns.md):**
- Agents CANNOT self-invoke
- Agents MUST report improvements to caller
- Pattern 22 violation: Agent trying to call `/plugin-update-agent`

**Command Rule (This pattern):**
- Commands CAN and SHOULD self-update
- Commands use `/plugin-update-command` to update themselves
- This is NOT a violation - this is the CORRECT pattern for commands

**Expected CONTINUOUS IMPROVEMENT RULE for commands:**

```markdown
## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better,
or more efficient approach, **YOU MUST immediately update this file** using
`/plugin-update-command command-name={command-name} update="[your improvement]"` with:
1. [Specific improvement area relevant to command]
2. [Another improvement area]
3. [Another improvement area]
...
```

**Detection:**
- Check if file is in `.../commands/` directory (command) vs `.../agents/` (agent)
- For commands: Verify CONTINUOUS IMPROVEMENT RULE uses self-update pattern
- For commands: Flag as WARNING if using caller-reporting pattern instead

**Why Commands Self-Update:**
- Commands are user-facing workflows with autonomous evolution capability
- Commands directly invoked by users (have SlashCommand tool access)
- Self-updating ensures commands improve based on actual usage patterns

**DO NOT confuse with Pattern 22:**
- Pattern 22 applies to AGENTS only (agents in `.../agents/` directories)
- Commands in `.../commands/` directories SHOULD self-update
- This is a fundamental architectural difference

## Pattern Detection Priority

### CRITICAL (Must Fix Before Use):
- Pattern 16: Missing YAML Frontmatter
- Pattern 17: Invalid YAML Syntax
- Pattern 18: Description Too Short
- Pattern 6: Missing Error Handling (for critical tools)
- Pattern 10: Parameter Validation Gap

### WARNING (Should Fix for Quality):
- Pattern 11: Command Bloat (> 500 lines)
- Pattern 12: Duplicate Content
- Pattern 2: Overlapping Steps
- Pattern 3: Missing Decision Logic
- Pattern 5: Cleanup Confusion
- Pattern 7: Incomplete Statistics
- Pattern 13: Over-Specification
- Pattern 14: Accumulated Warnings
- Pattern 15: Obsolete Content
- Pattern 19: Description Too Long
- Pattern 20: Documentation-Only Noise

### SUGGESTION (Nice to Have):
- Pattern 1: Inconsistent User Prompts
- Pattern 4: Ambiguous Tool Responsibilities
- Pattern 8: Missing Configuration Persistence
- Pattern 9: Unclear Step Purpose

## Pattern Detection Logic

When analyzing commands, check patterns in this order:

1. **Structural Issues** (Patterns 16, 17, 18, 19) - Command must be loadable
2. **Bloat Detection** (Pattern 11) - Overall size and complexity
3. **Content Quality** (Patterns 12, 13, 14, 15, 20) - Clarity and conciseness
4. **Workflow Issues** (Patterns 2, 3, 5, 9) - Execution clarity
5. **Completeness** (Patterns 6, 7, 10) - Error handling and validation
6. **UX Issues** (Patterns 1, 4, 8) - User experience

## Anti-Patterns to Avoid

**The Swiss Army Command:**
- Tries to do too many things
- > 500 lines
- Split into focused commands

**The Over-Documenter:**
- Excessive explanations everywhere
- Warnings and notes on every step
- Remove redundant documentation

**The Duplicator:**
- Repeats same information in multiple sections
- Copy-paste content
- Consolidate to single source of truth

**The Fossil:**
- Keeps deprecated steps "for reference"
- Obsolete comments everywhere
- Remove all obsolete content

**The Micro-Manager:**
- Over-specifies every detail
- Doesn't trust AI inference
- Simplify, trust AI capabilities

**The Cleanup Procrastinator:**
- Cleanup scattered throughout workflow
- Artifacts accumulate
- Clean immediately after each tool

**The Statistic Skipper:**
- Missing counters
- Incomplete final report
- Track all relevant metrics

**The Prompt Anarchist:**
- Different prompt formats everywhere
- [Y/n], [yes/no], [1/2/3] all mixed
- Standardize to one format

## Bloat Detection Algorithm

```
1. Count total lines
2. If > 500 lines:
   - Flag as BLOATED
   - Identify extractable sections:
     - Analysis patterns (> 100 lines?)
     - Best practices (> 100 lines?)
     - Detailed standards (> 100 lines?)
   - Recommend: Extract to skill

3. If > 400 lines:
   - Flag as LARGE
   - Warn: Monitor for bloat
   - Check for duplicate content
   - Check for over-specification

4. If < 400 lines:
   - Check other patterns only
```

## Restructuring Decision Tree

```
Is command > 500 lines?
├─ YES → Contains detailed patterns/standards?
│   ├─ YES → Extract to skill, reduce to 300-400 lines
│   └─ NO → Remove duplication, consolidate steps
└─ NO → Contains duplicate content?
    ├─ YES → Consolidate, aim for < 400 lines
    └─ NO → Command is well-sized, check other patterns
```
