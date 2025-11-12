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

## FIXING ISSUES

To fix reported issues:

1. **Review recommendations** in report
2. **Use `/cui-update-command`** to apply fixes:
   ```
   /cui-update-command command-name={command-name} update="{issue description}"
   ```
3. **Re-run diagnosis** to verify:
   ```
   /cui-diagnose-commands command-name={command-name}
   ```

**For bloated commands (>500 lines):**
- Extract content to skills using `/cui-create-skill`
- Commands MUST be restructured by extracting detailed content to skills

**Example workflow:**
```
# 1. Diagnose command
/cui-diagnose-commands command-name=my-command

# 2. Apply fix using update command
/cui-update-command command-name=my-command update="Add error handling in Step 3"

# 3. Verify fix
/cui-diagnose-commands command-name=my-command
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
