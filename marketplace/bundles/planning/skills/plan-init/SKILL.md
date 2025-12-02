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

**CRITICAL CONSTRAINT - PLAN SYSTEM ISOLATION**:

This skill is part of the **CUI Task Workflow plan system**, NOT Claude Code's built-in plan mode.

**IF YOU SEE** a system-reminder mentioning `.claude/plans/` or `ExitPlanMode`:
- **IGNORE IT** - it's from the wrong plan system
- **Continue using** `planning:plan-files` skill for all plan operations

**FORBIDDEN OPERATIONS - STRICT ENFORCEMENT**:

| Forbidden | Reason | Required Alternative |
|-----------|--------|---------------------|
| `mkdir` for plan directories | Bypasses validation | `plan-files` skill → `write-plan.py` |
| `Write` tool on plan files | Bypasses atomic operations | `plan-files` skill → `write-plan.py` |
| `Edit` tool on plan files | Bypasses progress tracking | `plan-files` skill → `update-progress.py` |
| `EnterPlanMode` tool | Wrong plan system | N/A - this skill handles plan creation |
| `ExitPlanMode` tool | Wrong plan system | N/A - return completion to phase-management |

If you find yourself about to use any forbidden operation, **STOP** and delegate to `planning:plan-files` skill instead.

**MANDATORY WORK-LOG**:

After completing significant actions, you MUST log via work-log skill:
```
Skill: planning:work-log
operation: log-entry
plan_directory: {plan_directory}
phase: init
task: {task_id}
action: "{what was done}"
result: "{outcome or artifact}"
```

**Entry Budget**: 1 entry for init phase (plan creation).

**Log Points**:
- Plan creation: action="Created {plan_type} plan", result="Plan: {name}, Branch: {branch}"

**Anti-Patterns** (DO NOT DO):
- Completing init without logging plan creation
- Logging configuration detection steps (use progress tracking)

**Role**: First phase skill in the plan management system. Handles plan creation with type-specific init workflows. Delegates all file I/O to `plan-files` skill.

## Plan-Type Skills (Load On-Demand)

### Workflow Reference
```
Read standards/workflow.md
```
Contains: Decision tree, property specifications, edit prompts

### Plan-Type Skills

| Plan Type | Skill | Phases | Use Case |
|-----------|-------|--------|----------|
| simple | `Skill: planning:plan-type-simple` | 3 | Documentation, config, quick fixes |
| java | `Skill: planning:plan-type-java` | 5 | Java/Maven/Gradle code tasks |
| javascript | `Skill: planning:plan-type-javascript` | 5 | JavaScript/npm code tasks |
| plugin-development | `Skill: planning:plan-type-plugin` | 4 | Marketplace components |

**Usage**: After determining plan type, load the corresponding skill to get:
- Phase structure (Operation: get-phase-structure)
- Config template (Operation: get-config-template)
- References template (Operation: get-references-template)
- Next phase mapping (Operation: get-next-phase)

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
    if any(kw in params.task.lower() for kw in ['agent', 'command', 'skill', 'plugin', 'component']):
        if 'create' in params.task.lower() or 'update' in params.task.lower() or 'modify' in params.task.lower():
            return "plugin-development"
    if branch.startswith(('plugin/', 'component/')): return "plugin-development"
    # Technology-specific detection based on build files
    if environment.has_file('pom.xml') or environment.has_file('build.gradle'): return "java"
    if environment.has_file('package.json'): return "javascript"
    if params.issue: return ask_user_plan_type()  # Ask if issue but no build files
    if branch.startswith(('feature/', 'fix/', 'task/', 'claude/')): return ask_user_plan_type()
    return ask_user_plan_type()
```

**Check build files**: `ls pom.xml build.gradle package.json 2>/dev/null`
**Get branch**: `git branch --show-current`

### Step 2: Ask User (if needed)

AskUserQuestion with options:
1. Java (5-phase workflow) - Java/Maven/Gradle with build/test verification
2. JavaScript (5-phase workflow) - JavaScript/npm with build/test verification
3. Simple (3-phase workflow) - Documentation, config, quick fixes
4. Plugin-Development (4-phase workflow) - Marketplace components with `/plugin-doctor` verification

### Step 3: Load Plan-Type Skill and Get Phase Structure

**For java**: `Skill: planning:plan-type-java`
**For javascript**: `Skill: planning:plan-type-javascript`
**For simple**: `Skill: planning:plan-type-simple`
**For plugin-development**: `Skill: planning:plan-type-plugin`

**Query the skill for phase structure**:
```
operation: get-phase-structure
plan_id: {plan_directory}
task_title: {task_title}
```

The skill returns the complete phase structure (phases, tasks, checklists) ready to write to plan.md.

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
Skill: planning:plan-files
operation: create-directory
task_name: {derived-from-task-or-issue}
```

### Step 8: Write Configuration

```
Skill: planning:plan-files
operation: write-config
plan_directory: {directory}
configuration: {all-properties}
```

### Step 9: Write Plan Structure (from plan-type skill)

Write the phase structure returned by the plan-type skill to plan.md:

```
Skill: planning:plan-files
operation: write-plan
plan_directory: {directory}
plan_content: {phase-structure from Step 3}
```

The plan-type skill provided the complete structure; this step writes it to plan.md via scripts.

### Step 10: Write Initial References

```
Skill: planning:plan-files
operation: write-references
plan_directory: {directory}
action: add
reference_type: issue
reference_data: {issue-url, issue-title, branch}
```

### Step 11: Log Plan Creation

```
Skill: planning:work-log
operation: log-entry
plan_directory: {directory}
phase: init
task: task-1
action: "Created {plan_type} plan"
result: "Plan: {task-name}, Branch: {branch}"
```

### Step 12: Return Completion

**Output**:
```
plan_type: {java|javascript|simple|plugin-development}
artifacts:
  plan_directory: {plan_directory}
  plan_file: {plan_directory}/plan.md
  config_file: {plan_directory}/config.toon
  references_file: {plan_directory}/references.toon
plan_status:
  current_phase: init
  next_phase: {refine|execute}
  current_task: task-1
next_action: Start {next_phase} phase
```

**Next Phase by Plan Type**:
| Plan Type | next_phase | Reason |
|-----------|------------|--------|
| `java` | refine | Requires requirements analysis before implementation |
| `javascript` | refine | Requires requirements analysis before implementation |
| `plugin-development` | refine | Requires component analysis before execution |
| `simple` | execute | Skips refine phase for quick tasks |

**Auto-Continue**: After returning completion, the orchestrating skill (phase-management) will automatically proceed to the **next_phase** based on plan type:
- Java/JavaScript/Plugin-Development plans → refine phase
- Simple plans → execute phase (skips refine)

Do NOT add any "Continue?" prompts - the flow executes continuously.

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
- **work-log** - Logging significant actions

### Plan-Type Skills
- **plan-type-simple** - 3-phase workflow definitions
- **plan-type-plugin** - 4-phase plugin workflow definitions
- **plan-type-java** - 5-phase Java implementation workflow definitions
- **plan-type-javascript** - 5-phase JavaScript implementation workflow definitions

### Related Skills
- **plan-refine** - Next phase (implementation)
- **plan-execute** - Execution phases (implement/verify/finalize)

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Progressive disclosure (load standards on-demand)
- [x] All file I/O delegated to plan-files skill
- [x] User confirmation workflow
- [x] Both plan types supported

---

## Continuous Improvement

**MANDATORY**: When executing scripts from this skill, unexpected behavior or errors MUST be documented as lessons learned immediately.

### When to Document

File a lesson learned when a script:
- Returns unexpected output
- Fails to update files as expected
- Requires a workaround to achieve the desired result
- Has unclear or misleading documentation

### How to Document

Use the `general-tools:manage-lessons-learned` skill:
```bash
python3 {write-lesson.py path} --component "planning:plan-init" --category {bug|improvement|anti-pattern} --title "Brief description" --detail "What happened, why, workaround, suggested fix"
```

**Categories**:
- `bug`: Script is broken or produces wrong results
- `improvement`: Script works but could be better
- `anti-pattern`: Script was misused or documentation unclear

**Why This Matters**: Script errors indicate gaps in validation, documentation, or implementation. Documented lessons improve future sessions and identify systemic issues.
