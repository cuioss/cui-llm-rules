---
name: cui-diagnose-agents
description: Analyze, verify, and fix agents for tool coverage, best practices, and structural issues
---

# Agents Doctor - Verify and Fix Agents

Orchestrates comprehensive analysis of agents by coordinating diagnose-agent for each agent.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-diagnose-agents update="[your improvement]"` with:
1. Improved agent quality analysis patterns and tool fit detection
2. Better methods for identifying tool coverage gaps and precision issues
3. More effective compliance checking and structural validation approaches
4. Enhanced error handling and partial success detection in parallel analysis
5. Any lessons learned about agent design patterns and best practices

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace agents (standalone + bundle agents)
- **scope=global**: Analyze agents in global location (~/.claude/agents/)
- **scope=project**: Analyze agents in project location (.claude/agents/)
- **agent-name** (optional): Review a specific agent by name (e.g., `maven-project-builder`)
- **auto-fix** (optional, default: true): Automatically fix safe issues; prompt for risky fixes
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Interactive mode with marketplace default

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

This provides architecture rules and validation patterns for marketplace components that may be useful for understanding agent design principles.

### Step 2: Discover Agents

**Parse parameters** to determine scope.

**For marketplace scope (default):**
```
Glob: pattern="*.md", path="~/git/cui-llm-rules/claude/marketplace/agents"
Glob: pattern="*/agents/*.md", path="~/git/cui-llm-rules/claude/marketplace/bundles"
```

**For global scope:**
```
Glob: pattern="*.md", path="~/.claude/agents"
```

**For project scope:**
```
Glob: pattern="*.md", path=".claude/agents"
```

**Extract agent names** from file paths.

**If specific agent name provided:**
- Filter list to matching agent only
- If no match found: Display error and exit

**If no parameters (interactive mode):**
- Display numbered list of all agents found
- Separate standalone and bundle agents
- Let user select which to analyze or change scope

**Error Handling:**

- **If Glob fails (directory not found):**
  ```
  ❌ Error: Directory not found: {path}

  Suggestions:
  - Verify path exists
  - Check scope parameter (marketplace/global/project)
  - For marketplace: ensure ~/git/cui-llm-rules is correct
  ```
  Exit with error status.

- **If no agents found in scope:**
  ```
  ℹ️ No agents found in {scope} scope

  Scopes searched:
  - {list of directories checked}

  Try a different scope or create agents first.
  ```
  Exit gracefully.

### Step 3: Analyze Agents (Parallel)

**For EACH agent discovered:**

Launch diagnose-agent:

```
Task:
  subagent_type: diagnose-agent
  description: Analyze {agent-name}
  prompt: |
    Analyze this agent comprehensively.

    Parameters:
    - agent_path: {absolute_path_to_agent}

    Return complete JSON report with all issues found.
```

**CRITICAL**: Launch ALL agents in PARALLEL (single message, multiple Task calls).

**Collect results** from each agent as they complete.

**Error Handling:**

- **If Task fails to launch:**
  ```
  ⚠️ Failed to analyze: {agent-name}
  Error: {task_error_message}
  ```
  Continue with remaining agents. Mark this agent as "Analysis Failed" in report.

- **If agent returns malformed JSON:**
  ```
  ⚠️ Invalid response from: {agent-name}
  Expected: JSON report
  Received: {truncated_response}
  ```
  Mark agent as "Malformed Response" and continue.

- **If agent analysis times out:**
  ```
  ⚠️ Analysis timeout: {agent-name}
  ```
  Mark agent as "Timeout" and continue with remaining agents.

**Partial Success Handling:**

If some agents fail but others succeed:
- Include successful analyses in report
- Add "Failed Analyses" section listing agents that couldn't be analyzed
- Report partial metrics (based on successful analyses only)

### Step 4: Aggregate Results

**Combine findings from all agents:**

```json
{
  "total_agents_analyzed": {count},
  "agents_with_issues": {count},
  "issue_summary": {
    "critical": {total_count},
    "warnings": {total_count},
    "suggestions": {total_count}
  },
  "by_agent": {
    "agent-name-1": {
      "status": "Clean|Warnings|Critical",
      "issues": {...},
      "scores": {...}
    },
    ...
  },
  "overall_metrics": {
    "avg_tool_fit": {score},
    "avg_precision": {score},
    "avg_compliance": {score},
    "agents_excellent": {count},
    "agents_good": {count},
    "agents_fair": {count},
    "agents_poor": {count}
  }
}
```

### Step 5: Generate Summary Report

**Display:**

```
==================================================
Agents Doctor - Analysis Complete
==================================================

Agents Analyzed: {total}
- Clean: {count} ✅
- With warnings: {count} ⚠️
- With critical issues: {count} ❌

Issue Statistics:
- Critical: {count}
- Warnings: {count}
- Suggestions: {count}
- Total: {count}

Quality Scores:
- Average Tool Fit: {score}/100
- Average Precision: {score}/100
- Average Compliance: {score}/100

By Agent:
- {agent-1}: {status} | Tool Fit: {score} | Precision: {score} | Compliance: {score}
- {agent-2}: {status} | Tool Fit: {score} | Precision: {score} | Compliance: {score}
...

Recommendations:
{if critical issues}
⚠️ CRITICAL: {count} agents need immediate attention
- {agent-name}: {issue summary}
{endif}

{if all clean}
✅ All agents are well-formed and follow best practices!
{endif}
```

**If --save-report flag is set:**
- Write the complete report above to `agents-diagnosis-report.md` in project root
- Inform user: "Report saved to: agents-diagnosis-report.md"

**Default behavior (no flag):**
- Display report only (as shown above)
- Do NOT create any files

**Error Handling for Report Writing:**

- **If file write fails:**
  ```
  ❌ Failed to save report: agents-diagnosis-report.md
  Error: {error_message}

  Possible causes:
  - Insufficient permissions
  - Disk full
  - File locked by another process

  Report displayed above (not saved to file).
  ```
  Continue execution - report was already displayed.

- **If path doesn't exist:**
  ```
  ❌ Cannot save report: project root not found

  Current directory: {cwd}
  Expected: valid project directory

  Report displayed above (not saved to file).
  ```
  Continue execution with displayed report only.

### Step 6: Categorize Issues for Fixing

**Categorize all issues into Safe vs Risky:**

**Safe fixes** (auto-apply when auto-fix=true):
- YAML frontmatter syntax errors
- Missing YAML fields (add defaults: `description`)
- Remove unused tools from `allowed-tools` frontmatter
- Add missing tools to `allowed-tools` based on workflow usage
- Add missing CONTINUOUS IMPROVEMENT RULE template
- Formatting/whitespace normalization

**Risky fixes** (always prompt user):
- Task tool misuse resolution (requires architectural redesign)
- Maven anti-pattern fixes (requires workflow restructuring)
- Ambiguous instruction clarification (judgment call on intent)
- Tool coverage gaps requiring workflow changes
- Precision issues requiring scope reduction

### Step 7: Apply Safe Fixes

**When to execute**: If auto-fix=true (default) AND safe fixes exist

**For each safe fix:**

**YAML syntax errors:**
```
Edit: {agent-file}
- Fix YAML frontmatter syntax
- Add missing required fields with defaults
- Correct field name typos
```

**Tool declaration fixes:**
```
Edit: {agent-file}
- Remove unused tools from allowed-tools array
- Add missing tools found in workflow (Read, Glob, Grep, etc.)
- Ensure proper tool declaration format
```

**Add missing CONTINUOUS IMPROVEMENT RULE:**
```
Edit: {agent-file}
- Insert CONTINUOUS IMPROVEMENT RULE template after description
- Include agent-specific improvement areas
```

**Formatting normalization:**
```
Edit: {agent-file}
- Normalize whitespace and indentation
- Fix heading hierarchy
- Ensure proper markdown structure
```

**Track fixes applied:**
```json
{
  "safe_fixes_applied": {count},
  "by_type": {
    "yaml_fixes": {count},
    "tool_declaration_fixes": {count},
    "continuous_improvement_added": {count},
    "formatting_fixes": {count}
  }
}
```

### Step 8: Prompt for Risky Fixes

**When to execute**: If risky fixes exist (regardless of auto-fix setting)

**For each risky fix, prompt user:**

```
[PROMPT] Risky fix detected in {agent-name}:

Issue: {issue description}
Location: {file path and line number}
Proposed fix: {fix description}
Impact: {explanation of architectural/workflow changes needed}

Apply this fix? [Y]es / [N]o / [S]kip all remaining
```

**Handle responses:**
- **Yes**: Apply the fix using Edit tool (may require significant workflow changes)
- **No**: Skip this fix, continue to next
- **Skip all remaining**: Exit fixing phase, proceed to verification

**Note**: For complex fixes like Task tool misuse or Maven anti-patterns:
- Prompt should explain the architectural change required
- Consider suggesting use of `/cui-update-agent` for complex refactoring

**Track risky fixes:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "risky_fixes_deferred_to_update_agent": {count}
}
```

### Step 9: Verify Fixes

**When to execute**: After any fixes applied (Step 7 or Step 8)

**Re-run analysis** on modified agents:
```
Task:
  subagent_type: diagnose-agent
  description: Verify fixes for {agent-name}
  prompt: |
    Re-analyze this agent after fixes.

    Parameters:
    - agent_path: {absolute_path_to_agent}

    Return complete JSON report.
```

**Compare before/after:**
```json
{
  "verification": {
    "agents_fixed": {count},
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
⚠️ {issues_remaining} issues remain (require manual intervention or /cui-update-agent)
{endif}
{if new_issues > 0}
❌ {new_issues} NEW issues introduced (fixes need review!)
{endif}
```

## ARCHITECTURE

This command is a simple orchestrator:
- Discovers agents using Glob (non-prompting)
- Launches diagnose-agent in parallel
- Aggregates and reports results

All analysis logic is in the specialized agent:
- diagnose-agent (comprehensive agent analysis)

## TOOL USAGE

- **Glob**: Discover agents (non-prompting)
- **Task**: Launch diagnose-agent (parallel)
- **Skill**: Load diagnostic patterns

## RELATED

- `/cui-update-agent` - Apply fixes to agents
- `/cui-diagnose-commands` - Diagnose commands
- `/cui-diagnose-skills` - Diagnose skills
- `/cui-diagnose-bundle` - Diagnose entire bundle

## STANDARDS

Agent analysis follows:
- Agent quality standards (bundles/cui-plugin-development-tools/standards/agent-quality-standards.md)
- Agent analysis patterns (bundles/cui-plugin-development-tools/standards/agent-analysis-patterns.md)

Standards are loaded automatically by diagnose-agent.
