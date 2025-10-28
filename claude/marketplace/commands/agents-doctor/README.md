# agents-doctor

Comprehensive analysis and verification tool for agents, ensuring they follow architectural best practices, have correct tool coverage, and maintain up-to-date standards.

## Purpose

Analyzes agents for structural issues, tool configuration problems, and compliance with agent design principles. Automatically fixes common problems and synchronizes embedded rules with source standards.

## Usage

```bash
# Analyze specific agent
/agents-doctor project-builder

# Analyze all project agents
/agents-doctor project

# Analyze all global agents
/agents-doctor global

# Interactive mode
/agents-doctor
```

## What It Does

The agents-doctor command performs comprehensive analysis across multiple dimensions:

### 1. Tool Coverage Analysis (Critical)

- Scans agent workflow to detect required tools
- Compares required tools vs configured tools in frontmatter
- Identifies missing tools (will cause approval requests)
- Identifies unnecessary tools (security bloat)
- Calculates Tool Fit Score (target: 100%)

### 2. Structural Analysis

- Validates YAML frontmatter (name, description, tools, model, color)
- Checks description quality and usage examples
- Verifies workflow structure (steps, decision points, error handling)
- Detects anti-patterns (self-modification, continuous improvement)
- Validates response format templates

### 3. Essential Rules Synchronization

- Compares embedded rules with source standards files
- Detects out-of-date rules (content changed in source)
- Detects orphaned rules (source file missing)
- Detects old syncs (>30 days since last update)
- Offers to automatically sync rules from sources

### 4. Best Practices Compliance

- Tool usage patterns (Read before Edit, minimal tool set)
- Autonomy (no permission gates blocking workflow)
- Communication (structured output, progress updates)
- Scope (single responsibility, clear boundaries)
- Build context (use target/ not /tmp/)

### 5. Quality Metrics

- **Duplication Analysis**: Detect duplicate instructions
- **Ambiguity Detection**: Flag vague language
- **Precision Analysis**: Measure instruction specificity
- **Industry Compliance**: Verify against authoritative best practices

### 6. Permission Pattern Verification

- Extracts bash commands from agent workflow
- Delegates to `/setup-project-permissions` for verification
- Reports missing approvals, over-permissions, and security risks
- Calculates Permission Fit Score

## Key Metrics

- **Tool Fit Score**: Percentage match between required and configured tools (target: 100%)
- **Precision Score**: Instruction specificity measurement (90-100% excellent)
- **Compliance Score**: Industry best practices adherence (100% ideal)
- **Permission Fit**: Bash command approval alignment (100% perfect)

## Auto-Fix Capabilities

The command can automatically fix:
- Add missing required tools to frontmatter
- Remove unnecessary tools
- Replace hardcoded absolute paths with user-relative paths
- Update out-of-date embedded rules from sources
- Remove orphaned rule references
- Fix tool configuration errors

## Issue Categories

**CRITICAL** (must fix):
- Missing required tools → Agent will fail or request approval
- Broken workflow logic → Agent cannot complete task
- Self-modification references → Wrong agent pattern
- Over-permissions → Security risks

**WARNINGS** (should fix):
- Unnecessary tools → Bloat, security surface
- Missing error handling → Fragile execution
- Poor description → Unclear usage
- Old embedded rules → May enforce outdated standards

**SUGGESTIONS** (nice to have):
- Add lessons learned reporting
- Enhance progress updates
- Improve documentation

## Repository Context

This is a **repository-specific utility** designed for the `cui-llm-rules` repository. It references:
- `~/git/cui-llm-rules/claude/agents-architecture.md` for verification criteria
- Analysis modules in `~/git/cui-llm-rules/claude/agents/agents-doctor/` directory

## Analysis Modules

The command delegates specialized analysis to separate modules:
- `duplication-analysis.md`: Detect duplicate content
- `ambiguity-detection.md`: Flag vague language
- `precision-analysis.md`: Measure instruction specificity
- `compliance-checking.md`: Verify industry best practices

## Parameters

- **project**: Analyze all agents in `.claude/agents/`
- **global**: Analyze all agents in `~/.claude/agents/`
- **agent-name**: Analyze specific agent by name
- **no parameters**: Interactive mode with menu selection

## Interactive Workflow

When issues are found, agents-doctor offers:
- **F** - Fix all issues automatically
- **R** - Review each issue individually before fixing
- **S** - Skip this agent (don't fix)
- **Q** - Quit analysis entirely

For Essential Rules synchronization:
- **U** - Update all out-of-date rules from sources
- **R** - Review changes and update selectively
- **V** - View detailed diff for each rule set
- **S** - Skip synchronization

## Example Output

```
==================================================
Analyzing: project-builder
Location: ~/.claude/agents/project-builder.md
==================================================

Agent Overview:
- Name: project-builder
- Model: sonnet
- Tools: Read, Edit, Write, Bash, Grep
- Length: 456 lines
- Complexity: Medium

Tool Coverage Analysis:
✅ Read - Required and configured
✅ Edit - Required and configured
✅ Write - Required and configured
✅ Bash - Required and configured
⚠️  Grep - Configured but not used (unnecessary)

Tool Fit Score: 90% (Good fit)

Essential Rules: 2 out of date, 0 orphaned

Found 3 issues:
- Critical: 0
- Warnings: 3

Options: [F/r/s/q]:
```

## Integration

Run agents-doctor:
- After creating new agents (via `/agents-create`)
- After significant agent updates
- When agents unexpectedly request user approvals
- As part of regular project maintenance
- Before deploying agents to production

Often used with:
- `/agents-create` - Create agents following best practices
- `/setup-project-permissions` - Manage bash command approvals
- `/slash-doctor` - Similar verification for slash commands

## Notes

- Analyzes agent **structure** and **configuration**, not functionality
- Use Tool Fit Score as primary health metric (target: 100%)
- Essential Rules sync keeps agents aligned with latest standards
- Permission verification prevents approval interruptions
- Always backup agents before auto-fixing (git tracking recommended)
- Re-run after fixes to verify no new issues introduced

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
