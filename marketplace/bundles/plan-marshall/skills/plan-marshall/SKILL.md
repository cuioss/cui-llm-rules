---
name: plan-marshall
description: Project configuration wizard for planning system. Manages executor generation, health checks, build systems, and plan-types.
allowed-tools: Read, Write, Edit, Bash, Glob, Skill, AskUserQuestion
---

# Plan Marshall Skill

## Enforcement Rules

**EXECUTION MODE**: Execute this skill immediately. Do not explain, summarize, or discuss these instructions.

### Script Execution
1. Run scripts EXACTLY as documented - no improvisation
2. Use the bash commands verbatim from each section
3. Bootstrap scripts (Step 0, Step 1, Step 2) use direct Python paths
4. All other scripts use: `python3 .plan/execute-script.py {notation} ...`

### Menu Behavior
1. Main Menu and submenus use EXACTLY 4 options as documented
2. After ANY operation completes → return to Main Menu
3. Only exit when user selects "Quit"

### Prohibited Actions
- Inventing alternative menu structures or options
- Skipping submenus to go directly to operations
- Ending without returning to menu (unless Quit)
- Checking files manually instead of running documented scripts
- Summarizing what you're about to do instead of doing it

### Execution Flow
```
Step 0: determine-mode.py
    ↓
mode=wizard → First-Run Wizard (Steps 1-8)
mode=menu   → Interactive Menu Loop
```

---

## What This Skill Provides

**Wizard Mode**: Sequential setup for new projects (executor generation, marshal.json init, build detection, plan-types)

**Menu Mode**: Interactive maintenance for returning users (regenerate executor, health check, configuration)

---

## Scripts

| Script | Notation | Purpose |
|--------|----------|---------|
| determine-mode | `plan-marshall:plan-marshall:determine-mode` | Determine wizard vs menu mode |
| gitignore-setup | `plan-marshall:plan-marshall:gitignore-setup` | Configure .gitignore for .plan/ |
| cleanup-temp | `plan-marshall:plan-marshall:cleanup-temp` | Clean temp directories and old files |
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
python3 marketplace/bundles/plan-marshall/skills/plan-marshall/scripts/determine-mode.py mode
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

Sequential structured setup for new projects.

### Step 1: Gitignore Setup

Configure `.gitignore` for `.plan/` directory.

**BOOTSTRAP**: Use DIRECT Python call:

```bash
python3 marketplace/bundles/plan-marshall/skills/plan-marshall/scripts/gitignore-setup.py
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

### Step 1b: Update Project Documentation

Check if project docs need `.plan/temp/` documentation:

**BOOTSTRAP**: Use DIRECT Python call (executor not yet available):

```bash
python3 marketplace/bundles/plan-marshall/skills/plan-marshall/scripts/determine-mode.py check-docs
```

**Output (TOON)**:
```toon
status	ok
files_needing_update	0
```

Or if updates needed:
```toon
status	needs_update
files_needing_update	2
missing	CLAUDE.md,agents.md
```

If `status` is `needs_update`, add to each listed file's appropriate section:
```
- Use `.plan/temp/` for ALL temporary files (covered by `Write(.plan/**)` permission - avoids permission prompts)
```

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

### Main Menu

```
AskUserQuestion:
  question: "What would you like to do?"
  header: "Main Menu"
  options:
    - label: "1. Maintenance"
      description: "Regenerate executor, clean logs"
    - label: "2. Health Check"
      description: "Verify setup, diagnose issues"
    - label: "3. Configuration"
      description: "Build systems, plan-types"
    - label: "4. Quit"
      description: "Exit plan-marshall"
  multiSelect: false
```

### Routing

| User Selection | Action | After Completion |
|----------------|--------|------------------|
| "1. Maintenance" | → Jump to "Menu Option: Maintenance" | → Return to Main Menu |
| "2. Health Check" | → Jump to "Menu Option: Health Check" | → Return to Main Menu |
| "3. Configuration" | → Jump to "Menu Option: Configuration" | → Return to Main Menu |
| "4. Quit" | Output "Good bye!" | → STOP (only valid exit) |

---

## Menu Option: Maintenance

Sub-menu for maintenance operations.

### Maintenance Submenu

```
AskUserQuestion:
  question: "Which maintenance operation?"
  header: "Maintenance"
  options:
    - label: "1. All"
      description: "Regenerate executor + clean logs/temp (recommended)"
    - label: "2. Regenerate Executor"
      description: "Rebuild executor with fresh script mappings"
    - label: "3. Clean Old Logs"
      description: "Remove execution logs older than 30 days"
    - label: "4. Back"
      description: "Return to main menu"
  multiSelect: false
```

### Routing

| User Selection | Action | After Completion |
|----------------|--------|------------------|
| "1. All" | Execute regenerate + clean (below) | → Return to Main Menu |
| "2. Regenerate Executor" | Execute regenerate only (below) | → Return to Main Menu |
| "3. Clean Old Logs" | Execute clean only (below) | → Return to Main Menu |
| "4. Back" | Do nothing | → Return to Main Menu |

### Operation: All (Regenerate + Clean)

Execute BOTH operations in sequence:

1. Execute "Operation: Regenerate Executor" (below)
2. Execute "Operation: Clean Old Logs" (below)

**Output**: Combined summary of both operations.

### Operation: Regenerate Executor

```bash
python3 marketplace/bundles/plan-marshall/skills/script-executor/scripts/generate-executor.py generate
```

The script uses subcommands (`generate`, `verify`, `drift`, `paths`, `cleanup`), not positional arguments.

Verify syntax:
```bash
python3 -m py_compile .plan/execute-script.py && echo "Executor syntax OK"
```

**Output (TOON)**:
```toon
status	scripts_discovered	executor_generated	logs_cleaned
success	47	.plan/execute-script.py	0
```

### Clean Old Logs and Temp Files

Clean execution logs and temp files:

```bash
python3 .plan/execute-script.py plan-marshall:script-executor:generate-executor cleanup --max-age-days 30
```

Clean temp directory:
```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall:cleanup-temp clean
```

**NOTE**: The `.plan/temp/` directory is the default temp directory for ALL temporary files. It is covered by the existing `Write(.plan/**)` permission (avoiding permission prompts for `/tmp/`) and cleaned during maintenance.

### Update Project Documentation (if needed)

Check if project docs need `.plan/temp/` documentation:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall:determine-mode check-docs
```

**Output (TOON)**:
```toon
status	ok
files_needing_update	0
```

Or if updates needed:
```toon
status	needs_update
files_needing_update	2
missing	CLAUDE.md,agents.md
```

If `status` is `needs_update`, add to each listed file:
```
- Use `.plan/temp/` for ALL temporary files (covered by `Write(.plan/**)` permission - avoids permission prompts)
```

---

## Menu Option: Health Check

Verify the planning system setup and diagnose issues. Run all checks and report results.

### Step 1: Verify Executor

Check executor exists, is valid, and in sync with marketplace:

```bash
python3 .plan/execute-script.py plan-marshall:script-executor:generate-executor verify
```

**Output (TOON)**:
```toon
status	script_count
ok	47
```

If status is `error` or executor missing: Offer to regenerate via Maintenance menu.

### Step 2: Check Executor Drift

Compare executor mappings with current marketplace state:

```bash
python3 .plan/execute-script.py plan-marshall:script-executor:generate-executor drift
```

**Output (TOON)**:
```toon
status	added	removed	changed
ok	0	0	0
```

If drift detected (added/removed/changed > 0): Offer to regenerate executor.

### Step 3: Verify Plugin Wildcards

Check that enabled plugins have corresponding Skill/SlashCommand wildcards:

```bash
python3 .plan/execute-script.py plan-marshall:permission-fix:permission-fix ensure-wildcards \
  --settings ~/.claude/settings.json \
  --marketplace-json marketplace/.claude-plugin/marketplace.json \
  --dry-run
```

**Interpret results**:
- `added: []` → All wildcards present ✓
- `added: [...]` → Missing wildcards, offer to add them

If missing wildcards found, ask user:
```
AskUserQuestion:
  question: "Found {N} missing plugin wildcards. Add them?"
  options:
    - label: "Yes"
      description: "Add missing wildcards to global settings"
      value: "yes"
    - label: "No"
      description: "Skip (may cause permission prompts)"
      value: "no"
```

If yes, run without `--dry-run`.

### Step 4: Check for Stale Permissions

Detect permissions for bundles that no longer exist:

```bash
python3 .plan/execute-script.py plan-marshall:permission-doctor:permission-doctor detect-redundant --scope both
```

Report any redundant or stale permissions found.

### Step 5: Summary

Output health check summary:

```toon
status: success
operation: health_check

executor:
  valid: true
  script_count: 47
  drift: none
wildcards:
  total: 16
  missing: 0
redundant_permissions: 0

overall: HEALTHY
```

Or if issues found:

```toon
status: warning
operation: health_check

executor:
  valid: true
  script_count: 47
  drift: 3 added, 1 removed
wildcards:
  total: 16
  missing: 2
redundant_permissions: 3

issues:
  - Executor drift detected (regenerate recommended)
  - 2 plugin wildcards missing
  - 3 redundant permissions in project settings

fixes_available: true
```

---

## Menu Option: Configuration

Sub-menu for build systems and plan-types configuration.

```
AskUserQuestion:
  question: "What would you like to configure?"
  options:
    - label: "Build Systems"
      description: "Detect and configure Maven/Gradle/npm"
      value: "build"
    - label: "Plan-Types"
      description: "Add/remove plan-types, define custom types"
      value: "plan-types"
    - label: "Full Reconfigure"
      description: "Run first-run wizard again"
      value: "wizard"
    - label: "Back"
      description: "Return to main menu"
      value: "back"
```

**Routing**:
| Selection | Action |
|-----------|--------|
| build | Execute "Configuration: Build System" |
| plan-types | Execute "Configuration: Plan-Types" |
| wizard | Execute "First-Run Wizard" |
| back | Return to main menu |

---

## Configuration: Build System

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

## Configuration: Plan-Types

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
