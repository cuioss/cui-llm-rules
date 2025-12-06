---
name: plan-configure
description: Analyze task input, create requirements, detect plan type, and configure plan
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Configure Skill

Analyze task input to create requirements, detect plan type, and configure the plan. This skill is the second phase of plan initialization, following plan-init.

## What This Skill Provides

- Task analysis from task.md
- Requirements extraction and creation
- Plan type detection (or override)
- Configuration creation with defaults
- Plan-type specific configuration via delegation

## When to Activate This Skill

Activate when `plan-configure-agent` delegates with:
- `plan_id` (required): Plan identifier
- `plan_type` (optional): Override auto-detection

---

## Script Path Resolution

**MANDATORY**: Before executing any script, resolve paths via script-runner.

```
Skill: general-tools:script-runner
Resolve: planning:manage-files/scripts/manage-files.py
Resolve: planning:manage-requirements/scripts/manage-requirement.py
Resolve: planning:manage-config/scripts/manage-config.py
Resolve: planning:manage-lifecycle/scripts/manage-lifecycle.py
Resolve: planning:manage-log/scripts/manage-work-log.py
```

Use the resolved absolute paths in all Bash commands.

---

## Workflow: Configure

Execute this workflow when invoked.

### Step 0: Log Phase Start

Log the start of the configure phase:

```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase configure \
  --type progress \
  --summary "Starting configure phase"
```

Script: `planning:manage-log/scripts/manage-work-log.py`

### Step 1: Read Task Input

Read the original task input from task.md:

```bash
python3 {resolved_manage_files} read \
  --plan-id {plan_id} \
  --file task.md
```

Script: `planning:manage-files/scripts/manage-files.py`

### Step 2: Analyze Task and Create Requirements

Analyze the task.md content to understand:
- What is the goal/objective?
- What are the acceptance criteria?
- What components/files are affected?
- What constraints or dependencies exist?
- What is the scope (small fix vs large feature)?

**If uncertain about any aspect**, ask clarifying questions:

```
AskUserQuestion:
  question: "What is the scope of this change?"
  options:
    - label: "Small fix"
      description: "Single file or function change"
    - label: "Medium change"
      description: "Few related files"
    - label: "Large feature"
      description: "Multiple components"
```

### Step 3: Create Requirements

For each identified requirement, create via manage-requirements:

```bash
python3 {resolved_manage_requirements} add \
  --plan-id {plan_id} \
  --title "Requirement title" \
  --body "Detailed requirement description"
```

Script: `planning:manage-requirements/scripts/manage-requirement.py`

Creates: `requirements/REQ-001-{slug}.toon`, `REQ-002-...`, etc.

**After each requirement**, log the artifact:

```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase configure \
  --type artifact \
  --summary "Created {req_id}: {title}" \
  --detail "{brief description of what this requirement covers}"
```

### Step 4: Detect Plan Type

Determine plan type from task analysis. Plan types use `bundle:skill` notation.

| Indicator | Plan Type |
|-----------|-----------|
| Java code, Maven/Gradle, .java files | `planning:plan-type-java` |
| JavaScript, npm, .js/.ts files | `planning:plan-type-javascript` |
| Plugin/skill/command development | `planning:plan-type-plugin` |
| Generic/simple task | `planning:plan-type-generic` |

**If plan_type parameter provided**: Use override value (must be bundle:skill notation).

**If uncertain**, ask:

```
AskUserQuestion:
  question: "What technology stack does this task primarily involve?"
  options:
    - label: "Java"
      description: "Java code with Maven or Gradle"
      value: "planning:plan-type-java"
    - label: "JavaScript"
      description: "JavaScript/TypeScript with npm"
      value: "planning:plan-type-javascript"
    - label: "Plugin Development"
      description: "Claude Code plugin components"
      value: "planning:plan-type-plugin"
    - label: "Generic"
      description: "Generic task, no specific technology"
      value: "planning:plan-type-generic"
```

**After detecting plan type**, log the decision with reasoning:

```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase configure \
  --type decision \
  --summary "Selected {plan_type}" \
  --detail "{reasoning why this plan type was chosen, e.g., 'Task modifies .java files in service layer'}"
```

### Step 5: Create Configuration

Create config.toon with base settings:

```bash
python3 {resolved_manage_config} create \
  --plan-id {plan_id} \
  --plan-type {plan_type}
```

Script: `planning:manage-config/scripts/manage-config.py`

This creates config.toon with:
- `plan_type`: detected or overridden
- `compatibility`: deprecations (default)
- `commit_strategy`: phase-specific (default)

### Step 6: Call Plan-Type Configure

Delegate to plan-type skill for domain-specific configuration:

```
Skill: planning:plan-type-{plan_type}
operation: configure
plan_id: {plan_id}
```

This adds finalize configuration to config.toon:
- `create_pr`: Whether to create PR
- `verification_required`: Whether verification needed
- `verification_command`: Command for verification
- `branch_strategy`: feature or direct

### Step 7: Transition Phase

The phase transitions from init → refine after configuration completes.

Use manage-lifecycle to track:

```bash
python3 {resolved_manage_lifecycle} transition \
  --plan-id {plan_id} \
  --completed-phase init
```

Script: `planning:manage-lifecycle/scripts/manage-lifecycle.py`

### Step 8: Log Phase Completion

Log the outcome of the configure phase:

```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase configure \
  --type outcome \
  --summary "Completed configure: {req_count} requirements, type={plan_type}" \
  --detail "compatibility={compatibility}, commit_strategy={commit_strategy}"
```

---

## Output

Return structured result:

```toon
status: success
plan_id: my-feature
plan_type: planning:plan-type-java
next_phase: refine

requirements:
  count: 3
  pending: 3

configuration:
  plan_type: planning:plan-type-java
  compatibility: deprecations
  commit_strategy: phase-specific
```

---

## Scripts Used

| Script | Purpose |
|--------|---------|
| `planning:manage-files/scripts/manage-files.py` | Read task.md |
| `planning:manage-requirements/scripts/manage-requirement.py` | Create requirements |
| `planning:manage-config/scripts/manage-config.py` | Create config.toon |
| `planning:manage-lifecycle/scripts/manage-lifecycle.py` | Phase transitions |
| `planning:manage-log/scripts/manage-work-log.py` | Work-log entries |

---

## Clarifying Question Patterns

Ask clarifying questions when:
- Scope is unclear (small/medium/large)
- Technology stack is ambiguous
- Breaking changes uncertain
- Testing requirements unclear

Always provide options for easier selection:

| Uncertainty | Question | Options |
|-------------|----------|---------|
| Scope | "What is the scope?" | Small fix, Medium change, Large feature |
| Technology | "What technology?" | Java, JavaScript, Plugin, Generic |
| Breaking | "Breaking changes?" | No (compatible), Yes (breaking) |
| Testing | "Testing required?" | Unit only, Unit+integration, Full suite |

---

## Error Handling

On script failure:

1. **Log the error** to work-log:

```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase configure \
  --type error \
  --summary "ERROR: {error_type}" \
  --detail "{full error context and message}"
```

2. Capture error context
3. Record lesson-learned via `general-tools:manage-lessons-learned`
4. Return error status with message

```toon
status: error
plan_id: my-feature
error: script_failed
message: manage-requirements failed to create requirement
```

---

## Integration Points

### Input From

- `plan-init-agent`: Creates plan directory and task.md
- `plan-configure-agent`: Delegates to this skill

### Output To

- `plan-refine-agent`: Uses requirements and config for refinement
- `plan-type-{type}`: Receives configure operation call

### Files Created/Updated

| File | Operation |
|------|-----------|
| `requirements/*.toon` | Created |
| `config.toon` | Created |
| `status.toon` | Updated (phase transition) |
