---
name: cui-diagnose-agents
description: Analyze, verify, and fix agents for tool coverage, best practices, and structural issues
---

# Agents Doctor - Verify and Fix Agents

Analyze, verify, and fix agents for tool coverage, best practices, and structural issues.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace agents (standalone + bundle agents)
- **scope=global**: Analyze agents in global location (~/.claude/agents/)
- **scope=project**: Analyze agents in project location (.claude/agents/)
- **agent-name** (optional): Review a specific agent by name (e.g., `maven-project-builder`)
- **No parameters**: Interactive mode with marketplace default

## PARAMETER VALIDATION

**If `scope=marketplace` (default):**
- Process all `.md` files in two locations:
  - Standalone: `~/git/cui-llm-rules/claude/marketplace/agents/`
  - Bundle agents: `~/git/cui-llm-rules/claude/marketplace/bundles/*/agents/`

**If `scope=global`:**
- Process all `.md` files in `~/.claude/agents/`

**If `scope=project`:**
- Process all `.md` files in `.claude/agents/`
- Skip if directory doesn't exist

**If specific agent name provided:**
- Search based on current scope parameter
- If no scope specified, search marketplace first, then global, then project

**If no parameters provided:**
- Display interactive menu with numbered list of all agents
- Let user select which agent(s) to review or change scope

## TOOL USAGE REQUIREMENTS

**CRITICAL**: This command must use non-prompting tools to avoid user interruptions during diagnosis.

### Activate Diagnostic Patterns Skill

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

This loads all tool usage patterns for non-prompting file operations.

### Required Tool Usage Patterns

✅ **File Discovery**: Use `Glob` tool (never `find` via Bash)
✅ **Existence Checks**: Use `Read` + try/except or `Glob` (never `test -f`/`test -d` via Bash)
✅ **Content Search**: Use `Grep` tool (never `grep`/`awk` via Bash)
✅ **File Reading**: Use `Read` tool (never `cat` via Bash)

**Why**: Bash commands trigger user prompts which interrupt the diagnostic flow.

## WORKFLOW INSTRUCTIONS

### Overview

The agents doctor performs comprehensive analysis in these phases:

1. **Discover** - Find all agents in specified scope
2. **Analyze** - Run validation checks on each agent
3. **Fix** - Apply automated fixes (if user approves)
4. **Report** - Generate comprehensive summary

### Load Analysis Standards

Before starting analysis, load the quality standards skill:

```
Skill: cui-plugin-development-tools:cui-skill-quality-standards
```

This skill provides:
- Agent quality standards (9 best practices)
- 20 common issue patterns (Pattern 1-20)
- Tool coverage analysis formulas
- Quality scoring criteria
- Fix patterns and strategies

### Step 1: Determine Scope and Discover Agents

**A. Parse Parameters**

Determine what to process based on scope parameter:
1. If `scope=marketplace` (default) → Search both standalone and bundle agents
2. If `scope=global` → Search `~/.claude/agents/`
3. If `scope=project` → Search `.claude/agents/`
4. If agent name provided → Search in current scope only
5. If no parameters → Interactive mode with marketplace default

**B. Discover Agents**

Use Glob to discover agent files:

```
# For marketplace scope (default)
standalone_agents = Glob(pattern="*.md", path="~/git/cui-llm-rules/claude/marketplace/agents")
bundle_agent_dirs = Glob(pattern="*/agents", path="~/git/cui-llm-rules/claude/marketplace/bundles")

# Combine and sort
marketplace_agents = standalone_agents + bundle_agents
marketplace_agents.sort()
```

**C. Interactive Mode (if no parameters)**

Display menu with all discovered agents:
```
Available Agents (scope=marketplace):

STANDALONE AGENTS:
1. research-best-practices
2. asciidoc-reviewer
...

BUNDLE AGENTS:
7. maven-project-builder (cui-maven bundle)
8. task-executor (cui-issue-implementation bundle)
...

Options: Enter number, "all", "scope=X", or "quit"
```

### Step 2: Read Architectural Principles

**CRITICAL**: Load agent architecture principles:

```
Read: ~/git/cui-llm-rules/claude/agents-architecture.md
```

Extract verification criteria:
- Best Practices for Well-Formed Agents
- Tool Coverage Analysis guidelines
- Essential Rules format specification
- Tool Fit Score calculation formula
- Response Format requirements

### Step 3: Initialize Analysis Statistics

Create tracking variables for reporting:
- `total_agents`, `agents_with_issues`, `agents_fixed`
- `total_issues`, `issues_fixed`
- `critical_issues`, `warnings`
- `tool_coverage_issues`
- `rules_out_of_date`, `rules_orphaned`
- `duplication_issues`, `ambiguity_issues`, `precision_issues`
- `permission_issues`

### Step 4: Analyze Each Agent

For EACH agent file, execute comprehensive analysis:

#### Step 4.1: Display Agent Header

```
==================================================
Analyzing: <agent-name>
Location: <file-path>
==================================================
```

#### Step 4.2-4.13: Run Validation Checks

Apply all validation checks from standards (in order):

**Structural Validation:**
- Read and parse agent (frontmatter + body)
- Validate YAML frontmatter (Pattern 3, 4)
- Check agent length and complexity (Pattern 17)

**Tool Coverage Analysis:**
- Extract tools from frontmatter
- Parse workflow for actual tool usage
- Calculate Tool Fit Score (Pattern 1, 2, 16)
- Identify missing/unused tools

**Structural Analysis:**
- Check for task description (Pattern 19)
- Verify workflow presence
- Check response format (Pattern 15)

**Best Practices Compliance:**
- Tool best practices
- Autonomy best practices
- Communication best practices
- Scope best practices
- Maven/Build context (Pattern 6)

**Essential Rules Synchronization:**
- Verify format (Pattern 7)
- Check sync status (Pattern 8)
- Detect orphaned rules
- Validate source references

**Architecture Compliance:**
- Check self-containment
- Detect absolute paths (Pattern 5)
- Validate portable paths

**Content Quality:**
- Internal duplication analysis (Pattern 11)
- Ambiguity detection (Pattern 10)
- Precision analysis
- Calculate precision score

**Industry Best Practices:**
- 9-point checklist compliance
- Calculate compliance score

**Permission Patterns:**
- Verify Bash permissions (Pattern 9)
- Detect missing approvals
- Find over-permissions (Pattern 20)
- Identify stale patterns

**Documentation Noise:**
- Detect broken external links (Pattern 18)
- Find documentation-only sections

### Step 5: Generate Issue Report

For each agent, categorize all issues found:

**CRITICAL Issues (Must Fix):**
- Missing critical tools (Pattern 1)
- Invalid YAML (Pattern 3)
- Absolute paths (Pattern 5)
- Orphaned rules (Pattern 7)
- Permission violations (Pattern 9)
- Missing description (Pattern 12)

**Warnings (Should Fix):**
- Over-permission (Pattern 2)
- Wrong tool field (Pattern 4)
- Temp directory violation (Pattern 6)
- Out-of-date rules (Pattern 8)
- Ambiguous instructions (Pattern 10)
- Internal duplication (Pattern 11)
- Description too long (Pattern 13)
- Low tool coverage score (Pattern 16)
- Documentation noise (Pattern 18)
- Stale permission patterns (Pattern 20)

**Suggestions (Nice to Have):**
- Inconsistent naming (Pattern 14)
- Missing response format (Pattern 15)
- Agent too complex (Pattern 17)
- Missing task description (Pattern 19)

Display categorized report:
```
Issue Report for <agent-name>:

CRITICAL (X issues):
1. [Description]
   Impact: [Impact]
   Fix: [Fix strategy]

WARNINGS (X issues):
...

SUGGESTIONS (X items):
...

Total: X issues found
Tool Fit Score: X/100
Precision Score: X/100
Compliance Score: X/100
```

### Step 6: Fix Issues (If User Approves)

**Decision Point:**
```
Found <count> issues in <agent-name>:
- Critical: <count>
- Warnings: <count>
- Suggestions: <count>

Options:
F - Fix all issues automatically
R - Review each issue individually before fixing
S - Skip this agent (do not fix)
Q - Quit analysis entirely

Please choose [F/r/s/q]:
```

**Auto-Fix Behavior:**
- YAML issues → Add/fix frontmatter structure
- Tool issues → Add missing tools, remove unused tools
- Path issues → Convert absolute to relative
- Permission issues → Add missing patterns, remove stale patterns
- Rules issues → Sync from source, add attribution
- Documentation noise → Remove sections with only broken links

**After Fixing:**
- Re-run analysis to verify fixes
- Compare before/after
- Update statistics
- Offer revert if new issues introduced

### Step 7: Generate Final Report

After processing all agents, display comprehensive summary:

```
==================================================
Agents Doctor - Analysis Complete
==================================================

Agents Analyzed: <total_agents>
- With issues: <agents_with_issues>
- Fixed: <agents_fixed>
- Still have issues: <remaining>

Issue Statistics:
- Total issues found: <total_issues>
- Critical: <critical_count>
- Warnings: <warning_count>
- Suggestions: <suggestion_count>
- Issues fixed: <issues_fixed>

Issue Breakdown by Category:
- Tool coverage issues: <tool_coverage_issues>
- Essential rules issues: <rules_out_of_date + rules_orphaned>
- Duplication issues: <duplication_issues>
- Ambiguity issues: <ambiguity_issues>
- Permission issues: <permission_issues>

Quality Scores:
- Average Tool Fit: <avg_tool_fit>/100
- Average Precision: <avg_precision>/100
- Average Compliance: <avg_compliance>/100

By Agent:
<for each agent analyzed>
- <agent-name>: <issue_count> issues (<critical>C / <warnings>W / <suggestions>S)
  Status: <Clean/Warnings/Critical>
  Tool Fit: <score>/100 | Precision: <score>/100 | Compliance: <score>/100
</for each>

Recommendations:
<if critical issues remain>
⚠️  CRITICAL: <count> agents still have critical issues
- <agent-1>: <issue>
Re-run diagnose-agents on these agents to fix.
</if>

<if quality issues>
⚠️  QUALITY: <count> agents have quality concerns
- Low tool fit: <list>
- Low precision: <list>
- Low compliance: <list>
</if>

<if all clean>
✅ All analyzed agents are well-formed and follow best practices!
</if>
```

## CRITICAL RULES

- **READ ENTIRE AGENT** before analyzing - context is essential
- **USE NON-PROMPTING TOOLS** - Follow diagnostic patterns skill guidance
- **LOAD STANDARDS FIRST** - Read quality standards and architecture document
- **LOAD ARCHITECTURE DOCUMENT** - Read ~/git/cui-llm-rules/claude/agents-architecture.md for verification criteria
- **CATEGORIZE ISSUES PROPERLY** - Critical vs Warning vs Suggestion based on loaded patterns
- **EXPLAIN FIXES CLEARLY** - User should understand why each change is made
- **VERIFY AFTER FIXING** - Always re-analyze to ensure fixes worked
- **PRESERVE INTENT** - Fix structure/consistency but preserve agent's purpose
- **USE EDIT TOOL** - Never rewrite entire files, use targeted edits
- **TRACK STATISTICS** - Maintain counters throughout analysis for final report
- **HANDLE ERRORS** - If agent file is malformed/unreadable, report and skip
- **INTERACTIVE BY DEFAULT** - Ask before making changes unless told otherwise
- **CALCULATE SCORES** - Tool Fit, Precision, and Compliance scores for each agent

## STANDARDS REFERENCED

This command relies on the skill quality standards skill and architecture document:

**Skill: cui-plugin-development-tools:cui-skill-quality-standards**

This skill provides:
- Agent quality standards (9 best practices)
- 20 common agent issue patterns
- Quality scoring criteria
- Fix strategies

**Architecture Document: ~/git/cui-llm-rules/claude/agents-architecture.md**

This document provides:
- Single source of truth for agent architecture
- Best practices verification criteria
- Tool coverage analysis guidelines
- Essential Rules format specification

Load both at the beginning of execution to guide analysis and fixes.

## RELATED DOCUMENTATION

See agents-architecture.md for:
- Agent architecture principles
- Best practices details
- Tool coverage requirements
- Essential Rules specification
