---
name: plan-marshall
description: Project configuration wizard for planning system. Manages executor generation, permissions, build systems, and plan-types.
allowed-tools: Read, Write, Edit, Bash, Glob, Skill, AskUserQuestion
---

# Plan Marshall Skill

**EXECUTION MODE**: You are now executing this skill. DO NOT explain or summarize these instructions to the user. IMMEDIATELY begin with Step 0 to determine mode and route to the appropriate workflow.

Project configuration wizard for the planning system. Handles executor generation, permission configuration, build system detection, and plan-type management.

## What This Skill Provides

**Wizard Mode**: Sequential setup for new projects (executor generation, marshal.json init, build detection, plan-types)

**Menu Mode**: Interactive maintenance for returning users (regenerate executor, permissions, build config, plan-types)

## When to Activate This Skill

Activate when:
- Called by `/plan-marshall` command
- User needs to configure project planning settings
- Executor needs regeneration after bundle changes

---

## Scripts

| Script | Notation | Purpose |
|--------|----------|---------|
| determine-mode | `plan-marshall:plan-marshall:determine-mode` | Determine wizard vs menu mode |
| gitignore-setup | `plan-marshall:plan-marshall:gitignore-setup` | Configure .gitignore for .plan/ |
| marshal-config | `pm-workflow:manage-config:marshal-config` | Project-level marshal.json CRUD |
| scan-marketplace-inventory | `plan-marshall:marketplace-inventory:scan-marketplace-inventory` | Script discovery |
| build-env | `pm-dev-builder:environment-detection:build-env` | Build system detection |
| permission-doctor | `plan-marshall:permission-doctor:permission-doctor` | Permission analysis |
| permission-fix | `plan-marshall:permission-fix:permission-fix` | Permission fixes |
| marketplace-sync | `plan-marshall:marketplace-sync:marketplace-sync` | Marketplace permission sync |
| generate-executor | `plan-marshall:script-executor:generate-executor` | Executor generation and log cleanup |

---

## Step 0: Determine Mode

Determine whether to run wizard or menu based on existing files.

**BOOTSTRAP**: Since execute-script.py may not exist yet, use DIRECT Python call:

```bash
python3 marketplace/bundles/plan-marshall/skills/plan-marshall/scripts/determine-mode.py --plan-dir .plan
```

**Output (TOON)**:
```toon
mode	wizard
reason	executor_missing
```

| mode | reason | Action |
|------|--------|--------|
| `wizard` | `executor_missing` | Run First-Run Wizard from Step 1 |
| `wizard` | `marshal_missing` | Run First-Run Wizard from Step 2 |
| `menu` | `both_exist` | Show Interactive Menu |

### Check for `--wizard` Flag

If `--wizard` flag provided, force first-run wizard regardless of determine-mode result.

---

## First-Run Wizard

Sequential structured setup for new projects. **CRITICAL**: Execute-script.py generation MUST be Step 1.

### Step 1: Gitignore Setup

Configure `.gitignore` for `.plan/` directory.

**BOOTSTRAP**: Use DIRECT Python call:

```bash
python3 marketplace/bundles/plan-marshall/skills/plan-marshall/scripts/gitignore-setup.py --project-root .
```

**Output (TOON)**:
```toon
status	created
gitignore_path	/path/to/.gitignore
entries_added	2
```

| status | Meaning |
|--------|---------|
| `created` | New .gitignore created with planning entries |
| `updated` | Existing .gitignore updated with planning entries |
| `unchanged` | Planning entries already present |

**NOTE**: `execute-script.py` is NOT tracked because it contains local absolute paths and must be regenerated per-machine.

### Step 2: Generate Executor

**BOOTSTRAP**: Since execute-script.py doesn't exist yet, use DIRECT Python call:

```bash
# Direct call - no executor dependency
python3 marketplace/bundles/plan-marshall/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py \
  --scope marketplace \
  --resource-types scripts
```

Parse the JSON output to extract script mappings. The output contains:
```json
{
  "bundles": [{
    "name": "planning",
    "scripts": [{
      "name": "manage-files",
      "skill": "manage-files",
      "notation": "pm-workflow:manage-files:manage-files",
      "path_formats": { "absolute": "/abs/path/manage-files.py" }
    }]
  }]
}
```

**Generate executor**:
1. Read template from: `marketplace/bundles/plan-marshall/skills/script-executor/templates/execute-script.py.template`
2. Replace `{{SCRIPT_MAPPINGS}}` with notation→path mappings
3. Replace `{{EXECUTION_LOG_DIR}}` with absolute path to executor scripts directory
4. Write to: `.plan/execute-script.py`

**Verify**:
```bash
python3 -m py_compile .plan/execute-script.py && echo "Executor syntax OK"
```

**Ensure executor permission** (prevents permission prompts when using executor):
```bash
python3 .plan/execute-script.py plan-marshall:marketplace-sync:marketplace-sync ensure-executor \
  --target global
```

**Output**: "Executor ready with N script mappings"

**NOTE**: From this point on, all script calls use: `python3 .plan/execute-script.py {notation} ...`

### Step 3: Initialize Marshal.json

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config init
```

**Output**: "Created .plan/marshal.json with defaults"

### Step 4: Build System Detection

```bash
python3 .plan/execute-script.py pm-dev-builder:environment-detection:build-env detect
```

Parse detected systems and prompt user:

```
AskUserQuestion:
  question: "Detected build systems: [Maven, npm]. Configure these?"
  options:
    - label: "Yes"
      description: "Configure detected build systems"
      value: "yes"
    - label: "No"
      description: "Skip build system configuration"
      value: "no"
```

If yes, update marshal.json with detected systems:
```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config build-systems set \
  --system maven --active true
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config build-systems set \
  --system npm --active true
```

### Step 5: Plan-Type Selection

```
AskUserQuestion:
  question: "Which plan-types should this project support? (select all that apply)"
  options:
    - label: "Java"
      description: "Maven/Gradle projects with Java/Kotlin"
      value: "java"
    - label: "JavaScript"
      description: "npm/TypeScript projects"
      value: "javascript"
    - label: "Plugin"
      description: "Claude Code marketplace development"
      value: "plugin"
    - label: "Generic only"
      description: "No domain-specific plan types"
      value: "generic"
```

For each selected type, configure domain agents:
```bash
# Example for Java
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config domain-agents set \
  --plan-type pm-workflow:plan-type-java \
  --solution-outline-agent pm-dev-java:java-solution-outline-agent \
  --task-plan-agent pm-dev-java:java-task-plan-agent
```

### Step 6: Custom Plan-Types

```
AskUserQuestion:
  question: "Define project-local plan-types?"
  options:
    - label: "Yes"
      description: "Create custom plan-type definitions"
      value: "yes"
    - label: "No"
      description: "Use only standard plan-types"
      value: "no"
```

If yes, run Custom Plan-Type Wizard (see below).

### Step 7: Permission Setup

```
AskUserQuestion:
  question: "Configure permissions now?"
  options:
    - label: "Yes"
      description: "Set up global and project permissions"
      value: "yes"
    - label: "Later"
      description: "Skip permission setup for now"
      value: "no"
```

If yes:
```bash
python3 .plan/execute-script.py plan-marshall:permission-fix:permission-fix apply-fixes --scope project
```

### Step 8: Summary

Output final summary:

```toon
status: success
operation: wizard_complete

gitignore: configured
executor:
  path: .plan/execute-script.py
  script_count: 45
marshal:
  path: .plan/marshal.json
build_systems:
  - maven
  - npm
plan_types:
  - pm-workflow:plan-type-java
  - pm-workflow:plan-type-javascript
  - pm-workflow:plan-type-generic
custom_types: 0

next_steps:
  - Run /plan-manage to create a new plan
  - Use /plan-marshall for maintenance tasks
```

---

## Interactive Menu (Returning User)

Display menu when both executor and marshal.json exist.

**MENU LOOP**: After completing any menu option (except Quit), return to this menu. Continue looping until user selects Quit.

```
AskUserQuestion:
  question: "What can I do for you?"
  options:
    - label: "1. Maintenance"
      description: "Regenerate executor, update mappings, clean logs"
      value: "maintenance"
    - label: "2. Permissions"
      description: "Update global/project permissions, sync wildcards"
      value: "permissions"
    - label: "3. Build System"
      description: "Detect and configure build systems"
      value: "build"
    - label: "4. Plan-Types"
      description: "Add/remove plan-types, define custom types"
      value: "plan-types"
    - label: "5. Full Reconfigure"
      description: "Run first-run wizard again"
      value: "wizard"
    - label: "6. Quit"
      description: "Exit plan-marshall"
      value: "quit"
```

**Routing**:
| Selection | Action |
|-----------|--------|
| maintenance | Execute "Menu Option: Maintenance", then **return to menu** |
| permissions | Execute "Menu Option: Permissions", then **return to menu** |
| build | Execute "Menu Option: Build System", then **return to menu** |
| plan-types | Execute "Menu Option: Plan-Types", then **return to menu** |
| wizard | Execute "First-Run Wizard", then **return to menu** |
| quit | Output "Good bye!" and **stop execution** |

---

## Menu Option: Maintenance

### Regenerate Executor

```bash
python3 marketplace/bundles/plan-marshall/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py \
  --scope marketplace \
  --resource-types scripts
```

Regenerate executor file with fresh mappings.

### Update Script Mappings

Same as regenerate but incremental - only add new scripts.

### Clean Old Logs

```bash
python3 .plan/execute-script.py plan-marshall:script-executor:generate-executor cleanup --max-age-days 30
```

---

## Menu Option: Permissions

### Step 1: Diagnose Permissions (always run first)

**Detect redundant permissions** (local duplicates of global):
```bash
python3 .plan/execute-script.py plan-marshall:permission-doctor:permission-doctor detect-redundant --scope both
```

**Detect suspicious permissions** in global settings:
```bash
python3 .plan/execute-script.py plan-marshall:permission-doctor:permission-doctor detect-suspicious --scope global
```

**Detect suspicious permissions** in project settings:
```bash
python3 .plan/execute-script.py plan-marshall:permission-doctor:permission-doctor detect-suspicious --scope project
```

### Step 2: Apply Fixes

**Apply safe fixes** to global settings:
```bash
python3 .plan/execute-script.py plan-marshall:permission-fix:permission-fix apply-fixes --scope global
```

**Apply safe fixes** to project settings:
```bash
python3 .plan/execute-script.py plan-marshall:permission-fix:permission-fix apply-fixes --scope project
```

### Step 3: Manual Operations (if needed)

**Add permission** (use `--target global` or `--target project`):
```bash
python3 .plan/execute-script.py plan-marshall:permission-fix:permission-fix add --target global --permission "Skill(bundle:*)"
```

**Remove permission** (use `--target global` or `--target project`):
```bash
python3 .plan/execute-script.py plan-marshall:permission-fix:permission-fix remove --target project --permission "Edit(.plan/**)"
```

**Note**: The `remove` and `add` commands use `--target`, while `apply-fixes` uses `--scope`.

### Sync Wildcards

```
SlashCommand: /tools-audit-permission-wildcards
```

---

## Menu Option: Build System

### Detect Build Systems

```bash
python3 .plan/execute-script.py pm-dev-builder:environment-detection:build-env detect
```

### Configure Build Mappings

| Detected | Skill | Verification Command |
|----------|-------|---------------------|
| Maven | `pm-dev-builder:builder-maven-rules` | `/pm-dev-builder:builder-build-and-fix` |
| Gradle | `pm-dev-builder:builder-gradle-rules` | `/pm-dev-builder:builder-build-and-fix` |
| npm | `pm-dev-builder:builder-npm-rules` | `/pm-dev-builder:builder-build-and-fix system=npm` |

### Update Verification Commands

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config plan-type-defaults set \
  --plan-type pm-workflow:plan-type-java \
  --verification-command "/pm-dev-builder:builder-build-and-fix"
```

---

## Menu Option: Plan-Types

### Add/Remove Plan-Types

```
AskUserQuestion:
  question: "Which plan-types to toggle?"
  options:
    - label: "Add Java"
      value: "add-java"
    - label: "Add JavaScript"
      value: "add-javascript"
    - label: "Add Plugin"
      value: "add-plugin"
    - label: "Remove a type"
      value: "remove"
```

### Define Custom Plan-Type

See Custom Plan-Type Wizard below.

### Update Domain Agent Mappings

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config domain-agents set \
  --plan-type {plan_type} \
  --solution-outline-agent {solution_outline_agent} \
  --task-plan-agent {task_plan_agent}
```

---

## Custom Plan-Type Wizard

Interactive flow for creating project-local plan-types:

```
AskUserQuestion:
  question: "Name for custom plan-type (kebab-case):"
  type: text
```

```
AskUserQuestion:
  question: "Description:"
  type: text
```

```
AskUserQuestion:
  question: "File patterns (comma-separated, e.g., *.java,*.kt):"
  type: text
```

```
AskUserQuestion:
  question: "Goals agent (or 'null' for none):"
  type: text
```

```
AskUserQuestion:
  question: "Plan agent (or 'null' for none):"
  type: text
```

Create custom plan-type:
1. Read template from `templates/custom-plan-type.md`
2. Create `.claude/plan-types/{name}/SKILL.md` with template
3. Add to marshal.json:

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config custom-types add \
  --name {name} \
  --skill-path .claude/plan-types/{name}/SKILL.md \
  --solution-outline-agent {solution_outline_agent} \
  --task-plan-agent {task_plan_agent}
```

---

## Output Format

All operations return TOON format:

**Success**:
```toon
status: success
operation: {operation_name}
data:
  key: value
```

**Error**:
```toon
status: error
error: {error_type}
message: {error_message}
recovery: {suggested_action}
```

---

## Error Handling

### Missing Executor

```toon
status: error
error: missing_executor
message: .plan/execute-script.py not found
recovery: Run first-run wizard to generate executor
```

### Invalid Marshal.json

```toon
status: error
error: invalid_config
message: Failed to parse marshal.json
recovery: Delete and re-run wizard, or fix JSON syntax
```

### Script Not Found

```toon
status: error
error: script_not_found
message: Script notation not found in executor
recovery: Regenerate executor via Maintenance menu
```

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/custom-plan-type.md` | SKILL.md template for custom plan-types |

---

## Quality Checklist

- [x] Detects first-run vs returning user
- [x] Bootstrap mechanism for executor generation
- [x] Gitignore configured correctly (execute-script.py NOT tracked)
- [x] All script calls use notation via executor (except bootstrap)
- [x] Interactive menu for returning users
- [x] Custom plan-type wizard
- [x] TOON output format
