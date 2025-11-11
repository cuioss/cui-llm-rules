# Agent Design Principles

## Overview

Design principles and quality standards for Claude Code agents.

**Audience**: Agent creators and reviewers

**Related**: [Architecture](architecture-overview.md) · [Specifications](plugin-specifications.md)

## Core Principles

### 1. Standards via Skills

**Rule**: Agents load standards using the Skill tool, not direct file reads.

**Implementation**:

* Declare `Skill` in tools list
* Invoke `Skill: cui-skill-name` in workflow Step 0
* Skills are self-contained bundles that read their own standards
* Never use direct file references (`../../../../` or `~/git/`)

**Example**:
```yaml
tools: Read, Edit, Skill
```
```markdown
### Step 0: Activate Skills
Skill: cui-java-core
Skill: cui-javadoc
```

### 2. Perfect Tool Fit (100%)

**Rule**: Agent has exactly the tools it needs - no more, no less.

**Why**: Missing tools require user approval (breaks autonomy), extra tools mislead about capabilities.

**Enforcement**: `/cui-diagnose-agents` verifies tool coverage.

**Tool Dependencies**:

* `Edit` requires `Read`
* Standards usage requires `Skill`
* Git commands require `Bash`

### 3. No Self-Modification

**Rule**: Agents report lessons learned but never modify themselves.

**Why**: Agents invoked by system (not user), modifications require restart, creates race conditions.

**Implementation**: Include "Lessons Learned" in response format.

### 4. Structured Response Format

**Required elements**:

* Status: ✅ SUCCESS | ❌ FAILURE | ⚠️ PARTIAL
* Summary: 1-2 sentences
* Metrics: Quantified results
* Tool Usage: Count per tool
* Lessons Learned: Insights for improvement

## Agent Structure

### Frontmatter

```yaml
---
name: agent-name
description: When to use with examples
tools: Read, Edit, Write, Bash, Skill
model: sonnet
color: green|blue|purple
---
```

### Required Sections

```markdown
## YOUR TASK
{Clear, specific task definition}

## SKILLS USED
- **skill-name**: Description
  - Provides: {standards provided}
  - When activated: Step 0

## WORKFLOW (FOLLOW EXACTLY)

### Step 0: Activate Skills
Skill: cui-skill-name

### Step 1-N: Task Steps
{Numbered, specific instructions}

## RESPONSE FORMAT
{Structured output template with required elements}
```

## Agent vs Command

| Aspect | Command | Agent |
|--------|---------|-------|
| Invocation | User types `/command` | System via Task tool |
| Duration | Can be hours/days | < 30 minutes |
| Interaction | Frequent questions | Minimal (decisions only) |
| Self-modify | ✅ Continuous improvement | ❌ Lessons learned only |
| Standards | Direct file reads OK | Skills via Skill tool |
| Output | Flexible | Structured, parseable |

**Use Agent When**:

* Well-defined autonomous task
* No user interaction during execution
* Single-session completion
* Structured output needed

## Writing Quality Standards

### Clarity

* Quantify thresholds ("3 retries", not "several")
* Use concrete verbs ("validate", "parse", not "handle")
* Define explicit criteria ("exit code 0", not "succeeds")
* Enumerate all options in decision points

### Specificity

| ❌ Avoid | ✅ Use |
|---------|--------|
| "if needed" | "if error count > 0" |
| "appropriately" | "using format YYYY-MM-DD" |
| "handle errors" | "catch IOException, log, retry once" |
| "fairly short" | "3-5 sentences" or "< 200 words" |

### Error Handling

Define for each error type:

* Retry count (explicit number)
* Retry conditions (which errors)
* Backoff strategy (immediate, exponential, fixed)
* Final action after exhaustion

### Measurability

All conditions must be boolean-evaluable:

* ✅ "Retry up to 3 times"
* ❌ "Retry several times"
* ✅ "Success = exit code 0 AND no ERROR lines"
* ❌ "Success = build completes successfully"

## Validation

### Tool: /cui-diagnose-agents

**Checks**:

* ✅ Tool Fit Score = 100%
* ✅ Agents using standards invoke skills properly
* ✅ No direct file references
* ✅ No self-modification
* ✅ Valid frontmatter
* ✅ Structured response format

**Usage**:
```bash
/cui-diagnose-agents           # Marketplace agents
/cui-diagnose-agents global    # Global agents
/cui-diagnose-agents project   # Project agents
```

**Auto-fixes**:

* Adds/removes tools for 100% fit
* Adds Skill tool if missing
* Converts file refs to skill invocations

### Quality Checklist

Before creating agent:

* [ ] Clear, quantified instructions (no "appropriately", "if needed")
* [ ] All thresholds have explicit numbers
* [ ] Error handling defined per error type
* [ ] Success criteria are measurable
* [ ] SKILLS USED section documents required skills
* [ ] Step 0 activates skills via Skill tool
* [ ] Only required tools configured (including Skill if using standards)
* [ ] Structured response format defined
* [ ] Tool Fit Score = 100% (verify with `/cui-diagnose-agents`)

## Common Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct Pattern |
|----------------|-------------------|
| "Process files as needed" | "Process all .java files in src/main/java" |
| "Build succeeds" | "exit code 0 AND no ERROR lines" |
| "Handle exceptions appropriately" | "Catch FileNotFoundException → log, skip. IOException → retry once, fail" |
| "If file is too large..." | "If file size > 10MB..." |
| `Read: ~/git/cui-llm-rules/standards/java.adoc` | `Skill: cui-java-core` |
| tools: Read, Edit<br>(workflow uses Skill) | tools: Read, Edit, Skill |

## Reference Template

See `.claude/agents/maven-project-builder.md` for fully compliant implementation:

* ✅ Perfect Tool Fit (100%)
* ✅ Proper skill loading (Step 0)
* ✅ SKILLS USED documentation
* ✅ Structured response format
* ✅ Complete frontmatter

## Cross-References

* [Plugin Architecture](architecture-overview.md)
* [Plugin Specifications](plugin-specifications.md)
* [Marketplace Architecture Skill](../SKILL.md)
