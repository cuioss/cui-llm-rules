# First-Run Wizard Flow

Sequential structured setup for new projects. Execute steps in order.

---

## Step 1: Gitignore Setup

Configure `.gitignore` for `.plan/` directory.

**BOOTSTRAP**: Use DIRECT Python call with glob:

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/*/skills/marshall-steward/scripts/gitignore-setup.py
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

---

## Step 1b: Update Project Documentation

Check if project docs need `.plan/temp/` documentation:

**BOOTSTRAP**: Use DIRECT Python call with glob (executor not yet available):

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/*/skills/marshall-steward/scripts/determine-mode.py check-docs
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

---

## Step 1c: Ensure Executor Permission

Add the executor permission to project-local settings so script execution doesn't prompt:

**BOOTSTRAP**: Use DIRECT Python call with glob:

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/*/skills/permission-fix/scripts/permission-fix.py ensure \
  --permissions "Bash(python3 .plan/execute-script.py *)" \
  --target project
```

**Output (TOON)**:
```toon
status	added
permission	Bash(python3 .plan/execute-script.py *)
target	project
settings_file	/path/to/.claude/settings.local.json
```

| status | Meaning |
|--------|---------|
| `added` | Permission added to project settings |
| `exists` | Permission already present |

This ensures script execution works without prompting, independent of global settings.

---

## Step 2: Generate Executor

**BOOTSTRAP**: Since execute-script.py doesn't exist yet, use DIRECT Python call with glob:

```bash
# Direct call - no executor dependency (auto-detects marketplace or plugin-cache)
python3 ${PLUGIN_ROOT}/plan-marshall/*/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py \
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
1. Read template from: `${PLUGIN_ROOT}/plan-marshall/*/skills/script-executor/templates/execute-script.py.template`
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

---

## Step 3: Initialize Marshal.json

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config init
```

**Output**: "Created .plan/marshal.json with defaults"

---

## Step 4: Build System and Module Detection

Detect build systems, modules, profiles, and generate canonical commands.

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist
```

**Output (TOON)**:
```toon
status: success
build_systems: maven,npm
modules_updated: 3
commands_generated: 18

modules[3]{name,path,type,commands_count}:
default	.	pom	4
oauth-sheriff-core	oauth-sheriff-core	jar	8
oauth-sheriff-ui	oauth-sheriff-ui	npm	6
```

Display to user:
```
Build Systems: Maven, npm
Modules detected: 3
  - default (pom, 4 commands)
  - oauth-sheriff-core (jar, 8 commands)
  - oauth-sheriff-ui (npm, 6 commands)
```

This single command:
- Detects available build systems (Maven, Gradle, npm)
- Detects project modules (Maven modules, Gradle subprojects, npm workspaces)
- Detects module types (pom, jar, war, quarkus, npm) for command filtering
- Detects Maven/Gradle profiles and maps to canonical command names
- Generates full command strings using **canonical command vocabulary**
- Supports **hybrid modules** (Maven + npm) with nested command format
- Persists to `modules.{name}.commands` in marshal.json
- Updates `build_systems[]` for skill reference

### Profile Detection

For projects with Maven/Gradle profiles, the persist command automatically detects and classifies them:

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-profiles
```

**Output (TOON)**:
```toon
status: success
module: default
path: /path/to/project
count: 3

profiles[3]{id,canonical,activation_type}:
integration-tests	integration-tests	command-line
coverage	coverage	command-line
benchmark	performance	command-line
```

Profile-based commands are automatically included in `persist` output with appropriate activation flags (-P or -D).

### Canonical Command Names

Commands use a fixed vocabulary for programmatic lookup by plan execution agents:

| Canonical | Description |
|-----------|-------------|
| `module-tests` | Unit tests for the module |
| `integration-tests` | Integration/E2E tests |
| `quality-gate` | Pre-commit checks (lint, format, static analysis) |
| `verify` | Full build verification |
| `coverage` | Test coverage reports |
| `performance` | Benchmark/performance tests |
| `install` | Install to local repository |
| `package` | Create distributable package |

### Hybrid Module Support

Modules with multiple build systems (e.g., Maven + npm) get nested command format:

```json
{
  "module-tests": {
    "maven": "python3 .plan/execute-script.py ... --goals \"clean test\"",
    "npm": "python3 .plan/execute-script.py ... --command \"run test\""
  }
}
```

Use `lookup --build-system maven` or `lookup --build-system npm` to get specific command

### 4b: Skill Domain Detection

Detect skill domains based on project files (pom.xml → java, package.json → javascript):

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains detect
```

This populates `skill_domains` in marshal.json with the nested structure:
- `{domain}.workflow_skills` - workflow phase skills
- `{domain}.core` - foundation skills (defaults + optionals)
- `{domain}.implementation` - implementation profile skills
- `{domain}.testing` - testing profile skills

---

## Step 5: Verify Skill Domain Configuration

Skill domains configure which implementation skills are loaded during plan execution. The thin agent architecture routes skills via `config.toon`'s workflow_skills block.

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains list
```

**Expected output**: Shows configured domains with their workflow_skills mappings:
```json
{
  "java": {
    "workflow_skills": {
      "solution_outline": "pm-plugin-development:plugin-solution-outline",
      "task_plan": "pm-plugin-development:plugin-task-plan",
      "implementation": "pm-plugin-development:plugin-plan-implement",
      "testing": "pm-plugin-development:plugin-plan-implement"
    },
    "core": {...},
    "implementation": {...},
    "testing": {...}
  }
}
```

**Note**: The pm-workflow thin agents (solution-outline-agent, task-plan-agent, task-execute-agent) load domain-specific skills dynamically based on deliverable.domain from config.toon.

---

## Step 6: Detect CI Provider

Detect CI provider and verify tools:

```bash
python3 .plan/execute-script.py plan-marshall:ci-operations:ci_health status
```

Display detection result to user. If tool not authenticated, warn:
- "GitHub detected but 'gh' not authenticated. Run 'gh auth login' for CI operations."
- "GitLab detected but 'glab' not authenticated. Run 'glab auth login' for CI operations."

Persist CI configuration to marshal.json:
```bash
python3 .plan/execute-script.py plan-marshall:ci-operations:ci_health persist
```

**Output**: CI configuration persisted to marshal.json with detected provider and authenticated tools.

---

## Step 7: Permission Setup

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

---

## Step 8: Summary

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
modules:
  count: 3
  commands_generated: 15
skill_domains:
  - java
  - javascript
  - plugin

next_steps:
  - Run /plan-manage to create a new plan
  - Use /marshall-steward for maintenance tasks
```

After summary output, wizard is complete. Exit skill execution.
