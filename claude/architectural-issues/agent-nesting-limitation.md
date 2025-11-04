# Agent Nesting Limitation in Claude Code

**Date**: 2025-11-04
**Status**: CONFIRMED PLATFORM LIMITATION
**Severity**: HIGH - Breaks hierarchical agent workflows

## Problem Statement

Sub-agents in Claude Code **cannot spawn other sub-agents** using the Task tool, despite the tool being explicitly declared in agent configuration frontmatter. This prevents hierarchical agent delegation patterns from functioning.

## Root Cause

The Claude Code platform intentionally restricts the Task tool from being available to sub-agents at runtime to prevent infinite nesting and control resource consumption.

**Configuration vs Runtime Mismatch:**
```yaml
# Agent configuration declares:
tools: Read, Edit, Write, Grep, Skill, Task

# Runtime provides:
tools: Read, Edit, Write, Grep, Skill
# Task is MISSING
```

## Evidence Sources

**Official Documentation**: https://docs.claude.com/en/docs/claude-code/sub-agents
> "Subagents cannot spawn other subagents" - preventing infinite nesting

**GitHub Issues** (all closed as known limitation):
- #4182: "Sub-Agent Task Tool Not Exposed When Launching Nested Agents"
- #5528: "Sub-agent delegation pattern unusable for hierarchical task decomposition"
- #4799: "Tool specifications completely ignored by sub-agents"

**Real-World Validation**: User test in #5528 confirmed agents configured with `tools: Task` report "I don't have access to a 'Task' tool" at runtime.

## Impact on CUI Architecture

**Broken Pattern**: `/cui-build-and-verify` → `maven-project-builder` (agent) → `maven-builder` (agent) ❌

**Current Failure**: `maven-project-builder.md` declares `tools: Task` but runtime doesn't provide it, causing delegation to fail.

**Affected**: `cui-maven/agents/maven-project-builder.md`, `cui-maven/commands/cui-build-and-verify.md`, any hierarchical workflows

## Why Workarounds Fail

**Attempted workaround**: `claude -p` via Bash spawns separate instances
- ❌ No visibility, complex error handling, no context sharing, causes crashes
- **Not recommended** by community

## Solution: Hybrid Command and Agent Architecture

Use BOTH command-to-command orchestration AND command-to-agent delegation appropriately:

### Pattern 1: Commands Orchestrate Commands
For high-level workflows that compose multiple logical operations:

```
/cui-build-and-verify (command)
  ↓ Main Claude executes (has SlashCommand tool)
  ├─> SlashCommand("/cui-maven-build") - reusable build command
  └─> SlashCommand("/cui-commit-changes") - reusable commit command
```

**Use when**: Composing reusable operations, each valuable as standalone command

### Pattern 2: Commands Delegate to Agents (Single Level)
For focused tasks requiring autonomous execution in isolated context:

```
/cui-maven-build (command)
  ↓ Main Claude executes (has Task tool)
  └─> Task(maven-builder) - focused build execution agent
```

**Use when**: Task benefits from separate context window, specialized tools, or focused system prompt

### Combined Architecture Example
```
/cui-build-and-verify (orchestration command)
  ├─> SlashCommand("/cui-maven-build")
  │    └─> Task(maven-builder agent) - builds with output capture
  ├─> Main Claude analyzes output and fixes issues
  └─> SlashCommand("/cui-commit-changes")
       └─> Task(commit-changes agent) - commits and pushes
```

### Critical Rules
- ✅ Commands CAN invoke other commands (via SlashCommand tool)
- ✅ Commands CAN invoke agents (via Task tool)
- ❌ Agents CANNOT invoke other agents (Task tool unavailable)
- ✅ Agents CAN use all other tools (Read, Write, Edit, Bash, etc.)

## References

- Official docs: https://docs.claude.com/en/docs/claude-code/sub-agents
- GitHub #4182: https://github.com/anthropics/claude-code/issues/4182
- GitHub #5528: https://github.com/anthropics/claude-code/issues/5528
