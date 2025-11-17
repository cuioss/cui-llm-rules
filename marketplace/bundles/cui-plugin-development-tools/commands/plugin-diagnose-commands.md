---
name: plugin-diagnose-commands
description: Analyze, verify, and fix slash commands for clarity, structure, and bloat
---

# Commands Doctor - Verify and Fix Commands

Orchestrates comprehensive analysis of slash commands by coordinating diagnose-command for each command.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-commands update="[your improvement]"` with:
1. Improved command bloat detection and size classification metrics
2. Better methods for identifying structural issues and anti-bloat violations
3. More effective quality scoring and command organization assessment techniques
4. Enhanced detection of commands requiring extraction to skills
5. Any lessons learned about command design patterns and complexity reduction strategies

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace commands
- **scope=global**: Analyze commands in ~/.claude/commands/
- **scope=project**: Analyze commands in .claude/commands/
- **command-name** (optional): Review specific command
- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes
- **--validate-references** (optional, default: false): Run reference validation analysis (doubles agent count)
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Interactive mode

## WORKFLOW

## WORKFLOW OVERVIEW

**This command has TWO phases - you MUST complete both:**

**PHASE 1: Analysis (Steps 1-6)**
- Discover components
- Analyze each component
- Generate report

**PHASE 2: Fix Workflow (Steps 7-11)**
- Handle reference issues
- Categorize issues (safe vs risky)
- Apply safe fixes automatically
- Prompt user for risky fixes
- Verify all fixes worked

**CRITICAL: Do not stop after Step 6. Continue to Step 7.**

### Step 1: Activate Diagnostic Patterns

**CRITICAL**: Load non-prompting tool patterns:

```
Skill: cui-utilities:cui-diagnostic-patterns
```

**Optionally load marketplace architecture standards**:

You may optionally load the marketplace architecture skill for additional architectural context:
```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components that may be useful for understanding command design principles.

### Step 2: Validate Parameters

**Parse and validate all parameters:**

**Scope validation:**
- If scope specified: Verify it's one of `marketplace`, `global`, `project`
- If invalid: Display error and abort
- Default: `marketplace`

**Command-name validation:**
- If provided: Will filter to specific command in Step 3

**Path validation:**
- For `global` scope: Verify `~/.claude/commands/` exists
- For `project` scope: Verify `.claude/commands/` exists
- If path missing: Display error and abort

**Flag validation:**
- `auto-fix`: Default true, accepts true/false
- `--validate-references`: Default false, flag only (enables reference validation agents)
- `--save-report`: Default false, flag only

### Step 3: Discover Commands

**Using validated scope from Step 2:**

**For marketplace scope (default):**

Execute plugin-inventory command:
```
SlashCommand: /plugin-inventory --json
```

Parse JSON output:
- Extract `bundles[]` array from JSON response
- For each bundle, collect `bundle.commands[]` with `name` and `path` fields
- Build flat list of command paths from all bundles

**For global scope:**
```
Glob: pattern="*.md", path="~/.claude/commands"
```

**For project scope:**
```
Glob: pattern="*.md", path=".claude/commands"
```

**Extract command names** from file paths.

**If specific command name provided:**
- Filter list to matching command only

**If no parameters (interactive mode):**
- Display numbered list of all commands found
- Separate standalone and bundle commands
- Let user select which to analyze or change scope

### Step 3a: Load Analysis Standards (Once)

**CRITICAL**: Load standards files once to avoid redundant reads in each agent.

**Load command analysis standards:**
```
Read: marketplace/bundles/cui-plugin-development-tools/standards/command-quality-standards.md
Read: marketplace/bundles/cui-plugin-development-tools/standards/command-analysis-patterns.md
```

**Store standards content** in context to pass to agents in Step 4.

**Token Optimization**: These standards are loaded once here instead of 46+ times (once per command in each diagnose-command agent).

### Step 4: Analyze Commands (Batched)

**CRITICAL**: Process commands in batches to manage token usage.

**Batch Configuration:**
- **Batch size**: 5 commands per batch
- **Agent count per batch**:
  - Without --validate-references: 5 agents (diagnose-command only)
  - With --validate-references: 10 agents (5 diagnose-command + 5 analyze-plugin-references)
- **Processing**: Sequential batch execution
- **Results**: Accumulate across all batches

**For EACH batch of commands:**

1. **Select next batch** of up to 5 commands from discovery list

2. **Launch agents in parallel for current batch:**

   **A. Command Analysis Agent (for each command in batch - ALWAYS run):**
   ```
   Task:
     subagent_type: diagnose-command
     description: Analyze {command-name}
     prompt: |
       Analyze this command comprehensively.

       Parameters:
       - command_path: {absolute_path_to_command}

       IMPORTANT: Standards have been pre-loaded by orchestrator.
       Skip Step 1 (Load Analysis Standards) - use standards from context instead.

       IMPORTANT: Use streamlined output format (issues only).
       Return minimal JSON - CLEAN commands get {"status": "CLEAN"},
       commands with issues get only critical_issues/warnings/suggestions arrays.

       This reduces token usage from ~2,000 to ~200-800 tokens per command.
   ```

   **B. Reference Validation Agent (for each command in batch - ONLY if --validate-references flag set):**
   ```
   Task:
     subagent_type: analyze-plugin-references
     description: Validate references in {command-name}
     prompt: |
       Analyze plugin references in this command.

       Parameters:
       - path: {absolute_path_to_command}
       - auto-fix: false  # Collect issues only, don't modify

       Return complete reference analysis with all issues found.
   ```

3. **Collect batch results** from agents

4. **Accumulate to aggregate results**

5. **Repeat** until all commands processed

**Token Management:**
- Without --validate-references: 5 agents per batch (optimal)
- With --validate-references: 10 agents per batch (doubles token usage but still manageable)
- Allow agents to complete before starting next batch
- Display progress: "Processing batch X/Y (commands N-M)..."

**Performance Note:**
- Default mode (no --validate-references): Analyzes 46 commands in ~10 batches
- With --validate-references: Same batches but 2× agents per batch

**Error handling:**
- If agent fails to launch or returns error: Collect failure info and continue with remaining agents in batch
- Report all failures in aggregate results
- Continue with next batch even if current batch has failures

### Step 5: Aggregate Results

**Combine findings from all commands:**

```json
{
  "total_commands_analyzed": {count},
  "commands_with_issues": {count},
  "bloated_commands": {count},
  "issue_summary": {
    "critical": {total_count},
    "warnings": {total_count},
    "suggestions": {total_count}
  },
  "reference_summary": {
    "total_references": {count},
    "correct_references": {count},
    "incorrect_references": {count},
    "ambiguous_references": {count},
    "commands_with_reference_issues": {count}
  },
  "by_command": {
    "command-name-1": {
      "status": "Clean|Warnings|Critical",
      "classification": "ACCEPTABLE|LARGE|BLOATED",
      "issues": {...},
      "scores": {...},
      "references": {
        "found": {count},
        "correct": {count},
        "issues": {count}
      }
    },
    ...
  },
  "overall_metrics": {
    "avg_bloat_score": {score},
    "avg_anti_bloat_compliance": {score},
    "avg_structure_score": {score},
    "avg_quality_score": {score},
    "commands_excellent": {count},
    "commands_good": {count},
    "commands_fair": {count},
    "commands_poor": {count}
  }
}
```

### Step 6: Generate Summary Report

**Display summary report with:**
- Commands analyzed by size classification (Acceptable/Large/Bloated)
- Issue statistics (Critical/Warnings/Suggestions)
- Reference validation statistics (Total/Correct/Incorrect/Ambiguous)
- Quality score averages (Bloat/Anti-Bloat/Structure/Quality)
- Per-command breakdown with classification, lines, and scores
- Recommendations for bloated commands or success message

**If --save-report flag is set:**
- Write the complete report above to `commands-diagnosis-report.md` in project root
- Inform user: "Report saved to: commands-diagnosis-report.md"

**Default behavior (no flag):**
- Display report only (as shown above)
- Do NOT create any files

==================================================
⚠️ CRITICAL: ANALYSIS PHASE COMPLETE
==================================================

You have completed PHASE 1 (Analysis).

**YOU MUST NOW PROCEED TO PHASE 2 (Fix Workflow)**

DO NOT STOP HERE. The analysis is useless without fixes.

If any issues were found (warnings or suggestions):
→ Continue to Step 7: Handle Reference Issues
→ Continue to Step 8: Categorize Issues
→ Continue to Step 9: Apply Safe Fixes
→ Continue to Step 10: Prompt for Risky Fixes
→ Continue to Step 11: Verify Fixes

If zero issues found:
→ Skip to completion message

==================================================

### Step 7: Handle Reference Issues ⚠️ PHASE 2 STARTS HERE

**When to execute:** ONLY if --validate-references flag was set AND reference issues found (incorrect or ambiguous references > 0)

**If --validate-references was NOT set:**
- Skip this step entirely
- Continue to Step 8

**If --validate-references WAS set and issues found:**

**Display summary** of reference problems by command with line numbers and issue types.

**Prompt user** with options: [F]ix automatically, [M]anual review, [S]kip reference fixes, [V]iew detailed reports

**Handle responses:**
- **Fix**: Re-run analyze-plugin-references with auto-fix=true for affected commands, then continue to Step 8
- **Manual**: Re-run analyze-plugin-references with user prompts enabled, then continue to Step 8
- **Skip**: Continue to Step 8
- **View**: Display paths to all .reference-analysis.md files, then re-prompt with same options

**Track statistics:**
- `reference_fixes_applied`: Count of references auto-fixed
- `reference_fixes_manual`: Count of references manually corrected

### Step 8: Categorize Issues for Fixing

**ALWAYS execute this step if any issues were found (warnings or suggestions).**

**Load fix workflow skill:**

```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

**Categorize all issues into Safe vs Risky using patterns from cui-fix-workflow skill.**

Read categorization patterns:
```
Read: standards/categorization-patterns.md (from cui-fix-workflow)
```

**Command-specific safe fix types:**
- YAML frontmatter syntax errors
- Missing YAML fields (add defaults: `name`, `description`)
- Obsolete content removal (deprecated sections, outdated comments)
- Add missing CONTINUOUS IMPROVEMENT RULE template
- Formatting/whitespace normalization
- Broken cross-references (remove or fix)

**Command-specific risky fix categories:**
1. **Bloat Issues** - Commands >500 lines requiring extraction to skills
2. **Clarity Issues** - Over-specification, ambiguous instructions, duplication
3. **Structural Issues** - Parameter validation gaps, workflow reorganization needs

### Step 9: Apply Safe Fixes

**When to execute**: If auto-fix=true (default) AND safe fixes exist

**CRITICAL: If you reached Step 6, you MUST execute this step if safe fixes exist. This is not optional.**

**Follow safe fix patterns from cui-fix-workflow skill.**

**Apply command-specific safe fixes using Edit tool:**

**YAML syntax errors:**
```
Edit: {command-file}
- Fix YAML frontmatter syntax
- Add missing required fields with defaults
- Correct field name typos
```

**Obsolete content removal:**
```
Edit: {command-file}
- Remove deprecated sections marked as obsolete
- Remove outdated comments and TODOs
- Clean up legacy instructions
```

**Add missing CONTINUOUS IMPROVEMENT RULE:**
```
Edit: {command-file}
- Insert CONTINUOUS IMPROVEMENT RULE template after YAML frontmatter
- Include command-specific improvement areas
```

**Formatting normalization:**
```
Edit: {command-file}
- Normalize whitespace and indentation
- Fix heading hierarchy
- Ensure proper markdown structure
- Fix broken cross-references
```

**Track fixes applied using tracking patterns from cui-fix-workflow:**
```json
{
  "safe_fixes_applied": {count},
  "by_type": {
    "yaml_fixes": {count},
    "obsolete_content_removed": {count},
    "continuous_improvement_added": {count},
    "formatting_fixes": {count}
  }
}
```

### Step 10: Prompt for Risky Fixes

**When to execute**: If risky fixes exist (regardless of auto-fix setting)

**Follow prompting patterns from cui-fix-workflow skill.**

Read prompting patterns:
```
Read: standards/prompting-patterns.md (from cui-fix-workflow)
```

**Group risky fixes by command-specific categories:**

1. **Bloat Issues** (>500 lines, extraction needed)
2. **Clarity Issues** (over-specification, unclear purpose)
3. **Structural Issues** (reorganization, consolidation)

**Use AskUserQuestion with standard structure from prompting patterns:**

```
AskUserQuestion:
  questions: [
    {
      question: "Apply fixes for {Category} issues?",
      header: "{Category}",
      multiSelect: true,
      options: [
        {
          label: "Fix: {specific-issue}",
          description: "Impact: {what-changes}. Location: {file}:{line}. Size: {metric}"
        },
        ...
        {
          label: "Skip all {category} fixes",
          description: "Continue without fixing this category"
        }
      ]
    }
  ]
```

**Process user selections following prompting patterns:**
- For each selected fix: Apply using Edit tool, increment `risky_fixes_applied`
- For unselected fixes: Skip, increment `risky_fixes_skipped`
- If "Skip all" selected: Skip entire category, increment `risky_fixes_skipped` by count

**Track risky fixes using tracking patterns from cui-fix-workflow:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "fixes_by_category": {
    "bloat": {applied: count, skipped: count},
    "clarity": {applied: count, skipped: count},
    "structural": {applied: count, skipped: count}
  }
}
```

### Step 11: Verify Fixes

**When to execute**: After any fixes applied (Step 9 or Step 10)

**Follow verification patterns from cui-fix-workflow skill.**

Read verification patterns:
```
Read: standards/verification-patterns.md (from cui-fix-workflow)
```

**Re-run analysis on modified commands:**
```
Task:
  subagent_type: diagnose-command
  description: Verify fixes for {command-name}
  prompt: |
    Re-analyze this command after fixes applied.

    Parameters:
    - command_path: {absolute_path_to_command}

    Return complete JSON report.
```

**Compare before/after using verification patterns:**
```json
{
  "verification": {
    "commands_fixed": {count},
    "issues_resolved": {count},
    "issues_remaining": {count},
    "new_issues": {count}  // Should be 0!
  }
}
```

**Report verification results following verification patterns:**
```
==================================================
Verification Complete
==================================================

✅ {issues_resolved} issues resolved
{if issues_remaining > 0}
⚠️ {issues_remaining} issues remain (require manual intervention or /plugin-update-command)
{endif}
{if new_issues > 0}
❌ {new_issues} NEW issues introduced (fixes need review!)
{endif}
```

## ARCHITECTURE

**Token-Optimized Orchestrator Architecture**

This command is a batched orchestrator designed to handle large-scale marketplace analysis without exceeding token limits:

**Discovery Phase:**
- Uses SlashCommand (/plugin-inventory --json) for marketplace scope (non-prompting)
- Uses Glob for global/project scopes (non-prompting)
- Pre-loads analysis standards once (Step 3a) to avoid redundant reads

**Analysis Phase (Batched):**
- Processes commands in batches of 5 (configurable)
- Launches diagnose-command agents in parallel per batch (5 agents/batch)
- Optionally launches analyze-plugin-references agents if --validate-references flag set (adds 5 more agents/batch)
- Uses streamlined JSON output format (issues only) to reduce result payload by 60%
- Passes pre-loaded standards to agents to eliminate redundant file reads

**Fix Phase:**
- Categorizes issues (safe vs risky) using cui-fix-workflow skill
- Applies safe fixes automatically if auto-fix=true
- Prompts user for risky fixes using AskUserQuestion
- Verifies fixes by re-running diagnose-command on modified files

**Token Optimization Strategies:**
1. **Batching**: Sequential batches of 5 commands instead of 46 parallel agents (90% peak token reduction)
2. **Standards Pre-loading**: Load once, pass to agents (75% reduction in standards loading)
3. **Streamlined Output**: Issues-only JSON format (60% reduction in result size)
4. **Optional Reference Validation**: Skip reference agents by default (50% agent count reduction)

**Expected Token Usage:**
- Without --validate-references: ~30,000 tokens/batch (5 agents)
- With --validate-references: ~60,000 tokens/batch (10 agents)
- Peak usage: Well within limits (vs ~415,000 tokens in original all-parallel design)

**All analysis logic is in specialized agents:**
- diagnose-command (comprehensive command analysis with streamlined output support)
- analyze-plugin-references (plugin reference validation - optional)

## TOOL USAGE

- **SlashCommand**: Execute /plugin-inventory --json (marketplace discovery)
- **Glob**: Discover commands in global/project scopes (non-prompting)
- **Read**: Pre-load standards once (token optimization)
- **Task**: Launch diagnose-command agents in batches (parallel within batch, sequential across batches)
- **Task** (optional): Launch analyze-plugin-references agents if --validate-references
- **Skill**: Load diagnostic patterns and fix workflow patterns
- **Edit**: Apply safe and approved risky fixes
- **AskUserQuestion**: Prompt for risky fix approval

## RELATED

- `/plugin-update-command` - Apply fixes to commands
- `/plugin-diagnose-agents` - Diagnose agents
- `/plugin-diagnose-skills` - Diagnose skills
- `/plugin-diagnose-bundle` - Diagnose entire bundle
- `/plugin-create-skill` - Extract bloated content to skills

## STANDARDS

Command analysis follows:
- Command quality standards (bundles/cui-plugin-development-tools/standards/command-quality-standards.md)
- Command analysis patterns (bundles/cui-plugin-development-tools/standards/command-analysis-patterns.md)
- 8 anti-bloat rules (CRITICAL for preventing bloat)

**Token Optimization**: Standards are pre-loaded once in Step 3a and passed to all agents to avoid 46+ redundant file reads.
