---
name: cui-create-agent
description: Guide users through creating a well-structured agent following architectural best practices
---

# Create Agent Command

Interactive wizard for creating well-structured Claude Code agents following marketplace architecture and best practices.

## PARAMETERS

**scope** - Where to create agent (marketplace/global/project, default: marketplace)

## WORKFLOW

### Step 1: Load Architecture Standards

```
Skill: cui-marketplace-architecture
```

### Step 2: Interactive Questionnaire

**A. Agent name** - kebab-case (e.g., `code-reviewer`, `test-runner`)

**B. Bundle selection** - List available bundles

**C. Description** - One sentence describing agent purpose (<100 chars)

**D. Agent type**:
1. Analysis agent (code review, diagnostics)
2. Execution agent (build, test, deploy)
3. Coordination agent (multi-step workflows)
4. Research agent (information gathering)

### Step 3: Collect Capability Information

**A. What does this agent do?** (detailed capabilities)

**B. Required tools** - Which tools does agent need?
- Read, Write, Edit, Glob, Grep, Bash, Task, WebFetch, etc.

**C. When should this agent be used?** (trigger conditions)

**D. Expected inputs/outputs**

### Step 4: Validate Architecture Compliance

Using cui-marketplace-architecture skill, verify:
- Self-contained (no cross-agent dependencies)
- Proper tool fit (agent needs listed tools)
- Essential rules compliance

### Step 5: Generate Agent File

Create `{bundle}/agents/{agent-name}.md` with:

**A. YAML frontmatter**:
- name, description, model (optional), tools

**B. Agent purpose** section

**C. Workflow** section (numbered steps)

**D. Tool usage** section

**E. Critical rules** section

Trust AI to generate appropriate structure from collected information.

### Step 6: Display Summary

Show created file path and next steps.

### Step 7: Run Agent Diagnosis

```
SlashCommand: /cui-diagnose-agents agent-name={agent-name}
```

## CRITICAL RULES

**Architecture:**
- Agents must be self-contained
- List ALL required tools in frontmatter
- Use Task tool for delegation only
- Follow essential rules from marketplace architecture

**Structure:**
- Valid YAML frontmatter required
- Clear numbered workflow
- Tool usage documented
- Critical rules defined

**Tool Fit:**
- Only list tools agent actually uses
- Verify tool fit score >80%
- No over-tooling

## USAGE EXAMPLES

**Create marketplace agent:**
```
/cui-create-agent
```

**Create in specific scope:**
```
/cui-create-agent scope=global
```

## RELATED

- `/cui-diagnose-agents` - Validates agent
- `cui-marketplace-architecture` skill - Architecture rules
