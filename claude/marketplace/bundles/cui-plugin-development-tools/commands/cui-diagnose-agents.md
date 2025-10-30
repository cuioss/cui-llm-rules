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

**If no parameters (interactive mode):**
- Display numbered list of all agents found
- Separate standalone and bundle agents
- Let user select which to analyze or change scope

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

## FIXING ISSUES

This command currently REPORTS issues only. To fix:

1. Review recommendations in report
2. Manually edit affected files
3. Re-run cui-diagnose-agents to verify fixes

**Future enhancement**: Auto-fix capability with user approval.

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

- `/cui-diagnose-commands` - Diagnose commands
- `/cui-diagnose-skills` - Diagnose skills
- `/cui-diagnose-bundle` - Diagnose entire bundle

## STANDARDS

Agent analysis follows:
- Agent quality standards (bundles/cui-plugin-development-tools/standards/agent-quality-standards.md)
- Agent analysis patterns (bundles/cui-plugin-development-tools/standards/agent-analysis-patterns.md)

Standards are loaded automatically by cui-diagnose-single-agent.
