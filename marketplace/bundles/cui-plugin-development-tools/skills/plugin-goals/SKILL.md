---
name: plugin-goals
description: Analyze plugin codebase and decompose request into goals
allowed-tools: Read, Glob, Grep, Bash
---

# Plugin Goals Skill

**Role**: Domain analysis skill for plugin development tasks. Transforms the request into goals by analyzing the marketplace structure and writing GOALs directly.

**Key Pattern**: Direct storage - goals are written immediately via `manage-goals` script.

## Operation: decompose

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Process**:

### Step 1: Load Request Context

Load plan context via manage-* scripts:

```bash
# Read original request description
python3 .plan/execute-script.py planning:manage-files:manage-files read \
  --plan-id {plan_id} \
  --file request.md

# Read plan configuration
python3 .plan/execute-script.py planning:manage-config:manage-config read \
  --plan-id {plan_id}

# Read references (issue context if available)
python3 .plan/execute-script.py planning:manage-references:manage-references read \
  --plan-id {plan_id}
```

Parse the request to identify what needs to be accomplished.

### Step 2: Analyze Marketplace Structure

Parse request intent and explore affected plugin components:

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

### Step 3: Decompose Into Goals

Break the request into discrete, achievable goals. Each goal should be:
- **Independent**: Can be implemented without other goals completing first (when possible)
- **Testable**: Has clear completion criteria
- **Sized**: Reasonable scope (not too large, not too small)

For each goal identified:

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal add \
  --plan-id {plan_id} \
  --title "{goal title}" \
  --body "{Plugin-specific technical goal description}"
```

**Goal Body Content**:
- Component type (skill, command, agent, script)
- Target bundle
- Target path (e.g., `marketplace/bundles/{bundle}/skills/...`)
- Dependencies (skills referenced, scripts needed)
- Frontmatter requirements
- Standards to follow

### Step 4: Record Issues as Lessons

On unexpected structure or ambiguity:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component-type skill \
  --component-name plugin-goals \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 5: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}

goals_created[N]:
- GOAL-1
- GOAL-2
- GOAL-3

lessons_recorded: {count}
```

---

## Goal Decomposition Patterns

| Request Pattern | Typical Goals |
|-----------------|---------------|
| "Add new skill" | 1. Create SKILL.md 2. Add standards documents 3. Create scripts 4. Update plugin.json |
| "Add new command" | 1. Create command markdown 2. Implement skill delegation 3. Update plugin.json |
| "Add new agent" | 1. Create agent markdown 2. Define tool requirements 3. Update plugin.json |

---

## Component Types

| Type | Indicators | Example |
|------|------------|---------|
| `skill` | SKILL.md, standards, references | java-goals |
| `command` | Slash command, user-facing | plugin-doctor.md |
| `agent` | Autonomous execution, tools | java-implement-agent.md |
| `script` | Python/Bash automation | manage-goal.py |

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

**Caller**: `cui-plugin-development-tools:plugin-goals-agent`

**Scripts Used**:
- `planning:manage-goals` - Create goals
- `planning:manage-lessons` - Record lessons on issues

**Standards Referenced**:
- `cui-plugin-development-tools:plugin-architecture` - Architecture principles
- `cui-plugin-development-tools:plugin-create` - Component creation patterns
- `cui-plugin-development-tools:plugin-doctor` - Quality validation
