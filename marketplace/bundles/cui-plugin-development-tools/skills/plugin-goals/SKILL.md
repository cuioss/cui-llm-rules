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
python3 .plan/execute-script.py planning:manage-files:manage-files read \
  --plan-id {plan_id} \
  --file request.md

python3 .plan/execute-script.py planning:manage-config:manage-config read \
  --plan-id {plan_id}

python3 .plan/execute-script.py planning:manage-references:manage-references read \
  --plan-id {plan_id}
```

Parse the request to identify what needs to be accomplished.

### Step 2: Determine Impact Path

Analyze the request to determine the impact scope:

**Path-Single** (Isolated Change):
- Creating/modifying 1-3 components in a single bundle
- No cross-references or dependencies to update
- Examples: "Add new skill", "Fix command X", "Create agent Y"

**Path-Multi** (Cross-Cutting Change):
- Changes affect shared patterns, interfaces, or conventions
- Multiple components reference the changed entity
- Examples: "Rename script notation", "Change output format", "Update API contract"

**Decision Criteria**:

| Indicator | Path |
|-----------|------|
| "add", "create", "new" (single component) | Single |
| "fix", "update" (localized) | Single |
| "rename", "migrate", "refactor" | Multi |
| "change format", "update pattern" | Multi |
| Cross-bundle impact mentioned | Multi |

**Log the decision**:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type decision \
  --summary "Impact path: {Single|Multi}" \
  --detail "{reasoning for the decision}"
```

---

### Step 3a: Path-Single Workflow

For isolated changes, identify the target components directly:

1. **Identify target bundle and component type**
2. **Read existing component** (if modify/refactor scope)
3. **Create goals** for each component to create/modify

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal add \
  --plan-id {plan_id} \
  --title "{component action}" \
  --body "{technical description with path, type, dependencies}"
```

**Goal Structure for Path-Single**:
- Component type (skill, command, agent, script)
- Target path
- Dependencies (if any)
- Standards to follow

**Continue to Step 4.**

---

### Step 3b: Path-Multi Workflow

For cross-cutting changes, perform comprehensive impact analysis:

#### 3b.1: Load Marketplace Inventory

Use scan-marketplace-inventory to get complete component list:

```bash
# Full inventory with descriptions
python3 .plan/execute-script.py \
  cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory \
  --include-descriptions

# Or filter by bundles if impact is known to be limited
python3 .plan/execute-script.py \
  cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory \
  --bundles planning,cui-java-expert \
  --include-descriptions
```

#### 3b.2: Analyze Each Component

For each component in the inventory, **read and analyze** to determine if affected:

**DO NOT use scripts to determine impact** - thoroughly analyze each component step-by-step:

1. Read the component file
2. Search for references to the changed entity
3. Determine if update is required
4. Document the finding

**Analysis checklist per component**:
- [ ] Does it reference the changed skill/command/agent?
- [ ] Does it use the changed script notation?
- [ ] Does it follow the pattern being modified?
- [ ] Does it output in the format being changed?

#### 3b.3: Create Goals

**Goal 1: Core Changes**

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal add \
  --plan-id {plan_id} \
  --title "Implement core {change type}" \
  --body "Primary implementation of the change:
- Component: {primary component}
- Path: {path}
- Change: {what needs to change}
- Standards: {applicable standards}"
```

**Goal N: Each Affected Component**

For each component identified as affected:

```bash
python3 .plan/execute-script.py planning:manage-goals:manage-goal add \
  --plan-id {plan_id} \
  --title "Update {component-name} for {change}" \
  --body "Update component to align with core change:
- Component: {bundle}:{component}
- Path: {path}
- References to update: {list}
- Verification: {how to verify}"
```

**Continue to Step 4.**

---

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
impact_path: {Single|Multi}

goals_created[N]:
- GOAL-1: {title}
- GOAL-2: {title}
- GOAL-3: {title}

components_analyzed: {count for Path-Multi, 0 for Path-Single}
lessons_recorded: {count}
```

---

## Inventory Script Reference

**Script**: `cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory`

**Options**:

| Option | Description |
|--------|-------------|
| `--scope marketplace` | Scan marketplace bundles (default) |
| `--resource-types agents,commands,skills,scripts` | Filter resource types |
| `--include-descriptions` | Extract descriptions from frontmatter |
| `--name-pattern <pattern>` | Filter by name (fnmatch glob, pipe-separated) |
| `--bundles <names>` | Filter to specific bundles (comma-separated) |

**Example Calls**:

```bash
# All components with descriptions
python3 .plan/execute-script.py \
  cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory \
  --include-descriptions

# Only skills in planning bundle
python3 .plan/execute-script.py \
  cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory \
  --bundles planning \
  --resource-types skills

# Components matching pattern
python3 .plan/execute-script.py \
  cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory \
  --name-pattern "*-goals*|*-plan*"
```

---

## Goal Decomposition Patterns

### Path-Single Patterns

| Request Pattern | Typical Goals |
|-----------------|---------------|
| "Add new skill" | 1. Create SKILL.md 2. Add standards docs 3. Create scripts 4. Update plugin.json |
| "Add new command" | 1. Create command.md 2. Implement skill delegation 3. Update plugin.json |
| "Add new agent" | 1. Create agent.md 2. Define tool requirements 3. Update plugin.json |
| "Fix command X" | 1. Update command with fix |

### Path-Multi Patterns

| Request Pattern | Typical Goals |
|-----------------|---------------|
| "Rename notation X to Y" | 1. Update core definition 2-N. Update each referencing component |
| "Change output format" | 1. Define new format 2-N. Update each producer/consumer |
| "Migrate to new API" | 1. Implement new API 2-N. Migrate each caller |

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
- `planning:manage-log` - Log decisions
- `cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory` - Inventory analysis

**Standards Referenced**:
- `cui-plugin-development-tools:plugin-architecture` - Architecture principles
- `cui-plugin-development-tools:plugin-create` - Component creation patterns
- `cui-plugin-development-tools:plugin-doctor` - Quality validation
