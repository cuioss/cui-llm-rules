# create-agent

Interactive wizard for creating well-structured agents that follow CUI architectural best practices.

## Purpose

Guides users through a step-by-step process to create new agents with proper structure, tool configuration, essential rules embedding, and compliance with agent architecture standards.

## Usage

```bash
/create-agent
```

The wizard will interactively ask you questions and generate a compliant agent file.

## What It Does

The wizard collects information about:

1. **Agent Location** - Global (`~/.claude/agents/`) or project-specific (`.claude/agents/`)
2. **Basic Information** - Name, purpose, invocation examples
3. **Required Tools** - Automatic tool detection based on workflow description
4. **Essential Rules** - Standards to embed inline for fast execution
5. **Response Format** - Metrics to track and report
6. **Detailed Workflow** - Step-by-step execution plan
7. **Critical Constraints** - Absolute rules and limitations

The wizard then:
- Generates a properly structured agent file
- Validates 100% Tool Fit
- Embeds essential rules inline
- Includes tool usage tracking
- Adds lessons learned reporting
- Auto-verifies with `/diagnose-agents`

## Key Features

- **Interactive Guidance** - Step-by-step wizard interface
- **Automatic Tool Detection** - Analyzes workflow to suggest required tools
- **Architecture Compliance** - Follows patterns from `agents-architecture.md`
- **Validation** - Ensures name uniqueness, tool fit, and structural correctness
- **Auto-Verification** - Runs `/diagnose-agents` after creation
- **Best Practices** - Applies industry standards for clarity and precision

## Generated Agent Structure

Created agents include:

```markdown
---
name: agent-name
description: Purpose and examples
tools: Read, Edit, Bash
model: sonnet
color: green
---

# Agent Title

## YOUR TASK
...

## ESSENTIAL RULES
...

## WORKFLOW (FOLLOW EXACTLY)
...

## CRITICAL RULES
...

## TOOL USAGE TRACKING
...

## LESSONS LEARNED REPORTING
...

## RESPONSE FORMAT
...
```

## Requirements

- Agents must achieve 100% Tool Fit (all declared tools are used)
- Essential rules must be embedded inline (no external reads during execution)
- Response format must be structured and parseable
- Tool usage must be tracked and reported
- Lessons learned reporting (not self-modification)

## Repository Context

This is a **repository-specific utility** designed for the `cui-llm-rules` repository. It references:
- `~/git/cui-llm-rules/claude/agents-architecture.md` for architectural patterns

## Examples

### Create a Global Agent

```bash
/create-agent
> Where should the agent be located?
> 1. Global agent (~/.claude/agents/)
1

> What is the agent name?
code-reviewer

> What is the agent's primary purpose?
Reviews code for quality, standards compliance, and best practices

...wizard continues...
```

### Create a Project-Specific Agent

```bash
/create-agent
> Where should the agent be located?
> 2. Project agent (.claude/agents/)
2

> What is the agent name?
custom-validator

...wizard continues...
```

## Validation

The wizard validates:
- Agent name format (lowercase, hyphens only)
- Uniqueness (no conflicts with existing agents)
- Tool fit (Edit requires Read, etc.)
- Essential rules structure (source + date + content)
- Industry best practices (no vague language, quantified thresholds)

After creation, `/diagnose-agents` automatically verifies:
- Tool Fit Score (target: 100%)
- Essential Rules sync status
- Internal quality (duplication, ambiguity)
- Compliance with architectural standards

## Notes

- All created agents follow the **Essential Rules Pattern** (embed + sync)
- Agents are **self-contained** (no external file reads during execution)
- Agents use **Lessons Learned Reporting** (not Continuous Improvement)
- Response format is **structured and parseable**
- Tool usage is **tracked and reported**

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
