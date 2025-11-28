---
name: plan-init
description: Init phase skill for plan management. Creates plans with type routing (implementation or simple), environment detection, and user confirmation. Produces complete phase structure for subsequent phases.
allowed-tools: Read, Write, Bash, Skill, AskUserQuestion
---

# Plan Init Skill

**EXECUTION MODE**: Execute plan creation immediately. Do not explain or summarize.

**OUTPUT RULES**:
- Do NOT narrate internal process or tool invocations
- Do NOT display raw script output - format as structured status
- DO show configuration confirmations and plan creation results
- Work silently until you have results to display

**Role**: First phase skill in the plan management system. Handles plan creation with type-specific init workflows. Delegates all file I/O to `plan-files` skill.

## Standards (Load On-Demand)

### Workflow
```
Read standards/workflow.md
```
Contains: Decision tree, plan types, property specifications, edit prompts

### Implementation Init
```
Read standards/implementation-init.md
```
Contains: Full 5-phase workflow, phase structure template

### Simple Init
```
Read standards/simple-init.md
```
Contains: Lightweight 3-phase workflow, minimal configuration

### Plugin Development Init
```
Read standards/plugin-development.md
```
Contains: 3-phase workflow with mandatory `/plugin-doctor` verification for marketplace components

---

## Operation: create

**Input**:
- `task`: Task description
- `type`: (optional) implementation|simple
- `issue`: (optional) Issue URL or identifier
- `branch`: (optional) Target branch

**Steps**:

### Step 1: Determine Plan Type

```python
def determine_plan_type(params, environment):
    if params.type: return params.type
    if params.issue: return "implementation"
    # Plugin development detection
    if 'marketplace/bundles' in params.task: return "plugin-development"
    if any(kw in params.task.lower() for kw in ['agent', 'command', 'skill', 'plugin', 'component']):
        if 'create' in params.task.lower() or 'update' in params.task.lower() or 'modify' in params.task.lower():
            return "plugin-development"
    if branch.startswith(('plugin/', 'component/')): return "plugin-development"
    # Standard implementation detection
    if environment.has_build_files(): return "implementation"
    if branch.startswith(('feature/', 'fix/', 'task/', 'claude/')): return "implementation"
    return ask_user_plan_type()
```

**Check build files**: `ls pom.xml build.gradle package.json 2>/dev/null`
**Get branch**: `git branch --show-current`

### Step 2: Ask User (if needed)

AskUserQuestion with options:
1. Implementation (5-phase workflow) - Code development with build/test verification
2. Simple (3-phase workflow) - Documentation, config, quick fixes
3. Plugin-Development (3-phase workflow) - Marketplace components with `/plugin-doctor` verification

### Step 3: Load Init Implementation

**For implementation**: `Read standards/implementation-init.md`
**For simple**: `Read standards/simple-init.md`
**For plugin-development**: `Read standards/plugin-development.md`

### Step 4: Detect Environment

**Branch**: `git branch --show-current`
- feature/*, fix/*, task/*, claude/* → propose current
- main, master, develop → ask for target (implementation only)

**Build System**: Delegate to `builder:environment-detection` or scan for pom.xml, build.gradle, package.json

**Issue**: From parameter, parse from branch name, or ask user

### Step 5: Configure Properties

Use AskUserQuestion if property unknown. See `standards/workflow.md` for property prompts.

### Step 6: Present Configuration

```
## Detected Configuration

**Plan Type**: {type}
**Branch**: {branch} ✓
**Issue**: {issue} ✓
**Build System**: {build_system} ✓
**Technology**: {technology} ✓

**Defaults Applied**:
- Compatibility: {compatibility}
- Commit Strategy: {commit_strategy}
- Finalizing: {finalizing}

Proceed with this configuration? (yes/no/edit)
```

### Step 7: Create Plan Directory

```
Skill: cui-task-workflow:plan-files
operation: create-directory
task_name: {derived-from-task-or-issue}
```

### Step 8: Write Configuration

```
Skill: cui-task-workflow:plan-files
operation: write-config
plan_directory: {directory}
configuration: {all-properties}
```

### Step 9: Write Plan Structure

```
Skill: cui-task-workflow:plan-files
operation: write-plan
plan_directory: {directory}
plan_content:
  title: {task-title}
  current_phase: init
  current_task: task-1
  phases: {phase-structure}
```

### Step 10: Write Initial References

```
Skill: cui-task-workflow:plan-files
operation: write-references
plan_directory: {directory}
action: add
reference_type: issue
reference_data: {issue-url, issue-title, branch}
```

### Step 11: Return Completion

**Output**:
```
plan_type: {implementation|simple}
artifacts:
  plan_directory: .claude/plans/{task-name}/
  plan_file: .claude/plans/{task-name}/plan.md
  config_file: .claude/plans/{task-name}/config.md
  references_file: .claude/plans/{task-name}/references.md
plan_status:
  current_phase: refine|execute
  current_task: task-1
next_action: Start {next-phase} phase
```

---

## Error Handling

### Branch on Main/Master (Implementation)
```
error: protected_branch
resolution: Create feature branch or select Simple plan type
```

### Build System Not Detected
```
warning: no_build_system
resolution: Select manually or continue with none
```

### Issue Not Found
```
warning: issue_not_found
resolution: Verify URL, check permissions, or continue without
```

---

## Integration

### Command Integration
- **/plan-manage** - Primary command invoking this skill via phase-management (action=init)

### Skills Used
- **plan-files** - All file I/O operations
- **builder:environment-detection** - Build system detection (optional)
- **phase-management** - Orchestration (invokes this skill)

### Related Skills
- **plan-refine** - Next phase (implementation)
- **plan-implement** - Implement phase
- **plan-verify** - Verify phase
- **plan-finalize** - Finalize phase

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Progressive disclosure (load standards on-demand)
- [x] All file I/O delegated to plan-files skill
- [x] User confirmation workflow
- [x] Both plan types supported
