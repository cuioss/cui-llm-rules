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

### Step 4a: Detect Build Systems, Modules, and Profiles

First, detect what's available without persisting:

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-modules
```

**Output (TOON)**:
```toon
status: success
module_count: 3

modules[3]{name,path,build_systems,type}:
default	.	maven	pom
oauth-sheriff-core	oauth-sheriff-core	maven	jar
oauth-sheriff-ui	oauth-sheriff-ui	npm	npm
```

Then detect profiles for modules with build systems that support them:

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-profiles
```

**Output (TOON)**:
```toon
status: success
modules_with_profiles: 2

profiles[5]{module,id,canonical,activation_type}:
default	pre-commit	quality-gate	command-line
default	coverage	coverage	command-line
oauth-sheriff-core	integration-tests	integration-tests	command-line
oauth-sheriff-core	coverage	coverage	command-line
oauth-sheriff-core	benchmark	performance	command-line
```

Display detection summary:
```
Build Systems: Maven, npm
Modules detected: 3
  - default (pom)
  - oauth-sheriff-core (jar)
  - oauth-sheriff-ui (npm)

Profiles detected: 5
  - default: pre-commit → quality-gate, coverage → coverage
  - oauth-sheriff-core: integration-tests, coverage, benchmark → performance
```

---

### Step 4b: User Command Selection

**Tiered approach** to handle projects of all sizes:

#### Tier 1: Setup Mode Selection

```yaml
AskUserQuestion:
  question: "How do you want to configure module commands?"
  header: "Setup Mode"
  options:
    - label: "Auto-detect (Recommended)"
      description: "Use smart defaults based on module types and detected profiles"
    - label: "Customize per module"
      description: "Select commands for each module individually"
    - label: "Minimal"
      description: "Only required commands (module-tests, quality-gate, verify)"
  multiSelect: false
```

**Routing:**

| Selection | Action |
|-----------|--------|
| Auto-detect | Go to Tier 2 (if profiles detected) or directly to Step 4c |
| Customize | Go to Tier 3 (per-module selection) |
| Minimal | Go to Step 4c with `--minimal` flag |

---

#### Tier 2: Profile Confirmation (Auto-detect path)

Only shown if profiles were detected:

```yaml
AskUserQuestion:
  question: "Detected specialized profiles in 2 modules. Include them?"
  header: "Profiles"
  multiSelect: true
  options:
    - label: "oauth-sheriff-core: integration-tests"
      description: "Integration tests (mvn verify -Pintegration-tests)"
    - label: "oauth-sheriff-core: coverage"
      description: "JaCoCo coverage (mvn verify -Pcoverage)"
    - label: "oauth-sheriff-core: benchmark → performance"
      description: "JMH benchmarks (mvn verify -Pbenchmark)"
    - label: "default: coverage"
      description: "Coverage reporting (mvn verify -Pcoverage)"
```

Selected profiles are passed to `persist` command. Proceed to Step 4c.

---

#### Tier 3: Per-Module Selection (Customize path)

For each module with available commands, present multi-select:

```yaml
AskUserQuestion:
  question: "Select commands for module 'oauth-sheriff-core':"
  header: "Commands"
  multiSelect: true
  options:
    - label: "module-tests (Required)"
      description: "Unit tests (mvn clean test)"
    - label: "quality-gate (Required)"
      description: "Quality checks (mvn verify -Ppre-commit)"
    - label: "verify (Required)"
      description: "Full verification (mvn clean verify)"
    - label: "integration-tests [DETECTED]"
      description: "Integration tests (mvn verify -Pintegration-tests)"
    - label: "coverage [DETECTED]"
      description: "Test coverage (mvn verify -Pcoverage)"
    - label: "performance [DETECTED]"
      description: "JMH benchmarks (mvn verify -Pbenchmark)"
    - label: "install"
      description: "Install to local repo (mvn clean install)"
```

Repeat for each module. Proceed to Step 4c with collected selections.

---

### Step 4c: Generate and Persist Commands

Based on user selection, generate and persist commands:

```bash
# Auto-detect mode (with optional profile filter)
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist

# Minimal mode
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist --minimal

# With specific profiles selected (from Tier 2)
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist \
  --include-profiles "oauth-sheriff-core:integration-tests,oauth-sheriff-core:coverage"
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
Modules configured: 3
  - default (pom, 4 commands)
  - oauth-sheriff-core (jar, 8 commands)
  - oauth-sheriff-ui (npm, 6 commands)
```

---

### Canonical Command Names

Commands use a fixed vocabulary for programmatic lookup by plan execution agents:

| Canonical | Required | Description |
|-----------|----------|-------------|
| `module-tests` | **Yes** | Unit tests for the module |
| `quality-gate` | **Yes** | Pre-commit checks (lint, format, static analysis) |
| `verify` | **Yes** | Full build verification |
| `integration-tests` | No | Integration/E2E tests |
| `coverage` | No | Test coverage reports |
| `performance` | No | Benchmark/performance tests |
| `install` | No | Install to local repository |
| `package` | No | Create distributable package |

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

Use `lookup --build-system maven` or `lookup --build-system npm` to get specific command.

---

### Step 4d: Skill Domain Configuration

Configure skill domains based on detected build systems. User selects which domains to enable.

**Step 4d-1: Get available domains**

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-available
```

**Output (TOON)**:
```toon
status: success
detected_domains[2]:
- key: java
  name: Java Development
  build_system: maven
- key: javascript
  name: Javascript Development
  build_system: npm
optional_domains[2]:
- key: requirements
  name: Requirements Engineering
- key: documentation
  name: Documentation
```

**Step 4d-2: User selection**

```yaml
AskUserQuestion:
  question: "Select skill domains to enable for this project:"
  header: "Skill Domains"
  multiSelect: true
  options:
    # Build dynamically from get-available output
    # Pre-select detected domains (those with build_system)
    - label: "Java Development [DETECTED]"
      description: "Java code patterns, CDI, JUnit (from Maven)"
    - label: "JavaScript Development [DETECTED]"
      description: "Modern JS, ESLint, Jest (from npm)"
    - label: "Requirements Engineering"
      description: "User stories and acceptance criteria"
    - label: "Documentation"
      description: "Technical documentation standards"
```

**Step 4d-3: Configure selected domains**

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains configure --domains "java,javascript"
```

**Output (TOON)**:
```toon
status: success
system_domain: configured
domains_configured: 2
domains: java,javascript
```

This populates `skill_domains` in marshal.json with:
- `system` domain (always) with workflow_skills for 5 phases
- Each selected domain with nested structure:
  - `workflow_skill_extensions` (outline, triage)
  - `core` (defaults + optionals)
  - 5 profile blocks (architecture, planning, implementation, testing, quality)

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
