---
name: plugin-specify
description: Analyze plugin codebase and create specifications from requirements with direct storage
allowed-tools: Read, Glob, Grep, Bash
---

# Plugin Specify Skill

**Role**: Domain analysis skill for plugin development tasks. Transforms requirements into specifications by analyzing the marketplace structure and writing SPECs directly.

**Key Pattern**: Direct storage - specifications are written immediately via `manage-specifications` script.

## Operation: specify

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `requirement_id` | string | No | Single REQ ID (omit for batch - queries all pending) |

**Process**:

### Step 1: Load Requirements

**Batch mode** (no requirement_id):
```bash
python3 .plan/execute-script.py planning:manage-requirements:manage-requirement findAll \
  --plan-id {plan_id}
```

**Single mode** (requirement_id provided):
```bash
python3 .plan/execute-script.py planning:manage-requirements:manage-requirement get \
  --plan-id {plan_id} \
  --number {requirement_id}
```

### Step 2: Load Context

Read plan context files:
```
Read {plan_dir}/task.md        # Original task description
Read {plan_dir}/config.toon    # build_system, plan_type
Read {plan_dir}/references.toon # issue_context if available
```

### Step 3: For Each Requirement

#### 3a. Analyze Marketplace Structure

Parse requirement intent and explore affected plugin components:

**Bundle Detection**:
```bash
Glob marketplace/bundles/*/\.claude-plugin/plugin.json
Read marketplace/.claude-plugin/marketplace.json
```

**Component Exploration**:
```bash
Glob marketplace/bundles/{bundle}/skills/*/SKILL.md
Glob marketplace/bundles/{bundle}/commands/*.md
Glob marketplace/bundles/{bundle}/agents/*.md
Read {component-path}
```

**Identify**:
- Skills, commands, agents affected
- Bundle structure and organization
- Script requirements
- Reference document needs
- Complexity assessment

#### 3b. Create Specification

Write specification with plugin-specific technical details:

```bash
python3 .plan/execute-script.py planning:manage-specifications:manage-specification add \
  --plan-id {plan_id} \
  --title "{component} implementation" \
  --requirements "REQ-{n}" \
  --body "{Plugin-specific technical specification}"
```

**Specification Body Content**:
- Component type (skill, command, agent, script)
- Target bundle
- Target path (e.g., `marketplace/bundles/{bundle}/skills/...`)
- Dependencies (skills referenced, scripts needed)
- Frontmatter requirements
- Standards to follow

#### 3c. Record Issues as Lessons

On unexpected structure or ambiguity:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component-type skill \
  --component-name plugin-specify \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 4: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}

specs_created[N]:
- SPEC-1
- SPEC-2
- SPEC-3

lessons_recorded: {count}
```

---

## Component Types

| Type | Indicators | Example |
|------|------------|---------|
| `skill` | SKILL.md, standards, references | java-specify |
| `command` | Slash command, user-facing | plugin-doctor.md |
| `agent` | Autonomous execution, tools | java-implement-agent.md |
| `script` | Python/Bash automation | manage-specification.py |

---

## Scope Detection

| Indicator | Scope |
|-----------|-------|
| "implement", "add", "create", "new" | create |
| "fix", "update", "modify", "change" | modify |
| "refactor", "reorganize", "migrate" | refactor |

---

## Complexity Assessment

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Components affected | 1-2 | 3-5 | 6+ |
| Cross-bundle | No | 1 bundle | 2+ bundles |
| Breaking changes | None | Internal | Public API |
| Dependencies | 0-1 | 2-3 | 4+ |
| Scripts needed | 0 | 1-2 | 3+ |

---

## Plugin Architecture Patterns

### Skill Structure
When task involves skills:
- Check for SKILL.md template
- Identify required references/
- Check for scripts/ directory
- Reference `cui-plugin-development-tools:plugin-architecture`

### Command Structure
When task involves commands:
- Check frontmatter format
- Identify skill delegation pattern
- Reference thin orchestrator pattern

### Agent Structure
When task involves agents:
- Check tools declaration
- Identify skill loading pattern
- Reference minimal wrapper pattern

---

## Error Handling

### Component Not Found

| Scope | Action |
|-------|--------|
| `create` | Continue (expected - component doesn't exist yet) |
| `modify` | Warn and ask for clarification |
| `refactor` | Error and request correct path |

### Bundle Not Found

If bundle doesn't exist:
- Check if task is to create the bundle
- Otherwise error with suggestion

### Ambiguous Component

If multiple components match:
- List all matches with paths
- Ask user to select correct one

---

## Integration

**Caller**: `cui-plugin-development-tools:plugin-specify-agent`

**Scripts Used**:
- `planning:manage-requirements` - Load requirements
- `planning:manage-specifications` - Create specifications
- `planning:manage-lessons` - Record lessons on issues

**Standards Referenced**:
- `cui-plugin-development-tools:plugin-architecture` - Architecture principles
- `cui-plugin-development-tools:plugin-create` - Component creation patterns
- `cui-plugin-development-tools:plugin-doctor` - Quality validation
