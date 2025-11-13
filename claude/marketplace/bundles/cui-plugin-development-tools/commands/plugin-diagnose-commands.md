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
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Interactive mode

## WORKFLOW

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
- `--save-report`: Default false, flag only

### Step 3: Discover Commands

**Using validated scope from Step 2:**

**For marketplace scope (default):**
```
Glob: pattern="*.md", path="~/git/cui-llm-rules/claude/marketplace/commands"
Glob: pattern="*/commands/*.md", path="~/git/cui-llm-rules/claude/marketplace/bundles"
```

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

### Step 4: Analyze Commands and Validate References (Parallel)

**For EACH command discovered, launch TWO agents in parallel:**

**A. Command Analysis Agent:**
```
Task:
  subagent_type: diagnose-command
  description: Analyze {command-name}
  prompt: |
    Analyze this command comprehensively.

    Parameters:
    - command_path: {absolute_path_to_command}

    Return complete JSON report with all issues found.
```

**B. Reference Validation Agent:**
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

**CRITICAL**: Launch ALL analyses in PARALLEL (single message with multiple Task calls for both agent types across all commands).

**Error handling:**
- If agent fails to launch or returns error: Collect failure info and continue with remaining agents
- Report all failures in aggregate results

**Collect results** from both agent types as they complete.

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

### Step 7: Handle Reference Issues

**When to execute:** If reference issues found (incorrect or ambiguous references > 0)

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

**Categorize all issues into Safe vs Risky:**

**Safe fixes** (auto-apply when auto-fix=true):
- YAML frontmatter syntax errors
- Missing YAML fields (add defaults: `name`, `description`)
- Obsolete content removal (deprecated sections, outdated comments)
- Add missing CONTINUOUS IMPROVEMENT RULE template
- Formatting/whitespace normalization
- Broken cross-references (remove or fix)

**Risky fixes** (always prompt user):
- Bloat resolution (>500 lines - requires extraction to skills)
- Over-specification reduction (requires judgment on what's essential)
- Duplication consolidation (requires understanding context)
- Parameter validation additions (requires understanding parameters)
- Structural reorganization (requires understanding workflow)

### Step 9: Apply Safe Fixes

**When to execute**: If auto-fix=true (default) AND safe fixes exist

**For each safe fix:**

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

**Track fixes applied:**
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

**For each risky fix:**

Prompt user with: Issue description, location, proposed fix, impact, and options [Y]es/[N]o/[S]kip all

**Handle responses:**
- **Yes**: Apply fix using Edit tool
- **No**: Skip this fix, continue to next
- **Skip all**: Exit fixing phase, proceed to Step 11

**For bloated commands (>500 lines):**

Prompt user with restructuring recommendation and options: [D]efer/[A]ttempt extraction/[S]kip

**Track risky fixes:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "bloat_fixes_deferred": {count}
}
```

### Step 11: Verify Fixes

**When to execute**: After any fixes applied (Step 9 or Step 10)

**Re-run analysis** on modified commands using diagnose-command agent.

**Compare before/after** and generate verification summary using same format as Step 6:
- Issues resolved count
- Issues remaining (if any)
- New issues introduced (should be 0)
- Bloated commands still requiring extraction (if any)

## ARCHITECTURE

This command is a simple orchestrator:
- Discovers commands using Glob (non-prompting)
- Launches diagnose-command and analyze-plugin-references in parallel
- Aggregates and reports results with bloat metrics and reference validation

All analysis logic is in specialized agents:
- diagnose-command (comprehensive command analysis)
- analyze-plugin-references (plugin reference validation)

## TOOL USAGE

- **Glob**: Discover commands (non-prompting)
- **Task**: Launch diagnose-command (parallel)
- **Skill**: Load diagnostic patterns

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

Standards are loaded automatically by diagnose-command.
