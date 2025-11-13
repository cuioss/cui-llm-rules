---
name: plugin-diagnose-agents
description: Analyze, verify, and fix agents for tool coverage, best practices, and structural issues
---

# Agents Doctor - Verify and Fix Agents

Orchestrates comprehensive analysis of agents by coordinating diagnose-agent for each agent.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-diagnose-agents update="[your improvement]"` with:
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
Skill: cui-utilities:cui-diagnostic-patterns
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
- If Glob fails: Display error with path and suggestions, exit with error status
- If no agents found: Display scopes searched and suggest trying different scope, exit gracefully

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
- If Task fails: Display warning with agent name and error, mark as "Analysis Failed", continue with remaining
- If malformed response: Display warning, mark as "Malformed Response", continue
- If timeout: Display warning, mark as "Timeout", continue
- If partial success: Include successful analyses, add "Failed Analyses" section, report partial metrics

### Step 4: Check Plugin References

**For EACH agent discovered:**

Launch analyze-plugin-references agent to validate cross-references:

```
Task:
  subagent_type: analyze-plugin-references
  description: Check references in {agent-name}
  prompt: |
    Check all plugin references in this agent.

    Parameters:
    - path: {absolute_path_to_agent}
    - auto-fix: true

    Return summary report with reference validation results.
```

**CRITICAL**: Launch ALL reference checks in PARALLEL (single message, multiple Task calls).

**Collect reference analysis results** from each agent as they complete.

**Error Handling:**
- If Task fails: Display warning with agent name and error, mark as "Reference Check Failed", continue
- If unexpected format: Display warning, mark as "Reference Check Error", continue

**Aggregate reference findings:**
Track for each agent: references_found, references_correct, references_fixed, references_ambiguous.
Aggregate totals: agents_checked, total_references, correct, fixed, issues.

### Step 5: Aggregate Results

**Combine findings from all agents (diagnosis + reference checks):**

Track key metrics: total_agents_analyzed, agents_with_issues, issue counts (critical/warnings/suggestions), reference stats (total/correct/fixed/issues).
Per-agent data: status, issues, scores (tool_fit/precision/compliance), reference counts.
Overall metrics: average scores, agent quality distribution (excellent/good/fair/poor).

### Step 6: Generate Summary Report

**Display summary report with:**
- Header: "Agents Doctor - Analysis Complete"
- Agent counts by status (clean/warnings/critical)
- Issue statistics (critical/warnings/suggestions totals)
- Quality scores (avg tool_fit, precision, compliance)
- Reference validation stats (total/correct/fixed/issues)
- Per-agent summary line: status, scores, reference counts
- Recommendations: critical issues requiring attention, reference issues with details, or success message if all clean

**If --save-report flag is set:**
- Write the complete report above to `agents-diagnosis-report.md` in project root
- Inform user: "Report saved to: agents-diagnosis-report.md"

**Default behavior (no flag):**
- Display report only (as shown above)
- Do NOT create any files

**Error Handling for Report Writing:**
- If file write fails: Display error with message and possible causes, note report was displayed, continue
- If path doesn't exist: Display error with current directory, note report was displayed, continue

### Step 7: Categorize Issues for Fixing

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

### Step 8: Apply Safe Fixes

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

### Step 9: Prompt for Risky Fixes

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
- Consider suggesting use of `/plugin-update-agent` for complex refactoring

**Track risky fixes:**
```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "risky_fixes_deferred_to_update_agent": {count}
}
```

### Step 10: Verify Fixes

**When to execute**: After any fixes applied (Step 8 or Step 9)

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
⚠️ {issues_remaining} issues remain (require manual intervention or /plugin-update-agent)
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

- `/plugin-update-agent` - Apply fixes to agents
- `/plugin-diagnose-commands` - Diagnose commands
- `/plugin-diagnose-skills` - Diagnose skills
- `/plugin-diagnose-bundle` - Diagnose entire bundle

## STANDARDS

Agent analysis follows:
- Agent quality standards (bundles/cui-plugin-development-tools/standards/agent-quality-standards.md)
- Agent analysis patterns (bundles/cui-plugin-development-tools/standards/agent-analysis-patterns.md)

Standards are loaded automatically by diagnose-agent.
