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

**CRITICAL: Load marketplace architecture standards**:

```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

This skill provides command quality standards and analysis patterns used throughout the diagnosis workflow. All agents will reference these standards from the loaded skill context.

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

Execute plugin-inventory command to get complete marketplace inventory:
```
SlashCommand: /plugin-inventory --json
```

**CRITICAL:** Must get complete inventory (agents, commands, AND skills) because analyze-plugin-references agents need skill data to validate Skill invocations.

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

### Step 4: Group Commands by Bundle

**CRITICAL**: Organize commands by bundle for sequential processing.

**Parse inventory from Step 3:**
- Extract `bundles[]` array from inventory JSON
- For each bundle, identify bundle name and collect all commands with their paths
- Create bundle-to-commands mapping

**Sort bundles:**
1. **First**: `cui-plugin-development-tools` (always first)
2. **Then**: All other bundles alphabetically by name

**Example bundle order:**
```
1. cui-plugin-development-tools
2. cui-documentation-standards
3. cui-frontend-expert
4. cui-java-expert
5. cui-maven
6. cui-task-workflow
7. cui-utilities
```

**Display processing plan:**
```
Processing {total_bundles} bundles in order:
1. cui-plugin-development-tools ({command_count} commands)
2. {bundle-name} ({command_count} commands)
...
```

### Step 5: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps for one bundle before moving to the next.

**For EACH bundle in sorted order:**

Display: `Processing bundle: {bundle_name} ({command_count} commands)`

**Step 5a: Analyze Bundle Commands**

For all commands in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:diagnose-command
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

**Launch command analysis agents in parallel** (single message, multiple Task calls) for all commands in current bundle.

**Collect results** for this bundle's commands.

**Error Handling:**
- If Task fails: Display warning with command name and error, mark as "Analysis Failed", continue
- If malformed response: Display warning, mark as "Malformed Response", continue
- If timeout: Display warning, mark as "Timeout", continue

**Step 5b: Check Plugin References for Bundle**

For all commands in current bundle:

```
Task:
  subagent_type: cui-plugin-development-tools:analyze-plugin-references
  description: Validate references in {command-name}
  prompt: |
    Analyze plugin references in this command.

    Parameters:
    - path: {absolute_path_to_command}
    - marketplace_inventory: {complete_json_inventory_from_step_3}
    - auto-fix: true  # Auto-fix deterministic reference issues (missing/incorrect bundle prefixes)

    IMPORTANT: marketplace_inventory must contain COMPLETE inventory (agents, commands, AND skills) from Step 3's /plugin-inventory --json call.
    This complete data is required to validate Skill invocations and cross-references between all resource types.

    Return complete reference analysis with all issues found.
```

**Launch reference validation agents in parallel** (single message, multiple Task calls) for all commands in current bundle.

**Collect results** for this bundle's reference validation.

**Error Handling:**
- If Task fails: Display warning with command name and error, mark as "Reference Check Failed", continue
- If unexpected format: Display warning, mark as "Reference Check Error", continue

**Aggregate reference findings for this bundle:**
Track for each command: references_found, references_correct, references_fixed, references_ambiguous.
Bundle totals: commands_checked, total_references, correct, fixed, issues.

**Step 5b.1: Verify Reference Violations (MANDATORY)**

**CRITICAL**: Before accepting reference violations, re-verify flagged issues to eliminate false positives.

**For each command flagged with reference violations in Step 5b:**

1. **Read exact flagged lines with context**:
   ```
   Read: {command_file_path}
   ```
   Focus on lines flagged by analyze-plugin-references, include ±2 lines context.

2. **Distinguish runtime invocations from documentation**:

   **✅ ACTUAL VIOLATIONS (runtime invocations)**:
   - Direct tool usage: `SlashCommand: /plugin-update-command`
   - Agent configuration: `subagent_type: cui-utilities:research`
   - Task launches: `Task:` followed by subagent_type
   - In workflow steps describing actual execution

   **❌ FALSE POSITIVES (documentation text - DO NOT REPORT)**:
   - Pattern examples: "Pattern: subagent_type:" or "e.g., 'Task:'"
   - CONTINUOUS IMPROVEMENT RULE instructions: "The caller can then invoke `/plugin-update-command`"
   - Documentation explaining how callers use commands: "Caller invokes /command-name"
   - Tool search patterns: "Search for tool mentions (e.g., 'Task:')"
   - Architecture descriptions: "When you need to use Task tool"

3. **Only report verified violations**:
   - Discard flagged lines that are documentation/examples
   - Keep only actual runtime invocations
   - Track: `violations_flagged`, `violations_verified`, `false_positives_filtered`

**Error Handling:**
- If Read fails: Log warning, mark as "Verification Failed", exclude from violation count
- If context unclear: Include in manual review list rather than auto-reporting as violation

**Step 5c: Aggregate Results for Bundle**

**Combine findings for this bundle's commands:**

Track bundle metrics:
- `bundle_name`: Current bundle name
- `total_commands_analyzed`: Count for this bundle
- `commands_with_issues`: Count for this bundle
- `bloated_commands`: Count for this bundle
- Issue counts: `critical`, `warnings`, `suggestions`
- Reference stats: `total_references`, `correct`, `incorrect`, `ambiguous`
- Quality scores: averages for bloat, anti-bloat compliance, structure, quality
- Per-command data: status, classification, issues, scores, reference counts

**Step 5d: Generate Bundle Summary Report**

**Display bundle summary:**

```
==================================================
Bundle: {bundle_name}
==================================================

Commands Analyzed: {total}
- Acceptable size: {count} ✅
- Large: {count} ⚠️
- Bloated: {count} ❌

Issue Statistics:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}

Quality Scores:
- Average Bloat Score: {score}/100
- Average Anti-Bloat Compliance: {score}/100
- Average Structure: {score}/100
- Average Quality: {score}/100

Reference Validation:
- Total references: {total_references}
- Correct: {correct}
- Incorrect: {incorrect}
- Ambiguous: {ambiguous}

Per-Command Summary:
- {command-1}: {classification} | {lines} lines | Quality: {score} | Refs: {correct}/{found}
- {command-2}: {classification} | {lines} lines | Quality: {score} | Refs: {correct}/{found}
...
```

**Step 5e: Categorize Issues for Bundle ⚠️ FIX PHASE STARTS**

**If any issues found in this bundle:**

**Load fix workflow skill (once, if not already loaded):**
```
Skill: cui-plugin-development-tools:cui-fix-workflow
```

**Categorize issues for this bundle into Safe vs Risky:**

**Command-specific safe fix types:**
- YAML frontmatter syntax errors
- Missing YAML fields (add defaults: `name`, `description`)
- Obsolete content removal
- Add missing CONTINUOUS IMPROVEMENT RULE template
- Formatting/whitespace normalization
- Broken cross-references

**Command-specific risky fix categories:**
1. **Bloat Issues** - Commands >500 lines requiring extraction to skills
2. **Clarity Issues** - Over-specification, ambiguous instructions, duplication
3. **Structural Issues** - Parameter validation gaps, workflow reorganization needs

**Step 5f: Handle Reference Issues for Bundle**

**When to execute**: If reference issues found in this bundle

Display summary of reference problems for this bundle.

Prompt user with options: [F]ix automatically, [M]anual review, [S]kip

Track: `bundle_reference_fixes_applied`, `bundle_reference_fixes_manual`

**Step 5g: Apply Safe Fixes for Bundle**

**When to execute**: If auto-fix=true (default) AND safe fixes exist in this bundle

Apply safe fixes for commands in this bundle using Edit tool.

Track: `bundle_safe_fixes_applied`, `by_type` (yaml, obsolete_content, continuous_improvement, formatting)

**When to execute**: If risky fixes exist in this bundle

Use AskUserQuestion for risky fixes in this bundle.

Group by categories: Bloat Issues, Clarity Issues, Structural Issues

Track: `bundle_risky_fixes_prompted`, `bundle_risky_fixes_applied`, `bundle_risky_fixes_skipped`

**Step 5i: Verify Fixes for Bundle**

**When to execute**: After any fixes applied in this bundle

Re-run analysis on modified commands in this bundle.

Track verification: `bundle_issues_resolved`, `bundle_issues_remaining`, `bundle_new_issues`

**Display bundle verification results:**
```
==================================================
Bundle {bundle_name} - Fixes Verified
==================================================

✅ {issues_resolved} issues resolved
{if issues_remaining > 0}
⚠️ {issues_remaining} issues remain
{endif}
```

**Step 5j: Repeat for Next Bundle**

**CRITICAL**: Return to Step 5 for the next bundle in sorted order.

Only proceed to Step 6 when ALL bundles have been processed (analysis + fixes).

### Step 6: Generate Overall Summary Report

**Execute ONLY after all bundles have been processed.**

**Aggregate cross-bundle metrics:**
- Total commands analyzed across all bundles
- Total issues found/resolved across all bundles
- Total bloated commands across all bundles
- Bundle-by-bundle breakdown
- Overall quality metrics

**Display final summary:**
```
==================================================
Commands Doctor - All Bundles Complete
==================================================

Bundles Processed: {total_bundles}
Total Commands: {total_commands}

Overall Statistics:
- Acceptable size: {count} ✅
- Large: {count} ⚠️
- Bloated: {count} ❌

Total Issues:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}

Fixes Applied:
- Safe fixes: {count}
- Risky fixes: {count}
- Reference fixes: {count}
- Issues resolved: {count}

By Bundle:
- cui-plugin-development-tools: {commands} commands | {bloated} bloated | {issues} issues | {fixes} fixed
- {bundle-2}: {commands} commands | {bloated} bloated | {issues} issues | {fixes} fixed
...

{if all clean}
✅ All commands across all bundles are well-structured!
{endif}
```

**If --save-report flag is set:**
- Write complete cross-bundle report to `commands-diagnosis-report.md`
- Inform user: "Report saved to: commands-diagnosis-report.md"


## ARCHITECTURE

This command is a bundle-by-bundle orchestrator designed to prevent token overload by processing marketplace resources sequentially by bundle.

**For detailed orchestration architecture, see:**
```
Skill: cui-plugin-development-tools:cui-marketplace-orchestration-patterns
```

**Key Architecture Characteristics:**
- **Bundle-by-bundle processing**: Process one bundle completely before moving to next
- **Bundle ordering**: cui-plugin-development-tools first, then alphabetically
- **Complete workflow per bundle**: Analysis → Reference validation → Categorize → Fix → Verify
- **Token-optimized**: Standards pre-loading, streamlined output, scoped processing
- **Parallel execution within bundle**: All commands for a bundle run in parallel
- **Sequential across bundles**: Next bundle only starts after previous is complete

**Processing Flow:**
1. Discover all bundles and sort (cui-plugin-development-tools first, then alphabetical)
2. For each bundle:
   - Analyze all commands in bundle (parallel)
   - Validate all references in bundle (parallel)
   - Aggregate bundle results
   - Generate bundle report
   - Handle reference issues for bundle
   - Categorize issues for bundle
   - Apply safe fixes for bundle
   - Prompt for risky fixes for bundle
   - Verify fixes for bundle
3. Generate overall cross-bundle summary

**All analysis logic is in specialized agents:**
- diagnose-command (comprehensive command analysis with streamlined output support)
- analyze-plugin-references (plugin reference validation)

## TOOL USAGE

- **SlashCommand**: Execute /plugin-inventory --json (marketplace discovery with complete inventory)
- **Glob**: Discover commands in global/project scopes (non-prompting)
- **Skill**: Load diagnostic patterns, marketplace architecture, and fix workflow patterns
- **Task**: Launch diagnose-command and analyze-plugin-references agents (parallel within bundle)
- **Edit**: Apply safe and approved risky fixes
- **AskUserQuestion**: Prompt for risky fix approval and reference issue handling per bundle

## RELATED

- `/plugin-update-command` - Apply fixes to commands
- `/plugin-diagnose-agents` - Diagnose agents
- `/plugin-diagnose-skills` - Diagnose skills
- `/plugin-diagnose-bundle` - Diagnose entire bundle
- `/plugin-create-skill` - Extract bloated content to skills

## STANDARDS

Command analysis follows standards from the cui-marketplace-architecture skill:
- Command quality standards
- Command analysis patterns
- 8 anti-bloat rules (CRITICAL for preventing bloat)

**Architecture Compliance**: Standards are loaded via skill activation in Step 1, following proper marketplace architecture patterns.
