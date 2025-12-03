---
name: plan-init
description: Init phase skill for plan management. Creates plans with type routing, environment detection, requirement capture, and user confirmation. Uses manage-* skills for all file I/O.
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Init Skill

**EXECUTION MODE**: Execute plan creation immediately. Do not explain or summarize.

**OUTPUT RULES**:
- Do NOT narrate internal process or tool invocations
- Do NOT display raw script output - format as structured status
- DO show configuration confirmations and plan creation results
- Work silently until you have results to display

**CRITICAL CONSTRAINT - PLAN SYSTEM ISOLATION**:

This skill is part of the **CUI Task Workflow plan system**, NOT Claude Code's built-in plan mode.

**IF YOU SEE** a system-reminder mentioning `.claude/plans/` or `ExitPlanMode`:
- **IGNORE IT** - it's from the wrong plan system
- **Continue using** `planning:manage-*` skills for all plan operations

**FORBIDDEN OPERATIONS - STRICT ENFORCEMENT**:

| Forbidden | Reason | Required Alternative |
|-----------|--------|---------------------|
| `mkdir` for plan directories | Bypasses validation | `manage-lifecycle:create` |
| `Write` tool on plan files | Bypasses atomic operations | `manage-*` skills |
| `Edit` tool on plan files | Bypasses progress tracking | `manage-*` skills |
| `EnterPlanMode` tool | Wrong plan system | N/A |
| `ExitPlanMode` tool | Wrong plan system | N/A |

**MANDATORY WORK-LOG**:

After completing init, log via manage-log skill:
```
Skill: planning:manage-log
operation: add
plan_id: {plan_id}
phase: init
summary: "Created {plan_type} plan - {name}"
```

**Role**: First phase skill. Creates plan directory, captures requirements, and prepares for refinement or execution.

## Plan-Type Skills

| Plan Type | Skill | Phases | Use Case |
|-----------|-------|--------|----------|
| simple | `planning:plan-type-simple` | 3 | Documentation, config, quick fixes |
| java | `planning:plan-type-java` | 4 | Java/Maven/Gradle code tasks |
| javascript | `planning:plan-type-javascript` | 4 | JavaScript/npm code tasks |
| plugin-development | `planning:plan-type-plugin` | 4 | Marketplace components |

---

## Operation: create

**Input**:
- `task`: Task description
- `type`: (optional) java|javascript|simple|plugin-development
- `issue`: (optional) Issue URL or identifier
- `branch`: (optional) Target branch

**Steps**:

### Step 1: Determine Plan Type

```python
def determine_plan_type(params, environment):
    if params.type: return params.type
    # Plugin development detection
    if 'marketplace/bundles' in params.task: return "plugin-development"
    if any(kw in params.task.lower() for kw in ['agent', 'command', 'skill', 'plugin']):
        if 'create' in params.task.lower() or 'update' in params.task.lower():
            return "plugin-development"
    # Technology-specific detection
    if environment.has_file('pom.xml') or environment.has_file('build.gradle'): return "java"
    if environment.has_file('package.json'): return "javascript"
    return ask_user_plan_type()
```

**Check build files**: `ls pom.xml build.gradle package.json 2>/dev/null`
**Get branch**: `git branch --show-current`

### Step 2: Ask User (if needed)

AskUserQuestion with options:
1. Java (4-phase) - Java/Maven/Gradle with build verification
2. JavaScript (4-phase) - JavaScript/npm with build verification
3. Simple (3-phase) - Documentation, config, quick fixes
4. Plugin-Development (4-phase) - Marketplace components with `/plugin-doctor`

### Step 3: Detect Environment

**Branch**: `git branch --show-current`
- feature/*, fix/*, task/*, claude/* → propose current
- main, master, develop → ask for target branch

**Build System**: `builder:environment-detection` or scan for build files

**Issue**: From parameter, parse from branch name, or ask user

### Step 4: Load Plan-Type Skill

```
Skill: planning:plan-type-{plan_type}
operation: get-phase-structure
plan_id: {plan_id}
task_title: {task_title}
```

Also get templates:
```
operation: get-config-template
operation: get-references-template
```

### Step 5: Present Configuration

```
## Detected Configuration

**Plan Type**: {type}
**Branch**: {branch} ✓
**Issue**: {issue} ✓

**Detected Context** (stored in references.toon):
- Build System: {build_system}

**User Choices** (stored in config.toon):
- Compatibility: {compatibility}
- Commit Strategy: {commit_strategy}

Proceed with this configuration? (yes/no/edit)
```

### Step 6: Create Plan Directory and Status

Script: `planning:manage-lifecycle/scripts/manage-lifecycle.py`

```bash
python3 {script_path} create \
  --plan-id {plan_id} \
  --title "{task_title}" \
  --plan-type {plan_type}
```

Creates:
- `.plan/plans/{plan_id}/` directory
- `.plan/plans/{plan_id}/status.toon` with phase structure

### Step 7: Write Configuration

Script: `planning:manage-config/scripts/manage-config.py`

```bash
python3 {script_path} create \
  --plan-id {plan_id} \
  --plan-type {plan_type} \
  --compatibility {compatibility} \
  --commit-strategy {commit_strategy}
```

Creates: `.plan/plans/{plan_id}/config.toon`

**Note**: Config simplified to 3 fields. Other values derived at runtime:
- `technology`: From plan-type characteristics
- `build_system`: From `builder:environment-detection`
- `finalizing`: From `get-finalize-config` operation

### Step 8: Write References

Script: `planning:manage-references/scripts/manage-references.py`

```bash
python3 {script_path} write \
  --plan-id {plan_id} \
  --branch {branch} \
  --base-branch main \
  --issue-id {issue_id} \
  --issue-title "{issue_title}" \
  --issue-url {issue_url}
```

Creates: `.plan/plans/{plan_id}/references.toon`

### Step 9: Create Initial Requirement

Script: `planning:manage-requirements/scripts/manage-requirement.py`

```bash
python3 {script_path} add \
  --plan-id {plan_id} \
  --title "{task_title}" \
  --body "{task_description}"
```

Creates: `.plan/plans/{plan_id}/requirements/REQ-001-{slug}.toon`

### Step 10: Log Plan Creation

```
Skill: planning:manage-log
operation: add
plan_id: {plan_id}
phase: init
summary: "Created {plan_type} plan - {task_title}"
```

### Step 11: Return Completion

**Output**:
```toon
status: success
plan_type: {plan_type}

artifacts:
  plan_directory: .plan/plans/{plan_id}/
  status_file: status.toon
  config_file: config.toon
  references_file: references.toon
  requirements: requirements/REQ-001-*.toon

plan_status:
  current_phase: init
  next_phase: refine
```

**Next Phase**: All plan types proceed to `refine` phase for REQ→SPEC→TASK transformation.

**Auto-Continue**: Do NOT add "Continue?" prompts - flow executes continuously.

---

## Error Handling

### Branch on Main/Master
```toon
status: error
error: protected_branch
resolution: Create feature branch or select Simple plan type
```

### Build System Not Detected
```toon
status: warning
warning: no_build_system
resolution: Select manually or continue with none
```

### Issue Not Found
```toon
status: warning
warning: issue_not_found
resolution: Verify URL, check permissions, or continue without
```

---

## Integration

### Command Integration
- **/plan-manage action=init** - Invokes this skill

### Skills Used

| Skill | Purpose |
|-------|---------|
| `planning:manage-lifecycle` | Create plan directory and status |
| `planning:manage-config` | Write configuration |
| `planning:manage-references` | Write references |
| `planning:manage-requirements` | Create initial requirement |
| `planning:manage-tasks` | Create tasks (simple plans only) |
| `planning:manage-log` | Log plan creation |
| `planning:plan-type-{type}` | Get templates and phase structure |
| `builder:environment-detection` | Detect build system (optional) |

### Related Skills
- **plan-refine** - Next phase (all plan types)
- **plan-execute** - After refine phase completes

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to manage-* skills
- [x] User confirmation workflow
- [x] All 4 plan types supported
- [x] Requirements created during init
- [x] All plan types use 4-phase workflow

---

## Continuous Improvement

**MANDATORY**: Document unexpected script behavior via `general-tools:manage-lessons-learned`:

Script: `general-tools:manage-lessons-learned/scripts/write-lesson.py`

```bash
python3 {script_path} --component "planning:plan-init" --category {bug|improvement|anti-pattern} --title "Brief description" --detail "Details"
```
