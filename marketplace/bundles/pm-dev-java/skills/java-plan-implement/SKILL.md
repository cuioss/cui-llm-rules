---
name: java-plan-implement
description: Implement Java tasks from plan with step iteration and progress tracking
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Skill
---

# Java Plan Implement Skill

**Role**: Implement Java-domain tasks by iterating through steps (file paths) and applying changes.

**Execution Pattern**: Load task → Load skills → Iterate steps → Apply changes → Verify → Return result

## Scripts

| Script | Purpose |
|--------|---------|
| `pm-workflow:manage-tasks:manage-tasks` | Task retrieval and progress tracking |
| `plan-marshall:logging:manage-log` | Work log entries |
| `plan-marshall:plan-marshall-config:plan-marshall-config` | Domain skill retrieval |

---

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `task_number` | number | Yes | Task to execute |

## Workflow

### Step 1: Load Task Details

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks get \
  --plan-id {plan_id} \
  --number {task_number}
```

Extract from response:
- `title`: Task title for logging
- `description`: What changes to apply
- `delegation.domain`: For loading default skills
- `delegation.context_skills`: Additional skills
- `steps[]`: File paths to process
- `verification`: Commands and criteria

### Step 2: Load Domain Skills

#### 2a. Get Domain Defaults

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-defaults \
  --domain {delegation.domain}
```

#### 2b. Load Default Skills

```
Skill: {default_skill_1}
Skill: {default_skill_2}
```

#### 2c. Load Context Skills

From task delegation block:

```
Skill: {delegation.context_skills[0]}
Skill: {delegation.context_skills[1]}
```

### Step 3: Log Task Start

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "[TASK] Starting task {task_number}: {title}"
```

### Step 4: Execute Steps

For each step WHERE `status == pending`:

#### 4a. Mark Step Started

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks step-start \
  --plan-id {plan_id} \
  --task {task_number} \
  --step {step_number}
```

#### 4b. Execute Step

The step `title` is a file path. Apply changes based on:
1. Task `description` - overall change guidance
2. Loaded skills - implementation patterns
3. File type - Java source files, test files, etc.

**For Java files**:
- Read the file
- Identify sections to update
- Apply changes per task description
- Follow CUI Java patterns from loaded skills
- Write updated content

#### 4c. Log Step Progress

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "[STEP] Completed step {step_number}: {file_path}"
```

#### 4d. Mark Step Done

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks step-done \
  --plan-id {plan_id} \
  --task {task_number} \
  --step {step_number}
```

### Step 5: Run Verification

After all steps complete:

```bash
# Execute each verification command
{verification.commands[0]}
{verification.commands[1]}
```

Log result:

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "[VERIFY] Verification {passed|failed}: {criteria}"
```

### Step 6: Return Result

**Success Output**:

```toon
status: success
plan_id: {plan_id}
task_number: {task_number}

execution_summary:
  steps_completed: {N}
  steps_total: {M}
  files_modified[N]:
    - {path1}
    - {path2}

verification:
  passed: true
  command: "{verification command}"

next_action: task_complete
```

**Error Output**:

```toon
status: error
plan_id: {plan_id}
task_number: {task_number}

execution_summary:
  steps_completed: {N}
  steps_failed: {M}

failure:
  step: {step_number}
  file: "{file path}"
  error: "{error message}"
  recoverable: true

next_action: requires_attention
```

---

## Step Execution Patterns

Each step `title` is a file path. Determine operation type from:
1. Task description
2. File existence
3. Deliverable guidance

| File Exists | Task Intent | Operation |
|-------------|-------------|-----------|
| Yes | Update | Modify existing file |
| Yes | Replace | Overwrite file |
| No | Create | Create new file |
| Yes | Delete | Remove file |

### Execution Flow Per Step

#### 1. Read Current Content

```
Read: {step.title}
```

Parse the file to understand:
- Package declaration
- Import statements
- Class structure
- Existing methods

#### 2. Plan Changes

Based on task description, identify:
- What methods to modify
- What imports to add
- What patterns to apply (from loaded skills)

#### 3. Apply Changes

Use Edit tool for surgical changes:

```
Edit:
  file_path: {step.title}
  old_string: {exact text to replace}
  new_string: {replacement text}
```

**Prefer multiple small edits over one large write.**

#### 4. Verify Changes

After editing, optionally verify:
- File still compiles
- No syntax errors
- CUI patterns followed

### Common Java Changes

**Add Field**: Find field section → Add with annotations → Add getter/setter if needed (Lombok may handle)

**Add Method**: Find appropriate location → Add with JavaDoc → Follow CUI patterns

**Add Test Method**: Find test class → Add @Test method → Follow JUnit 5 patterns → Use generators if applicable

**Update JavaDoc**: Find class/method JavaDoc → Update description, params, returns → Follow CUI standards

---

## Error Handling

### Step Failure

If a step fails:
1. Log error to work-log
2. Do NOT mark step as done
3. Continue to next step OR stop (based on severity)
4. Include failure in result

### Verification Failure

If verification fails:
1. Log what failed
2. Return error status with `recoverable: true`
3. Task remains in_progress for retry

### Edit Conflict

If old_string not found:
1. Read file again (may have changed)
2. Adjust old_string
3. Retry edit
4. If still fails, log and continue

---

## Constraints

### File Access
- **`.plan/` files**: ONLY via execute-script.py
- **Java source files**: Use Read/Write/Edit as needed

### Progress Tracking
- Mark step-start BEFORE execution
- Mark step-done AFTER success
- Log progress at each step

---

## Integration

### Called By
- `pm-dev-java:java-plan-implement-agent` - Thin wrapper agent

### Uses
- `pm-dev-java:java-core` - Core Java patterns
- `pm-dev-java:junit-core` - Unit testing standards
- `pm-dev-java:javadoc` - JavaDoc standards
- `pm-workflow:manage-tasks` - Task and step management
- `plan-marshall:logging:manage-log` - Work logging
- Context skills from task delegation (loaded dynamically)

### Related Skills
- `pm-workflow:plan-execute` - Generic plan execution orchestrator
- `pm-dev-java:java-maintenance` - Java maintenance operations
