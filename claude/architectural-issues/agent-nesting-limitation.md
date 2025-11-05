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

Use BOTH command-to-command orchestration AND command-to-agent delegation appropriately.

The **migration-plan.md** document defines three operational patterns for implementing this architecture:

### Pattern 1: Self-Contained Command (Single Operation)
For single, focused operations (implement, test, analyze, build):
- Command orchestrates: focused agent → verification agent → iterate → return result
- Examples: `/java-implement-code`, `/java-implement-tests`, `/java-coverage-report`, `/execute-task`

### Pattern 2: Three-Layer Design (Batch Operations)
For batch/collection operations (multiple independent items):
- **Layer 1** (Batch Command): Collects items, delegates to Layer 2 per item
- **Layer 2** (Self-Contained Command): Pattern 1 for single item
- **Layer 3** (Focused Agents): Execute specific tasks only
- Examples: `/review-technical-docs` → `/review-single-asciidoc` → validator agents

### Pattern 3: Fetch + Triage + Delegate (Smart Orchestration)
For complex orchestration requiring analysis before action:
- Command: Fetcher agent → For each: Triager agent → Delegate based on triage → Verify
- Used when items need analysis before deciding action (fix vs suppress, code change vs explanation)
- Examples: `/fix-sonar-issues`, `/respond-to-review-comments`

See **migration-plan.md** for detailed workflow examples, concrete implementations, and complete migration tasks.

### Critical Rules
- ✅ Commands CAN invoke other commands (via SlashCommand tool)
- ✅ Commands CAN invoke agents (via Task tool)
- ❌ Agents CANNOT invoke other agents (Task tool unavailable)
- ❌ Agents CANNOT invoke commands (SlashCommand tool unavailable)
- ✅ Agents CAN use all other tools (Read, Write, Edit, Bash, Grep, Glob, Skill, etc.)
- 📋 Flow is unidirectional: command → command OR command → agent (NEVER agent → *)

## References

- Official docs: https://docs.claude.com/en/docs/claude-code/sub-agents
- GitHub #4182: https://github.com/anthropics/claude-code/issues/4182
- GitHub #5528: https://github.com/anthropics/claude-code/issues/5528
