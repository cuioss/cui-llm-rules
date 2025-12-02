---
name: plugin-analysis
description: Analyzes plugin development tasks to identify components, dependencies, and scope. Implements planning:analysis-api contract.
allowed-tools: Read, Glob, Grep, Bash
---

# Plugin Analysis Skill

**Role**: Domain analysis skill for plugin development tasks. Analyzes task requirements and codebase to identify plugin components (scripts, skills, commands, agents) and their dependencies.

**Integration**: Called by `planning:plan-refine` during the refine phase for `plugin-development` plan types.

**API Contract**: Load `planning:analysis-api` for full input/output specification.

```
Skill: planning:analysis-api
```

## Operation: analyze

**Contract**: See `planning:analysis-api` for full input/output specification.

### Domain-Specific Input

Standard input parameters per API contract. No additional parameters for plugin domain.

### Domain-Specific Output

**Component Types**: `script`, `skill`, `command`, `agent`

**Domain-Specific Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `bundle` | string | Target bundle name (e.g., "planning", "cui-java-expert") |

**Example Output**:
```yaml
analysis_result:
  status: "success"
  components:
    - name: "update-progress.py"
      type: "script"
      scope: "create"
      path: "marketplace/bundles/planning/skills/plan-files/scripts/update-progress.py"
      bundle: "planning"
      dependencies:
        - "plan-files skill"
      complexity: "medium"
      notes: "New script for progress tracking"
```

## Analysis Process

### Step 1: Parse Task Intent

Extract from task description:
- Action verbs: create, update, modify, refactor, fix
- Component types: script, skill, command, agent, bundle
- Target bundle: Look for `marketplace/bundles/{bundle-name}`
- Affected components: Names mentioned in task

### Step 2: Explore Codebase

For each identified component:

**Scripts**:
```bash
Glob marketplace/bundles/{bundle}/skills/*/scripts/*.py
Grep "{pattern}" --type py
```

**Skills**:
```bash
Glob marketplace/bundles/{bundle}/skills/*/SKILL.md
Read {skill-path}/SKILL.md
```

**Commands**:
```bash
Glob marketplace/bundles/{bundle}/commands/*.md
Read {command-path}
```

**Agents**:
```bash
Glob marketplace/bundles/{bundle}/agents/*.md
Read {agent-path}
```

### Step 3: Identify Dependencies

For each component, analyze:
- **Skill dependencies**: `Skill: {bundle}:{skill}` references
- **Script dependencies**: Import statements, subprocess calls
- **Command dependencies**: Skill invocations
- **Cross-bundle dependencies**: References to other bundles

### Step 4: Assess Complexity

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Files affected | 1-2 | 3-5 | 6+ |
| Cross-bundle | No | 1 bundle | 2+ bundles |
| Breaking changes | None | Internal | External API |
| Dependencies | 0-1 | 2-3 | 4+ |

### Step 5: Return Components

Return structured component list with all metadata for plan-type skill to generate tasks.

## Component Type Detection

| Indicator | Type |
|-----------|------|
| "create script", "new script", "write script" | script |
| "create skill", "new skill", "add skill" | skill |
| "create command", "new command", "add command" | command |
| "create agent", "new agent", "add agent" | agent |
| "update {component}", "modify {component}" | Detect from existing |
| `marketplace/bundles/.../scripts/` path | script |
| `marketplace/bundles/.../skills/` path | skill |
| `marketplace/bundles/.../commands/` path | command |
| `marketplace/bundles/.../agents/` path | agent |

## Scope Detection

| Indicator | Scope |
|-----------|-------|
| "create", "new", "add" | create |
| "update", "modify", "change", "fix" | modify |
| "refactor", "reorganize", "restructure" | refactor |

## Example Analysis

**Task**: "Create a new script update-progress.py in plan-files skill and modify the existing SKILL.md"

**Analysis Output**:
```yaml
components:
  - name: "update-progress.py"
    type: "script"
    scope: "create"
    bundle: "planning"
    path: "marketplace/bundles/planning/skills/plan-files/scripts/update-progress.py"
    dependencies:
      - "plan-files skill"
    complexity: "medium"
    notes: "New script for progress tracking"

  - name: "plan-files SKILL.md"
    type: "skill"
    scope: "modify"
    bundle: "planning"
    path: "marketplace/bundles/planning/skills/plan-files/SKILL.md"
    dependencies:
      - "update-progress.py"
    complexity: "low"
    notes: "Document new script API"
```

## Integration with Plan-Type Skills

After analysis completes, return components to `plan-refine`, which passes them to:

```
Skill: planning:plan-type-plugin
operation: generate-tasks
plan_id: {plan_id}
components: {components from analysis}
```

The plan-type skill then generates appropriate tasks based on component types and writes them directly to plan.md.

## Error Handling

### Component Not Found
If task references a component that doesn't exist:
- For "create" scope: Continue (expected)
- For "modify" scope: Warn and ask for clarification
- For "refactor" scope: Error and request correct path

### Bundle Not Found
If bundle path doesn't exist:
- Check if task is to create the bundle
- Otherwise error with suggestion

### Ambiguous Component Type
If type cannot be determined:
- Ask user to clarify
- Provide detected options

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Returns structured components[] for plan generation
- [x] Identifies dependencies between components
- [x] Assesses complexity for task planning
- [x] Handles create/modify/refactor scopes
