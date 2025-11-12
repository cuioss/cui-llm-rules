---
name: cui-diagnose-commands
description: Analyze, verify, and fix slash commands for clarity, structure, and bloat
---

# Commands Doctor - Verify and Fix Commands

Orchestrates comprehensive analysis of slash commands by coordinating cui-diagnose-single-command for each command.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-diagnose-commands update="[your improvement]"` with:
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
Skill: cui-utility-commands:cui-diagnostic-patterns
```

**Optionally load marketplace architecture standards**:

You may optionally load the marketplace architecture skill for additional architectural context:
```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This provides architecture rules and validation patterns for marketplace components that may be useful for understanding command design principles.

### Step 2: Discover Commands

**Parse parameters** to determine scope.

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

### Step 3: Analyze Commands (Parallel)

**For EACH command discovered:**

Launch cui-diagnose-single-command:

```
Task:
  subagent_type: cui-diagnose-single-command
  description: Analyze {command-name}
  prompt: |
    Analyze this command comprehensively.

    Parameters:
    - command_path: {absolute_path_to_command}

    Return complete JSON report with all issues found.
```

**CRITICAL**: Launch ALL commands in PARALLEL (single message, multiple Task calls).

**Collect results** from each command as they complete.

### Step 4: Aggregate Results

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
  "by_command": {
    "command-name-1": {
      "status": "Clean|Warnings|Critical",
      "classification": "ACCEPTABLE|LARGE|BLOATED",
      "issues": {...},
      "scores": {...}
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

### Step 5: Generate Summary Report

**Display:**

```
==================================================
Commands Doctor - Analysis Complete
==================================================

Commands Analyzed: {total}
- Acceptable (<400 lines): {count} ✅
- Large (400-500 lines): {count} ⚠️
- Bloated (>500 lines): {count} ❌ NEEDS RESTRUCTURING

Issue Statistics:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}
- Total: {count}

Quality Scores:
- Average Bloat: {score}/100 (target <100)
- Average Anti-Bloat Compliance: {score}/100
- Average Structure: {score}/100
- Average Quality: {score}/100

By Command:
- {cmd-1}: {classification} | {lines} lines | Bloat: {score} | Quality: {score}
- {cmd-2}: {classification} | {lines} lines | Bloat: {score} | Quality: {score}
...

Recommendations:
{if bloated commands}
⚠️ CRITICAL: {count} commands are bloated and need restructuring
- {command-name}: {lines} lines - Extract sections to skills
{endif}

{if all acceptable}
✅ All commands are well-sized and follow anti-bloat rules!
{endif}
```

**If --save-report flag is set:**
- Write the complete report above to `commands-diagnosis-report.md` in project root
- Inform user: "Report saved to: commands-diagnosis-report.md"

**Default behavior (no flag):**
- Display report only (as shown above)
- Do NOT create any files

### Step 6: Categorize Issues for Fixing

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

### Step 7: Apply Safe Fixes

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

### Step 8: Prompt for Risky Fixes

**When to execute**: If risky fixes exist (regardless of auto-fix setting)

**For each risky fix, prompt user:**

```
[PROMPT] Risky fix detected in {command-name}:

Issue: {issue description}
Location: {file path and line number}
Proposed fix: {fix description}
Impact: {explanation of changes needed}

Apply this fix? [Y]es / [N]o / [S]kip all remaining
```

**Handle responses:**
- **Yes**: Apply the fix using Edit tool
- **No**: Skip this fix, continue to next
- **Skip all remaining**: Exit fixing phase, proceed to verification

**Special handling for bloated commands (>500 lines):**
```
[PROMPT] Bloated command detected: {command-name} ({line_count} lines)

This command exceeds the 500-line limit and requires restructuring.

Recommended action:
1. Extract detailed content to skills using /cui-create-skill
2. Update command to reference skills instead of inline content

This requires manual intervention. Options:
[D]efer to manual fix / [A]ttempt automatic extraction / [S]kip

Note: Automatic extraction is experimental and may require review.
```

**Track risky fixes:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "bloat_fixes_deferred": {count}
}
```

### Step 9: Verify Fixes

**When to execute**: After any fixes applied (Step 7 or Step 8)

**Re-run analysis** on modified commands:
```
Task:
  subagent_type: cui-diagnose-single-command
  description: Verify fixes for {command-name}
  prompt: |
    Re-analyze this command after fixes.

    Parameters:
    - command_path: {absolute_path_to_command}

    Return complete JSON report.
```

**Compare before/after:**
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

**Report verification results:**
```
Verification Complete:
✅ {issues_resolved} issues resolved
{if issues_remaining > 0}
⚠️ {issues_remaining} issues remain (require manual intervention or /cui-update-command)
{endif}
{if new_issues > 0}
❌ {new_issues} NEW issues introduced (fixes need review!)
{endif}
{if bloated_commands_remain}
⚠️ Bloated commands require extraction to skills:
- Use /cui-create-skill to extract content
- Update command to reference skills
{endif}
```

## ARCHITECTURE

This command is a simple orchestrator:
- Discovers commands using Glob (non-prompting)
- Launches cui-diagnose-single-command in parallel
- Aggregates and reports results with bloat metrics

All analysis logic is in the specialized agent:
- cui-diagnose-single-command (comprehensive command analysis)

## TOOL USAGE

- **Glob**: Discover commands (non-prompting)
- **Task**: Launch cui-diagnose-single-command (parallel)
- **Skill**: Load diagnostic patterns

## RELATED

- `/cui-update-command` - Apply fixes to commands
- `/cui-diagnose-agents` - Diagnose agents
- `/cui-diagnose-skills` - Diagnose skills
- `/cui-diagnose-bundle` - Diagnose entire bundle
- `/cui-create-skill` - Extract bloated content to skills

## STANDARDS

Command analysis follows:
- Command quality standards (bundles/cui-plugin-development-tools/standards/command-quality-standards.md)
- Command analysis patterns (bundles/cui-plugin-development-tools/standards/command-analysis-patterns.md)
- 8 anti-bloat rules (CRITICAL for preventing bloat)

Standards are loaded automatically by cui-diagnose-single-command.
