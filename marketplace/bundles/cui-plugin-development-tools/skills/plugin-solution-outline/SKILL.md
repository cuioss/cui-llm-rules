---
name: plugin-solution-outline
description: Analyze plugin codebase and decompose request into goals
allowed-tools: Read, Glob, Grep, Bash
---

# Plugin Goals Skill

**Role**: Domain analysis skill for plugin development tasks. Transforms the request into a solution document by analyzing the marketplace structure.

**Key Pattern**: Single solution document - goals are consolidated into `solution_outline.md` via `manage-plan-documents` skill.

## Operation: decompose

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Process**:

### Step 0: Load Solution Outline Skill

Load the solution outline skill for structure and examples:

```
Skill: planning:manage-solution-outline
```

This provides:
- Required document structure (Summary, Overview, Deliverables)
- ASCII diagram patterns for plugin integration tasks
- Deliverable reference format
- Realistic examples (see `examples/plugin-feature.md`)

### Step 1: Load Request Context

Load plan context via manage-* scripts:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request read \
  --plan-id {plan_id}

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
3. **Build goals section** for each component to create/modify

Build a goals markdown section:

```markdown
### 1. {Component Action}

{Technical description}

**Type**: {skill|command|agent|script}
**Path**: `marketplace/bundles/{bundle}/{type}/{name}`
**Dependencies**: {dependencies if any}
**Standards**: {standards to follow}

**Success Criteria:**
- {criterion 1}
- {criterion 2}
```

**Continue to Step 3c to create the solution document.**

---

### Step 3b: Path-Multi Workflow

For cross-cutting changes, perform comprehensive impact analysis that produces **concrete file enumeration**.

**CRITICAL**: Goals must contain explicit file paths. A goal that says "update all X" without listing the files is INVALID - it just restates the request.

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

For each component in the inventory, **read and analyze** to determine if affected.

**CRITICAL**: Analyze components in batches with explicit logging to ensure thoroughness.

##### Batch Processing

Process components in batches of **10-15 files** per bundle. After each batch:

1. Log a checkpoint to work-log
2. Review findings before continuing
3. Do NOT skip components or rush through batches

```bash
# After each batch of 10-15 components
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type progress \
  --summary "Analyzed batch {N} of {bundle}: {X} affected, {Y} not affected" \
  --detail "Affected: file1.md, file2.md | Not affected: file3.md, file4.md, ..."
```

##### Per-Component Analysis

For each component, execute these steps **in order**:

1. **Read** the component file completely
2. **Search** for references to the changed entity
3. **Evaluate** against the checklist below
4. **Record** the result (affected or not, with reason)

**Analysis checklist per component**:
- [ ] Does it reference the changed skill/command/agent?
- [ ] Does it use the changed script notation?
- [ ] Does it follow the pattern being modified?
- [ ] Does it output in the format being changed?

##### Logging Affected Files

For each **affected** file, log immediately:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type finding \
  --summary "Affected: {file_path}" \
  --detail "Reason: {why this file needs changes}"
```

**Build affected files list** as you analyze:
```
affected_files:
  bundle-a:
    - path/to/file1.md (reason: uses JSON output)
    - path/to/file2.md (reason: references changed pattern)
  bundle-b:
    - path/to/file3.md (reason: produces affected format)
```

##### Final Verification

After all batches complete, log the summary:

```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase init \
  --type milestone \
  --summary "Impact analysis complete: {total_affected} of {total_analyzed} affected" \
  --detail "Bundles analyzed: {list}. Ready for goal creation."
```

#### 3b.3: Build Goals Section with Enumeration

**Goal Organization**: Create one goal per bundle (or per ~5-8 files if a bundle has many). Each goal MUST list the specific files to modify.

**Goal Requirements** (all fields mandatory for Path-Multi):

| Field | Description | Example |
|-------|-------------|---------|
| `files` | Explicit list of file paths | `marketplace/bundles/planning/agents/plan-refine-agent.md` |
| `change_per_file` | What changes in each file | "Replace ```json output blocks with ```toon" |
| `verification` | How to verify the change | "Grep for ```json returns 0 matches" |

**Template**:

```markdown
### 1. Update {bundle} {component-type}s for {change}

**Affected files:**
- `{path/to/file1.md}`
- `{path/to/file2.md}`
- `{path/to/file3.md}`

**Change per file:** {specific change description}
**Verification:** {how to verify completion}

**Success Criteria:**
- {criterion 1}
- {criterion 2}
```

**Example** (correct):
```markdown
### 1. Update planning agents to TOON output

**Affected files:**
- `marketplace/bundles/planning/agents/plan-init-agent.md`
- `marketplace/bundles/planning/agents/plan-refine-agent.md`
- `marketplace/bundles/planning/agents/plan-execute-agent.md`

**Change per file:** Replace output format from JSON to TOON in Return/Output sections
**Verification:** grep -l 'status: success' returns all files, grep -l '"status":' returns none

**Success Criteria:**
- All agents use TOON output format
- No JSON output blocks remain
```

**Anti-pattern** (INVALID - do not create goals like this):
```markdown
### 1. Update agent output formats to TOON

Migrate all agent .md files to specify TOON output format
```
This restates the request without enumeration. The goals phase added no information.

**Continue to Step 3c to create the solution document.**

---

### Step 3c: Create Solution Document

After building the goals section (from either Path-Single or Path-Multi workflow), write the solution document directly using Claude Code's Write tool to: `.plan/plans/{plan_id}/solution_outline.md`

Then validate the structure:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution validate \
  --plan-id {plan_id}
```

**Why direct Write?** Solution outlines contain ASCII diagrams and rich content that don't fit CLI parameter passing. The agent generates the full markdown document and writes it directly.

**Continue to Step 4.**

---

### Step 4: Record Issues as Lessons

On unexpected structure or ambiguity:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component-type skill \
  --component-name plugin-solution-outline \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 5: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}
solution_created: true
impact_path: {Single|Multi}

goals_count: {number of goals in solution document}
total_files_affected: {sum of files across all goals}
components_analyzed: {count for Path-Multi, 0 for Path-Single}
lessons_recorded: {count}
```

**Path-Multi Validation**: If `total_files_affected` is 0 or goals don't contain file paths, the decomposition is incomplete.

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
| `skill` | SKILL.md, standards, references | java-solution-outline |
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

**Caller**: `cui-plugin-development-tools:plugin-solution-outline-agent`

**Script Notations** (use EXACTLY as shown):
- `planning:manage-solution-outline:manage-solution-outline` - Write and validate solution document
- `planning:manage-plan-documents:manage-plan-document` - Read request (request read)
- `planning:manage-lessons:manage-lesson` - Record lessons on issues (add)
- `planning:manage-log:manage-work-log` - Log decisions (add, read)
- `planning:manage-config:manage-config` - Read config (read)
- `planning:manage-references:manage-references` - Read references (read)
- `cui-plugin-development-tools:marketplace-inventory:scan-marketplace-inventory` - Inventory analysis

**Standards Referenced**:
- `cui-plugin-development-tools:plugin-architecture` - Architecture principles
- `cui-plugin-development-tools:plugin-create` - Component creation patterns
- `cui-plugin-development-tools:plugin-doctor` - Quality validation
