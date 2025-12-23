# Menu Option: Configuration

Sub-menu for build systems and skill domains configuration.

---

## Configuration Submenu

```
AskUserQuestion:
  question: "What would you like to configure?"
  options:
    - label: "Build Systems"
      description: "Detect and configure Maven/Gradle/npm"
      value: "build"
    - label: "Skill Domains"
      description: "Configure implementation skills per domain"
      value: "skill-domains"
    - label: "Modules"
      description: "Define module structure (path, domains, build-systems)"
      value: "modules"
    - label: "Manage Commands"
      description: "Configure build commands per module (test, verify, etc.)"
      value: "commands"
    - label: "Full Reconfigure"
      description: "Run first-run wizard again"
      value: "wizard"
    - label: "Back"
      description: "Return to main menu"
      value: "back"
```

## Routing

| Selection | Action |
|-----------|--------|
| build | Execute "Configuration: Build System" below |
| skill-domains | Execute "Configuration: Skill Domains" below |
| modules | Execute "Configuration: Modules" below |
| commands | Execute "Configuration: Manage Commands" below |
| wizard | Load and execute: `Read references/wizard-flow.md` |
| back | Return to Main Menu |

---

## Configuration: Build System

### Detect Build Systems

```bash
python3 .plan/execute-script.py pm-dev-builder:environment-detection:build-env detect
```

### Auto-Configure Detected Systems

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems detect
```

This detects build systems from project files and adds them with default commands.

### Build System Mappings

| Detected | Skill | Verification Command |
|----------|-------|---------------------|
| Maven | `pm-dev-builder:builder-maven-rules` | `/pm-dev-builder:builder-build-and-fix` |
| Gradle | `pm-dev-builder:builder-gradle-rules` | `/pm-dev-builder:builder-build-and-fix` |
| npm | `pm-dev-builder:builder-npm-rules` | `/pm-dev-builder:builder-build-and-fix system=npm` |

### View Configured Build Systems

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems list
```

### Add/Remove Build System

```bash
# Add Gradle with defaults
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems add --system gradle

# Remove unused build system
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems remove --system gradle
```

---

## Configuration: Skill Domains

Skill domains configure which implementation skills are loaded for different code types. Domains and supplements are auto-discovered from installed bundles.

Uses shared configuration flow (same as wizard Step 4d-4f).

### Reconfigure Skill Domains

**Step 1: Discover available domains and supplements**

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-available
```

**Output** shows `discovered_domains[]` (from bundle manifests) and `supplements[]` (optional additions).

**Step 2: User domain selection**

Present AskUserQuestion with available domains:

```yaml
AskUserQuestion:
  question: "Select skill domains to enable for this project:"
  header: "Skill Domains"
  multiSelect: true
  options:
    # Build dynamically from discovered_domains
    # Pre-select domains already configured in marshal.json
    - label: "Java Development"
      description: "Java code patterns, CDI, JUnit (pm-dev-java)"
    - label: "JavaScript Development"
      description: "Modern JS, ESLint, Jest (pm-dev-frontend)"
    - label: "Plugin Development"
      description: "Claude Code components (pm-plugin-development)"
    - label: "Requirements Engineering"
      description: "User stories and specs (pm-requirements)"
```

**Step 3: Supplement selection (if applicable)**

If supplements exist for selected domains, present them:

```yaml
AskUserQuestion:
  question: "Enable domain supplements?"
  header: "Supplements"
  multiSelect: true
  options:
    # Build from supplements[] filtered by selected domains
    - label: "CUI Java Patterns"
      description: "CUI logging, testing, HTTP for Java domain (pm-dev-java-cui)"
```

**Step 4: Configure selected domains**

```bash
# Without supplements
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains configure --domains "java,javascript"

# With supplements
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains configure --domains "java,javascript" --supplements "pm-dev-java-cui"
```

This configures:
- `system` domain (always) with workflow_skills for 5 phases
- Each selected domain with profile structure from bundle manifest
- Supplement skills merged as optionals in matching profiles

### List Domains

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains list
```

### View Domain Configuration

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains get --domain java
```

### Resolve Domain Skills (for task planning)

Aggregate core + profile skills with descriptions for LLM skill selection:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config resolve-domain-skills \
  --domain java --profile implementation
```

### Update Domain Skills

Update skills for a specific profile:

```bash
# Update implementation profile skills
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains set \
  --domain java \
  --profile implementation \
  --defaults "pm-dev-java:java-core" \
  --optionals "pm-dev-java:java-cdi,pm-dev-java:java-maintenance"
```

---

## Configuration: Modules

Modules define project structure with domain and build system mappings.

### Detect Modules

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules detect
```

### List Modules

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules list
```

### Add Module

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules add \
  --module my-module \
  --path path/to/module \
  --domains "java,java-testing" \
  --build-systems "maven"
```

---

## Configuration: Manage Commands

Manage canonical commands for project modules. Allows adding profile-based commands, removing unused commands, or resetting to defaults.

### Step 1: Select Module

```yaml
AskUserQuestion:
  question: "Which module do you want to configure?"
  header: "Module"
  options:
    - label: "default"
      description: "Root project (N commands)"
    - label: "{module-name}"
      description: "{module-type} (N commands)"
    - label: "All modules"
      description: "Reconfigure all module commands"
  multiSelect: false
```

Build options dynamically from marshal.json modules.

### Step 2: Select Operation

```yaml
AskUserQuestion:
  question: "What do you want to do with '{module}' commands?"
  header: "Operation"
  options:
    - label: "View"
      description: "Show current command configuration"
    - label: "Add"
      description: "Add new commands from detected profiles"
    - label: "Remove"
      description: "Remove commands from this module"
    - label: "Reset"
      description: "Reset to auto-detected defaults"
  multiSelect: false
```

### Operation: View

Show current commands for the module:

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env get-available-commands \
  --module "{module}"
```

Display output:
```
Commands for module '{module}' ({type}):
  - module-tests: mvn clean test
  - quality-gate: mvn verify -Ppre-commit
  - verify: mvn clean verify
  - coverage: mvn verify -Pcoverage [DETECTED]
```

### Operation: Add

First, detect available profiles not yet configured:

```bash
python3 .plan/execute-script.py plan-marshall:build-operations:build_env detect-profiles \
  --module "{module}"
```

Then present multi-select for profiles to add:

```yaml
AskUserQuestion:
  question: "Select profiles to add as commands:"
  header: "Add Commands"
  multiSelect: true
  options:
    - label: "integration-tests → integration-tests"
      description: "mvn verify -Pintegration-tests"
    - label: "benchmark → performance"
      description: "mvn verify -Pbenchmark"
```

Add selected profiles:

```bash
# Re-run persist with include-profiles to add specific profiles
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist \
  --include-profiles "{module}:{profile-id},{module}:{profile-id}"
```

### Operation: Remove

Present multi-select of current commands:

```yaml
AskUserQuestion:
  question: "Select commands to remove from '{module}':"
  header: "Remove Commands"
  multiSelect: true
  options:
    - label: "coverage"
      description: "mvn verify -Pcoverage"
    - label: "performance"
      description: "mvn verify -Pbenchmark"
```

Remove selected commands by editing marshal.json directly:

```bash
# Read current config, remove selected commands, write back
python3 .plan/execute-script.py plan-marshall:json-file-operations:manage-json-file delete-field \
  .plan/marshal.json --field "modules.{module}.commands.{canonical}"
```

### Operation: Reset

Reset module to auto-detected defaults:

```yaml
AskUserQuestion:
  question: "Reset '{module}' commands to defaults?"
  header: "Confirm Reset"
  options:
    - label: "Yes - Auto-detect"
      description: "Use smart defaults based on module type and profiles"
    - label: "Yes - Minimal"
      description: "Only required commands (module-tests, quality-gate, verify)"
    - label: "Cancel"
      description: "Keep current configuration"
  multiSelect: false
```

Execute reset:

```bash
# Auto-detect mode
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist

# Minimal mode
python3 .plan/execute-script.py plan-marshall:build-operations:build_env persist --minimal
```

---

## Thin Agent Architecture (5-Phase Model)

The pm-workflow bundle uses thin agents that load skills from system domain:

| Agent | Purpose | Skill Source |
|-------|---------|--------------|
| `plan-init-agent` | Initialize plan, detect domains | System defaults only |
| `solution-outline-agent` | Create deliverables | `resolve-workflow-skill --phase outline` |
| `task-plan-agent` | Create tasks from deliverables | `resolve-workflow-skill --phase plan` |
| `task-execute-agent` | Execute single task | `resolve-workflow-skill --phase execute` + `task.skills` |
| `plan-finalize-agent` | Commit, PR, triage | `resolve-workflow-skill --phase finalize` |

Workflow skills are resolved from `system.workflow_skills`. Domain-specific extensions are loaded via `resolve-workflow-skill-extension --domain {domain} --type {outline|triage}`.

---

After any configuration completes, return to Main Menu.
