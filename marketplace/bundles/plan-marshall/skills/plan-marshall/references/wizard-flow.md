# First-Run Wizard Flow

Sequential structured setup for new projects. Execute steps in order.

---

## Step 1: Gitignore Setup

Configure `.gitignore` for `.plan/` directory.

**BOOTSTRAP**: Use DIRECT Python call with glob:

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/*/skills/plan-marshall/scripts/gitignore-setup.py
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
python3 ${PLUGIN_ROOT}/plan-marshall/*/skills/plan-marshall/scripts/determine-mode.py check-docs
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

## Step 4: Project Detection

Detect build systems, skill domains, and modules from project structure.

### 4a: Build System Detection

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

If yes, auto-detect and add build systems to marshal.json:
```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems detect
```

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

### 4c: Module Detection

For multi-module projects, detect modules and infer their domains/build systems:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules detect
```

This populates `modules` in marshal.json with per-module domain and build system mappings.

**Note**: Module detection infers domains from module content (e.g., nested `package.json` → javascript domain for that module).

---

## Step 5: Plan-Type Selection

Plan-types are automatically available based on installed skills. The following plan-types are provided by the marketplace:

| Plan-Type | Skill | Description |
|-----------|-------|-------------|
| Java | `pm-workflow:plan-type-java` | Maven/Gradle projects with Java/Kotlin |
| JavaScript | `pm-workflow:plan-type-javascript` | npm/TypeScript projects |
| Plugin | `pm-workflow:plan-type-plugin` | Claude Code marketplace development |
| Generic | `pm-workflow:plan-type-generic` | Documentation, config, quick fixes |

**Note**: Domain agents and plan defaults are defined in plan-type skill frontmatter (`patterns:`, `keywords:`, `domain:`, `plan_defaults:`), not in marshal.json. No configuration is required - plan-types are discovered automatically.

---

## Step 6: Custom Plan-Types

Custom plan-types require creating new plan-type skills with appropriate frontmatter (`patterns:`, `keywords:`, `domain:`, `plan_defaults:`).

```
AskUserQuestion:
  question: "Define project-local plan-types?"
  options:
    - label: "Yes"
      description: "Create custom plan-type skill"
      value: "yes"
    - label: "No"
      description: "Use only standard plan-types"
      value: "no"
```

If yes:
```
Read references/plan-type-wizard.md
```
Execute the Custom Plan-Type Wizard workflow from that file. This creates a new plan-type skill in the project's bundle.

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
plan_types:
  - pm-workflow:plan-type-java
  - pm-workflow:plan-type-javascript
  - pm-workflow:plan-type-generic
custom_types: 0

next_steps:
  - Run /plan-manage to create a new plan
  - Use /plan-marshall for maintenance tasks
```

After summary output, wizard is complete. Exit skill execution.
