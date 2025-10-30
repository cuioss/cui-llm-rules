---
name: cui-diagnose-commands
description: Analyze, verify, and fix slash commands for clarity, structure, and bloat
---

# Commands Doctor - Verify and Fix Commands

Orchestrates comprehensive analysis of slash commands by coordinating cui-diagnose-single-command for each command.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace commands
- **scope=global**: Analyze commands in ~/.claude/commands/
- **scope=project**: Analyze commands in .claude/commands/
- **command-name** (optional): Review specific command
- **No parameters**: Interactive mode

## WORKFLOW

### Step 1: Activate Diagnostic Patterns

**CRITICAL**: Load non-prompting tool patterns:

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

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

## FIXING ISSUES

This command currently REPORTS issues only. To fix:

1. Review recommendations in report
2. For bloated commands: Extract sections to skills
3. For quality issues: Manually edit files
4. Re-run cui-diagnose-commands to verify fixes

**Critical**: Commands >500 lines MUST be restructured by extracting content to skills.

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

- `/cui-diagnose-agents` - Diagnose agents
- `/cui-diagnose-skills` - Diagnose skills
- `/cui-diagnose-bundle` - Diagnose entire bundle

## STANDARDS

Command analysis follows:
- Command quality standards (bundles/cui-plugin-development-tools/standards/command-quality-standards.md)
- Command analysis patterns (bundles/cui-plugin-development-tools/standards/command-analysis-patterns.md)
- 8 anti-bloat rules (CRITICAL for preventing bloat)

Standards are loaded automatically by cui-diagnose-single-command.
