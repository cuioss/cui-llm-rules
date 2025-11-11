---
name: cui-diagnose-agents
description: Analyze, verify, and fix agents for tool coverage, best practices, and structural issues
---

# Agents Doctor - Verify and Fix Agents

Orchestrates comprehensive analysis of agents by coordinating cui-diagnose-single-agent for each agent.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace agents (standalone + bundle agents)
- **scope=global**: Analyze agents in global location (~/.claude/agents/)
- **scope=project**: Analyze agents in project location (.claude/agents/)
- **agent-name** (optional): Review a specific agent by name (e.g., `maven-project-builder`)
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

Launch cui-diagnose-single-agent:

```
Task:
  subagent_type: cui-diagnose-single-agent
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

## FIXING ISSUES

To fix reported issues:

1. **Review recommendations** in report
2. **Use `/cui-update-agent`** to apply fixes:
   ```
   /cui-update-agent agent-name={agent-name} update="{issue description}"
   ```
3. **Re-run diagnosis** to verify:
   ```
   /cui-diagnose-agents agent-name={agent-name}
   ```

**Example workflow:**
```
# 1. Diagnose agent
/cui-diagnose-agents agent-name=my-agent

# 2. Apply fix using update command
/cui-update-agent agent-name=my-agent update="Add error handling for tool failures"

# 3. Verify fix
/cui-diagnose-agents agent-name=my-agent
```

## ARCHITECTURE

This command is a simple orchestrator:
- Discovers agents using Glob (non-prompting)
- Launches cui-diagnose-single-agent in parallel
- Aggregates and reports results

All analysis logic is in the specialized agent:
- cui-diagnose-single-agent (comprehensive agent analysis)

## TOOL USAGE

- **Glob**: Discover agents (non-prompting)
- **Task**: Launch cui-diagnose-single-agent (parallel)
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

Standards are loaded automatically by cui-diagnose-single-agent.
