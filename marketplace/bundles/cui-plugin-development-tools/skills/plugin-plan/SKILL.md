---
name: plugin-plan
description: Create implementation tasks from specifications with direct storage
allowed-tools: Read, Bash
---

# Plugin Plan Skill

**Role**: Domain planning skill for plugin development tasks. Transforms specifications into executable tasks by applying plugin-specific knowledge and writing TASKs directly.

**Key Pattern**: Direct storage - tasks are written immediately via `manage-tasks` script.

## Operation: plan

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `specification_id` | string | No | Single SPEC ID (omit for batch - queries all pending) |

**Process**:

### Step 1: Load Specifications

Script: `planning:manage-specifications`

**Batch mode** (no specification_id):
```bash
python3 .plan/execute-script.py planning:manage-specifications:findAll \
  --plan-id {plan_id}
```

**Single mode** (specification_id provided):
```bash
python3 .plan/execute-script.py planning:manage-specifications:get \
  --plan-id {plan_id} \
  --number {specification_id}
```

### Step 2: For Each Specification

#### 2a. Analyze Specification Content

Parse the specification body to determine:
- Component type and target path
- Task granularity (single task or multiple)
- Plugin-specific implementation steps
- Verification requirements
- Standards to apply

#### 2b. Create Task(s)

Generate task(s) with plugin-specific steps:

Script: `planning:manage-tasks`

```bash
python3 .plan/execute-script.py planning:manage-tasks:add \
  --plan-id {plan_id} \
  --specification SPEC-{n} \
  --title "Implement {component}" \
  --description "{goal from specification}" \
  --steps \
    "Create/modify component at {path}" \
    "Add frontmatter with correct fields" \
    "Follow architecture patterns (load cui-plugin-development-tools:plugin-architecture)" \
    "Add to plugin.json" \
    "Verify with /plugin-doctor"
```

#### 2c. Record Issues as Lessons

On ambiguous specification or planning issues:

Script: `planning:manage-lessons`

```bash
python3 .plan/execute-script.py planning:manage-lessons:add \
  --component-type skill \
  --component-name plugin-plan \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 3: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}

tasks_created[N]:
- TASK-1
- TASK-2
- TASK-3
- TASK-4
- TASK-5

lessons_recorded: {count}
```

---

## Task Generation Patterns

### Single Component Task

One specification → one task when:
- Single skill/command/agent to implement
- Localized change in one file
- Simple addition

**Steps**:
1. Create/modify component at `{path}`
2. Add correct frontmatter
3. Follow architecture patterns
4. Add to plugin.json
5. Verify with `/plugin-doctor`

### Multi-Step Component Task

One specification → multiple tasks when:
- Skill + scripts pattern
- Command + skill delegation
- Refactoring with multiple phases

**Example for Skill with Scripts**:
- TASK-1: Create SKILL.md with structure
- TASK-2: Create Python script(s)
- TASK-3: Add references/ if needed
- TASK-4: Update plugin.json and verify

---

## Standard Task Steps by Component Type

### Skill
```
1. Create skill directory at {bundle}/skills/{skill-name}/
2. Create SKILL.md with frontmatter and operations
3. Create scripts/ directory if automation needed
4. Create references/ directory if documentation needed
5. Add to plugin.json skills array
6. Verify with /plugin-doctor
```

### Command
```
1. Create command file at {bundle}/commands/{command-name}.md
2. Add frontmatter (name, description)
3. Implement thin orchestrator pattern
4. Add skill delegation logic
5. Add to plugin.json commands array
6. Verify with /plugin-doctor
```

### Agent
```
1. Create agent file at {bundle}/agents/{agent-name}.md
2. Add frontmatter (name, description, tools, model)
3. Implement minimal wrapper pattern (< 150 lines)
4. Add skill delegation
5. Add to plugin.json agents array
6. Verify with /plugin-doctor
```

### Script
```
1. Create script at {skill}/scripts/{script-name}.py
2. Add shebang and stdlib-only imports
3. Implement argparse with --help
4. Use JSON output format
5. Add script documentation to SKILL.md
6. Create test in test/ directory
```

---

## Task Dependencies

When creating multiple tasks from one specification, consider:

| Dependency Type | Ordering |
|-----------------|----------|
| Scripts before skill | Scripts first (if skill uses them) |
| Skill before command | Skill first (command delegates) |
| Skill before agent | Skill first (agent delegates) |
| References before main doc | Reference docs first |

---

## Verification Steps

All plugin tasks should include verification:

**For component compliance**:
```
Run /plugin-doctor
```

**For bundle health**:
```
Verify plugin.json is valid JSON
Verify all referenced files exist
```

---

## Error Handling

### Ambiguous Specification

If specification doesn't clearly indicate:
- Target path → Ask for clarification
- Component type → Infer from context or ask
- Bundle placement → Check marketplace structure

### Missing Information

If specification lacks detail:
- Generate task with placeholder
- Add lesson-learned for future reference
- Note ambiguity in task description

---

## Integration

**Caller**: `cui-plugin-development-tools:plugin-plan-agent`

**Scripts Used**:
- `planning:manage-specifications` - Load specifications
- `planning:manage-tasks` - Create tasks
- `planning:manage-lessons` - Record lessons on issues

**Standards Referenced in Task Steps**:
- `cui-plugin-development-tools:plugin-architecture` - Architecture principles
- `cui-plugin-development-tools:plugin-create` - Creation patterns
- `cui-plugin-development-tools:plugin-doctor` - Verification
